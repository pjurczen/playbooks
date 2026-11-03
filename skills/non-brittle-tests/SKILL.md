---
name: non-brittle-tests
description: Use when writing, changing or reviewing a test, to build one that proves behaviour through the caller's surface, survives refactoring and reads like its sentence.
---

# Non-Brittle Tests

A test proves externally meaningful behaviour. It changes only when the behaviour it specifies changes. Treat test code as production code.

**bdd-testing** decides whether code deserves a test and what the test says. The repository's instruction files and `.claude/gates.md` decide where a test
lives. This skill decides how the test is built. Read `references/examples.md` before the first test of a task.

<HARD-GATE>
A test is finished only when it would stay unchanged through a pure refactoring, an unrelated feature, a bug fix elsewhere and an equivalent algorithm. A test
that fails on any of these guards the implementation, not the behaviour, and every later change pays for it.
</HARD-GATE>

Fired by executing-plans step 1, debugging step 5 and the safety net of refactoring. Invoke it directly when the user asks for a test, or asks to review or
repair one.

## When to skip

- Code without interesting behaviour. bdd-testing says no test.
- An expected value that changed because the behaviour changed on purpose. Update the value.

## Ground rules

- Never invent a business rule to make a test concrete. If the behaviour is ambiguous, check callers, docs, tickets and acceptance tests. Name the open decision
  and test only the unambiguous part.
- Never weaken, delete, skip or rewrite a valid test to make a build pass.
- Read a few nearby tests for local idioms, but do not copy patterns that break these rules.

## Rules

| ID     | Rule                                                                                                |
|--------|-----------------------------------------------------------------------------------------------------|
| **B1** | Test through the owned public API, the way a real caller does.                                      |
| **B2** | Choose the smallest scope that still proves the behaviour. Never mock the infrastructure under test. |
| **D1** | Stubs supply inputs only. Never stub the logic under test.                                          |
| **D2** | Fakes honour the real contract and get a shared contract test.                                      |
| **R1** | One behaviour per test, Arrange–Act–Assert separated by blank lines.                                |
| **R2** | Every relevant value is a named variable, used to arrange and to expect.                            |
| **R3** | Build test objects with creation methods named after the situation.                                 |
| **R4** | Compose inputs from small named parts, about three parameters per helper.                           |
| **R5** | Action helpers hide the arguments the behaviour ignores.                                            |
| **R6** | Name stub, fake and setup steps after the situation they create.                                    |
| **R7** | No logic in tests. Parameterize only rows of the same behaviour.                                    |
| **R8** | DAMP over premature DRY. Keep inline what the test is about.                                        |
| **A1** | Assert behaviour, not representation.                                                               |
| **A2** | Assert only what the behaviour promises.                                                            |
| **A3** | Control time, randomness, I/O, shared state and order.                                              |

## For each test

1. **Sentence.** bdd-testing gives it. Use ZOMBIES (Zero, One, Many, Boundaries, Interface, Exceptional, Simple) to pick the cases that protect real
   distinctions.
2. **Surface and scope (B1, B2).** The entry point a real caller uses, and the smallest scope that proves it.
3. **Collaborators (D1, D2).** Real first, as bdd-testing says. Justify every double.
4. **Write it (R1–R8).** Shape the body like the sentence: named values, situation-named creation and action helpers, no logic.
5. **Assert (A1–A3).** Only the promised, observable outcome, in a controlled environment.
6. **Run and diagnose.** Narrowest test first, then the broader suite. Classify a failure before you touch the test: intended red, production defect, brittle
   test, nondeterminism, environment, pre-existing. If a run is blocked, report the command, the category, the error and what did or did not run.
7. **Review.** Go through "Done when" and fix what fails.

## By situation

- **Refactoring safety net.** Characterization tests per bdd-testing, through the public method, asserting observable results. Commit them before the
  refactoring. A test that breaks during a behaviour-preserving refactoring is brittle: raise its abstraction (B1). Do not bend the code to it.
- **Improving existing tests.** Find the behaviour each test protects, then: public entry points instead of private calls (B1), state instead of interactions
  (A1), real objects or fakes instead of needless mocks (D2), stubs reduced to inputs (D1), one behaviour per test (R1), relevant values into the body (R2),
  creation and action helpers (R3–R6), logic removed (R7), nondeterminism controlled (A3). Run after each small step. Keep the coverage. Shorter is not the
  goal.
- **Reviewing.** Classify findings by consequence:
  - *Must fix:* does not prove the claimed behaviour; an internal detail is the test surface; interaction checks that fail equivalent implementations; an
    expected value that duplicates production logic; uncontrolled time, randomness, network or shared state; a silenced, skipped or weakened failure; a fake
    that breaks its contract; an invented business rule.
  - *Should fix:* several behaviours in one test; hidden assertion-relevant setup; a vague name; needless doubles; over-assertion; helpers that obscure intent;
    repeated builder chains, long argument lists or literals repeated in arrange and assert; a fidelity-sensitive fake without a contract test.
  - *Consider:* harmless DAMP duplication, local naming, parameterization that improves diagnosis. Never recommend an abstraction only to cut lines.

## Done when

Every new or changed test passes all of these:

- Invoked like a real caller, no private methods or internal representation (B1).
- Outcome asserted on output or observable state (A1).
- Every stub needed, every fake contract-tested (D1, D2).
- The name states action and outcome, one behaviour, readable without opening helpers (R1).
- Relevant values are named variables used in arrange and assert, objects come from situation-named creation methods, the act line shows only relevant arguments
  (R2–R6).
- No logic in the test (R7), assertions limited to the promise (A2), time, randomness, I/O and order controlled (A3).
- A flaky test gets its uncontrolled input found, never a retry (A3).

Then **verifying-before-done**.
