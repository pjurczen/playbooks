---
name: using-playbooks
description: Use at the start of any conversation, to discover which skills are available and invoke them when they apply.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent for a specific task, skip this skill — your dispatcher already gave you what you need.
</SUBAGENT-STOP>

# Using Playbooks

**When a skill clearly applies to the work in front of you, invoke it with the `Skill` tool before you answer or act.**
Skills shape *how* the work is done, so running one afterwards is too late. The skip list below is the whole carve-out;
don't extend it by analogy.

User instructions (CLAUDE.md, AGENTS.md, the message itself) take precedence over a skill; a skill takes precedence over
default behaviour.

## When to invoke

| Trigger                                                                  | Skill                                                           |
|--------------------------------------------------------------------------|-----------------------------------------------------------------|
| Non-trivial creative work: a feature, a component, a behaviour change    | **brainstorming**, then **writing-plans** → **executing-plans** |
| A bug or a failure to investigate                                        | **debugging**                                                   |
| Resuming a feature that has a plan in `docs/playbooks/plans/`            | **executing-plans**                                             |
| About to say "done", "fixed", "passing"                                  | **verifying-before-done**                                       |
| Finishing a feature branch: merge, PR, cleanup                           | **finishing-branch**                                            |
| Graduating design/plan docs into real documentation                      | **consolidating-docs**                                          |
| The user asks to record a decision ("ADR this")                          | **writing-adr**                                                 |
| 2+ independent investigations that can run in parallel                   | **using-parallel-agents**                                       |
| An approved initiative design without a roadmap                          | **writing-roadmap**                                             |
| Continuing an initiative with a roadmap in `docs/playbooks/initiatives/` | **brainstorming** (next slice)                                  |

The pipeline runs in order — no code before a design, no execution before a plan; an initiative runs brainstorming →
writing-roadmap, then the pipeline per slice. Work the user has already approved enters where it stands: a design at *
*writing-plans**, a plan at **executing-plans**.

## When to skip

Just answer, or just do it, for:

- **Questions** — "what does this function do?", "where is X defined?"
- **Read-only exploration** — listing, reading, grepping.
- **Trivial changes** — anything you can describe in one sentence and verify with one command; a design and a plan would
  take longer to review than the change takes to make.
- **Work inside a running skill** — it names the sub-skills it needs.

The bar is *clearly applies*, not *might apply*.

## Red Flags — STOP

| Thought                                         | Reality                                                      |
|-------------------------------------------------|--------------------------------------------------------------|
| "I'll skip the skill, this is faster"           | Speed isn't correctness. If it applies, invoke.              |
| "I already know what the skill would say"       | Knowing the concept isn't running the workflow.              |
| "I'll do the work first, then invoke the skill" | Skills shape the work. After is too late.                    |
| "This is technically a small change"            | Small isn't trivial. A behaviour change needs brainstorming. |

To invoke: the `Skill` tool with the skill's name, announce *"Using [skill] to [purpose]"*, follow the loaded content;
don't `Read` SKILL.md files. When you add or move documentation, consult `.claude/documentation.md` if it exists.
