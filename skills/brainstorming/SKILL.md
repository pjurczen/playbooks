---
name: brainstorming
description: Use before any non-trivial creative work (features, components, behaviour changes), to turn an idea into an approved design through clarifying questions and 2-3 proposed approaches.
---

# Brainstorming

Turn an idea into a fully formed design through natural dialogue. Ask questions one at a time. Propose 2–3 approaches. Settle on a design with the user, write
it to disk, hand off to writing-plans.

Write in ASD-STE100 (Simplified Technical English). Read `${CLAUDE_PLUGIN_ROOT}/references/ste.md` before you write.

<HARD-GATE>
Do not invoke writing-plans, write code, scaffold a project or take any implementation action before you have presented a design and the user has approved it.
This applies to every project, whatever its size. "Simple" projects are where unexamined assumptions cause the most wasted work. The design can be a few
sentences. The approval is what matters.
</HARD-GATE>

## When to skip

Truly trivial one-off tweaks never enter brainstorming: a typo, a renamed local, an adjusted constant. The skip list of using-playbooks applies. Once you are
here, do not skip the design.

## The steps

1. Explore the project context (see "Look before you ask").
2. Ask clarifying questions, one at a time. Focus on purpose, constraints and success criteria.
3. Propose 2–3 approaches with their trade-offs and your recommendation. The user picks one.
4. Invoke **using-git-worktrees**. This happens before anything is committed, so the design, the plan and the implementation all land on the feature branch.
   Invoke **writing-adr** when the approach is a system-level choice or a rule that the team adopts. Apply its test.
5. Present the design in sections. Get the user's approval after each section.
6. Write the design to disk and commit it. The `proposed` ADR commits with it.
7. Self-review the document. Then run the builder check on a full design.
8. Ask the user to review the written document. Wait for explicit approval.
9. Invoke **writing-plans**. For an initiative, invoke **writing-roadmap**. Invoke nothing else.

## Look before you ask

Read until you can say how the relevant parts work today and what the change touches:

- the code paths, the callers and the data that the request names
- recent commits, and `docs/followups.md` for earlier attempts. Fold in an open followup that intersects this work.
- the ADRs that `.claude/documentation.md` names. They constrain the fix. A reversal of an ADR is a supersede.
- `.claude/gates.md`, for the rules that the repo enforces
- `docs/playbooks/initiatives/`, to see if this work is a slice of an initiative
- `.claude/designs.md`, for the design conventions of the repo

Do not ask a question that the repo answers.

## How to ask

- If the request describes multiple independent subsystems ("a platform with chat, file storage, billing, and analytics"), flag this immediately and help the
  user decompose into sub-projects. Each sub-project gets its own design → plan → implementation cycle. Do not spend questions refining details of a project
  that needs to be split first.
- For appropriately-scoped work, ask one question at a time.
- Prefer multiple-choice when possible. Open-ended is fine when needed.
- Focus on purpose, constraints, success criteria, not implementation details.

## How to propose approaches

- 2–3 distinct approaches with their trade-offs
- Lead with your recommendation and the reason for it
- Conversational, not a comparison matrix
- **Failure-mode pass** — for any approach that puts an *unreliable component* on a load-bearing seam (an LLM at a generation/sampling boundary, a heuristic
  trusted to hold a global/structural invariant), ask: how does it degenerate under real load, and what is the deterministic alternative? If holding it together
  would need post-hoc patches to force the behaviour, the abstraction is wrong. Make the structure deterministic and use the model only for bounded content-fill
  in a known shape.
  - *"Free composition fenced by invariants" is the classic trap: the fence becomes ten patches.*

Then say how big the work is:

| The work                      | The design                                           |
|-------------------------------|------------------------------------------------------|
| A small change                | a short one: what you covered together, written down |
| A feature                     | the design below                                     |
| Several independent projects  | agree an order, and brainstorm one at a time         |
| Too big to land as one change | an initiative design (below), then a roadmap         |

## How to present the design

- Once you understand what you are building, present the design in sections
- Scale each section to its complexity: a few sentences for straightforward parts, up to 200–300 words for nuanced ones
- After each section, ask "looks right so far?"
- Cover: architecture, components, data flow, error handling, testing approach
- Be ready to back up and clarify if something does not make sense

Draw when three or more parts, or ordered steps, take part. Read `references/views.md` before you draw. One sequence diagram that follows one case through the
parts is the walk-through. Do not retell it in prose.

## Design for isolation and clarity

- Break the system into smaller units, each with one clear purpose, well-defined interfaces, testable independently
- For each unit: what does it do, how do you use it, what does it depend on?
- If a unit's internals leak through its interface, the boundary is wrong
- Smaller, well-bounded units are also easier for an agent to reason about and edit reliably
- YAGNI: strip the features that the goal does not need

## Working in existing codebases

- Explore current structure before proposing changes. Follow existing patterns.
- If existing code has problems that affect this work (oversized file, unclear boundaries, tangled responsibilities), include targeted improvements as part of
  the design, the way a good developer improves code they are working in
- Do not propose unrelated refactoring. Stay focused on what serves the current goal.

## Repo conventions

When `.claude/designs.md` exists, apply it. It names the glossary, the kinds of diagram nodes, the source of the acceptance criteria, the home of a story gap,
the document locations and the extra review questions. Do not restate it. Use a glossary term as the glossary spells it. Do not translate it.

## The written design

Save it to `docs/playbooks/designs/YYYY-MM-DD-<topic>.md` and commit it. The `proposed` ADR commits with it. The document is the approved sections written down,
with their diagrams. The headings are yours. A small change gets a short one.

## Self-review (after writing the doc)

Look at the design doc with fresh eyes:

1. **Placeholder scan** — any "TBD", "TODO", incomplete sections, vague requirements? Fix them.
2. **Internal consistency** — do sections contradict each other? Does the architecture match the feature descriptions?
3. **Scope check** — is this focused enough for a single implementation plan, or does it need decomposition?
4. **Ambiguity check** — could any requirement be interpreted two ways? Pick one and make it explicit.

Fix issues inline. No need to re-review. Fix and move on.

## Builder check

Run this check once on a full design, after the self-review. Dispatch a fresh subagent with `references/builder-check.md`. The subagent is a builder who knows
the codebase. The builder reads the design and reports where a guess is still necessary. Sort the report:

- **Answered already**: put the answer in the document.
- **Minor**: settle it yourself and write the answer in.
- **Theirs**: bring these to the user in one message, the most important first.

The check catches what the author cannot see. It does not reopen the dialogue. It leaves no trace in the document.

## User review gate

After the builder check:

> "Design written and committed to `<path>`[, ADR at `<path>`]. Please review it and let me know if you want any changes before we move to writing-plans."

Wait for explicit approval. If the user requests changes, make them and re-run the self-review.

## After approval

The approved design is frozen.

- A changed decision comes back here for re-approval. A changed decision is a change to the approach, to a contract that others build against, or to a
  consequence.
- Anything smaller goes to the PR description. The end-of-feature reviewer reports every difference.
- A re-entry from executing-plans works only on that seam. Keep the workspace. Revise the `proposed` ADR in place. Re-review at the gate.

## Initiatives

Work that is too big to land as one change ships in slices. Such work gets an initiative design first: the target state and the shared contracts, and for
replacement work the coexistence mechanism, because the old path serves between the slices. Save it in `docs/playbooks/initiatives/` on the base branch. It
commits there after the user confirms, so it needs no worktree. Each slice then gets an ordinary design, with its own worktree. A slice design inherits from the
initiative design and does not restate it. One change is one design, whatever the number of milestones in its plan. Hand off to **writing-roadmap**.
