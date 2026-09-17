"""Per-source totals, memoized under a key the sources module also knows about."""

from . import memo
from .sources import load_source


def summarize(name: str) -> dict:
    def compute():
        rows = load_source(name)
        return {"name": name, "rows": len(rows), "total": sum(r["amount"] for r in rows)}

    return memo.memoize(f"summary:{name}", compute)
