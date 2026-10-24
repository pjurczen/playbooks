---
id: boundary-visible
name: Boundary and touchpoints visible
unit: doc
scoring: binary
direction: higher
needs: [judge]
quote_required: pass
batch: 1
sources:
  - arc42 FAQ B-4 (context and external interfaces are part of the minimum)
  - C4 System Context diagram (what the system touches)
  - Ubl, Design Docs at Google (context and scope)
  - Reilly 2019, Squarespace (surprise dependencies as a review failure)
---

Decide whether a reader could list, from the document, which existing parts of the system this change touches and which it deliberately leaves alone.

Pass when the document names the parts that change, the parts that are new, and at least one neighbouring part that stays as it is or is not touched, so that
the edge of the change is clear.

Fail when the document describes only the new parts with no statement of what around them changes or stays, or when touched parts can only be inferred from code
names in passing.

Unknown when the document covers a system you cannot tell the neighbours of from the text alone.

Evidence: for a pass, quote the passage that marks the boundary. A fail needs no quote.
