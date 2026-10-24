---
id: decision-up-front
name: Decision readable in the opening
unit: doc
scoring: binary
direction: higher
needs: [judge]
quote_required: pass
batch: 1
sources:
  - Google technical writing course (summarize key points at the start)
  - HashiCorp writing practices (the proposal outlines the high-level approach first)
  - PEP 1 (the abstract states the proposal before the details)
  - BLUF, bottom line up front
---

Read only the title and roughly the first two hundred words of the document.

Pass when that opening tells a reader both what is wrong and what will be done about it, as an idea they could repeat in a sentence, before any detail.

Fail when the opening gives only the problem, only context about the current system, or only a list of sections to come, and the chosen approach first appears
later.

Unknown when the opening is cut by a diagram or table so that the two hundred words cannot be judged as prose.

Evidence: for a pass, quote the sentence in the opening that states the approach. A fail needs no quote.
