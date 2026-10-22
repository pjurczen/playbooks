---
id: paragraph-earns-place
name: Every paragraph earns its place
unit: paragraph
scoring: fraction
direction: higher
needs: [mechanical, judge]
quote_required: fail
batch: 10
sources:
  - Mayer 2021, coherence principle (exclude extraneous material; median d 0.86)
  - Aghajani et al. 2020 (superfluous content, conciseness)
  - Garousi et al. 2015 (larger documents are less cost-effective)
  - HashiCorp writing practices (excess detail as a common pitfall)
---

For each paragraph you are asked about, decide: if this paragraph were deleted, would the reader lose something they need and cannot get elsewhere on the page?
Something they need is a decision, a reason, a boundary of the change, a rule that gets built, a cost, or a fact about the system that the reader could not see
by opening the code.

Pass when the paragraph carries at least one such thing that no other part of the document states. A short paragraph passes if the one thing it says is new on
the page. A one-sentence reminder of a constraint at the place where it applies passes when that place needs it.

Fail when the paragraph only repeats what the document already says elsewhere, describes how the current code works at a level a reader could get by opening it,
walks through a sequence of calls, pads a point already made, or exists because the text above it seemed to call for more text. Also fail a paragraph that says
only that something stays as it is, unless a reader would otherwise worry that it changed.

Unknown when you cannot tell whether the fact is available elsewhere without seeing the code, or when the paragraph is a fragment you cannot judge on its own.

Evidence: for every fail, quote the other passage of the document that already carries the same content; when the problem is code-level description or padding,
quote the sentence that shows it. A pass needs no quote.
