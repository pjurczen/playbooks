---
name: writing-adr
description: Use when brainstorming settles an architecturally significant choice, or when the user asks to record a decision, to write a short Nygard-style ADR at design altitude in the repo's ADR home.
---

# Writing ADRs

An Architecture Decision Record captures one decision, the forces behind it, the options rejected, and what it costs. It is written when the decision is made — not after the code exists — and it stays readable after every rename. This skill is the only place ADR text is written; consolidating-docs promotes `proposed` to `accepted` at landing but never writes ADR text itself.

## When this runs — and when to skip

- **Fired by brainstorming** after design approval — the normal path: the decision is fresh, the rejected approaches are on the table, and no code exists yet.
- **Fired by writing-plans** (mid-pipeline entry) or **consolidating-docs** (fallback at landing) — from the design doc, never from the diff.
- **Invoked directly** — "ADR this", "write down why we chose X".

Skip when:
- The decision doesn't clear the bar below. Most features don't.
- The decision already has an ADR: `proposed` → edit it in place; `accepted` → write a superseding one only if the decision is actually being reversed.
- The user asks "why did we choose X?" — that's a read. Find the ADR and answer.

## The bar — all three, or no ADR

1. **Constrains work beyond this feature.** Others will have to follow it or work around it.
2. **Hard to reverse.** It's structural: a boundary, a data flow, a dependency, a mechanism added or removed.
3. **There was a real choice.** Two or more approaches a competent engineer might reasonably have picked. If brainstorming's options were the obvious way, the obvious way with a twist, and a strawman, nothing was decided.

| Decision | ADR? |
|----------|------|
| A new pattern every future caller must follow | yes |
| Removing a mechanism someone might otherwise reintroduce | yes |
| Reversing an accepted ADR | yes — as a supersede |
| A component built the way its neighbours are built | no |
| The obvious standard library for the job | no |
| Naming, formatting, a version bump, a refactor that keeps the design | no |

**Most features produce no ADR.** One per feature is the norm. If you're writing a third, the feature should have been split at brainstorming.

## Conventions come from the map, not from this skill

Read `.claude/documentation.md` first. It owns where ADRs live (possibly several homes, one per domain — pick by the feature's domain; ask if it isn't obvious), the filename pattern, the language — prose *and* headings; German ADRs get German headings — whether there is an index to update (never create one the map doesn't mention), and any status vocabulary.

Follow the repo's naming and language. Follow *this skill's* shape — not the shape of the ADRs already in the directory; they may be the bloated ones this skill exists to stop.

**No map, or no ADR home in it:** propose `docs/adr/` with `YYYY-MM-DD-<slug>.md` naming plus a routing line for the map — propose, don't impose. Dates rather than numbers, because dates never collide across in-flight branches; no `template.md`, no index README.

## The shape

```markdown
# <The decision, as a short noun phrase — names the choice, not the class>

**Status:** proposed

## Context
Two to five sentences of prose. The forces at play: what hurt, what constrained, what was at stake.

## Decision
One to three sentences. Y-statement shape: "In the context of <situation>, facing <concern>,
we decided <this> over <that> and <the other>, to achieve <quality>, accepting <cost>."

## Alternatives
- <Option> — rejected because <one clause>.
- <Option> — rejected because <one clause>.

## Consequences
- Three to six honest bullets: what gets easier, what gets harder, what future work must respect.
```

Whole thing under ~40 lines — a two-minute read. See `example.md` beside this skill for a real decision at the right altitude.

## Altitude — mechanical rules

The ADR sits one level above the design doc: components and mechanisms, not classes and methods, because the design doc is a husk and the ADR outlives every rename.

- **No code blocks. No backticks.** A component may be named as a proper noun in prose; the moment you reach for a backtick you're at code altitude.
- **No annotations, signatures, or file paths.** Git has them, and they rot on the first rename.
- **Context is prose, not a list.** A numbered findings list is a review report, not the forces behind a decision.
- **Consequences say what got easier or harder** — not which classes were deleted; that's a diff summary.
- **Alternatives are one line each** — the reason it lost, not a pros-and-cons matrix. No alternatives means it wasn't a decision, and it doesn't need an ADR.

## Lifecycle

```
proposed → accepted (YYYY-MM-DD) → superseded by <link> | deprecated
```

- **proposed** — written at brainstorming, on the feature branch; editable in place (a circuit-breaker re-open, a reviewer's drift finding). An implementation that changed a bit means editing this one, never a second ADR.
- **accepted** — flipped by consolidating-docs at landing, dated. From here the status line is the one mutable field; everything else is superseded, not edited.
- **superseded / deprecated** — set on the old ADR when a new one reverses it or its feature is removed; always link the replacement.

A `proposed` ADR sitting on the base branch means consolidation was skipped — flip it when you see it. Recording a decision from the past? Say so in Context and give the original date.
