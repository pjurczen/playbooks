# Playbooks Release Notes

## v0.4.0 (2026-06-29)

### `consolidating-docs` skill — graduate decisions, delete the husks

Design docs and plans accumulated in `docs/playbooks/designs/` and `plans/` and were never cleaned up; the durable decisions inside them never reached the repo's real documentation. A new `consolidating-docs` skill extracts the durable content (decisions, rationale, alternatives, constraints), routes it per a `.claude/documentation.md` map — a general-purpose guide to where docs live and how they're maintained, usable beyond playbooks — then deletes the spent files (capture-then-delete; git keeps the history). It's fired by `finishing-branch` on the landing paths (merge / PR) so doc updates ship with the feature, and can be invoked manually to sweep the backlog. When the map is absent it offers to bootstrap one. `using-playbooks` advertises the skill and points any doc-touching task at the map.

### `followups.md` relocated to `docs/followups.md`

The durable followups backlog moves out of `docs/playbooks/` — now reserved for ephemeral design/plan working artifacts — up to `docs/followups.md`. The skills that read or write it (`brainstorming`, `writing-plans`, `executing-plans`) are updated accordingly.

## v0.3.1 (2026-05-14)

### `writing-plans` now requires committing the plan

`brainstorming` step 5 explicitly says "save and commit" for the design doc; `writing-plans` mentioned the commit only via the user-review gate template ("Plan written and committed to `<path>`"), with no enumerated commit step. The plan was occasionally landing as uncommitted changes. The "Save plans to:" line now reads "save and commit", restoring symmetry between the two skills. Design and plan commits land on the current branch / worktree, before any new worktree is created at the start of `executing-plans`.

## v0.3.0 (2026-05-07)

### `using-git-worktrees` added; worktrees are now the default workspace mode

A new `using-git-worktrees` skill is invoked from `executing-plans` Step 3 before any code is written. It detects existing isolation (linked worktrees, submodules) and then asks the user via `AskUserQuestion`:

1. **New worktree on a new feature branch** *(default — current checkout stays untouched)*
2. New feature branch in the current checkout
3. Work directly on the current branch *(requires explicit confirmation on `main` / `master`)*

User-declared preferences in CLAUDE.md / AGENTS.md / the request itself bypass the question. Native harness worktree tools are preferred over `git worktree add` when both are available; project-local `.worktrees/` paths are verified `.gitignore`-covered before creation.

This reverses the original v0.1.0 stance ("worktrees opt-in") documented in `docs/DESIGN.md` — solo work in practice benefits enough from the isolation to make it the default. `executing-plans` Step 3 wording updated accordingly.

## v0.2.2 (2026-05-07)

### Commit scope redefined as feature name

`milestone-commits` previously defined `(scope)` as "the subsystem touched", which agents misread — using the doc's audience (`chore(claude):`), the plugin used to author it (`docs(playbooks):`), or the filename's stem as the scope. Scope is now defined as the feature name as a short kebab-case slug — typically the topic from the design / plan filename (e.g. `feat(blacklist):`, `feat(agent-capture):`). Cross-cutting work (architecture docs, repo-wide config, tooling) keeps the no-scope carve-out. Examples and the anti-patterns table updated to match.

## v0.2.1 (2026-05-06)

### Milestone-commits invocation made explicit

`executing-plans` Step 8 read as a cross-reference ("commit per **milestone-commits**") and the skill body wasn't being loaded — agents fell back to using the plan's milestone titles as commit subjects (e.g. `Phase 2 M5: ReActAgent tool_calls writes`). Step 8 now explicitly invokes the skill, with a sentence noting the plan's milestone titles are reasoning scaffolding for the implementer, not commit material. `milestone-commits` anti-patterns table gains a row naming this failure mode.

## v0.2.0 (2026-05-06)

### End-of-feature review tightened

Closed a leak where trivial fixes were being promoted to `followups.md` instead of fixed in the review-fix milestone:

- Reviewer prompt now produces four severity buckets: Critical / Important / Minor (fix in review-fix milestone) / Followup (architectural, promote to `followups.md`).
- `Tier 2 — Durable followups` redefined to only items that need their own design / plan; anything fixable in a boy-scout pass stays in scope.
- Step 5 self-checkpoint now flags "added X but didn't wire it up at the call sites the plan named" as incomplete milestone work, not a finding for end-of-feature review.
- Red Flags row added: "Pre-existing ≠ out-of-scope."

## v0.1.0 (2026-05-06)

Initial release. Forked from [superpowers](https://github.com/obra/superpowers) and reshaped around different defaults: intent-shaped plans, main-session execution, milestone commits, BDD-flavoured tests, one end-of-feature review pass. See `README.md` for the skill list and `docs/DESIGN.md` for the rationale.

Mechanism: a SessionStart hook injects `using-playbooks` on every session start / clear / compact; other skills load on demand via the `Skill` tool.

Skill descriptions follow a canonical shape — `Use [trigger], to [goal]` — so pre-loaded metadata states both the firing condition and the purpose.
