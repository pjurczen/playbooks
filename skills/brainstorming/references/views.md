# Views — which picture answers which question

Read before drawing. Mermaid, because GitHub, GitLab, Bitbucket and the IDE previews render it; never `dot` in a design.

| The reader asks                                                     | Draw                                                                                                                                                                            |
|---------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Which parts take part, who owns what, where does the new piece sit? | A structure `flowchart`: nodes typed by role (service, store, external system, adapter), edges labelled with what flows or who depends on whom. The first view of most designs. |
| In what order does it happen, and what happens when a step fails?   | A `sequenceDiagram` with the failure path, for integrations and for flows whose order is the point.                                                                             |
| What states can it be in, and what moves it?                        | A `stateDiagram-v2` of one entity, screen or job, for user-facing flows and long-running work.                                                                                  |
| What changes?                                                       | Before and after as two subgraphs of one structure diagram, or a table; the same names in both, the changed parts marked.                                                       |
| What is stored, and how does it relate?                             | An `erDiagram`; the migration is a rollout table.                                                                                                                               |
| In what phases does it land?                                        | A table: phase, what it delivers, what the old path still serves meanwhile.                                                                                                     |

Rules for every view:

- One question per diagram, stated in the caption line before it. A second diagram only for a different question.
- Nodes are the parts a team would draw on a whiteboard: modules, services, stores, external systems, the domain's aggregates. Mappers, factories, resolvers and
  the classes of the diff are not nodes unless `.claude/designs.md` says otherwise. More than about a dozen nodes means two diagrams.
- Every node says what kind of thing it is, by shape, subgraph or a key; every edge is directed and labelled with a verb phrase, never a bare "uses" and never a
  method name.
- Node labels at most four words; no signatures, no `<br/>` paragraphs, no styling directives.
- The prose after the view says why it is shaped so and what the picture cannot show; it never narrates the edges.
