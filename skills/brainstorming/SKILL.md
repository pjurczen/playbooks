---
name: brainstorming
description: Use before any non-trivial creative work (features, components, behaviour changes), to turn an idea into an approved design through clarifying questions and 2-3 proposed approaches.
---

# Brainstorming

Turn an idea into a design through dialogue: ask questions one at a time, propose two or three approaches, settle on one with the user, write it down, hand off to planning.

<HARD-GATE>
Present a design and get the user's approval before invoking a planning skill or writing any code — for every project, a todo list included. "Simple" is where unexamined assumptions cost the most; the design can be a few sentences when the work is small, but the approval is what matters.
</HARD-GATE>

## When to skip

A change you can describe in one sentence and verify with one command — a rename, a typo, a constant — never enters brainstorming; using-playbooks' skip list handles it. Once you're here, don't skip the design.

## Checklist

Track these as todos and complete them in order:

1. **Name the kind of work** — from the table in `references/design-doc-shape.md`: a feature in an existing codebase, greenfield, a replacement, an integration, a data change, a user-facing flow, an infrastructure change, a cross-cutting policy, an initiative. It decides what to explore, what to ask, which views to draw and what the contracts are.
2. **Explore project context** — as the kind demands: the surrounding code; `docs/followups.md` (intersecting items get folded in); existing ADRs per `.claude/documentation.md` (they constrain the design; reversing one is a supersede); `docs/playbooks/initiatives/` (a slice of one is designed in slice mode, per `references/initiative-design.md`). Not a git repo yet? Offer `git init` (ask first).
3. **Ask clarifying questions** — one at a time; purpose, constraints, success criteria, not implementation details. Multiple-choice when it fits.
4. **Propose 2–3 approaches** — lead with your recommendation and why; conversational, not a comparison matrix. Run the failure-mode pass below on each.
5. **Present the design in sections** — the doc's sections in order; ask "looks right so far?" after each.
6. **Choose workspace** — invoke **using-git-worktrees**: after approval, so abandoned brainstorms leave no orphan branches; before any commit, so every artifact lands on the feature branch where finishing-branch and consolidating-docs find it.
7. **Record the decision (if any)** — does the chosen approach instantiate a rule the team is adopting, or is it itself a system-level choice? Apply **writing-adr**'s test to *that*; it holds → invoke **writing-adr**, and the `proposed` ADR commits with the design. Most features: neither.
8. **Write the design doc** — read `references/design-doc-shape.md` (sections and rules), `references/design-views.md` (the views you draw) and `references/example-design-<kind>.md` for your kind. Save to `docs/playbooks/designs/YYYY-MM-DD-<topic>.md` and commit.
9. **Self-review** (below), then **ask the user to review** and wait for explicit approval.
10. **Hand off** — **writing-plans** for a feature or slice, **writing-roadmap** for an initiative; nothing else.

## Initiatives

Work that won't fit one design → plan → execute cycle — several subsystems, old and new coexisting while it lands, a third ADR-worthy decision appearing — is an initiative. Say so and switch: the document becomes an initiative design per `references/initiative-design.md` (target architecture, coexistence mechanism, shared contracts, decisions; no slices), committed to the base branch as docs only, and the hand-off is **writing-roadmap**. Slice mode and the lifecycle are in that reference.

## Failure-mode pass

For any approach that puts an unreliable component on a load-bearing seam — an LLM at a generation boundary, a heuristic trusted to hold a structural invariant — ask how it degenerates under real load and what the deterministic alternative is. If holding it together needs post-hoc patches, the abstraction is wrong: make the structure deterministic and use the model only for bounded content-fill in a known shape.

## Design for isolation

Units with one purpose and well-defined interfaces, testable independently; internals leaking through an interface mean the boundary is wrong. In an existing codebase follow its patterns, fold in the improvements this work needs, leave unrelated refactoring alone.

## Self-review

1. **Placeholders and contradictions** — no TBDs; sections agree with each other.
2. **Ambiguity** — a requirement readable two ways gets one reading, stated.
3. **Scope** — one plan's worth, or an initiative?
4. **Stranger test** — could a teammate who has never opened the codebase follow Problem → Approach → Design? A sentence that needs three identifiers to parse is rewritten at component level.
5. **Walk the per-section rules** in `references/design-doc-shape.md`: each view answers its named question; a snippet only where the mechanism is the decision; Decisions, Assumptions, Open questions present; guarantees numbered and falsifiable; Status set.
6. **Accuracy** — before cutting anything: would it lose accuracy for the implementer? If not, cut.

Fix inline; no second review.

## User review gate

> "Design written and committed to `<path>`[, ADR at `<adr-path>`]. Please review it and let me know if you want any changes before we move on."

Wait for explicit approval; on changes, apply them and re-run the self-review. On approval set the header Status to `approved`. The ADR, if any, is reviewed at this same gate.

## Re-entering from executing-plans

The circuit-breaker sends a wrong seam back here. Work only that seam: keep the workspace; revise the `proposed` ADR in place if the decision changed — never a second one. For a slice the seam may be the initiative's: edit its design with a deviation line, and the roadmap if the order changes. Re-review at the gate; amend the plan to match.

## Red Flags — STOP

| Thought | Reality |
|---------|---------|
| "I'll paste the class so the implementer can't get it wrong" | Paste the contract; a body only when the mechanism is the decision. |
| "Context needs the call chain so readers understand" | Readers need the problem. Call chains are conversation residue. |
| "I'll add a future-optimizations section" | YAGNI. A property → Guarantees; an idea → `docs/followups.md`. |
| "Shorter is better, I'll drop the contracts" | Shorter is not the goal. Complete at the right altitude is. |
