---
id: success-criterion
name: How we will know it worked
unit: doc
scoring: binary
direction: higher
needs: [judge]
quote_required: pass
batch: 1
optional: true
sources:
  - Kubernetes KEP template (how will we know that this has succeeded?)
  - Microsoft ISE feature design template (acceptance criteria required to meet the definition of done)
  - Ubl, Design Docs at Google (goals without a success metric; the element is disputed between templates)
---

Optional check, disputed between published templates. Decide whether the document states an observable outcome that would show the change achieved its goal.

Pass when the document names something a person could observe or measure after the change that is true only if the goal was reached: a behaviour that now
happens, a number that moves, a failure that no longer occurs.

Fail when the goal is stated only as the solution being in place ("the cache exists"), or not at all.

Unknown when the outcome named could be observed but you cannot tell whether it depends on this change.

Evidence: for a pass, quote the outcome. A fail needs no quote.
