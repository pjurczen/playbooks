---
name: verifying-before-done
description: Use before claiming work is complete, fixed, or passing, and before commits or PRs, to confirm success with fresh verification evidence rather than assumption.
---

# Verifying Before Done

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does the output confirm the claim?
   - If NO: state actual status with evidence
   - If YES: state claim WITH evidence
5. ONLY THEN: make the claim

Skip any step = lying, not verifying.
```

## Common failures

| Claim | Requires | Not sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Subagent completed | VCS diff shows changes | Subagent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags — STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!")
- About to commit / push / open a PR without verification
- Trusting subagent success reports without checking the diff
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **Any wording implying success without having run the verification in this message**

## Rationalization prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | Run the verification. |
| "I'm confident" | Confidence ≠ evidence. |
| "Just this once" | No exceptions. |
| "Linter passed" | Linter ≠ compiler ≠ tests. |
| "Subagent said success" | Verify independently. |
| "I'm tired" | Exhaustion ≠ excuse. |
| "Partial check is enough" | Partial proves nothing. |
| "Different words, rule doesn't apply" | Spirit over letter. |

## Patterns

**Tests:**
```
✅ [Run test command] → [See: 34/34 pass] → "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (red-green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] → [See: exit 0] → "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read requirements → checklist → verify each → report gaps or completion
❌ "Tests pass, milestone complete"
```

**Subagent delegation:**
```
✅ Subagent reports success → check VCS diff → verify changes → report actual state
❌ Trust the subagent report
```

## When to apply

ALWAYS, before:
- Any variation of success / completion claims
- Any expression of satisfaction
- Any positive statement about work state
- Committing, pushing, opening a PR
- Closing a milestone or marking work done in a TODO list
- Handing back to the user with a "should be working" message

The rule applies to:
- Exact phrases ("done", "fixed", "passing")
- Paraphrases and synonyms ("looks good", "should be working")
- Implications of success
- Any communication suggesting completion or correctness

## The bottom line

Run the command. Read the output. THEN claim the result.

This is non-negotiable.
