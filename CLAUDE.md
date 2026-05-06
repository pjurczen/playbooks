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
skills/<name>/<companion>.md   — optional companion files (e.g. reviewer prompts)
docs/                          — design rationale and reference notes
```

## Conventions for skill files

- **YAML frontmatter required:** `name` (kebab-case, matches directory) and `description` (one sentence on when to use).
- **Tone:** senior dev to senior dev. State the rule and the reason; trust the reader to apply judgment.
- **Strong framing is OK** (`<EXTREMELY-IMPORTANT>`, Red Flags tables, `dot` flowcharts) where it drives compliance — but always paired with an explicit "when to skip" carve-out.
- **Soft length target ~150 lines.** A skill that runs longer should justify itself (operationally dense, like `finishing-branch`); otherwise split or trim.
- **Cross-skill references:** when one skill expects another to follow it, name the next skill explicitly (`Invoke writing-plans`).

## Conventions for produced artifacts

This is the actual differentiator from superpowers. The artifacts the *user* reads (design docs, plans) must be readable end-to-end in 2–3 minutes:

- Plans are intent-shaped (components, behaviours, milestones, risks) — no pre-written test code, no per-step commit messages.
- Design docs are sectioned and scaled to the topic's complexity.
- Commit messages follow Conventional Commits and describe the *why* of the slice, not a play-by-play of files.

Skill files themselves can be richer where compliance demands it — but the artifacts the user reads are the bloat target.

## Testing changes

There is no automated test suite. Verification is empirical:

1. **Sanity-check the JSON.** After editing `plugin.json` or `hooks.json`:
   ```bash
   python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"
   python3 -c "import json; json.load(open('hooks/hooks.json'))"
   ```
2. **Sanity-check the bash hook.** After editing `hooks/session-start`:
   ```bash
   bash -n hooks/session-start
   CLAUDE_PLUGIN_ROOT=$(pwd) hooks/session-start | python3 -m json.tool
   ```
3. **Dogfood.** Load the plugin in a fresh Claude Code session and run a small real task. The acceptance smoke test: ask "let's make a small react todo list" and verify `brainstorming` triggers without prompting.

## Commits

Conventional Commits 1.0.0. See `skills/milestone-commits/SKILL.md` for the rules — they apply to this repo's own history.

## License

[MIT](LICENSE).
