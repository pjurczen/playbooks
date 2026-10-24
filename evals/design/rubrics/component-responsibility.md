---
id: component-responsibility
name: Every named part has a responsibility
unit: component
scoring: fraction
direction: higher
needs: [extraction, judge]
quote_required: pass
batch: 8
sources:
  - C4 notation (every element carries a short description of its key responsibilities)
  - Clements et al., Views and Beyond (an element catalog explains and defines the elements shown)
  - arc42 section 5 (describe the responsibility of every important black box)
---

You are given the components the document introduces or changes, each with its id and status.

For each component, decide whether the document says in one sentence what it is responsible for. For a changed component, what changes in its responsibility;
for a removed one, what takes over its responsibility.

Pass when such a sentence exists anywhere in the document, specific enough that a reader could say what the component must do and must not do.

Fail when the component is only named, or described only by its type ("a service", "a repository"), or by what it calls, or when a changed component has no
statement of what changes.

Unknown when the component is marked existing and the document does not need to describe it.

Evidence: for a pass, quote the responsibility sentence. A fail needs no quote.
