---
id: structure-drawn
name: Structure is drawn, not narrated
unit: relational_passage
scoring: fraction
direction: higher
needs: [extraction, judge]
quote_required: none
batch: 6
sources:
  - Mayer 2021, multimedia principle (words plus pictures beat words alone; the largest effect in the compilation)
  - Larkin & Simon 1987 (diagrams group related things spatially and cut search; a diagram of a list adds nothing)
  - Microsoft ISE design template (relevant diagrams: sequence, component, context, deployment)
---

You are given passages of the document that describe parts interacting, data flowing, states changing, or a before-and-after structure, each with its id and
kind.

For each passage, decide whether the structure it describes is also shown in a form a reader can scan instead of read: a diagram, a decision table, or
pseudo-code laid out step by step.

Pass when such a form in the document shows the same parts and relationships, or the same ordered steps, that the passage describes, so the prose only has to
carry the why.

Fail when the structure exists only as running prose and involves at least three parts, or three or more steps whose order matters, so a reader must reconstruct
the picture while reading.

Unknown when the passage describes two parts and one relationship, or a before and after that one sentence carries as well as a picture would.

Evidence: the passage is the unit; no quote is needed. Name the diagram, table or pseudo-code, or its absence, in the reason.
