---
name: writing-adr
description: Use when brainstorming settles an architecturally significant choice, or when the user asks to record a decision, to write a short Nygard-style ADR at design altitude in the repo's ADR home.
---

# Writing ADRs

An Architecture Decision Record captures one decision, the forces behind it, the options rejected, and what it costs. It is written when the decision is made — not after the code exists — and it stays readable after every rename. This skill is the only place ADR text is written; brainstorming, writing-plans and consolidating-docs invoke it rather than freehanding the format.

**Announce at start:** "Using writing-adr to record the decision."

## When this runs — and when to skip

- **Fired by brainstorming** after design approval and workspace choice — the normal path. The decision is fresh, the rejected approaches are still on the table, and no code exists yet, so the record can only be at design altitude.
- **Fired by writing-plans** (the user brought an approved design and skipped brainstorming) or **by consolidating-docs** (fallback at landing) — always from the design doc, never from the diff.
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

Read `.claude/documentation.md` first. It owns:

- **Where ADRs live** — possibly several homes, one per domain. Pick by the feature's domain; if it isn't obvious, ask.
- **Filename pattern** — follow it exactly.
- **Language** — prose *and* headings. German ADRs get German headings.
- **An index** — only if the map names one. Then add the entry. Never create an index the map doesn't mention.
- **Status vocabulary**, if the map defines one.

Follow the repo's naming and language. Follow *this skill's* shape — not the shape of the ADRs already in the directory. They may be the bloated ones this skill exists to stop.

**No map, or no ADR home in it:** propose `docs/adr/` with `YYYY-MM-DD-<slug>.md` naming plus a routing line for the map. Propose, don't impose — same posture as consolidating-docs' bootstrap. If the repo already numbers its ADRs, honour that; don't introduce numbering yourself — dates never collide across in-flight branches. No `template.md`, no index README: filenames are the index.

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

The ADR sits one level above the design doc. Components and mechanisms, not classes and methods.

- **No code blocks. No backticks.** A component may be named as a proper noun in prose. The moment you reach for a backtick you're at code altitude.
- **No annotations, signatures, or file paths.** Git has them, and they rot on the first rename.
- **Context is prose, not a list.** A numbered findings list is a review report, not the forces behind a decision.
- **Consequences say what got easier or harder** — not which classes were deleted. That's a diff summary.
- **Alternatives are one line each.** The reason it lost, not a pros-and-cons matrix.

## Lifecycle

```
proposed → accepted (YYYY-MM-DD) → superseded by <link> | deprecated
```

- **proposed** — written at brainstorming, on the feature branch. Editable in place: circuit-breaker re-opens, reviewer drift findings, wording.
- **accepted** — flipped by consolidating-docs when the feature lands, dated with the landing date. From here the status line is the one mutable field. Everything else: supersede, don't edit.
- **superseded / deprecated** — set on the old ADR when a new one reverses it, or when the feature it governs is removed. Always link the replacement.

A `proposed` ADR sitting on the base branch means consolidation was skipped — flip it when you see it. Recording a decision from the past? Say so in Context and give the original date.

## Where it fits in the pipeline

- **brainstorming** invokes this after design approval; the ADR is presented at the same review gate as the design doc — no separate confirmation. The design doc links the ADR from its Approach section and doesn't restate it.
- **executing-plans** — a circuit-breaker that re-opens the design revises the `proposed` ADR in place. Never a second ADR for the same feature.
- **The end-of-feature reviewer** checks whether the Decision is still true of the code.
- **consolidating-docs** reconciles drift, flips `proposed` → `accepted`, updates the index if the map names one. It never writes ADR text on its own.

## Red Flags — STOP

| Thought | Reality |
|---------|---------|
| "I'll list the findings that led here" | Findings are review output. Two sentences of forces. |
| "The design doc names the classes, so the ADR can too" | The design doc is a husk; the ADR outlives every rename. Proper nouns, no backticks. |
| "Every decision in the design deserves a record" | Most features produce no ADR. Apply all three tests. |
| "The existing ADRs here look like X, I'll match them" | Match naming and language. The shape comes from this skill. |
| "The implementation changed a bit, I'll write a second ADR" | It's still `proposed`. Edit it in place. |
| "Consequences: removed A, B, C" | That's a diff. What got easier or harder? |
| "I'll skip the alternatives, we just picked it" | Then it wasn't a decision, and it doesn't need an ADR. |
