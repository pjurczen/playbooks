---
id: problem-names-cause
name: The problem names a cause above its symptoms
unit: doc
scoring: binary
direction: higher
needs: [judge]
quote_required: both
batch: 1
sources:
  - Gause & Weinberg 1982, Are Your Lights On? (the problem is what the symptoms share, not the symptoms)
  - Ohno 1988, Toyota Production System (five whys; a symptom is not a cause)
  - Nygard 2011 (the context of a decision is the forces at play, not a list of observations)
---

Read the document up to the first sentence that proposes a solution: a component to add, a change to make, a mechanism to introduce. Among the sentences before
it, find the one that names a cause: the structural fact behind the symptoms, which the symptoms share and the solution removes. A cause reads like "the process
is split across two systems by person type" or "no part owns the state after the request ends".

Pass when such a sentence exists, is not the absence of the solution, and is visibly set apart from the symptoms: it is the topic sentence and the symptoms
follow it as a list or as sentences that each say what it costs; a reader can tell which sentence is the cause without working it out.

Fail when the problem is only a list of observations about today's behaviour with nothing that says why they occur together; when the cause and the symptoms are
sentences of equal standing in one block, so that the reader has to pick the cause out; when the only cause offered is "there is no X" where X is what the
document goes on to build; or when the cause appears only after the first solution sentence.

Unknown when you cannot tell which sentence first proposes a solution.

Evidence: for a pass, quote the cause sentence. For a fail, quote the sentence that comes closest to a cause, or the first solution sentence if there is none.
