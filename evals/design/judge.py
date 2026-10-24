"""The pipeline: load docs, extract units (mechanically, then with the model), run every rubric's checks, score, write the run."""
from __future__ import annotations

import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from . import __version__, digest, mechanical, output, prompts, rubrics as R, text as T
from .case import Case, Doc, load_docs
from .client import CallFailed, Client
from .extraction import LLM_KINDS, extract_llm
from .mechanical import Extraction, Unit
from .output import Check
from .schemas import JudgeOut


@dataclass
class RunResult:
    trace_path: Path
    share_dir: Path
    scores: list[dict]
    checks: list[Check]
    covariates: dict
    usage: dict = field(default_factory=dict)
    errors: list[dict] = field(default_factory=list)


def prompt_hash() -> str:
    """sha256 over every rubric and prompt file, so a run records exactly the text that shaped its judges."""
    h = hashlib.sha256()
    base = R.rubric_dir().parent
    for sub in ("rubrics", "prompts"):
        d = base / sub
        if d.is_dir():
            for p in sorted(d.glob("*.md")):
                h.update(p.name.encode())
                h.update(p.read_bytes())
    return h.hexdigest()[:16]


# ------------------------------------------------------------ mechanical evaluators

def _wall_of_text(doc: Doc, ex: Extraction) -> list[Check]:
    out = []
    for u in ex.by_kind("paragraph"):
        if u.meta.get("form") != "paragraph":
            continue
        n = u.meta["sentences"]
        if n > mechanical.LONG_PARAGRAPH_SENTENCES:
            out.append(Check("wall-of-text", u.id, doc.id, "fail", quote=u.text, reason=f"{n} sentences in one paragraph"))
        else:
            out.append(Check("wall-of-text", u.id, doc.id, "pass"))
    return out


def _stray_hedges(doc: Doc, ex: Extraction) -> list[Check]:
    span = ex.spans.get("open_questions")
    note = "" if span is not None else " (open-questions span unknown: every hedge counts)"
    out = []
    for h in ex.spans.get("hedges", []):
        if span and h["unit"] in span:
            continue
        out.append(Check("stray-hedges", h["unit"], doc.id, "fail", quote=h["sentence"], reason=f"hedge '{h['word']}' outside the open questions{note}"))
    return out


def _no_fact_twice_candidates(doc: Doc, ex: Extraction) -> list[Check]:
    return [Check("no-fact-twice", u.id, doc.id, "unknown", quote=u.meta["b"]["text"],
                  reason=f"near-duplicate of {u.meta['a']['unit']} (similarity {u.meta['similarity']}); judge confirmation not run")
            for u in ex.by_kind("duplicate_pair")]


def _diagram_mechanical(doc: Doc, ex: Extraction) -> list[Check]:
    out = []
    for g in ex.by_kind("diagram"):
        m = g.meta
        has_title = bool(m.get("title") or m.get("caption"))
        out.append(Check("diagram-stands-alone", g.id, doc.id, "pass" if has_title else "fail", item="title",
                         reason="" if has_title else "no title line and no caption sentence right before the diagram"))
        if m.get("type") in ("flowchart", "graph"):
            ok = bool(m.get("direction"))
            out.append(Check("diagram-stands-alone", g.id, doc.id, "pass" if ok else "fail", item="direction", reason="" if ok else "flowchart declares no direction"))
        if m.get("nodes"):
            ok = m["labelled_nodes"] == m["nodes"]
            out.append(Check("diagram-stands-alone", g.id, doc.id, "pass" if ok else "fail", item="nodes labelled",
                             reason="" if ok else f"{m['nodes'] - m['labelled_nodes']} of {m['nodes']} nodes have an id but no label"))
        if m.get("edges"):
            ok = m["labelled_edges"] == m["edges"]
            out.append(Check("diagram-stands-alone", g.id, doc.id, "pass" if ok else "fail", item="edges labelled",
                             reason="" if ok else f"{m['edges'] - m['labelled_edges']} of {m['edges']} edges carry no label"))
    return out


def _references_resolve(doc: Doc, docs: list[Doc]) -> list[Check]:
    if doc.kind != "slice":
        return []
    m = re.search(r"Initiative:\s*`?([^`·\n]+?)`?\s*(?:·|$)", doc.header)
    initiatives = {d.name for d in docs if d.kind == "initiative"}
    if not m:
        return [Check("references-resolve", doc.id, doc.id, "fail", reason="no Initiative link in the header line")]
    target = Path(m.group(1).strip()).name
    ok = target in initiatives
    return [Check("references-resolve", doc.id, doc.id, "pass" if ok else "fail", quote=doc.header,
                  reason="" if ok else f"header names {target}, which is not an initiative document of this case")]


