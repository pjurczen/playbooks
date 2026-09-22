# Playbooks Release Notes

## v0.9.0 (2026-09-22)

### brainstorming designs any kind of work; initiatives get a design and a roadmap

The design-doc rules shipped in v0.7.0 had been reverse-engineered from one example — a replacement in a Java service — and promoted to laws: "what replaces what", before/after subgraphs, method signatures with javadoc, one diagram, twelve nodes. They fit that example and little else. The nine sections were right as concerns; the rule under each was overfit.

`brainstorming` now starts by naming the kind of work — a feature in an existing codebase, greenfield, a replacement, an integration, a data change, a user-facing flow, an infrastructure change, a cross-cutting policy, an initiative — from a table in `references/design-doc-shape.md` that says, per kind, what to explore, what to ask, which views to draw, what the contracts are and which guarantees are typical. A new `references/design-views.md` is a catalogue of views, each a question and a mermaid type with a short snippet: context, structure with before/after, behaviour as a sequence, state, data, process, rollout. The rule is now the views a reader needs, usually one to three, each opening with its question. Contracts are any declaration the world sees — signatures, endpoints, schemas, flags, states — never bodies. Two sections are new: **Decisions**, one line per design-level decision with the alternative rejected, linking to an ADR only when one clears the test; and, inside Design, **the mechanism when it is the decision**: an algorithm whose complexity is the point, a concurrency scheme, a state machine, carried as pseudo-code as long as it needs to be and no longer, with the property it buys as a guarantee — never code that is merely the obvious way to implement a decision made elsewhere. "Shape" is renamed "Design". References are named by what they are, and worked examples by kind: `example-design-replacement.md`, `example-design-feature.md` (an API rate limiter, with a mechanism snippet), `example-design-initiative.md`.

An **initiative** is now defined as work with a target state no single slice reaches, a coexistence period, and shared contracts set once. Its design (`references/initiative-design.md`) holds the target architecture, the coexistence mechanism, the shared contracts and the decisions, and no slices; it lives on the base branch so every slice sees it. Slicing is a separate artifact and a separate skill: **`writing-roadmap`** produces the roadmap — slices with what each delivers, dependencies and status, the ordering rationale, an exit criterion — and consolidating-docs advances it as slices land and consolidates the initiative when the last one does. Each slice is then an ordinary brainstorming → writing-plans → executing-plans → finishing-branch cycle that inherits from the initiative instead of restating it. using-playbooks routes an approved initiative design to writing-roadmap and a roadmap with open slices to brainstorming.

## v0.8.1 (2026-09-22)

### writing-adr: what counts as an ADR

A reviewer read the shipped example ADR and pointed out that it recorded a local design choice — replace two recalculation mechanisms with one service — not an architecture decision. The skill's bar had let it through: any shared service with two future callers passed all three of its tests, and one table row ("removing a mechanism") was exactly how the example got written. The source skill's answer to "what is an ADR", a category table with examples, had been cut as padding in the lean pass.

The skill now leads with the deciding test — state the decision without naming the feature that triggered it; if nothing is left, it is a design decision and belongs in the design doc, with one sentence in the architecture doc — followed by a category table with examples of what is worth recording, a list of what is not, and a short "rule or instance" section: the approach brainstorming picked is usually an instance; if it instantiates a rule the team is adopting, the rule is the decision and the feature is the evidence; and an ADR records a decision that was taken, so someone who sees a wider rule proposes a new one rather than rewriting the record. The writing rules are a Do/Don't list again, as in the source, carrying ours: design altitude, the cost stated, alternatives at the decision's altitude, present tense, no second ADR for a drifted proposed one. The example is a rule-level ADR, "Business-process state outside technical lifecycle scope", with the feature as evidence.

Across the shape skills, the examples now own the shape: the skeleton in `writing-adr`, the template in `writing-plans` and the section skeleton in `design-doc.md` are gone, and each skill keeps only what each section must hold. brainstorming's decision step asks what rule, if any, the chosen approach instantiates before applying the test.

Evals: under the new skill, eval 3 (an ADR under a German per-domain map, with a bloated ADR already in the directory) passes 7/7 in both runs, as does the v0.8.0 baseline; the new skill's ADRs are titled as rules with the feature as evidence, the baseline's as instances. The length check in the skill and the grader now counts words rather than lines, since hard-wrapped paragraphs had turned a 379-word ADR into 48 lines. Results in `evals/results/`.

