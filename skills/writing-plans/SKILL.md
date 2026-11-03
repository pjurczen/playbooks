---
name: writing-plans
description: Use after brainstorming and before any code, to turn an approved design into an intent-shaped implementation plan readable end-to-end in 2-3 minutes.
---

# Writing Plans

Take an approved design and produce a plan that decomposes it into milestones a senior engineer can execute. The plan describes intent, not implementation.

Write in ASD-STE100 (Simplified Technical English). Read `${CLAUDE_PLUGIN_ROOT}/references/ste.md` before you write.

<HARD-GATE>
Do not pre-write the implementation in the plan. Do not include full test code, full method bodies, complete file contents or per-step commit messages. The plan
describes what and why at the level of components and behaviours. The how is for the implementer. A plan that does the implementation's job cannot be read in
2–3 minutes, and it rots first.
</HARD-GATE>

Fired by brainstorming after design approval. When the user brings an approved design instead, apply **writing-adr**'s bar to its approach first.

## The artifact-brevity rule

A plan must be readable end-to-end in 2–3 minutes. If yours is not, the plan is doing the implementation's job. Pull the code out, let the implementer fill it
in.

If you catch yourself writing pre-canned test code, full class definitions or step-by-step commit instructions, stop. The plan is not a script.

**Save plans to:** `docs/playbooks/plans/YYYY-MM-DD-<feature>.md` and commit.

## Scope check

Before defining the plan:

1. Does the approved design cover a single coherent feature? If it sprawls across multiple independent subsystems, send it back to brainstorming for
   decomposition. Each sub-feature gets its own design → plan → implementation cycle. A design too big to land as one change goes back as an initiative.
2. Read `docs/followups.md` if it exists. Any open followups intersect with this work? If so, fold them in *explicitly*, as their own milestones or as part of
   existing ones. Do not quietly extend scope.

## Walk the order against the repo

Every premise a milestone rests on is checked now, by reading the code or running a command: that a call site exists, that a type is shared, that a suite covers
a path. A premise you cannot check goes to the user before approval, never to the implementer as "stop and ask". A plan that fails in its first hour was
approved on a guess. Revert any probe.

## The plan shape

Every plan has these sections, in this order:

````markdown
# <feature> — implementation plan

Design: <link> · ADR: <link, if any> · Initiative: <link, for a slice>

## Goal
One sentence describing what this builds.

## Decomposition
- ComponentA — responsibility, interface, depends on …
- ComponentB — responsibility, interface, depends on …

A few sentences per component. Name the boundary, not the implementation.

## Behaviours to verify
1. Given X, when Y, then Z
2. (etc.)

Use-case-level behaviours. Not "the enum has these values" but "when the user
submits an empty form, they see the validation error".

## Milestones
1. Vertical slice 1: <short description>
   Done when: <observable outcome>
   Verified by: behaviours 1, 3; <the suites, gates and commands that must be green>
2. Vertical slice 2: <short description>
   Done when: <observable outcome>
   Verified by: …

Each milestone is a vertical slice with observable progress. Sized so a
self-checkpoint and a refactor pass can both happen meaningfully: small
enough to commit cleanly, big enough to be more than a single edit.
Greenfield project? Milestone 1 includes the minimal test scaffolding
(runner plus one passing behavioural test).

## Assumptions
- <premise the order rests on>, checked in the repo while planning, stated as a fact

## Open questions
- <what> — blocks <milestone>, <who answers>
````

That is it. No code blocks except short illustrative interface sketches when prose is genuinely worse.

## What does NOT belong in the plan

- Pre-written test code (the implementer writes tests using **bdd-testing**)
- Full method or function bodies
- Complete file contents
- Per-step commit messages (commit messages are crafted at execution time per **milestone-commits**)
- Exact bash commands (the implementer has shell access)
- A file path for every line. Component-level decomposition is enough.
- How a premise was checked. Assumptions holds the fact.

## Self-review

After writing the plan, look at it with fresh eyes:

1. **Code-block scan** — any code blocks larger than ~5 lines? Those probably belong in the implementation. Remove or replace with prose.
2. **Length check** — can a senior engineer read this end-to-end in 2–3 minutes? If not, you are over-specifying.
3. **Coverage** — does each behaviour appear in at least one milestone's Verified by? Does each component get built somewhere?
4. **Milestone independence** — is each milestone a real vertical slice with observable progress, or is it just "set up scaffolding" that cannot be tested on
   its own?
5. **Assumptions** — was every Assumption checked in the repo, not assumed? Does anything still read as "stop and ask"?
6. **Followup integration** — if you folded in any followups from `followups.md`, are they explicit?

Fix issues inline.

## User review gate

After self-review:

> "Plan written and committed to `<path>`. Please review it and let me know if you want changes before we move to executing-plans."

Wait for explicit approval. If the user requests changes, make them and re-run the self-review.

## Hand off

After user approval, invoke **executing-plans** to begin implementation. Do not invoke any other skill from here.

## Red Flags — STOP

| Thought                                                                 | Reality                                                   |
|-------------------------------------------------------------------------|-----------------------------------------------------------|
| "Let me include the test code so the implementer doesn't have to think" | They should think. That is the value.                     |
| "More detail is safer"                                                  | More detail is harder to read and rots faster.            |
| "The plan needs every method signature"                                 | Component-level interfaces are enough.                    |
| "I'll note it as 'check whether X' for the implementer"                 | Check it now. A premise handed over is a guess approved.  |
