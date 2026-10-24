---
id: decision-up-front
name: Title or first paragraph says what is proposed
unit: doc
scoring: binary
direction: higher
needs: [judge]
quote_required: pass
batch: 1
sources:
  - Google technical writing course (summarize key points at the start)
  - PEP 1 (the abstract states the proposal before the details)
  - Bhat et al. 2026 (reviewers read the title, the first line, then the headings)
---

Read only the title and the first paragraph of the document, not the sections after it. The body of a design rightly opens with the problem and its context;
this check asks only whether a reader skimming the top can already say what is being proposed.

Pass when the title or the first paragraph lets a reader state the proposal in one sentence: the thing that will exist or change, named as an idea, not as a
ticket number or a section name. A title that carries the idea passes on its own.

Fail when the title is only a ticket, a feature name or a component name, and the first paragraph speaks only of the current system and its problem, so that
what is proposed first appears further down.

Unknown when the title is in a language or vocabulary you cannot judge, or when there is no prose before the first heading.

Evidence: for a pass, quote the title or the sentence that states the proposal. A fail needs no quote.
