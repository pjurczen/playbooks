---
name: writing-roadmap
description: Use after brainstorming approves an initiative design, to slice it into a roadmap of independently landable steps with their order, dependencies and exit criterion.
---

# Writing a Roadmap

An initiative lands slice by slice. The roadmap says which slices, in what order, and when the initiative is done. It is a plan at the initiative's grain: it
owns slices the way a feature plan owns milestones, and it owns nothing a slice plan will — no behaviours, no changes tables, no milestones.

<HARD-GATE>
Every slice must land on its own — mergeable, tested, leaving the system working with old and new side by side. A slice that only makes sense once the next one
lands is not a slice: merge it with its neighbour or cut differently. Landability is what turns one large risk into a sequence of small ones.
</HARD-GATE>

## When this runs — and when to skip

Fired by brainstorming after an initiative design is approved; revised, never rewritten, whenever a landed slice changes the picture. Skip for anything that
fits one design → plan → execute cycle: that work gets a plan, not a roadmap.

## The shape

The shape is `references/example-roadmap.md` — read it, with its initiative design `../brainstorming/references/example-design-initiative.md`. Its sections:

- **Header** — links the initiative design and its ADR.
- **Exit criterion** — one sentence: the initiative is done when the end state is reached and the legacy is gone.
- **Slices** — a table: slice, what it delivers (something a user or operator can observe), depends on, status ( `planned` | `in progress` | `landed`). One or
  two lines a reader can picture; the details wait for the slice design.
- **Order** — why this order, and which slices are independent and may run in parallel.
- **Open questions** — what a later slice must answer before it can be designed.

## Slicing

- Walking skeleton first: the thinnest path through the new architecture, end to end, carrying real traffic for the smallest case.
- Riskiest next: the slice most likely to prove the coexistence mechanism or a shared contract wrong, while changing them is still cheap.
- Vertical, not layered: each slice delivers something observable, never "the data layer".
- Independent where the design allows: slices touching disjoint areas can run in parallel worktrees; say which.
- The last slice deletes the legacy path and the coexistence mechanism.

## Self-review

1. Every slice lands on its own, and the old path keeps serving whatever the slice doesn't cover.
2. The initiative design's coexistence mechanism supports this order — its guarantee says which orders it supports.
3. Every shared contract is introduced by some slice, and no slice needs a contract a later slice introduces.
4. The first slice is a skeleton or the riskiest piece, not the easiest.
5. The exit criterion is observable.

## Lifecycle

Lives beside the initiative design in `docs/playbooks/initiatives/`, committed to the base branch with the same confirmation. brainstorming flips a slice to
`in progress` when its design is approved; consolidating-docs flips it to `landed` when it lands and asks whether the initiative is complete when the last one
does. Reorder or split slices as learning arrives: edit the table, never annotate it.

## User review gate

> "Roadmap written and committed to `<path>`. Please review it; when you're ready, the first slice starts with brainstorming."

Wait for explicit approval. The next slice then enters **brainstorming** in slice mode — nothing else is invoked from here.
