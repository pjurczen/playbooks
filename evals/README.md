# evals — judging the documents the skills produce

`design` judges a design document (or an initiative plus its slices) with small checks, one yes/no question at a time, each verdict carrying the span of the
document it rests on. Metrics come from published design-doc practice and the LLM-judge literature (the research report lives in
`../../playbooks-workspace/reports/`), not from the skill's section names: judges see whole documents and find units by content.

Setup, from this directory:

```bash
uv sync                      # the tool, its tests and Jupyter
cp example.env .env          # then put ANTHROPIC_API_KEY in .env (git-ignored); not needed for --mechanical-only or the tests
uv run pytest
uv run jupyter lab           # then open notebooks/single-run.ipynb: one run, step by step
```

Commands:

```bash
uv run design judge cases/reportgen-unified-cache.json --flow private/runs/smoke --mechanical-only
uv run design judge --doc path/to/design.md --flow <dir>                    # quick form, no case file
uv run design judge --initiative init.md --doc slice-1.md --doc slice-2.md --flow <dir>
uv run design judge --dir private/designs --flow private/runs/baseline [--votes 3] [--skip-done]   # every document, one case each
                                                                      # --parallel 4 (default) runs a case's judge calls concurrently; cases run one after another
uv run design digest <flow>                                                  # regenerate digest.md files from traces
```

A run writes into `<flow>/<variant>/` (put flows under `private/runs/`, which is git-ignored): `results.jsonl` (one row per case and rep, hillclimb-compatible),
`traces/`, `share/<case>/` and `private/<case>/`, plus `<flow>/_state.json`. **Only `share/` is meant to leave your machine**: it holds the documents, the
units, the checks with their quotes, and `digest.md`. Absolute paths, the commit, usage and the task text stay in `private/`.

Internal documents and their cases go in `private/` (git-ignored except its README); the schema is `cases/schema.json` and `cases/reportgen-unified-cache.json`
is the public smoke case on the reportgen fixture. The older harness (`evals.json`, `grade.py`, `run-setup.sh`, `fixtures/`, `results/`) is unchanged.

Status: milestone 1 (mechanical metrics, layout, notebook shell). Judged metrics, extraction, facts and the aggregate digest follow.
