"""Rubrics: one markdown file per metric, frontmatter for the mechanics, body for the judge."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path

UNITS = ("doc", "paragraph", "heading", "code_block", "diagram", "duplicate_pair", "overview_sentence", "decision", "component",
         "claim", "detailed_part", "relational_passage", "fact", "slice")
NEEDS = ("mechanical", "extraction", "facts", "set", "judge", "derived")


@dataclass
class Rubric:
    id: str
    name: str
    unit: str
    scoring: str  # binary | fraction | count
    direction: str = "higher"  # higher | lower
    applies_to: list[str] = field(default_factory=lambda: ["design", "initiative", "slice"])
    needs: list[str] = field(default_factory=list)
    quote_required: str = "both"  # pass | fail | both | none
    batch: int = 10
    sources: list[str] = field(default_factory=list)
    optional: bool = False
    scope: str = ""  # for decision units: "key" restricts the rubric to key decisions
    categories: list[str] = field(default_factory=list)  # a judge labels every fail with one of these
    derived_from: str = ""  # computed from another rubric's checks instead of its own judge calls
    category: str = ""  # with derived_from: the category of the source checks that count as fails here
    items: list[str] = field(default_factory=list)  # judge items per unit (unit:item)
    body: str = ""
    path: Path | None = None

    @property
    def has_mechanical(self) -> bool:
        """The rubric has a part that runs without a model (it may also have judge items)."""
        return "mechanical" in self.needs


class RubricError(ValueError):
    pass


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Minimal YAML subset: `key: scalar` and `key: [a, b]`; quoted scalars allowed; no nesting."""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        raise RubricError("missing frontmatter")
    meta: dict = {}
    current: str | None = None  # key of an open block list
    for ln in m.group(1).split("\n"):
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        if current and re.match(r"\s+-\s", ln):
            meta[current].append(ln.strip()[1:].strip().strip("'\""))
            continue
        current = None
        k, _, v = ln.partition(":")
        k, v = k.strip(), v.strip()
        if v == "":
            meta[k] = []
            current = k
        elif v.startswith("[") and v.endswith("]"):
            meta[k] = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
        elif v.lower() in ("true", "false"):
            meta[k] = v.lower() == "true"
        elif re.fullmatch(r"-?\d+", v):
            meta[k] = int(v)
        else:
            meta[k] = v.strip("'\"")
    return meta, m.group(2).strip()


def _from_file(path: Path) -> Rubric:
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    for k in ("id", "name", "unit", "scoring"):
        if k not in meta:
            raise RubricError(f"{path.name}: frontmatter needs '{k}'")
    if meta["unit"] not in UNITS:
        raise RubricError(f"{path.name}: unknown unit {meta['unit']!r}")
    if meta["scoring"] not in ("binary", "fraction", "count"):
        raise RubricError(f"{path.name}: scoring must be binary, fraction or count")
    needs = meta.get("needs", [])
    for n in needs:
        if n not in NEEDS:
            raise RubricError(f"{path.name}: unknown need {n!r}")
    if meta["id"] != path.stem:
        raise RubricError(f"{path.name}: id {meta['id']!r} must match the file name")
    return Rubric(
        id=meta["id"], name=meta["name"], unit=meta["unit"], scoring=meta["scoring"], direction=meta.get("direction", "higher"),
        applies_to=meta.get("applies_to", ["design", "initiative", "slice"]), needs=needs, quote_required=meta.get("quote_required", "both"),
        batch=int(meta.get("batch", 10)), sources=meta.get("sources", []), optional=bool(meta.get("optional", False)),
        scope=str(meta.get("scope", "")), categories=list(meta.get("categories", [])), derived_from=str(meta.get("derived_from", "")),
        category=str(meta.get("category", "")), items=list(meta.get("items", [])), body=body, path=path,
    )


def rubric_dir() -> Path:
    return Path(str(resources.files("design") / "rubrics"))


def load_rubrics(directory: Path | None = None) -> dict[str, Rubric]:
    d = directory or rubric_dir()
    out = {}
    for p in sorted(d.glob("*.md")):
        r = _from_file(p)
        out[r.id] = r
    return out


def select(rubrics: dict[str, Rubric], metrics: list[str] | None, *, mechanical_only: bool, doc_kinds: set[str], has_facts: bool, multi_doc: bool,
           mechanical_ids: set[str] | None = None) -> list[Rubric]:
    if metrics:
        unknown = [m for m in metrics if m not in rubrics]
        if unknown:
            raise RubricError(f"unknown metrics: {', '.join(unknown)}; known: {', '.join(sorted(rubrics))}")
    chosen = []
    for r in rubrics.values():
        if metrics and r.id not in metrics:
            continue
        if not metrics and r.optional:
            continue
        if mechanical_only and (r.id not in (mechanical_ids or set()) if mechanical_ids is not None else not r.has_mechanical):
            continue
        if r.derived_from and (mechanical_only or (metrics and r.derived_from not in metrics)):
            continue
        if "facts" in r.needs and not has_facts:
            continue
        if "set" in r.needs and not multi_doc:
            continue
        if not (set(r.applies_to) & doc_kinds):
            continue
        chosen.append(r)
    return chosen
