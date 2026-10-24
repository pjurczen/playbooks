---
id: problem-before-solution
name: Problem stated before any solution
unit: doc
scoring: binary
direction: higher
needs: [judge]
quote_required: both
batch: 1
sources:
  - PEP 1 (submissions without sufficient motivation may be rejected)
  - Rust RFC process (an RFC without convincing motivation is poorly received)
  - Orosz 2018, Uber RFCs (the recurring reviewer question "what is the motivation to do this work?")
---

Read the document from the top. Find the first sentence that proposes or describes a solution: a component to add, a change to make, a mechanism to introduce.

Pass when, before that sentence, the document says what is wrong or missing today and for whom, specifically enough that a reader could go and check it: a
behaviour that fails, a cost that is paid, a question nobody can answer, a risk that is live.

Fail when the document opens with the solution, or when the only "problem" is the solution restated as an absence ("there is no cache", "the service lacks X")
with no consequence named, or when the problem is a ticket reference with no statement of what hurts.

Unknown when you cannot tell which sentence first proposes a solution.

Evidence: for a pass, quote the sentence that states the problem. For a fail, quote the first solution sentence.
