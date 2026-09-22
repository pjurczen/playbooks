---
name: consolidating-docs
description: Use when landing a feature (merge or PR) or sweeping the backlog, to graduate durable decisions out of design/plan files into the repo's real docs and then delete the husks.
---

# Consolidating Docs

Design docs and plans are working artifacts: the durable decisions inside them belong in the repo's real documentation, and the husks should not pile up in `docs/playbooks/`. This skill routes what's durable into the docs your `.claude/documentation.md` map names and deletes the spent files — git remembers them. `docs/followups.md` is a durable backlog and stays put.

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

Read it first; it says where durable knowledge belongs. Missing? Run **Bootstrap** below — never guess destinations. Expected shape:

```markdown
# Documentation map

How documentation is maintained in this repo.

## Where things live
- `docs/architecture.md` — system structure and component boundaries.
- `docs/adr/YYYY-MM-DD-*.md` — one architecture decision record per *architecturally significant* decision (shape: writing-adr).
- `README.md` — install, usage, overview.

## Routing — where durable knowledge goes
- An architecturally significant decision → an ADR in `docs/adr/`, via **writing-adr** (normally already on the branch from brainstorming — promote it).
- A smaller decision → a sentence in `docs/architecture.md`.
- A change to component boundaries → `docs/architecture.md`.
- A user-facing behaviour change → `CHANGELOG.md`.

## Conventions
- ADRs are immutable once accepted (status line excepted); supersede rather than edit.
```

## Bootstrap — when the map is absent

1. Scan the repo: `README`, `docs/`, any `adr/`, doc conventions in CLAUDE.md.
2. Draft `.claude/documentation.md` in the shape above: the real doc inventory plus routing rules. If the repo has **no** home for decisions at all, propose creating one (`docs/adr/` or a `DECISIONS.md`) — propose, don't impose.
3. Present the draft. On approval, commit it, then continue.
4. If the user declines, **stop**: leave the design/plan files untouched. Never delete what you couldn't consolidate.

## ADRs — once per feature, before the loop

ADRs are handled once, up front, and never from inside the per-file loop below. **writing-adr** owns the format; this skill only promotes.

1. **Find** the ADRs this feature added: `git diff --name-only <base>..HEAD -- <ADR home(s) from the map>`.
2. **Reconcile.** The end-of-feature reviewer reported whether the Decision is still true of the code. If it drifted, amend the Decision in place — it's still `proposed`.
3. **Promote.** Flip `proposed` → `accepted (<landing date>)`. Update the index if the map names one.
4. **Fallback** — no ADR on the branch, but the design doc's Approach section clears writing-adr's bar (the user brought their own design, or brainstorming missed it)? Invoke **writing-adr** once, from the design doc — not from the diff.

Most features have no ADR to promote and don't earn one at the fallback. That's the normal outcome, not a gap.

**Slices.** If the design links an initiative, flip the slice's row in the roadmap to `landed` (both files live on the base branch and travel with the merge). When every row is landed, ask whether the initiative is complete; on yes, graduate per `../brainstorming/references/initiative-design.md` — the target architecture into the architecture doc, the below-bar decisions as sentences there, the coexistence mechanism dropped — and delete the initiative design and the roadmap. The ADRs remain.

## The consolidation loop

For each target file:

1. **Read it.** Separate durable from ephemeral (see the bar below).
2. **Route each durable item** to a non-ADR destination the map names — ADRs were handled above; never create one from inside this loop. If an item has no home, **ask the user** — extend the map, or pick a doc. Never invent a destination; never drop it silently.
3. **Write** the durable content into the destination doc, following that doc's conventions (changelog style, architecture-doc structure, …). Rewrite any reference to a design/plan file as you write — inline what it points at, or point to the content's new home. The husk is about to be deleted; a link to it is a link to nothing.
4. **Delete the husk** — only now, after its content has landed.

Then verify and commit (see below).

## Verify — no dangling references

Before committing, prove nothing still points at the husks:

```bash
git grep -n "docs/playbooks/" -- ':(exclude)docs/playbooks'
```

Also grep each deleted file's basename. Any hit naming a specific design or plan file is a dangling reference — inline the content or repoint the link, then re-run. Mentions of the workspace convention itself (CLAUDE.md explaining where plans live) are fine.

## Scope by entry point

- **Per-feature (finishing-branch):** the design and plan files for the feature being landed — those added on this branch under `docs/playbooks/designs/` and `plans/`. Identify them with `git diff --name-only <base>..HEAD`, `<base>` being the branch point finishing-branch establishes in its Step 3 — the workspace is chosen during brainstorming, so the feature's design/plan commits are always inside that range. Never `docs/playbooks/initiatives/` — an initiative outlives its slices.
- **Sweep (manual):** every file under `docs/playbooks/designs/` and `plans/`. Summarize what you intend to consolidate and where *before* touching anything, then work file by file. For `docs/playbooks/initiatives/`: ask whether every slice in the roadmap has landed. Only then graduate the initiative as above; otherwise leave both files untouched.

## Durable vs ephemeral

- **Durable** (graduates): decisions, their rationale, alternatives considered, hard constraints.
- **Ephemeral** (dies with the husk): the Q&A dialogue, milestone breakdown, done-when criteria, per-step sequencing.
- **Altitude:** durable knowledge sits at design altitude — components, boundaries, mechanisms, invariants. Symbols, signatures, annotations and file paths are ephemeral; git has them and they rot on the first rename.

When in doubt: a thing is durable if a future contributor would ask "why was this done this way?" and want the answer. A decision below writing-adr's bar still gets an answer — one sentence in the nearest architecture or module doc, or nowhere at all (the commit message has it). It does not get an ADR.

## Commit

One commit for the whole operation — destination-doc updates **and** husk deletions together, so they review and ship as a unit. Use a Conventional Commits `docs:` subject describing what was consolidated, per **milestone-commits**.

## Red Flags — STOP

| Thought | Reality |
|---------|---------|
| "I'll delete the husk now and write the doc after" | Capture first. A crash between the two loses the decision. |
| "There's no map, I'll just put it somewhere sensible" | Guessed destinations rot. Bootstrap the map or ask. |
| "This decision has no obvious home, I'll drop it" | Surface it. Homeless durable knowledge means the map is incomplete. |
| "The whole design doc is durable — I'll copy it wholesale" | Then you've moved a husk, not consolidated. Extract decisions, not dialogue. |
