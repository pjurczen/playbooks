# private — documents and cases that never leave this machine

Everything in this folder except this file is git-ignored. Put internal design documents in `designs/` and their case files in `cases/` (paths inside a case are
relative to the case file, so `../designs/<name>.md`). The notebook and `design judge` read from here by default; the public smoke material stays in
`../fixtures/` and `../cases/`.
