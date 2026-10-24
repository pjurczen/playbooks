---
id: diagram-earns-place
name: Diagram earns its place
unit: diagram
scoring: fraction
direction: higher
needs: [mechanical, judge]
quote_required: none
batch: 5
sources:
  - Larkin & Simon 1987 (diagrams win where content has spatial or relational structure)
  - Kalyuga et al. 2003, expertise reversal (experienced readers do better with the diagram alone)
  - Kruchten 1995 (boxes that are a bit of everything)
---

You are given the diagrams of the document, each with its id and source.

For each diagram, decide whether it shows relationships or structure a reader would otherwise have to reconstruct from prose.

Pass when the diagram has at least three elements with relationships among them, or states with transitions, or a before and an after, and those relationships
are what the reader needs to understand the approach.

Fail when the diagram draws a list, a single chain of two or three steps, or a single box, or when it mixes kinds of things (modules, classes, servers, people)
so that the picture does not answer one question, or when it only decorates a point the prose already makes as well.

Unknown when the diagram source cannot be read.

Evidence: the diagram is the unit; no quote is needed.
