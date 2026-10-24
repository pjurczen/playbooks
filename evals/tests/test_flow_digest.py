import shutil
from pathlib import Path

from design.case import case_from_docs
from design.cli import main
from design.digest import render_flow
from design.judge import run_case


def test_flow_digest_tables(tmp_path):
    src = Path(__file__).resolve().parents[1] / "fixtures/designs/2026-09-17-unified-cache.md"
    d = tmp_path / "docs"; d.mkdir()
    shutil.copy(src, d / "2026-01-01-a.md"); shutil.copy(src, d / "2026-01-02-b.md")
    flow = tmp_path / "flow"
    for rep in (0, 1):
        for p in sorted(d.glob("*.md")):
            run_case(case_from_docs([str(p)]), flow=flow, variant="baseline", rep=rep, mechanical_only=True)
    run_case(case_from_docs([str(d / "2026-01-01-a.md")]), flow=flow, variant="v1", mechanical_only=True)
    md = render_flow(flow)
    assert "## baseline: metric by document (mean over 2 reps)" in md and "## v1: metric by document" in md
    assert "| `wall-of-text` | lower |" in md and "within spread" in md  # identical documents: v1 lies inside the baseline spread
    assert "## What fails most" in md and "`diagram-stands-alone`" in md
    assert main(["digest", str(flow)]) == 0 and (flow / "digest.md").is_file()
