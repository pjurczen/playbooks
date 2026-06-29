# Documentation consolidation & cleanup — design

## Problem

Design docs and plans accumulate in `docs/playbooks/designs/` and `docs/playbooks/plans/` and are never cleaned up. Two costs: the folders fill with dated husks, and the durable decisions captured inside them never graduate into the repo's real documentation — so the knowledge is buried in working artifacts no one re-reads.

## Approach

Extend the model the repo already uses for findings — in-session `## Findings` (ephemeral) → `followups.md` (durable) — one level up. Design and plan files are working artifacts. Their *durable* content (decisions and their rationale) graduates into the repo's real docs; the husks are deleted. Git remembers them.

This is a methodology change, not a mechanism change: a new artifact, a new skill, and wiring into the existing lifecycle.

## New artifact — `.claude/documentation.md`

A general-purpose **documentation-maintenance guide** for the repo. It describes:

- what documentation the repo keeps and where each piece lives,
- what kind of knowledge belongs in each (architecture decisions, user-facing changes, module docs, …),
- the conventions for updating them (formats, naming).

It is **not playbooks-specific**. Any agent or developer touching docs can read it to learn where things go. The `consolidating-docs` skill is one consumer: it reads this file as a **routing map** — "this durable decision → that doc."

A deterministic path (`.claude/documentation.md`) is chosen over a parsed CLAUDE.md heading so consumers can check for and read it reliably.

## New skill — `consolidating-docs`

One engine, two entry points:

- **Per-feature (automatic):** `finishing-branch` invokes it on the merge and PR paths, before executing the merge/push, scoped to *this branch's* design + plan files.
- **Sweep (manual):** invoked directly by the user. With no branch/feature context, it offers to process the whole backlog in `docs/playbooks/designs/` and `plans/`.

Engine:

1. **Read the map** (`.claude/documentation.md`). If absent → bootstrap (below).
2. **Select targets** — this branch's files, or the backlog.
3. **Extract durable content** — the decision, its *why*, alternatives rejected, hard constraints.
4. **Route per the map** — place each into the doc the map names. A decision with no home is surfaced to the user (extend the map? new doc?). Never guess a destination; never silently drop.
5. **Capture-then-delete** — only after durable content is written to its destination, delete the husk.
6. **One commit** — doc updates and deletions together, so they review and ship as a unit.

## Bootstrap — when `.claude/documentation.md` is absent

Most repos won't have the map on day one, so the skill offers to create it:

- Scan the repo (README, `docs/`, any ADRs, doc conventions in CLAUDE.md).
- Draft `.claude/documentation.md`: the doc inventory plus routing conventions. If the repo has **no** decisions home at all, the draft **proposes** one (e.g. `docs/adr/` or `DECISIONS.md`) so consolidation always has a target — offered, not forced.
- User approves → commit → proceed.
- User declines → skip consolidation and **leave the files untouched**. Never delete what wasn't consolidated.

## Cleanup semantics

Delete the husk outright — it's already committed, so history preserves it, consistent with the repo's "no dead code, git remembers" rule. The **capture-then-delete invariant** is absolute: a file is only deleted after its durable content lands in a destination doc.

## Durable vs ephemeral

- **Durable** (graduates): decisions, rationale, alternatives considered, hard constraints.
- **Ephemeral** (deleted with the husk): the Q&A dialogue, milestone breakdown, done-when criteria, per-step sequencing.

## Related change — relocate `followups.md`

`followups.md` is a durable, active backlog, distinct from the ephemeral design/plan husks. Move it from `docs/playbooks/followups.md` to `docs/followups.md`, so `docs/playbooks/` holds only the ephemeral working artifacts (`designs/`, `plans/`). This is a path change across every skill that names it.

## Files changed

- **`skills/consolidating-docs/SKILL.md`** — new skill.
- **`skills/finishing-branch/SKILL.md`** — invoke `consolidating-docs` on Options 1 (merge) and 2 (PR), before executing; skip on keep/discard.
- **`skills/using-playbooks/SKILL.md`** — add the skill to the library and the "when to invoke" table; add a light pointer telling any doc-touching task to consult `.claude/documentation.md`.
- **`skills/brainstorming/SKILL.md`**, **`skills/writing-plans/SKILL.md`**, **`skills/executing-plans/SKILL.md`** — update the `followups.md` path from `docs/playbooks/followups.md` to `docs/followups.md`.
- **`README.md`** — document `.claude/documentation.md`, the new lifecycle step, and the new `followups.md` path.
- **`docs/DESIGN.md`** — capture the rationale; update the `followups.md` path.

## Decisions settled

- **Sweep ergonomics** — one skill, context-detected (not a separate command).
- **Bootstrap** — proposes a decisions home when none exists; offered, not forced.
- **Reach beyond playbooks** — yes; add a light pointer so non-playbooks tasks also consult the map.

## Risks / open questions

- **Sweep breadth** — a backlog sweep can touch many files. It should summarize the planned consolidation before acting, and apply capture-then-delete per file.
- **Mis-routing** — mitigated by being map-driven and surfacing homeless decisions to the user rather than guessing.
- **finishing-branch density** — `finishing-branch` is already the densest skill; keep the logic in the standalone skill and have finishing-branch only invoke it.
