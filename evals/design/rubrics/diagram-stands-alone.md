---
id: diagram-stands-alone
name: Diagram stands alone
unit: diagram
scoring: fraction
direction: higher
needs: [mechanical, judge]
quote_required: none
batch: 5
sources:
  - C4 diagram review checklist (title, scope, key, named and typed elements, labelled unidirectional arrows)
  - SEI Views and Beyond rule 3a (every diagram has a key)
  - Kruchten 1995 (boxes that are a bit of everything)
---

Mechanical items, per diagram: it has a title or a caption sentence right before it; a flowchart declares its direction; every node has a label, not just an id;
every edge carries a label saying what the relationship is.

Judge items, per diagram: a reader can tell what each element is (a module, a service, a store, a person); the diagram makes sense without reading the
surrounding prose; where the notation is not obvious, a key explains it. Answer each item yes or no; unknown when the item does not apply to this kind of
diagram.
