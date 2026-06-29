---
name: consolidating-docs
description: Use when landing a feature (merge or PR) or sweeping the backlog, to graduate durable decisions out of design/plan files into the repo's real docs and then delete the husks.
---

# Consolidating Docs

Design docs and plans are working artifacts. The durable decisions inside them belong in the repo's real documentation; the husks should not pile up in `docs/playbooks/`. This skill extracts what's durable, routes it into the docs your `.claude/documentation.md` map names, and deletes the spent files. They're already committed — git remembers them.

This is not about `docs/followups.md` — that's a separate, durable backlog that stays put.

**Announce at start:** "Using consolidating-docs to consolidate and clean up design/plan files."

## When this runs — and when to skip

- **Fired by finishing-branch** on the merge and PR paths, before the merge/push — scoped to the feature being landed.
- **Invoked manually** with no feature context — offer to sweep the backlog in `docs/playbooks/designs/` and `plans/`.

Skip when:
- The user chose *keep* or *discard* in finishing-branch — nothing is landing, so nothing graduates.
- There are no design/plan files to process.

<HARD-GATE>
Never delete a design or plan file until its durable content has been written to a destination doc and that change is staged for the same commit. Capture first, delete second. No exceptions.
</HARD-GATE>

## The map: `.claude/documentation.md`

The map tells you where durable knowledge belongs. Read it first. If it's missing, run **Bootstrap** below — do not guess destinations.

Expected shape:

```markdown
# Documentation map

How documentation is maintained in this repo.

## Where things live
- `docs/architecture.md` — system structure and component boundaries.
- `docs/adr/NNNN-*.md` — one architecture decision record per decision.
- `README.md` — install, usage, overview.

## Routing — where durable knowledge goes
- A decision + its rationale → a new ADR in `docs/adr/`.
- A change to component boundaries → `docs/architecture.md`.
- A user-facing behaviour change → `CHANGELOG.md`.

## Conventions
- ADRs are numbered and immutable once accepted; supersede rather than edit.
```

This file is general-purpose — any doc-touching task can read it, not just this skill.

## Bootstrap — when the map is absent

1. Scan the repo: `README`, `docs/`, any `adr/`, doc conventions in CLAUDE.md.
2. Draft `.claude/documentation.md` in the shape above: the real doc inventory plus routing rules. If the repo has **no** home for decisions at all, propose creating one (`docs/adr/` or a `DECISIONS.md`) — propose, don't impose.
3. Present the draft. On approval, commit it, then continue.
4. If the user declines, **stop**: leave the design/plan files untouched. Never delete what you couldn't consolidate.

## The consolidation loop

For each target file:

1. **Read it.** Separate durable from ephemeral (see the bar below).
2. **Route each durable item** to the destination the map names. If an item has no home, **ask the user** — extend the map, or pick a doc. Never invent a destination; never drop it silently.
3. **Write** the durable content into the destination doc, following that doc's conventions (ADR format, changelog style, …).
4. **Delete the husk** — only now, after its content has landed.

Then commit (see below).

## Scope by entry point

- **Per-feature (finishing-branch):** the design and plan files for the feature being landed — those added on this branch under `docs/playbooks/designs/` and `plans/`.
- **Sweep (manual):** every file under `docs/playbooks/designs/` and `plans/`. Summarize what you intend to consolidate and where *before* touching anything, then work file by file.

## Durable vs ephemeral

- **Durable** (graduates): decisions, their rationale, alternatives considered, hard constraints.
- **Ephemeral** (dies with the husk): the Q&A dialogue, milestone breakdown, done-when criteria, per-step sequencing.

When in doubt: a thing is durable if a future contributor would ask "why was this done this way?" and want the answer.

## Commit

One commit for the whole operation — destination-doc updates **and** husk deletions together, so they review and ship as a unit. Use a Conventional Commits `docs:` subject describing what was consolidated, per **milestone-commits**.

## Red Flags — STOP

| Thought | Reality |
|---------|---------|
| "I'll delete the husk now and write the doc after" | Capture first. A crash between the two loses the decision. |
| "There's no map, I'll just put it somewhere sensible" | Guessed destinations rot. Bootstrap the map or ask. |
| "This decision has no obvious home, I'll drop it" | Surface it. Homeless durable knowledge means the map is incomplete. |
| "The whole design doc is durable — I'll copy it wholesale" | Then you've moved a husk, not consolidated. Extract decisions, not dialogue. |
| "Keep/discard, but I'll consolidate anyway" | Nothing is landing. Skip. |
