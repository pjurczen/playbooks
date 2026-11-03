---
name: refactoring
description: Use when asked to refactor, clean up or improve the design of existing code, to run the refactoring loop (safety net, Composed Method, move methods, hidden concepts) until a full pass changes nothing and the exit criteria hold.
---

# Refactoring

Improve the design of existing code without changing its behaviour, in passes, until nothing is left to improve. The rules are the catalogue in
`references/examples.md` (rule IDs M1–T9), with the explanation and a full Avoid/Prefer example for each rule; read it before the first pass. This skill is the
order in which to apply them and the point at which you are done. Where rules pull in different directions, the rule order decides (move before naming). Do not
stop after one pass: a pass that changed something is followed by another.

## Before the first pass

1. **Scope.** List the public methods in scope (the ones named by the user, plus the private methods they call). Write them as a checklist into
   `docs/playbooks/plans/YYYY-MM-DD-refactoring-<class>.md`, one line per method with the columns *composed*, *moved*, *concepts*, *tests*. This file is how a
   later run continues after a stop. Skip the file when the scope is three methods or fewer; track them in the session instead.
2. **Safety net.** Invoke the **non-brittle-tests** skill before writing or changing any test, including extending existing ones. For every method in scope,
   check that tests cover its branches. If not, write characterization tests first (**bdd-testing** › Characterization tests). Commit the tests on their own.
3. **Fast test loop.** Use the test command from `.claude/gates.md`, narrowed to the module; run tests once per pass, not per edit.

## One pass

Work through the checklist in this order; one rule at a time, smallest step first.

1. **Compose (M1, M2).** Each public method reads like a news article: a few named steps, each a domain concept that returns at most one result for the next
   step. Group lines that belong together into a private method named after that concept. Name every new or extracted method per the repository's code style for
   names; renaming existing public methods is out of scope.
2. **Clean the steps (M3–M8, C1–C5, S1–S6).** Apply the method-level rules inside every extracted method. Move every declaration next to its first use, into the
   branch that needs it (M7). Inline every method that only forwards to one call, including wrappers that existed before and those that became pass-throughs
   after an extraction (M8). Naming creates new low-level lines: check the result against step 1 again before moving on. Variables that only build one value
   below the level of the rest are a hidden step (M3).
3. **Move (T2, T8, T9, Emerging Design).** Check every touched line, not only private methods — public and static methods, creation methods, lambdas and
   explaining variables included, also code you just wrote in this pass:
    - For every private method: which state does it really use? If that is mainly one parameter's type, move it there as public; if no type holds that state
      yet, wrap it (T1) and move the method in.
    - For every collection that is queried (filtered, searched, counted, checked for emptiness, first element), as parameter, local variable or field: wrap it
      in a first-class collection named after the type it wraps, or reuse the existing one, and move the query in as a method named after its intention (T9).
      The same holds for a collection that crosses a port or public method as a domain concept, even if nobody queries it.
    - **Search before you write a query or a conversion (mandatory).** For every collection element type you touch, search the module for an existing
      first-class collection of that type (a class whose only field is a list or set of it) and add the method there instead of in the caller. For every
      conversion you write or move, search the module, not only the scope, for other copies of it and replace them with one creation method (T3). Record both
      searches and their findings in the checklist.
    - For every call on the result of another call (`a.b().c()`, outside fluent pipelines): if you own the type, add a query or command on the nearest object
      named after the concept (`a.c()`), delegating one level per type, and call that instead. If you cannot change the type, assign the reached value to an
      explaining variable named after the concept (T8).

   Factories create, domain objects decide, services orchestrate I/O. Never cross a layer boundary. Before adding a getter-style query to a type that a mapper
   or serializer reflects over, check that no mapping target has a property of that name.
4. **Find hidden concepts (T1, T3).** Methods sharing the same parameters → a private record named after the concept, with the behaviour that uses those values.
   Callers assembling the same factory arguments → one creation method per purpose. Before creating a creation method, search the module for copies of the same
   conversion, also outside the scope, and replace them.
5. **Verify and record.** Run the tests and the gates (`.claude/gates.md`). Tick the checklist, commit the pass with **milestone-commits**.

Then start the next pass. A refactoring step that would change a public contract outside the class (another module's API, an endpoint signature) is
stop-and-ask, never a silent change.

## Done when

A full pass changes nothing, and all of these hold for every method in scope:

- [ ] Every public method is a short sequence of named steps on one level of abstraction.
- [ ] No private method works mainly on another type's data (it would have moved in step 3).
- [ ] No method only forwards to one other call (M8).
- [ ] No touched line calls a method on the result of another call (`a.b().c()`) outside fluent pipelines; owned types answer themselves, foreign DTOs go
  through a named variable (T8).
- [ ] No parameter set or argument assembly repeats across methods.
- [ ] No touched method queries a raw collection; queried collections and collections that cross a port as a concept are first-class collections (T9).
- [ ] The searches for existing collection wrappers and for copies of each conversion are recorded in the checklist, and every hit was used or replaced.
- [ ] The structural gates report nothing (length, complexity, nesting, parameters, boolean parameters).
- [ ] A fresh structure critic (`${CLAUDE_PLUGIN_ROOT}/references/structure-critic-prompt.md`) finds no M/C/S/T violation in the touched methods.
- [ ] The tests are green, and every behaviour that had a test before still has one.
- [ ] All new or changed tests follow **non-brittle-tests** (observable results, no stubbed logic under test).

Only then report the refactoring as complete (**verifying-before-done**). If you must stop earlier (budget, timeout, user), leave the checklist file and the
last commit consistent and say which pass and method is next.

## Red flags — keep going

| Thought | Reality |
|---|---|
| "The method is shorter now, good enough." | Shorter isn't composed. Run steps 3 and 4. |
| "These private methods are fine in the service." | Check each: which data does it use? |
| "The wrapper has a nice name / a decorator." | A forward is not a concept; a decorator that only works through the framework doesn't run on a private method (M8). |
| "It's a public creation method, step 3 doesn't apply." | Step 3 covers every touched line, also code written this pass. |
| "I'll name the chain with an explaining variable." | Only for types you can't change. If you own it, let the nearest object answer (T8). |
| "The move made this variable unnecessary." | Moves don't remove names M3 still needs; check the argument list again. |
| "Every value has its own variable now." | Variables that only build one value below the level of the rest are a hidden step: a query named after the value (M1) or a creation method on its type (T3); the receiver keeps its domain-type parameter. |
| "This private method is already a step." | If several of its lines only build one value for the rest, that is a step inside the step (M3). A single read-and-convert pair may stay. |
| "The domain already uses other verbs, I'll match them." | New names follow the repository's code style. |
| "`.value` is just unwrapping." | Only in adapters and mappers; elsewhere overload the callee for the tiny type (T8). |
| "The gate violation was there before." | A touched method must pass the gates, its signature included. |
| "Same three parameters again, but it works." | That is a missing concept (T1). |
| "It's just a `list`, there is no type to move the query to." | A queried collection is a missing type: wrap it and move the query in (T9). |
| "The list is only passed on to the gateway." | If it crosses a port as a domain concept, it is a first-class collection too (T9). |
| "The conversion only appears in my class." | Search the module first; copies outside the scope are the usual case (T3). |
| "Tests are slow, I'll run them at the end." | Once per pass, with the fast loop. |
