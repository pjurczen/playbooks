"""On-disk cache of raw source rows. Independent of the memo; callers keep the two in sync by hand."""

import json
import time
from pathlib import Path


class FileCache:
    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.directory / f"{key}.cache.json"

    def get(self, key: str):
        path = self._path(key)
        if not path.exists():
            return None
        return json.loads(path.read_text())["value"]

    def put(self, key: str, value) -> None:
        self._path(key).write_text(json.dumps({"value": value, "written_at": time.time()}))

    def invalidate(self, key: str) -> None:
        path = self._path(key)
        if path.exists():
            path.unlink()

    def purge_older_than(self, seconds: float) -> int:
        now = time.time()
        removed = 0
        for path in self.directory.glob("*.cache.json"):
            if now - json.loads(path.read_text())["written_at"] >= seconds:
                path.unlink()
                removed += 1
        return removed
