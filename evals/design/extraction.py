"""LLM extraction: the units a judge cannot find mechanically, anchored to the text and given ids by position."""
from __future__ import annotations

from dataclasses import dataclass

from . import prompts, text as T
from .case import Doc
from .client import Client
from .mechanical import Extraction, Unit
from .schemas import ExtractionOut

LLM_KINDS = {"key_decisions": ("dec", "decision"), "components": ("cmp", "component"), "system_claims": ("clm", "claim"),
             "relational_passages": ("rel", "relational_passage"), "detailed_parts": ("det", "detailed_part")}


@dataclass
class Anchored:
    kind: str
    start: int
    end: int
    quote: str
    meta: dict


def _anchor(doc: Doc, items: list[dict], kind: str) -> tuple[list[Anchored], int]:
    out, dropped = [], 0
    for it in items:
        span = T.find_quote(doc.text, it.get("quote", ""), min_words=3)
        if span is None:
            dropped += 1
            continue
        meta = {k: v for k, v in it.items() if k != "quote"}
        out.append(Anchored(kind, span[0], span[1], doc.text[span[0]:span[1]], meta))
    return out, dropped


def _valid_paragraphs(ex: Extraction, labels: list[str]) -> list[str]:
    known = {u.id for u in ex.units if u.kind == "paragraph"}
    return [p for p in labels if p in known]


def extract_llm(client: Client, doc: Doc, ex: Extraction, *, max_attempts: int = 2) -> dict:
    """Add decision/component/claim/relational/detailed units and the overview and open-questions spans to `ex` in place.

    Returns a small report (counts, dropped quotes). Drops any item whose quote cannot be anchored; if more than a third of the items
    fail to anchor, the whole call is repeated once.
    """
    marked = prompts.marked_document(doc.text, ex)
    system = prompts.system_prompt()
    document = prompts.document_block(doc.name, marked)
    question = prompts.extraction_question()
    report: dict = {}
    for attempt in range(1, max_attempts + 1):
        out: ExtractionOut = client.parse(ExtractionOut, system=system, document=document, question=question, effort="medium",
                                          max_tokens=8000, label=f"extract-{doc.id}" + ("" if attempt == 1 else f"-r{attempt}"))
        data = out.model_dump()
        anchored: list[Anchored] = []
        total = dropped = 0
        for field, (_prefix, kind) in LLM_KINDS.items():
            got, d = _anchor(doc, data[field], kind)
            anchored.extend(got)
            total += len(data[field])
            dropped += d
        report = {"items": total, "dropped": dropped, "attempt": attempt}
        if total == 0 or dropped <= total / 3:
            break
    # remove units from any earlier extraction, then add these, ids by position within kind
    ex.units = [u for u in ex.units if u.kind not in {k for _, k in LLM_KINDS.values()}]
    for _field, (prefix, kind) in LLM_KINDS.items():
        items = sorted((a for a in anchored if a.kind == kind), key=lambda a: a.start)
        for i, a in enumerate(items, 1):
            meta = dict(a.meta)
            if kind == "detailed_part":
                meta["paragraphs"] = _valid_paragraphs(ex, meta.get("paragraphs", []))
            ex.units.append(Unit(f"{prefix}-{i:02d}", kind, a.start, a.end, a.quote, T.sha8(a.quote), meta))
    ex.spans["overview"] = _valid_paragraphs(ex, data["overview_span"]["paragraphs"])
    ex.spans["open_questions"] = _valid_paragraphs(ex, data["open_questions_span"]["paragraphs"])
    ex.covariates.update({
        "decisions": sum(1 for u in ex.units if u.kind == "decision"),
        "components": sum(1 for u in ex.units if u.kind == "component"),
        "claims": sum(1 for u in ex.units if u.kind == "claim"),
    })
    return report


def claims_markdown(doc: Doc, ex: Extraction) -> str:
    """claims.md: the statements about the existing system, for a check against the code elsewhere."""
    lines = [f"# Claims about the existing system in `{doc.name}`", "", "Each is a statement the design makes about what exists today. Check it against the code at the pinned commit.", ""]
    for u in ex.units:
        if u.kind == "claim":
            lines.append(f"- **{u.id}** — {u.meta.get('summary', '')}\n  > {u.text}")
    if len(lines) == 4:
        lines.append("_No claims about the existing system were found._")
    return "\n".join(lines) + "\n"
