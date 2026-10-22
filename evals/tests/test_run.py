import json
from pathlib import Path

from design import output
from design.case import load_case, case_from_docs
from design.cli import main
from design.judge import run_case


def test_mechanical_run_writes_layout_and_keeps_paths_private(smoke_case, tmp_path):
    case = load_case(smoke_case)
    flow = tmp_path / "flow"
    res = run_case(case, flow=flow, variant="baseline", rep=0, mechanical_only=True)
    v = flow / "baseline"
    assert (v / "results.jsonl").is_file() and (flow / "_state.json").is_file()
    assert res.trace_path.is_file() and (res.share_dir / "digest.md").is_file() and (res.share_dir / "units.json").is_file()
    secrets = [str(smoke_case), str(case.docs[0].path), str(flow)]
    assert output.verify_share(res.share_dir, secrets) == []
    for p in (v / "results.jsonl", res.trace_path):
        assert not any(s in p.read_text() for s in secrets)
    meta = json.loads((v / "private" / case.id / "meta.json").read_text())
    assert meta["doc_paths"][0] == str(case.docs[0].path)
    row = json.loads((v / "results.jsonl").read_text().splitlines()[-1])
    assert row["prompt_id"] == case.id and "wall-of-text" in row["grade"] and row["perf"]["diagrams"] == 1
    ids = {s["id"] for s in res.scores}
    assert {"wall-of-text", "stray-hedges", "no-fact-twice", "diagram-stands-alone"} <= ids
    assert "references-resolve" not in ids  # single-doc case


def test_rerun_same_rep_replaces_row(smoke_case, tmp_path):
    case = load_case(smoke_case)
    flow = tmp_path / "flow"
    run_case(case, flow=flow, mechanical_only=True)
    run_case(case, flow=flow, mechanical_only=True)
    assert len((flow / "baseline" / "results.jsonl").read_text().splitlines()) == 1


def test_cli_quick_form_and_digest(smoke_case, tmp_path, capsys):
    doc = str(load_case(smoke_case).docs[0].path)
    flow = str(tmp_path / "flow")
    assert main(["judge", "--doc", doc, "--flow", flow, "--mechanical-only"]) == 0
    assert "wall-of-text" in capsys.readouterr().out
    assert main(["digest", flow]) == 0
    assert (Path(flow) / "baseline" / "share" / "unified-cache" / "digest.md").is_file()


def test_case_from_docs_infers_kinds(tmp_path):
    init = tmp_path / "initiatives" / "2026-10-01-x.md"
    sl = tmp_path / "designs" / "2026-10-02-x-slice.md"
    init.parent.mkdir(); sl.parent.mkdir()
    init.write_text("# I\n\nStatus: draft\n"); sl.write_text("# S\n\nStatus: draft · Initiative: `2026-10-01-x.md`\n")
    case = case_from_docs([str(sl)], initiative=str(init))
    assert [d.kind for d in case.docs] == ["initiative", "slice"] and case.docs[1].initiative == init


def test_filter_reason_withholds_code_looking_text():
    doc = "The ReportCache owns validity. The summariser asks the cache."
    assert output.filter_reason("the ReportCache owns validity, so the summariser need not", doc) == ("the ReportCache owns validity, so the summariser need not", False)
    for bad in ("see `memo.py`", "reportgen/sources.py reads files", "the load_source helper", "at line 42", "sources.py:12"):
        assert output.filter_reason(bad, doc)[1] is True
    assert output.filter_reason("the `ReportCache` owns validity", doc)[1] is False  # backticks around a name the document uses are fine
