---
name: executing-plans
description: Use after writing-plans, with an approved plan in hand, to implement the feature milestone by milestone in the main session.
---

# Executing Plans

Implement the plan in the main session, milestone by milestone. Default execution mode is the main session and main model — not subagents. Subagents are for genuinely parallel or context-heavy subtasks (see **using-parallel-agents**).

## Before you start

1. Read the plan file once. Extract: the goal, the changes and call-site tables, the behaviours to verify, the full list of milestones with their done-when criteria. Read the design it links for the contracts and guarantees.
2. Re-read it critically. Any milestone unclear? Any missing dependency? Any behaviour you can't see how to verify? Raise it with the user before any code is written. The plan's *Stop and ask if* list stays binding throughout: when a condition hits mid-milestone, stop and ask — don't pick an interpretation and build on it.
3. Confirm the workspace chosen during brainstorming (branch, path, and the recorded `BASE_SHA` from the using-git-worktrees report). Invoke **using-git-worktrees** now only if there is no workspace yet — e.g. the user brought their own plan and skipped the earlier pipeline stages.
4. Create one TODO entry per milestone for tracking.

## Resuming a partially executed plan

If the session was cleared or compacted mid-feature: locate the existing branch/worktree (`git worktree list`, `git branch --list`) — do **not** re-run using-git-worktrees when the workspace already exists. Compare the plan's milestones against `git log <BASE_SHA>..HEAD` to find the first incomplete one. Reconstruct what you can of the `## Findings` block from the milestone commit messages, note that it's partial, and continue the loop from there.

## Clean code defaults

"Smallest thing that passes" means smallest *that respects* single responsibility, small functions, descriptive names, no dead or commented-out code, and no premature abstraction (three near-identical pieces → extract; two → leave). These shape the GREEN step as you write; the refactor pass is where you enforce them deliberately. A sprawling 200-line glue function is not the smallest thing, it's the laziest.

## The milestone loop

For each milestone, run these steps in order, then repeat for the next milestone; after the last one, the end-of-feature review, promotion of findings, and the hand-off to finishing-branch.

### Step 1 — Sketch behavioural test(s) (RED)

Use **bdd-testing** to write the behavioural test for the milestone. One test per behaviour the milestone is supposed to add. Behaviour-level, not structural.

### Step 2 — Watch them fail

Run the test. Confirm it fails for the right reason — the behaviour isn't implemented yet, not because of a typo or a missing import. If the test passes immediately, you're testing existing behaviour — fix the test.

### Step 3 — Implement smallest thing (GREEN)

Write the smallest code that makes the test pass. No premature abstraction. No "while I'm here" features.

### Step 4 — Run tests + nearby smoke

Run the milestone tests + a quick smoke of nearby behaviour. All must pass.

### Step 5 — Self-checkpoint

Re-read the milestone goal from the plan. Look at the diff for *only this milestone*. Answer:
- **Did I meet the goal?** Each done-when criterion?
- **Did I leave anything broken?** Any test elsewhere this change might have affected?
- **Anything surprising worth noting?** Discovered helper, unexpected coupling, sharp edge?

If something's off: fix in place before continuing.
If the code had to differ from the design's Contracts or Shape: edit the design so it stays true and add one `Deviation:` line under its Approach — the end-of-feature reviewer compares against the design as written.
If something's a note for later: add it to your in-session `## Findings` block (see "Findings" below).

"Added X but didn't wire it up at the call sites the plan named" is incomplete milestone work, not a finding — fix it now.

### Step 6 — Refactor pass

Boy scout rule: leave the neighbourhood you touched — same file, the functions above and below, the helpers you called, immediate callers — better than you found it. Time-box ~5–10 minutes; anything bigger becomes a finding (`## Findings → Open questions`). Allowed: rename, extract a small helper, collapse obvious duplication, remove dead code, simplify a conditional. Not allowed: redesign interfaces, restructure modules, sweeping pattern "improvements" — those need a milestone. Tests stay green throughout; a bug found here is a finding, not a silent fix. "Looked, nothing worth doing" is a valid answer.

