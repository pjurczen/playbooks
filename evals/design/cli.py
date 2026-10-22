"""design: judge design documents. Subcommands: judge, extract, facts, digest."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .case import CaseError, case_from_docs, load_case
from .client import CallFailed


def _judge(a: argparse.Namespace) -> int:
    from .judge import run_case

    if a.case:
        case = load_case(a.case)
    elif a.doc:
        case = case_from_docs(a.doc, a.initiative, a.id)
    else:
        print("give a case.json or at least one --doc", file=sys.stderr)
        return 2
    metrics = [m.strip() for m in a.metrics.split(",")] if a.metrics else None
    if not a.mechanical_only:
        from .client import has_credentials

        if not has_credentials():
            print("no Anthropic credentials: put ANTHROPIC_API_KEY in evals/.env (see example.env), or run with --mechanical-only", file=sys.stderr)
            return 2
    res = run_case(case, flow=Path(a.flow).resolve(), variant=a.variant, rep=a.rep, mechanical_only=a.mechanical_only,
                   metrics=metrics, model=a.model, votes=a.votes, share_task=a.share_task,
                   units_from=Path(a.units_from).resolve() if a.units_from else None, max_calls=a.max_calls)
    for s in res.scores:
        v = "–" if s["value"] is None else (f"{s['value']:.2f}" if s["scoring"] != "count" else str(int(s["value"])))
        print(f"{s['id']:<28} {v:>6}  ({s['passed']} pass / {s['failed']} fail / {s['unknown']} unknown)  {s['confidence']}")
    if res.usage.get("calls"):
        cost = res.usage.get("cost_usd")
        print(f"calls: {res.usage['calls']} ({res.usage.get('cached_calls', 0)} cached), tokens in/out: {res.usage['in_tokens']}/{res.usage['out_tokens']}"
              + (f", cost ${cost:.4f}" if isinstance(cost, (int, float)) else "") + (f", failed attempts: {len(res.errors)}" if res.errors else ""))
    print(f"share: {res.share_dir}")
    print(f"trace: {res.trace_path}")
    return 0


def _extract(a: argparse.Namespace) -> int:
    from . import mechanical
    from .case import load_docs
    from .client import Client, has_credentials
    from .extraction import claims_markdown, extract_llm

    if not has_credentials():
        print("no Anthropic credentials: put ANTHROPIC_API_KEY in evals/.env (see example.env)", file=sys.stderr)
        return 2
    case = load_case(a.case)
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    client = Client(**({"model": a.model} if a.model else {}), cache_dir=out / ".cache")
    docs = load_docs(case)
    units = {"docs": []}
    for d in docs:
        ex = mechanical.extract(d.text)
        report = extract_llm(client, d, ex)
        units["docs"].append({"id": d.id, "kind": d.kind, "name": d.name, "sha256": d.sha256, **ex.to_dict()})
        (out / f"{d.path.stem}.claims.md").write_text(claims_markdown(d, ex), encoding="utf-8")
        print(f"{d.name}: {report}")
    (out / "units.json").write_text(json.dumps(units, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"units: {out / 'units.json'}")
    return 0


def _digest(a: argparse.Namespace) -> int:
    from .digest import render_from_trace

    flow = Path(a.flow).resolve()
    variants = [a.variant] if a.variant else sorted(p.name for p in flow.iterdir() if (p / "traces").is_dir())
    n = 0
    for v in variants:
        for trace in sorted((flow / v / "traces").glob("*.json")):
            case_id = trace.name.rsplit("_rep", 1)[0]
            if a.case and case_id != a.case:
                continue
            md = render_from_trace(trace)
            out = flow / v / "share" / case_id / "digest.md"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(md, encoding="utf-8")
            print(out)
            n += 1
    if n == 0:
        print("no traces found", file=sys.stderr)
        return 1
    return 0


def _not_yet(what: str):
    def run(a: argparse.Namespace) -> int:
        print(f"{what} is not implemented yet", file=sys.stderr)
        return 2

    return run


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="design", description="Judge design documents with small, evidence-quoting checks.")
    p.add_argument("--version", action="version", version=f"design {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    j = sub.add_parser("judge", help="judge one case (a case.json, or --doc paths)")
    j.add_argument("case", nargs="?", help="path to case.json")
    j.add_argument("--doc", action="append", help="document path; repeatable (quick form without a case file)")
    j.add_argument("--initiative", help="initiative document; other --doc paths become its slices")
    j.add_argument("--id", help="case id for the quick form")
    j.add_argument("--flow", required=True, help="flow directory (runs are grouped by variant inside it)")
    j.add_argument("--variant", default="baseline", help="baseline, v1, v2, ... (default: baseline)")
    j.add_argument("--rep", type=int, default=0, help="repetition index (default 0)")
    j.add_argument("--model", help="judge model id (default: DESIGN_JUDGE_MODEL from .env)")
    j.add_argument("--votes", type=int, default=1, help="judge votes per check (default 1)")
    j.add_argument("--metrics", help="comma-separated rubric ids to run (default: all that apply)")
    j.add_argument("--mechanical-only", action="store_true", help="no model calls: mechanical metrics and covariates only")
    j.add_argument("--share-task", action="store_true", help="copy the task text into share/ (off by default)")
    j.add_argument("--units-from", help="a previous <flow>/<variant> dir whose extracted units are reused when the document is identical")
    j.add_argument("--max-calls", type=int, help="abort after this many model calls")
    j.set_defaults(fn=_judge)

    d = sub.add_parser("digest", help="regenerate digest.md files from a flow's traces")
    d.add_argument("flow")
    d.add_argument("--variant")
    d.add_argument("--case")
    d.set_defaults(fn=_digest)

    e = sub.add_parser("extract", help="write units.json and claims.md for a case without judging")
    e.add_argument("case")
    e.add_argument("--out", required=True)
    e.add_argument("--model")
    e.set_defaults(fn=_extract)

    f = sub.add_parser("facts", help="draft fact questions from a transcript or brief")
    f.add_argument("case")
    f.add_argument("--from", dest="source", choices=["transcript", "brief"], default="transcript")
    f.set_defaults(fn=_not_yet("facts"))
    return p


def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    try:
        return a.fn(a)
    except CaseError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except CallFailed as e:
        print(f"model call failed ({e.failure_class}): {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
