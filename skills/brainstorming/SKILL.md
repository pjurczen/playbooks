---
name: brainstorming
description: Use before any non-trivial creative work (a feature, a component, a behaviour change), to turn the request into an approved design through one question at a time and two or three weighed approaches.
---

# Brainstorming

Write the design for a developer who knows the codebase. The developer reads the design once, presents it and approves it. An implementer in another session
reads it once more and plans from it. Every rule here serves those two reads.

Write the design and the dialogue in Simplified Technical English. Read `references/ste.md` before you write.

<HARD-GATE>
Do not write code, scaffolding or a dependency before the user approves the written design. Do not invoke writing-plans before that approval. Three sentences
can be a sufficient design. The approval is what matters, because an unexamined assumption costs the most in simple work.
</HARD-GATE>

Do these steps in this order:

1. Look at what exists. Then ask one question at a time.
2. Lay out the approaches in a message of their own. The user picks one.
3. Write the design, short or full. Run the builder check on a full design.
4. Get approval of the written design.
5. Hand off to **writing-plans**. For an initiative, hand off to **writing-roadmap**.

## When to skip

A trivial change does not enter brainstorming. A trivial change is one that you can describe in one sentence and verify with one command. The skip list of
using-playbooks applies.

## Look before you ask

Read until you can say how the relevant parts work today and what the change touches:

- the code paths, the callers and the data that the request names
- `docs/followups.md`, for earlier attempts
- the ADRs that `.claude/documentation.md` names. They constrain the fix. A reversal of an ADR is a supersede.
- `.claude/gates.md`, for the rules that the repo enforces
- `docs/playbooks/initiatives/`, to see if this work is a slice of an initiative
- `.claude/designs.md`, for the design conventions of the repo (see below)

Do not ask a question that the repo answers.

## Your first message

- Repeat the request in your own words: what, for whom, and why.
- Add what you found that bears on it: a constraint, a conflict or a cheaper path.
- End with the one question whose answer changes the most about what gets built.

## The conversation

- **Ask one question in each message.** A message with three questions gets one answer.
- **Ask about purpose, constraints and what done looks like.** Do not ask about implementation. Implementation choices are yours to make and to explain.
- **Offer a multiple choice only when the options differ in consequence.** For each option, say what it buys and what it costs. An option without a cost leaves
  "the user chose" as the only reason on record.
- **Play back as you go.** When you understand one part, say it back in a few sentences. Then move to the next part. What the user said is theirs. What you
  filled in is your proposal, with its reason.
- **Send a gap to its owner.** Only the requester can settle a product rule or an acceptance criterion. Record such a gap as an open point. Do not fill it with
  a default.

## Lay out the approaches

Before you write anything, put the ways to build it in a message of their own:

- Give two or three real approaches, grounded in the code. Include "keep things as they are" when it is credible.
- For each approach, say what it buys and what it costs.
- Recommend one approach and say why. If only one approach fits, say why the others do not.

The costs of the rejected approaches are the reason for the chosen one. Without them, there is nothing to write down.

Then say how big the work is:

| The work                      | The design                                           |
|-------------------------------|------------------------------------------------------|
| A small change                | a short one: what you covered together, written down |
| A feature                     | the full design below                                |
| Several independent projects  | agree an order, and brainstorm one at a time         |
| Too big to land as one change | an initiative design (below), then a roadmap         |

## The written design

Save the design to `docs/playbooks/designs/YYYY-MM-DD-<topic>.md`. The title names the change. The header is `Status: draft | approved · Ticket: …`.

After one read, the reader can say:

- what hurts, and what done looks like
- what causes it
- what we will do, what it beat, and why
- which parts take part, and who owns what
- how one case travels through the parts, in order
- the rules and the contracts to build
- what it costs, and what changes for callers
- what is still open

Choose your own headings. Write a line only if it tells the reader something that is not already on the page. Describe the code of today only where it explains
the change. Do not write an inventory of the code.

**Takeaway, then detail.** Write each rule, each decision and each part as one line of not more than fifteen words. A reviewer scans the lines. Put the detail
below the line, for the implementer. Use a `<details>` block when a renderer shows the document. Otherwise indent the detail. The line says what. The detail
starts with why, then with what it beat. Then the detail adds the conditions, the edges and what fails. The detail does not repeat the line. If the detail has
more than three sentences, write it as a list. Write each item as a fold or as a table row, not both.

**The rules:**

