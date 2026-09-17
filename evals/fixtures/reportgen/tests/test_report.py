import pytest

from reportgen import memo, sources
from reportgen.report import build_report
from reportgen.summary import summarize


@pytest.fixture(autouse=True)
def isolated_caches(tmp_path):
    memo.clear_memo()
    sources.configure_cache_dir(tmp_path / "cache")
    sources.READS["disk"] = 0
    yield
    memo.clear_memo()


def test_report_totals_each_source():
    report = build_report(["sales", "costs"])
    assert "| sales | 3 | 600 |" in report
    assert "| costs | 2 | 150 |" in report


def test_second_summary_of_same_source_does_not_hit_disk():
    summarize("sales")
    summarize("sales")
    assert sources.READS["disk"] == 1


def test_fresh_report_rereads_every_source():
    build_report(["sales"])
    build_report(["sales"], fresh=True)
    assert sources.READS["disk"] == 2
