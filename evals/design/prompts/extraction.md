List what this document contains, so that later questions can be asked about each item. Return only what the document actually holds; an empty list is the right
answer when there is nothing of that kind.

- key_decisions: every choice the author made that a competent reviewer could argue with (a structure, a mechanism, a boundary, a trade-off taken). For each,
  the sentence where the document makes it (quote, 5 to 40 words, verbatim), a summary of at most 15 words, and its scope: "key" when the choice changes a
  boundary, a contract or a mechanism that other parts depend on, or carries a cost or risk a reviewer would weigh; "minor" when it is a local choice with no
  consequence beyond its own unit (a name, a default, a detail of wiring). A fact about the current system is not a decision; a statement that something stays
  as it is is not a decision; a rule the design imposes on others is a decision.
- components: every part of the system the document names as taking part: modules, services, stores, jobs, interfaces. For each: its name as written, its status
  (new, changed, removed, existing), and the sentence that introduces it (quote).
- system_claims: every statement about how the existing system works today, before this change (what exists, who calls what, where something is decided). For
  each, the sentence (quote) and a summary of at most 15 words saying what is claimed to exist.
- relational_passages: every passage of prose that describes parts interacting, data flowing, states changing, or a before-and-after structure. For each, the
  first sentence of the passage (quote) and its kind.
- overview_span: the labels of the paragraphs that present the approach at a high level, before details (the part a reader would read to learn what will be
  done, not how).
- detailed_parts: every part the document describes in detail (a rule, an algorithm, a mechanism, a contract): its name, the paragraph labels that carry the
  detail, and its first sentence (quote).
- open_questions_span: the labels of the paragraphs that list unresolved questions, if any.

Quotes must be verbatim; the labels in brackets are not part of the text.
