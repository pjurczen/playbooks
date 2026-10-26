---
name: writing-plans
description: Use after brainstorming and before any code, to turn an approved design into an execution list: milestones in order, each with what it does, the state it leaves and the checks that must be green.
---

# Writing Plans

A plan is the order the work is done in, and nothing else. The design says what and why; the plan says in which steps, what each step leaves behind and what
proves it. The user reads it to approve the order; an implementer in another session reads it to execute.

<HARD-GATE>
Present a plan only after walking its order against the repo. Every premise a milestone rests on is checked now, by reading the code or running a command. A
premise you cannot check goes to the user before approval, never to the implementer as "stop and ask". A plan that fails in its first hour was approved on a
guess.
</HARD-GATE>

Before the plan is presented, in order:

1. Check the scope.
2. Cut the work into milestones.
3. Walk the order against the repo.
4. Write the plan, self-review it, commit.
5. Get approval, then hand off to **executing-plans**.

Fired by brainstorming after design approval. When the user brings an approved design instead, apply **writing-adr**'s bar to its approach first.

## Working it out

**Scope.** A design across independent subsystems goes back to brainstorming as an initiative. Intersecting `docs/followups.md` items are folded in as
milestones.

**Milestones.** Each is a state the system can stay in: it builds, every suite is green, something new is observable. What everything depends on comes first;
the riskiest unknown comes early. Vertical slices, small enough to commit cleanly.

**Walk it.** Start from the state the previous milestone leaves and ask what this one breaks at the moment it is made. A changed shared type, signature or
dependency breaks every user at once: the milestone takes them all along, or old and new coexist until a later milestone removes the old one, and the plan says
which. Check each premise where it lives. Revert any probe.

**Settle.** A failed premise changes the order, or the design, which goes back to brainstorming.

## The plan

Save to `docs/playbooks/plans/YYYY-MM-DD-<feature>.md`. The header links the design, the ADR if any, the initiative for a slice.

- **Goal**: one sentence.
- **Milestones**, numbered, in order. Each:
  - *Does*: what it builds or removes, in which parts.
  - *Leaves*: the state of the system: what runs the new way, what still runs the old way.
  - *Checks*: what must be green: suites, gates, commands. A new test is named by the rule it proves.
- **Checked**: the premises the order rests on, one line each, as facts.
- **Open**: what neither the repo nor the user could settle: what, what it blocks, which milestone finds out. Omitted when empty.

Not in a plan:

- classes, files or signatures: the implementer finds them from the design and the code
- scenarios or test code: tests anchor to the rules the design states, and executing-plans writes them
- method bodies, commit messages
- anything the design already says

A plan longer than the order it describes has written the design or the code a second time.

## Self-review

1. The walk happened: every *Leaves* was checked, not assumed, and each premise has its line under Checked.
2. Nothing breaks in between: no milestone changes something shared without taking its users along or saying how old and new coexist.
3. Every rule and contract in the design is built in some milestone and covered by some *Checks* line.
4. Nothing the design says is repeated.
5. Could the user say, after a few minutes, why milestone two comes before three?

Fix inline.

## Approval

> "Plan committed to `<path>`: <n> milestones. Approve, or tell me what to change."

Wait for explicit approval. On changes, apply them and re-run the self-review. Then invoke **executing-plans**, nothing else.
