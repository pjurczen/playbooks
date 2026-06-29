# Agentic Coding Analysis: Superpowers, and What I'd Build Instead

This document is a working analysis of the `superpowers` plugin — how it actually works under the hood when loaded into Claude Code, what the trade-offs are, and how I (Piotr) would design a leaner, more opinionated version for myself.

It's intentionally a living doc. We'll come back to it and edit as we build.

---

## 1. How superpowers actually plugs into Claude Code

It is useful to demystify this first, because most of the perceived "magic" is just three things stacked together.

### 1.1 The plugin manifest
- `.claude-plugin/plugin.json` — standard Claude Code plugin metadata.
- That's enough for Claude Code to recognise this as an installable plugin. Nothing else in the manifest is special.

### 1.2 A `SessionStart` hook that injects the bootstrap skill
- `hooks/hooks.json` registers a `SessionStart` hook (matchers: `startup|clear|compact`) that runs `hooks/session-start`.
- That script reads `skills/using-superpowers/SKILL.md` and emits it as `additionalContext` (Claude Code), `additional_context` (Cursor) or top-level `additionalContext` (Copilot CLI) so it gets injected into the very first system context of every new/cleared/compacted session.
- The `using-superpowers` content is wrapped in `<EXTREMELY_IMPORTANT>` and basically tells the agent: "if there's a 1% chance a skill applies, you MUST invoke it via the `Skill` tool before doing anything (including before asking clarifying questions)."

This is the mechanism that makes the rest of the system feel automatic. Without that injection at session start, the rest of the skills are just files on disk that nobody reads.

### 1.3 A library of skills in `skills/<name>/SKILL.md`
- Each skill is a markdown file with a YAML frontmatter (`name`, `description`).
- Claude Code's native `Skill` tool reads these, presents the content, and the agent is expected to follow it. Some skills include extra "companion" docs (`*-prompt.md`, `*.md` references) loaded on demand.
- Several skills include rendered `dot` graphs for flow control, big tables of "Red Flags / Rationalizations", and `<HARD-GATE>` / `<EXTREMELY-IMPORTANT>` blocks. This is all behaviour-shaping, not infrastructure.

So the entire system is essentially: **inject a "use skills" rule at session start → keep a folder of opinionated process documents → let Claude's `Skill` tool surface them on demand**.

That is genuinely simple, and very copyable.

---

## 2. The end-to-end workflow superpowers tries to enforce

The skills don't operate in isolation; they form a pipeline. The intended flow is:

```
User idea
   │
   ▼
brainstorming  ──► writes docs/superpowers/specs/<date>-<topic>-design.md
   │              (one question at a time, 2–3 approaches, sectioned design,
   │               spec self-review, user review gate, commit)
   ▼
writing-plans  ──► writes docs/superpowers/plans/<date>-<feature>.md
   │              (every file path, every test code-block, every commit
   │               message, bite-sized 2–5 minute steps)
   ▼
subagent-driven-development  (recommended)        OR  executing-plans (inline)
   │                                                   │
   ▼                                                   ▼
For each task in plan:                            For each task in plan:
   • dispatch implementer subagent                   • do the steps inline
   • implementer follows TDD, commits                • run the verifications
   • dispatch spec-compliance reviewer subagent      • mark TODO done
   • dispatch code-quality reviewer subagent
   • loop until both reviewers ✅
   • mark TODO complete
   ▼
finishing-a-development-branch
   • verify tests pass
   • detect worktree state
   • present 4 (or 3) options: merge / PR / keep / discard
```

Cross-cutting:
- `using-git-worktrees` — wants to create an isolated worktree before you start
- `test-driven-development` + `testing-anti-patterns.md` — strict RED-GREEN-REFACTOR, watch every test fail first, no production code without a failing test
- `verification-before-completion` — never claim "done" without running the verification command in the same message
- `systematic-debugging` — root cause before any fix
- `dispatching-parallel-agents` — fan-out for independent failing test files

It is a coherent system. The price is rigidity.

---

## 3. What this actually looks like in practice

Concretely, when you ask superpowers to "build feature X":

