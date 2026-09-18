# Playbooks — working on the plugin itself

This file is for Claude (or any agent) editing the source of the `playbooks` plugin. If you're using `playbooks` *as* a plugin in some other project, ignore this file — `using-playbooks/SKILL.md` is what you want.

## What this repo is

A Claude Code plugin: a `SessionStart` hook that injects `using-playbooks/SKILL.md` into every new / cleared / compacted session, plus a folder of skills loaded on demand via the `Skill` tool. That's the entire mechanism.

## Where things live

```
.claude-plugin/plugin.json     — plugin metadata
hooks/hooks.json               — registers the SessionStart hook
hooks/session-start            — bash script: loads using-playbooks, escapes for JSON, emits hookSpecificOutput.additionalContext
skills/<name>/SKILL.md         — one skill per directory
skills/<name>/references/*.md  — documents a step tells the model to read: shapes, worked examples, reviewer prompts
docs/                          — design rationale and reference notes
```

## Conventions for skill files

Skill files are prompts. Instruction count degrades adherence and early instructions win, so every line has to earn its place. The rules:

- **YAML frontmatter required:** `name` (kebab-case, matches directory) and `description` in the shape "Use [trigger], to [goal]" — what and when, never a summary of the steps.
- **Budget in words, not lines** (`wc -w`, tables included): ≤ 1,000 per SKILL.md; ≤ 1,500 for runbooks (`finishing-branch`, `executing-plans`, `consolidating-docs`); ≤ 500 for `using-playbooks`, which is loaded every session.
- **One gate per skill, first, with its reason, in normal register.** Everything else is a rule with a reason; caps live only inside that gate.
- **One rule, one owner.** A rule lives in the skill or companion that owns it; other skills point to it and never restate it.
- **Red Flags tables only where discipline is the point** (`using-playbooks`, `brainstorming`, `executing-plans`, `verifying-before-done`, `debugging`, `consolidating-docs`), ≤ 4 rows, each naming an excuse the body doesn't already refute — not a body rule with a quotation mark in front.
- **No per-skill "Announce at start"** — the bootstrap says to announce once. **`dot` graphs only for a real loop or non-obvious branch**; linear flows are numbered lists.
- **"When to skip" is a standard section** in every directly-invocable skill; pipeline-only skills say "fired by X".
- **Companions carry a read-when** ("read `references/design-doc.md` before step 7"). **Positive framing, reasons over emphasis, no brand names.**
- **Tone:** senior dev to senior dev. State the rule and the reason; trust the reader.

## Conventions for produced artifacts

This is the actual differentiator from superpowers. The artifacts the *user* reads (design docs, plans) have two readers: a teammate who follows the narrative without the codebase, and an implementer in another session — Opus-class by default — who must find nothing to guess. Structure and altitude, not length, are the bar:

- Design docs have a fixed shape: Problem, Approach (with alternatives), Shape (one mermaid diagram), Contracts, Guarantees, Risks, Out of scope. The narrative layer reads in 2–3 minutes; Contracts carry public signatures with semantics — never bodies.
- Plans are exact work maps — a changes table by class and method, call-site from → to, scenarios tied to the design's Guarantees, milestones — and never restate the design. No test code, no bodies, no per-step commit messages.
- Commit messages follow Conventional Commits and describe the *why* of the slice, not a play-by-play of files.
- ADRs are 2-minute reads at design altitude — no code, no symbols, alternatives named. Written when the decision is made (brainstorming), not when the feature lands.

Skill files themselves can be richer where compliance demands it — but the artifacts the user reads are the bloat target.

## Testing changes

Verification is empirical, and a skill change does not ship on judgment alone.

1. **Sanity-check the JSON and the hook** after editing them:
   ```bash
   python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"
   python3 -c "import json; json.load(open('hooks/hooks.json'))"
   bash -n hooks/session-start && CLAUDE_PLUGIN_ROOT=$(pwd) hooks/session-start | python3 -m json.tool
   ```
2. **Word budgets and structure:** `wc -w skills/*/SKILL.md` against the budgets above; one gate per skill; Red Flags only on the six discipline skills.
3. **Run the evals.** `evals/evals.json` holds the prompts and expectations; `evals/fixtures/` the fixture repos; `evals/run-setup.sh <eval-id> <run-dir>` prepares a run; `evals/grade.py` grades the mechanical expectations into the skill-creator viewer format. Runs live outside the repo in `../playbooks-workspace/iteration-N/eval-*/<config>/run-1/`, one subagent per run **on Opus** (the model that runs these skills), with a snapshot of the previous skills as the baseline. Aggregate with the skill-creator's `aggregate_benchmark.py` and review in its viewer. A change ships when its delta is non-negative on pass rate and tokens.
4. **Dogfood.** Load the plugin in a fresh session and run a small real task; "let's make a small react todo list" must trigger `brainstorming` unprompted, and a one-sentence rename must not.

## Commits

Conventional Commits 1.0.0. See `skills/milestone-commits/SKILL.md` for the rules — they apply to this repo's own history.

## License

[MIT](LICENSE).
