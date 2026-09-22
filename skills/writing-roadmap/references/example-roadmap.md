# Example roadmap

The roadmap for `../../brainstorming/references/example-design-initiative.md`. Slices, order, exit criterion; nothing a
slice plan will own.

---

# Event-driven report rendering — roadmap

Initiative: `docs/playbooks/initiatives/<date>-event-driven-rendering.md` · ADR:
`<date>-adr-render-on-change-not-on-schedule.md`

## Exit criterion

Every report type is rendered by the queue, the nightly scheduler and the routing table are deleted, and a change to any
report is visible within the queue's delivery bound.

## Slices

| # | Slice                                                | Delivers                                                                                                                                        | Depends on | Status      |
|---|------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|------------|-------------|
| 1 | Walking skeleton: the balance-sheet type             | queue, one worker, the definition emitter, routing table with one migrated type; balance sheets re-render within minutes of a definition change | —          | landed      |
| 2 | Source-change emitters for the two high-volume types | sales and inventory reports re-render on source change; proves idempotency and throughput under the largest daily volume                        | 1          | in progress |
| 3 | Version-check adapters                               | the two sources without change detection emit on a periodic version check; their types migrate                                                  | 1          | planned     |
| 4 | The long tail                                        | every remaining type migrated in batches of ten, each batch a configuration change after its emitters ship                                      | 2, 3       | planned     |
| 5 | Delete the scheduler                                 | nightly job, routing table and scheduler-only code removed; operations runbook updated                                                          | 4          | planned     |

## Order

Slice 1 is the skeleton: it carries real traffic for one low-volume type and proves the queue, a worker, the routing
table and a revert end to end. Slice 2 is the riskiest: the high-volume types are where at-least-once delivery and
idempotent renders either hold or don't, and changing the request contract is still cheap. Slices 2 and 3 are
independent and may run in parallel worktrees. Slice 4 is bulk migration with no new design. Slice 5 removes coexistence
and is only possible once nothing depends on the scheduler.

## Open questions

- Batch size for slice 4 — operations, once slice 2 has produced a day of throughput numbers.
- Whether slice 3's version check needs its own dead-letter policy — before slice 3's design.
