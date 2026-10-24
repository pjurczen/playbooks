"""digest.md: what a person reads after a run, and what a skill-improvement session is handed."""
from __future__ import annotations

import json
from pathlib import Path

from . import text as T


def _fmt(v, scoring: str | None = None) -> str:
    if v is None:
        return "–"
    if scoring == "count":
        return str(int(v))
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v)


def _clip(s: str, words: int = 40) -> str:
    w = s.split()
    return " ".join(w[:words]) + (" …" if len(w) > words else "")


def render(case_id: str, variant: str, rep: int, docs: list[dict], scores: list[dict], checks: list[dict], covariates: dict, meta: dict) -> str:
    out = [f"# {case_id} — {variant}, rep {rep}", ""]
    out.append("Documents: " + ", ".join(f"`{d['name']}` ({d['kind']})" for d in docs))
    if meta.get("mechanical_only"):
        out.append("")
        out.append("Mechanical-only run: metrics that need a judge or the LLM extraction were not run.")
    elif meta.get("model"):
        cost = meta.get("cost_usd")
        out.append("")
        out.append(f"Judge: `{meta['model']}`, {meta.get('votes', 1)} vote(s), {meta.get('calls', 0)} calls"
                   + (f" ({meta['cached_calls']} from cache)" if meta.get("cached_calls") else "")
                   + (f", about ${cost:.2f} paid now" if isinstance(cost, (int, float)) else "")
                   + (f" (${meta['replayed_cost_usd']:.2f} when the cached calls were first made)" if meta.get("replayed_cost_usd") else "")
                   + (f", {meta['failed_attempts']} failed attempt(s)" if meta.get("failed_attempts") else "") + ".")
    out += ["", "## Scores", "", "| metric | value | passed | failed | unknown | total | confidence |", "|---|---|---|---|---|---|---|"]
    for s in scores:
        out.append(f"| {s['name']} (`{s['id']}`) | {_fmt(s['value'], s['scoring'])} | {s['passed']} | {s['failed']} | {s['unknown']} | {s['total']} | {s['confidence']} |")
    findings = [c for c in checks if c["verdict"] in ("fail", "unknown", "unverified")]
    out += ["", "## Findings", ""]
    if not findings:
        out.append("No failing or undecided checks.")
    by_metric: dict[str, list[dict]] = {}
    for c in findings:
        by_metric.setdefault(c["metric"], []).append(c)
    names = {s["id"]: s["name"] for s in scores}
    for mid, cs in by_metric.items():
        out.append(f"### {names.get(mid, mid)} (`{mid}`)")
        out.append("")
        if all(c.get("source") == "derived" for c in cs):
            out.append(f"{len(cs)} paragraph(s): " + ", ".join(c["unit"] for c in cs) + ". Details under the metric these are derived from.")
            out.append("")
            continue
        cats = {}
        for c in cs:
            if c.get("category"):
                cats[c["category"]] = cats.get(c["category"], 0) + 1
        if cats:
            out.append("By category: " + " · ".join(f"{k} {v}" for k, v in sorted(cats.items(), key=lambda kv: -kv[1])))
            out.append("")
        for c in cs:
            tag = f"[{c['unit']}{':' + c['item'] if c.get('item') else ''}] {c['verdict']}" + (f" ({c['category']})" if c.get("category") else "")
            line = f"- {tag}"
            if c.get("quote"):
                line += f' — "{_clip(c["quote"])}"'
            if c.get("reason"):
                line += f" — {c['reason']}"
            out.append(line)
        out.append("")
    out += ["## Covariates", "", "| " + " | ".join(covariates.keys()) + " |", "|" + "---|" * len(covariates)]
    out.append("| " + " | ".join(_fmt(v) for v in covariates.values()) + " |")
    out.append("")
    return "\n".join(out)


def render_from_trace(trace_path: Path) -> str:
    t = json.loads(trace_path.read_text(encoding="utf-8"))
    cov: dict = {}
    for d in t["units"]["docs"]:
        for k, v in d.get("covariates", {}).items():
            if isinstance(v, (int, float)):
                cov[k] = cov.get(k, 0) + v
    return render(t["case_id"], t["variant"], t["rep"], t["docs"], t["scores"], t["checks"], cov, t.get("meta", {}))
