---
name: verifying-before-done
description: Use before claiming work is complete, fixed, or passing, and before commits or PRs, to confirm success with fresh verification evidence rather than assumption.
---

# Verifying Before Done

**Before you claim any status — done, fixed, passing, complete, or any paraphrase — name the command that proves it, run
it fresh, read the whole output, and only then make the claim, with the evidence.** A claim without fresh evidence is
the failure this skill exists to stop: the user reads it as verification, and the moment it's wrong everything
downstream is built on it.

## The gate

1. **Identify** — what command proves this claim?
2. **Run** — the full command, now, in this message. A previous run doesn't count.
3. **Read** — the whole output: exit code, failure count, not just the last line.
4. **Claim** — state what the output shows. If it contradicts the claim, say the actual status instead.

This applies before committing, pushing, opening a PR, closing a milestone, and handing back to the user.

## What proves what

| Claim                 | Requires                             | Not sufficient                 |
|-----------------------|--------------------------------------|--------------------------------|
| Tests pass            | Test command output: 0 failures      | Previous run, "should pass"    |
| Linter clean          | Linter output: 0 errors              | Partial check, extrapolation   |
| Build succeeds        | Build command: exit 0                | Linter passing, logs look good |
| Bug fixed             | Test of the original symptom: passes | Code changed, assumed fixed    |
| Regression test works | Red-green cycle verified             | Test passes once               |
| Subagent completed    | VCS diff shows the changes           | Subagent reports "success"     |
| Requirements met      | Line-by-line checklist               | Tests passing                  |
| Structure holds       | Gate output from `.claude/gates.md`  | Tests passing                  |

## Two patterns

- **Tests:** run the command → see `34/34 pass` → "All tests pass". Not: "should pass now".
- **Regression test:** write → run (pass) → revert the fix → run (**must fail**) → restore → run (pass). Not: "I've
  written a regression test".

## Rationalizations

| Excuse                              | Reality                                    |
|-------------------------------------|--------------------------------------------|
| "Should work now" / "I'm confident" | Confidence isn't evidence. Run it.         |
| "Linter passed"                     | Linter ≠ compiler ≠ tests.                 |
| "The subagent said success"         | Check the diff and run the tests yourself. |
| "A partial check is enough"         | Partial proves nothing about the rest.     |
| "Just this once"                    | The once is where it goes wrong.           |