MECHANICAL = {
    "wall-of-text": lambda doc, ex, docs: _wall_of_text(doc, ex),
    "stray-hedges": lambda doc, ex, docs: _stray_hedges(doc, ex),
    "diagram-stands-alone": lambda doc, ex, docs: _diagram_mechanical(doc, ex),
    "references-resolve": lambda doc, ex, docs: _references_resolve(doc, docs),
}
CANDIDATES_ONLY: set[str] = set()  # mechanical parts that only propose units for a judge
JUDGE_PENDING = {"diagram-stands-alone"}  # judge items not implemented yet


# ------------------------------------------------------------ judged rubrics

def units_for(rubric: R.Rubric, doc: Doc, ex: Extraction) -> list[tuple[str, str]]:
    """(unit id, text shown to the judge) for every unit this rubric asks about in this document."""
    k = rubric.unit
    if k == "doc":
        return [("doc", "The whole document.")]
    if k == "paragraph":
        return [(u.id, u.text) for u in ex.by_kind(k) if not u.meta.get("caption_for") and u.meta.get("form") != "header"]
    if k in ("heading", "code_block", "diagram"):
        return [(u.id, u.text) for u in ex.by_kind(k)]
    if k == "duplicate_pair":
        return [(u.id, f"A ({u.meta['a']['unit']}): {u.meta['a']['text']}\nB ({u.meta['b']['unit']}): {u.meta['b']['text']}") for u in ex.by_kind(k)]
    if k == "decision":
        decs = ex.by_kind(k)
        if rubric.scope:
            decs = [u for u in decs if u.meta.get("scope", "key") == rubric.scope]
        return [(u.id, f"{u.meta.get('summary', '')} [{u.meta.get('scope', 'key')}]\nWhere the document makes it: \"{u.text}\"") for u in decs]
    if k == "component":
        return [(u.id, f"{u.meta.get('name', '')} ({u.meta.get('status', '')}): \"{u.text}\"") for u in ex.by_kind(k)]
    if k == "claim":
        return [(u.id, f"{u.meta.get('summary', '')}: \"{u.text}\"") for u in ex.by_kind(k)]
    if k == "relational_passage":
        return [(u.id, f"({u.meta.get('kind', '')}) \"{u.text}\"") for u in ex.by_kind(k)]
    if k == "detailed_part":
        return [(u.id, f"{u.meta.get('name', '')}, paragraphs {', '.join(u.meta.get('paragraphs', [])) or '?'}: \"{u.text}\"") for u in ex.by_kind(k)]
    if k == "overview_sentence":
        out = []
        for pid in ex.spans.get("overview") or []:
            u = ex.get(pid)
            if u:
                for n, s in enumerate(T.sentences(u.text), 1):
                    out.append((f"{pid}.s{n}", s))
        return out
    return []


def _chunks(items: list, n: int) -> list[list]:
    n = max(1, n)
    return [items[i : i + n] for i in range(0, len(items), n)]


def _judge_batch(client: Client, rubric: R.Rubric, system: str, document: str, batch: list[tuple[str, str]], v: int, label: str) -> dict | CallFailed:
    """One judge call for one batch (plus a targeted retry for units it left out). Returns unit -> CheckOut, or the failure."""
    try:
        out: JudgeOut = client.parse(JudgeOut, system=system, document=document, question=prompts.judge_question(rubric, batch),
                                     effort="low", max_tokens=4000, label=label, tag=f"v{v}")
    except CallFailed as e:
        return e
    got = {c.unit: c for c in out.checks}
    missing = [u for u in batch if u[0] not in got]
    if missing:
        try:
            out2 = client.parse(JudgeOut, system=system, document=document, question=prompts.judge_question(rubric, missing),
                                effort="low", max_tokens=4000, label=label + "-missing", tag=f"v{v}")
            got.update({c.unit: c for c in out2.checks if c.unit in {m[0] for m in missing}})
        except CallFailed:
            pass
    return got


