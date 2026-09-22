---
name: setting-up-gates
description: Use when a repo has no `.claude/gates.md`, or the user asks for linters, complexity limits or architecture tests, to propose and wire the lightest quality gates the stack supports and record them in the gates map.
---

# Setting Up Gates

A quality gate is a command that fails when the code's structure is wrong: a dependency points the wrong way, a function is too long or too complex, a block is duplicated. Models write locally plausible code with poor structure, and asking them to be careful doesn't change that; a gate they must pass does. This skill finds what the repo already enforces, proposes the smallest addition that covers what matters, and records both in `.claude/gates.md` so every other skill runs the same commands instead of guessing.

<HARD-GATE>
Propose, don't impose. Never write a config file or install a tool without the user's explicit approval, and never fix existing violations here — a baseline is information, not a task. A decline is recorded in the map so the pipeline stops asking.
</HARD-GATE>

## When this runs — and when to skip

- **Fired by using-git-worktrees** when it verifies a clean baseline and finds no `.claude/gates.md`.
- **Invoked directly** — "set up linters", "add an architecture test", "what gates do we have".

Skip when the map exists and the user hasn't asked for a change, or when it records a decline. A direct ask always applies.

## What a gate can enforce

Three properties are mechanically checkable in every mainstream stack, and they are the ones that decay first in generated code:

1. **Dependency direction** — which modules may import which; no cycles; layers stay layers.
2. **Function length and complexity** — a ceiling on lines per function and on cyclomatic or cognitive complexity.
3. **Duplication** — no repeated block above a size.

Defaults when the user has no preference: function ≤ 40 lines (statements where the stack's linter counts statements), complexity ≤ 10, duplicated block ≥ 10 lines. What no tool catches — a missing abstraction, a wrong diagnosis, an invariant kept by hand — is written under "Not enforced" so design and review know they own it.

## Procedure

1. **Detect the stack** from lockfiles and manifests (`pom.xml` / `build.gradle`, `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, `*.csproj`).
2. **Inventory what exists** — CI config, linter and formatter configs, architecture tests (ArchUnit, Konsist, dependency-cruiser, import-linter), a Sonar setup. Existing tools are kept and recorded; a Sonar server is used only if the repo already runs one, never proposed.
3. **Propose** from `references/gates-by-stack.md`: for each of the three properties the tool, the minimal config, the command and the threshold — one table — plus the gaps the stack can't cover and how the tools get installed (the repo's dev-dependency group; add one if there is none). Ask.
4. **On approval:** write the config, install the tools as proposed, run every gate once and report the baseline — how many violations exist today — without fixing any. Length and complexity gates are recorded as running on touched files, so the baseline blocks nothing. Dependency and duplication rules run repo-wide (one changed file has nothing to duplicate against) and are written so today's code passes: named exceptions for dependencies, the duplication threshold at today's count, both to tighten as code moves.
5. **Write `.claude/gates.md`** in the shape below and commit config and map together as `chore(gates): …` — or hand them over uncommitted when the target isn't its own repo.

## The map — `.claude/gates.md`

```markdown
# Quality gates

How this repo proves correctness and structure. Skills run these commands; none guesses one.

## Commands
- Tests: `<command>`
- Lint: `<command>` | not enforced
- Format: `<command>` | not enforced
- Complexity and length: `<command> <files>` — runs on touched files; thresholds under Rules enforced
- Structure (dependencies, layers): `<command>` — runs repo-wide
- Duplication: `<command>` — runs repo-wide | not enforced

## Rules enforced
- <one line per rule: "no import from X into Y", "function ≤ 40 lines, complexity ≤ 10", …>

## Not enforced
- <what no tool checks, what the team chose not to gate, or "declined on YYYY-MM-DD: <reason>">

## Conventions
- A structural rule a design introduces is added here and to the tool config in the feature's first milestone.
- Length and complexity run on the files a milestone touches; dependency and duplication rules run repo-wide.
```

## Who reads the map

using-git-worktrees runs every command as the clean baseline. executing-plans runs tests and gates after every green and after every refactor, and its structure critic reads the gate output. verifying-before-done counts a structure claim as proven only by a gate's output. brainstorming reads the rules as constraints on a design; writing-plans wires a design's new structural rules into the config in milestone one.
