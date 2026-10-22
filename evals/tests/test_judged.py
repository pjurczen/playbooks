"""The model path, exercised with a scripted backend: extraction anchoring, votes, quote verification, cache, errors, end to end."""
import json

import pytest

from design import mechanical
from design.case import load_case, load_docs
from design.client import CallFailed, Client, ScriptedBackend
from design.extraction import extract_llm
from design.judge import judge_rubric, run_case
from design.rubrics import load_rubrics
from design.schemas import ExtractionOut, JudgeOut

DEC1 = "Put one ReportCache in front of every read."
DEC2 = "Invalidation is by key prefix, not by enumerating keys"
ALT = "Keep both caches and document the sync rules — rejected. The rules already exist as comments and are already broken in three places"


def extraction_payload(bad_quote=False):
    return {
        "key_decisions": [{"quote": DEC2, "summary": "invalidate by prefix"}, {"quote": DEC1, "summary": "one cache in front of reads"},
                          {"quote": "this sentence is nowhere in the document at all", "summary": "ghost"} if bad_quote else {"quote": "Memory sits in front of disk inside the cache", "summary": "memory before disk"}],
        "components": [{"name": "ReportCache", "status": "new", "quote": "ReportCache (new) — the only cache: a memory tier in front of a disk tier"}],
        "system_claims": [{"quote": "Every source read goes through two caches that know nothing about each other", "summary": "two independent caches today"}],
        "relational_passages": [{"quote": "The loader, the summariser and the report builder receive the cache as a collaborator", "kind": "interaction"}],
        "overview_span": {"paragraphs": ["p03", "p04", "p99"]},
        "detailed_parts": [{"name": "Validity", "paragraphs": ["p14"], "quote": "Every entry carries its expiry; nothing else decides whether a value may be served", }],
        "open_questions_span": {"paragraphs": ["p23"]},
    }


def scripted(extraction=None, judge=None):
    def handler(req):
        if req.schema is ExtractionOut:
            return extraction(req) if callable(extraction) else (extraction or extraction_payload())
        if req.schema is JudgeOut:
            return judge(req)
        raise AssertionError(req.schema)
    return ScriptedBackend(handler)


@pytest.fixture
def doc_and_ex(smoke_case):
    case = load_case(smoke_case)
    doc = load_docs(case)[0]
    return case, doc, mechanical.extract(doc.text)


def test_extraction_anchors_orders_and_drops(doc_and_ex):
    case, doc, ex = doc_and_ex
    client = Client(model="test-model", backend=scripted(extraction_payload(bad_quote=True)))
    report = extract_llm(client, doc, ex)
    decs = ex.by_kind("decision")
    assert [d.id for d in decs] == ["dec-01", "dec-02"] and decs[0].start < decs[1].start
    assert decs[0].text.startswith("Put one ReportCache")  # ordered by position, not by the model's order
    assert report["dropped"] == 1 and report["items"] == 7
    assert ex.spans["overview"] == ["p03", "p04"] and ex.spans["open_questions"] == ["p23"]
    assert ex.by_kind("component")[0].meta["name"] == "ReportCache"
    assert ex.covariates["decisions"] == 2


def test_judge_votes_and_quote_verification(doc_and_ex):
    case, doc, ex = doc_and_ex
    Client(model="test-model", backend=scripted()).__class__  # noqa: just for symmetry
    client = Client(model="test-model", backend=scripted())
    extract_llm(client, doc, ex)
    rubric = load_rubrics()["alternatives-with-reasons"]
    calls = {"n": 0}

    def judge(req):
        calls["n"] += 1
        vote = req.nonce.split("/")[0]
        ids = [l.split('"')[1] for l in req.question.splitlines() if l.startswith("<unit id=")]
        checks = []
        for uid in ids:
            if uid == "dec-01":   # pass with a real quote in votes 0 and 1, fail in vote 2 -> majority pass
                checks.append({"unit": uid, "verdict": "pass" if vote != "v2" else "fail", "quote": ALT if vote != "v2" else "", "reason": "an alternative with its cost"})
            elif uid == "dec-02":  # pass claimed but the quote does not exist -> unverified every time
                checks.append({"unit": uid, "verdict": "pass", "quote": "a quote that is not in the document anywhere", "reason": "see `memo.py`"})
            else:                  # omitted on purpose -> targeted retry returns it
                pass
        return {"metric": rubric.id, "checks": checks}

    client.backend = scripted(judge=judge)
    checks = judge_rubric(client, rubric, doc, ex, votes=3)
    by = {c.unit: c for c in checks}
    assert by["dec-01"].verdict == "pass" and by["dec-01"].votes == ["pass", "pass", "fail"]
    assert doc.text.find(by["dec-01"].quote) >= 0 and by["dec-01"].quote.startswith("Keep both caches")
    assert by["dec-02"].verdict == "unverified" and by["dec-02"].quote == "" and "[quote not found" in by["dec-02"].reason
    assert by["dec-02"].reason.startswith("[withheld")  # the backtick in the reason tripped the leak filter
    assert by["dec-03"].verdict == "unknown" and by["dec-03"].reason == "no verdict returned"
    assert calls["n"] == 6  # 3 votes x (one batch + one targeted retry for the missing unit)


