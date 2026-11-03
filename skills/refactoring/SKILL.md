---
name: refactoring
description: Use when asked to refactor, clean up or improve the design of code the user names, to run the pass loop under a safety net until a full pass changes nothing.
---

# Refactoring

Improve the design of existing code without changing its behaviour, in passes, until nothing is left to improve. The structure rules are the structure critic's
checklist (`${CLAUDE_PLUGIN_ROOT}/references/structure-critic-prompt.md`) and the repository's instruction files. This skill is the order in which to apply them
and the point at which you are done. Read `references/examples.md` before the first pass. A pass that changed something is followed by another.

<HARD-GATE>
No refactoring step before every method in scope has tests that fail when its behaviour changes, committed on their own. **non-brittle-tests** builds them.
Refactoring is behaviour-preserving by definition. Without a net, "preserved" is a belief.
</HARD-GATE>

## When to skip

- Cleanup of code a milestone touched. executing-plans step 7 owns that.
- Code the user did not name.
- A change to a public contract outside the scope (another module's API, an endpoint signature). That is a feature: brainstorming.

## Before the first pass

1. **Scope.** List the public methods in scope: the ones the user named, plus the private methods they call. With more than three methods, write them as a
   checklist into `docs/playbooks/plans/YYYY-MM-DD-refactoring-<unit>.md`, one line per method with the columns *composed*, *moved*, *concepts*, *tests*. This
   file is how a later run continues after a stop.
2. **Safety net.** For every method in scope, check that tests cover its branches. If not, write characterization tests first and commit them on their own.
3. **Fast test loop.** Use the test command from `.claude/gates.md`, narrowed to the module. Run tests once per pass, not per edit.

## One pass

Work through the checklist in this order, one rule at a time, smallest step first. Move before naming.

1. **Compose.** Each public method reads like a news article: a few named steps, each a domain concept that returns at most one result for the next step. Group
   the lines that belong together into a private method named after that concept. Name every new method in the vocabulary the repository's instruction files
   prescribe. Renaming existing public methods is out of scope.
2. **Clean the steps.** Apply the method-level rules inside every extracted method. Move every declaration next to its first use, into the branch that needs it.
   Inline every method that only forwards to one call, including wrappers that existed before and those that became pass-throughs after an extraction. A
   decorator that does not run on a private method is no reason to keep a wrapper. Naming creates new low-level lines: check the result against step 1 again.
   Variables that only build one value below the level of the rest are a hidden step.
3. **Move.** Check every touched line, not only private methods: public and static methods, creation methods, lambdas and explaining variables, also code you
   wrote in this pass.
   - For every private method: which state does it really use? If that is mainly one parameter's type, move it there as public. If no type holds that state yet,
     wrap it and move the method in.
   - For every collection that is filtered, searched, counted or asked for its first element, as parameter, local or field: wrap it in a first-class collection
     named after what it holds, or reuse the existing one, and move the query in as a method named after its intention. The same holds for a collection that
     crosses a port or a public method as a domain concept, even if nobody queries it.
   - **Search before you write a query or a conversion.** For every element type you touch, search the module for an existing first-class collection of that
     type and add the method there. For every conversion you write or move, search the module, not only the scope, for other copies and replace them with one
     creation method. Record both searches and their findings in the checklist.
   - For every call on the result of another call (`a.b().c()`, outside fluent pipelines): if you own the type, add a query or a command on the nearest object
     named after the concept (`a.c()`), delegating one level per type. If you cannot change the type, assign the reached value to an explaining variable named
     after the concept. Unwrap a tiny value only in adapters.

   Factories create, domain objects decide, services orchestrate I/O. Never cross a layer boundary. Before adding a query to a type that a mapper or a
   serializer reflects over, check that the name does not become a mapped property.
4. **Find hidden concepts.** Methods sharing the same parameters → a small value type named after the concept, with the behaviour that uses those values.
   Callers assembling the same factory arguments → one creation method per purpose, after the search in step 3.
5. **Verify and record.** Run the tests and the gates. Tick the checklist. Commit the pass with **milestone-commits**.

Then start the next pass.

## Done when

A full pass changes nothing, and all of these hold for every method in scope:

- Every public method is a short sequence of named steps on one level of abstraction.
- No private method works mainly on another type's data.
- No method only forwards to one other call.
- No touched line calls a method on the result of another call outside fluent pipelines. Owned types answer themselves, foreign data goes through a named
  variable.
- No parameter set or argument assembly repeats across methods.
- No touched method queries a raw collection.
- The searches for existing collection wrappers and for copies of each conversion are recorded, and every hit was used or replaced.
- The gates report nothing on the touched methods, pre-existing violations included.
- A fresh structure critic, fed the pass's diff and the gate output, returns no findings.
- The tests are green, every behaviour that had a test before still has one, and every new or changed test follows **non-brittle-tests**.

Then **verifying-before-done**. If you must stop earlier, leave the checklist file and the last commit consistent and say which pass and method is next.
