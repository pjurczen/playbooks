---
name: debugging
description: Use when fixing a bug or investigating a failure, to find the root cause before changing code and pin the fix with a red-first regression test.
---

# Debugging

Root cause before fix. For any bug bigger than a typo: reproduce it, state the root-cause hypothesis and the evidence for it, and only then change code.

**Announce at start:** "Using debugging to find the root cause."

## When to skip

- **Typo-class fixes** — misspelled identifier, wrong constant, an off-by-one visible in the diff. Just fix it; still run **verifying-before-done**.
- **Failures in work you're implementing right now** — a red test mid-milestone is the normal loop of **executing-plans**, not a debugging session.

## The loop

1. **Reproduce.** Run the failing thing; capture the exact error output. Can't reproduce → gather more first (inputs, environment, version) — don't theorize about a failure you can't see.
2. **Locate.** Read the full error message — it usually names the answer. Trace the code path the evidence implicates.
3. **Hypothesize — with evidence.** State it explicitly: "Root cause: X. Evidence: Y." If you can't fill in both halves, keep investigating. Two candidate causes → find the experiment that discriminates between them.
4. **Confirm.** Run the cheapest check that proves or disproves the hypothesis (a log line, a debugger stop, a minimal input). Disproved → back to step 2. Don't stack a second guess on top of an unconfirmed first.
5. **Regression test (RED).** Write the behavioural test that fails *because of this bug*, per **bdd-testing**. Watch it fail with the original symptom.
6. **Fix (GREEN).** Smallest change that addresses the root cause — not the symptom, not the call site that happened to surface it.
7. **Verify.** Regression test passes, nearby suite stays green. **verifying-before-done** before claiming fixed.
8. **Commit** per **milestone-commits** — `fix:` type, body states the root cause.

## Escalation

If the confirmed root cause is a design problem (wrong boundary, missing abstraction, tangled responsibilities), don't patch around it in place. Route to **brainstorming** — that fix needs a design. If the user needs the symptom gone today, a workaround plus a `docs/followups.md` entry is acceptable — but say explicitly which of the two you're delivering.

## Red Flags — STOP

| Thought | Reality |
|---------|---------|
| "I'll just try changing this and see" | Guess-and-check is not debugging. State the hypothesis first. |
| "It's probably X, let me fix that" | "Probably" is a hypothesis without evidence. Confirm it. |
| "The error is obviously in this file" | Read the full error and trace the path. Obvious is often wrong. |
| "The error went away, so it's fixed" | Gone ≠ root-caused. Can you say *why* it happened? |
| "No time for a regression test" | The bug already cost more than the test will. |
| "Third fix attempt — this one should work" | Two failed fixes means you don't understand the cause. Back to evidence. |
