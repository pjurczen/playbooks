---
id: headings-carry-meaning
name: Headings say what the section holds
unit: heading
scoring: fraction
direction: higher
needs: [mechanical, judge]
quote_required: none
batch: 15
sources:
  - Lorch & Lorch 1996 (headings improve recall of unfamiliar or complex topic structures)
  - Google technical writing course, large documents (headings let readers navigate and skip)
  - Bhat et al. 2026 (reviewers read the title, the first line, then headings and subheadings)
  - Clements et al., Views and Beyond rule 4 (use a standard organization)
---

You are given the headings of the document, each with its id.

For each heading, decide whether a reader who sees only this heading can tell what the section contains or decides well enough to choose whether to read or skip
it.

Pass when the heading names the content specifically (a part, a rule, a question answered), or is one of a document's standard top-level sections whose meaning
readers know (the problem, the approach, decisions, architecture, consequences, open questions).

Fail when the heading is vague ("Details", "Other", "Notes", "Misc"), when it does not match what the section contains, or when several headings in the document
are identical.

Unknown when you cannot judge the match because the section is empty.

Evidence: the heading is the unit; no quote is needed.