1. It explores the repo, then asks clarifying questions one at a time, refusing to write code until you approve a design doc.
2. It writes a long design doc to `docs/superpowers/specs/...` and commits it.
3. It writes a long, very explicit plan to `docs/superpowers/plans/...` — every file path, every test (with full code), every commit message, in 2–5 minute steps. It self-reviews the plan and re-fixes inline.
4. It asks: subagent-driven or inline?
5. (Subagent-driven) For each task, it dispatches an implementer subagent. After every task it dispatches a spec-compliance reviewer, then a code-quality reviewer, looping until both pass. Each step the implementer makes its own micro-commit.
6. After all tasks: a final reviewer pass, then `finishing-a-development-branch` presents the 4 options.

This is why you see:
- "comprehensive design document with clarifying questions" → the part you liked.
- "very long plan with each class and each test pre-written" → `writing-plans` literally instructs the agent to put complete code blocks for every test and every implementation step into the plan. This is by design.
- "uses haiku/sonnet instead of my opus" → `subagent-driven-development` explicitly says **"Use the least powerful model that can handle each role to conserve cost and increase speed."** Mechanical implementation tasks → fast, cheap model. Only architecture/review uses the most capable model.
- "context isn't propagated" → also **explicitly intentional**: the skill says "subagents should never inherit your session's context or history — you construct exactly what they need." The whole point of subagents in this system is context isolation. The trade-off you noticed (findings from earlier tasks don't help later ones) is the cost they accept on purpose.
- "50+ tiny commits per feature" → `writing-plans` mandates `Step 1: write failing test → Step 2: run it → Step 3: minimal code → Step 4: run → Step 5: commit`. Every step ends in a commit. Every task ends in a commit. Plus reviewer-fix iterations also commit. It compounds fast.
- "tests trivial things like a StrEnum's values" → `test-driven-development` is RED-GREEN-REFACTOR with an "Iron Law": NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST, with no behavioural carve-out. So when the plan lists a `StrEnum`, the plan also lists a "test that the enum has these values" step. The skill does not distinguish between *behavioural* tests and *structural* tests.

---

## 4. Where I disagree with the design (and why)

These are the things you flagged, restated in the language of the system so we know exactly what we want to change.

### 4.1 Plans are over-specified
**Their position:** "Document everything they need to know" — assume the engineer is skilled but knows nothing about your toolset, has questionable taste, and doesn't understand good test design. Therefore: write out every test, every method signature, every commit message in the plan.

**Why they do it:** They want subagents (with isolated context) to be able to execute a single task without ambiguity. If the plan is fully specified, the implementer subagent can be a small/cheap model.

**Why I dislike it:** When you're using Opus 4.x as your *main* model, the plan becomes a worse version of what the model would produce on its own. You're paying tokens twice: once to write code-as-prose into the plan, once to translate it back into actual code. And the plan rots the second the design changes.

**My preference:** Plans should describe *intent and decomposition*, not implementation. A good plan tells me:
- What components/units exist and what each is responsible for
- What the boundaries/interfaces are
- What behaviours need to be verified, in plain language
- What order the milestones go in
- Where the risky / non-obvious bits are

…and stops there. The model is more than capable of filling the gap. If a plan needs full code blocks to be unambiguous, the design wasn't actually decomposed.

### 4.2 Subagents using cheaper models with no context bridge
**Their position:** Subagents = isolated context = predictable, parallel-safe, cheap. Match model power to task complexity.

**Why I dislike it:**
- I'm paying for Opus on the main session because I want Opus's judgment on the implementation, not just on the orchestration. Down-shifting to Haiku for "mechanical" tasks frequently produces code that needs to be partly redone, which is more expensive end-to-end than just doing it on Opus once.
- Real codebases are full of cross-task lessons: "actually the existing `FooClient` already does this", "the test fixture in tests/conftest.py wires up a real DB". A fresh subagent rediscovers these every task. The "controller curates context" pattern only works if the controller already knows everything the subagent will discover, which by definition it doesn't.
- Context isolation is sold as a feature ("preserves your own context for coordination") but it actively prevents the kind of pattern recognition that makes a senior dev efficient.

**My preference:**
- Default to executing in the main session on the main model.
- Use subagents sparingly and *intentionally*: for genuinely parallel, genuinely independent things (e.g. fixing 4 unrelated failing test files at once — exactly what `dispatching-parallel-agents` is for) or for context-protection of large noisy tasks (running and parsing huge diagnostic output). Not as the default execution strategy.
- When I do dispatch a subagent, force the model to match the parent (or be explicit when down-shifting), and make it report back a *findings summary* meant to inform later work, not just "DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT".

### 4.3 Tiny commits
**Their position:** Every TDD step is its own commit (failing test, implementation, refactor). It produces a perfect, bisectable history.

**Why I dislike it:** It produces a useless, bisectable history. The signal-to-noise ratio of 50 commits like "test: add failing test for X / feat: minimal X / refactor: extract Y" is awful. `git log --oneline` becomes unreadable. `git blame` points at "minimal implementation" commits with no rationale. PR reviews are harder, not easier.

**My preference:** Commit at *meaningful milestones*. Roughly:
- Per logical feature/sub-feature
- After a passing milestone (a vertical slice working end-to-end)
- Before risky refactors (so you can revert)
- When switching context

Inside a milestone, work in an editor / staging area, not in commit history. If I want a TDD audit trail, I can squash from a working branch — but the *durable* history should be readable.

### 4.4 Dogmatic TDD over BDD
**Their position:** RED-GREEN-REFACTOR every time, no exceptions, "violating the letter is violating the spirit", "if you didn't watch it fail you don't know it tests anything", testing-anti-patterns enforces no test-only methods, no mock-of-mock, etc.

**Why I dislike it:** It conflates two things:
1. *Behaviour-driven* tests — assert what the system does for a user / caller. Genuinely valuable.
2. *Structural* tests — assert that a class exists, an enum has these values, a property is named X. Mostly worthless; they restate the implementation in a second form.

The superpowers TDD skill doesn't make this distinction, and `writing-plans` happily generates structural tests for `StrEnum` values, dataclass field names, etc. I want the discipline of "behaviour first, watch it fail, then implement", but applied at the *use-case* level — not at the level of "does this enum literally contain these strings".

**My preference: BDD-flavoured TDD.**
- Tests describe behaviours of *units with interesting logic*. Each test name reads like a sentence: "given X, when Y, then Z."
- No tests for: pure data containers (enums, dataclasses, DTOs), thin wrappers, framework code with no logic, code where the test would be "the same thing, written backwards".
- Tests at the right altitude: prefer integration / use-case tests that exercise real collaborators where feasible — they're closer to acceptance tests and survive refactors.
- TDD's "red first" discipline still applies *at the behaviour level* — write a behavioural assertion, watch it fail for the right reason, implement, watch it pass.

### 4.5 Other things in the system worth a note

- **`verification-before-completion`** — actually good. Keep this idea. The "no completion claims without fresh evidence" pattern is genuinely useful and I'd port it almost verbatim.
- **`systematic-debugging`** — also good in spirit ("root cause before fix"), but the heavy four-phase ceremony is overkill for small bugs. Distil to: "for any bug bigger than a typo, state the root cause hypothesis and the evidence for it before changing code".
- **`finishing-a-development-branch`** — solid: verify tests, detect worktree state, present a fixed menu. Worth porting.
- **`using-git-worktrees`** — good defaults, but I rarely actually want a worktree for solo work. Make this opt-in.
- **`writing-skills`** — meta-skill about writing skills with subagent pressure-tests. Cute but not load-bearing. I'd skip it for v1.
- **`dispatching-parallel-agents`** — keep, this is the legitimate use case for subagents.
- **`brainstorming`** — keep most of it. The clarifying-questions-one-at-a-time + 2–3 approaches + sectioned design + spec doc on disk pattern is the part you said you liked, and it's well-tuned.
- **The "Red Flags / Rationalizations" tables** in many skills are a clever behaviour-shaping device. Worth borrowing the pattern even if I don't keep their content.

---

## 5. What I'd build instead — proposed shape: `playbooks`

The good news: building my own version is *small*. The whole superpowers infrastructure is "a SessionStart hook + a folder of markdown".

**Plugin name: `playbooks`.** Same shape as `superpowers` — a vivid noun that *is* the directory of stuff you know how to do — but the metaphor is the thesis: a seasoned operator with a set of plays, not a hero with powers.

### 5.0 Design principle: produced artifacts must be readable end-to-end

The biggest single problem with superpowers in practice isn't the skill files — it's **the artifacts those skills produce**, especially the plan document. The plan is what the *human* has to read and approve, and superpowers' plans are gigantic: every test pre-written, every commit message pre-drafted, every method signature pre-specified. Reviewing one is a chore, so the human either rubber-stamps it (defeating the purpose of the gate) or doesn't read it at all.

**The artifact-brevity rules for `playbooks`:**

- **Plans should be readable end-to-end in 2–3 minutes.** If they're not, the plan is doing the implementation's job. Shape: goal, decomposition, behaviours, milestones, risks. No code blocks except for tiny illustrative interface sketches when genuinely needed (and even then — prefer prose).
- **Design docs the same.** Sectioned, scaled to complexity, no padding. A simple feature gets a one-page design; a complex one gets a few pages — never more.
- **Commit messages describe the *why* of the slice**, not a play-by-play of every file touched.

#### What about the skill files themselves?

**Default position: start strong, dial down later.** Skill files can use whatever shape best drives correct agent behaviour — including `<EXTREMELY-IMPORTANT>` framing, Red Flags / Rationalizations tables, and `dot` flowcharts where they make branching explicit. Superpowers gets a lot of compliance from these devices; we'll keep them as the default and remove individual ones only when we observe them producing real harm (e.g. over-invocation on trivial questions).

The one real rule for skill files: **strong "must invoke" framing must always be paired with an equally explicit "when to skip" carve-out.** Compliance pressure without a skip rule is what produces the "invoke a skill before every clarifying question" behaviour that makes superpowers feel ceremonial. The fix isn't softer rules — it's clearer carve-outs.

In short: skill files are not the bloat target. The plan document is. Shape skill files for behaviour, not for elegance.

### 5.1 Repo / plugin layout

```
playbooks/
├── .claude-plugin/
│   └── plugin.json                  # standard CC plugin metadata
├── hooks/
│   ├── hooks.json                   # SessionStart hook registration
│   └── session-start                # injects using-playbooks as context
└── skills/
    ├── using-playbooks/SKILL.md         # bootstrap rule, toned down
    ├── brainstorming/SKILL.md           # ported, trimmed (drop visual companion)
    ├── writing-plans/SKILL.md           # rewritten — intent, not code
    ├── executing-plans/SKILL.md         # rewritten — main-session by default
    ├── using-parallel-agents/SKILL.md   # ported from dispatching-parallel-agents
    ├── bdd-testing/SKILL.md             # new — replaces test-driven-development
    ├── milestone-commits/SKILL.md       # new — explicit anti-tiny-commit rule
    ├── verifying-before-done/SKILL.md   # ported, trimmed
    ├── debugging/SKILL.md               # condensed systematic-debugging
    └── finishing-branch/SKILL.md        # ported, trimmed
```

That's 10 SKILL.md files plus a hook. Smaller, opinionated, and — most importantly — producing artifacts (plans, design docs, commit messages) that a human can actually read end-to-end.

### 5.2 Concrete rule changes from superpowers

| Topic                | Superpowers rule                                            | My rule                                                                                      |
|----------------------|-------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| Plans                | Full code blocks per step, every test pre-written            | Components, boundaries, behaviours, milestones — no implementation code in the plan          |
| Execution model      | Subagent-driven by default, cheap models for "mechanical"    | Main-session by default, on the main model. Subagents only for parallel-independent or context-protection cases |
| Subagent context     | Never inherit session context                                | Subagent gets curated context AND must report a findings summary the parent stores           |
| Subagent model       | Match power to task complexity (cheap by default)            | Match parent model unless I explicitly down-shift                                            |
| Commits              | One per TDD step (~5 per task)                               | One per milestone / vertical slice                                                           |
| TDD                  | Red-green-refactor on every unit, including data classes     | Behavioural / use-case tests only. No tests for data-only constructs. Red-first still required at the behaviour level |
| Worktrees            | Default-on, ask for consent                                  | Opt-in only                                                                                  |
| Verification         | "No completion claims without fresh evidence"                | Same — port directly                                                                         |
| Skill discipline     | "1% chance a skill applies → you MUST invoke it"             | Tone down: "if a skill clearly applies, follow it" — don't flood the model with `Skill` calls on trivial questions |

### 5.3 BDD-flavoured testing skill — sketch

Core rules I'd codify:

1. **Test only things with interesting behaviour.** A unit has interesting behaviour if it makes a decision, transforms data non-trivially, has effects, or coordinates collaborators. If it's a data container or thin pass-through, no test.
2. **Tests are use-case shaped.** Name pattern: `test_<unit>_<given>_<when>_<then>` (or pytest-bdd / equivalent if you want true Gherkin). Each test should read like a behavioural assertion, not a structural one.
3. **Red-first applies to behaviour.** Write the behavioural assertion → run it → watch it fail for the right reason → implement → watch it pass. No watching-empty-classes-fail-to-instantiate.
4. **Prefer integration over unit when realistic.** If your unit's collaborators are simple and fast, exercise them rather than mocking. Mock at the IO boundary (network, filesystem, time, randomness), not at every internal class boundary.
5. **No structural tests.** No `test_enum_has_values`, no `test_dataclass_has_fields`, no `test_class_inherits_from`, no `test_method_exists`. The type system / linter does this.
6. **No test-only methods on production classes.** Carry over from superpowers — that one's right.

### 5.4 Plan-writing skill — sketch

A plan I want would look like:

```markdown
# <feature> — implementation plan

## Goal
One sentence.

## Decomposition
- ComponentA — responsibility, interface, depends on …
- ComponentB — responsibility, interface, depends on …
- (etc.)

## Behaviours to verify (BDD-style)
- Given X, when Y, then Z
- (etc.)

## Milestones
1. Vertical slice 1: …  (done when: …)
2. Vertical slice 2: …  (done when: …)

## Risk / open questions
- …
```

No code blocks. No file paths unless they're load-bearing. No commit messages.

### 5.5 Execution skill — sketch

Default loop in the main session, per milestone:

1. Pick the next milestone from the plan.
2. Sketch the behavioural test(s) for it. Watch them fail.                    *(RED)*
3. Implement the smallest thing that satisfies the milestone end-to-end.       *(GREEN)*
4. Run the relevant tests + a quick smoke of nearby behaviour.
5. **Self-checkpoint review** — *did I meet the goal?* (see "Review timing" below).
6. **Refactor pass** — *leave it better than I found it* (see "Refactor pass" below). *(REFACTOR)*
7. Run tests again; verify still green.
8. **One milestone commit.** Message describes the *why* of the slice. The refactor is part of this commit, not a separate drive-by.
9. Move on.

#### Refactor pass

After the milestone is correct (tests green, self-checkpoint passed), spend a few minutes looking around the area you just touched and improve what you can. A senior dev almost always notices small cleanups once they have the context from doing the work. The cheapest moment to clean up is now — before the milestone commit, while the area is still loaded in your head.

**Scope: the neighbourhood of what you touched.** Same file, the function above and below, the helpers you called, the immediate callers if you read them. *Not* random distant files. *Not* the whole module.

**Time-box: ~5–10 minutes.** If you find something bigger, capture it in `## Findings → Open questions` and move on. The refactor pass is a polish, not a project.

**Allowed moves:** rename for clarity, extract a small helper, collapse obvious duplication, remove dead code, simplify a conditional, tighten a comment. **Not allowed:** redesign interfaces, restructure modules, change architecture, sweeping pattern "improvements". Those need their own milestone — and possibly their own plan.

**Tests stay green throughout.** Refactoring is behaviour-preserving by definition. If you find a bug while refactoring, stop — that's a separate finding, not something to silently fix under the cover of cleanup.

**Pre-existing code is partially in scope.** Boy scout rule applies: rename a confusingly-named local, extract a small helper if it genuinely makes the new code read better. But don't rewrite a 300-line function that was there before you arrived. Radius = "things that touch what I just did."

**It's OK to find nothing.** Most milestones will have something worth a small clean-up. A few won't. "Looked, nothing worth doing" is an honest and acceptable answer — forcing a refactor when there's nothing to do creates exactly the kind of noise we're avoiding.

#### Findings: where they live and where they go

Findings come in two flavours with different lifespans, and they live in two different places:

**Tier 1 — In-session findings** (useful within the current feature).
Live as a running `## Findings` block in the conversation. The agent appends to this block whenever it notices something during the work — discovered helpers, small surprises, deferred refactor items, gotchas, things the next milestone should know. The block has three subsections: `Changes` (what was done), `Gotchas` (things future milestones should know), `Open questions` (refactor items too big for the current milestone, design questions, anything that was deferred). This block is part of the input to the end-of-feature reviewer subagent.

**Tier 2 — Durable followups** (outlive the feature).
Live on disk at `docs/followups.md`. One file per project, append-only during work. Format is deliberately light — no effort estimates, no priority labels, no ceremony:

```markdown
# Followups

Notes from past work that didn't fit into the active feature. Triaged when
starting new work — if it intersects, fold into the new plan; otherwise leave.

## 2026-05-06 — split AuthHandler.validate() responsibilities
Validation and logging tangled together. Worth splitting before the next
auth-area work. File: src/auth/handler.py:120. Discovered while: session-cookie-rotation.
```

**Promotion: when Tier 1 becomes Tier 2.**
At end-of-feature, *after* the review pass and *before* `finishing-branch`, the agent reads the running in-session `## Findings` block, drops anything that was addressed during the work, and promotes anything still actionable to `docs/followups.md`.

**Read-back: closing the loop.**
Findings that don't get re-read are findings that rot. So `brainstorming` and `writing-plans` must check `docs/followups.md` during their "explore project context" / decomposition step. If a followup intersects with the feature being planned, fold it in. If it doesn't, leave it alone — don't snowball every adjacent cleanup into the current plan.

#### Review timing

Two review points, deliberately lighter than superpowers' two-reviewers-per-task model:

- **After each milestone — self-checkpoint (in-session, ~2–5 min).** Before committing the milestone, the agent re-reads the milestone goal from the plan, looks at the diff for *just this milestone*, and answers three questions: *Did I actually meet the goal? Did I leave any behaviour broken? Anything surprising worth noting for later milestones?* If something's off, fix it before the commit. If it's a note for later, capture it in a `## Findings` block in the session and proceed.
- **End of feature — focused review pass (one subagent, before `finishing-branch`).** When all milestones are done, dispatch a *single* reviewer subagent with: the design doc, the plan, the full feature diff, and the accumulated findings. It returns Strengths / Issues (Critical / Important / Minor) / Assessment. Fix Critical and Important. Note Minor. Then proceed to `finishing-branch`.

That's it. No per-task spec-compliance reviewer plus per-task code-quality reviewer plus end-of-feature reviewer like superpowers does. One pass at the end is enough when milestones are real vertical slices and self-checkpoints are honest.

#### When to use subagents during execution

Default: don't. Stay in the main session.

Dispatch a subagent only when:
- ≥2 genuinely independent failing slices need investigation in parallel (the legitimate `using-parallel-agents` case), or
- A subtask will produce a lot of context noise that I don't need in the main thread (large log parses, broad codebase searches), and the *findings* are what I care about.

When I dispatch one, it must return a `## Findings` block with three subsections:
- **Changes** — files touched and a one-line summary per file
- **Gotchas** — things I should know going forward (existing utilities discovered, naming conventions, sharp edges)
- **Open questions** — anything it couldn't resolve

The parent stores these inline in the main session before the next step, so subsequent milestones benefit from what was learned. This is the deliberate fix for superpowers' "context isolation eats institutional knowledge" problem.

### 5.6 Bootstrap-skill tone (`using-playbooks`)

Replace superpowers' "if there's a 1% chance a skill applies, you MUST" with something like:

> When a playbook clearly applies to the work in front of you, follow it. Playbooks are reference guides — not contracts you have to invoke before every reply. For trivial questions and read-only exploration, just answer.

This kills the "invoke a skill before every clarifying question" behaviour, which is the thing that makes superpowers feel ceremonial. The bootstrap skill should fit on one screen.

---

## 6. Decisions

These were open questions; we've now closed them:

1. **Worktrees: off by default, opt-in.** No prompt, no consent question at session start. The `using-git-worktrees` skill becomes a *manually invokable* utility, not a step the workflow tries to insert.
2. **Commits: one per milestone. No hard upper bound.** Milestones are sized in the plan to be meaningfully self-contained but not huge. If a milestone is so big it needs an arbitrary "commit every N hours" cutoff, the plan was wrong — fix the plan, not the commit rule.
3. **Subagent reporting: required `## Findings` block** with three subsections — `Changes`, `Gotchas`, `Open questions`. Free-form within each. Documented in 5.5 above.
4. **Plan storage:** `docs/playbooks/designs/YYYY-MM-DD-<topic>.md` and `docs/playbooks/plans/YYYY-MM-DD-<feature>.md`. Mirrors superpowers' shape under our own namespace.
5. **Red Flags / Rationalizations pressure:** keep on the two high-stakes skills only — `verifying-before-done` and `debugging`. Drop entirely from `brainstorming`, `writing-plans`, `executing-plans`, `bdd-testing`, `milestone-commits`, `finishing-branch`. The everyday skills should read like a senior dev's note to themselves, not a parental warning.
6. **Visual companion (browser-based mockup tool in `brainstorming`): drop for v1.** It's experimental, token-heavy, and adds surface area for a feature I don't reach for. Easy to add later if I miss it.
7. **Multi-harness support: Claude Code only.** No `.codex-plugin/`, no `.cursor-plugin/`, no `gemini-extension.json`. If another harness becomes interesting later, the bootstrap script is ~50 lines — adding a branch is trivial.

---

## 7. Suggested first slice if we build this together

If we want to actually start, I'd propose this sequence (each one a real milestone, not a 12-step plan):

1. **Bootstrap the plugin shell.** `plugin.json` (name: `playbooks`), `hooks.json`, `session-start` script that injects a stripped-down `using-playbooks/SKILL.md`. Verify it shows up in a fresh Claude Code session and that the agent actually reads it.
2. **Port the keepers — trimmed.** `brainstorming` (drop visual companion), `verifying-before-done`, `finishing-branch`, `using-parallel-agents`. Port near-as-is but cut to the brevity targets in 5.0.
3. **Write the new ones.** `writing-plans` (intent-only — the most important one to get right, since this is where the artifact-bloat problem lives), `executing-plans` (main-session-default, with the review timing in 5.5), `bdd-testing` (no structural tests), `milestone-commits`.
4. **Use it on a small real project.** Iterate based on what actually annoys me.
5. **Decide on `debugging` + worktree skills** based on whether I miss them. Both stay out of v1 unless they earn their place.

---

## 8. TL;DR for myself

- Plugin name: **`playbooks`**. Same shape as `superpowers` — a vivid noun for "the stuff you know how to do" — but the metaphor is the thesis: a seasoned operator with a set of plays, not a hero with powers.
- Superpowers = `SessionStart` hook + a folder of opinionated markdown. The mechanism is trivial; the value is the *content*. So copying the mechanism is easy.
- **The big complaint about superpowers is bloat in the *artifacts it produces*** — plan documents 30+ pages long with every test and commit message pre-written. `playbooks` plans are intent-shaped and readable end-to-end in 2–3 minutes, so the human can actually review them. Skill files themselves get the same treatment as a side effect.
- The parts I want to keep: **brainstorming, verifying-before-done, using-parallel-agents, finishing-branch**, and the general idea of process-shaping skills.
- The parts I want to rewrite: **writing-plans (intent not code), executing-plans (main session not subagents, with one self-checkpoint per milestone + one focused review pass at the end), bdd-testing (no structural tests), milestone-commits (one per slice, not one per step)**.
- The parts I want to drop or downplay: **subagent-driven-development as default, the "1% chance" extreme tone in `using-superpowers`, multi-harness support, writing-skills meta-skill, default-on worktrees, visual companion, Red Flags tables on everyday skills**.
- Resulting plugin is ~10 SKILL.md files plus a hook script — roughly a quarter of superpowers' total markdown. That's the whole thing.

---

## 9. Addendum — doc consolidation & cleanup (2026-06)

Two changes after v1, both extending the existing two-tier knowledge model (in-session `## Findings` → durable `followups.md`) to the design and plan artifacts themselves.

**`consolidating-docs` skill + `.claude/documentation.md`.** Design docs and plans are working artifacts; their durable decisions belong in the repo's real documentation, not piled up in `docs/playbooks/`. The new skill extracts the durable content, routes it per a `.claude/documentation.md` map (a general doc-maintenance guide, usable beyond playbooks), then deletes the husks — capture-then-delete, with git keeping the history. It's fired by `finishing-branch` on the merge/PR paths (so doc updates land with the feature) and can be invoked manually to sweep the backlog. When the map is absent it offers to bootstrap one. Rationale: dated husks were accumulating and the decisions inside them were never re-read.

**`followups.md` → `docs/followups.md`.** It's a durable, active backlog, unlike the ephemeral design/plan husks, so it moves out of `docs/playbooks/`, which now holds only working artifacts.
