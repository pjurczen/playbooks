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

### Step 2: Detect environment

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
```

| State | Menu | Cleanup |
|-------|------|---------|
| `GIT_DIR == GIT_COMMON` (normal repo) | Standard 4 options | No worktree to clean up |
| `GIT_DIR != GIT_COMMON`, named branch | Standard 4 options | Provenance-based (Step 6) |
| `GIT_DIR != GIT_COMMON`, detached HEAD | Reduced 3 options (no merge) | None (externally managed) |

### Step 3: Determine base branch

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

Or ask: "This branch split from main — is that correct?"

### Step 4: Present options

**Normal repo or named-branch worktree — exactly these 4 options:**

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

**Detached HEAD — exactly these 3 options:**

```
Implementation complete. You're on a detached HEAD (externally managed workspace).

1. Push as new branch and create a Pull Request
2. Keep as-is (I'll handle it later)
3. Discard this work

Which option?
```

Don't add explanation — keep options concise.

### Step 5: Execute choice

**Before executing Option 1 or 2** (the work is landing), invoke **consolidating-docs** to graduate durable decisions from this feature's design/plan files into the repo's docs and delete the husks. It commits that as one change, so the doc updates land with the feature. Skip for Options 3 and 4 — nothing is landing.

#### Option 1: Merge locally

```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"

git checkout <base-branch>
git pull
git merge <feature-branch>

# Verify tests on merged result
<test command>
```

Then: cleanup worktree (Step 6), then delete branch:
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

Report: "Keeping branch <name>. Worktree preserved at <path>."

**Don't clean up the worktree.**

#### Option 4: Discard

Confirm first:
```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

Wait for the exact word "discard". If confirmed:

```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
```

Then: cleanup worktree (Step 6), then force-delete branch:
```bash
git branch -D <feature-branch>
```

### Step 6: Cleanup workspace

**Only runs for Options 1 and 4.** Options 2 and 3 always preserve the worktree.

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
WORKTREE_PATH=$(git rev-parse --show-toplevel)
```

- **If `GIT_DIR == GIT_COMMON`:** Normal repo, no worktree to clean up. Done.
- **If worktree path is under `.worktrees/`, `worktrees/`, or `~/.config/playbooks/worktrees/`:** Playbooks created this worktree — we own cleanup.
  ```bash
  MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
  cd "$MAIN_ROOT"
  git worktree remove "$WORKTREE_PATH"
  git worktree prune
  ```
- **Otherwise:** The harness owns this workspace. Do NOT remove it. Use the harness's exit tool if available; otherwise leave it.

## Quick reference

| Option | Merge | Push | Keep worktree | Cleanup branch |
|--------|-------|------|---------------|----------------|
| 1. Merge locally | yes | - | - | yes |
| 2. Create PR | - | yes | yes | - |
| 3. Keep as-is | - | - | yes | - |
| 4. Discard | - | - | - | yes (force) |

## Red Flags

**Never:**
- Proceed with failing tests
- Merge without verifying tests on the merged result
- Delete work without typed confirmation
- Force-push without explicit user request
- Remove a worktree before the merge succeeds
- Clean up worktrees you didn't create (provenance check)
- Run `git worktree remove` from inside the worktree being removed

**Always:**
- Verify tests before offering options
- Detect environment before presenting menu
- Present exactly 4 options (or 3 for detached HEAD)
- Get typed "discard" confirmation for Option 4
- Clean up the worktree only for Options 1 and 4
- `cd` to main repo root before worktree removal
- Run `git worktree prune` after removal
