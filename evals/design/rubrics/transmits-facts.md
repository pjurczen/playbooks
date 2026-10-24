---
id: transmits-facts
name: A reader can answer the key questions from the document alone
unit: fact
scoring: fraction
direction: higher
needs: [facts]
quote_required: none
sources:
  - QAGS, Wang et al. 2020 (question answering as a measure of whether a text carries the facts)
  - QuestEval, Scialom et al. 2021 (questions written from the ground truth, asked of a reader of the document)
---

The comprehension probe. A reader that sees only the document answers each fact-sheet question; a second call judges whether the answer states the same fact as
the expected one. The questions come from what was decided and constrained in the conversation that produced the design, not from the document, so a pass means
the document transmitted the decision.
