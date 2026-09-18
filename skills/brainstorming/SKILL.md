---
name: brainstorming
description: Use before any non-trivial creative work (features, components, behaviour changes), to turn an idea into an approved design through clarifying questions and 2-3 proposed approaches.
---

# Brainstorming

Turn an idea into a design through dialogue: ask questions one at a time, propose two or three approaches, settle on one with the user, write it down, hand off to writing-plans.

<HARD-GATE>
Present a design and get the user's approval before invoking writing-plans or writing any code — for every project, a todo list included. "Simple" is where unexamined assumptions cost the most; the design can be a few sentences when the work is small, but the approval is what matters.
</HARD-GATE>

## When to skip

A change you can describe in one sentence and verify with one command — a rename, a typo, a constant — never enters brainstorming; using-playbooks' skip list handles it. Once you're here, don't skip the design.

## Checklist

Track these as todos and complete them in order:

1. **Explore project context**
   - files and recent commits; not a git repo yet? offer `git init` (ask first) — the pipeline commits its artifacts
   - `docs/followups.md` — open items that intersect this work get folded in
   - existing ADRs in the repo's ADR home (per `.claude/documentation.md`) — they constrain the design; reversing one is a supersede
   - `docs/playbooks/initiatives/` — if this is a slice of one, link it; if every slice in its table has landed, offer to consolidate it
2. **Ask clarifying questions** — one at a time; purpose, constraints, success criteria, not implementation details. Multiple-choice when it fits.
3. **Propose 2–3 approaches** — lead with your recommendation and why; conversational, not a comparison matrix. Run the failure-mode pass below on each.
4. **Present the design in sections** — the doc's sections, in order (step 7); ask "looks right so far?" after each.
5. **Choose workspace** — invoke **using-git-worktrees**: after approval, so abandoned brainstorms leave no orphan branches; before any commit, so design, plan and implementation all land on the feature branch where finishing-branch and consolidating-docs can find them.
6. **Record the decision (if any)** — apply **writing-adr**'s bar to the approach the user picked. Clears it → invoke **writing-adr**; the ADR is `proposed` and commits with the design doc. Most features don't clear it.
7. **Write the design doc** — read `references/design-doc.md` first; it owns the shape (Problem → Approach → Shape → Contracts → Guarantees → Assumptions → Open questions → Risks → Out of scope), the altitude rule, the diagram rules and initiative designs. Worked example: `references/example-design.md`. Save to `docs/playbooks/designs/YYYY-MM-DD-<topic>.md` and commit.
8. **Self-review** (below), then **ask the user to review** and wait for explicit approval.
9. **Invoke writing-plans** — the only skill you invoke from here.

## Decomposition

A request that spans several independent subsystems ("a platform with chat, storage, billing and analytics") is split before any question is spent refining it: each sub-project gets its own design → plan → implementation cycle. When the slices share a target architecture, an **initiative design** comes first (`references/design-doc.md`, *Initiative designs*) and each slice links it. Work that fits one cycle needs no initiative.

## Failure-mode pass

For any approach that puts an unreliable component on a load-bearing seam — an LLM at a generation boundary, a heuristic trusted to hold a structural invariant — ask how it degenerates under real load and what the deterministic alternative is. If holding it together would need post-hoc patches, the abstraction is wrong: make the structure deterministic and use the model only for bounded content-fill in a known shape. "Free composition fenced by invariants" is the classic trap.

## Design for isolation

Units with one purpose each and well-defined interfaces, testable independently; internals leaking through an interface mean the boundary is wrong. In an existing codebase, follow its patterns, fold in the targeted improvements this work needs, and leave unrelated refactoring alone.

## Self-review

1. **Placeholders and contradictions** — no TBDs; sections agree with each other.
2. **Ambiguity** — a requirement readable two ways gets one reading, stated.
3. **Scope** — one implementation plan's worth, or does it need decomposition?
4. **Stranger test** — could a teammate who has never opened the codebase follow Problem → Approach → Shape? A sentence that needs three identifiers to parse is rewritten at component level.
5. **Walk `references/design-doc.md`'s per-section rules** as a checklist: altitude, diagram, contracts with failure behaviour, numbered falsifiable guarantees ending in what must not change, Assumptions and Open questions present, Status set.
6. **Accuracy** — for anything you're tempted to cut: would cutting it lose accuracy for the implementer? If not, cut; if so, keep.

Fix inline; no second review.

## User review gate

> "Design written and committed to `<path>`[, ADR at `<adr-path>`]. Please review it and let me know if you want any changes before we move to writing-plans."

Wait for explicit approval; on changes, apply them and re-run the self-review. On approval set the header Status to `approved`. The ADR, if any, is reviewed at this same gate.

## Re-entering from executing-plans

The circuit-breaker sends a wrong seam back here. Work only that seam: don't re-run the workspace choice; revise the existing `proposed` ADR in place if the decision changed — never a second ADR. Update the design, re-review at the gate, amend the plan to match.

## Red Flags — STOP

| Thought | Reality |
|---------|---------|
| "I'll paste the class so the implementer can't get it wrong" | Paste the signature. The body is theirs; in a design it rots. |
| "Context needs the call chain so readers understand" | Readers need the problem. Call chains are conversation residue. |
| "I'll add a future-optimizations section" | YAGNI. A property → Guarantees; an idea → `docs/followups.md`. |
| "Shorter is better, I'll drop the contracts" | Shorter is not the goal. Complete at the right altitude is. |
