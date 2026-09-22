# Quality gates

How this repo proves correctness and structure. Skills run these commands; none guesses one. The "code" here is markdown, so the gates are structural checks on
the skill library.

## Commands
- Tests: the eval loop in `evals/` — run manually on Opus per CLAUDE.md; not a single command
- Lint: not enforced
- Format: not enforced
- Complexity and length: `scripts/check-skills.sh` — word budgets per skill, one gate per skill, Red Flags placement
- Structure (dependencies, layers): `scripts/check-skills.sh` — reference links resolve, no stale names, example sections in order, no reflow damage
- Duplication: not enforced

## Rules enforced
- Word budgets: ≤ 1,000 per SKILL.md; 1,500 for `finishing-branch`, `executing-plans`, `consolidating-docs`; 1,200 for `writing-adr`, `brainstorming`; 500 for
  `using-playbooks`.
- One gate block per skill; Red Flags tables only on the six discipline skills, ≤ 4 rows; no per-skill announce lines; no `dot` graphs.
- Frontmatter `name` matches the directory; description in "Use …, to …" shape.
- Every `references/` link resolves; no brand names in skills.
- The three example designs and the eval fixture carry the eleven design sections in order.
- No bold marker split by a line wrap; no merged headings or bullets.
- Prose lines are at most 160 columns; tables, fences and frontmatter are exempt. `scripts/reflow-md.py` rewraps a file without changing its content.

## Not enforced
- Prose quality, tone, and whether a rule earns its place — the human read-through and the evals.

## Conventions
- A structural rule a skill change introduces is added to `scripts/check-skills.sh` and listed here in the same commit.
- The pre-commit hook in `scripts/hooks/` reflows staged markdown and runs the script; `git config core.hooksPath scripts/hooks` installs it.
