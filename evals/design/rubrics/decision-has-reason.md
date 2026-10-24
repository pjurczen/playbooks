---
id: decision-has-reason
name: A reason for every decision
unit: decision
scoring: fraction
direction: higher
needs: [extraction, judge]
quote_required: pass
batch: 8
sources:
  - ISO/IEC/IEEE 42010 clause 5.8.2 (rationale for each key architecture decision)
  - arc42 section 9 (document the reasons for decisions)
  - Nygard 2011 (an ADR records the context and the forces behind the decision)
  - Architecture haiku (every decision with its driving quality)
---

You are given the decisions found in the document, key and minor, each with the sentence where the document makes it.

For each decision, decide whether the document gives a reason for it that is tied to something named on the page: a goal, a constraint, a quality the design
must have, a cost it avoids, or a fact about the system it responds to.

Pass when such a reason is present somewhere in the document, even in one clause, and a reader could check it against the rest of the page.

Fail when no reason is given; when the reason only restates the decision in other words ("we use X because X is the approach"); or when the reason is a bare
quality word ("cleaner", "simpler", "standard") with nothing on the page that makes it checkable.

Unknown when you cannot tell from the document whether the stated reason refers to something real in this system.

Evidence: for a pass, quote the reason (verbatim, up to 40 words). For a fail, quote the sentence that makes the decision.
