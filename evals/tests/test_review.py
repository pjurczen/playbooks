import pytest

from design import review
from design.case import load_case
from design.judge import run_case


def test_review_tables_from_a_mechanical_run(smoke_case, tmp_path):
    pd = pytest.importorskip("pandas")
    case = load_case(smoke_case)
    flow = tmp_path / "flow"
    run_case(case, flow=flow, mechanical_only=True)
    assert review.list_cases(flow) == [case.id]
    scores = review.scores_table(flow)
    assert case.id in scores.columns and "wall-of-text" in scores.index and "perf: words" in scores.index
    checks = review.checks_table(flow, verdict="fail")
    assert list(checks.columns) == ["case", "metric", "unit", "item", "verdict", "category", "votes", "reason", "quote"]
    assert (checks["verdict"] == "fail").all()
    share = review.failure_share(flow)
    assert "fail share" in share.columns and "diagram-stands-alone" in share.index
    units = review.units_table(flow, case=case.id, kinds=("diagram",))
    assert len(units) == 1 and units.iloc[0]["kind"] == "diagram"
    assert review.digest(flow, case=case.id).startswith("# reportgen-unified-cache")
    assert "[p01]" in review.document(flow, case=case.id, marked=True)
