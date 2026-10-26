---
name: writing-plans
description: Use after brainstorming and before any code, to turn an approved design into a verified implementation order — the parts involved, milestones that keep the system working between them, and the tests that prove each.
---

# Writing Plans

Take an approved design and work out how it gets built: which parts of the system are involved, in what order, what state each step leaves behind, and which
tests prove it. Design = why, shape, logic. Plan = order. Its first reader approves it and wants to see that the order works; its second implements it in
another session and wants to know where to start and what done is at each step.

<HARD-GATE>
Present a plan only after walking its order against the repo. Every premise a milestone rests on — a dependency version that resolves, a type or field that
exists, the callers of what changes, a build that stays green in the intermediate state — is checked now, by reading the code or running a command. A premise
you cannot check is put to the user before approval; it never reaches the implementer as "stop and ask if". A plan that fails in its first hour of execution was
approved on a guess.
</HARD-GATE>

## Working it out

1. **Scope.** A design that sprawls across independent subsystems goes back to brainstorming as an initiative. Intersecting items in `docs/followups.md` are
   folded in explicitly, as milestones or parts of them. Entered without brainstorming (the user brought a design)? Apply **writing-adr**'s bar to its approach
   and invoke it before planning if it clears and no ADR exists on the branch.
2. **Decompose.** From the design's Architecture, list the parts of the system the work touches — modules and components — and for each the tests that cover it
   today and the tests it needs. Read the code of every part now: the plan is written from the code, not from the design's description of it.
3. **Order.** Cut the work into milestones, each a state the system can stay in: it builds, every existing suite is green, and something new is observable. What
   everything else depends on comes first; the riskiest unknown comes early, while changing course is cheap.
4. **Walk it.** Take each milestone from the state the previous one leaves and ask what it breaks at the moment it is made. A changed shared type, signature or
   dependency version breaks every user at once: the milestone takes all of them along, or old and new coexist — an overload, an adapter, a flag — until a later
   milestone removes the old one, and the plan says which. Check each premise where it lives: resolve the dependency, open the generated type, list the callers,
   run the suite that must stay green. Revert any probe; planning leaves only the plan.
5. **Settle what the walk found.** A premise that fails changes the order, or the design — edited with a `Deviation:` line and shown to the user first.

## The plan shape

The shape is `references/example-plan-replacement.md` — read it before writing. Save to `docs/playbooks/plans/YYYY-MM-DD-<feature>.md` and commit. Its sections:

- **Header** — links the design, the ADR if any, and the initiative for a slice.
- **Goal** — one sentence.
- **Parts involved** — a short table: the part, as the design names it; what changes there, in one line; its tests — the existing suites that must stay green
  and the new ones to write. A class is named only where the implementer would otherwise look in the wrong place; this is never a list of files to edit.
- **Order** — one block per milestone, in sequence:
  - *Builds* — what, in which parts.
  - *After it* — the state of the system: what works the new way, what still runs the old way, what coexists. Always building and green.
  - *Why here* — what it depends on, or what risk it retires; left out when the order is obvious.
  - *Proven by* — the tests, by scenario or suite name and home, at the level of behaviour. For a rule in the design's Logic, name the rule and say "one
    scenario per branch" rather than repeating it. Each milestone starts with these red.
- **Checked** — what the walk verified, one line each: the fact, and how it was checked. Only the premises the order rests on.
- **Open** — only what neither the repo nor the user could settle: what it is, what it blocks, and the milestone that finds out first. Left out when empty.

Milestones are vertical slices, small enough to commit cleanly and big enough for a refactor pass. Milestone one wires any structural rule from the design that
`.claude/gates.md` doesn't enforce yet; for greenfield work it also brings the minimal test scaffolding.

How the code reads is the implementer's: no method bodies, no test code, no file contents, no commit messages — a pre-written body rots before it is read. And
nothing the design already says: responsibilities, logic, contracts and consequences are linked, not repeated.

## Self-review

1. **The walk happened** — every *After it* was checked, not assumed; each premise has its line under Checked.
2. **Nothing breaks in between** — no milestone changes something shared without taking its users along or saying how old and new coexist.
3. **Coverage** — every rule in the design's Logic and every contract has a test in some milestone; every part is built in one.
4. **Overlap** — a sentence the design already says is deleted; component names match the design's.
5. **Readable** — could the user say, after a few minutes, why milestone two comes before three?

Fix inline.

## User review gate

> "Plan written and committed to `<path>`. Please review it and let me know if you want changes before we move to executing-plans."

Wait for explicit approval; on changes, apply them and re-run the self-review. Then invoke **executing-plans** — nothing else.
