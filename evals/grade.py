#!/usr/bin/env python3
"""Mechanical grader for playbooks evals. Writes <run-dir>/grading.json in the skill-creator viewer format.

Usage: grade.py --eval N --run-dir DIR --repo DIR [--example-design PATH] [--fixture-design PATH]
Qualitative expectations are left to the grader subagent; this script only records what it can check.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

SECTIONS = ["Problem", "Approach", "Shape", "Contracts", "Guarantees", "Assumptions", "Open questions", "Risks", "Out of scope"]
STATEMENT = re.compile(r"^\s+(return\b|if\b|for\b|while\b|with\b|try:|except\b|raise\b|self\.\w+\s*=|\w+\s*=\s*[^=]|print\()")
FENCE = re.compile(r"```(\w*)\n(.*?)```", re.S)

def words(t): return len(t.split())
def fences(t): return FENCE.findall(t)
def sentences(t):
    t = FENCE.sub("", t); t = re.sub(r"\|.*?\n", "", t)
    return {s.strip().lower() for s in re.split(r"(?<=[.!?])\s+|\n", t) if len(s.strip()) > 40}
def has_bodies(text):
    bad = 0
    for lang, body in fences(text):
        if lang == "mermaid": continue
        for line in body.splitlines():
            if STATEMENT.match(line) and not line.strip().startswith(('"""', "#", "*", "/**", "//")):
                bad += 1
    return bad
