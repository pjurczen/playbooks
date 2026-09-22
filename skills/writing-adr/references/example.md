# Example ADR

The shape every ADR takes, on a real decision: a rule stated without the feature that surfaced it, alternatives at the rule's altitude, and the cost accepted.

---

# Business-process state outside technical lifecycle scope

**Status:** accepted (2026-09-16)

## Context

During discovery and design of product recalculation, we found that pending domain work was accumulated in a request-scoped bean and executed at the end of the request. This made the business-process boundary depend on a technical lifecycle, hid the pending work and its finalisation, and made the process difficult to reuse from non-request entry points. The case exposed a general problem: request scope is appropriate for technical context, but not for owning business-process state.

Here, business-process state means pending work, process scope, progress, completion, retry, or outcome. It is distinct from technical request context such as authentication, correlation, or locale.

## Decision

For domain processes that coordinate or defer work, business-process state and pending domain actions must not be accumulated in request-scoped or analogous technical lifecycle scopes. The caller must pass the process scope explicitly to an application use case, which orchestrates the process without retaining state in the request lifecycle. Domain services may encapsulate domain rules and request scope may carry technical context only, accepting that every caller now passes the scope of its work explicitly and that batch callers must name their items.

## Alternatives

- Track pending domain work in request-scoped beans — rejected because request completion becomes an implicit business-process boundary and couples the process to synchronous request handling.
- Move the accumulation to a longer-lived technical scope — rejected because changing the scope does not change the ownership problem; technical lifecycle scopes are not business-process models.
- Keep the existing process-specific orchestration and optimise it in place — rejected because the work scope and finalisation remain implicit, making transaction handling, reuse, and parallelisation harder to control.

## Consequences

- Request completion does not implicitly trigger or finalise deferred or accumulated business work.
- Business-process boundaries, inputs, and batch scope are visible at the call site.
- The same process can be invoked from requests, commands, batch jobs, or other adapters without scope-bound tracking.
- Stateless application services become the natural orchestration mechanism; statelessness follows from explicit process scope rather than being the primary decision.
- Request-scoped beans remain valid for technical context, but not for business-process state.
- A process that must survive beyond one invocation requires an explicit process model, durable work item, or message; this ADR does not prescribe which mechanism to use.
