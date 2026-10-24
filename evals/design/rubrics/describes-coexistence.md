---
id: describes-coexistence
name: No coexistence hidden in a single design
unit: doc
scoring: binary
direction: higher
applies_to: [design]
needs: [judge]
quote_required: fail
batch: 1
sources:
  - Spotify 2024, in-car case study (a big-picture RFC that frames options, then focused RFCs)
  - playbooks brainstorming (work where old and new must coexist while landing is an initiative, not one design)
---

This document is a single design, not an initiative with slices. Decide whether it describes work that cannot land in one step.

Pass when the design describes one target state, reached in one change, with no period in which an old and a new path both run.

Fail when the design describes a period where old and new paths run together, routing or switching between them, a sequence of separate landings each leaving
the system usable, a migration phase with both shapes present, or a rollout that spans several releases. Such work belongs in an initiative design with slices.

Unknown when the document mentions a phase but you cannot tell whether both paths run at once.

Evidence: for a fail, quote the passage that describes the coexistence or the sequencing. A pass needs no quote.