def section(text, name):
    m = re.search(rf"^## {re.escape(name)}\s*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1) if m else None
def first(glob_dir, pattern):
    fs = sorted(Path(glob_dir).glob(pattern)) if Path(glob_dir).exists() else []
    return fs[0] if fs else None

def grade_1(out, repo, example):
    ex = []
    d = first(out / "docs/playbooks/designs", "*.md")
    ex.append(("A design file exists under docs/playbooks/designs/", d is not None, str(d) if d else "none found"))
    t = d.read_text() if d else ""
    heads = [h for h in re.findall(r"^## (.+?)\s*$", t, re.M)]
    order = [h for h in heads if h in SECTIONS]
    ex.append(("The design has the nine sections Problem, Approach, Shape, Contracts, Guarantees, Assumptions, Open questions, Risks, Out of scope, in that order", order == SECTIONS, f"headings: {heads}"))
    mm = sum(1 for l, _ in fences(t) if l == "mermaid")
    ex.append(("The design contains exactly one mermaid code fence", mm == 1, f"{mm} mermaid fences"))
    b = has_bodies(t)
    ex.append(("Every non-mermaid code fence in the design is signature-only (no statement bodies)", b == 0, f"{b} statement-looking lines in fences"))
    g = section(t, "Guarantees") or ""
    items = re.findall(r"^\s*\d+\.\s+(.*)$", g, re.M)
    last_ok = bool(items) and bool(re.search(r"must not change|unchanged|not change", items[-1], re.I))
    ex.append(("Guarantees are a numbered list of at least three and the last one states what must not change", len(items) >= 3 and last_ok, f"{len(items)} items; last: {items[-1][:80] if items else ''}"))
    a, o = section(t, "Assumptions") or "", section(t, "Open questions") or ""
    ex.append(("Assumptions and Open questions are present and non-empty (a 'None.' line counts)", a.strip() != "" and o.strip() != "", f"assumptions={len(a.strip())} chars, open={len(o.strip())} chars"))
    p = (section(t, "Problem") or "").strip()
    ex.append(("The Problem section ends with a sentence beginning 'Done means'", bool(re.search(r"Done means[^.]*\.?\s*$", p)), p[-120:]))
    ex.append(("The design is at most 1,200 words", 0 < words(t) <= 1200, f"{words(t)} words"))
    adr = first(out / "docs/adr", "*.md")
    at = adr.read_text() if adr else ""
    adr_ok = adr is not None and "`" not in at and len(at.splitlines()) <= 40 and re.search(r"proposed", at, re.I) and re.search(r"^## Alternativ", at, re.M | re.I) and re.search(r"^- ", at, re.M)
    ex.append(("An ADR exists under docs/adr/ with no backticks, at most 40 lines, a proposed status, and at least one alternative", bool(adr_ok), f"{adr}; lines={len(at.splitlines())}; backticks={at.count('`')}"))
    shared = sentences(t) & sentences(Path(example).read_text()) if example and Path(example).exists() else set()
    ex.append(("No sentence of the design is copied from the shipped example-design.md", len(shared) == 0, f"{len(shared)} shared sentences"))
    branch = subprocess.run(["git", "-C", str(repo), "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True).stdout.strip()
    logn = subprocess.run(["git", "-C", str(repo), "rev-list", "--count", "HEAD"], capture_output=True, text=True).stdout.strip()
    ex.append(("The design (and ADR) were committed on a feature branch, not on main", branch not in ("main", "master", "") and logn.isdigit() and int(logn) > 1, f"branch={branch}, commits={logn}"))
    return ex

def grade_2(out, repo, fixture_design):
    ex = []
    p = first(out / "docs/playbooks/plans", "*.md")
    t = p.read_text() if p else ""
    ex.append(("A plan file exists under docs/playbooks/plans/ and links the design by filename", p is not None and "unified-cache" in t and "Design" in t, str(p)))
    ex.append(("The plan has a Changes table whose header names the unit and the change", bool(re.search(r"^\|\s*Unit.*\|\s*Change", t, re.M | re.I)), ""))
    ex.append(("The plan has a call-site table with From and To columns", bool(re.search(r"^\|\s*Site\s*\|\s*From\s*\|\s*To", t, re.M | re.I)), ""))
    gs = re.findall(r"\bG\d+\b", t)
    ex.append(("At least two scenarios cite a design Guarantee by number (G1, G2, ...)", len(gs) >= 2, f"citations: {gs[:8]}"))
    ex.append(("Milestones are a table with a Done-when column", bool(re.search(r"^\|.*Done when.*\|", t, re.M | re.I)), ""))
    ex.append(("The plan has a 'Stop and ask' list", "stop and ask" in t.lower(), ""))
    shared = sentences(t) & sentences(Path(fixture_design).read_text()) if fixture_design else set()
    ex.append(("No sentence of the plan is copied from the design", len(shared) == 0, f"{len(shared)} shared: {list(shared)[:2]}"))
    long_f = [b for l, b in fences(t) if len(b.strip().splitlines()) > 5]
    ex.append(("No code fence in the plan contains statement bodies or exceeds five lines", has_bodies(t) == 0 and not long_f, f"bodies={has_bodies(t)}, long fences={len(long_f)}"))
    ex.append(("The plan is at most 900 words", 0 < words(t) <= 900, f"{words(t)} words"))
    return ex

def grade_3(out, repo):
    ex = []
    rep = sorted((out / "doc/adr/reporting").glob("*.md")) if (out / "doc/adr/reporting").exists() else []
    exp = sorted((out / "doc/adr/export").glob("*.md")) if (out / "doc/adr/export").exists() else []
    new = [f for f in rep if f.name != "2026-06-01-adr-quellen-dateicache.md"]
    named = bool(new) and bool(re.match(r"^\d{4}-\d{2}-\d{2}-adr-[a-z0-9-]+\.md$", new[0].name))
    ex.append(("Exactly one new ADR was created, in doc/adr/reporting/, named YYYY-MM-DD-adr-<kebab-topic>.md", len(new) == 1 and not exp and named, f"reporting={[f.name for f in rep]}, export={[f.name for f in exp]}"))
    t = new[0].read_text() if new else ""
    ex.append(("The ADR is written in German, headings included", bool(re.search(r"^## Kontext", t, re.M)) and bool(re.search(r"^## Entscheidung", t, re.M)) and not re.search(r"^## (Context|Decision|Consequences)", t, re.M), re.findall(r"^## .*$", t, re.M).__str__()))
    idx = out / "doc/asciidoc/09_architecture_decisions.adoc"
    it = idx.read_text() if idx.exists() else ""
    ex.append(("The index doc/asciidoc/09_architecture_decisions.adoc gained a row linking the new ADR", bool(new) and new[0].name in it, "index copied" if idx.exists() else "index not in outputs"))
    ex.append(("The ADR contains no backticks and no code fence", "`" not in t and bool(t), f"backticks={t.count('`')}"))
    ex.append(("The ADR is at most 40 lines", 0 < len(t.splitlines()) <= 40, f"{len(t.splitlines())} lines"))
    k = section(t, "Kontext") or ""
    shape = bool(re.search(r"Status", t)) and not re.search(r"^\s*\d+\.\s", k, re.M) and bool(re.search(r"^## Alternativ", t, re.M)) and bool(re.search(r"^## Konsequenzen", t, re.M))
    ex.append(("The ADR has a status line, a Kontext section in prose (no numbered list), an alternatives section with at least one entry, and a consequences section", shape, ""))
    ex.append(("The ADR does not copy the shape of the existing bloated ADR (no Referenzen section, no class listing)", not re.search(r"^## Referenzen", t, re.M) and "class " not in t, ""))
    return ex

def grade_4(out, repo):
    ex = []
    created = (out / "created-docs.txt").read_text().strip() if (out / "created-docs.txt").exists() else "MISSING"
    docs_now = [str(p.relative_to(repo)) for p in (repo / "docs").rglob("*") if p.is_file() and "playbooks" in str(p.relative_to(repo))] if (repo / "docs").exists() else []
    ex.append(("No file was created under docs/", created == "" and not docs_now, f"created-docs.txt='{created[:80]}', docs/playbooks files={docs_now}"))
    src = "".join(p.read_text() for p in (repo / "reportgen").glob("*.py"))
    ex.append(("MAX_RETRIES no longer appears in the repo and DEFAULT_MAX_RETRIES is used in cli.py", "DEFAULT_MAX_RETRIES" in (repo / "reportgen/cli.py").read_text() and not re.search(r"(?<!DEFAULT_)MAX_RETRIES", src), ""))
    r = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=repo, capture_output=True, text=True)
    ex.append(("The test suite passes after the change", r.returncode == 0, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]))
    tr = (Path(out).parent / "transcript.md")
    tt = tr.read_text().lower() if tr.exists() else ""
    ex.append(("The transcript shows brainstorming was not followed", tr.exists() and "brainstorming/skill.md" not in tt and "using brainstorming" not in tt, "transcript present" if tr.exists() else "no transcript"))
    logn = subprocess.run(["git", "-C", str(repo), "rev-list", "--count", "HEAD"], capture_output=True, text=True).stdout.strip()
    ex.append(("The change was committed", logn.isdigit() and int(logn) > 1, f"commits={logn}"))
    return ex

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", type=int, required=True); ap.add_argument("--run-dir", required=True); ap.add_argument("--repo", required=True)
    ap.add_argument("--example-design"); ap.add_argument("--fixture-design")
    a = ap.parse_args()
    run, repo, out = Path(a.run_dir), Path(a.repo), Path(a.run_dir) / "outputs"
    ex = {1: lambda: grade_1(out, repo, a.example_design), 2: lambda: grade_2(out, repo, a.fixture_design), 3: lambda: grade_3(out, repo), 4: lambda: grade_4(out, repo)}[a.eval]()
    exps = [{"text": t, "passed": bool(p), "evidence": str(e)[:300]} for t, p, e in ex]
    passed = sum(1 for e in exps if e["passed"])
    result = {"expectations": exps, "summary": {"passed": passed, "failed": len(exps) - passed, "total": len(exps), "pass_rate": round(passed / len(exps), 2) if exps else 0}}
    # time and tokens are read by the aggregator from the sibling timing.json; emitting them here would shadow it
    (run / "grading.json").write_text(json.dumps(result, indent=2))
    print(f"eval {a.eval}: {passed}/{len(exps)} passed -> {run / 'grading.json'}")

if __name__ == "__main__":
    main()
