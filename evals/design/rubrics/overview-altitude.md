---
id: overview-altitude
name: Overview stays at overview altitude
unit: overview_sentence
scoring: count
direction: lower
needs: [extraction, judge]
quote_required: none
batch: 15
sources:
  - Ubl, Design Docs at Google (overview first, then details; an implementation manual is not a design)
  - Kubernetes KEP template (the Proposal must not include API designs or implementation)
  - Rust RFC template (guide-level explanation before the reference-level one)
  - HashiCorp RFC template (the proposal outlines the high-level approach; details go in later sections)
---

You are given the sentences of the part of the document that presents the approach at a high level, each with its id.

For each sentence, decide whether it stays at the altitude of components and responsibilities, or drops to implementation.

Pass when the sentence speaks of components, what they are responsible for, what moves between them, and why.

Fail when the sentence names a file, a class or method, a function, a field or column, a flag or configuration key, a library call, or a line-level step ("then
it calls X and sets Y"), or walks a call chain. A component named as a team would draw it on a whiteboard is not a failure; a method name is.

Unknown when you cannot tell whether a name refers to a component or to a code symbol.

Evidence: the sentence is the unit; no quote is needed. Name the offending term in the reason.
