---
name: non-brittle-tests
description: Use whenever writing, extending or changing a test — for a new implementation, a bug fix or a refactoring safety net — and when reviewing or repairing tests, to produce tests that prove behaviour, survive refactoring and read like their behaviour sentence.
---

# Non-Brittle Tests

A test proves externally meaningful behaviour. It stays unchanged through a pure refactoring, an unrelated compatible feature, a bug fix elsewhere and an
internal redesign; it changes only when the behaviour it specifies changes. Treat test code as production code.

The rules are indexed below (IDs B, D, R, A). The full explanation and an Avoid/Prefer example for each rule are in `references/examples.md`; read them before
the first test of a task. Where a test goes (acceptance, unit, integration, architecture) is decided by the repository's instruction files and
`.claude/gates.md`, whether code deserves a test at all by **bdd-testing**. This skill decides how the test is built.

## Ground rules

- Never invent a business rule to make a test concrete. If the behaviour is ambiguous, check callers, docs, tickets and acceptance tests; name the open decision
  and test only the unambiguous part.
- Never weaken, delete, skip or rewrite a valid test to make a build pass.
- Never claim a test passes without running it.
- Read a few nearby tests for local idioms, but don't copy patterns that break these rules.

## Rules

| ID     | Rule                                                                                                 |
|--------|------------------------------------------------------------------------------------------------------|
| **B1** | Define the behaviour sentence (Given–When–Then) before the test shape; one behaviour per test.       |
| **B2** | Test through the owned public API, the way a real caller does.                                       |
| **B3** | Choose the smallest scope that still proves the behaviour; never mock the infrastructure under test. |
| **D1** | Prefer real collaborators: real → stub → fake → mock. Replace only awkward boundaries.               |
| **D2** | Stubs supply inputs only; never stub the logic under test.                                           |
| **D3** | Fakes honour the real contract and get a shared contract test.                                       |
| **D4** | Verify an interaction only when the interaction is the behaviour.                                    |
| **R1** | Behaviour names, one behaviour, Arrange–Act–Assert separated by blank lines.                         |
| **R2** | Every relevant value is a named variable, used to arrange and to expect.                             |
| **R3** | Build test objects with creation methods named after the situation.                                  |
| **R4** | Compose inputs from small named parts; about three parameters per helper.                            |
| **R5** | Action helpers hide arguments the behaviour ignores.                                                 |
| **R6** | Name stub, fake and setup steps after the situation they create.                                     |
| **R7** | No logic in tests; parameterize only rows of the same behaviour.                                     |
| **R8** | DAMP over premature DRY; keep inline what the test is about.                                         |
| **A1** | Assert behaviour, not representation.                                                                |
| **A2** | Assert only what the behaviour promises.                                                             |
| **A3** | Control time, randomness, I/O, shared state and order.                                               |

## Workflow for each test

1. **Behaviour (B1).** Write the sentence. Use ZOMBIES (Zero, One, Many, Boundaries, Interface, Exceptional, Simple) to pick the cases that protect real
   distinctions.
2. **Surface and scope (B2, B3).** Pick the entry point a real caller uses and the smallest scope that proves it.
3. **Collaborators (D1–D4).** Real first; justify every double.
4. **Write it (R1–R8).** Shape the body like the sentence: named values, situation-named creation and action helpers, no logic.
5. **Assert (A1–A3).** Only the promised, observable outcome, in a controlled environment.
6. **Run and diagnose.** Narrowest test first, then the broader suite. Classify a failure before touching the test: intended red, production defect, brittle
   test, nondeterminism, environment, pre-existing. If a run is blocked, report the command, the category, the error and what did or didn't run.
7. **Review.** Go through *Done when* and fix what fails.

## By situation

- **New implementation.** Small red–green–refactor cycles: the smallest test for one missing behaviour, watch it fail for the expected reason, the smallest
  production change, refactor test and code while green, run the suite, next behaviour. No batches of speculative tests.
- **Bug fix.** A regression test that fails because of the bug, then the fix (**debugging**).
- **Refactoring safety net.** Characterization tests per **bdd-testing**, through the public method, asserting observable results; commit them before the
  refactoring (**refactoring**). A test that breaks during a behaviour-preserving refactoring is brittle: raise its abstraction (B2, D4), don't bend the code to
  it.
- **Improving existing tests.** Find the behaviour each test protects, then: public entry points instead of private calls (B2), state instead of interactions
  (D4), real objects or fakes instead of needless mocks (D1, D3), stubs reduced to inputs (D2), one behaviour per test ( R1), relevant values into the body
  (R2), creation and action helpers (R3–R6), logic removed (R7), nondeterminism controlled (A3). Run after each small step; keep the coverage, shorter is not
  the goal.
- **Reviewing.** Classify findings by consequence:
    - *Must fix:* doesn't prove the claimed behaviour; internal detail is the test surface; interaction checks that fail equivalent implementations; expected
      value duplicates production logic; uncontrolled time, randomness, network or shared state; a silenced, skipped or weakened failure; a fake that breaks its
      contract; an invented business rule.
    - *Should fix:* several behaviours in one test; hidden assertion-relevant setup; vague name; needless doubles; over-assertion; helpers that obscure intent;
      repeated builder chains, long argument lists or literals repeated in arrange and assert; a fidelity-sensitive fake without contract test.
    - *Consider:* harmless DAMP duplication, local naming, parameterization that improves diagnosis. Never recommend an abstraction only to cut lines.

## Done when

Every new or changed test passes all of these:

- [ ] **Four-change check:** unchanged after a pure refactoring, an unrelated feature, a bug fix elsewhere and an equivalent algorithm.
- [ ] Invoked like a real caller; no private methods or internal representation (B2).
- [ ] Outcome asserted on output or observable state; every `verify` is the behaviour itself (D4, A1).
- [ ] Real collaborators where possible; every stub needed; fakes contract-tested (D1–D3).
- [ ] Name states action and outcome; one behaviour; readable without opening helpers (R1).
- [ ] Relevant values are named variables used in arrange and assert; objects come from situation-named creation methods; the act line shows only relevant
  arguments (R2–R6).
- [ ] No logic in the test (R7); assertions limited to the promise (A2); time, randomness, I/O and order controlled ( A3).
- [ ] The tests ran: green, or red for the intended reason.

## Red flags

| Thought                                                                  | Reality                                                        |
|--------------------------------------------------------------------------|----------------------------------------------------------------|
| "I'll mock it, that's simpler."                                          | Simpler to write, not to trust. Real collaborators first (D1). |
| "`verify` proves it was called."                                         | Called is not correct. Assert the outcome (D4).                |
| "A helper with six parameters is fine."                                  | Compose small named parts (R4).                                |
| "The literal in the assert is obvious."                                  | Name it once, use it twice (R2).                               |
| "The test broke in the refactoring; I'll adapt it to the new internals." | It was brittle. Raise its abstraction (B2).                    |
| "It's flaky, add a retry."                                               | Find the uncontrolled input (A3).                              |

## Completion report

Report briefly: the behaviours added, changed or reviewed; the observation surface; the doubles chosen and why; the commands run and their results; what remains
unverified; and any production design issue that made a behaviour hard to test.

## Sources

Marco Consolaro, Alessandro di Gioia: *Agile Technical Practices Distilled*; *Software Engineering at Google* (Testing Overview, Unit Testing, Test Doubles,
Larger Testing); Robert C. Martin: *Clean Craftsmanship*. Engineering guidance, not a substitute for the repository's business requirements.