def judge_rubric(client: Client, rubric: R.Rubric, doc: Doc, ex: Extraction, votes: int = 1, workers: int = 1) -> list[Check]:
    units = units_for(rubric, doc, ex)
    if not units:
        return []
    system = prompts.system_prompt()
    document = prompts.document_block(doc.name, prompts.marked_document(doc.text, ex))
    per_unit: dict[str, list[tuple[str, str, str, str]]] = {uid: [] for uid, _ in units}
    batches = _chunks(units, rubric.batch)
    for v in range(max(1, votes)):
        jobs = [(b, batch, f"{rubric.id}-{doc.id}-b{b}-v{v}") for b, batch in enumerate(batches)]
        if workers > 1 and len(jobs) > 1:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                results = list(pool.map(lambda j: _judge_batch(client, rubric, system, document, j[1], v, j[2]), jobs))
        else:
            results = [_judge_batch(client, rubric, system, document, j[1], v, j[2]) for j in jobs]
        for (b, batch, _label), got in zip(jobs, results):
            if isinstance(got, CallFailed):
                for uid, _ in batch:
                    per_unit[uid].append(("unknown", "", f"no verdict: {got.failure_class}", ""))
                continue
            for uid, utext in batch:
                c = got.get(uid)
                if c is None:
                    per_unit[uid].append(("unknown", "", "no verdict returned", ""))
                    continue
                verdict, quote, reason = _verify(rubric, doc, c.verdict, c.quote.strip(), c.reason.strip(), utext)
                category = c.category.strip().lower() if rubric.categories else ""
                if category and category not in rubric.categories:
                    category = "other"
                per_unit[uid].append((verdict, quote, reason, category if verdict == "fail" else ""))
    checks = []
    for uid, vs in per_unit.items():
        decided = [x for x in vs if x[0] in ("pass", "fail")]
        p = sum(1 for x in decided if x[0] == "pass")
        f = len(decided) - p
        if p > f:
            final, pick = "pass", next(x for x in decided if x[0] == "pass")
        elif f > p:
            final, pick = "fail", next(x for x in decided if x[0] == "fail")
        elif decided:
            final, pick = "unknown", (decided[0][0], decided[0][1], f"votes split {p}-{f}: " + decided[0][2], "")
        else:
            final = "unverified" if any(x[0] == "unverified" for x in vs) else "unknown"
            pick = next((x for x in vs if x[0] == final), vs[0])
        checks.append(Check(rubric.id, uid, doc.id, final, quote=pick[1], reason=pick[2], votes=[x[0] for x in vs], source="judge",
                            category=pick[3] if final == "fail" else ""))
    return checks


def derive(rubric: R.Rubric, checks: list[Check]) -> list[Check]:
    """A derived rubric re-reads another rubric's checks: a fail there with the named category is a fail here, the rest pass through."""
    out = []
    for c in checks:
        if c.metric != rubric.derived_from:
            continue
        if c.verdict == "fail":
            v = "fail" if c.category == rubric.category else "pass"
        else:
            v = c.verdict
        out.append(Check(rubric.id, c.unit, c.doc, v, quote=c.quote if v == "fail" else "", reason=c.reason if v == "fail" else "",
                         votes=list(c.votes), source="derived", category=c.category if v == "fail" else ""))
    return out


def _verify(rubric: R.Rubric, doc: Doc, verdict: str, quote: str, reason: str, unit_text: str = "") -> tuple[str, str, str]:
    """Apply the evidence rule and the leak filter to one judge answer."""
    reason, _withheld = output.filter_reason(reason, doc.text)
    required = verdict in ("pass", "fail") and rubric.quote_required in (verdict, "both")
    if required and unit_text and T.word_count(unit_text) < 4:
        required = False  # a unit shorter than a quote is its own evidence ("None.")
    if quote:
        span = T.find_quote(doc.text, quote)
        if span:
            return verdict, doc.text[span[0]:span[1]], reason
        if required:
            return "unverified", "", (reason + " " if reason else "") + "[quote not found in the document]"
        return verdict, "", reason
    if required:
        return "unverified", "", (reason + " " if reason else "") + "[no quote given]"
    return verdict, "", reason


# ------------------------------------------------------------ scoring

def score(rubric: R.Rubric, checks: list[Check]) -> dict:
    cs = [c for c in checks if c.metric == rubric.id]
    passed = sum(1 for c in cs if c.verdict == "pass")
    failed = sum(1 for c in cs if c.verdict == "fail")
    unknown = sum(1 for c in cs if c.verdict in ("unknown", "unverified"))
    total = len(cs)
    decided = passed + failed
    if rubric.scoring == "count":
        value: float | None = float(failed)
    elif decided == 0:
        value = None
    else:
        value = passed / decided
    if total == 0 and rubric.scoring != "count":
        confidence = "n/a"
    elif total and unknown / total > 0.25:
        confidence = "low"
    elif rubric.scoring != "count" and decided == 0:
        confidence = "low"
    else:
        confidence = "ok"
    return {"id": rubric.id, "name": rubric.name, "unit": rubric.unit, "scoring": rubric.scoring, "direction": rubric.direction,
            "value": value, "passed": passed, "failed": failed, "unknown": unknown, "total": total, "confidence": confidence}


# ------------------------------------------------------------ reuse of a previous extraction

