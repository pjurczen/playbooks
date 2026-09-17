# Architecture

`sources` loads rows for a named JSON file under `data/`. `summary` computes per-source totals. `report` renders a markdown table; `cli` is the entry point.

Two caches sit in front of the disk read: an in-process memo (`memo.py`, free-form string keys) and an on-disk cache (`filecache.py`). They are independent. `sources` writes both and drops the summary memo whenever it loads; `report --fresh` empties both by calling into each. There is no single place that knows what is cached or for how long.
