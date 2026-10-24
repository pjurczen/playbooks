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


# ------------------------------------------------------------ the flow digest: all cases, all variants

def _load_rows(vdir: Path) -> list[dict]:
    f = vdir / "results.jsonl"
    return [json.loads(ln) for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip()] if f.is_file() else []


def _load_checks(vdir: Path) -> list[dict]:
    out = []
    for t in sorted((vdir / "traces").glob("*.json")) if (vdir / "traces").is_dir() else []:
        tr = json.loads(t.read_text(encoding="utf-8"))
        for c in tr["checks"]:
            out.append({**c, "case": tr["case_id"], "rep": tr["rep"]})
    return out


def _scorings(vdir: Path) -> dict[str, dict]:
    kinds: dict[str, dict] = {}
    for t in sorted((vdir / "traces").glob("*.json")) if (vdir / "traces").is_dir() else []:
        for sc in json.loads(t.read_text(encoding="utf-8"))["scores"]:
            kinds.setdefault(sc["id"], {"name": sc["name"], "scoring": sc["scoring"], "direction": sc["direction"]})
    return kinds


def _mean(xs: list[float]) -> float | None:
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def render_flow(flow: Path) -> str:
    """digest.md for a whole flow: metric by case per variant, variant means against the baseline with its spread, failure shares by category."""
    flow = Path(flow)
    variants = sorted(p.name for p in flow.iterdir() if (p / "results.jsonl").is_file())
    variants.sort(key=lambda v: (v != "baseline", v))
    out = [f"# {flow.name}: all documents, all variants", ""]
    if not variants:
        return "\n".join(out + ["No runs yet."])
    kinds: dict[str, dict] = {}
    per_variant: dict[str, dict[str, dict[str, list[float]]]] = {}  # variant -> metric -> case -> values over reps
    for v in variants:
        kinds.update({k: d for k, d in _scorings(flow / v).items() if k not in kinds})
        table: dict[str, dict[str, list[float]]] = {}
        for r in _load_rows(flow / v):
            for m, val in r["grade"].items():
                table.setdefault(m, {}).setdefault(r["prompt_id"], []).append(val)
        per_variant[v] = table
    metrics = sorted(kinds)

    def show(m: str, v: float | None) -> str:
        if v is None:
            return "–"
        return str(int(round(v))) if kinds.get(m, {}).get("scoring") == "count" else f"{v:.2f}"

    for v in variants:
        cases = sorted({c for m in per_variant[v] for c in per_variant[v][m]})
        reps = max((len(vals) for m in per_variant[v] for vals in per_variant[v][m].values()), default=1)
        out += [f"## {v}: metric by document" + (f" (mean over {reps} reps)" if reps > 1 else ""), "",
                "| metric | " + " | ".join(cases) + " |", "|---|" + "---|" * len(cases)]
        for m in metrics:
            row = per_variant[v].get(m, {})
            out.append(f"| `{m}` | " + " | ".join(show(m, _mean(row.get(c, []))) for c in cases) + " |")
        out.append("")

    base = variants[0]
    out += [f"## Variants against `{base}`", "",
            "Mean over documents. The spread is the min to max of the baseline's per-document means across its reps; a variant counts as moved only when its mean lies outside that spread, and with a single baseline rep there is no noise floor.", "",
            "| metric | direction | " + " | ".join(variants) + " | spread | moved |", "|---|---|" + "---|" * len(variants) + "---|---|"]
    for m in metrics:
        means = []
        for v in variants:
            means.append(_mean([_mean(vals) for vals in per_variant[v].get(m, {}).values()]))
        base_rows = per_variant[base].get(m, {})
        rep_means = []
        nreps = max((len(vals) for vals in base_rows.values()), default=0)
        if nreps > 1:
            for i in range(nreps):
                rep_means.append(_mean([vals[i] for vals in base_rows.values() if len(vals) > i]))
        spread = (min(rep_means), max(rep_means)) if len(rep_means) > 1 else None
        moved = []
        for v, mv in zip(variants[1:], means[1:]):
            if mv is None or means[0] is None:
                moved.append("–")
            elif spread is None:
                moved.append("no noise floor")
            else:
                better = (mv > means[0]) == (kinds[m]["direction"] == "higher")
                moved.append(("better" if better else "worse") if (mv < spread[0] or mv > spread[1]) else "within spread")
        out.append(f"| `{m}` | {kinds[m]['direction']} | " + " | ".join(show(m, x) for x in means) + " | "
                   + (f"{show(m, spread[0])}–{show(m, spread[1])}" if spread else "–") + " | " + (", ".join(moved) if moved else "–") + " |")
    out.append("")

    out += ["## What fails most", ""]
    for v in variants:
        checks = _load_checks(flow / v)
        if not checks:
            continue
        out += [f"### {v}", "", "| metric | fail | unknown | pass | total | fail share | categories |", "|---|---|---|---|---|---|---|"]
        by: dict[str, list[dict]] = {}
        for c in checks:
            by.setdefault(c["metric"], []).append(c)
        rows = []
        for m, cs in by.items():
            fail = sum(1 for c in cs if c["verdict"] == "fail")
            unk = sum(1 for c in cs if c["verdict"] in ("unknown", "unverified"))
            pas = sum(1 for c in cs if c["verdict"] == "pass")
            total = len(cs)
            share = None if kinds.get(m, {}).get("scoring") == "count" else (fail / total if total else None)
            cats: dict[str, int] = {}
            for c in cs:
                if c["verdict"] == "fail" and c.get("category"):
                    cats[c["category"]] = cats.get(c["category"], 0) + 1
            rows.append((share if share is not None else -1, m, fail, unk, pas, total, share, cats))
        for _, m, fail, unk, pas, total, share, cats in sorted(rows, reverse=True):
            out.append(f"| `{m}` | {fail} | {unk} | {pas} | {total} | {'–' if share is None else f'{share:.2f}'} | "
                       + (" · ".join(f"{k} {n}" for k, n in sorted(cats.items(), key=lambda kv: -kv[1])) or "") + " |")
        out.append("")
    return "\n".join(out)
