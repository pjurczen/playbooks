---
id: code-justified
name: Code only where prose cannot say it
unit: code_block
scoring: fraction
direction: higher
needs: [mechanical, judge]
quote_required: none
batch: 5
sources:
  - Ubl, Design Docs at Google (design docs should rarely contain code except for novel algorithms; copied interfaces quickly get out of date)
  - C4 Code level (optional, only for the most important or complex components)
  - Uddin & Robillard 2015 (excess structural information is available from the IDE)
---

You are given the code blocks of the document, each with its id. For each block, decide whether it says something prose could not say as precisely.

Pass when the block is a rule or algorithm stated as pseudo-code or a decision table that a test could follow branch by branch; a contract others build against,
shown as declarations only (a signature with its semantics, an endpoint with request and response, a schema, a configuration key); or a small example whose
exact shape matters.

Fail when the block is implementation body (statements, control flow, error plumbing), a copy of code that already exists in the system, a class listing, or
something a sentence would state as well ("the method returns the cached value").

Unknown when you cannot tell from the document whether the code exists already or is new.

Evidence: the block itself is the unit; no quote is needed. Say in the reason which kind it is.
