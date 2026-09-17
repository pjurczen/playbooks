"""Loads a named source. Two caches sit in front of the disk read; invalidation is done here by hand."""

import json
from pathlib import Path

from . import memo
from .filecache import FileCache

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
READS = {"disk": 0}

_file_cache = FileCache(Path(".reportgen-cache"))


def file_cache() -> FileCache:
    return _file_cache


def configure_cache_dir(directory: Path) -> None:
    global _file_cache
    _file_cache = FileCache(directory)


def _read_from_disk(name: str) -> list[dict]:
    READS["disk"] += 1
    return json.loads((DATA_DIR / f"{name}.json").read_text())


def load_source(name: str) -> list[dict]:
    key = f"source:{name}"
    cached = _file_cache.get(key)
    if cached is None:
        cached = _read_from_disk(name)
        _file_cache.put(key, cached)
    rows = memo.memoize(key, lambda: cached)
    # a freshly loaded source makes any summary built from it stale
    memo.drop(f"summary:{name}")
    return rows


def forget_source(name: str) -> None:
    memo.drop(f"source:{name}")
    memo.drop(f"summary:{name}")
    _file_cache.invalidate(f"source:{name}")