- State the problem and its cause before any solution. State "done" as something observable.
- A decision is a sentence that a reviewer can argue with: an approach, a mechanism, a boundary, a temporary thing. The line of a decision says what. Its detail
  starts with why, then with what it beat. A "why" names a goal, a constraint, a cost or a risk. "Who decided", "what exists" and "what a guide says" are not a
  why. "What it beat" is the nearest other option and the one cost that ruled it out, in one clause.
- State each fact once, in one place. Do not write a lead-in. Do not write "unchanged" unless the reader would worry. Delete a sentence that a later edit made
  stale.
- Mark a decision that the conversation did not make as your call, with its reason, in the list of decisions. Do not put the label in the body.
- Put the open points in one list. Give each open point an owner, and say what it blocks. Do not hedge anywhere else.
- Describe the project, never the session. Do not record a check or a review. Do not list who clarified what. Do not name a reviewer. Put a point that the
  session settled into the rule or the decision that it settled.
- Give each part one sentence that says what it owns. Include the adapters. An arrow in a diagram is not a responsibility. For a part that changes, say what it
  owns afterwards. For a part that goes away, say what takes over its work. A class name is a good reference. A call chain is not.
  - Design: "The adapter maps the pairs to the `InvoiceLine` objects of the billing service."
  - Trace: "`OrderService.submit` loads the open order, delegates to the domain service and saves."
- Draw three or more parts, or ordered steps. Draw one sequence diagram that follows one case through the parts in order. That diagram is the walk-through. Do
  not retell it in prose. Write the sentence before a diagram to say which question the diagram answers. Let each node say what kind of thing it is. Let each
  edge carry a verb. Use prose to say why, not to say what the picture shows. Read `references/views.md` before you draw.
- Number and name the rules to build. Group them by stage when there is an order. Write one line for each rule, and the detail below. An edge that the code must
  handle is a rule, not a plan item.
- List the contracts that others build against, new or changed: a signature with its semantics, an endpoint with its shapes, a message, a schema change.
- Write code only as a declaration, or as a rule that a test can follow branch by branch.
- Use a table only for tabular content: contracts, open points, a mapping. Write one short sentence in each cell. Do not put detail in a cell.
- Write one thing in each sentence, in the words that a teammate says aloud. Do not join two ideas with a semicolon.
- Say what you leave out, and what gets worse.

**Initiatives.** Work that is too big to land as one change ships in slices. The old path serves between the slices. Such work gets an initiative design first:
the target state, the coexistence mechanism and the shared contracts. Save it in `docs/playbooks/initiatives/` on the base branch. Each slice then gets an
ordinary design. A slice design inherits from the initiative design and does not restate it. One change is one design, whatever the number of milestones in its
plan.

**Repo conventions.** When `.claude/designs.md` exists, apply it. It names the glossary, the kinds of diagram nodes, the source of the acceptance criteria, the
home of a story gap, the document locations and the extra review questions. Do not restate it. Use a glossary term as the glossary spells it. Do not translate
it.

## Builder check

Run this check on a full design, after you write every section. Dispatch a fresh subagent with `references/builder-check.md`. The subagent is a builder who
knows the codebase. The builder reads the design and reports where a guess is still necessary. Sort the report:

- **Answered already**: put the answer in the document.
- **Minor**: settle it yourself. Mark it in the document as your call.
- **Theirs**: bring these to the user in one message, the most important first.

Run the check once. The check catches what the author cannot see. It does not reopen the dialogue. It leaves no trace in the document.

## Approval

Before the gate, look up what the code can answer. Ask the user what the user can settle, one question at a time. An open point is a point that neither could
settle now. An open point that can change the approach blocks approval.

> "Design committed to `<path>`[, ADR at `<path>`]. Done means: …. It beat … because …. Costs: …. Open: <n>, <m> blocking. Approve, or tell me what to change."

Wait for explicit approval. If the user asks for changes, rewrite the affected text in place. Put the reason for the change in the commit message. On approval,
set `Status: approved`.

## After approval

The approved design is frozen.

- A changed decision comes back here for re-approval. A changed decision is a change to the approach, to a contract that others build against, or to a
  consequence.
- Anything smaller goes to the PR description. The end-of-feature reviewer reports every difference.
- A re-entry from executing-plans works only on that seam. Keep the workspace. Revise the `proposed` ADR in place. Re-review at the gate.

## Hand-offs

- Invoke **using-git-worktrees** when the user has chosen the approach, before you commit the design.
- Invoke **writing-adr** when the approach is a system-level choice or a rule that the team adopts. Apply its test. The `proposed` ADR commits with the design.
- After approval, invoke **writing-plans**. For an initiative, invoke **writing-roadmap**. Invoke nothing else.
