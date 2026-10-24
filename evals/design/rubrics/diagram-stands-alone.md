---
id: diagram-stands-alone
name: Diagram stands alone
unit: diagram
scoring: fraction
direction: higher
needs: [mechanical, judge]
quote_required: none
batch: 6
items: [kinds-clear, standalone, key]
sources:
  - C4 diagram review checklist (title, scope, key, named and typed elements, labelled unidirectional arrows)
  - SEI Views and Beyond rule 3a (every diagram has a key)
  - Kruchten 1995 (boxes that are a bit of everything)
---
Mechanical items, per diagram: it has a title or a caption sentence right before it; a flowchart declares its direction; every node has a label, not just an id;
every edge carries a label saying what the relationship is.

Judge items, per diagram, each asked as its own unit `<diagram id>:<item>`:

- kinds-clear: a reader can tell what each element is (a module, a service, a store, a person, an external system) from its label or shape.
- standalone: the diagram makes sense without reading the surrounding prose: a reader learns what interacts with what and why from the picture and its labels
  alone.
- key: where the notation is not obvious (colours, shapes, line styles, a before and an after), a key or the title explains it; unknown when the notation is
  plain boxes and labelled arrows and needs no key.

Evidence: the diagram is the unit; no quote is needed.
