# Example ADR — a real decision at the right altitude

A decision from an insurance-offer system, rewritten from a 60-line ADR full of class names, annotations and a five-item findings list into the shape `writing-adr` produces. Match this altitude — not the altitude of whatever ADRs your repo already has.

---

# Product recalculation as one explicit domain service, no request scope

**Status:** accepted (2026-09-16)

## Context

After the move to the mutation orchestrator, the offer context had two overlapping ways to recalculate products: a request-scoped collector that marked offers dirty and flushed them at request end, and a sequential discount recalculation that flushed once per dependent offer. The deferral almost never batched — only two callers ever marked more than one offer — and the main command path bypassed it entirely, so the "we defer N offers" mental model was wrong where it mattered. Parallelising the sequential path had been abandoned over transaction-scope clashes.

## Decision

We replace both mechanisms with one explicit, stateless domain service. It recalculates either a single already-loaded offer in memory, or an explicit batch — discount-giving offers first, then a three-phase run: read, compute on workers, reconcile and finalise on the main thread. We chose this over keeping either existing path to get one predictable recalculation route and to unlock the parallel run the old design blocked, accepting that batch callers must now name their offers explicitly.

## Alternatives

- Keep the request-scoped collector, drop the sequential path — rejected: the deferral had no real batching benefit and hid the flush point.
- Keep the sequential path and fix its parallelism in place — rejected: per-element mark-and-finalise is what caused the transaction clash; parallelism needs the in-memory/finalise split.

## Consequences

- One recalculation path; the request-scoped collector and its event processor are gone.
- Batch boundaries are visible at the call site instead of hidden in request state.
- Discount fan-out is one-directional: mutating a discount-giving offer recalculates its dependents, never the reverse. New callers must respect this.
- Health-declaration sync stays synchronous; the lazy variant from the earlier ADR remains unimplemented.

---

## What got cut from the original, and why

- **A five-item findings list** became two sentences of context. Findings are review output; an ADR needs the forces that motivated the decision.
- **Annotations, method signatures, class names** are gone. The code and git have them; they rot on the first rename. The title now names the decision, not the class.
- **A "cleanup, behaviour unchanged" paragraph** is gone. Unchanged behaviour is not a decision; it's a commit-message note.
- **"Removed: A, B, C, D, E"** became what got easier or harder. A list of deleted classes is a diff summary.
- **A References section** collapsed: the one live constraint moved into Consequences; the rest was context already covered. Cross-links stay only for supersedes / depends-on.
- **Kept on purpose:** the one-directional fan-out invariant — the most durable line in the original — promoted from a finding to a consequence that constrains future callers.
