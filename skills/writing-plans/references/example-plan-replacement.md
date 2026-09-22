# Example plan — exact, and nothing the design already says

The plan for `../../brainstorming/references/example-design-replacement.md`. Read the two together: the design has the
why, the shape and the contracts; this has the work. Every table row names the class and method the implementer must
touch; every scenario names where it lives and which Guarantee it proves.

---

# One explicit product-recalculation service — implementation plan

Design: `docs/playbooks/designs/<date>-product-recalculation-service.md` · ADR:
`<date>-adr-business-process-state-outside-technical-lifecycle-scope.md`

## Goal

Land ProduktRecalculationService and retire the collector, the event processor and the sequential discount loop with
every existing scenario green.

## Changes

| Unit                                                                                                                                     | Change  | What, exactly                                                                                                                                                                                                                                       |
|------------------------------------------------------------------------------------------------------------------------------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `ProduktRecalculationService` (+ `ProduktRecalculationServiceTest`)                                                                      | new     | `recalculate(Angebot, ProduktCalculationContext)` and `recalculateAngebote(List<AngebotNr>, Bearbeiter)`; batch logic lifted from `ProduktCalculationCollectorService.calculateDirtyAngebote`                                                       |
| `AngebotMutationService`                                                                                                                 | changed | both `finalisiereAenderung` overloads call `gesundheitsdeklarationCollector.updateGesundheitsdeklarationen()` directly                                                                                                                              |
| `RollenService`                                                                                                                          | changed | `calculateRabattnehmendeAngebote` delegates to `recalculateAngebote`; `aktualisiereAngebote` and its FIXME deleted                                                                                                                                  |
| `ProduktService`                                                                                                                         | changed | `calculateVersicherungsprodukte` reimplemented as `recalculateAngebote(List.of(nr), bearbeiter)` — it has three callers (`RollenService.propagiereRollenAufAngebot`, `RollenService.aktualisiereAngebote`, `AngebotLesenService.hole`), so it stays |
| `AngebotKopierenServiceTest`, `RollenServiceTest`, `AngebotMutationServiceTest`                                                          | changed | retargeted from collector / event processor to the service                                                                                                                                                                                          |
| `ProduktCalculationCollector`, `ProduktCalculationCollectorService`, `AngebotKvEventProcessor`, `ProduktCalculationCollectorServiceTest` | deleted | in milestone 5, after the caller gate                                                                                                                                                                                                               |

Call sites:

| Site                                                                  | From                                                                 | To                                                                                                                                           |
|-----------------------------------------------------------------------|----------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| `RollenService.calculateRabattnehmendeAngebote`                       | loop: `calculateVersicherungsprodukte` per dependent, one flush each | `recalculateAngebote(dependents, bearbeiter)`; bearbeiter reaches the two-arg finalise so each dependent's `letzterBearbeiter` still updates |
| `AngebotKopierenService.kopiereAngebote`                              | `markProdukteDirty` per copy + `calculateDirtyAngebote()`            | `recalculateAngebote(copiedNrs, bearbeiter)`                                                                                                 |
| `AngebotPersonendatenService.onInteressentPersonendatenChanged`       | `markProdukteDirty` per offer + one `processEvents()`                | collect affected nrs → one `recalculateAngebote`                                                                                             |
| `AngebotPersonendatenService.aktualisierePartnerdaten` / `setzeBeruf` | `markProdukteDirty`                                                  | `recalculate(angebot, context)` before finalise                                                                                              |
| `AbschlussService` (Bestandespolice übernehmen)                       | `markProdukteDirty` + `processEvents()` + reload products            | `recalculate(angebot, context)`, no reload                                                                                                   |
| `ProdukteFactory.neueProdukte`                                        | `markProdukteDirty`                                                  | nothing; `AngebotErstellenService` calls `recalculate` after `insertAngebot`                                                                 |
| `AngebotMutationOrchestrator`                                         | inline `produktGateway.calculate`                                    | unchanged                                                                                                                                    |

`ProduktCalculationContext` is built everywhere as
`new ProduktCalculationContext(rabattgebendeOapService.ermittleRabattgebendeOap(angebot.getProdukte()))`.

## Behaviours to verify

- G2 · `rabattnehmende_angebote_neuberechnen.feature` — given one discount-giving and two receiving offers, when the
  giving one changes, then all three are recalculated, giving first, and each dependent's last-editor is updated.
- G3 · `ProduktRecalculationServiceTest` — given the same family, when a receiving offer changes, then only that offer
  is recalculated.
- G4 · new scenario in the copy feature — given a Kundenberater copies a consultation's offers, when the request ends,
  then every copy's health declaration is synchronised.
- G4 · `AngebotMutationServiceTest` — given a non-Kundenberater mutates an offer, when finalised, then no
  health-declaration call is made.
- G6 · `neukunde_familienrabatt`, copy, Partnerdaten and Personendaten features — pass unchanged.
- Edge · `ProduktRecalculationServiceTest` — an empty batch makes no gateway call and finalises nothing.
- Edge · Partnerdaten, Beruf and Abschluss unit tests — each recalculates exactly its offer and still flushes GD at
  finalise.

## Milestones

| # | Milestone                    | Delivers                                                                                                                                                | Done when                                                                                     | Biggest risk                                                  |
|---|------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|---------------------------------------------------------------|
| 1 | Service beside the collector | both operations, unit-tested; nothing wired                                                                                                             | `ProduktRecalculationServiceTest` green; reactor compiles                                     | none — additive                                               |
| 2 | Discount path                | `calculateRabattnehmendeAngebote` delegates to the batch; `aktualisiereAngebote` deleted; `calculateVersicherungsprodukte` reimplemented                | `rabattnehmende_angebote_neuberechnen` + `neukunde_familienrabatt` green under the full suite | first parallel run of this path — one scenario proves nothing |
| 3 | Copy                         | `kopiereAngebote` hands its list to the batch; copy-with-Kundenberater scenario added                                                                   | copy features green; copies end the request GD-synchronised                                   | none                                                          |
| 4 | Remaining sites              | Personendaten to the batch; Partnerdaten, Beruf, Abschluss inline; `AngebotErstellenService` recalculates after insert; `ProdukteFactory` stops marking | those Cucumber and unit suites green                                                          | two mechanisms coexist until milestone 5                      |
| 5 | Delete the deferral          | collector, its service and the event processor removed; finalise flushes GD directly                                                                    | `mvn clean verify` green; no references to the removed types                                  | a hidden caller — grep every deleted type first               |

Each milestone starts with its Behaviours red.

## Execution risks / open questions

- Milestones 2–4 leave both mechanisms alive; keep each milestone's scenario set broad enough to exercise the
  coexistence window.
- Check `AngebotLesenService` and test-support code for callers of the deleted types before milestone 5 — the design's
  caller list came from mutation services only.
- If no scenario asserts the dependents' `letzterBearbeiter` today, add the assertion in milestone 2; otherwise the
  threaded bearbeiter is untested.

Stop and ask if:

- a contract in the design doesn't match the code as found — a third `finalisiereAenderung` overload, a different
  `Bearbeiter` type.
- milestone 2's scenarios can't go green without changing the product gateway contract (out of scope in the design).
- any deleted type still has a production caller at milestone 5 that isn't in the call-site table.
