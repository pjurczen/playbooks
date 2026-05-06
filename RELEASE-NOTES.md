# Playbooks Release Notes

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
