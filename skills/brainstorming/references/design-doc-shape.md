# The design doc — what it holds, and at what altitude

A design explains how a problem gets solved, to a teammate who will review it and present it and has not opened the code. It works when that reader can, after
one read, repeat the solution, argue with its decisions and say what it costs. The implementer in another session reads the same document and then the plan;
what only the implementer needs — every unit to touch, the order, the tests — belongs to the plan.

## The test for every line

Does the reader learn something here that is not already on the page and that they could not see by opening the code? If not, it goes. Three rules follow:

- **One fact, one place.** A decision, a rule or a consequence is stated once, in the section that owns it. Another section that needs it names it and moves on.
- **A section exists when it has content.** Problem, Diagnosis, Approach and Architecture always; the others only when there is something to say. No "None."
  lines, and nothing written because the list has a heading for it.
- **Concrete before prose.** A rule as pseudo-code or a table, a surface as a signature, a structure as a diagram. Prose carries what those cannot: the why.

Length follows the work. A bigger feature takes more pages; an unfocused design is cut, whatever its size.

## Sections

The shape is the example for your kind (`example-design-<kind>.md`). Header: Status (`draft` | `approved`), then Ticket, ADR and Initiative links where they
exist. Sections in order:

### Problem

One paragraph (an initiative may take three): what hurts, for whom, why now; for greenfield work, who it's for and the constraints. The need, not the requested
solution. No lists, no call chains, no findings. End with a sentence starting "Done means" — the observable outcome.

### Diagnosis

One paragraph: the cause of the problem in structural terms a reader can check — which mechanisms, data or boundaries produce the pain, and what constrains the
fix. Name components, not methods. This is the sentence everything after it hangs on, and the one a reviewer should be able to disagree with.

### Approach

One paragraph stating what we will do, as an idea a teammate could repeat in a sentence. Then the alternatives seriously considered, usually one or two: what it
was, the trade-off that killed it, when it would become right. If an ADR exists it owns the rationale: one line and a link. When implementation diverges from
the approved design, edit the design so it stays true and add one line here starting "Deviation:" — never an amendment.

### Decisions

The choices inside the approach that a reviewer might make differently, most consequential first: the decision, what was rejected, why. A choice nobody would
contest is not a decision, and neither is a note that something stays as it is. The ones that pass writing-adr's bar link to their ADR instead of restating it.

### Architecture

Which parts of the system take part, who owns what, and where the new piece sits: one view, a second only when it answers a different question
(`design-views.md`). Then one bullet per component: name, new / changed / removed, what it is responsible for and what it must not do. Components are what a
teammate would draw on a whiteboard — modules, services, stores — with the class name in brackets where it helps to find one. Mappers, stubs, build files and
test support are the plan's.

### Logic

What gets built: the rules, algorithms, state machines and mappings that carry the solution. Each appears once, in its most concrete form — pseudo-code, a
decision table, a state diagram — under the name of the component that owns it. Write it at the level of the rule: something a domain expert could check and a
test could follow branch by branch. No language syntax, no error plumbing, and nothing that is merely the obvious way to implement a contract; the body stays
the implementer's. Work that only moves or wires things has no Logic section.

### Contracts

The surface others build against, where it is new or changed: public signatures with a one-line doc stating semantics and failure behaviour; endpoints with
request and response shapes; schemas and migration steps; configuration keys; states and the events between them. Bodies, private members and unchanged
declarations stay out. A repeating pattern is shown once.

When the architecture implies a structural rule a gate can check — who may depend on whom, who owns what — state it here in one line; milestone one of the plan
wires any such rule `.claude/gates.md` doesn't enforce yet.

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

### Consequences

What the solution changes and costs beyond its goal, most serious first: behaviour that changes for users or callers, what stops working, what rollout or
operation now needs, what could go wrong with the approach, what a reader would expect it to cover and it does not. Close with what stays the same when a reader
would worry about it. A rejected alternative is not repeated here as something left out.

### Open questions

Only what someone outside the session must answer: the question, who answers it, what it blocks. What the code can answer is looked up; what the user can answer
is asked during brainstorming; neither is written down as an assumption.

## Kinds of work

The kind falls out of the chosen approach, and it says which view to draw and what logic and contracts usually are. Add a row when a kind is missing.

| Kind                                | Views                                   | Logic is usually                    | Contracts are                          |
|-------------------------------------|-----------------------------------------|-------------------------------------|----------------------------------------|
| Feature in an existing codebase     | structure; behaviour if order matters   | the new rule or algorithm           | signatures, endpoints                  |
| Greenfield system or service        | context first, then structure           | the core rules of the domain        | the external surface: API, CLI, config |
| Replacement or refactor             | structure, before → after               | what the new path does differently  | the changed declarations               |
| Integration with an external system | behaviour, with the failure paths       | retry, timeout, idempotency         | messages, endpoints                    |
| Data-model change                   | data; rollout                           | migration and backfill              | schema, migration steps                |
| User-facing flow                    | state, process                          | transitions and validation          | screens, states, events                |
| Infrastructure or deployment        | context; rollout                        | failover and rollback               | resources, configuration               |
| Cross-cutting policy                | structure                               | the rule itself                     | the rule as an interface               |
| Initiative (`initiative-design.md`) | context, structure, rollout             | the coexistence mechanism           | the shared contracts                   |