## v0.8.0 (2026-09-17)

### Lean skills, measured

An audit against published skill-writing guidance — Anthropic's skill best practices and its prompting guide for the current model family, superpowers' own `writing-skills`, the instruction-count research — found the library dense by the measure that matters, words and rule count, with single rules restated across a gate, a checklist item, a Red Flags row and a companion, and an always-loaded bootstrap of 1,118 words. Nothing had ever been run against a test prompt.

The lean pass cuts 15,200 words to 11,200 without removing a rule: one gate per skill, stated first with its reason, in normal register; each rule owned by one skill or companion and pointed to from elsewhere; Red Flags tables only on the six discipline skills, at most four rows each, every row an excuse rather than a restated rule; no per-skill announce lines; no linear flows drawn as digraphs; `verifying-before-done` rewritten around one gate; the bootstrap down to 465 words with its library index gone, since the Skill tool already lists every description. CLAUDE.md records the conventions, with budgets in words rather than lines.

The release ships with an eval harness (`evals/`) and its first results. Four evals — design a feature, plan from a design, record an ADR under a German per-domain map with a bloated ADR already in the directory, and a trivial rename that must not trigger the pipeline — ran on Opus in three configurations: the trimmed skills, the pre-trim skills, and no skills. Trimmed and pre-trim both pass 30 of 32 checks; the trimmed set uses 4.5% fewer tokens; the raw model passes 15 of 32 and reproduces the original failure modes exactly — a 93-line ADR with 80 backticks marked accepted before any code, a 159-line design with no diagram and no guarantees, a plan with no changes table. The two skilled misses were word caps set too tight for tables and are widened. Results are in `evals/results/`; a change to a skill now ships only with a non-negative delta.

## v0.7.0 (2026-09-17)

### ADRs captured at decision time — new `writing-adr` skill

ADRs were being written by `consolidating-docs` at landing time, and they came out as implementation summaries with a "Decision" heading: sixty lines of class names, annotations and method signatures, a findings list instead of context, no alternatives, and one for every decision in every feature. The cause was timing plus a missing owner. The decision happens in `brainstorming` — the user picks one of 2–3 approaches — but nothing recorded it until weeks later, when the agent's context was the diff and the review; rules against class names lose to that gravity. Meanwhile the example map in `consolidating-docs` ("a decision + its rationale → a new ADR") had no significance bar, and no skill defined what an ADR looks like.

A new **`writing-adr`** skill owns ADR text. It carries a conjunctive bar (constrains work beyond this feature, hard to reverse, there was a real choice — all three or no ADR; most features produce none), a lean Nygard shape (Context in prose, a one-to-three-sentence Decision, one-line Alternatives, honest Consequences, under ~40 lines), mechanical altitude rules (no code, no backticks, no symbols or file paths), and a `proposed → accepted → superseded` lifecycle in which the status line is the one mutable field. Location, filename pattern, language (headings included) and any index all come from `.claude/documentation.md`, never from the skill; the bootstrap default is date-prefixed names, which can't collide across in-flight branches. A companion `example.md` shows a real decision rewritten at the right altitude, so agents calibrate on it rather than on a repo's existing ADRs.

The pipeline now captures at the decision point. `brainstorming` reads existing ADRs during context exploration, applies the bar after design approval and workspace choice, and writes a `proposed` ADR next to the design doc — reviewed at the same gate, no extra confirmation; the design doc gains a short required "approach chosen and why" section. `writing-plans` applies the bar on mid-pipeline entry (the user brought a design). `executing-plans`' circuit-breaker revises the proposed ADR in place rather than writing a second. The end-of-feature reviewer checks whether the Decision is still true of the code. `consolidating-docs` handles ADRs once per feature *before* its per-item loop — reconcile drift, flip to `accepted`, update the index if the map names one, fall back to `writing-adr` from the design doc only when brainstorming was skipped — and its durable-vs-ephemeral bar gains an altitude rule: symbols and signatures are ephemeral, and decisions below the bar get a sentence in the architecture doc, not an ADR.

### Design docs and plans: readable by a team, complete for an implementer in another session

