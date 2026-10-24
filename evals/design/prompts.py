"""Prompt loading and assembly. The text lives in prompts/*.md; this module only fills placeholders and marks up documents."""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from .mechanical import Extraction
from .rubrics import Rubric, rubric_dir


def prompt_dir() -> Path:
    return rubric_dir().parent / "prompts"


@lru_cache(maxsize=None)
def template(name: str) -> str:
    return (prompt_dir() / f"{name}.md").read_text(encoding="utf-8").strip()


def fill(text: str, **values: str) -> str:
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", v)
    leftover = re.findall(r"{{(\w+)}}", text)
    if leftover:
        raise KeyError(f"unfilled placeholders: {leftover}")
    return text


def marked_document(doc_text: str, ex: Extraction) -> str:
    """The document with [pNN] labels in front of every prose unit, so a judge can name paragraphs by id."""
    inserts = sorted(((u.start, f"[{u.id}] ") for u in ex.units if u.kind == "paragraph"), reverse=True)
    out = doc_text
    for pos, marker in inserts:
        out = out[:pos] + marker + out[pos:]
    return out


def system_prompt() -> str:
    return template("system")


def document_block(doc_name: str, marked: str) -> str:
    return fill(template("document"), name=doc_name, document=marked)


def extraction_question() -> str:
    return template("extraction")


def judge_question(rubric: Rubric, units: list[tuple[str, str]]) -> str:
    """units: (id, text shown to the judge)."""
    listing = "\n\n".join(f"<unit id=\"{uid}\">\n{txt}\n</unit>" for uid, txt in units)
    categories = ""
    if rubric.categories:
        categories = "For every fail, set category to exactly one of: " + ", ".join(rubric.categories) + ". For a pass or unknown leave category empty."
    return fill(template("judge-question"), metric=rubric.id, name=rubric.name, rubric=rubric.body, units=listing, categories=categories)


def reader_question(facts: list[dict]) -> str:
    listing = "\n".join(f"{i}. {f['q']}" for i, f in enumerate(facts, 1))
    return fill(template("reader"), questions=listing)


def equivalence_block(question: str, expected: str, given: str) -> str:
    return fill(template("equivalence-block"), question=question, expected=expected, given=given)


def equivalence_question() -> str:
    return template("equivalence")


def facts_question() -> str:
    return template("facts")


def record_block(name: str, text: str) -> str:
    return fill(template("document"), name=name, document=text)