### Step 7 — Run tests again

Verify the refactor didn't break anything. Use **verifying-before-done** before claiming the milestone is complete.

### Step 8 — One milestone commit

Invoke **milestone-commits**, then write one commit for the entire milestone (feature + refactor). The plan's milestone titles and identifiers are reasoning scaffolding for *you* — they do not belong in the commit subject. Describe the outcome with a Conventional Commits type.

### Repeat for each milestone.

## Circuit-breaker: the design might be wrong

The milestone loop assumes the design is sound and your job is to build it. On a hard problem that assumption can fail *mid-build* — and every local instinct here (fix-in-place, boy-scout, defer to followups) will quietly push you to **patch around a broken design** instead of stopping. Watch for the tremors:

- You're adding a **compensating patch** — a mutator / guard / coercion whose only job is to force the design to behave — **especially the second one.** One is a fix; a pile is a smell.
- The **plan's contract or interface has churned** — you've revised the same seam two or three times.
- You're **fighting the plan** — each milestone needs more scaffolding than the last to hold together.

These mean *the design is wrong*, not *this milestone is hard*. **STOP — do not keep patching.** Surface what you've learned to the user and go back to the design (re-open brainstorming for the affected seam; if a `proposed` ADR exists, it is revised there, in place — never a second ADR). Ten accreted patches shipped as "done" is the failure this catches, and the tremors are visible long before the end-of-feature review — which is far too late to unwind a wrong abstraction.

## Findings: Tier 1 (in-session) and Tier 2 (followups.md)

**Tier 1 — in-session.** A running `## Findings` block in the conversation with three subsections: **Changes** (per milestone), **Gotchas** (what later milestones should know), **Open questions** (deferred refactors, design questions). It is input to the end-of-feature reviewer.

**Tier 2 — durable followups** at `docs/followups.md`, append-only: only items that would need their own design / plan — architectural refactorings, generalizations, structural changes. Anything fixable in a boy-scout pass is in scope now; don't promote it. Format:

````markdown
## YYYY-MM-DD — short title
One-line description. File: src/path/file.py:line. Discovered while: feature-name.
````

## End-of-feature review

After the last milestone commits, run a single review pass before `finishing-branch`:

1. Dispatch ONE reviewer subagent with the companion prompt `references/end-of-feature-reviewer-prompt.md`, giving it the design, the plan, the feature diff (`BASE_SHA..HEAD`, from the using-git-worktrees report) and the `## Findings` block.
2. It returns Strengths / Issues (Critical / Important / Minor / Followup) / Assessment. Fix Critical, Important and Minor; only Followup-tier items go to `followups.md`.
3. Commit the fixes as one "review fixes" milestone (same loop). One pass, fix, move on — wanting a re-review means a milestone was wrong; don't re-loop.

## Promotion: Tier 1 → Tier 2

After the end-of-feature review and its fixes:

1. Read your in-session `## Findings` block.
2. Drop anything that was addressed during the work.
3. Promote only Tier-2 items per the definition above. Anything else gets fixed in a small follow-up commit or dropped.
4. Commit the followups update.

## Hand off

Invoke **finishing-branch** to complete the work.

## Subagents during execution

Default: don't; stay in the main session. Dispatch one only for 2+ genuinely independent investigations (**using-parallel-agents** — it also defines the `## Findings` block every subagent must return) or for a context-heavy subtask whose findings, not its noise, you need. Store the findings inline before the next milestone.

## Red Flags — STOP

| Thought | Reality |
|---------|---------|
| "I'll skip the test, this case is obvious" | Then the test takes 30 seconds. Write it. |
| "I'll commit the feature now and refactor later" | The refactor is part of the milestone commit. Do it now. |
| "It's pre-existing, my change didn't introduce it" | Boy-scout rule. Pre-existing isn't out of scope. |
| "I'll just add one more guard to make it behave" | Compensating patches accrete into a broken design. The second one means STOP and re-open the design (see Circuit-breaker). |
