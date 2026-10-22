---
id: no-fact-twice
name: No fact stated twice
unit: duplicate_pair
scoring: count
direction: lower
needs: [mechanical, judge]
quote_required: fail
batch: 10
sources:
  - SEI Views and Beyond rule 2 (avoid unnecessary repetition)
  - arc42 section 9 (avoid redundant texts)
  - Aghajani et al. 2020 (duplicate content)
  - Meng et al. 2019 (repeat a critical point where a skimmer lands)
---

You are reading a software design document the way a reviewer would, once, before a meeting. The document is shown in full with each paragraph labelled. You are
given pairs of sentences from different paragraphs that say nearly the same thing.

For each pair, decide whether it is the same fact stated twice in two places, or a constraint deliberately restated at the place where it applies.

Fail when the second sentence adds nothing a reader at that place needs: it repeats a decision, a rule, a consequence or a description that the other sentence
already carries, and the reader who reached the second one has already read the first.

Pass when the second sentence is a short reminder of a constraint at the point where the reader must apply it, or when the two sentences share words but state
different facts.

Unknown when you cannot tell from the document whether the two places serve different readers.

Evidence: for a fail, quote the second sentence (verbatim, up to 40 words). Quotes must be copied exactly from the document. Your reason is at most 30 words and
refers only to the document.
