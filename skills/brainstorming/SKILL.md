---
name: brainstorming
description: Use before any non-trivial creative work (features, components, behaviour changes), to turn an idea into an approved design through clarifying questions and 2-3 proposed approaches.
---

# Brainstorming

Turn an idea into a fully formed design through natural dialogue. Ask questions one at a time. Propose 2–3 approaches. Settle on a design with the user, write it to disk, hand off to writing-plans.

**Announce at start:** "Using brainstorming to turn this idea into a design."

<HARD-GATE>
Do NOT invoke writing-plans, write any code, scaffold any project, or take any implementation action until you have presented a design and the user has approved it. This applies to EVERY project regardless of perceived simplicity.
</HARD-GATE>

<HARD-GATE>
The design doc carries contracts, not bodies: the public signatures it introduces or changes, with their semantics — never method bodies, private members, fields or boilerplate. It has two readers. A teammate who has never opened the codebase must be able to follow Problem → Approach → Shape. The implementer — in another session, with none of this conversation — must find nothing to guess in Contracts and Guarantees plus the plan. Shape and rules: `design-doc.md` beside this skill.
</HARD-GATE>

## Anti-pattern: "this is too simple to need a design"

Every project that enters this skill goes through the full process. A todo list, a single-function utility, a config change — all of them. "Simple" projects are where unexamined assumptions cause the most wasted work. The design can be short (a few sentences for truly simple things), but you MUST present it and get approval.

(Truly trivial changes — a typo, a renamed local, an adjusted constant, anything you can describe in one sentence and verify with one command — never enter brainstorming at all; that's using-playbooks' skip list. But once you're here, don't skip the design.)

## Checklist

Track these as todos and complete them in order:

1. **Explore project context** — files, recent commits, `docs/followups.md` if it exists (any open followups intersect with this work? fold them in if so), and existing ADRs in the repo's ADR home (per `.claude/documentation.md`) — they constrain the design; reversing one is a supersede, not a quiet contradiction — and `docs/playbooks/initiatives/`: if this work is a slice of one, link it; if every slice in its table has landed, offer to consolidate it. Not a git repo yet? Offer `git init` (ask first) — the pipeline commits its artifacts.
2. **Ask clarifying questions** — one at a time; focus on purpose, constraints, success criteria
3. **Propose 2–3 approaches** — with trade-offs and your recommendation
4. **Present the design in sections** — get user approval after each section
5. **Choose workspace** — invoke **using-git-worktrees**. This happens *before* anything is committed, so the design doc, the plan, and the implementation all land on the feature branch — that's what lets finishing-branch and consolidating-docs find and clean them up later. It waits until after design approval so abandoned brainstorms leave no orphan branches.
6. **Record the decision (if any)** — apply **writing-adr**'s bar (constrains future work, hard to reverse, there was a real choice) to the approach the user picked. Clears it → invoke **writing-adr**; the ADR is `proposed` and commits alongside the design doc. Most features don't clear it — no ADR is the normal outcome.
7. **Write design doc** — in the shape `design-doc.md` gives (worked example: `example-design.md`); save to `docs/playbooks/designs/YYYY-MM-DD-<topic>.md` and commit
8. **Self-review the doc** — placeholders, contradictions, ambiguity, scope (see below)
9. **Ask the user to review the written doc** — wait for explicit approval
10. **Transition to writing-plans** — invoke that skill; do not invoke any other implementation skill

## Decision flow

```dot
digraph brainstorming {
    "Explore project context" [shape=box];
    "Ask clarifying questions" [shape=box];
    "Propose 2-3 approaches" [shape=box];
    "Present design sections" [shape=box];
    "User approves design?" [shape=diamond];
    "Choose workspace (using-git-worktrees)" [shape=box];
    "Clears the ADR bar?" [shape=diamond];
    "Write ADR (writing-adr)" [shape=box];
    "Write design doc" [shape=box];
    "Self-review doc" [shape=box];
    "User reviews written doc?" [shape=diamond];
    "Invoke writing-plans" [shape=doublecircle];

    "Explore project context" -> "Ask clarifying questions";
    "Ask clarifying questions" -> "Propose 2-3 approaches";
    "Propose 2-3 approaches" -> "Present design sections";
    "Present design sections" -> "User approves design?";
    "User approves design?" -> "Present design sections" [label="no, revise"];
    "User approves design?" -> "Choose workspace (using-git-worktrees)" [label="yes"];
    "Choose workspace (using-git-worktrees)" -> "Clears the ADR bar?";
    "Clears the ADR bar?" -> "Write ADR (writing-adr)" [label="yes"];
    "Clears the ADR bar?" -> "Write design doc" [label="no (most features)"];
    "Write ADR (writing-adr)" -> "Write design doc";
    "Write design doc" -> "Self-review doc";
    "Self-review doc" -> "User reviews written doc?";
    "User reviews written doc?" -> "Write design doc" [label="changes requested"];
    "User reviews written doc?" -> "Invoke writing-plans" [label="approved"];
}
```

The terminal state is invoking **writing-plans**. Do NOT invoke executing-plans, bdd-testing, or any other implementation skill from here. The ONLY skill you invoke after brainstorming is writing-plans.

## How to ask

