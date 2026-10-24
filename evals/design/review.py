"""Load finished runs into tables for review. pandas is imported lazily so the judging code never depends on it."""
from __future__ import annotations

import json
from pathlib import Path


def list_cases(flow: Path, variant: str = "baseline") -> list[str]:
    tdir = Path(flow) / variant / "traces"
    return sorted({p.name.rsplit("_rep", 1)[0] for p in tdir.glob("*.json")}) if tdir.is_dir() else []


def load_traces(flow: Path, variant: str = "baseline", case: str | None = None) -> list[dict]:
    tdir = Path(flow) / variant / "traces"
    out = []
    for p in sorted(tdir.glob("*.json")) if tdir.is_dir() else []:
        t = json.loads(p.read_text(encoding="utf-8"))
        if case is None or t["case_id"] == case:
            out.append(t)
    return out


def load_results(flow: Path, variant: str = "baseline") -> list[dict]:
    p = Path(flow) / variant / "results.jsonl"
    return [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()] if p.is_file() else []


def scores_table(flow: Path, variant: str = "baseline", perf: tuple[str, ...] = ("words", "paragraphs", "code_lines", "diagrams", "cost_usd")):
    """Metric by document: one column per case (and rep), metrics as rows, selected covariates below them."""
    import pandas as pd

    rows = load_results(flow, variant)
    if not rows:
        return pd.DataFrame()
    cols = {}
    for r in rows:
        key = r["prompt_id"] if r["rep"] == 0 else f"{r['prompt_id']} (rep {r['rep']})"
        col = dict(r["grade"])
        col.update({f"perf: {k}": r["perf"].get(k) for k in perf if k in r["perf"]})
        cols[key] = col
    df = pd.DataFrame(cols)
    metrics = [i for i in df.index if not str(i).startswith("perf:")]
    return df.loc[sorted(metrics) + [i for i in df.index if str(i).startswith("perf:")]]


def checks_table(flow: Path, variant: str = "baseline", case: str | None = None, metric: str | None = None, verdict: str | list[str] | None = None,
                 quote_chars: int | None = None):
    """Every check of the variant, one row each, with its quote and reason. Filter by case, metric and verdict ('fail', or ['fail', 'unknown'])."""
    import pandas as pd

    verdicts = {verdict} if isinstance(verdict, str) else set(verdict or [])
    rows = []
    for t in load_traces(flow, variant, case):
        for c in t["checks"]:
            if metric and c["metric"] != metric:
                continue
            if verdicts and c["verdict"] not in verdicts:
                continue
            q = c.get("quote") or ""
            rows.append({"case": t["case_id"], "metric": c["metric"], "unit": c["unit"], "item": c.get("item") or "", "verdict": c["verdict"],
                         "category": c.get("category") or "", "votes": "/".join(c.get("votes") or []), "reason": c.get("reason") or "",
                         "quote": q[:quote_chars] + ("…" if quote_chars and len(q) > quote_chars else "") if quote_chars else q})
    return pd.DataFrame(rows, columns=["case", "metric", "unit", "item", "verdict", "category", "votes", "reason", "quote"])


def units_table(flow: Path, variant: str = "baseline", case: str | None = None, kinds: tuple[str, ...] | None = None):
    """The units of a case: paragraphs, headings, code, diagrams, and the model-found decisions, components, claims and passages."""
    import pandas as pd

    rows = []
    for t in load_traces(flow, variant, case):
        for d in t["units"]["docs"]:
            for u in d["units"]:
                if kinds and u["kind"] not in kinds:
                    continue
                m = u.get("meta", {})
                rows.append({"case": t["case_id"], "doc": d["name"], "id": u["id"], "kind": u["kind"], "form": m.get("form", ""),
                             "summary": m.get("summary") or m.get("name") or m.get("kind") or "", "status": m.get("status", ""), "text": u["text"]})
    return pd.DataFrame(rows, columns=["case", "doc", "id", "kind", "form", "summary", "status", "text"])


def failure_share(flow: Path, variant: str = "baseline"):
    """Per metric across all cases: how many checks failed, were undecided, passed; sorted by failure share. The 'what to fix first' table."""
    import pandas as pd

    df = checks_table(flow, variant)
    if df.empty:
        return df
    scoring = {s["id"]: s["scoring"] for t in load_traces(flow, variant) for s in t["scores"]}
    g = df.groupby("metric")["verdict"].value_counts().unstack(fill_value=0)
    for col in ("pass", "fail", "unknown", "unverified"):
        if col not in g:
            g[col] = 0
    g["total"] = g[["pass", "fail", "unknown", "unverified"]].sum(axis=1)
    g["scoring"] = [scoring.get(m, "") for m in g.index]
    # a count metric records only its failures, so a share means nothing there; it keeps its count and an empty share
    g["fail share"] = [round(f / t, 2) if sc != "count" and t else float("nan") for f, t, sc in zip(g["fail"], g["total"], g["scoring"])]
    return g[["scoring", "fail", "unknown", "unverified", "pass", "total", "fail share"]].sort_values("fail share", ascending=False, na_position="last")


def digest(flow: Path, variant: str = "baseline", case: str = "") -> str:
    p = Path(flow) / variant / "share" / case / "digest.md"
    return p.read_text(encoding="utf-8") if p.is_file() else f"no digest for {case}"


def document(flow: Path, variant: str = "baseline", case: str = "", marked: bool = False) -> str:
    """The judged document; with marked=True, prose paragraphs carry the [pNN] labels the checks refer to."""
    sdir = Path(flow) / variant / "share" / case
    docs = [p for p in sdir.glob("*.md") if p.name != "digest.md"]
    if not docs:
        return ""
    text = docs[0].read_text(encoding="utf-8")
    if not marked:
        return text
    from .mechanical import extract
    from .prompts import marked_document

    return marked_document(text, extract(text))
