#!/usr/bin/env bash
# Usage: run-setup.sh <eval-id> <run-dir>
# Creates <run-dir>/repo from the fixture for that eval (git-initialised, one commit) and <run-dir>/outputs.
set -euo pipefail
EVAL_ID="$1"; RUN="$2"
HERE="$(cd "$(dirname "$0")" && pwd)"
FX="$HERE/fixtures"
rm -rf "$RUN/repo"; mkdir -p "$RUN/repo" "$RUN/outputs"
cp -R "$FX/reportgen/." "$RUN/repo/"
case "$EVAL_ID" in
  2) mkdir -p "$RUN/repo/docs/playbooks/designs"; cp "$FX/designs/2026-09-17-unified-cache.md" "$RUN/repo/docs/playbooks/designs/" ;;
  3) cp -R "$FX/overlay-de/." "$RUN/repo/"; rm -rf "$RUN/repo/docs/adr"
     mkdir -p "$RUN/repo/docs/playbooks/designs"; cp "$FX/designs/2026-09-17-unified-cache.md" "$RUN/repo/docs/playbooks/designs/" ;;
esac
cd "$RUN/repo"
git init -q -b main
git -c user.name=fixture -c user.email=fixture@example.com add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm "chore: fixture baseline"
echo "$RUN/repo"
