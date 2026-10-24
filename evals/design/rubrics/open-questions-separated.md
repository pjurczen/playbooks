---
id: open-questions-separated
name: Open questions in one place
unit: doc
scoring: binary
direction: higher
needs: [extraction, judge]
quote_required: fail
batch: 1
sources:
  - Rust RFC template (Unresolved questions section)
  - Spolsky 2000 (open issues marked as such in the spec)
  - SEI TN-030 (placeholders for what has yet to be documented)
---

Decide whether every unresolved point in the document is gathered in one place and marked for who answers it or what it blocks, and whether the rest of the
document speaks with decision.

Pass when open points appear only in a dedicated list, each with an owner or a note of what it blocks, and the decision text elsewhere does not hedge
("probably", "to be decided", "we assume", "TBD") or ask questions it does not answer.

Fail when a hedge or an unanswered question appears in decision text outside that list, when the list exists but entries have no owner or blocking note, or when
questions are scattered through several sections.

Unknown when you cannot tell whether a sentence is a hedge or a deliberate statement of a tolerance.

Evidence: for a fail, quote the stray hedge or question. A pass needs no quote.
