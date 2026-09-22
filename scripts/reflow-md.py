#!/usr/bin/env python3
"""Hard-reflow markdown at 160 columns: unwrap paragraphs, list items and blockquotes, rewrap.
Untouched: frontmatter, fences (mermaid etc.), tables, headings, rules, tag lines.
Invariant: the whitespace-collapsed content of every file is identical before and after.

Usage: git ls-files '*.md' | xargs scripts/reflow-md.py   (-q: print only when something changed)"""
import re, sys

WIDTH = 160
FENCE = re.compile(r'^(\s*)(`{3,}|~{3,})')
HEADING = re.compile(r'^\s{0,3}#{1,6}(\s|$)')
TABLE = re.compile(r'^\s*\|')
HR = re.compile(r'^\s*([-*_])(\s*\1){2,}\s*$')
LIST = re.compile(r'^(\s*)([-*+]|\d+[.)])(\s+)(\S.*)$')
TAG = re.compile(r'^\s*</?[A-Za-z][A-Za-z0-9_-]*[^>]*>\s*$')
QUOTE = re.compile(r'^\s*>')
BLANK = re.compile(r'^\s*$')
UNSAFE_START = re.compile(r'^([-*+]|\d+[.)]|#{1,6}|>|\||-{3,}|\*{3,}|_{3,})$')

report = {"indented_para": [], "over": []}


def is_block_start(line):
    return bool(BLANK.match(line) or FENCE.match(line) or HEADING.match(line) or TABLE.match(line)
                or HR.match(line) or LIST.match(line) or TAG.match(line) or QUOTE.match(line))


def tokenize(text):
    protected = [False] * len(text)
    for m in re.finditer(r'(`+)(.+?)\1', text):
        for k in range(m.start(), m.end()):
            protected[k] = True
    tokens, cur = [], []
    for k, ch in enumerate(text):
        if ch == ' ' and not protected[k]:
            if cur:
                tokens.append(''.join(cur))
                cur = []
        else:
            cur.append(ch)
    if cur:
        tokens.append(''.join(cur))
    return tokens


def wrap(text, first_prefix, cont_prefix):
    tokens = tokenize(text)
    lines, cur = [], []

    def width(prefix, toks):
        return len(prefix) + len(' '.join(toks))

    for tok in tokens:
        prefix = first_prefix if not lines else cont_prefix
        if cur and width(prefix, cur + [tok]) > WIDTH:
            if (UNSAFE_START.match(tok) or (tok.startswith('*') and cur[-1].endswith('*'))) and len(cur) > 1:
                carry = cur.pop()
                lines.append(cur)
                cur = [carry, tok]
            else:
                lines.append(cur)
                cur = [tok]
        else:
            cur.append(tok)
    if cur:
        lines.append(cur)
    out = []
    for i, toks in enumerate(lines):
        out.append((first_prefix if i == 0 else cont_prefix) + ' '.join(toks))
    return out


def format_lines(lines, fname):
    out = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if BLANK.match(line):
            out.append('')
            i += 1
            continue
        m = FENCE.match(line)
        if m:
            fence = m.group(2)
            out.append(line.rstrip())
            i += 1
            while i < n:
                out.append(lines[i].rstrip())
                closing = lines[i].strip()
                i += 1
                if closing.startswith(fence[0] * len(fence)) and set(closing) <= {fence[0]}:
                    break
            continue
        if HEADING.match(line) or TABLE.match(line) or HR.match(line) or TAG.match(line):
            out.append(line.rstrip())
            i += 1
            continue
        if QUOTE.match(line):
            inner = []
            while i < n and QUOTE.match(lines[i]):
                inner.append(re.sub(r'^\s*> ?', '', lines[i]))
                i += 1
            for l in format_lines(inner, fname):
                out.append('>' if l == '' else '> ' + l)
            continue
        m = LIST.match(line)
        if m:
            indent, marker, spacing, text = m.groups()
            first_prefix = indent + marker + spacing
            cont_prefix = ' ' * len(first_prefix)
            parts = [text.strip()]
            i += 1
            while i < n and not is_block_start(lines[i]):
                parts.append(lines[i].strip())
                i += 1
            out.extend(wrap(' '.join(parts), first_prefix, cont_prefix))
            continue
        # paragraph
        indent = re.match(r'^(\s*)', line).group(1)
        if len(indent) >= 4:
            report["indented_para"].append(f"{fname}:{i + 1}")
        parts = [line.strip()]
        i += 1
        while i < n and not is_block_start(lines[i]):
            parts.append(lines[i].strip())
            i += 1
        out.extend(wrap(' '.join(parts), indent, indent))
    return out


def reflow(fname):
    src = open(fname).read()
    lines = src.split('\n')
    head = []
    if lines and lines[0].strip() == '---':
        j = 1
        while j < len(lines) and lines[j].strip() != '---':
            j += 1
        head, lines = lines[:j + 1], lines[j + 1:]
    body = format_lines(lines, fname)
    out = '\n'.join(head + body)
    out = out.rstrip('\n') + '\n'
    norm = lambda t: ' '.join(re.sub(r'^(\s*>)+ ?', '', t, flags=re.M).split())
    assert norm(out) == norm(src), f"content changed: {fname}"
    for k, l in enumerate(out.split('\n'), 1):
        if len(l) > WIDTH:
            report["over"].append(f"{fname}:{k} ({len(l)})")
    if out != src:
        open(fname, 'w').write(out)
        return True
    return False


quiet = "-q" in sys.argv
files = [f for f in sys.argv[1:] if f != "-q"]
changed = [f for f in files if reflow(f)]
if quiet:
    for f in changed:
        print(f"reflowed {f}")
    sys.exit(0)
print(f"reflowed {len(changed)} of {len(files)} files")
if report["indented_para"]:
    print("paragraphs indented >= 4 (check they were not code):", *report["indented_para"], sep="\n  ")
print(f"{len(report['over'])} lines still over {WIDTH}:")
for l in report["over"]:
    print("  ", l)
