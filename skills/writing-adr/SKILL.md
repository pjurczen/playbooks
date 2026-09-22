---
name: writing-adr
description: Use when brainstorming settles an architecturally significant choice, or when the user asks to record a decision, to write a short Nygard-style ADR at design altitude in the repo's ADR home.
---

# Writing ADRs

An Architecture Decision Record captures one decision, the forces behind it, the options rejected, and what it costs. It is written when the decision is made, not after the code exists. This skill is the only place ADR text is written; consolidating-docs promotes `proposed` to `accepted` at landing but never writes one.

## When this runs — and when to skip

- **Fired by brainstorming** after design approval — the normal path: the decision is fresh and no code exists yet.
- **Fired by writing-plans** (mid-pipeline entry) or **consolidating-docs** (fallback at landing) — from the design doc, never the diff.
- **Invoked directly** — "ADR this", "write down why we chose X".

Skip when:
- It isn't worth an ADR (below); most aren't.
- It already has an ADR: `proposed` → edit in place; `accepted` → supersede only if the decision is being reversed.
- "Why did we choose X?" is a read — find the ADR and answer.

## Worth an ADR, or not

The deciding test: **state the decision without naming the feature that triggered it.** If nothing is left, it is a design decision: it lives in the design doc, and its one durable sentence goes to the architecture doc.

**Worth an ADR** — specific in the choice, system-wide in scope ("use Prisma", not "use an ORM"):
- A structural rule every process must follow.
- A technology or platform choice.
- A boundary, contract or API other modules build against.
- A data model or caching policy.
- A cross-cutting policy: transactions, idempotency, security, deployment.
- A deliberate trade-off with lasting cost.
- A reversal of any of the above — as a supersede.

**Not worth an ADR** — design-doc content, or a commit message:
- A refactoring outcome: "replace X and Y with Z".
- An internal algorithm, module placement, naming.
- Removing a mechanism — unless stated as the rule that keeps the mechanism out.
- Anything true of only one feature.

A real ADR also constrains work beyond this feature, is hard to reverse, and came from a real choice between approaches a competent engineer might have picked. One per feature is the norm; most features produce none.

## Rule or instance

The approach brainstorming picked is usually an instance. If it instantiates a rule the team is adopting, the rule is the decision and the feature is the evidence in Context. If it is itself a system-level choice — a database, a platform — record the choice. Neither: no ADR.

An ADR records a decision that was taken. Someone who sees a wider rule in a design proposes a *new* ADR, status `proposed`; they don't rewrite the record.

## Conventions come from the map, not from this skill

Read `.claude/documentation.md` first. It owns where ADRs live (several homes → pick by the feature's domain; ask if unclear), the filename pattern, the language — prose *and* headings — any index to update (never create one the map doesn't mention), and any status vocabulary.

Follow the repo's naming and language, and *this skill's* shape — not the shape of the ADRs already there; they may be the bloated ones this skill exists to stop.

**No map, or no ADR home in it:** propose `docs/adr/` with `YYYY-MM-DD-<slug>.md` naming and a routing line for the map — propose, don't impose. Dates, not numbers: they never collide across in-flight branches. No `template.md`, no index README.

## The shape

The shape is `references/example.md` — read it before writing. Its sections, and what each must hold:

- **Title** — a short noun phrase naming the choice, not a class.
- **Status** — one line; `proposed` when written (see Lifecycle).
- **Context** — two to five sentences of prose: what hurt, what constrained, what was at stake. When a future reader must apply a rule, one sentence defines its key term.
- **Decision** — one to three sentences in Y-statement form: in the context of <situation>, facing <concern>, we decided <this> over <that>, to achieve <quality>, accepting <cost>. The cost is not optional.
- **Alternatives** — one line each: the option and why it lost, at the decision's altitude — for a rule, rule-level alternatives, not ways to fix the triggering feature. None means it wasn't a decision.
- **Consequences** — three to six honest bullets: what gets easier, what gets harder, what future work must respect.

Under ~40 lines: a two-minute read.

## Altitude — mechanical rules

The ADR sits one level above the design doc — components and mechanisms, not classes and methods — because it outlives every rename.

- **No code blocks. No backticks.** A component may be named as a proper noun in prose; the moment you reach for a backtick you're at code altitude.
- **No annotations, signatures, or file paths.** Git has them; they rot on the first rename.
- **Context is prose, not a list.** A findings list is a review report, not the forces.
- **Consequences say what got easier or harder** — not which classes were deleted.

## Lifecycle

```
proposed → accepted (YYYY-MM-DD) → superseded by <link> | deprecated
```

- **proposed** — written at brainstorming, on the feature branch; editable in place (a circuit-breaker re-open, a reviewer's drift finding). Never a second ADR for the same decision.
- **accepted** — flipped by consolidating-docs at landing, dated. From here the status line is the one mutable field; everything else is superseded, not edited.
- **superseded / deprecated** — set on the old ADR when a new one reverses it or its feature is removed; always link the replacement.

A `proposed` ADR on the base branch means consolidation was skipped — flip it. Recording a past decision? Say so in Context and give the original date.
