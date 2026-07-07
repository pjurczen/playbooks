---
name: finishing-branch
description: Use when implementation is complete and tests pass, to integrate the work via merge, PR, keep, or discard.
---

# Finishing a Development Branch

Verify tests → detect environment → present options → consolidate docs (when landing) → execute choice → clean up.

**Announce at start:** "Using finishing-branch to complete this work."

## Process

### Step 1: Verify tests

Run the project's test suite (adjust to project: `npm test` / `cargo test` / `pytest` / `go test ./...`).

If tests fail:
```
Tests failing (<N> failures). Must fix before completing:

[Show failures]

Cannot proceed with merge / PR until tests pass.
```

Stop. Do not proceed to Step 2.

If the project has **no test suite at all**, state that explicitly and continue — a missing suite is not a failing suite.

### Step 2: Detect environment — capture state NOW, from inside the workspace

Run these once, from the workspace you implemented in, and keep the values. Step 6 consumes them *after* you've `cd`'d away — re-running the detection from the main checkout always concludes "no worktree".

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
WORKTREE_PATH=$(git rev-parse --show-toplevel)
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)   # prints "HEAD" when detached
MAIN_ROOT=$(git -C "$GIT_COMMON/.." rev-parse --show-toplevel)
```

| State | Menu | Cleanup |
|-------|------|---------|
| `CURRENT_BRANCH` is the base branch (current-branch mode) | On-base menu (B1–B2) | None |
| `GIT_DIR == GIT_COMMON`, feature branch (normal repo) | Standard menu (1–4) | No worktree to clean up |
| `GIT_DIR != GIT_COMMON`, named branch (worktree) | Standard menu (1–4) | Provenance-based (Step 6) |
| `GIT_DIR != GIT_COMMON`, detached HEAD | Detached menu (D1–D3) | None (externally managed) |

### Step 3: Determine base branch

You need the base branch *name* (later commands check it out) and the branch point:

```bash
BASE_BRANCH=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')
```

If that's unset, look for a local `main` / `master`; if still ambiguous, ask: "This branch split from main — is that correct?" Then:

```bash
BASE_POINT=$(git merge-base HEAD "$BASE_BRANCH")
```

In current-branch mode `merge-base` is just `HEAD` — use the `BASE_SHA` recorded in the using-git-worktrees report as the branch point instead.

### Step 4: Present options

Don't add explanation — keep options concise.

**Standard menu (normal repo or named-branch worktree):**

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

**Detached menu (detached HEAD — externally managed workspace):**

```
Implementation complete. You're on a detached HEAD.

D1. Push as new branch and create a Pull Request
D2. Keep as-is (I'll handle it later)
D3. Discard this work

Which option?
```

**On-base menu (work was committed directly on <base-branch>):**

```
Implementation complete — the commits are already on <base-branch>.

B1. Keep them (work is landed)
B2. Revert the feature commits

Which option?
```

### Step 5: Execute choice

**Consolidation gate:** before executing any landing option (1, 2, D1, B1 — anything that integrates the work), invoke **consolidating-docs** to graduate durable decisions from this feature's design/plan files into the repo's docs and delete the husks. It commits that as one change, so the doc updates land with the feature. For keep and discard options (3, 4, D2, D3, B2), skip consolidation — nothing is landing.

#### Option 1: Merge locally

```bash
cd "$MAIN_ROOT"
git checkout "$BASE_BRANCH"
git pull
git merge <feature-branch>

# Verify tests on merged result
<test command>
```

Then: cleanup worktree (Step 6, using the Step-2 values), then delete branch:
```bash
git branch -d <feature-branch>
```

#### Option 2: Push and create PR

```bash
git push -u origin <feature-branch>

gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets of what changed>

## Test Plan
- [ ] <verification steps>
EOF
)"
```

**Do NOT clean up the worktree** — the user needs it alive to iterate on PR feedback.

#### Option 3: Keep as-is

Report: "Keeping branch <name>. Worktree preserved at <path>." **Don't clean up the worktree.**

#### Option 4: Discard

Confirm first:
```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

Wait for the exact word "discard". If confirmed: `cd "$MAIN_ROOT"`, cleanup worktree (Step 6), then force-delete branch:
```bash
git branch -D <feature-branch>
```

#### Option D1: Push detached work as a new branch + PR

There is no local branch — push HEAD to a new remote branch (ask for or derive a name):

```bash
git push origin HEAD:refs/heads/<new-branch>
gh pr create --head <new-branch> --title "<title>" --body "<as Option 2>"
```

Leave the workspace alone — it's externally managed.

#### Option D2: Keep as-is (detached)

Report: "Keeping work at <HEAD SHA>. Workspace preserved." Nothing else to do.

#### Option D3: Discard (detached)

Confirm with the typed word "discard" (list the commits, as Option 4). There is no branch to delete and the workspace is externally managed — report the HEAD SHA so the commits stay recoverable, and leave everything in place.

#### Option B1: Keep work already on base

The commits are already on `<base-branch>`. After the consolidation gate, report and stop — no merge, no cleanup.

#### Option B2: Revert the feature commits

List the commits in `BASE_SHA..HEAD` and confirm with the typed word "revert". Then:

```bash
git revert --no-edit <BASE_SHA>..HEAD
```

**Never** delete or reset the base branch — revert adds inverse commits and keeps history intact.

### Step 6: Cleanup workspace

**Only runs for Options 1 and 4.** Options 2 and 3 preserve the worktree; detached and on-base modes never clean up. Use the values captured in Step 2 — do not re-detect from the main checkout.

- **If `GIT_DIR == GIT_COMMON`:** normal repo, no worktree to clean up. Done.
- **If `WORKTREE_PATH` is under `.worktrees/`, `worktrees/`, or `~/.config/playbooks/worktrees/`:** playbooks created this worktree — we own cleanup.
  ```bash
  cd "$MAIN_ROOT"
  git worktree remove "$WORKTREE_PATH"
  git worktree prune
  ```
- **Otherwise:** the harness owns this workspace. Do NOT remove it. Use the harness's exit tool if available; otherwise leave it.

## Quick reference

| Option | Integrates | Push | Keep workspace | Branch cleanup |
|--------|-----------|------|----------------|----------------|
| 1. Merge locally | yes | - | removed (Step 6) | delete |
| 2. Create PR | via PR | yes | yes | - |
| 3. Keep as-is | - | - | yes | - |
| 4. Discard | - | - | removed (Step 6) | force-delete |
| D1. Push + PR | via PR | yes | yes (external) | - |
| D2. Keep | - | - | yes (external) | - |
| D3. Discard | - | - | yes (external) | none exists |
| B1. Keep on base | already landed | - | yes | - |
| B2. Revert | - | - | yes | revert commits |

## Red Flags

**Never:**
- Proceed with failing tests
- Merge without verifying tests on the merged result
- Delete or revert work without typed confirmation
- Force-push without explicit user request
- Remove a worktree before the merge succeeds
- Clean up worktrees you didn't create (provenance check)
- Run `git worktree remove` from inside the worktree being removed
- Re-run the Step-2 detection after leaving the workspace — from the main checkout it always says "no worktree"
- Delete or `git reset` the base branch — B2 reverts, nothing else

**Always:**
- Verify tests before offering options
- Capture Step-2 state from inside the workspace, before any `cd`
- Present exactly the menu the Step-2 table names (1–4, D1–D3, or B1–B2)
- Get typed confirmation for discard and revert
- `cd` to `$MAIN_ROOT` before worktree removal, and `git worktree prune` after
