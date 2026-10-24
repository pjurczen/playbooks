---
id: non-goals
name: Non-goals that could have been goals
unit: doc
scoring: binary
direction: higher
needs: [judge]
quote_required: pass
batch: 1
sources:
  - Ubl, Design Docs at Google (non-goals are things that could reasonably be goals but are explicitly chosen not to be)
  - Kubernetes KEP template (Non-Goals section)
  - Reilly 2019, Squarespace (an explicit non-goals section added after reviews broke down)
  - Google technical writing course (a better document additionally defines its non-scope)
---

Decide whether the document names at least one thing a reader could reasonably expect this work to cover and explicitly leaves out.

Pass when such an exclusion is stated as a choice: a related change not made, a case not handled, a system not touched, a later phase. The statement may sit
anywhere in the document.

Fail when nothing is excluded, or when the only exclusions are negated requirements ("must not crash", "no data loss") or things nobody would have expected in
scope.

Unknown when you cannot tell whether an excluded item was ever a plausible part of this work.

Evidence: for a pass, quote the exclusion. A fail needs no quote.
