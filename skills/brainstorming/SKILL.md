---
name: brainstorming
description: Use before any non-trivial creative work (a feature, a component, a behaviour change), to turn the request into an approved design through one question at a time and two or three weighed approaches.
---

# Brainstorming

The design is read once, by a developer who knows the codebase and then by an implementer in another session; everything here serves that read.

<HARD-GATE>
No code, scaffolding, dependency or writing-plans until the user approves the written design. Three sentences can be enough; the approval is what matters,
because "simple" is where unexamined assumptions cost the most.
</HARD-GATE>

## When to skip

A change you can describe in one sentence and verify with one command never enters brainstorming; using-playbooks' skip list handles it.

## Look before you ask

Read what the request touches until you can say how it works today and what the change would touch: code paths, callers and data; `docs/followups.md`; the ADRs
`.claude/documentation.md` names; `.claude/gates.md`; `docs/playbooks/initiatives/`; `.claude/designs.md`. A question the repo answers wastes the user's turn
and anchors the design on their guess.

## The conversation

**First message.** Echo the request in your own words, plus what you found that bears on it: a constraint, a conflict, a cheaper path. End with the one question
whose answer most changes what gets built.

**One question per message**, because three get one answered. Ask about purpose, constraints and what done looks like, never about implementation: a choice the
code can settle is yours to make and explain. Multiple choice only when the options differ in consequence, each with what it buys and costs; an option without a
cost yields a decision whose written reason is "the user chose".

**Play back** each part as you understand it, briefly. What they said is theirs; what you filled in is your proposal with its reason, because a default they
never heard is one they could not reject. A gap only the request's owner can close becomes an open question with that owner, never a silent answer.

**Approaches, in a message of their own.** Two or three real ones grounded in the code, keeping things as they are included when credible. Each says what it
buys and what it costs; recommend one and say why; when only one fits, say why the others do not. A small change gets a short design; several independent
projects are brainstormed one at a time, in an agreed order.

## The written design

Save to `docs/playbooks/designs/YYYY-MM-DD-<topic>.md`, header `Status: draft | approved · Ticket: …`, a title that names the change. After one read the reader
can say: what hurts and what done looks like; what causes it; what we will do, what it beat and why; which parts take part and who owns what; the rules and
contracts that get built; what it costs and what changes for callers; what is still open. Headings are yours; no section exists because a template lists it.

- **Problem and cause before any solution**, done as something observable; a reader who meets the solution first cannot judge it.
- **Every decision carries its reason and what it beat**, where it is made. "Simpler" counts only when the page shows what is simpler.
- **One fact, one place.** No lead-ins, no "unchanged" unless the reader would worry, no sentence a later edit made stale.
- **Open points in one list**, each with its owner or what it blocks; no hedge anywhere else. A "probably" inside a decision is a question not asked.
- **Altitude.** Say what a part is responsible for, what moves between parts, when, and why. A class or type name is the shortest precise reference and welcome;
  a call chain, signature or flag given as the proposal is not. "The adapter maps the pairs to the billing service's `InvoiceLine` objects" is design;
  "`OrderService.submit` loads the open order, delegates to the domain service and saves" is a trace.
- **Draw structure.** Three or more parts, or ordered steps, get a diagram, table or pseudo-code with a caption, typed nodes and labelled edges; prose carries
  the why, never a narration of the picture. Read `references/views.md` before drawing.
- **Code** only as a declaration with its semantics, or a rule a test can follow branch by branch.
- **Name what a reader would expect and you leave out**, and what gets worse.

**Initiatives.** Work too big to land as one change ships in slices, the old path serving in between. It gets an initiative design: target state, coexistence
mechanism, shared contracts, in `docs/playbooks/initiatives/` on the base branch, handed to **writing-roadmap**; each slice then gets an ordinary design that
inherits from it and never restates it. One change, however many milestones its plan has, is one design.

**Repo conventions.** `.claude/designs.md`, when present, carries the repo's vocabulary, diagram node kinds, where acceptance criteria come from and where story
gaps go, document locations and extra review questions. Apply it; never restate it.

## Builder check, approval, after

For a full design, dispatch a fresh subagent with `references/builder-check.md`. Sort what comes back: answered already goes into the document; minor is settled
and marked as your call; theirs goes to the user in one message, most important first. One round. Then the gate:

> "Design committed to `<path>`[, ADR at `<path>`]. Done means: …. It beat … because …. Costs: …. Open: <n>, owners named. Approve, or tell me what to change."

On changes, rewrite in place. On approval set `Status: approved`; the design is frozen. A changed decision (the approach, a contract others build against, a
consequence) comes back here for re-approval; anything else goes to the PR description. Re-entry from executing-plans works only that seam.

## Hand-offs

**using-git-worktrees** once the approach is chosen and before the design is committed, so every artifact lands on the feature branch; **writing-adr** when the
approach is a system-level choice or instantiates a rule the team adopts (its test), the `proposed` ADR committing with the design; after approval
**writing-plans**, or **writing-roadmap** for an initiative. Nothing else.
