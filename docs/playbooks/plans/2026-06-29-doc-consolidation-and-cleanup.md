# Doc consolidation & cleanup — implementation plan

## Goal

Add a `consolidating-docs` skill (and its `.claude/documentation.md` map) that graduates durable decisions out of design/plan files into the repo's real docs and deletes the husks, and relocate `followups.md` to `docs/`.

## Decomposition

- **`.claude/documentation.md` (artifact + format)** — the repo's doc-maintenance guide and routing map. Lives at a known path so any consumer can read it. Not shipped by the plugin; generated per-repo by the bootstrap flow. Its *format* is specified inside the skill.
- **`consolidating-docs` skill** — the engine: read map → extract durable content → route per map → capture-then-delete → one commit. Two entry points (fired by finishing-branch with feature scope; invoked manually for a backlog sweep) plus the bootstrap flow when the map is absent. Depends on `.claude/documentation.md`.
- **finishing-branch integration** — invokes the skill on the merge and PR paths before executing, skips on keep/discard. Depends on `consolidating-docs`.
- **using-playbooks integration** — advertises the skill (library + when-to-invoke table) and adds a light pointer sending any doc-touching task to the map. Depends on `consolidating-docs`, `.claude/documentation.md`.
- **followups.md relocation** — move the durable backlog from `docs/playbooks/followups.md` to `docs/followups.md`; touches brainstorming, writing-plans, executing-plans, README, DESIGN.

## Behaviours to verify

- Finishing a branch that has design/plan files via merge or PR reaches `consolidating-docs` before the merge/push; choosing keep or discard does not.
- When `.claude/documentation.md` is absent, the skill offers to bootstrap it; if the user declines, design/plan files are left untouched.
- A durable decision with no home in the map is surfaced to the user — never guessed, never silently dropped.
- A husk file is deleted only after its durable content has been committed to a destination doc.
- Invoking the skill with no feature context offers a backlog sweep over `designs/` and `plans/`.
- After relocation, nothing in the repo references `docs/playbooks/followups.md`; all references point to `docs/followups.md`.
- Dogfood: loading the plugin and running a finish flow surfaces `consolidating-docs` at the right moment without prompting.

## Milestones

1. **Relocate `followups.md` to `docs/followups.md`.**
   Update every reference (brainstorming, writing-plans, executing-plans, README, DESIGN).
   Done when: a repo-wide search for `docs/playbooks/followups.md` returns nothing and all mentions resolve to the new path.

2. **Author the `consolidating-docs` skill.**
   Write `skills/consolidating-docs/SKILL.md`: the `.claude/documentation.md` format spec, the engine, both entry points, the bootstrap flow, and the capture-then-delete invariant — following the repo's skill conventions (frontmatter, when-to-skip carve-out, ~150-line target).
   Done when: a senior reader can follow the skill end-to-end and both entry points + bootstrap are unambiguous.

3. **Wire it into the lifecycle.**
   `finishing-branch` invokes the skill on merge/PR (skips keep/discard); `using-playbooks` adds it to the library and when-to-invoke table and adds the pointer to `.claude/documentation.md`.
   Done when: a reader following finishing-branch reaches `consolidating-docs` on exactly the merge/PR paths, and using-playbooks lists it.

4. **Docs & dogfood.**
   Update README (new artifact, new step, new followups path) and `docs/DESIGN.md` (rationale + path). Run the empirical checks from CLAUDE.md (hook/JSON sanity if touched; dogfood smoke test).
   Done when: README and DESIGN reflect the feature and the dogfood smoke test passes.

## Risk / open questions

- **No automated test suite** — verification is empirical per CLAUDE.md (JSON/hook sanity + dogfood). "Correctness" of a prose skill means a senior reader can follow it without ambiguity; lean on the self-review pass.
- **Skill length** — `consolidating-docs` covers two entry points + bootstrap; if it pushes well past the ~150-line target, consider a companion file (like finishing-branch's reference tables) rather than cramming.
- **Self-dogfooding artifact** — whether to also add a `.claude/documentation.md` for the playbooks repo itself is a Milestone 4 judgement call; not required for the feature to ship.
