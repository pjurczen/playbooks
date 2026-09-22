---
name: writing-adr
description: Use when brainstorming settles an architecturally significant choice, or when the user asks to record a decision, to write a short Nygard-style ADR at design altitude in the repo's ADR home.
---

# Writing ADRs

An Architecture Decision Record captures one decision, the forces behind it, the options rejected, and what it costs, so
that future developers understand why the codebase is shaped the way it is. It is written when the decision is made, not
after the code exists. This skill is the only place ADR text is written; consolidating-docs promotes `proposed` to
`accepted` at landing but never writes one.

## When this runs — and when to skip

- **Fired by brainstorming** after design approval — the normal path: the decision is fresh and no code exists yet.
- **Fired by writing-plans** (mid-pipeline entry) or **consolidating-docs** (fallback at landing) — from the design doc,
  never the diff.
- **Invoked directly** — "ADR this", "write down why we chose X".

Skip when:

- It isn't worth recording (below); most decisions aren't.
- It already has an ADR: `proposed` → edit in place; `accepted` → supersede only if the decision is being reversed.
- "Why did we choose X?" is a read — find the ADR and answer.

## Worth recording

The deciding test: **state the decision without naming the feature that triggered it.** If nothing is left, it is a
design decision: it lives in the design doc, and its one durable sentence goes to the architecture doc. An ADR is
specific in the choice and system-wide in scope — "use Prisma", not "use an ORM".

| Category                                | Examples                                                                            |
|-----------------------------------------|-------------------------------------------------------------------------------------|
| Technology choices                      | Framework, language, database, cloud provider                                       |
| Architecture rules and patterns         | Event-driven vs request/response, CQRS, where business-process state may live       |
| Boundaries, contracts, APIs             | REST vs GraphQL, versioning strategy, module boundaries other modules build against |
| Data modelling                          | Schema design, normalisation, caching strategy                                      |
| Infrastructure and security             | Deployment model, CI/CD, auth strategy, secret management                           |
| Testing and process                     | Test framework, E2E vs integration balance, branching strategy                      |
| Deliberate trade-offs with lasting cost | Accepting a known coupling, keeping a synchronous call that could be lazy           |
| Reversals of any of the above           | Recorded as a supersede                                                             |

**Not worth recording** — design-doc content, or a commit message:

- A refactoring outcome: "replace X and Y with Z".
- An internal algorithm, module placement, naming, formatting.
- Removing a mechanism — unless stated as the rule that keeps it out.
- Anything true of only one feature.

A real ADR also constrains work beyond this feature, is hard to reverse, and came from a real choice between approaches
a competent engineer might have picked. One per feature is the norm; most produce none.

## Rule or instance

The approach brainstorming picked is usually an instance. If it instantiates a rule the team is adopting, the rule is
the decision and the feature is the evidence in Context. If it is itself a system-level choice — a database, a
platform — record the choice. Neither: no ADR. An ADR records a decision that was taken; someone who sees a wider rule
in a design proposes a *new* ADR, status `proposed`, rather than rewriting the record.

## Conventions come from the map, not from this skill

Read `.claude/documentation.md` first. It owns where ADRs live (several homes → pick by the feature's domain; ask if
unclear), the filename pattern, the language — prose *and* headings — any index to update (never create one the map
doesn't mention), and any status vocabulary. Follow the repo's naming and language, and *this skill's* shape — not the
shape of the ADRs already there; they may be the bloated ones this skill exists to stop.

**No map, or no ADR home in it:** propose `docs/adr/` with `YYYY-MM-DD-<slug>.md` naming and a routing line for the
map — propose, don't impose. Dates, not numbers: they never collide across in-flight branches. No `template.md`, no
index README.

## The shape

The shape is `references/example.md` — read it before writing: Title, Status, Context, Decision, Alternatives,
Consequences. Under ~400 words: a two-minute read.

## What makes a good ADR

**Do**

- **Be specific** — "Use Prisma ORM", not "use an ORM"; a title that names the choice, not a class.
- **Record the why** — Context is two to five sentences of the forces: what hurt, what constrained, what was at stake.
  When a future reader must apply a rule, one sentence defines its key term.
- **State the decision as a Y-statement** — in the context of <situation>, facing <concern>, we decided <this>
  over <that>, to achieve <quality>, accepting <cost>. The cost is not optional.
- **Include rejected alternatives** — one line each, the option and why it lost, at the decision's altitude: for a rule,
  rule-level alternatives, not ways to fix the triggering feature.
- **State consequences honestly** — three to six bullets: what gets easier, what gets harder, what future work must
  respect.
- **Stay at design altitude** — components and mechanisms as proper nouns in prose. The ADR outlives every rename.
- **Use present tense** — "we use X", not "we will use X".
- **Keep it short** — under ~400 words, a two-minute read; wrapping style is the repo's, length is not.

**Don't**

- **No code blocks, backticks, annotations, signatures or file paths** — git has them; they rot on the first rename.
- **No findings list as Context** — that's a review report, not the forces.
- **No diff summary as Consequences** — "removed A, B, C" says what changed, not what got easier or harder.
- **No essays** — Context over ten lines is a design doc.
- **Don't omit alternatives** — "we just picked it" means it wasn't a decision.
- **Don't copy the neighbours** — the ADRs already in the directory set the naming and language, not the shape.
- **Don't write a second ADR for a drifted `proposed` one** — edit it in place.
- **Don't backfill without marking it** — recording a past decision, say so in Context and give the original date.

## Lifecycle

```
proposed → accepted (YYYY-MM-DD) → superseded by <link> | deprecated
```

- **proposed** — written at brainstorming, on the feature branch; editable in place (a circuit-breaker re-open, a
  reviewer's drift finding).
- **accepted** — flipped by consolidating-docs at landing, dated. From here the status line is the one mutable field;
  everything else is superseded, not edited.
- **superseded / deprecated** — set on the old ADR when a new one reverses it or its feature is removed; link the
  replacement.

A `proposed` ADR on the base branch means consolidation was skipped — flip it.
