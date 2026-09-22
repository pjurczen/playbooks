#!/usr/bin/env bash
# Structural gate for the skill library. Exit non-zero on any failure. See .claude/gates.md.
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0
DISCIPLINE="using-playbooks brainstorming executing-plans verifying-before-done debugging consolidating-docs"

budget() { case "$1" in finishing-branch|executing-plans|consolidating-docs) echo 1500;; writing-adr|brainstorming) echo 1200;; using-playbooks) echo 500;; *) echo 1000;; esac; }

echo "== word budgets =="
for f in skills/*/SKILL.md; do n=$(basename "$(dirname "$f")"); w=$(wc -w < "$f"); lim=$(budget "$n"); [ "$w" -le "$lim" ] || { echo "  OVER $n: $w > $lim"; fail=1; }; done

echo "== frontmatter name matches directory; description in 'Use …, to …' shape =="
for d in skills/*/; do n=$(sed -n 's/^name: //p' "$d/SKILL.md"); [ "$n" = "$(basename "$d")" ] || { echo "  MISMATCH $d -> $n"; fail=1; }; sed -n 's/^description: //p' "$d/SKILL.md" | grep -q '^Use .*, to ' || { echo "  DESCRIPTION SHAPE $d"; fail=1; }; done

echo "== one gate per skill; Red Flags only on discipline skills, ≤ 4 rows; no announce lines; no dot graphs =="
for f in skills/*/SKILL.md; do n=$(basename "$(dirname "$f")")
  g=$(grep -cE '^<(HARD-GATE|EXTREMELY-IMPORTANT)>' "$f" || true); [ "$g" -le 1 ] || { echo "  MULTI-GATE $n"; fail=1; }
  rows=$(awk '/^## Red Flags/{f=1} f&&/^\| "/{c++} END{print c+0}' "$f")
  if echo " $DISCIPLINE " | grep -q " $n "; then [ "$rows" -le 4 ] || { echo "  ROWS $n: $rows"; fail=1; }; else [ "$rows" -eq 0 ] || { echo "  UNEXPECTED RED FLAGS $n"; fail=1; }; fi
  grep -q "Announce at start" "$f" && { echo "  ANNOUNCE $n"; fail=1; }
  grep -q '```dot' "$f" && { echo "  DOT GRAPH $n"; fail=1; }
done

echo "== reference links resolve; no stale file names; no brand references =="
python3 - <<'PY' || fail=1
import re, os, glob, sys
bad = 0
for f in glob.glob("skills/**/*.md", recursive=True):
    t = open(f).read()
    for m in re.findall(r"`((?:\.\./|references/)[^`<]+\.md)`", t):
        if "<" in m: continue
        if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f), m))): print("  MISSING", f, "->", m); bad += 1
    if re.search(r"superpowers", t): print("  BRAND", f); bad += 1
sys.exit(1 if bad else 0)
PY

echo "== example designs and the fixture carry the eleven sections in order =="
python3 - <<'PY' || fail=1
import re, sys
S = ["Problem","Diagnosis","Approach","Decisions","Design","Contracts","Guarantees","Assumptions","Open questions","Risks","Out of scope"]
bad = 0
for f in ["skills/brainstorming/references/example-design-replacement.md","skills/brainstorming/references/example-design-feature.md","skills/brainstorming/references/example-design-initiative.md","evals/fixtures/designs/2026-09-17-unified-cache.md"]:
    h = [x for x in re.findall(r"^## (.+?)\s*$", open(f).read(), re.M) if x in S]
    if h != S: print("  SECTIONS", f, h); bad += 1
sys.exit(1 if bad else 0)
PY

echo "== no bold markers split by a line wrap; no merged headings or bullets =="
python3 - <<'PY' || fail=1
import glob, re, sys
bad = 0
for f in sorted(glob.glob("skills/**/*.md", recursive=True)):
    t = open(f).read()
    if re.search(r"\*\n[ \t]*\*", t): print("  SPLIT MARKER", f); bad += 1
    body = re.sub(r"```.*?```", "", t, flags=re.S)
    for i, para in enumerate(body.split("\n\n")):
        if para.lstrip().startswith("|"): continue
        if para.count("**") % 2: print(f"  ODD BOLD {f} paragraph {i}"); bad += 1
    for i, l in enumerate(body.splitlines(), 1):
        if re.search(r"\S.* ## \S", l) or re.search(r"\S\. - \*\*", l): print(f"  MERGED {f}:{i}"); bad += 1
sys.exit(1 if bad else 0)
PY

echo "== json =="
python3 -c "import json; json.load(open('.claude-plugin/plugin.json')); json.load(open('hooks/hooks.json')); json.load(open('evals/evals.json'))" || fail=1

[ $fail -eq 0 ] && echo "ALL CHECKS PASSED" || { echo "CHECKS FAILED"; exit 1; }
