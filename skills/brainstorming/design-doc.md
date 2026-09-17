# The design doc — shape, altitude, diagrams

Companion to `brainstorming`. A design has two readers. A teammate who has never opened the codebase reads the narrative layer — Problem, Approach, Shape — in two or three minutes. The implementer — a person, or a smaller model in another session — works from the precision layer, Contracts and Guarantees, plus the plan. Every section serves one of them. Length is whatever completeness needs; padding is what serves neither.

## Shape

```markdown
# <The change as a noun phrase>

Ticket: <id> · ADR: <link> · Initiative: <link>       ← each item only if it exists

## Problem          ─┐
## Approach          │ narrative layer
## Shape            ─┘
## Contracts        ─┐ precision layer
## Guarantees       ─┘
## Risks
## Out of scope
```

### Problem — narrative

One paragraph. What hurts, for whom, why now. No lists, no call chains, no numbered findings. If exploration disproved a hypothesis, the *test* that disproved it becomes a scenario in the plan; the hypothesis gets no paragraph.

### Approach — narrative

One paragraph stating what we will do, as an idea a teammate could repeat in a sentence. Then the one or two alternatives it beat, one line each with why they lost. If an ADR exists it owns the rationale: one line and a link, nothing restated.

### Shape — narrative

One sentence naming the question the diagram answers ("What replaces what?", "In what order do the groups run?"). One mermaid diagram (rules below). Then one bullet per component: its name, whether it is new / changed / removed, and its responsibility. Components and responsibilities — never call sites; the plan enumerates those.

### Contracts — precision

The public signatures this design introduces or changes, one fenced block per type: interfaces, records, enums, sealed hierarchies, method signatures with a one-line javadoc stating the semantics, and the annotations that carry semantics (scope, transactionality). A changed existing method: its signature plus one line saying what changes.

Not here: method bodies, private members, fields, constructors, boilerplate annotations (Lombok, `@Inject`). A repeating pattern is shown once — "one marker interface per category, same pattern".

```java
// yes — a contract: what the implementer must match, what a reviewer can check
@DomainService @Dependent @Transactional
public class ProduktRecalculationService {
   /** Recalculates one already-loaded offer in memory. No reload, no flush. */
   public void recalculate(Angebot angebot, ProduktCalculationContext context);
}

// no — a body: the implementer's job, and it rots before the plan is written
public void recalculate(Angebot angebot, ProduktCalculationContext context) {
   produktGateway.calculate(angebot, context);
   sideEffectReconciler.reconcile(angebot);
}
```

### Guarantees — precision

G1 … Gn: three to six numbered properties the design holds — ordering, freshness, parity, a single entry point, an invariant callers must respect. The plan's scenarios cite them by number. This is the section a team review should attack.

### Risks — narrative

What could go wrong with the approach itself. Execution risks — ordering, hidden callers, big-bang compile steps — belong to the plan.

### Out of scope

What this deliberately does not do, one line each.

## Diagrams — mermaid

Mermaid renders natively on GitHub, GitLab, Bitbucket and in the JetBrains Markdown preview. Never `dot` in a design; that notation is for skill files, read by the agent.

- `flowchart` for structure, flow, before → after. `sequenceDiagram` for ordering across time. `classDiagram` only for a type-hierarchy change. Nothing else.
- One diagram answers one question, and the sentence before it names the question.
- At most ~12 nodes and 2 subgraphs (before / after). Node labels ≤ 4 words, edge labels ≤ 3 words: names and short verbs. No signatures, no `<br/>` paragraphs, no instance numbers, no styling directives.
- Required when the change alters how components interact — a new flow, a moved responsibility, a removed mechanism. Skip it for a change contained in one component. A second diagram is allowed when a section cannot be understood without one; it answers its own named question.
- The prose after the diagram explains it. Neither is self-sufficient.

## Initiative designs — `docs/playbooks/initiatives/`

Optional. Only when the work will not fit one design → plan → execute cycle *and* the slices share a target architecture. Most features never produce one.

Same shape, with three differences: Shape's diagram is the target architecture; Contracts are the shared ones every slice builds on; and a **Slices** table (slice · what it delivers · status: planned / in progress / landed) is the only place status lives. Guarantees are architecture-level. There are no behaviours — slice designs carry their own Guarantees, slice plans carry scenarios.

Each slice's design links it (`Initiative:` in the header) and covers only its delta. The initiative commits on slice 1's branch with slice 1's design and is reviewed at the same gate. Its target architecture is usually the ADR-worthy decision: written `proposed` with the initiative, promoted when slice 1 lands.

It is a working doc. When a slice diverges, **edit** the initiative so it stays true — never add a "the implementation diverges" callout. consolidating-docs leaves it alone until every slice in its table has landed.

See `example-design.md` beside this file for a real design at the right altitude, and `../writing-plans/example-plan.md` for its plan.
