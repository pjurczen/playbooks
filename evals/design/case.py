"""Cases: what to judge. A case is one design, or an initiative plus its slices, with optional task, facts and transcript."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import text as T

KINDS = ("design", "initiative", "slice")


@dataclass
class DocRef:
    kind: str
    path: Path
    initiative: Path | None = None


@dataclass
class Case:
    id: str
    docs: list[DocRef]
    task: dict | None = None
    facts: list[dict] = field(default_factory=list)
    transcript: Path | None = None
    repo: dict | None = None
    source: Path | None = None


@dataclass
class Doc:
    id: str
    kind: str
    name: str
    path: Path
    text: str
    sha256: str
    initiative: str | None = None  # basename of the initiative doc for slices

    @property
    def header(self) -> str:
        """The status line under the title (Status: ... · Ticket: ... · Initiative: ...)."""
        m = re.search(r"^Status:.*$", self.text, re.M)
        return m.group(0) if m else ""


class CaseError(ValueError):
    pass


def _resolve(base: Path, p: str) -> Path:
    q = Path(p)
    return q if q.is_absolute() else (base / q).resolve()


def load_case(path: str | Path) -> Case:
    path = Path(path).resolve()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise CaseError(f"{path}: not valid JSON ({e})") from e
    validate(raw, where=str(path))
    base = path.parent
    docs = [DocRef(d["kind"], _resolve(base, d["path"]), _resolve(base, d["initiative"]) if d.get("initiative") else None) for d in raw["docs"]]
    return Case(
        id=raw["id"],
        docs=docs,
        task=raw.get("task"),
        facts=list(raw.get("facts") or []),
        transcript=_resolve(base, raw["transcript"]) if raw.get("transcript") else None,
        repo=raw.get("repo"),
        source=path,
    )


def case_from_docs(docs: list[str], initiative: str | None = None, case_id: str | None = None) -> Case:
    refs: list[DocRef] = []
    init_path = Path(initiative).resolve() if initiative else None
    if init_path:
        refs.append(DocRef("initiative", init_path))
    for d in docs:
        p = Path(d).resolve()
        if init_path and p == init_path:
            continue
        kind = "initiative" if "initiatives" in p.parts and not init_path else ("slice" if init_path else "design")
        refs.append(DocRef(kind, p, init_path if kind == "slice" else None))
    if not refs:
        raise CaseError("no documents given")
    cid = case_id or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", refs[-1].path.stem)
    return Case(id=cid, docs=refs)


def validate(raw: dict, where: str = "case") -> None:
    if not isinstance(raw, dict):
        raise CaseError(f"{where}: top level must be an object")
    if not isinstance(raw.get("id"), str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", raw["id"]):
        raise CaseError(f"{where}: 'id' must be a path-safe string")
    docs = raw.get("docs")
    if not isinstance(docs, list) or not docs:
        raise CaseError(f"{where}: 'docs' must be a non-empty list")
    initiatives = {d.get("path") for d in docs if isinstance(d, dict) and d.get("kind") == "initiative"}
    for i, d in enumerate(docs):
        if not isinstance(d, dict) or d.get("kind") not in KINDS or not isinstance(d.get("path"), str):
            raise CaseError(f"{where}: docs[{i}] needs 'kind' in {KINDS} and a 'path'")
        if d["kind"] == "slice" and d.get("initiative") not in initiatives:
            raise CaseError(f"{where}: docs[{i}] is a slice but its 'initiative' is not one of the case's initiative docs")
    if "task" in raw and raw["task"] is not None:
        t = raw["task"]
        if not isinstance(t, dict) or not any(isinstance(t.get(k), str) for k in ("request", "brief")):
            raise CaseError(f"{where}: 'task' must be an object with 'request' and/or 'brief' strings")
    for i, f in enumerate(raw.get("facts") or []):
        if not isinstance(f, dict) or not isinstance(f.get("q"), str) or not isinstance(f.get("a"), str):
            raise CaseError(f"{where}: facts[{i}] needs 'q' and 'a' strings")
    if "repo" in raw and raw["repo"] is not None and not isinstance(raw["repo"], dict):
        raise CaseError(f"{where}: 'repo' must be an object")


def load_doc(ref: DocRef, index: int) -> Doc:
    if not ref.path.is_file():
        raise CaseError(f"document not found: {ref.path}")
    text = ref.path.read_text(encoding="utf-8")
    return Doc(f"d{index + 1}", ref.kind, ref.path.name, ref.path, text, T.sha256(text), ref.initiative.name if ref.initiative else None)


def load_docs(case: Case) -> list[Doc]:
    return [load_doc(r, i) for i, r in enumerate(case.docs)]
