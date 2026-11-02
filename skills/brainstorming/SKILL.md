---
name: brainstorming
description: Use before any non-trivial creative work (a feature, a component, a behaviour change), to turn the request into an approved design through one question at a time and two or three weighed approaches.
---

# Brainstorming

Two people read the design: a developer who presents and approves it, and an implementer in another session who plans from it. Every rule here serves those two
reads.

Write in ASD-STE100 (Simplified Technical English). Read `references/ste.md` before you write. The design is descriptive text. The dialogue is procedural text.

<HARD-GATE>
Do not write code, scaffolding or a dependency before the user approves the written design. Do not invoke writing-plans before that approval. Three sentences
can be a sufficient design. The approval is what matters, because an unexamined assumption costs the most in simple work.
</HARD-GATE>

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
- the ADRs that `.claude/documentation.md` names — they constrain the fix; a reversal is a supersede
- `.claude/gates.md`, for the rules that the repo enforces
- `docs/playbooks/initiatives/`, to see if this work is a slice of an initiative
- `.claude/designs.md`, for the design conventions of the repo

Do not ask a question that the repo answers.

## Your first message

- Repeat the request in your own words: what, for whom, and why.
- Add what you found that bears on it: a constraint, a conflict or a cheaper path.
- End with the one question whose answer changes the most about what gets built.

## The conversation

- **One question per message.** A message with three questions gets one answer.
- **Ask about purpose, constraints and what done looks like.** Implementation choices are yours to make and to explain.
- **Offer a choice only when the options differ in consequence.** For each option, say what it buys and what it costs. An option without a cost leaves "the user
  chose" as the only reason on record.
- **Play back as you go.** When you understand one part, say it back. What the user said is theirs. What you filled in is your proposal, with its reason.
- **Send a gap to its owner.** Only the requester can settle a product rule or an acceptance criterion. Record such a gap as an open point.

## Lay out the approaches

Put the ways to build it in a message of their own, before you write:

- Two or three real approaches, grounded in the code. Include "keep things as they are" when it is credible.
- For each approach, what it buys and what it costs.
- One recommendation, with its reason. If only one approach fits, say why the others do not.

The costs of the rejected approaches are the reason for the chosen one. Without them, there is nothing to write down.

Then say how big the work is:

| The work                      | The design                                           |
|-------------------------------|------------------------------------------------------|
| A small change                | a short one: what you covered together, written down |
| A feature                     | the full design below                                |
| Several independent projects  | agree an order, and brainstorm one at a time         |
| Too big to land as one change | an initiative design (below), then a roadmap         |

## The written design

Save to `docs/playbooks/designs/YYYY-MM-DD-<topic>.md`. Title names the change. Header: `Status: draft | approved · Ticket: …`.

After one read, the reader can say:

- what hurts and what done looks like
- what causes it
- what we will do, what it beat and why
- which parts take part and who owns what
- how one case travels through the parts
- the rules and the contracts to build
- what it costs and what changes for callers
- what is still open

Choose your own headings. Write a line only if it tells the reader something not already on the page. Describe today's code only where it explains the change.

### Shape

Each decision, rule and part is one list item. The first sentence is bold and says what, in not more than fifteen words. The next sentences, in the same item,
say why, what it beat, the conditions and what fails. No fold, table or code block for a decision, rule or part.

Show what drives what. Put the item that the others follow from first. Nest a child item under its parent, indented, and number it under the parent (D1, D1.1).
The reader sees the tree by the indentation. A number alone is not a hierarchy. When several children answer one question, name that question above them.

- **D1. The service owns the whole process.** One owner for the progress. It replaces the split across two paths, which cannot enforce one rule.
  - **D1.1. Events advance the process.** They survive a wait of days. They replace polling, which adds load.

Several things of one kind are a list, one per line: symptoms, results, costs, exclusions, tests. A paragraph holds one claim and the sentences that support it.

### Problem

Before any solution, in this order:

- **One sentence names the cause.** A cause is a structural fact: a process split across places, a state that no part owns, a rule enforced twice. "There is no
  X" is not a cause. It names what you will build.
- **The symptoms are a list under it.** Each symptom is one observable thing that a reader can check.
- **One sentence names the consequence:** what the symptoms cost, and for whom.
- **"Done" is a list of observable results,** one per line.

### Decisions

- **What a decision is:** a sentence a reviewer can argue with — an approach, a mechanism, a boundary, a temporary thing.
- **The first decision answers the cause.** Every other decision follows from it, directly or through another.
- **Nest a decision under the one it follows from.** Its first sentence then reads as "given the parent, X". Group siblings under the question they share.
- **First sentence says what.** Next sentences say why, then what it beat.
- **A valid "why"** names a goal, a constraint, a cost or a risk. "Who decided", "what exists" and "what a guide says" are not a why.
- **"What it beat"** is the nearest other option and the one cost that ruled it out, in one clause.
- **Your calls:** mark a decision the conversation did not make as your call, with its reason, in the decisions list. Do not put the label in the body.

