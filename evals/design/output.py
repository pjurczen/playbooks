"""Run output: the hillclimb-compatible flow layout, the share/private split, redaction and the reason leak filter.

<flow>/<variant>/results.jsonl, errors.jsonl, traces/<case>_rep<k>.json, share/<case>/, private/<case>/ and <flow>/_state.json.
Only private/ may contain absolute paths, the commit, the case path or usage; everything else is scrubbed before it is written.
"""
from __future__ import annotations

import json
import re
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from . import text as T

REDACTED = "[redacted]"
WITHHELD = "[withheld: not from the document]"
PERF_FIELDS = ["words", "paragraphs", "long_paragraphs", "code_lines", "diagrams", "duplicate_pairs", "stray_hedges", "cost_usd", "in_tokens", "out_tokens"]


@dataclass
class Check:
    metric: str
    unit: str
    doc: str
    verdict: str  # pass | fail | unknown | unverified
    quote: str = ""
    reason: str = ""
    item: str | None = None
    votes: list[str] = field(default_factory=list)
    source: str = "mechanical"  # mechanical | judge | derived
    category: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def scrub(obj, secrets: list[str]):
    """Replace every occurrence of a secret string inside obj (nested dicts/lists/strings)."""
    secrets = [s for s in secrets if s]
    if isinstance(obj, str):
        for s in secrets:
            if s in obj:
                obj = obj.replace(s, REDACTED)
        return obj
    if isinstance(obj, list):
        return [scrub(x, secrets) for x in obj]
    if isinstance(obj, dict):
        return {k: scrub(v, secrets) for k, v in obj.items()}
    return obj


_CODE_EXT = re.compile(r"\.(py|js|mjs|ts|tsx|jsx|java|kt|go|rb|cs|php|rs|swift|sql|sh|yaml|yml|toml|json|xml|ini|cfg|gradle)$", re.I)
_CAMEL = re.compile(r"^[a-z]+[A-Z][A-Za-z0-9]*$")
_SNAKE = re.compile(r"^[a-z0-9]+_[a-z0-9_]+$")
_LINE_REF = re.compile(r"\bline\s+\d+\b|\.\w{1,5}:\d+\b")


def filter_reason(reason: str, doc_text: str) -> tuple[str, bool]:
    """Withhold a judge's reason when it names something that looks like code and is not in the document."""
    if _LINE_REF.search(reason):
        return WITHHELD, True
    norm_doc = T.normalize(doc_text)
    for tok in re.findall(r"\S+", reason):
        bare = tok.strip(".,;:()[]{}\"'`*")
        if not bare:
            continue
        looks_like_code = "/" in bare or "\\" in bare or _CODE_EXT.search(bare) or _CAMEL.match(bare) or _SNAKE.match(bare)
        if looks_like_code and T.normalize(bare) not in norm_doc:
            return WITHHELD, True
    return reason, False


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def upsert_jsonl(path: Path, row: dict, keys: tuple[str, ...] = ("prompt_id", "rep")) -> None:
    rows = []
    if path.exists():
        for ln in path.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                r = json.loads(ln)
                if any(r.get(k) != row.get(k) for k in keys):
                    rows.append(r)
    rows.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def append_errors(vdir: Path, rows: list[dict]) -> None:
    path = vdir / "errors.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def update_state(flow: Path, metrics: list[dict]) -> None:
    path = flow / "_state.json"
    state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    known = {m["id"]: m for m in state.get("metrics", [])}
    for m in metrics:
        known[m["id"]] = m
    state["metrics"] = list(known.values())
    state["perf_fields"] = [{"id": f} for f in PERF_FIELDS]
    state.setdefault("harness_paths", ["design/", "design/rubrics/", "design/prompts/"])
    _write_json(path, state)


def write_run(*, flow: Path, variant: str, rep: int, case, docs, extractions: dict, checks: list[Check], scores: list[dict],
              meta: dict, private_meta: dict, digest_md: str, share_task: bool = False) -> Path:
    """Write every artifact of one run. Returns the trace path."""
    vdir = flow / variant
    share = vdir / "share" / case.id
    private = vdir / "private" / case.id
    share.mkdir(parents=True, exist_ok=True)
    private.mkdir(parents=True, exist_ok=True)
    secrets = [str(flow), str(case.source or ""), *(str(d.path) for d in docs), *(str(d.path.parent) for d in docs)]
    if case.repo and case.repo.get("commit"):
        secrets.append(str(case.repo["commit"]))
    if case.task and not share_task:
        for v in case.task.values():
            if isinstance(v, str) and len(v) > 40:
                secrets.append(v)

    for d in docs:
        shutil.copyfile(d.path, share / d.name)
    units = {"docs": [{"id": d.id, "kind": d.kind, "name": d.name, "sha256": d.sha256, **extractions[d.id].to_dict()} for d in docs]}
    _write_json(share / "units.json", scrub(units, secrets))
    check_dicts = [c.to_dict() for c in checks]
    _write_json(share / "checks.json", scrub({"scores": scores, "checks": check_dicts}, secrets))
    (share / "digest.md").write_text(scrub(digest_md, secrets), encoding="utf-8")
    if share_task and case.task:
        _write_json(share / "task.json", case.task)

    _write_json(private / "meta.json", private_meta)

    public_meta = scrub(meta, secrets)
    trace = {
        "case_id": case.id, "variant": variant, "rep": rep,
        "docs": [{"id": d.id, "kind": d.kind, "name": d.name, "sha256": d.sha256} for d in docs],
        "units": units, "checks": check_dicts, "scores": scores, "meta": public_meta,
    }
    trace_path = vdir / "traces" / f"{case.id}_rep{rep}.json"
    _write_json(trace_path, scrub(trace, secrets))

    cov = {}
    for d in docs:
        for k, v in extractions[d.id].covariates.items():
            if isinstance(v, (int, float)):
                cov[k] = cov.get(k, 0) + v
    perf = {k: cov.get(k, 0) for k in PERF_FIELDS if k in cov}
    perf.update({k: meta.get(k, 0) for k in ("cost_usd", "in_tokens", "out_tokens")})
    row = {
        "prompt_id": case.id,
        "prompt": f"{case.id}: " + ", ".join(f"{d.name} ({d.kind})" for d in docs),
        "variant": variant, "rep": rep, "status": "ok",
        "grade": {s["id"]: s["value"] for s in scores if s["value"] is not None},
        "perf": perf,
        "meta": {**public_meta, "docs": [{"name": d.name, "kind": d.kind, "sha256": d.sha256} for d in docs]},
    }
    upsert_jsonl(vdir / "results.jsonl", scrub(row, secrets))
    update_state(flow, [{"id": s["id"], "label": s["name"][:14], "kind": "binary" if s["scoring"] == "binary" else "float",
                         "scale": 1 if s["scoring"] != "count" else max(1, int(s.get("total") or 1)), "better": s["direction"]} for s in scores])
    return trace_path


def verify_share(share_dir: Path, secrets: list[str]) -> list[str]:
    """Return the names of files under share_dir that still contain a secret (expected: none)."""
    bad = []
    for p in share_dir.rglob("*"):
        if p.is_file():
            t = p.read_text(encoding="utf-8", errors="ignore")
            if any(s and s in t for s in secrets):
                bad.append(p.name)
    return bad


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
