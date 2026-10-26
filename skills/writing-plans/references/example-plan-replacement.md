# Example plan — the order, and why it is believed to work

The plan for a design that replaces a request-scoped dirty-marking collector with an explicit recalculation service. The design has the why, the shape and the
logic; this has the parts, the order and the evidence. Nothing the design says is repeated.

---

# One explicit product-recalculation service — implementation plan

Design: `docs/playbooks/designs/<date>-product-recalculation-service.md` · ADR: `<date>-adr-business-process-state-outside-technical-lifecycle-scope.md`

## Goal

Land the recalculation service and retire the collector, the event processor and the sequential discount loop, with the build and every scenario green after
each milestone.

## Parts involved

| Part                                       | What changes                                                     | Tests                                                                                   |
|--------------------------------------------|------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| Recalculation service (new)                | both operations; the batch logic moves here from the collector   | new `ProduktRecalculationServiceTest`; the architecture test gains the gateway rule     |
| Roles service                              | the discount fan-out hands its list to the batch; its loop goes  | `rabattnehmende_angebote_neuberechnen` and `neukunde_familienrabatt` features           |
| The six callers that mark offers dirty     | each hands over a loaded offer or a list instead of marking      | copy, Personendaten and Partnerdaten features; each caller's unit test                  |
| Mutation service                           | finalise flushes health declarations directly                    | `AngebotMutationServiceTest`                                                            |
| Collector, its service, event processor    | deleted                                                          | `ProduktCalculationCollectorServiceTest` deleted with them                              |

The six callers: copy, person data, partner data, occupation, contract takeover (`AbschlussService`) and offer creation (through `ProdukteFactory`).

## Order

### 1. The service, beside the collector

- *Builds* — both operations of the recalculation service. Nothing calls it yet. The gateway rule joins the architecture test, with today's callers recorded as
  its exceptions.
- *After it* — production behaviour is unchanged; the old mechanisms do all the work.
- *Proven by* — `ProduktRecalculationServiceTest`: one scenario per line of the batch rule (design, Logic), and for a single offer, a gateway failure leaves the
  offer unmodified.

### 2. The discount path

- *Builds* — the roles service hands the dependent offers to the batch and loses its loop. `ProduktService.calculateVersicherungsprodukte` becomes a one-offer
  batch, because other callers still need it.
- *After it* — the discount fan-out runs through the new service, in parallel. Every other caller still uses the collector; the two mechanisms coexist and never
  handle the same offer in one request.
- *Why here* — it is the riskiest change, the first parallel run of this path, and at this point only one caller depends on the new service.
- *Proven by* — the two discount features under the full suite, with a new assertion that each dependent's last editor is updated;
  `ProduktRecalculationServiceTest`: a changed receiving offer recalculates only itself.

### 3. Copy

- *Builds* — the copy flow hands its list of copies to the batch.
- *After it* — copy no longer marks; the collector still serves the single-offer callers.
- *Proven by* — the copy features; a new scenario in them: copies made by a customer advisor end the request with their health declarations synchronised.

### 4. The remaining callers

- *Builds* — person data collects the affected offers into one batch; partner data, occupation and contract takeover recalculate the loaded offer before
  finalise; offer creation recalculates after insert and the product factory stops marking.
- *After it* — nothing marks offers dirty. The collector is still wired and idle.
- *Proven by* — the Personendaten and Partnerdaten features, unchanged; each caller's unit test: it recalculates exactly its offer and still flushes the health
  declaration at finalise.

### 5. Delete the deferral

- *Builds* — removes the collector, its service and the event processor; finalise flushes health declarations directly; the architecture test's exception list
  is emptied.
- *After it* — one mechanism.
- *Why here* — the event processor also carries the health-declaration flush for every caller, so it can go only when no caller relies on the drain.
- *Proven by* — `mvn clean verify`; `AngebotMutationServiceTest`: a mutation by a non-advisor makes no health-declaration call; no reference to the removed
  types remains.

## Checked

- `markProdukteDirty` has exactly the six callers listed, in production and test-support code (`grep -rn markProdukteDirty`).
- `calculateVersicherungsprodukte` has three callers, one of them `AngebotLesenService`, which milestone 5 would otherwise break — so it stays, reimplemented.
- Each single-offer caller holds the loaded offer at the point where it marks today, so the single-offer operation needs no lookup (read all four sites).
- The discount fan-out never marks, and no marking caller triggers the fan-out before its request ends, so milestones 2–4 cannot recalculate one offer twice
  (read `RollenService` and the six callers).
- Both `finalisiereAenderung` overloads go through the event processor, and there is no third.
- No existing scenario asserts the dependents' last editor; without the new assertion in milestone 2 the editor passed to the batch would be untested.
- Baseline: `mvn clean verify` is green on the branch before any change.

## Open

- A batch with an unknown offer number fails as a whole or skips it — the design's open question. Milestone 1 builds fail-whole; if the answer is skip, one
  scenario and one line of the batch change.
