# Playbooks Release Notes

## v0.2.1 (2026-05-06)

### Milestone-commits invocation made explicit

`executing-plans` Step 8 read as a cross-reference ("commit per **milestone-commits**") and the skill body wasn't being loaded — agents fell back to using the plan's milestone titles as commit subjects (e.g. `Phase 2 M5: ReActAgent tool_calls writes`). Step 8 now explicitly invokes the skill, with a sentence noting the plan's milestone titles are reasoning scaffolding for the implementer, not commit material. `milestone-commits` anti-patterns table gains a row naming this failure mode.

## v0.2.0 (2026-05-06)

### End-of-feature review tightened

Closed a leak where trivial fixes were being promoted to `followups.md` instead of fixed in the review-fix milestone:

- Reviewer prompt now produces four severity buckets: Critical / Important / Minor (fix in review-fix milestone) / Followup (architectural, promote to `followups.md`).
- `Tier 2 — Durable followups` redefined to only items that need their own design / plan; anything fixable in a boy-scout pass stays in scope.
- Step 5 self-checkpoint now flags "added X but didn't wire it up at the call sites the plan named" as incomplete milestone work, not a finding for end-of-feature review.
- Red Flags row added: "Pre-existing ≠ out-of-scope."

## v0.1.0 (2026-05-06)

Initial release. Forked from [superpowers](https://github.com/obra/superpowers) and reshaped around different defaults: intent-shaped plans, main-session execution, milestone commits, BDD-flavoured tests, one end-of-feature review pass. See `README.md` for the skill list and `docs/DESIGN.md` for the rationale.

Mechanism: a SessionStart hook injects `using-playbooks` on every session start / clear / compact; other skills load on demand via the `Skill` tool.

Skill descriptions follow a canonical shape — `Use [trigger], to [goal]` — so pre-loaded metadata states both the firing condition and the purpose.