### No repetition

- State each fact once, in one place.
- No lead-ins, no "unchanged" unless the reader would worry.
- Delete a sentence that a later edit made stale.
- A parent's first sentence summarises its children. That is structure, not repetition.

### Open points

- One list. Each open point has an owner and says what it blocks.
- Do not hedge anywhere else in the document.

### The project, not the session

- Do not record a check, a review or who clarified what.
- A point the session settled goes into the rule or the decision it settled.

### Parts and responsibilities

- **One sentence per part** says what it owns. Include the adapters.
- **Owns, not does.** "The family adapter owns the family delta" is a part. "It searches before it writes" is a decision or a rule. Write the how once, there.
- **The owning part first.** Nest an adapter under the part it serves.
- **A part that changes:** say what it owns afterwards.
- **A part that goes away:** say what takes over its work.
- **Good reference:** a class name. **Bad reference:** a call chain. An arrow in a diagram is not a responsibility.
- Design: "The adapter maps the pairs to the `InvoiceLine` objects of the billing service."
- Trace: "`OrderService.submit` loads the open order, delegates to the domain service and saves."

### Diagrams

Draw when there are three or more parts, or ordered steps. Read `references/views.md` before you draw.

- **One sequence diagram** follows one case through the parts in order. That diagram is the walk-through. Do not retell it in prose.
- **Before and after** when a part goes away or moves: one structure diagram, two subgraphs, the same names in both.
- **States** when a thing has three or more states, such as a recovery outcome: one state diagram. The rules name what moves it.
- **Caption before each diagram** says which question it answers.
- **Typed nodes, labelled edges.** Each node says what kind of thing it is. Each edge carries a verb.
- **Prose says why**, not what the picture shows.

### Rules and contracts

- **Rules:** number and name them. Group by stage when there is an order. One paragraph per rule. An edge the code must handle is a rule, not a plan item.
- **Contracts:** list the contracts that others build against, new or changed — a signature with its semantics, an endpoint with its shapes, a message, a schema
  change.
- **Code in a design:** only as a declaration, or as a rule that a test can follow branch by branch.
- **No evidence or test section.** A rule is what a test proves, and "done" is the acceptance list. A list of tests restates both. The plan names the checks.

### Tables and prose

- Use a table only for tabular content: contracts, open points, a mapping. One short sentence per cell.
- One thing per sentence, in the words a teammate says aloud. No semicolons joining two ideas.
- Say what you leave out, and what gets worse.

## Initiatives

Work too big to land as one change ships in slices. The old path serves between the slices. Such work gets an initiative design first: the target state, the
coexistence mechanism and the shared contracts. Save it in `docs/playbooks/initiatives/` on the base branch.

Each slice gets an ordinary design that inherits from the initiative and does not restate it. One change is one design, whatever the number of milestones.

## Repo conventions

When `.claude/designs.md` exists, apply it. It names the glossary, diagram node kinds, acceptance-criteria source, story-gap home, document locations and extra
review questions. Do not restate it. Use a glossary term as the glossary spells it. Do not translate it.

## Builder check

Run on a full design, after every section. Dispatch a fresh subagent with `references/builder-check.md`. The subagent is a builder who knows the codebase and
reports where a guess is still necessary. Sort the report:

- **Answered already:** put the answer in the document.
- **Minor:** settle it yourself and mark it as your call.
- **Theirs:** bring these to the user, most important first.

Run once. The check catches what the author cannot see. It does not reopen the dialogue. It leaves no trace in the document.

## Approval

Before the gate, look up what the code can answer. Ask the user what they can settle, one question at a time. An open point is one that neither could settle
now. An open point that can change the approach blocks approval.

> "Design committed to `<path>`[, ADR at `<path>`]. Done means: …. It beat … because …. Costs: …. Open: <n>, <m> blocking. Approve, or tell me what to change."

Wait for explicit approval. On changes, rewrite the affected text in place. Put the reason in the commit message. On approval, set `Status: approved`.

## After approval

The approved design is frozen.

- **Changed decision** — a change to the approach, to a contract others build against, or to a consequence — comes back here for re-approval.
- **Anything smaller** goes to the PR description. The end-of-feature reviewer reports every difference.
- **Re-entry from executing-plans** works only on that seam. Keep the workspace. Revise the `proposed` ADR in place. Re-review at the gate.

## Hand-offs

- Invoke **using-git-worktrees** when the user has chosen the approach, before you commit the design.
- Invoke **writing-adr** when the approach is a system-level choice or a rule the team adopts. Apply its test. The `proposed` ADR commits with the design.
- After approval, invoke **writing-plans**. For an initiative, invoke **writing-roadmap**. Invoke nothing else.
