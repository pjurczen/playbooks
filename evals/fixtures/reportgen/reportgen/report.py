"""Builds the markdown report. `fresh` empties both caches by reaching into each of them."""

from . import memo, sources
from .summary import summarize


def build_report(names: list[str], fresh: bool = False) -> str:
    if fresh:
        memo.clear_memo()
        sources.file_cache().purge_older_than(0)
    lines = ["| source | rows | total |", "|---|---|---|"]
    for name in names:
        s = summarize(name)
        lines.append(f"| {s['name']} | {s['rows']} | {s['total']} |")
    return "\n".join(lines)
