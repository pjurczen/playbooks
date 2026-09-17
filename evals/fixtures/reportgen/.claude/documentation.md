# Documentation map

How documentation is maintained in this repo.

## Where things live

- `README.md` — usage.
- `docs/architecture.md` — how the pieces fit: sources, caches, summaries, report.
- `docs/adr/YYYY-MM-DD-<slug>.md` — one ADR per architecturally significant decision.
- `docs/followups.md` — durable backlog (created on first use).
- `docs/playbooks/designs/`, `docs/playbooks/plans/`, `docs/playbooks/initiatives/` — ephemeral working artifacts.

## Routing — where durable knowledge goes

- An architecturally significant decision → an ADR in `docs/adr/`.
- A change to component boundaries → `docs/architecture.md`.

## Conventions

- All documentation in English.
- ADRs are date-prefixed and immutable once accepted (status line excepted); supersede rather than edit.
