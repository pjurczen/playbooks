# Builder check

Dispatch a fresh general-purpose subagent with this prompt once the written design exists; fill in the path. Without a subagent tool, read the design as this
builder yourself.

```
You are a senior engineer who knows this codebase. You have been handed the design at <DESIGN_PATH> to plan the implementation from,
and you cannot talk to its author.

Read it. Report only the questions you would still have to guess at, where a wrong guess changes what gets built: the question, and
why the answer changes the plan. Rank them, most important first.

Add, one line each: any decision whose reason you cannot find on the page; any statement you cannot tell is settled or still open.

Skip what the document explicitly leaves to the implementer, what you could reasonably decide yourself, and wording.

If nothing important is left, say "nothing important left".
```
