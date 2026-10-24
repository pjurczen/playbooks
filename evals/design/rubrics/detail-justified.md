---
id: detail-justified
name: Detail spent only where it is not routine
unit: detailed_part
scoring: fraction
direction: higher
needs: [extraction, judge]
quote_required: pass
batch: 6
sources:
  - arc42 section 5 (refine only the important, surprising, risky, complex or volatile building blocks)
  - Fairbanks, risk-driven architecture (detail in proportion to perceived failure risk)
  - Clements et al., Views and Beyond (the essence of architecture is the suppression of information not necessary to the task at hand)
---

You are given the parts the document describes in detail, each with its id and the paragraphs that carry the detail.

For each part, decide whether the document says, or makes evident, why this part deserves detail.

Pass when the detail is a rule, algorithm, state machine or contract that a reviewer must check or a test must follow, or when the document says the part is
risky, novel, complex, volatile or load-bearing, or when getting it wrong would be costly in a way the document names.

Fail when the detailed part is routine wiring, mapping, configuration or plumbing that follows from the approach with no stated reason to spell it out, or when
the detail restates what the code would show anyway.

Unknown when you cannot tell from the document whether the part is routine in this system.

Evidence: for a pass, quote the sentence that gives the reason or states the rule. A fail needs no quote.
