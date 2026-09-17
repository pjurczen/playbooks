---
name: writing-plans
description: Use after brainstorming and before any code, to turn an approved design into an exact, intent-shaped implementation plan an implementer in another session can execute and a team can read.
---

# Writing Plans

Take an approved design and produce the plan that gets it built: what changes where, in what order, proven by which scenarios. The plan stands on the design and links it; it never restates it. Design = why, shape, contract. Plan = work. The implementer is in another session with none of this conversation: name what they would otherwise have to search for or decide, and nothing more — a plan that restates the design and the code is a plan nobody reads.

<HARD-GATE>
Don't pre-write the implementation: no method bodies, no test code, no complete file contents, no per-step commit messages, no bash recipes. The plan says WHAT changes and WHERE, by exact name; HOW the body reads is the implementer's, and a pre-written body rots before it's read.
</HARD-GATE>

## The two tests a plan must pass

- **Implementer test** — given only the design, this plan and the repo, could an implementer with none of this conversation produce the right code without guessing a name, a signature, an order, or a test? "They'd have to search for it" → name the file or method. "They'd have to decide it" → decide it here, or list it as an open question.
- **Overlap test** — a sentence the design already says gets deleted and linked. Responsibilities, contracts, the diagram and design risks live in the design.

A plan is as long as the work map needs and no longer; the test is the implementer, not the clock.

**Save to** `docs/playbooks/plans/YYYY-MM-DD-<feature>.md` and commit.

## Scope check

1. One coherent feature? If the design sprawls across independent subsystems, send it back to brainstorming for decomposition — an initiative design plus slice designs.
2. `docs/followups.md`, if it exists — intersecting items are folded in explicitly, as milestones or parts of them, never quietly.
3. Entered without brainstorming (the user brought a design)? Apply **writing-adr**'s bar to its approach; if it clears and no ADR exists on the branch, invoke **writing-adr** from the design doc before planning — the decision is still fresh here; at landing it won't be.

## The plan shape

````markdown
# <feature> — implementation plan

Design: <link> · ADR: <link if any>

## Goal
One sentence describing what this builds.

## Changes
| Unit | Change | What, exactly |
|------|--------|---------------|
| ClassOrFile | new / changed / deleted | methods added, removed, re-pointed — by name |

Call sites, when existing callers move:

| Site | From | To |
|------|------|----|
| Class.method | what it calls today | what it calls after |

Add a Depends-on column when it drives milestone order. Greenfield: the new
units, their files, and the milestone that builds each. Never restate
responsibilities or contracts — the design's Shape and Contracts own them.

## Behaviours to verify
- G2 · <TestClass or feature file> — Given X, when Y, then Z
- Edge · <TestClass> — Given …, when …, then …

Scenarios cite the design's Guarantee they prove; every G has at least one.
Edge cases and parity fixtures are listed too.

## Milestones
| # | Milestone | Delivers | Done when | Biggest risk |
|---|-----------|----------|-----------|--------------|
| 1 | <vertical slice> | <observable outcome> | <named suites / scenarios green> | <one clause, or none> |

Each milestone starts with its Behaviours red: the scenario is written and
fails before the slice is built.

## Execution risks / open questions
Only what the design didn't say: ordering, big-bang compile steps, hidden
callers, decisions needed mid-execution.

Stop and ask if:
- <a contract in the design doesn't fit the code as found>
- <a milestone's suite can't go green without touching something outside Changes>
- <a Guarantee can't be proven by any scenario>
````

Milestones are vertical slices with observable progress — small enough to commit cleanly, big enough for a self-checkpoint and a refactor pass. The milestone table is what a team reads in a meeting. Greenfield? Milestone 1 includes the minimal test scaffolding. The *Stop and ask if* list is binding: an unlisted surprise is reported, not resolved by picking an interpretation.

See `example-plan.md` beside this skill, with its design `../brainstorming/example-design.md` — together they are complete, and nothing is said twice.

## Self-review

1. **Body scan** — any code block that is more than a signature? Replace it with a table row.
2. **Implementer test** — walk the design and the plan as the implementer: every name written, every order fixed, every test named.
3. **Overlap scan** — any sentence the design already says? Delete it. Any component named differently in the two documents? Align it.
4. **Coverage, both directions** — walk the design's Guarantees: each has a scenario. Walk the scenarios: each names a Guarantee or is marked Edge. Walk Changes: each row is built in some milestone. Start from the design's list so a missing one shows.
5. **Milestone independence** — each a real vertical slice with observable progress, not "set up scaffolding".

Fix inline.

## User review gate

> "Plan written and committed to `<path>`. Please review it and let me know if you want changes before we move to executing-plans."

Wait for explicit approval; on changes, apply them and re-run the self-review. Then invoke **executing-plans** — the only skill you invoke from here.
