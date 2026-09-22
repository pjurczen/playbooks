# Documentation map

How documentation is maintained in this repo. Consult this before adding, moving, or substantially changing docs.

## Where things live

- `README.md` — user-facing overview: what playbooks is, install, usage, the skill list.
- `docs/DESIGN.md` — design rationale: why the methodology is shaped the way it is. A point-in-time analysis plus dated addenda.
- `skills/<name>/SKILL.md` — the skills themselves; each is the source of truth for how that workflow behaves.
- `CLAUDE.md` — conventions for agents editing this plugin.
- `.claude/gates.md` — the repo's quality gates: which commands prove structure, and what is not enforced.
- `RELEASE-NOTES.md` — user-facing changes per release.
- `docs/followups.md` — durable, cross-feature backlog (created on first use).
- `docs/playbooks/designs/`, `docs/playbooks/plans/` — ephemeral working artifacts; consolidated into the docs above and deleted when work lands. `docs/playbooks/initiatives/` — an initiative's design and roadmap, on the base branch; consolidated only when the roadmap's last slice lands.

## Routing — where durable knowledge goes

- A methodology or design decision + its rationale → a dated addendum in `docs/DESIGN.md` (don't rewrite the original analysis).
- A change to how a skill behaves → that skill's `skills/<name>/SKILL.md`.
- A change to overview, install, or usage → `README.md`.
- A convention for contributors editing the plugin → `CLAUDE.md`.
- A release-worthy user-facing change → `RELEASE-NOTES.md`.

## Conventions

- Skill files: YAML frontmatter (`name` matches the directory), senior-dev tone, ~150-line soft target, always a "when to skip" carve-out.
- `docs/DESIGN.md` is historical; record later decisions as dated addenda rather than editing the original sections.
- Commits follow Conventional Commits 1.0.0 (see `skills/milestone-commits/SKILL.md`).
- Artifacts a user reads (README, design docs, plans): the narrative layer reads in 2–3 minutes; the precision layer (contracts, plan) is complete enough for an implementer in another session. Structure and altitude, not length.
