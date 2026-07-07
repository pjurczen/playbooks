---
name: milestone-commits
description: Use when committing implementation work, to produce readable history with one commit per meaningful slice.
---

# Milestone Commits

One commit per meaningful slice. Message describes the *why* of the slice. The implementation, the tests, and the milestone's refactor pass all go in the same commit.

## Core rule

Commit at meaningful slices, not at TDD steps. A milestone from the plan is one commit. Inside that commit:

- The behavioural test for the milestone
- The implementation
- The refactor pass (boy scout cleanup of the area you touched)
- Any incidental fixes the milestone forced

If you find yourself making 5 micro-commits per milestone (failing test → implementation → refactor → fix → cleanup), squash them. The durable history should be readable.

## When to commit

| Commit | Don't commit |
|--------|--------------|
| At the end of a milestone (test + impl + refactor together) | After writing a failing test (no implementation yet) |
| At the end of an end-of-feature review-fix pass | After every individual file edit |
| Before a risky refactor — commit the *completed sub-slice* as its own milestone first (see "When milestones are too big"); never a WIP snapshot | After every TDD step (red, green, refactor each as own commit) |
| When switching milestones — same rule: the finished sub-slice, not a half-done state | "Just to checkpoint" without a meaningful slice |

## Commit message shape

We follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/):

```
<type>[(scope)][!]: <description>

[optional body — the why, not the files]

[optional footer(s)]
```

**Subject line:**
- Starts with a type (see below), optional scope, then the outcome description
- Description is imperative mood: "add cookie rotation", not "added" / "adds"
- Describes the *outcome*, not the changeset: `feat(auth): reject malformed login requests with 400`, not `chore: update login.py and validator.py`
- ~50–72 characters total. Tight.

**Body (when needed):**
- The why. The motivation. The user-visible difference.
- NOT a play-by-play of every file touched. The diff is the play-by-play.
- NOT references to "the current task" / "as discussed" / "for issue #123". Those rot — they belong in the PR description, not in durable history.

## Commit types

| Type | When |
|------|------|
| `feat` | New user-visible behaviour |
| `fix` | Bug fix |
| `refactor` | Behaviour-preserving cleanup (no test changes implying new behaviour) |
| `perf` | Performance improvement (behaviour-preserving) |
| `test` | Test-only changes (rare for milestone commits — tests normally ship with `feat` / `fix`) |
| `docs` | Documentation only |
| `chore` | Repo housekeeping (deps, config, tooling) — no production code change |
| `build` | Build system or dependency changes |
| `ci` | CI configuration changes |

**For a milestone commit, pick the type that matches the primary outcome of the slice.** A milestone that adds a feature is `feat`, even though it includes a test and a small refactor pass. Don't fragment a milestone across multiple types — that's micro-commit thinking.

**Scope (optional but encouraged):** the feature name as a short kebab-case slug — typically the topic from the design / plan filename (e.g. `feat(blacklist):`, `feat(agent-capture):`). Skip scope for cross-cutting work (architecture docs, repo-wide config, tooling) where any feature name would mislead.

**Breaking changes:** add `!` after the type/scope AND mention it in the body or as a `BREAKING CHANGE:` footer.

```
feat(session-rotation)!: rotate session cookies on every request

BREAKING CHANGE: clients caching session cookies across requests will
break and need to refresh per request. Migration guide: docs/session-rotation-migration.md.
```

## Examples

Good (feat milestone):
```
feat(login-validation): reject malformed login requests with 400

Previously the auth endpoint silently accepted requests missing the
client_id field, returning a 500 from the downstream service. Now the
request is validated up front and a 400 is returned with a clear error.
```

Good (review-fix milestone):
```
fix(login-validation): validate client_id length, not just presence

End-of-feature review caught that a 0-length client_id was passing the
presence check and still triggering the downstream 500.
```

Good (refactor-only milestone, no scope — cross-cutting cleanup):
```
refactor: extract token-classification into TokenClassifier

Behaviour-preserving extraction. Drops request_parser from 380 to 210
lines and lets the classifier be unit-tested in isolation.
```

Bad (micro-commit churn — same milestone fragmented across 4 commits, squash into one):
```
test(login-validation): add failing test for empty email
feat(login-validation): add empty email check
refactor(login-validation): extract validator
fix(login-validation): typo
```
The format is fine — the *granularity* is wrong. The four together are one milestone, so they should be one commit.

Bad (file-list narration — describe behaviour, not files):
```
chore: update login.py, validator.py, and tests/auth_test.py

Modified login.py to call validator.py. Added new validator.py with
validate_email function. Updated tests/auth_test.py to test it.
```

## Anti-patterns

| Pattern | Why it's bad |
|---------|--------------|
| One commit per TDD step | History is noise. `git log --oneline` becomes useless. |
| One commit per file | The slice is the unit, not the file. |
| "WIP" / "checkpoint" commits left in history | They rot the log. Squash them before merge. |
| Commit message describes files, not behaviour | The diff describes files. The message describes intent. |
| References to ticket numbers, "as discussed", "per review" | Belongs in the PR description, not in durable history. |
| Subject reuses the plan's milestone label (e.g. `Phase 2 M5: ...`) | The plan is scaffolding for the implementer; subjects describe outcome with a Conventional Commits type. |
| Scope is the doc's audience, the AI tool, or the plugin used to author it (`(claude)`, `(playbooks)`) | Scope = feature slug, not who reads the file or what produced it. |

## When milestones are too big

Sometimes a milestone turns out larger than expected mid-execution. If a single milestone is producing a >300-line diff that touches >5 files, that's a signal to either:

- Pause and revise the plan to split the milestone, or
- Commit the natural sub-slices as their own milestones (each with a clear "intermediate but observable" outcome)

Don't force everything into one giant commit just to avoid touching the plan. Don't fragment into micro-commits to avoid touching the plan either.

## Red Flags — STOP

- About to make a "WIP" / "checkpoint" / "save progress" commit
- Commit message has no type prefix (Conventional Commits violation)
- Commit message describes files instead of behaviour ("update login.py …")
- 5+ commits coming from a single plan milestone
- About to reference a ticket number / PR number / "as discussed" in the message body
- Tempted to commit the test on its own before the implementation lands
- Using `chore:` or `refactor:` to disguise actual feature/fix work
- Breaking change without `!` in the subject and a `BREAKING CHANGE:` footer
