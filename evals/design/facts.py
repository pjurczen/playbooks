"""Draft a fact sheet (expected answers about what was decided) from a session transcript or the task brief."""
from __future__ import annotations

import json
from pathlib import Path

from . import prompts
from .case import Case
from .client import Client
from .schemas import FactsOut


def draft_facts(client: Client, case: Case, source: str = "transcript") -> list[dict]:
    if source == "transcript" and case.transcript and Path(case.transcript).is_file():
        text, name = Path(case.transcript).read_text(encoding="utf-8"), Path(case.transcript).name
    elif case.task and (case.task.get("brief") or case.task.get("request")):
        text = "Request: " + (case.task.get("request") or "") + "\n\nBrief: " + (case.task.get("brief") or "")
        name = "the task brief"
    else:
        raise ValueError("the case has neither a transcript nor a task to draft facts from")
    out: FactsOut = client.parse(FactsOut, system=prompts.system_prompt(), document=prompts.record_block(name, text),
                                 question=prompts.facts_question(), effort="medium", max_tokens=4000, label="facts-draft")
    return [{"q": f.q.strip(), "a": f.a.strip()} for f in out.facts if f.q.strip() and f.a.strip()]


def write_draft(case: Case, facts: list[dict]) -> Path:
    base = case.source.parent if case.source else Path.cwd()
    stem = case.source.stem if case.source else case.id
    path = base / f"{stem}.facts.draft.json"
    path.write_text(json.dumps({"draft": True, "case": case.id, "facts": facts}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
