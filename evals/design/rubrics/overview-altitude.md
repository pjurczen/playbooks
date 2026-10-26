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

You are given the sentences of the part of the document that presents the approach at a high level, each with its id. The readers know the codebase: a developer
who owns the feature and an implementer who will look every name up.

For each sentence, decide whether what it says is a statement about parts, responsibilities, data and reasons, or a description of how the code runs.

Pass when the sentence says what a part does, what it is responsible for, what moves between parts, under what condition, or why. A class, interface, type,
field, endpoint or value named as the name of a component, a contract or a piece of data is not a failure, with or without backticks: it is the shortest precise
reference to the thing. "The adapter maps the pairs to the billing service's `InvoiceLine` objects" passes; so does "the client states the channel when it
creates the order".

Fail when the content of the sentence is a code-level step or placement: which method is called and in what order, what a method loads or sets, a signature or a
path given as the proposal, which annotation, flag or configuration key is used, or test-level detail. The test: replace every name with its role and ask
whether what remains still describes parts and responsibilities, or narrates the code. "`OrderService.submit` loads the open order, delegates to the domain
service and saves the change" fails: it is a call chain.

Unknown when you cannot tell from the document whether the sentence describes a part or a procedure.

Evidence: the sentence is the unit; no quote is needed. Name the offending step in the reason.
