# Playbooks

A lean, opinionated library of workflow skills for Claude Code.

Playbooks gives Claude a small set of process skills — for designing features, planning, executing in milestones, debugging, testing, and finishing branches — that auto-load at the start of every session. The library is intentionally small: fifteen skills, about 13,000 words of markdown in total, and every change to a skill is measured against evals before it ships. Less to read, less ceremony, more trust in the model.

## Why not just use [superpowers](https://github.com/obra/superpowers)?

Playbooks started as a fork of superpowers and ended up as a different design. The mechanism is the same — `SessionStart` hook + a folder of opinionated markdown — but the philosophy diverges in a few specific ways:

| Topic | Superpowers | Playbooks |
|-------|-------------|-----------|
| Plans | Pre-write every test, every method signature, every commit message | An exact work map — changes by class and method, scenarios tied to the design's guarantees, milestones. Signatures live in the design's contracts; bodies, tests and commit messages stay with the implementer. |
| Execution | Subagent-driven by default; cheaper models for "mechanical" tasks | Main-session by default, on the main model. Subagents are situational (parallel work, context-heavy lookups). |
| Commits | One per TDD step (~5 per task, dozens per feature) | One per milestone; uses Conventional Commits. |
| Testing | Strict TDD, including structural tests | BDD-flavoured: behaviour-shaped tests for code with interesting logic. No tests for enums, dataclasses, thin wrappers. |
| Reviews | Two reviewer subagents per task + a final pass | One self-checkpoint per milestone + one focused review pass at end-of-feature. |
| Refactor | Implicit in TDD's third step | Explicit boy-scout pass per milestone, with scope and time-box guardrails. |
| Multi-harness | Ships configurations for Codex, Cursor, Gemini, Copilot CLI | Claude Code only. |

If superpowers' rigour fits your work, use superpowers — it has a track record. Playbooks is the version I wanted for myself: faster to follow, less to read, more deference to Claude's judgment.

## Install

As a Claude Code plugin (assuming a local checkout):

```bash
# In Claude Code, point the plugin marketplace at this directory
# or symlink playbooks/ into your plugins directory.
```

Once loaded, the `SessionStart` hook fires on session start / clear / compact and injects the `using-playbooks` skill into context. Other skills are loaded on demand via the `Skill` tool.

## What's inside

**Process** (how to approach the work):
- `brainstorming` — design dialogue → committed design doc: a narrative a teammate can follow, the views the reader needs, the contracts the implementer must match; kinds of work from a feature to an initiative
- `writing-plans` — design → exact implementation plan an implementer in another session can execute; stands on the design, never restates it
- `writing-roadmap` — initiative design → a roadmap of independently landable slices, their order and exit criterion
- `executing-plans` — main-session milestone loop: tests and gates green, a fresh-context structure critic, a refactor pass, one commit per milestone, an end-of-feature review
- `debugging` — root cause with evidence before any fix, pinned by a red-first regression test
- `finishing-branch` — verify tests, then merge / PR / keep / discard
- `consolidating-docs` — on landing, graduate durable decisions into real docs and delete the design/plan husks
- `writing-adr` — one short ADR at design altitude when a decision clears the significance bar; written at brainstorming, promoted on landing

**Implementation** (how to do the work):
- `using-git-worktrees` — pick a workspace mode before anything is committed (default: new worktree on a new branch)
- `setting-up-gates` — propose and wire the lightest linters, complexity limits and architecture tests the stack supports, recorded in `.claude/gates.md`
- `bdd-testing` — behaviour-shaped tests for code with interesting logic
- `milestone-commits` — one commit per slice, Conventional Commits format

**Cross-cutting**:
- `verifying-before-done` — never claim done without running the verification first
- `using-playbooks` — bootstrap: when to invoke vs when to skip

**Situational**:
- `using-parallel-agents` — parallel subagents for genuinely independent investigations

## Usage

Just describe what you want — the bootstrap handles the rest. For non-trivial work, the agent will run the pipeline:

```
brainstorming → writing-plans → executing-plans → finishing-branch
```

Each stage produces a small, readable artifact:
- `docs/playbooks/designs/<date>-<topic>.md` — the design
- `docs/playbooks/plans/<date>-<feature>.md` — the implementation plan
- `<adr home>/<date>-<slug>.md` — the decision, if the feature made one (most don't)
- `docs/playbooks/initiatives/<date>-<topic>.md` and its roadmap — target architecture, coexistence mechanism and slices when work spans several landings (optional)
- `docs/followups.md` — durable notes from past work

When a feature lands, `consolidating-docs` promotes the feature's ADR from `proposed` to `accepted`, graduates the remaining durable decisions from its design and plan into the repo's real documentation — guided by `.claude/documentation.md`, a map of where docs live — and removes the husks.

For trivial questions, read-only exploration, and one-off changes, the agent skips the pipeline and just answers.

## Evals

`evals/` holds four evals — design a feature, plan from a design, record an ADR under a repo-specific map, and a trivial change that must not trigger the pipeline — run on Opus against a snapshot of the previous skills and against no skills at all. Results live in `evals/results/`; CLAUDE.md describes the loop.

## Design

The full design rationale — what changed from superpowers and why — is in [`docs/DESIGN.md`](docs/DESIGN.md).

## License

[MIT](LICENSE)
