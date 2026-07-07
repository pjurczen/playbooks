---
name: using-git-worktrees
description: Use when a design is approved and before any artifact is committed, to choose a workspace mode and set it up clean — defaults to a new worktree on a new feature branch.
---

# Using Git Worktrees

Choose where the work will land before anything is committed. Normally fired from **brainstorming** right after design approval — so the design doc, plan, and implementation all end up on the feature branch. Default is a new worktree on a new feature branch — it keeps your current checkout untouched and lets multiple features run in parallel.

**Announce at start:** "Using using-git-worktrees to choose a workspace mode."

## Step 0: Already isolated?

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
SUPER=$(git rev-parse --show-superproject-working-tree 2>/dev/null)
```

- `git rev-parse` fails entirely → not a git repo. Offer `git init` (ask first); if declined, skip workspace setup and warn that the pipeline's commits and doc consolidation won't work.
- `GIT_DIR != GIT_COMMON` and `SUPER` empty → you're already in a linked worktree. Skip to Step 2. Do NOT nest another worktree.
- `GIT_DIR != GIT_COMMON` and `SUPER` non-empty → you're in a submodule. Treat as a normal repo and continue.
- `GIT_DIR == GIT_COMMON` → normal checkout. Continue.

## Step 1: Pick a workspace mode

If the user has already declared a preference (CLAUDE.md, AGENTS.md, or the current request), honour it without asking.

Otherwise, dispatch `AskUserQuestion` (or ask in plain text if your harness lacks the tool) with:

> **How should we set up the workspace for this implementation?**
> 1. New worktree on a new feature branch *(default — current checkout stays untouched)*
> 2. New feature branch in the current checkout *(no worktree)*
> 3. Work directly on the current branch

For option 3, if the current branch is `main` or `master`, require an explicit second confirmation before proceeding.

### Option 1 — new worktree on a new feature branch (default)

If the harness provides a native worktree tool (`EnterWorktree`, a `/worktree` command, a `--worktree` flag), use it and skip to Step 2. Native tools handle placement and cleanup; using `git worktree add` alongside a native tool creates phantom state the harness can't manage.

Otherwise, git fallback:

**Directory** — first match wins:
1. User-declared preference.
2. Existing `.worktrees/` or `worktrees/` (`.worktrees/` wins if both).
3. Existing `~/.config/playbooks/worktrees/<project>/`.
4. Default: create `.worktrees/` at project root.

**Verify ignored** (project-local paths only) — check the directory you actually chose, not any alternative:

```bash
git check-ignore -q "<chosen-dir>"
```

If not ignored: add to `.gitignore`, commit, then proceed.

**Create:**

```bash
git worktree add "$path/$BRANCH_NAME" -b "$BRANCH_NAME"
cd "$path/$BRANCH_NAME"
```

If creation fails with a permission error (sandbox denial), tell the user the sandbox blocked it and re-ask Step 1 — option 2 or 3 is now the realistic choice.

### Option 2 — new feature branch in current checkout

```bash
git checkout -b "$BRANCH_NAME"
```

### Option 3 — current branch

Stay where you are. If on `main` / `master`, the second confirmation from Step 1 must already be in hand.

## Step 2: Project setup

**Only for option 1 (fresh worktree).** Options 2 and 3 reuse the current checkout, which is already set up.

Key off the lockfile — it names the package manager; guessing from the manifest alone installs with the wrong tool:

```bash
[ -f pnpm-lock.yaml ]    && pnpm install
[ -f yarn.lock ]         && yarn install
[ -f package-lock.json ] && npm install
[ -f uv.lock ]           && uv sync
[ -f poetry.lock ]       && poetry install
[ -f Cargo.toml ]        && cargo build
[ -f go.mod ]            && go mod download
```

No lockfile match? Use whatever the project's README / CI config declares — don't improvise a package manager.

## Step 3: Verify clean baseline

Run the project's test command. If tests fail: report failures and ask whether to proceed or investigate first — don't silently continue.

No test infrastructure yet (greenfield)? Say so and continue — don't block. The plan's first milestone should establish it (see writing-plans).

## Report

Record `BASE_SHA` now — it marks where the feature starts. The end-of-feature review (executing-plans) diffs `BASE_SHA..HEAD`, and in current-branch mode it's the only thing that identifies the feature's commits.

```
Workspace mode: <worktree | feature-branch | current-branch>
Path:           <full-path>
Branch:         <branch-name>
Base SHA:       <output of `git rev-parse HEAD`>
Tests:          <N passed, 0 failed>
Ready to work on <feature-name>.
```

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll just run `git worktree add` — the harness probably won't mind" | Native tool first. Phantom state the harness can't see is the #1 failure mode. |
| "Step 0 is overkill, I'll skip it" | Skipping creates nested worktrees inside existing ones. Always run it. |
| "The directory's probably ignored, no need to check" | Always `git check-ignore` for project-local paths. |
| "Tests fail in the baseline but I can tell which are pre-existing" | Stop. Confirm with the user before continuing. |
| "Working on main is fine — just this once" | Two confirmations from Step 1, no exceptions. |
