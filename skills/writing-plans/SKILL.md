---
name: writing-plans
description: Use after brainstorming and before any code, to turn an approved design into an intent-shaped implementation plan readable end-to-end in 2-3 minutes.
---

# Writing Plans

Take an approved design and produce a plan that decomposes it into milestones a senior engineer can execute. The plan describes intent, not implementation.

**Announce at start:** "Using writing-plans to create the implementation plan."

<HARD-GATE>
Do NOT pre-write the implementation in the plan. Do NOT include full test code, full method bodies, complete file contents, or per-step commit messages. The plan describes WHAT and WHY at the level of components and behaviours. The HOW is for the implementer.
</HARD-GATE>

## The artifact-brevity rule

A plan must be readable end-to-end in 2-3 minutes. If yours is not, the plan is doing the implementation's job. Pull the code out, let the implementer fill it in.

If you catch yourself writing pre-canned test code, full class definitions, or step-by-step commit instructions, stop. The plan is not a script.

**Save plans to:** `docs/playbooks/plans/YYYY-MM-DD-<feature>.md`

## Scope check

Before defining the plan:

1. Does the approved design cover a single coherent feature? If it sprawls across multiple independent subsystems, send it back to brainstorming for decomposition. Each sub-feature gets its own design → plan → implementation cycle.
2. Read `docs/playbooks/followups.md` if it exists. Any open followups intersect with this work? If so, fold them in *explicitly* — as their own milestones or as part of existing ones. Don't quietly extend scope.

## The plan shape

Every plan has these sections, in this order:

````markdown
# <feature> — implementation plan

## Goal
One sentence describing what this builds.

## Decomposition
- ComponentA — responsibility, interface, depends on …
- ComponentB — responsibility, interface, depends on …

A few sentences per component. Name the boundary, not the implementation.

## Behaviours to verify
- Given X, when Y, then Z
- (etc.)

Use-case-level behaviours. Not "the enum has these values" — "when the user
submits an empty form, they see the validation error".

## Milestones
1. Vertical slice 1: <short description>
   Done when: <observable outcome>
2. Vertical slice 2: <short description>
   Done when: <observable outcome>

Each milestone is a vertical slice with observable progress. Sized so a
self-checkpoint and a refactor pass can both happen meaningfully — small
enough to commit cleanly, big enough to be more than a single edit.

## Risk / open questions
- Anything that might block work or requires the user to choose at execution time.
````

That's it. No code blocks except short illustrative interface sketches when prose is genuinely worse.

## What does NOT belong in the plan

- Pre-written test code (the implementer writes tests using **bdd-testing**)
- Full method or function bodies
- Complete file contents
- Per-step commit messages (commit messages are crafted at execution time per **milestone-commits**)
- Exact bash commands (the implementer has shell access)
- A file path for every line — component-level decomposition is enough

## Self-review

After writing the plan, look at it with fresh eyes:

1. **Code-block scan** — any code blocks larger than ~5 lines? Those probably belong in the implementation. Remove or replace with prose.
2. **Length check** — can a senior engineer read this end-to-end in 2-3 minutes? If not, you're over-specifying.
3. **Coverage** — does each behaviour from the design get covered by at least one milestone? Does each component get built somewhere?
4. **Milestone independence** — is each milestone a real vertical slice with observable progress, or is it just "set up scaffolding" that can't be tested on its own?
5. **Followup integration** — if you folded in any followups from `followups.md`, are they explicit?

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
| "Let me include the test code so the implementer doesn't have to think" | They should think — that's the value. |
| "More detail is safer" | More detail is harder to read and rots faster. |
| "The plan needs every method signature" | Component-level interfaces are enough. |
| "I'll add a step-by-step bash recipe" | The implementer has shell access. |
| "The plan should be exhaustive" | The plan should be readable. Different bar. |
| "I'll write the tests now since the design is fresh" | The implementer writes tests after watching them fail (bdd-testing). |
