# Initiative designs — target, coexistence, shared contracts

## What an initiative is

Work that can't land in one design → plan → execute cycle: several slices, each landable on its own, sharing a target
architecture and an order. Three properties make it one. A target state no single slice reaches. A coexistence period,
in which old and new run side by side until the last slice lands. Shared contracts set once, that every slice builds
against. Size alone is not one of them.

Signals at brainstorming: the request spans several subsystems; the chosen approach needs old and new to coexist while
it lands; it can't land in one branch without breaking something; a third ADR-worthy decision is appearing.

## The document

The same sections as a feature design (`design-doc-shape.md`), with these differences:

- **Problem** and **Diagnosis** at system level, up to three paragraphs each; Problem ends with what done means for the
  whole initiative: the end state reached and the legacy that is gone.
- **Design** holds two things a feature design never has. The **target architecture**: the after-picture, as a context
  or structure view of the end state. The **coexistence mechanism**: how work is routed between old and new while slices
  land, what stays byte-identical, what state is duplicated and how it stays consistent, and how the split disappears at
  the end. Coexistence is where the risk lives, and a slice design cannot own it.
- **Contracts** are the shared ones, what every slice builds against. A slice's own contracts stay in its design.
- **Guarantees** hold at every intermediate state, not only at the end. One of them says which slice orders the
  coexistence mechanism supports — the roadmap may only choose among those.
- **Decisions** as in a feature design. The target architecture is usually the ADR-worthy one: written `proposed` with
  the initiative, promoted when the first slice lands.
- **No slices, behaviours or milestones.** The roadmap (writing-roadmap) owns slices and their order; slice plans own
  behaviours and milestones.

The example is `example-design-initiative.md`; its roadmap is `../../writing-roadmap/references/example-roadmap.md`.

## Where it lives and how it changes

`docs/playbooks/initiatives/YYYY-MM-DD-<topic>.md`, committed to the base branch as a docs-only change with the usual
confirmation for main, because every slice — including parallel ones in their own worktrees — must see it. It is a
working document: when a slice proves it wrong, edit it and add a `Deviation:` line under Approach; never a callout.
consolidating-docs leaves it alone until the roadmap's last slice lands, then graduates the target architecture into the
architecture doc, drops the coexistence mechanism because it's over, writes the below-bar decisions as sentences there,
and deletes the file. The ADRs remain.

## Slice mode

A slice of an initiative inherits and does not restate: `Initiative:` in the header; Problem is one line naming the
slice and what it delivers; Design draws only this slice's portion; Contracts lists only what the slice adds; Decisions
only the slice's own; approaches are proposed only for the slice's delta. An ADR is rare here — the initiative's covers
it. Resuming later: read the initiative design and the roadmap, take the next unblocked slice or the one the user names.

## Discovered mid-execution

A feature that turns out to be an initiative arrives through executing-plans' circuit-breaker. Extract the initiative
design from the current design — target, coexistence, shared contracts, decisions — commit it on the base branch, write
the roadmap, and let the current branch become slice one, its design trimmed to that slice's delta.
