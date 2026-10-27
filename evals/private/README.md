# private — documents and cases that never leave this machine

Everything in this folder except this file is git-ignored. Internal design documents go in `designs/<variant>/`: `designs/base/` holds the documents the frozen
baseline was judged on, `designs/v1/`, `designs/v2/`, … the regenerations after each skill change; plans go in `plans/<variant>/` the same way. Case files go in
`cases/` (paths inside a case are relative to the case file, so `../designs/base/<name>.md`), and `designs.md` is the working copy of the consuming repo's
`.claude/designs.md`. The notebook and `design judge` read from here by default; the public smoke material stays in `../fixtures/` and `../cases/`.
