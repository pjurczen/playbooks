"""Structured-output schemas for every model call. Every field is required so the schema is strict and the parse deterministic."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Quoted(_Strict):
    quote: str
    summary: str


class ComponentOut(_Strict):
    name: str
    status: Literal["new", "changed", "removed", "existing"]
    quote: str


class RelationalOut(_Strict):
    quote: str
    kind: Literal["interaction", "data_flow", "states", "before_after"]


class DetailedPartOut(_Strict):
    name: str
    paragraphs: list[str]
    quote: str


class Span(_Strict):
    paragraphs: list[str]


class ExtractionOut(_Strict):
    key_decisions: list[Quoted]
    components: list[ComponentOut]
    system_claims: list[Quoted]
    relational_passages: list[RelationalOut]
    overview_span: Span
    detailed_parts: list[DetailedPartOut]
    open_questions_span: Span


class CheckOut(_Strict):
    unit: str
    verdict: Literal["pass", "fail", "unknown"]
    quote: str
    reason: str


class JudgeOut(_Strict):
    metric: str
    checks: list[CheckOut]


class AnswerOut(_Strict):
    question: str
    answer: str


class ReaderOut(_Strict):
    answers: list[AnswerOut]


class EquivalenceOut(_Strict):
    equivalent: bool
    reason: str


class FactOut(_Strict):
    q: str
    a: str


class FactsOut(_Strict):
    facts: list[FactOut]
