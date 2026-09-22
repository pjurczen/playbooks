# The design doc — kinds of work, sections, altitude

The design doc is the trace of brainstorming's five stages: Problem and Diagnosis are stages one and two, Approach and
Decisions stage three, Design, Contracts and Guarantees stage four, the rest stage five. A design has two readers. A
teammate who has never opened the codebase reads the narrative — Problem, Diagnosis, Approach, Decisions, Design — in a
few minutes. The implementer — a person or a model in another session, with none of the brainstorming conversation —
works from the precision layer, Contracts and Guarantees, plus the plan. Each layer stays pure: no rationale inside
Contracts, no declarations inside Approach. Length is whatever completeness needs; padding is what serves neither.

## Sections

The shape is the example for your kind (`example-design-<kind>.md`). Header: Status (`draft` | `approved`), then Ticket,
ADR and Initiative links where they exist. Sections in order; what each must hold:

### Problem — narrative

One paragraph (an initiative may take three): what hurts, for whom, why now; for greenfield work, who it's for and the
constraints. The need, not the requested solution. No lists, no call chains, no findings. End with a sentence starting "
Done means" — the observable outcome.

### Diagnosis — narrative

One paragraph: the cause of the problem in structural terms a reader can check — which mechanisms, data or boundaries
produce the pain, and what constrains the fix. Name components, not methods; no call chains, no numbered findings. This
is the sentence everything after it hangs on, and the one a reviewer should be able to disagree with. A hypothesis
exploration disproved becomes a scenario in the plan, not a paragraph here.

### Approach — narrative

One paragraph stating what we will do, as an idea a teammate could repeat in a sentence. Then the one to three
alternatives it beat, one to three sentences each: what it was, the trade-off that killed it, when it would become
right. If an ADR exists it owns the rationale: one line and a link. When implementation diverges from the approved
design, edit Design and Contracts so they stay true and add one line here starting "Deviation:" — never an amendment.

### Decisions — narrative

The decisions this design makes, one line each: the decision, the alternative rejected, why. Most are below
writing-adr's bar and live here; the ones that pass it link to their ADR instead of restating it. No decision hides in
prose elsewhere, and no resolved decision sits under Open questions.

### Design — narrative

The views a reader needs to understand the problem and the solution — usually one to three, each opening with the
question it answers; `design-views.md` says which view answers which question. Then one bullet per component: name,
new / changed / removed, responsibility. Components and responsibilities, not call sites; the plan enumerates those.

The kind of work falls out of the chosen approach, and it says which views to draw and what a contract is here. Add a
row when a kind is missing.

| Kind                                | Views                                    | Contracts are                          | Typical guarantees                        |
|-------------------------------------|------------------------------------------|----------------------------------------|-------------------------------------------|
| Feature in an existing codebase     | structure; behaviour when a flow changes | signatures, endpoints                  | parity for untouched behaviour            |
| Greenfield system or service        | context first, then structure            | the external surface: API, CLI, config | the properties the surface promises       |
| Replacement or refactor             | structure, before → after                | the changed declarations               | invariants preserved, parity              |
| Integration with an external system | behaviour, with the failure paths        | messages, endpoints                    | delivery semantics, timeout bounds        |
| Data-model change                   | data; rollout                            | schema, migration steps                | no data loss; old readers keep working    |
| User-facing flow                    | state, process                           | screens, states, events                | every state reachable and exitable        |
| Infrastructure or deployment        | context; rollout                         | resources, configuration               | a rollback path; the downtime claim       |
| Cross-cutting policy                | structure                                | the rule as an interface               | applies everywhere, and how it's enforced |
| Initiative (`initiative-design.md`) | context, structure, rollout              | the shared contracts                   | hold at every intermediate state          |

**The mechanism, when it is the decision.** Most designs need no code: the contracts fix the surface and a competent
implementer fills the body. But when an algorithm's complexity, a concurrency scheme, a state machine or a data
structure *is* the solution — when an implementer given only the contracts would plausibly build something materially
different — the design carries it here: pseudo-code or a minimal sketch, as long as it needs to be to remove that
ambiguity and no longer, with the property it buys stated as a guarantee. Never code that is merely the obvious way to
implement a decision made elsewhere; that is what rots in a design.

### Contracts — precision

The surface the rest of the world sees, at the altitude of a declaration: public signatures with a one-line doc stating
semantics including failure behaviour; endpoints with request and response shapes; schemas and migration steps;
configuration keys and flags; screens, states and the events between them. Annotations that carry semantics (scope,
transaction) stay; bodies, private members, fields and boilerplate go. A changed existing thing: its declaration plus
one line saying what changes. A repeating pattern is shown once.

**Structural rules** — three to five, derived from the Design view, that the gates can check: which components may depend on which; who owns which responsibility; length or complexity limits where they differ from `.claude/gates.md`. Milestone one of the plan wires any rule the map doesn't enforce yet.

```java
// a contract: what the implementer must match, what a reviewer can check
@Transactional
public class ProduktRecalculationService {
   /** One already-loaded offer, recalculated in memory. No reload, no flush; a gateway failure propagates and leaves the offer unmodified. */
   public void recalculate(Angebot angebot, ProduktCalculationContext context);
}
```

```
POST /reports/{name}/render  → 202 { jobId }                 an endpoint contract
                             → 409 if a render for {name} is already queued
```

### Guarantees — precision

G1 … Gn: three to seven numbered properties the design holds, each one sentence a single test can falsify, in the form "
when X, then Y". A guarantee no scenario could prove is a risk, and moves there. The last one states what must *not*
change — "none" if nothing. The plan's scenarios cite these numbers; this is the section a team review should attack.

### Assumptions

Defaults taken without asking, one line each; if a reader disagrees with a line, the design changes. "None." when there
are none — never omit the section.

### Open questions

One line each: the question, who answers it, by which milestone. "None." when there are none — never omit the section.
An open question the design doesn't record becomes a silent guess.

### Risks — narrative

What could go wrong with the approach itself. Ask whether compatibility, migration, rollout or observability applies; if
so it is a risk or an out-of-scope line, never an omission. Execution risks — ordering, hidden callers, big-bang compile
steps — belong to the plan.

### Out of scope

What this deliberately does not do, one line each.
