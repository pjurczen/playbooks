---
name: brainstorming
description: Use before any non-trivial creative work (features, components, behaviour changes), to turn an idea into an approved design through clarifying questions and 2-3 proposed approaches.
---

# Brainstorming

Turn a request into a design by reasoning in five stages — problem, diagnosis, decision, shape, check — each producing
one thing the next depends on. The design doc is the trace of that reasoning, not a form. Dialogue throughout: one
question at a time, and approval before anything is built on.

<HARD-GATE>
Present a design and get the user's approval before invoking a planning skill or writing any code — for every project, a todo list included. "Simple" is where unexamined assumptions cost the most; the design can be a few sentences when the work is small, but the approval is what matters.
</HARD-GATE>

## When to skip

A change you can describe in one sentence and verify with one command — a rename, a typo, a constant — never enters
brainstorming; using-playbooks' skip list handles it. Once you're here, don't skip the design.

## The five stages

Track them as todos; present each stage's output as you reach it and ask "looks right so far?" — a wrong diagnosis is
cheap before approaches are proposed and expensive after.

**1. Problem — what are we actually trying to solve?** The request is usually phrased as a solution ("add a cache", "
unify the calculation"). Recover the need behind it: who hurts, what happens if nothing is done, what "done" looks like
as something observable. The clarifying questions belong here — one at a time, multiple-choice when it fits, about
purpose, constraints and success, not implementation. If the ask and the need differ, the design is about the need.
*Output:* Problem, ending in "Done means".

**2. Diagnosis — what causes it?** Ground the problem in what exists, driven by the problem rather than by a category:
the code paths, data and callers that produce the pain; `docs/followups.md` (earlier attempts); existing ADRs per
`.claude/documentation.md` (they constrain the fix; reversing one is a supersede); `docs/playbooks/initiatives/` (a
slice of one? — `references/initiative-design.md`). No git repo yet? Offer `git init`, asking first. *Output:* the
cause, in structural terms a reader can check — Diagnosis.

**3. Decision — what are the moves, and which one?** Each approach is a different answer to the diagnosis; propose two
or three, lead with your recommendation and why, and run the failure-mode pass below on each. The kind of work falls out
of the chosen approach: it adds within the existing structure, replaces something, integrates, changes the data or a
flow — or cannot land at once and needs old and new to coexist, which makes it an **initiative** (below). Ask whether
the approach instantiates a rule the team is adopting or is itself a system-level choice, and apply **writing-adr**'s
test to that. *Output:* Approach with the alternatives it beat, and Decisions.

**4. Shape — what does it look like, exactly?** The components; the views a reader needs (`references/design-views.md`;
the kinds table in `references/design-doc-shape.md` maps the chosen approach to views and contracts); the contracts the
implementer must match; the mechanism only where it is the decision; the guarantees as falsifiable properties. Units
with one purpose and clean interfaces — leaking internals mean a wrong boundary; in an existing codebase follow its
patterns, leave unrelated refactoring alone. *Output:* Design, Contracts, Guarantees.

**5. Check — does it solve the problem?** Hold the design against stage 1: does it remove the diagnosed cause; do the
guarantees cover "done means"; what was assumed without asking; what stays open, for whom, by when; what could go wrong
with the approach itself; what is deliberately out. *Output:* Assumptions, Open questions, Risks, Out of scope.

## Mechanics around the stages

- **Workspace** — once the decision is approved and before any commit, invoke **using-git-worktrees**, so every artifact
  lands on the feature branch.
- **ADR** — when stage 3 says so, invoke **writing-adr**; the `proposed` ADR commits with the design.
- **Write** — sections and rules in `references/design-doc-shape.md`; read `references/example-design-<kind>.md` for the
  chosen kind. Save to `docs/playbooks/designs/YYYY-MM-DD-<topic>.md` and commit.
- **Self-review**, then the **review gate**, then the **hand-off**: **writing-plans** for a feature or slice, *
  *writing-roadmap** for an initiative. Nothing else.

## Initiatives

When stage 3's approach needs old and new to coexist while it lands, the document becomes an initiative design per
`references/initiative-design.md` (target architecture, coexistence mechanism, shared contracts, decisions; no slices),
committed to the base branch as docs only; the hand-off is **writing-roadmap**. Slice mode and lifecycle: that
reference.

## Failure-mode pass

For any approach that puts an unreliable component on a load-bearing seam — an LLM at a generation boundary, a heuristic
trusted to hold a structural invariant — ask how it degenerates under real load and what the deterministic alternative
is. If holding it together needs post-hoc patches, the abstraction is wrong: make the structure deterministic and use
the model only for bounded content-fill in a known shape.

## Self-review

1. **The chain holds** — the diagnosis explains the problem; the approach answers the diagnosis; the guarantees cover "
   done means".
2. **Placeholders, contradictions, ambiguity** — no TBDs; sections agree; a requirement readable two ways gets one
   reading, stated.
3. **Stranger test** — could a teammate who has never opened the codebase follow Problem → Diagnosis → Approach →
   Design? A sentence needing three identifiers to parse is rewritten at component level.
4. **Walk the per-section rules** in `references/design-doc-shape.md`: each view answers its named question; a snippet
   only where the mechanism is the decision; Decisions, Assumptions, Open questions present; guarantees numbered and
   falsifiable; Status set.
5. **Accuracy** — before cutting anything: would it lose accuracy for the implementer? If not, cut.

Fix inline; no second review.

## User review gate

> "Design written and committed to `<path>`[, ADR at `<adr-path>`]. Please review it and let me know if you want any
> changes before we move on."

Wait for explicit approval; on changes, apply them and re-run the self-review. On approval set the header Status to
`approved`. The ADR, if any, is reviewed at this same gate.

## Re-entering from executing-plans

The circuit-breaker sends a wrong seam back here — usually a wrong diagnosis, or a decision that didn't survive contact.
Work only that seam: keep the workspace; revise the `proposed` ADR in place if the decision changed — never a second
one. For a slice the seam may be the initiative's: edit its design with a deviation line, and the roadmap if the order
changes. Re-review at the gate; amend the plan to match.

## Red Flags — STOP

| Thought                                                      | Reality                                                                           |
|--------------------------------------------------------------|-----------------------------------------------------------------------------------|
| "The request says what to build, I'll design that"           | The request is a solution. Find the need first; the design is about the need.     |
| "I'll paste the class so the implementer can't get it wrong" | Paste the contract; a body only when the mechanism is the decision.               |
| "Context needs the call chain so readers understand"         | Readers need the problem and the diagnosis. Call chains are conversation residue. |
| "I'll add a future-optimizations section"                    | YAGNI. A property → Guarantees; an idea → `docs/followups.md`.                    |
