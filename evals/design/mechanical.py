"""Mechanical extraction: units a judge can be asked about, found without a model.

Units get ordinal ids in document order (p01.. for prose, h01.. headings, c01.. code fences, g01.. mermaid diagrams, dup01..
near-duplicate sentence pairs). Ids are deterministic for identical bytes. Offsets are character offsets into the original text.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from . import text as T

HEDGES = re.compile(
    r"\b(probably|maybe|perhaps|TBD|TODO|not sure|unclear whether|to be decided|to be determined|we assume|assuming that|hopefully|should work|should be fine"
    r"|wahrscheinlich|vielleicht|eventuell|möglicherweise|vermutlich|noch offen|noch unklar|zu klären|zu entscheiden|wir nehmen an|unter der Annahme)\b",
    re.I,
)
LONG_PARAGRAPH_SENTENCES = 7
DUPLICATE_MIN_WORDS = 8
DUPLICATE_SIMILARITY = 0.5

PROSE_FORMS = {"paragraph", "list_item", "table", "blockquote", "header"}
CAPTION_MAX_CHARS = 160


@dataclass
class Unit:
    id: str
    kind: str  # paragraph | heading | code_block | diagram | duplicate_pair
    start: int
    end: int
    text: str
    sha8: str
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Extraction:
    units: list[Unit]
    covariates: dict
    spans: dict = field(default_factory=dict)

    def by_kind(self, kind: str) -> list[Unit]:
        return [u for u in self.units if u.kind == kind]

    def get(self, unit_id: str) -> Unit | None:
        return next((u for u in self.units if u.id == unit_id), None)

    def to_dict(self) -> dict:
        return {"units": [u.to_dict() for u in self.units], "covariates": self.covariates, "spans": self.spans}


_FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})\s*(\w*)")
_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_LIST = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
_RULE = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
_LINK_DEF = re.compile(r"^\s*\[[^\]]+\]:\s*\S+")


def _blocks(text: str):
    """Yield (form, start, end, body, meta) blocks in document order."""
    lines = text.split("\n")
    offs = []
    pos = 0
    for ln in lines:
        offs.append(pos)
        pos += len(ln) + 1
    i, n = 0, len(lines)
    if n and lines[0].strip() == "---":  # YAML front matter
        j = 1
        while j < n and lines[j].strip() != "---":
            j += 1
        i = j + 1 if j < n else 0
    para: list[int] = []

    def flush():
        nonlocal para
        if para:
            s, e = offs[para[0]], offs[para[-1]] + len(lines[para[-1]])
            yield_block = ("paragraph", s, e, text[s:e], {})
            para = []
            return yield_block
        return None

    while i < n:
        ln = lines[i]
        m = _FENCE.match(ln)
        if m:
            b = flush()
            if b:
                yield b
            marker, lang = m.group(2), m.group(3).lower()
            j = i + 1
            while j < n and not re.match(rf"^\s*{re.escape(marker[0])}{{{len(marker)},}}\s*$", lines[j]):
                j += 1
            body_lines = lines[i + 1 : j]
            s = offs[i + 1] if i + 1 < n else offs[i] + len(ln)
            e = (offs[j - 1] + len(lines[j - 1])) if j - 1 >= i + 1 else s
            form = "diagram" if lang == "mermaid" else "code_block"
            yield (form, s, e, "\n".join(body_lines), {"lang": lang, "lines": len(body_lines), "fence_start": offs[i], "fence_end": (offs[j] + len(lines[j])) if j < n else e})
            i = j + 1
            continue
        if not ln.strip():
            b = flush()
            if b:
                yield b
            i += 1
            continue
        hm = _HEADING.match(ln)
        if hm:
            b = flush()
            if b:
                yield b
            yield ("heading", offs[i], offs[i] + len(ln), hm.group(2), {"level": len(hm.group(1))})
            i += 1
            continue
        if _RULE.match(ln):
            b = flush()
            if b:
                yield b
            i += 1
            continue
        if ln.lstrip().startswith("|"):
            b = flush()
            if b:
                yield b
            j = i
            while j < n and lines[j].lstrip().startswith("|"):
                j += 1
            rows = [l.strip() for l in lines[i:j] if not _TABLE_SEP.match(l)]
            yield ("table", offs[i], offs[j - 1] + len(lines[j - 1]), "\n".join(rows), {"rows": len(rows)})
            i = j
            continue
        if _LINK_DEF.match(ln):  # [name]: url — a reference, not prose
            b = flush()
            if b:
                yield b
            i += 1
            continue
        if _LIST.match(ln):
            b = flush()
            if b:
                yield b
            j = i + 1
            while j < n and lines[j].strip() and not _LIST.match(lines[j]) and lines[j][:1].isspace() and not _FENCE.match(lines[j]) and not _HEADING.match(lines[j]):
                j += 1
            s, e = offs[i], offs[j - 1] + len(lines[j - 1])
            body = _LIST.sub("", lines[i], count=1) + "".join("\n" + l.strip() for l in lines[i + 1 : j])
            yield ("list_item", s, e, body.strip(), {})
            i = j
            continue
        if ln.lstrip().startswith(">"):
            b = flush()
            if b:
                yield b
            j = i
            while j < n and lines[j].lstrip().startswith(">"):
                j += 1
            s, e = offs[i], offs[j - 1] + len(lines[j - 1])
            body = "\n".join(re.sub(r"^\s*>\s?", "", l) for l in lines[i:j])
            yield ("blockquote", s, e, body.strip(), {})
            i = j
            continue
        para.append(i)
        i += 1
    b = flush()
    if b:
        yield b


# ---------------------------------------------------------------- mermaid

_MM_EDGE = re.compile(r"\s*(?:-->\s*\|[^|]*\||---\s*\|[^|]*\||-\.->\s*\|[^|]*\||==>\s*\|[^|]*\||--\s*[^-|>]+?\s*-->|-\.\s*[^.|>]+?\s*\.->|==\s*[^=|>]+?\s*==>|-->|---|-\.->|==>)\s*")
_MM_NODE = re.compile(r"^\s*([\w.-]+)\s*(\[\[.*?\]\]|\[\(.*?\)\]|\(\(.*?\)\)|\{\{.*?\}\}|\[.*?\]|\(.*?\)|\{.*?\}|>.*?\])?")
_MM_SKIP = re.compile(r"^\s*(subgraph|end\b|direction|style|classDef|class\b|click|linkStyle|%%|note|loop|alt|else|opt|par|rect|activate|deactivate)")


def parse_mermaid(src: str) -> dict:
    lines = [l for l in src.split("\n")]
    title = None
    body = lines
    if lines and lines[0].strip() == "---":
        j = 1
        while j < len(lines) and lines[j].strip() != "---":
            m = re.match(r"\s*title\s*:\s*(.+)", lines[j])
            if m:
                title = m.group(1).strip()
            j += 1
        body = lines[j + 1 :]
    body = [l for l in body if l.strip() and not l.strip().startswith("%%")]
    if not body:
        return {"type": None, "direction": None, "title": title, "nodes": 0, "labelled_nodes": 0, "edges": 0, "labelled_edges": 0, "subgraphs": 0, "has_key": False}
    head = body[0].strip()
    kind = head.split()[0].lower() if head else None
    direction = None
    m = re.match(r"(?:flowchart|graph)\s+(LR|RL|TB|TD|BT)", head, re.I)
    if m:
        direction = m.group(1).upper()
    nodes: dict[str, bool] = {}
    edges = labelled = subgraphs = 0
    has_key = False
    if kind in ("flowchart", "graph"):
        for ln in body[1:]:
            s = ln.strip()
            if s.lower().startswith("subgraph"):
                subgraphs += 1
                if re.search(r"\b(key|legend)\b", s, re.I):
                    has_key = True
                continue
            if _MM_SKIP.match(s):
                continue
            ops = _MM_EDGE.findall(s)
            segs = _MM_EDGE.split(s)
            for seg in segs:
                nm = _MM_NODE.match(seg)
                if nm and nm.group(1):
                    nid = nm.group(1)
                    nodes[nid] = nodes.get(nid, False) or bool(nm.group(2))
            for op in ops:
                edges += 1
                if "|" in op or re.search(r"--\s*\S.*\S\s*-->|-\.\s*\S.*\.->|==\s*\S.*==>", op):
                    labelled += 1
    elif kind == "sequencediagram":
        for ln in body[1:]:
            s = ln.strip()
            pm = re.match(r"(?:participant|actor)\s+(\S+)", s)
            if pm:
                nodes[pm.group(1)] = True
                continue
            em = re.match(r"(\S+?)\s*(-->>|->>|-->|->|--x|-x|--\)|-\))\s*(\S+?)\s*(:\s*(.*))?$", s)
            if em:
                nodes.setdefault(em.group(1), True)
                nodes.setdefault(em.group(3), True)
                edges += 1
                if em.group(5):
                    labelled += 1
    else:  # stateDiagram, classDiagram, erDiagram: count arrows and ': label' suffixes
        for ln in body[1:]:
            s = ln.strip()
            if _MM_SKIP.match(s):
                continue
            if re.search(r"-->|--|\|\|--|\|o--|}o--|}\|--|<\|--|\*--|o--", s):
                edges += 1
                if re.search(r":\s*\S", s):
                    labelled += 1
                for nid in re.findall(r"[A-Za-z_][\w]*", s.split(":")[0]):
                    if nid.lower() not in ("state", "class"):
                        nodes.setdefault(nid, True)
    return {
        "type": kind,
        "direction": direction,
        "title": title,
        "nodes": len(nodes),
        "labelled_nodes": sum(1 for v in nodes.values() if v),
        "edges": edges,
        "labelled_edges": labelled,
        "subgraphs": subgraphs,
        "has_key": has_key,
    }


# ---------------------------------------------------------------- extraction

def extract(text: str) -> Extraction:
    units: list[Unit] = []
    counters = {"p": 0, "h": 0, "c": 0, "g": 0}
    prev_prose: Unit | None = None
    seen_section = False
    for form, s, e, body, meta in _blocks(text):
        if form == "heading" and meta.get("level", 1) >= 2:
            seen_section = True
        if form == "paragraph" and not seen_section and body.lstrip().startswith("Status:"):
            form = "header"  # the status line under the title: metadata, not prose to judge
        if form in PROSE_FORMS:
            counters["p"] += 1
            sents = T.sentences(body) if form != "table" else [body] * meta.get("rows", 1)
            u = Unit(f"p{counters['p']:02d}", "paragraph", s, e, body, T.sha8(body), {"form": form, "sentences": len(sents), "words": T.word_count(body), **meta})
            prev_prose = u
        elif form == "heading":
            counters["h"] += 1
            u = Unit(f"h{counters['h']:02d}", "heading", s, e, body, T.sha8(body), meta)
        elif form == "code_block":
            counters["c"] += 1
            u = Unit(f"c{counters['c']:02d}", "code_block", s, e, body, T.sha8(body), meta)
        else:  # diagram
            counters["g"] += 1
            parsed = parse_mermaid(body)
            caption = None
            if prev_prose is not None and prev_prose.meta.get("form") == "paragraph" and len(prev_prose.text) <= CAPTION_MAX_CHARS and prev_prose.text.rstrip().endswith(("?", ":")):
                caption = prev_prose.text.strip()
            u = Unit(f"g{counters['g']:02d}", "diagram", s, e, body, T.sha8(body), {**meta, **parsed, "caption": caption})
        units.append(u)
    _mark_captions(units)
    units.extend(_duplicate_pairs(units, len(units)))
    hedges = _hedges(units)
    prose = [u for u in units if u.kind == "paragraph"]
    cov = {
        "words": sum(u.meta["words"] for u in prose) + sum(T.word_count(u.text) for u in units if u.kind == "heading"),
        "paragraphs": len(prose),
        "sentences": sum(u.meta["sentences"] for u in prose),
        "long_paragraphs": sum(1 for u in prose if u.meta["form"] == "paragraph" and u.meta["sentences"] > LONG_PARAGRAPH_SENTENCES),
        "headings": sum(1 for u in units if u.kind == "heading"),
        "code_lines": sum(u.meta["lines"] for u in units if u.kind == "code_block"),
        "code_blocks": sum(1 for u in units if u.kind == "code_block"),
        "diagrams": sum(1 for u in units if u.kind == "diagram"),
        "duplicate_pairs": sum(1 for u in units if u.kind == "duplicate_pair"),
        "stray_hedges": len(hedges),
    }
    return Extraction(units, cov, {"hedges": hedges, "open_questions": None, "overview": None})


def _mark_captions(units: list[Unit]) -> None:
    """A short paragraph ending in ':' or '?' right before a table, list, diagram or code block introduces it; judged with it, not alone."""
    for a, b in zip(units, units[1:]):
        if a.kind != "paragraph" or a.meta.get("form") != "paragraph" or len(a.text) > CAPTION_MAX_CHARS:
            continue
        if not a.text.rstrip().endswith((":", "?")):
            continue
        if b.kind in ("diagram", "code_block") or (b.kind == "paragraph" and b.meta.get("form") in ("table", "list_item")):
            a.meta["caption_for"] = b.id


def _sentence_spans(u: Unit) -> list[tuple[int, int, str]]:
    """(start, end, sentence) for each sentence of a prose unit, offsets into the document."""
    out = []
    pos = 0
    for s in T.sentences(u.text):
        at = u.text.find(s[:30], pos)
        if at < 0:
            at = pos
        out.append((u.start + at, u.start + at + len(s), s))
        pos = at + len(s)
    return out


def _duplicate_pairs(units: list[Unit], _n: int) -> list[Unit]:
    cands = []
    for u in units:
        if u.kind != "paragraph":
            continue
        for s, e, sent in _sentence_spans(u):
            toks = T.tokens(sent)
            if len(toks) >= DUPLICATE_MIN_WORDS:
                cands.append((u.id, s, e, sent, T.shingles(toks)))
    pairs: list[Unit] = []
    k = 0
    for i in range(len(cands)):
        for j in range(i + 1, len(cands)):
            a, b = cands[i], cands[j]
            if a[0] == b[0]:
                continue
            sim = T.jaccard(a[4], b[4])
            if sim >= DUPLICATE_SIMILARITY:
                k += 1
                txt = a[3] + "\n" + b[3]
                pairs.append(Unit(f"dup{k:02d}", "duplicate_pair", a[1], b[2], txt, T.sha8(txt), {
                    "a": {"unit": a[0], "start": a[1], "end": a[2], "text": a[3]},
                    "b": {"unit": b[0], "start": b[1], "end": b[2], "text": b[3]},
                    "similarity": round(sim, 3),
                }))
    return pairs


def _hedges(units: list[Unit]) -> list[dict]:
    hits = []
    for u in units:
        if u.kind != "paragraph":
            continue
        for s, e, sent in _sentence_spans(u):
            for m in HEDGES.finditer(sent):
                hits.append({"unit": u.id, "start": s, "end": e, "word": m.group(0), "sentence": sent})
    return hits
