# Documentation map

How documentation is maintained in this repo.

## Where things live (durable)

- `README.md` — usage.
- `doc/asciidoc/` — arc42 architecture documentation (AsciiDoc).
- `doc/adr/reporting/` — Architecture Decision Records for the reporting domain (sources, caches, summaries, report), one per decision, date-prefixed.
- `doc/adr/export/` — Architecture Decision Records for the export domain (CLI, output formats).
- `docs/followups.md` — durable backlog of follow-up items (not swept by consolidation).

## Working artifacts (ephemeral)

- `docs/playbooks/designs/`, `docs/playbooks/plans/`, `docs/playbooks/initiatives/` — design documents and plans for initiatives in progress.

## Routing — where durable knowledge goes

- An architecturally significant decision → a new ADR in `doc/adr/reporting/` or `doc/adr/export/` (format: `YYYY-MM-DD-adr-<topic>.md`).
- A change to component boundaries or architecture → `doc/asciidoc/` (chapter 5, building blocks).
- A follow-up task discovered during work → append to `docs/followups.md`.

## Conventions

- ADRs and arc42 docs are written in **German** (domain language). All other documentation (README, working artifacts, this file) is in **English**.
- ADRs are date-prefixed and immutable once accepted; supersede rather than edit.
- ADR naming: `YYYY-MM-DD-adr-<kebab-case-topic>.md`.
- When adding a new ADR, **also add an entry** to the index table in `doc/asciidoc/09_architecture_decisions.adoc`.
- Design/plan files use the same date prefix: `YYYY-MM-DD-<topic>.md`.
