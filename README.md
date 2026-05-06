# Playbooks

A lean, opinionated library of workflow skills for Claude Code.

Playbooks gives Claude a small set of process skills — for designing features, planning, executing in milestones, testing, and finishing branches — that auto-load at the start of every session. The library is intentionally small: nine skills, roughly 1,200 lines of markdown total. Less to read, less ceremony, more trust in the model.

## Why not just use [superpowers](https://github.com/obra/superpowers)?

Playbooks started as a fork of superpowers and ended up as a different design. The mechanism is the same — `SessionStart` hook + a folder of opinionated markdown — but the philosophy diverges in a few specific ways:

| Topic | Superpowers | Playbooks |
|-------|-------------|-----------|
| Plans | Pre-write every test, every method signature, every commit message | Intent-shaped: components, behaviours, milestones, risks. Readable end-to-end in 2-3 minutes. |
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
- `brainstorming` — design dialogue → committed design doc
- `writing-plans` — design → intent-shaped implementation plan
- `executing-plans` — main-session milestone loop with self-checkpoints, refactor pass, end-of-feature review
- `finishing-branch` — verify tests, then merge / PR / keep / discard

**Implementation** (how to do the work):
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
- `docs/playbooks/followups.md` — durable notes from past work

For trivial questions, read-only exploration, and one-off changes, the agent skips the pipeline and just answers.

## Design

The full design rationale — what changed from superpowers and why — is in [`docs/DESIGN.md`](docs/DESIGN.md).

## License

[MIT](LICENSE)