Three real design/plan pairs were judged for cleanliness, readability and completeness, and none was presentable: designs were investigation reports followed by 60–300 lines of Java bodies, alternatives were never written down, plans restated the design's components and risks and added little beyond milestones, and one 600-line umbrella design had been patched with "the implementation diverges" callouts until it was no longer true. The causes were structural. `brainstorming` had no altitude rule and no defined shape, so the design absorbed the conversation. `writing-plans` and `brainstorming` overlapped by construction. And the pipeline still assumed the strong model implements — `docs/DESIGN.md` §4.1's argument for intent-only plans — while in practice the pair is handed to an implementer in another session — Opus-class by default, occasionally a cheaper model when the user judges the work simple.

The design doc now has a fixed shape with two layers. A narrative layer — Problem, Approach with the alternatives it beat, Shape with one mermaid diagram and the components — that a teammate follows without the codebase; then a precision layer — **Contracts** (the public signatures the design introduces or changes, with semantics, never bodies) and numbered **Guarantees** — that the implementer works from. The rule is contracts, not bodies: a signature belongs in a design, a body rots there. Mermaid is the notation (GitHub, GitLab, Bitbucket and IntelliJ render it); one diagram answers one named question in ≤12 name-only nodes. The plan stands on the design and never restates it: a **Changes** table with method names, a call-site from → to table, scenarios that name their test home and the Guarantee they prove, milestones whose done-when names the suites, and only execution risks. Its self-review runs the implementer test on design + plan together — could an implementer with none of the conversation build this without guessing a name, a signature, an order, or a test? Both skills ship a worked example pair (`example-design.md`, `example-plan.md`) rewritten from a real feature, with nothing said twice.

Work that won't fit one cycle gets an optional **initiative design** in `docs/playbooks/initiatives/`: same shape, its diagram is the target architecture, its Contracts are the shared ones, and a Slices table is the only place status lives. It is edited to stay true, never annotated; `consolidating-docs` leaves it alone until every slice has landed. The end-of-feature reviewer now checks the code against the design's Guarantees and Contracts by name.

