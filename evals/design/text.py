"""Text utilities: normalisation with an offset map, quote finding, hashing, sentences and shingles.

Every quote a judge returns is verified against the document here. Verification runs on a normalised form of both sides (so
hard-wrapped lines, curly quotes and dropped backticks do not break a match) and maps the match back to original offsets, so the
quote stored in a run is a byte-exact substring of the document.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata

MARKER = re.compile(r"\[p\d{2,}\]\s?")
_QUOTES = {"‘": "'", "’": "'", "‚": "'", "“": '"', "”": '"', "„": '"'}
_DASHES = {"–": "-", "—": "-", "−": "-", "‐": "-", "‑": "-"}
_DROP = set("`*#|[]")


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha8(text: str) -> str:
    return sha256(text)[:8]


def normalize_map(text: str) -> tuple[str, list[int]]:
    """Return (normalised text, map from each normalised char to its original index)."""
    out: list[str] = []
    idx: list[int] = []
    in_space = False
    for i, ch in enumerate(text):
        if ch in _DROP:
            continue
        if ch in _QUOTES:
            ch = _QUOTES[ch]
        elif ch in _DASHES:
            ch = _DASHES[ch]
        elif ch == "…":
            for c in "...":
                out.append(c)
                idx.append(i)
            in_space = False
            continue
        if ch.isspace():
            if in_space:
                continue
            in_space = True
            out.append(" ")
            idx.append(i)
            continue
        in_space = False
        for c in unicodedata.normalize("NFKC", ch).casefold():
            out.append(c)
            idx.append(i)
    return "".join(out), idx


def normalize(text: str) -> str:
    return normalize_map(text)[0].strip()


def strip_markers(text: str) -> str:
    return MARKER.sub("", text)


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def find_quote(doc: str, quote: str, *, min_words: int = 4, max_words: int = 60, span_limit: int = 400) -> tuple[int, int] | None:
    """Locate `quote` in `doc`; return original (start, end) offsets or None.

    A quote containing "..." is an ordered list of parts, each at least four words, all within `span_limit` original characters.
    """
    quote = strip_markers(quote).strip()
    n = word_count(re.sub(r"\.\.\.|…", " ", quote))
    if n < min_words or n > max_words:
        return None
    norm_doc, idx = normalize_map(doc)
    parts = [p.strip() for p in re.split(r"\s*(?:\.\.\.|…)\s*", normalize(quote)) if p.strip()]
    if not parts:
        return None
    if len(parts) > 1 and any(word_count(p) < min_words for p in parts):
        return None
    pos = 0
    first_start = last_end = None
    for part in parts:
        at = norm_doc.find(part, pos)
        if at < 0:
            return None
        start, end = idx[at], idx[at + len(part) - 1] + 1
        if first_start is None:
            first_start = start
        elif end - first_start > span_limit:
            return None
        last_end = end
        pos = at + len(part)
    # include formatting characters glued to the match, so "**Name** (new)" and "`id` does" come back whole
    while first_start > 0 and doc[first_start - 1] in "`*":
        first_start -= 1
    while last_end < len(doc) and doc[last_end] in "`*":
        last_end += 1
    return first_start, last_end


_SENT_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[*_`])")


def sentences(text: str) -> list[str]:
    """Split prose into sentences. Crude on purpose: abbreviations and decimals may split wrongly, which only affects counts."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    return [s for s in _SENT_END.split(text) if s]


_TOKEN = re.compile(r"[a-z0-9]+")


def tokens(text: str) -> list[str]:
    return _TOKEN.findall(normalize(text))


def shingles(words: list[str], k: int = 3) -> set[tuple[str, ...]]:
    if len(words) < k:
        return {tuple(words)} if words else set()
    return {tuple(words[i : i + k]) for i in range(len(words) - k + 1)}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)