def test_per_run_cache_and_failure_classes(doc_and_ex, tmp_path):
    case, doc, ex = doc_and_ex
    backend = scripted()
    client = Client(model="test-model", backend=backend, cache_dir=tmp_path / "cache")
    extract_llm(client, doc, ex)
    extract_llm(client, doc, mechanical.extract(doc.text))
    assert client.usage.calls == 2 and client.usage.cached_calls == 1 and len(backend.requests) == 1
    assert client.usage.input_tokens == 100 and client.usage.replayed["input_tokens"] == 100  # the replayed call keeps its original usage

    def failing(req):
        raise CallFailed("refusal", "nope")
    client2 = Client(model="test-model", backend=scripted(extraction=failing))
    with pytest.raises(CallFailed) as e:
        extract_llm(client2, doc, mechanical.extract(doc.text))
    assert e.value.failure_class == "refusal" and len(client2.errors) == 3


def test_run_case_judged_end_to_end(smoke_case, tmp_path):
    case = load_case(smoke_case)

    def judge(req):
        ids = [l.split('"')[1] for l in req.question.splitlines() if l.startswith("<unit id=")]
        metric = req.question.split("`")[1]
        if metric == "paragraph-earns-place":
            return {"metric": metric, "checks": [{"unit": u, "verdict": "fail" if u == "p02" else "pass", "quote": DEC1 if u == "p02" else "", "reason": "restated"} for u in ids]}
        return {"metric": metric, "checks": [{"unit": u, "verdict": "pass", "quote": ALT, "reason": "named with cost"} for u in ids]}

    client = Client(model="test-model", backend=scripted(judge=judge), cache_dir=tmp_path / "c")
    flow = tmp_path / "flow"
    res = run_case(case, flow=flow, variant="baseline", client=client, metrics=["paragraph-earns-place", "alternatives-with-reasons", "stray-hedges", "no-fact-twice"])
    ids = {s["id"]: s for s in res.scores}
    assert ids["alternatives-with-reasons"]["value"] == 1.0 and ids["alternatives-with-reasons"]["total"] == 3
    assert ids["paragraph-earns-place"]["failed"] == 1 and 0 < ids["paragraph-earns-place"]["value"] < 1
    assert ids["stray-hedges"]["value"] == 0.0
    row = json.loads((flow / "baseline" / "results.jsonl").read_text().splitlines()[-1])
    assert row["grade"]["alternatives-with-reasons"] == 1.0 and row["meta"]["model"] == "test-model" and row["meta"]["calls"] > 0
    assert not (flow / "baseline" / "errors.jsonl").exists()
    units = json.loads((res.share_dir / "units.json").read_text())
    assert any(u["kind"] == "decision" for u in units["docs"][0]["units"])
    # a second run reusing the units makes no extraction call
    client2 = Client(model="test-model", backend=scripted(judge=judge), cache_dir=tmp_path / "c2")
    run_case(case, flow=flow, variant="baseline", rep=1, client=client2, metrics=["alternatives-with-reasons"], units_from=flow / "baseline")
    assert all(r.schema is JudgeOut for r in client2.backend.requests)


def test_parallel_batches_give_the_same_checks(smoke_case, tmp_path):
    case = load_case(smoke_case)

    def judge(req):
        ids = [l.split('"')[1] for l in req.question.splitlines() if l.startswith("<unit id=")]
        return {"metric": req.question.split("`")[1], "checks": [{"unit": u, "verdict": "fail" if u.endswith("3") else "pass", "quote": DEC1 if u.endswith("3") else "", "reason": "r"} for u in ids]}

    runs = []
    for workers in (1, 4):
        client = Client(model="test-model", backend=scripted(judge=judge))
        res = run_case(case, flow=tmp_path / f"w{workers}", client=client, metrics=["paragraph-earns-place"], workers=workers)
        runs.append(sorted((c.unit, c.verdict) for c in res.checks))
    assert runs[0] == runs[1] and any(v == "fail" for _, v in runs[0])