- Check the project state first (files, recent commits, followups.md)
- If the request describes multiple independent subsystems ("a platform with chat, file storage, billing, and analytics"), flag this immediately and help the user decompose into sub-projects. Each sub-project gets its own design → plan → implementation cycle. Don't spend questions refining details of a project that needs to be split first. When the slices share a target architecture, write an **initiative design** first (`design-doc.md`, *Initiative designs*) — the shared shape, contracts and slice order — then brainstorm slice 1 as a normal feature whose design links it. Work that fits one cycle gets no initiative; most work doesn't need one.
- For appropriately-scoped work, ask one question at a time
- Prefer multiple-choice when possible; open-ended is fine when needed
- Focus on purpose, constraints, success criteria — not implementation details

## How to propose approaches

- 2–3 distinct approaches with their trade-offs
- Lead with your recommendation and the reason for it
- Conversational, not a comparison matrix
- **Failure-mode pass** — for any approach that puts an *unreliable component* on a load-bearing seam (an LLM at a generation/sampling boundary, a heuristic trusted to hold a global/structural invariant), ask: how does it degenerate under real load, and what's the deterministic alternative? If holding it together would need post-hoc patches to force the behaviour, the abstraction is wrong — make the structure deterministic and use the model only for bounded content-fill in a known shape.
  - *"Free composition fenced by invariants" is the classic trap: the fence becomes ten patches.*

## How to present the design

- Once you understand what you're building, present the design in sections
- Scale each section to its complexity — a few sentences for straightforward parts, up to 200–300 words for nuanced ones
- After each section, ask "looks right so far?"
- The sections you present are the sections you write, in order: Problem → Approach (with the alternatives it beat; one line + link when an ADR exists) → Shape (one diagram, the components) → Contracts → Guarantees → Assumptions → Open questions → Risks → Out of scope. Rules per section in `design-doc.md`.
- Be ready to back up and clarify if something doesn't make sense

## Design for isolation and clarity

- Break the system into smaller units, each with one clear purpose, well-defined interfaces, testable independently
- For each unit: what does it do, how do you use it, what does it depend on?
- If a unit's internals leak through its interface, the boundary is wrong
- Smaller, well-bounded units are also easier for an agent to reason about and edit reliably

## Working in existing codebases

- Explore current structure before proposing changes; follow existing patterns
- If existing code has problems that affect this work (oversized file, unclear boundaries, tangled responsibilities), include targeted improvements as part of the design — the way a good developer improves code they're working in
- Don't propose unrelated refactoring; stay focused on what serves the current goal

## Self-review (after writing the doc)

Look at the design doc with fresh eyes:

1. **Placeholder scan** — any "TBD", "TODO", incomplete sections, vague requirements? Fix them.
2. **Internal consistency** — do sections contradict each other? Does the architecture match the feature descriptions?
3. **Scope check** — is this focused enough for a single implementation plan, or does it need decomposition?
4. **Ambiguity check** — could any requirement be interpreted two ways? Pick one and make it explicit.
5. **Body scan** — any fenced block that isn't `mermaid` or a signature-only contract? Cut it to the contract.
6. **Stranger test** — could a teammate who has never opened the codebase follow Problem → Approach → Shape? A sentence that needs three identifiers to parse gets rewritten at component level.
7. **Diagram check** — does it answer the question named before it, in ≤ 12 nodes with name-only labels?
8. **Contracts check** — every type the Shape marks new or changed has its signature in Contracts, failure behaviour included; Guarantees are numbered, falsifiable, and the last one says what must not change.
9. **Sections check** — Assumptions and Open questions are present, even if "None."; Problem ends with "Done means"; Status is set.
10. **Cross-cutting check** — does compatibility, migration, rollout or observability apply to this change? If yes, it's a Risk or an Out-of-scope line, not an omission.
11. **Accuracy check** — for anything you're tempted to cut: would cutting it lose accuracy for the implementer? If not, cut. If so, keep.

Fix issues inline. No need to re-review — just fix and move on.

## User review gate

After the self-review:

> "Design written and committed to `<path>`[, ADR at `<adr-path>`]. Please review it and let me know if you want any changes before we move to writing-plans."

Wait for explicit approval. If the user requests changes, make them and re-run the self-review. On approval, set the header Status to `approved`. The ADR, if one was written, is reviewed at this same gate — there is no separate confirmation step for it.

## Re-entering from executing-plans

The circuit-breaker in executing-plans sends a wrong seam back here. Work only that seam: don't re-run the workspace choice, and revise the existing `proposed` ADR in place if the decision changed — never a second ADR for the same feature. Update the design doc, re-review it at the gate, and amend the plan to match before execution resumes.

## Key principles

- **One question at a time** — don't overwhelm
- **YAGNI ruthlessly** — strip unnecessary features from every design
- **Always 2–3 approaches** — never present a single take as the only option
- **Incremental approval** — present, approve, advance
- **Be flexible** — back up and clarify when something doesn't add up

## Red Flags — STOP

| Thought | Reality |
|---------|---------|
| "I'll paste the class so the implementer can't get it wrong" | Paste the signature. The body is theirs; in a design it rots. |
| "Context needs the call chain so readers understand" | Readers need the problem. Call chains are conversation residue. |
| "The finding corrected an earlier hypothesis, worth recording" | It becomes a scenario in the plan, not a paragraph. |
| "I'll add a future-optimizations section" | YAGNI. A property → Guarantees; an idea → `docs/followups.md`. |
| "The slice diverged from the initiative, I'll add a callout" | Edit the initiative; it's a working doc. The ADR is the record. |
| "Shorter is better, I'll drop the contracts" | Shorter is not the goal. Complete at the right altitude is. |
| "Every feature needs an initiative doc" | Only work that won't fit one cycle. Most doesn't. |
