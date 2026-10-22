---
id: alternatives-with-reasons
name: Alternatives named with the reason they lost
unit: decision
scoring: fraction
direction: higher
needs: [extraction, judge]
quote_required: pass
batch: 5
sources:
  - Ubl, Design Docs at Google (alternatives considered is one of the most important sections)
  - Rust RFC template (why is this design the best in the space of possible designs)
  - Calçado 2018, SoundCloud RFC process (alternatives always include Do Nothing)
  - ISO/IEC/IEEE 42010 (rationale for each key architecture decision, considered alternatives)
  - SEI Views and Beyond rule 5 (record the alternatives you rejected and why)
---

You are given key decisions found in the document, each with the sentence where the document makes it.

For each decision, decide whether the document names at least one other option that could really have been taken for this decision, including doing nothing or
keeping things as they are, and gives the reason that option lost.

Pass when both are present somewhere in the document: an alternative that a competent engineer could have chosen here, and a reason it was rejected that a
reader could argue with: a cost, a risk, a constraint it breaks, a goal it misses, or the condition under which it would have been the right choice. The
alternative and its reason may sit in a different place from the decision.

Fail when no alternative is named for this decision; when the only alternative is one nobody would choose; when an alternative is named but the reason is
missing or only restates the choice; or when the reason is a bare label such as "simpler" or "cleaner" with nothing in the document that makes it checkable.

Unknown when you cannot tell from the document alone whether a named option is realistic for this system.

Evidence: for a pass, quote the passage that names the alternative together with its reason; if they are apart, quote the reason. For a fail, quote the sentence
that names an alternative without a reason if there is one; otherwise give no quote.
