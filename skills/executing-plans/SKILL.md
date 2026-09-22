---
name: executing-plans
description: Use after writing-plans, with an approved plan in hand, to implement the feature milestone by milestone in the main session.
---

# Executing Plans

Implement the plan in the main session, milestone by milestone; subagents only where this skill names one.

## Before you start

1. Read the plan file once. Extract: the goal, the changes and call-site tables, the behaviours to verify, the full list of milestones with their done-when
   criteria. Read the design it links for the contracts and guarantees, and `references/structure-critic-prompt.md` once: its four levels are the words the
   plan's altitude clauses use, and the critic holds your code to its checklist.
2. Re-read it critically. Any milestone unclear? Any missing dependency? Any behaviour you can't see how to verify? Raise it with the user before any code is
   written. The plan's *Stop and ask if* list stays binding throughout: when a condition hits mid-milestone, stop and ask — don't pick an interpretation and
   build on it.
3. Confirm the workspace chosen during brainstorming (branch, path, `BASE_SHA` from the using-git-worktrees report). Invoke **using-git-worktrees** only if
   there is none yet — the user brought their own plan.
4. One TODO per milestone.

## Resuming a partially executed plan

After a clear or compaction mid-feature: find the existing branch or worktree (`git worktree list`, `git branch --list`) — never re-run using-git-worktrees when
one exists. Compare the plan's milestones against `git log <BASE_SHA>..HEAD` for the first incomplete one, rebuild what you can of `## Findings` from the commit
messages, note it's partial, continue.

## Clean code defaults

"Smallest thing that passes" means smallest *that sits where the plan put it*: each function at the one level the plan names for it, a rule in the unit that
owns its data, translation in the adapter, no abstraction without a second caller. The critic holds the diff to the same checklist after green.

## The milestone loop

For each milestone, run these steps in order, then repeat for the next milestone; after the last one, the end-of-feature review, promotion of findings, and the
hand-off to finishing-branch.

### Step 1 — Sketch behavioural test(s) (RED)

Use **bdd-testing**: one test per behaviour the milestone adds, behaviour-level, not structural.

### Step 2 — Watch them fail

Run it. It must fail because the behaviour is missing, not from a typo or an import. A test that passes immediately tests existing behaviour — fix it.

### Step 3 — Implement smallest thing (GREEN)

Write the smallest code that makes the test pass, at the level and in the unit the plan names. No "while I'm here" features.

### Step 4 — Run tests + nearby smoke

Run the milestone tests, a quick smoke of nearby behaviour, and the gates from `.claude/gates.md` on the touched files. All green — tests and structure.

### Step 5 — Self-checkpoint

Re-read the milestone goal. Look at the diff for *only this milestone*. Answer:

- **Did I meet the goal?** Each done-when criterion?
- **Did I leave anything broken?** Any test elsewhere this change might have affected?
- **Anything surprising worth noting?** Discovered helper, unexpected coupling, sharp edge?

If something's off: fix in place before continuing. If the code had to differ from the design's Contracts or Design: edit the design so it stays true and add
one `Deviation:` line under its Approach — the end-of-feature reviewer compares against the design as written. If something's a note for later: add it to your
in-session `## Findings` block (see "Findings" below).

"Added X but didn't wire the call sites the plan named" is incomplete milestone work, not a finding — fix it now.

### Step 6 — Structure critic

Dispatch ONE fresh subagent with `references/structure-critic-prompt.md`: this milestone's diff, the design's Contracts with their structural rules, the gate
output. It returns at most six findings by location with the move, or "none"; a "design issue" goes to the circuit-breaker. The model that wrote the long method
doesn't see it in the same context; a fresh one with a checklist does.

### Step 7 — Refactor pass

Apply the critic's findings first, then the boy scout rule: leave the code you touched — same file, the functions above and below, the helpers you called,
immediate callers, and anything your change made worse or exposed — better than you found it. The scope is what you touched; the effort is whatever that scope
needs, not a time-box. Allowed: rename, extract, collapse duplication, remove dead code, simplify a conditional, split the long function you had to modify, move
a responsibility to the unit that owns it. Not allowed: cleaning code you didn't touch, and changing a contract other code depends on — that is a stop-and-ask,
never a quiet refactor and never a followup. A bug in touched code is fixed here, with a scenario, and named in the commit; a bug elsewhere is a finding. Tests
stay green throughout. "Looked, nothing worth doing" is a valid answer; "too big for now" is not — if you touched it, it's yours.

