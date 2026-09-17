# reportgen

Builds a markdown summary report from named JSON sources in `data/`.

```
python -m reportgen.cli sales costs          # cached
python -m reportgen.cli sales costs --fresh  # bypass both caches
python -m pytest
```

Sources are cached twice: an in-process memo (`reportgen/memo.py`) and an on-disk cache (`reportgen/filecache.py`). Each caller keeps them in sync by hand.