A field check against ~40 primary sources (Google's design-doc culture, Oxide RFDs, Rust RFCs, PEPs, HashiCorp, arc42, C4, Diátaxis; GitHub Spec Kit and Kiro templates; superpowers' own plan skills; Anthropic's Claude Code guidance; and the Ambig-SWE, Agentless and SWE-bench Verified papers) confirmed every structural choice above — the design/plan split, contracts-not-bodies, the two layers, caption-before-diagram, numbered traceable guarantees, and above all the changes and call-site tables, since localisation is the measured hard step for models — and added what was missing. Designs gain a `Status` field, an `Assumptions` section and an `Open questions` section that are never omitted, a "Done means" sentence closing Problem, failure behaviour in every contract, and a final guarantee stating what must not change; alternatives may run to three sentences and guarantees are falsifiable "when X, then Y" lines. Plans gain a milestone table (milestone · delivers · done when · biggest risk — the part a team reads), a stated red-first rule, and a binding *Stop and ask if* list, which is what makes an occasional cheaper implementer safe without bloating the plan; the self-review checks coverage in both directions. When implementation diverges, the design is edited and a `Deviation:` line records it. The using-playbooks skip list now includes any change describable in one sentence and verifiable with one command. Deliberately not taken, because they are superpowers-direction: signatures on every plan row, restated constraints, read-first precedent lists, pseudo-code in designs.

## v0.6.1 (2026-07-14)

### `consolidating-docs` — no dangling references to deleted husks

Consolidation was leaving links to the very files it deletes: durable content graduated into destination docs still saying "see `docs/playbooks/designs/…`" while that file died in the same commit. The skill now guards this at three points. The consolidation loop's write step requires rewriting any design/plan reference on the spot — inline what it points at or link the content's new home. A new **Verify** gate before the commit makes the check mechanical: since everything under `docs/playbooks/` is ephemeral by design, `git grep "docs/playbooks/" -- ':(exclude)docs/playbooks'` plus a grep for each deleted file's basename must come back clean of specific-file references (mentions of the workspace convention itself are fine) — which also catches pre-existing docs that pointed at a husk before the run. A matching Red Flags row covers the "see the design doc for details" tell.

## v0.6.0 (2026-07-08)

### Catch designs that degenerate under load

A hard problem's wrong abstraction was getting patched into slop because the pipeline is one-way with no reverse edge — "the design is wrong" kept becoming "patch it locally," N times over. Two edits add that reverse edge, at both ends of the pipeline. `brainstorming` gains a **failure-mode pass**: any approach that puts an unreliable component (an LLM at a generation boundary, a heuristic trusted to hold a structural invariant) on a load-bearing seam gets checked for how it degenerates under real load — the fix is to make the structure deterministic and move the unreliable part off the boundary, not to fence it with post-hoc patches. `executing-plans` gains a **circuit-breaker** (and a matching Red Flag): a second compensating patch, churn on the same contract, or each milestone needing more scaffolding than the last means the design is wrong, not the milestone hard — STOP and re-open it instead of patching. Together they catch the failure at design time and again mid-build, long before the end-of-feature review is too late to unwind it.

## v0.5.0 (2026-07-07)

A comprehensive review of the skill set (all 11 skills, the reviewer prompt, and `docs/DESIGN.md`) surfaced five workflow-breaking bugs, a set of coverage gaps, and drift between the design doc and the shipped skills. This release fixes all of it.

### Workspace is now chosen during brainstorming, before the first commit

Design and plan docs were committed to the current branch (usually `main`) before `executing-plans` created the feature branch — so `consolidating-docs`' `base..HEAD` scoping could never find them, discard left husks on `main`, and the end-of-feature review had no base to diff from. `using-git-worktrees` now fires at the end of `brainstorming` (after design approval, before the design doc is committed), and its report records a `BASE_SHA` that the end-of-feature review diffs against. `executing-plans` confirms the existing workspace instead of creating one.

### `finishing-branch` overhauled

Step 6 re-detected the worktree *after* `cd`-ing to the main checkout, so cleanup never fired and the branch delete failed; the detached-HEAD menu's 1–3 numbering collided with the Option 1–4 execution headers; and current-branch mode had no handling at all, letting the discard path offer to force-delete the base branch. Now: state is captured once from inside the workspace, detached choices get their own D1–D3 blocks (`git push origin HEAD:refs/heads/<name>`), on-base work gets a B1/B2 menu (keep / `git revert` — never deletion or reset), and Step 3 derives the base branch *name*, not a SHA. All flows verified against a scratch repo.

### New `debugging` skill

Bug fixes fell through the trigger table entirely. The condensed root-cause-first skill sketched in `docs/DESIGN.md` §4.5 now ships: reproduce, state the hypothesis with evidence, confirm, pin with a red-first regression test (`bdd-testing`), fix the cause not the symptom, verify (`verifying-before-done`). Escalates to `brainstorming` when the root cause is a design problem.

### Coverage gaps closed

- **Resume:** a trigger row and a Resuming section in `executing-plans` for continuing a half-executed plan after a session clear — find the workspace, diff milestones against `git log`, don't create a second worktree.
- **Greenfield / non-git:** `brainstorming` and `using-git-worktrees` offer `git init` (ask first); a missing test suite no longer blocks `using-git-worktrees` or `finishing-branch`; `writing-plans` puts minimal test scaffolding in milestone 1.
- **Mid-pipeline entry:** user brings an approved design → start at `writing-plans`; an approved plan → `executing-plans`.
- **Characterization tests:** `bdd-testing` now permits pass-on-first-run tests for existing code, verified by mutate-and-restore.

### Operational and consistency fixes

Worktree ignore-check now checks the chosen directory (previously an OR of two could pass while the chosen one was unignored); setup commands key off lockfiles instead of guessing the package manager, and skip for reused checkouts; `milestone-commits`' "when to commit" table no longer licenses the WIP checkpoints its own Red Flags forbid; `brainstorming` gains its announce line and an explicit trivial-tweak carve-out; `docs/DESIGN.md` gains a dated addendum (§10) reconciling its Decisions section with what actually shipped.

## v0.4.0 (2026-06-29)

### `consolidating-docs` skill — graduate decisions, delete the husks

Design docs and plans accumulated in `docs/playbooks/designs/` and `plans/` and were never cleaned up; the durable decisions inside them never reached the repo's real documentation. A new `consolidating-docs` skill extracts the durable content (decisions, rationale, alternatives, constraints), routes it per a `.claude/documentation.md` map — a general-purpose guide to where docs live and how they're maintained, usable beyond playbooks — then deletes the spent files (capture-then-delete; git keeps the history). It's fired by `finishing-branch` on the landing paths (merge / PR) so doc updates ship with the feature, and can be invoked manually to sweep the backlog. When the map is absent it offers to bootstrap one. `using-playbooks` advertises the skill and points any doc-touching task at the map.

### `followups.md` relocated to `docs/followups.md`

The durable followups backlog moves out of `docs/playbooks/` — now reserved for ephemeral design/plan working artifacts — up to `docs/followups.md`. The skills that read or write it (`brainstorming`, `writing-plans`, `executing-plans`) are updated accordingly.

## v0.3.1 (2026-05-14)

### `writing-plans` now requires committing the plan

`brainstorming` step 5 explicitly says "save and commit" for the design doc; `writing-plans` mentioned the commit only via the user-review gate template ("Plan written and committed to `<path>`"), with no enumerated commit step. The plan was occasionally landing as uncommitted changes. The "Save plans to:" line now reads "save and commit", restoring symmetry between the two skills. Design and plan commits land on the current branch / worktree, before any new worktree is created at the start of `executing-plans`.

## v0.3.0 (2026-05-07)

### `using-git-worktrees` added; worktrees are now the default workspace mode

A new `using-git-worktrees` skill is invoked from `executing-plans` Step 3 before any code is written. It detects existing isolation (linked worktrees, submodules) and then asks the user via `AskUserQuestion`:

1. **New worktree on a new feature branch** *(default — current checkout stays untouched)*
2. New feature branch in the current checkout
3. Work directly on the current branch *(requires explicit confirmation on `main` / `master`)*

User-declared preferences in CLAUDE.md / AGENTS.md / the request itself bypass the question. Native harness worktree tools are preferred over `git worktree add` when both are available; project-local `.worktrees/` paths are verified `.gitignore`-covered before creation.

This reverses the original v0.1.0 stance ("worktrees opt-in") documented in `docs/DESIGN.md` — solo work in practice benefits enough from the isolation to make it the default. `executing-plans` Step 3 wording updated accordingly.

## v0.2.2 (2026-05-07)

### Commit scope redefined as feature name

`milestone-commits` previously defined `(scope)` as "the subsystem touched", which agents misread — using the doc's audience (`chore(claude):`), the plugin used to author it (`docs(playbooks):`), or the filename's stem as the scope. Scope is now defined as the feature name as a short kebab-case slug — typically the topic from the design / plan filename (e.g. `feat(blacklist):`, `feat(agent-capture):`). Cross-cutting work (architecture docs, repo-wide config, tooling) keeps the no-scope carve-out. Examples and the anti-patterns table updated to match.

## v0.2.1 (2026-05-06)

### Milestone-commits invocation made explicit

`executing-plans` Step 8 read as a cross-reference ("commit per **milestone-commits**") and the skill body wasn't being loaded — agents fell back to using the plan's milestone titles as commit subjects (e.g. `Phase 2 M5: ReActAgent tool_calls writes`). Step 8 now explicitly invokes the skill, with a sentence noting the plan's milestone titles are reasoning scaffolding for the implementer, not commit material. `milestone-commits` anti-patterns table gains a row naming this failure mode.

## v0.2.0 (2026-05-06)

### End-of-feature review tightened

Closed a leak where trivial fixes were being promoted to `followups.md` instead of fixed in the review-fix milestone:

- Reviewer prompt now produces four severity buckets: Critical / Important / Minor (fix in review-fix milestone) / Followup (architectural, promote to `followups.md`).
- `Tier 2 — Durable followups` redefined to only items that need their own design / plan; anything fixable in a boy-scout pass stays in scope.
- Step 5 self-checkpoint now flags "added X but didn't wire it up at the call sites the plan named" as incomplete milestone work, not a finding for end-of-feature review.
- Red Flags row added: "Pre-existing ≠ out-of-scope."

## v0.1.0 (2026-05-06)

Initial release. Forked from [superpowers](https://github.com/obra/superpowers) and reshaped around different defaults: intent-shaped plans, main-session execution, milestone commits, BDD-flavoured tests, one end-of-feature review pass. See `README.md` for the skill list and `docs/DESIGN.md` for the rationale.

Mechanism: a SessionStart hook injects `using-playbooks` on every session start / clear / compact; other skills load on demand via the `Skill` tool.

Skill descriptions follow a canonical shape — `Use [trigger], to [goal]` — so pre-loaded metadata states both the firing condition and the purpose.
