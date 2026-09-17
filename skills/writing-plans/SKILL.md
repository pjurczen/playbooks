---
name: writing-plans
description: Use after brainstorming and before any code, to turn an approved design into an exact, intent-shaped implementation plan a less capable implementer can execute and a team can read.
---

# Writing Plans

Take an approved design and produce the plan that gets it built: what changes where, in what order, proven by which scenarios. The plan stands on the design and links it — it never restates it. Design = why, shape, contract. Plan = work. Assume the implementer may be a smaller model in another session: name everything they would otherwise have to search for or decide.

**Announce at start:** "Using writing-plans to create the implementation plan."

<HARD-GATE>
Do NOT pre-write the implementation in the plan. No full test code, no method bodies, no complete file contents, no per-step commit messages. The plan says WHAT changes and WHERE, by exact name; HOW the body reads is the implementer's.
</HARD-GATE>

## The two tests a plan must pass

- **The implementer test** — given only the design, this plan and the repo, could a less capable implementer produce the right code without guessing a name, a signature, an order, or a test? "They'd have to search for it" → name the file or method. "They'd have to decide it" → decide it here, or list it under open questions.
- **The overlap test** — is there a sentence here the design already says? Delete it and link. Responsibilities, contracts, the diagram and design risks live in the design.

A plan is as long as the work map needs and no longer. The test is the implementer, not the clock.

**Save plans to:** `docs/playbooks/plans/YYYY-MM-DD-<feature>.md` and commit.

## Scope check

Before defining the plan:

1. Does the approved design cover a single coherent feature? If it sprawls across multiple independent subsystems, send it back to brainstorming for decomposition — an initiative design plus slice designs. Each slice gets its own design → plan → implementation cycle.
2. Read `docs/followups.md` if it exists. Any open followups intersect with this work? If so, fold them in *explicitly* — as their own milestones or as part of existing ones. Don't quietly extend scope.
3. Entered here without brainstorming (the user brought an approved design)? Apply **writing-adr**'s bar to the design's approach. If it clears and no ADR exists on the branch, invoke **writing-adr** from the design doc before planning — the decision is still fresh here; at landing it won't be.

## The plan shape

Every plan has these sections, in this order:

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
1. <Vertical slice>: <what it delivers>
   Done when: <the named suites / scenarios that must be green>
2. …

## Execution risks / open questions
Only what the design didn't say: ordering, big-bang compile steps, hidden
callers, decisions needed mid-execution.
````

Milestones are vertical slices with observable progress — small enough to commit cleanly, big enough to be more than a single edit, sized so a self-checkpoint and a refactor pass can both happen. Greenfield project? Milestone 1 includes the minimal test scaffolding (runner plus one passing behavioural test).

See `example-plan.md` beside this skill; its design is `../brainstorming/example-design.md`. Read them as a pair — together they are complete, and nothing is said twice.

## What does NOT belong in the plan

- Pre-written test code (the implementer writes tests using **bdd-testing**; the plan names the scenarios)
- Method or function bodies
- Complete file contents
- Per-step commit messages (crafted at execution time per **milestone-commits**)
- The design's responsibilities, contracts, diagram or risks — link, don't copy
- Exact bash commands (the implementer has shell access)

## Self-review

After writing the plan, look at it with fresh eyes:

1. **Body scan** — any code block that is more than a signature? Remove it or replace it with a table row.
2. **Implementer test** — walk the design and the plan as the implementer. Every name they need is written; every order is fixed; every test is named.
3. **Overlap scan** — any sentence the design already says? Delete it.
4. **Coverage** — every Guarantee in the design has at least one scenario; every unit in Changes is built or changed in some milestone.
5. **Milestone independence** — is each milestone a real vertical slice with observable progress, or just "set up scaffolding" that can't be tested on its own?
6. **Followup integration** — if you folded in any followups from `followups.md`, are they explicit?

Fix issues inline.

## User review gate

After self-review:

> "Plan written and committed to `<path>`. Please review it and let me know if you want changes before we move to executing-plans."

Wait for explicit approval. If the user requests changes, make them and re-run the self-review.

## Hand off

After user approval, invoke **executing-plans** to begin implementation. Do NOT invoke any other skill from here.

## Red Flags — STOP

| Thought | Reality |
|---------|---------|
| "Let me include the test code so the implementer doesn't have to think" | Name the scenario. They write the test. |
| "I'll summarize the design at the top so the plan stands alone" | It stands on the design. Link it. |
| "The design's risks belong here too" | Design risks live in the design. Only execution risks here. |
| "Component-level is enough, they'll find the method" | A smaller implementer won't. Name it. |
| "The plan needs every method body to be unambiguous" | Signatures are in the design's Contracts. Bodies are the implementer's. |
| "Shorter is better" | Complete is better. Cut only what loses no accuracy. |
| "I'll write the tests now since the design is fresh" | The implementer writes tests after watching them fail (bdd-testing). |