### Step 8 — Run tests and gates again

Tests and gates again; the refactor changed nothing observable and introduced no violation. **verifying-before-done** before claiming the milestone complete.

### Step 9 — One milestone commit

Invoke **milestone-commits**: one commit for the whole milestone, feature and refactor. Milestone titles are scaffolding for you, not commit subjects; describe
the outcome.

### Repeat for each milestone.

## Circuit-breaker: the design might be wrong

The milestone loop assumes the design is sound and your job is to build it. On a hard problem that assumption can fail *mid-build* — and every local instinct
here (fix-in-place, boy-scout, defer to followups) will quietly push you to **patch around a broken design** instead of stopping. Watch for the tremors:

- You're adding a **compensating patch** — a mutator / guard / coercion whose only job is to force the design to behave — **especially the second one.** One is
  a fix; a pile is a smell.
- The **plan's contract or interface has churned** — you've revised the same seam two or three times.
- You're **fighting the plan** — each milestone needs more scaffolding than the last to hold together.

These mean *the design is wrong*, not *this milestone is hard*. **STOP — do not keep patching.** Surface what you've learned and re-open brainstorming for the
affected seam (for a slice, possibly the initiative's; a `proposed` ADR is revised there, in place). The tremors show long before the end-of-feature review,
which is too late to unwind a wrong abstraction.

## Findings: Tier 1 (in-session) and Tier 2 (followups.md)

**Tier 1 — in-session.** A running `## Findings` block in the conversation with three subsections: **Changes** (per milestone), **Gotchas** (what later
milestones should know), **Open questions**. It is input to the end-of-feature reviewer.

**Tier 2 — durable followups** at `docs/followups.md`, append-only: only items that would need their own design / plan — architectural refactorings,
generalizations, structural changes — in code this feature did not touch. Cleanliness debt on touched code never goes here; it is in scope now. Format:

````markdown
## YYYY-MM-DD — short title

One-line description. File: src/path/file.py:line. Discovered while: feature-name.
````

## End-of-feature review

After the last milestone commits, run a single review pass before `finishing-branch`:

1. Dispatch ONE reviewer subagent with the companion prompt `references/end-of-feature-reviewer-prompt.md`, giving it the design, the plan, the feature diff
   (`BASE_SHA..HEAD`, from the using-git-worktrees report) and the `## Findings` block.
2. It returns Strengths / Issues (Critical / Important / Minor / Followup) / Assessment. Fix Critical, Important and Minor; only Followup-tier items go to
   `followups.md`.
3. Commit the fixes as one milestone (same loop). One pass, fix, move on — wanting a re-review means a milestone was wrong.

## Promotion: Tier 1 → Tier 2

After the review fixes: drop what the work addressed, promote only Tier-2 items per the definition above, fix or drop the rest in a small follow-up commit, and
commit the followups update.

## Hand off

Invoke **finishing-branch** to complete the work.

## Subagents during execution

Standing dispatches: the structure critic per milestone (Step 6) and the end-of-feature reviewer. Beyond those, default: don't — only for 2+ genuinely
independent investigations (**using-parallel-agents**, which also defines the `## Findings` block every subagent returns) or a context-heavy subtask whose
findings, not its noise, you need. Store findings inline before the next milestone.

## Red Flags — STOP

| Thought                                            | Reality                                                                                                                    |
|----------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| "I'll skip the test, this case is obvious"         | Then the test takes 30 seconds. Write it.                                                                                  |
| "I'll commit the feature now and refactor later"   | The refactor is part of the milestone commit. Do it now.                                                                   |
| "It's pre-existing, my change didn't introduce it" | If you touched it, it's yours. Followups are for code you didn't touch.                                                    |
| "I'll just add one more guard to make it behave"   | Compensating patches accrete into a broken design. The second one means STOP and re-open the design (see Circuit-breaker). |
