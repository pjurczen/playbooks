# Example ADR

A real decision at the altitude `writing-adr` asks for. Match this altitude — not the altitude of whatever ADRs your repo already has.

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
