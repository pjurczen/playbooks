---
name: brainstorming
description: Use before any non-trivial creative work (features, components, behaviour changes), to turn an idea into an approved design through clarifying questions and 2-3 proposed approaches.
---

# Brainstorming

Turn a request into a design by reasoning in five stages — problem, diagnosis, decision, shape, check — each producing one thing the next depends on. The design
doc is the trace of that reasoning, written to be read once, not a form to fill. Dialogue throughout: one question at a time, and approval before anything is
built on.

<HARD-GATE>
Present a design and get the user's approval before invoking a planning skill or writing any code — for every project, a todo list included. "Simple" is where
unexamined assumptions cost the most; the design can be a few sentences when the work is small, but the approval is what matters.
</HARD-GATE>

## When to skip

A change you can describe in one sentence and verify with one command — a rename, a typo, a constant — never enters brainstorming; using-playbooks' skip list
handles it.

## The five stages

Track them as todos; present each stage's output as you reach it and ask "looks right so far?" — a wrong diagnosis is cheap to fix before approaches exist.

**1. Problem — what are we actually trying to solve?** The request is usually phrased as a solution ("add a cache"). Recover the need behind it: who hurts, what
happens if nothing is done, what "done" looks like as something observable. The clarifying questions belong here — one at a time, multiple-choice when it fits,
about purpose, constraints and success, not implementation. *Output:* Problem, ending in "Done means".

**2. Diagnosis — what causes it?** Ground the problem in what exists, driven by the problem rather than by a category: the code paths, data and callers that
produce the pain; `docs/followups.md` (earlier attempts); existing ADRs per `.claude/documentation.md` (they constrain the fix; reversing one is a supersede);
the rules in `.claude/gates.md`; `docs/playbooks/initiatives/` (a slice of one? — `references/initiative-design.md`). No git repo yet? Offer `git init`, asking
first. *Output:* the cause, in structural terms a reader can check — Diagnosis.

**3. Decision — what are the moves, and which one?** Each approach is a different answer to the diagnosis; propose two or three, lead with your recommendation
and why, and run the failure-mode pass below on each. The kind of work falls out of the chosen approach: it adds within the existing structure, replaces
something, integrates, changes the data or a flow — or cannot land at once and needs old and new to coexist, which makes it an **initiative** (below). Ask
whether the approach instantiates a rule the team is adopting or is itself a system-level choice, and apply **writing-adr**'s test to that. *Output:* Approach
with the alternatives it beat, and Decisions.

**4. Shape — what does it look like, and what gets built?** The parts of the system that take part and who owns what, as a view (`references/design-views.md`;
the kinds table in `references/design-doc-shape.md` maps the approach to views, logic and contracts); the logic that carries the solution — rules, algorithms,
states — stated concretely, in the component that owns it; the contracts others build against. Units with one purpose and clean interfaces — leaking internals
mean a wrong boundary; follow the codebase's patterns, leave unrelated refactoring alone. *Output:* Architecture, Logic, Contracts.

**5. Check — does it solve the problem, and what does it cost?** Hold the design against stage 1: does it remove the diagnosed cause and reach "done means";
what changes for users and callers, what stops working, what could go wrong. Anything you assumed is settled now — looked up in the code, or asked; only what
someone outside the session must answer stays open. *Output:* Consequences, Open questions.

## Mechanics around the stages

- **Workspace** — once the decision is approved and before any commit, invoke **using-git-worktrees**, so every artifact lands on the feature branch.
- **ADR** — when stage 3 says so, invoke **writing-adr**; the `proposed` ADR commits with the design.
- **Write** — sections and rules in `references/design-doc-shape.md`; read `references/example-design-<kind>.md` for the chosen kind. Save to
  `docs/playbooks/designs/YYYY-MM-DD-<topic>.md` and commit.
- **Self-review**, then the **review gate**, then the **hand-off**: **writing-plans** for a feature or slice, **writing-roadmap** for an initiative. Nothing
  else.

## Initiatives

When stage 3's approach needs old and new to coexist while it lands, the document becomes an initiative design per `references/initiative-design.md` (target
architecture, coexistence mechanism, shared contracts, decisions; no slices), committed to the base branch as docs only; the hand-off is **writing-roadmap**.
Slice mode and lifecycle: that reference.

## Failure-mode pass

For any approach that puts an unreliable component on a load-bearing seam — an LLM at a generation boundary, a heuristic trusted to hold a structural invariant
— ask how it degenerates under real load and what the deterministic alternative is. If holding it together needs post-hoc patches, the abstraction is wrong:
make the structure deterministic and use the model only for bounded content-fill in a known shape.

## Self-review

1. **The chain holds** — the diagnosis explains the problem; the approach answers it; architecture and logic reach "done means".
2. **Every line earns its place** — walk the document with the test in `references/design-doc-shape.md`. A fact stated twice keeps one home; a section with
   nothing new is deleted; a decision nobody would contest goes.
3. **Stranger test** — could a teammate who has never opened the codebase repeat the solution, name its decisions and say what it costs after one read? The view
   shows components, not a call chain.
4. **Placeholders, contradictions, ambiguity** — no TBDs; sections agree; a requirement readable two ways gets one reading, stated. Status set.

Fix inline; no second review.

## User review gate

> "Design written and committed to `<path>`[, ADR at `<adr-path>`]. Please review it and let me know if you want any changes before we move on."

Wait for explicit approval; on changes, apply them and re-run the self-review. On approval set the header Status to `approved`.

## Re-entering from executing-plans

The circuit-breaker sends a wrong seam back here — usually a wrong diagnosis, or a decision that didn't survive contact. Work only that seam: keep the
workspace; revise the `proposed` ADR in place if the decision changed — never a second one. For a slice the seam may be the initiative's: edit its design with a
deviation line, and the roadmap if the order changes. Re-review at the gate; amend the plan to match.

## Red Flags — STOP

| Thought                                                      | Reality                                                                           |
|--------------------------------------------------------------|-----------------------------------------------------------------------------------|
| "The request says what to build, I'll design that"           | The request is a solution. Find the need first; the design is about the need.     |
| "I'll paste the class so the implementer can't get it wrong" | Show the rule and the contract; the body is the implementer's.                    |
| "Context needs the call chain so readers understand"         | Readers need the problem and the diagnosis. Call chains are conversation residue. |
| "I'll note this assumption so the reader knows"              | Check it in the code or ask. An assumption on the page is a question not asked.   |
