---
id: decisions-form-a-tree
name: Decisions ordered by what follows from what
unit: doc
scoring: binary
direction: higher
needs: [judge]
quote_required: both
batch: 1
sources:
  - Kruchten 2004, An Ontology of Architectural Design Decisions (decisions constrain, enable and subsume one another)
  - Jansen & Bosch 2005 (an architecture is a set of design decisions with dependencies among them)
  - ISO/IEC/IEEE 42010 clause 5.8 (decisions recorded with the decisions they depend on)
---

Find where the document lists its decisions. Read the first one, then each later one, and ask of each: which earlier decision does this rest on?

Pass when the first decision is the one that answers the stated problem and the others rest on it, directly or through another, and each later decision is
placed under or after the decision it follows from, so that a reader going top-down meets each premise before the decision that rests on it. Nesting, dotted
numbering (D1, D1.1) or a group heading that names the shared question all count as placement.

Fail when the first decision is a mechanism in service of a later one; when a decision rests on another that comes after it; or when the decisions are a flat
list of equal weight although one of them is the premise of the others.

Unknown when the document has fewer than three decisions, or when you cannot tell which decision the others rest on.

Evidence: for a pass, quote the first decision. For a fail, quote the decision that is out of place and name the one it should follow.
