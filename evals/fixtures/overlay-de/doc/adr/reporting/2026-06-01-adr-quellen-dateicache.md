# ADR: Quellen über einen Dateicache laden — `FileCache`

## Status

Akzeptiert (2026-06-01)

## Kontext

Nach der Umstellung auf JSON-Quellen unter `data/` wurden die Dateien bei **jedem** Aufruf von
`load_source(name)` erneut gelesen. Analyse der Aufrufer:

1. **`summarize(name)` liest je Aufruf einmal.** `summary.summarize` ruft `sources.load_source`
   ohne Memoisierung; bei N Quellen im Report sind es N Lesezugriffe pro `build_report`.
2. **Die CLI ruft `build_report` mehrfach** (`cli.main` → `build_report(args.names)`), da der
   `--fresh`-Pfad und der normale Pfad getrennt implementiert sind.
3. **Kein Prozess-Cache vorhanden.** `memo.memoize` existierte noch nicht.
4. **Lesezeit dominiert.** Messung mit `READS["disk"]`: 12 Lesezugriffe für einen Report mit 3 Quellen.

## Entscheidung

Einführung von `FileCache` (`reportgen/filecache.py`), `@dataclass`-frei, mit `get`/`put`/
`invalidate`/`purge_older_than`:

```python
class FileCache:
    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def get(self, key: str):
        path = self._path(key)
        if not path.exists():
            return None
        return json.loads(path.read_text())["value"]

    def put(self, key: str, value) -> None:
        self._path(key).write_text(json.dumps({"value": value, "written_at": time.time()}))
```

`sources.load_source` prüft zuerst `_file_cache.get(f"source:{name}")`, liest bei Miss von der Platte
(`_read_from_disk`) und schreibt mit `put`. `report.build_report(fresh=True)` ruft
`purge_older_than(0)`.

## Konsequenzen

- Entfernt: direkte Lesezugriffe in `summary.py`.
- Neu: `sources._file_cache`, `sources.file_cache()`, `sources.configure_cache_dir(path)`.
- `READS["disk"]` bleibt als Messpunkt erhalten.
- Cache-Verzeichnis `.reportgen-cache/` wird in `.gitignore` aufgenommen.

## Referenzen

- `docs/architecture.md`
