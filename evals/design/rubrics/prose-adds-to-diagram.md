---
id: prose-adds-to-diagram
name: Prose adds what the picture cannot
unit: diagram
scoring: fraction
direction: higher
needs: [mechanical, judge]
quote_required: fail
batch: 5
sources:
  - Kalyuga et al. 2003, expertise reversal (redundant explanation harms expert readers)
  - Mayer 2021, redundancy principle (re-narrating the picture adds load without information)
  - C4 notation (every element carries a description of its responsibilities; the diagram stands alone)
---

You are given the diagrams of the document, each with its id. Look at the prose directly around each diagram.

Pass when that prose states what the picture cannot: responsibilities of the elements, the reasons for the relationships, what is new or changed, what must not
happen.

Fail when the prose re-narrates the boxes and arrows ("A calls B, which writes to C"), repeating what the diagram already shows.

Unknown when there is no prose around the diagram at all.

Evidence: for a fail, quote the re-narrating sentence. A pass needs no quote.
