---
name: brainstorming
description: Use before any non-trivial creative work (a feature, a component, a behaviour change), to turn the request into an approved design through one question at a time and two or three weighed approaches.
---

# Brainstorming

You are designing for a developer who knows the codebase. They read the design once, present it and approve it; an implementer in another session reads it once
more and plans from it. Everything here serves those two reads.

<HARD-GATE>
No code, scaffolding, dependency or writing-plans until the user approves the written design. Three sentences can be enough; the approval is what matters,
because "simple" is where unexamined assumptions cost the most.
</HARD-GATE>

Before anything gets built, in order:

1. Look at what exists, then ask one question at a time.
2. Lay out the approaches in a message of their own; the user picks one.
3. Write the design, short or full. Run the builder check on a full one.
4. Get approval of the written design.
5. Hand off to **writing-plans**, or **writing-roadmap** for an initiative.

## When to skip

A change you can describe in one sentence and verify with one command never enters brainstorming; using-playbooks' skip list handles it.

## Look before you ask

Read until you can say how the relevant parts work today and what the change would touch:

- the code paths, callers and data the request names
- `docs/followups.md`: earlier attempts
- the ADRs `.claude/documentation.md` names: they constrain the fix; reversing one is a supersede
- `.claude/gates.md`: the rules the repo enforces
- `docs/playbooks/initiatives/`: is this a slice of one?
- `.claude/designs.md`: the repo's design conventions (below)

Never ask what the repo already answers.

## Your first message

- Echo the request in your own words: what, who for, why.
- Add what you found that bears on it: a constraint, a conflict, a cheaper path.
- End with the one question whose answer most changes what gets built.

## The conversation

- **One question per message.** Three questions get one answer.
- **Ask about purpose, constraints and what done looks like.** Implementation choices are yours to make and explain.
- **Multiple choice only when the options differ in consequence.** Each option: what it buys, what it costs. An option without a cost leaves "the user chose" as
  the only reason on record.
- **Play back as you go.** One part at a time, briefly. What they said is theirs; what you filled in is your proposal, with its reason.
- **A gap goes to its owner.** A product rule or acceptance criterion only the requester can settle becomes an open question, never a silent default.

## Lay out the approaches

In a message of their own, before you write anything:

- Two or three real ones, grounded in the code. Keeping things as they are counts when it is credible.
- For each: what it buys, what it costs.
- Recommend one and say why. If only one fits, say why the others do not.

The losers' costs are the chosen approach's reason; without them there is nothing to write down.

Then size the work:

| The work                      | The design                                           |
|-------------------------------|------------------------------------------------------|
| A small change                | a short one: what you covered together, written down |
| A feature                     | the full design below                                |
| Several independent projects  | agree an order; one at a time                        |
| Too big to land as one change | an initiative design (below), then a roadmap         |

## The written design

Save to `docs/playbooks/designs/YYYY-MM-DD-<topic>.md`. Title names the change; header `Status: draft | approved · Ticket: …`.

After one read, the reader can say:

- what hurts, and what done looks like
- what causes it
- what we will do, what it beat, and why
- which parts take part and who owns what
- the rules and contracts that get built
- what it costs, and what changes for callers
- what is still open

Headings are yours. No section exists because a template lists it.

**The rules:**

- Problem and cause before any solution. Done as something observable.
- Every decision says why, and what it beat. "Simpler" only if the page shows what is simpler.
- One fact, one place. No lead-ins, no "unchanged" unless the reader would worry, no sentence a later edit left stale.
- Open points in one list, each with an owner or what it blocks. No hedging anywhere else.
- Parts and responsibilities, not call chains. A class name is a fine reference; a trace is not.
  - Design: "The adapter maps the pairs to the billing service's `InvoiceLine` objects."
  - Trace: "`OrderService.submit` loads the open order, delegates to the domain service and saves."
- Three or more parts, or ordered steps: draw them. Caption, typed nodes, labelled edges; prose says why, not what the picture shows. Read `references/views.md`
  before drawing.
- Code only as a declaration, or a rule a test can follow branch by branch.
- Say what you leave out, and what gets worse.

**Initiatives.** Work too big to land as one change ships in slices, the old path serving in between. It gets an initiative design first, in
`docs/playbooks/initiatives/` on the base branch: target state, coexistence mechanism, shared contracts. Each slice then gets an ordinary design that inherits
from it and never restates it. One change is one design, however many milestones its plan has.

**Repo conventions.** `.claude/designs.md`, when present: vocabulary, diagram node kinds, where acceptance criteria come from and where story gaps go, document
locations, extra review questions. Apply it; never restate it.

## Builder check

For a full design, dispatch a fresh subagent with `references/builder-check.md`: a builder who knows the codebase reads the design and reports where they would
still have to guess. Sort what comes back:

- **Answered already**: put the answer in the document.
- **Minor**: settle it yourself; mark it in the document as your call.
- **Theirs**: bring to the user in one message, most important first.

One round. The check catches what the author cannot see; it does not reopen the dialogue.

## Approval

> "Design committed to `<path>`[, ADR at `<path>`]. Done means: …. It beat … because …. Costs: …. Open: <n>, owners named. Approve, or tell me what to change."

Wait for explicit approval. On changes, rewrite in place; why it changed goes in the commit message. On approval set `Status: approved`.

## After approval

The design is frozen.

- A changed decision comes back here for re-approval: the approach, a contract others build against, a consequence.
- Anything smaller goes to the PR description; the end-of-feature reviewer reports every difference.
- Re-entry from executing-plans works only that seam: keep the workspace, revise the `proposed` ADR in place, re-review at the gate.

## Hand-offs

- **using-git-worktrees** once the approach is chosen, before the design is committed.
- **writing-adr** when the approach is a system-level choice or a rule the team adopts, by its test; the `proposed` ADR commits with the design.
- **writing-plans** after approval; **writing-roadmap** for an initiative. Nothing else.
