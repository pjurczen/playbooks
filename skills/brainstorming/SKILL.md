---
name: brainstorming
description: Use before any non-trivial creative work (a feature, a component, a behaviour change), to turn the request into an approved design through one question at a time and two or three weighed approaches.
---

# Brainstorming

You are about to design something for a developer who knows the codebase. They read the design once, present it and approve it; an implementer in another
session reads it once more and plans from it. Everything here serves those two reads.

<HARD-GATE>
No code, scaffolding, dependency or writing-plans until the user approves the written design. Three sentences can be enough; the approval is what matters,
because "simple" is where unexamined assumptions cost the most.
</HARD-GATE>

Before anything gets built, in order:

1. Look at what exists, then ask one question at a time.
2. Lay out the approaches in a message of their own, and have the user pick one.
3. Write the design, short or full, and run the builder check on a full one.
4. Get the user's approval of the written design.
5. Hand off: **writing-plans**, or **writing-roadmap** for an initiative.

## When to skip

A change you can describe in one sentence and verify with one command never enters brainstorming; using-playbooks' skip list handles it.

## Look before you ask

Read until you can say how the relevant parts work today and what the change would touch:

- the code paths, callers and data the request names
- `docs/followups.md`, for earlier attempts
- the ADRs that `.claude/documentation.md` names; they constrain the fix, and reversing one is a supersede
- `.claude/gates.md`, the rules the repo enforces
- `docs/playbooks/initiatives/`, in case this is a slice of one
- `.claude/designs.md`, the repo's design conventions (below)

A question the repo answers wastes the user's turn and anchors the design on their guess.

## Your first message

- Echo the request in your own words: what, who it is for, why, as far as they said it.
- Add what you found that bears on it: a constraint, a conflict, a cheaper path.
- End with the one question whose answer most changes what gets built.

## The conversation

**One question per message.** A message with three questions gets one answered.

**Ask about purpose, constraints and what done looks like.** Never about implementation: a choice the code can settle is yours to make and explain.

**Multiple choice only when the options differ in consequence.** Each option says in one line what it buys and what it costs. An option without a cost yields a
decision whose written reason is "the user chose", which is no reason.

**Play back as you go.** When you understand one part, say it back briefly, then move to the next. What they said is theirs. What you filled in is your
proposal, with its reason, because a default they never heard is one they could not reject.

**A gap goes to its owner.** A product rule, a missing acceptance criterion, anything only the request's owner can close becomes an open question with that
owner, never a silent answer.

## Lay out the approaches

Once you understand what they want, and before you write anything, put the ways of building it in a message of their own:

- Two or three real ones, grounded in the code. Keeping things as they are is one of them when it is credible.
- For each: what it buys and what it costs.
- Recommend one and say why. When only one fits, say why the others do not.

The chosen approach's reason can only be written down if the losers' costs were stated.

Then size the work, and say so:

| The work                       | The design                                              |
|--------------------------------|---------------------------------------------------------|
| A small change                 | a short one: what you covered together, written down    |
| A feature                      | the full written design below                           |
| Several independent projects   | agree an order; brainstorm one at a time                |
| Too big to land as one change  | an initiative design (below), then a roadmap            |

## The written design

Save to `docs/playbooks/designs/YYYY-MM-DD-<topic>.md` with a title that names the change and the header `Status: draft | approved · Ticket: …`.

After one read, the reader can say:

- what hurts, and what done looks like
- what causes it
- what we will do, what it beat, and why
- which parts take part and who owns what
- the rules and contracts that get built
- what it costs, and what changes for callers
- what is still open

Headings are yours. No section exists because a template lists it.

**The rules, each with its reason:**

- **Problem and cause before any solution**, with done as something observable. A reader who meets the solution first cannot judge it.
- **Every decision carries its reason and what it beat**, where it is made. "Simpler" counts only when the page shows what is simpler.
- **One fact, one place.** No lead-ins, no "unchanged" unless the reader would worry, no sentence a later edit made stale. The reader stops at the first
  repetition.
- **Open points in one list**, each with its owner or what it blocks, and no hedge anywhere else. A "probably" inside a decision is a question not asked.
- **Altitude.** Say what a part is responsible for, what moves between parts, when, and why. A class or type name is the shortest precise reference and welcome;
  a call chain, a signature or a flag given as the proposal is not.
  - Design: "The adapter maps the pairs to the billing service's `InvoiceLine` objects."
  - Trace: "`OrderService.submit` loads the open order, delegates to the domain service and saves."
- **Draw structure.** Three or more parts, or ordered steps, get a diagram, a table or pseudo-code, with a caption, typed nodes and labelled edges. Prose
  carries the why, never a narration of the picture. Read `references/views.md` before drawing.
- **Code only as a declaration with its semantics**, or as a rule a test can follow branch by branch.
- **Name what a reader would expect and you leave out**, and what gets worse.

**Initiatives.** Work too big to land as one change ships in slices, the old path serving in between. It gets an initiative design first, in
`docs/playbooks/initiatives/` on the base branch: the target state, the coexistence mechanism, the shared contracts. Each slice then gets an ordinary design
that inherits from it and never restates it. One change, however many milestones its plan has, is one design.

**Repo conventions.** `.claude/designs.md`, when present, carries the repo's vocabulary, the node kinds its diagrams use, where acceptance criteria come from
and where story gaps go, document locations, extra review questions. Apply it; never restate it in the design.

## Builder check

For a full design, dispatch a fresh subagent with `references/builder-check.md`: a builder who knows the codebase reads the design to plan from and reports
where they would still have to guess. Sort what comes back into three piles:

- **Answered already**, by the conversation or the code: put the answer in the document.
- **Minor**: a sensible builder could settle it without changing what gets built. Settle it yourself and mark it in the document as your call.
- **Theirs**: only the user can answer, and the answer changes what gets built. Bring these in one message, most important first.

One round. The check exists to catch what the author cannot see, not to reopen the dialogue.

## Approval

> "Design committed to `<path>`[, ADR at `<path>`]. Done means: …. It beat … because …. Costs: …. Open: <n>, owners named. Approve, or tell me what to change."

Wait for explicit approval. On changes, rewrite the affected sentences in place; why they changed belongs in the commit message, not in the document. On
approval set `Status: approved`.

## After approval

The approved design is frozen.

- A changed decision comes back here and is re-approved: the approach, a contract others build against, a consequence.
- Anything smaller goes to the PR description, where the end-of-feature reviewer reports every difference.
- Re-entry from executing-plans works only that seam: keep the workspace, revise the `proposed` ADR in place if the decision changed, re-review at the gate.

## Hand-offs

- **using-git-worktrees** once the approach is chosen and before the design is committed, so every artifact lands on the feature branch.
- **writing-adr** when the approach is a system-level choice or instantiates a rule the team adopts, by its test; the `proposed` ADR commits with the design.
- **writing-plans** after approval, or **writing-roadmap** for an initiative. Nothing else.