def reuse_units(units_from: Path, case_id: str, doc: Doc, ex: Extraction) -> bool:
    """Copy the model-found units and spans of a previous run into `ex` when the document is byte-identical."""
    p = units_from / "share" / case_id / "units.json"
    if not p.is_file():
        return False
    data = json.loads(p.read_text(encoding="utf-8"))
    llm_kinds = {k for _, k in LLM_KINDS.values()}
    for d in data.get("docs", []):
        if d.get("sha256") != doc.sha256:
            continue
        ex.units = [u for u in ex.units if u.kind not in llm_kinds]
        for u in d.get("units", []):
            if u["kind"] in llm_kinds:
                ex.units.append(Unit(u["id"], u["kind"], u["start"], u["end"], u["text"], u["sha8"], u.get("meta", {})))
        ex.spans["overview"] = d.get("spans", {}).get("overview")
        ex.spans["open_questions"] = d.get("spans", {}).get("open_questions")
        for k in ("decisions", "components", "claims"):
            if k in d.get("covariates", {}):
                ex.covariates[k] = d["covariates"][k]
        return True
    return False


# ------------------------------------------------------------ the run

def run_case(case: Case, *, flow: Path, variant: str = "baseline", rep: int = 0, mechanical_only: bool = False, metrics: list[str] | None = None,
             model: str | None = None, votes: int = 1, share_task: bool = False, units_from: Path | None = None, max_calls: int | None = None,
             client: Client | None = None, workers: int = 1) -> RunResult:
    docs = load_docs(case)
    ex = {d.id: mechanical.extract(d.text) for d in docs}
    vdir = flow / variant
    private = vdir / "private" / case.id
    extraction_report: dict = {}
    if not mechanical_only:
        if client is None:
            client = Client(**({"model": model} if model else {}), cache_dir=private / "cache", raw_dir=private / "raw", max_calls=max_calls)
        for d in docs:
            if units_from and reuse_units(Path(units_from), case.id, d, ex[d.id]):
                extraction_report[d.id] = {"reused_from": str(units_from)}
            else:
                extraction_report[d.id] = extract_llm(client, d, ex[d.id])
    all_rubrics = R.load_rubrics()
    chosen = R.select(all_rubrics, metrics, mechanical_only=mechanical_only, mechanical_ids=set(MECHANICAL), doc_kinds={d.kind for d in docs},
                      has_facts=bool(case.facts), multi_doc=len(docs) > 1)
    checks: list[Check] = []
    for r in chosen:
        judged = not mechanical_only and "judge" in r.needs and r.id not in JUDGE_PENDING and not r.derived_from
        for d in docs:
            if d.kind not in r.applies_to:
                continue
            if r.id in MECHANICAL and (mechanical_only or not judged or r.id not in CANDIDATES_ONLY):
                checks.extend(MECHANICAL[r.id](d, ex[d.id], docs))
            if judged:
                checks.extend(judge_rubric(client, r, d, ex[d.id], votes, workers=workers))
    for r in chosen:
        if r.derived_from and not mechanical_only:
            checks.extend(derive(r, checks))
    scores = [score(r, checks) for r in chosen]
    covariates: dict = {}
    for d in docs:
        for k, v in ex[d.id].covariates.items():
            if isinstance(v, (int, float)):
                covariates[k] = covariates.get(k, 0) + v
    usage = client.usage.to_dict(client.model) if client else {"calls": 0, "cost_usd": 0.0, "in_tokens": 0, "out_tokens": 0}
    errors = list(client.errors) if client else []
    meta = {"tool_version": __version__, "timestamp": output.now_iso(), "model": client.model if client else None, "votes": votes, "workers": workers,
            "prompt_hash": prompt_hash(), "mechanical_only": mechanical_only, "units_from": str(units_from) if units_from else None,
            "cost_usd": usage.get("cost_usd") or 0.0, "in_tokens": usage.get("in_tokens", 0), "out_tokens": usage.get("out_tokens", 0),
            "calls": usage.get("calls", 0), "cached_calls": usage.get("cached_calls", 0), "replayed_cost_usd": usage.get("replayed_cost_usd"),
            "extraction": extraction_report,
            "failed_attempts": len(errors)}
    private_meta = {**meta, "usage": usage, "case_path": str(case.source) if case.source else None, "doc_paths": [str(d.path) for d in docs],
                    "repo": case.repo, "flow": str(flow), "task": case.task, "errors": errors}
    doc_dicts = [{"id": d.id, "kind": d.kind, "name": d.name} for d in docs]
    md = digest.render(case.id, variant, rep, doc_dicts, scores, [c.to_dict() for c in checks], covariates, meta)
    trace = output.write_run(flow=flow, variant=variant, rep=rep, case=case, docs=docs, extractions=ex, checks=checks, scores=scores,
                             meta=meta, private_meta=private_meta, digest_md=md, share_task=share_task)
    if errors:
        output.append_errors(vdir, [{"prompt_id": case.id, "variant": variant, "rep": rep, **e} for e in errors])
    return RunResult(trace, vdir / "share" / case.id, scores, checks, covariates, usage, errors)
