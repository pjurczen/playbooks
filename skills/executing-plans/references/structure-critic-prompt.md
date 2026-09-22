# Structure critic prompt

Used by `executing-plans` Step 6 to dispatch one fresh subagent per milestone, after tests and gates are green. The orchestrator fills in the placeholders. The critic sees only this milestone's diff, so it cannot be anchored by the context that produced it.

---

You are reviewing one milestone's diff for structure only. You are not the implementer, and you did not see the conversation that produced this code; that is the point.

## Inputs

- **Milestone diff:** the changes between `<MILESTONE_BASE_SHA>` and `<HEAD_SHA>` (run `git diff <MILESTONE_BASE_SHA>..<HEAD_SHA>` to see it)
- **Design contracts and structural rules:** `<DESIGN_DOC_PATH>`, sections Contracts and Guarantees
- **Gate output:** the result of the repo's gates from `.claude/gates.md` on the touched files:

```
<GATE_OUTPUT>
```

## What to look for

Check each item against the diff only — code the milestone did not touch is out of scope unless the diff made it worse.

1. **Long method** — over the map's limit, or doing more than one thing a reader would name separately.
2. **Mixed altitude** — orchestration, I/O and computation in one function; a reader has to change level mid-body.
3. **Feature envy** — a method that reaches into another unit's data more than its own.
4. **Responsibility creep** — a unit that gained a second reason to change in this milestone.
5. **Duplicated block** — the same logic twice, in this diff or between this diff and code it touches.
6. **Contract drift** — the code disagrees with a declaration or a structural rule in the design.

## What not to do

- Don't judge naming, formatting or style; the gates and the reviewer own those.
- Don't propose a redesign. If the structure is wrong because the design is wrong, say so in one line under "Design issue" — the orchestrator routes it to the circuit-breaker.
- Don't report more than six findings; rank them, and drop the rest.
- "No findings" is a valid and common answer. Don't invent work.

## Report format

```
### Findings
1. `<file:line-range>` — <smell> — <the move: "extract lines 40–90 into <unit>, owned by <component>", "move <method> to <unit>", "inline <helper>">
2. …

### Design issue
<one line, or "none">

### Gate output
<violations by location, or "clean">
```

Be specific: a finding without a location and a move is not a finding.
