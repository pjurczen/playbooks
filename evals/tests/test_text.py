from design import text as T


def test_find_quote_across_hard_wrapped_lines():
    doc = "The loader writes both stores and drops the summary memo\nwhenever it loads; the report builder empties both."
    q = "writes both stores and drops the summary memo whenever it loads"
    span = T.find_quote(doc, q)
    assert span is not None
    assert doc[span[0]:span[1]] == "writes both stores and drops the summary memo\nwhenever it loads"


def test_find_quote_tolerates_curly_quotes_backticks_and_case():
    doc = "Put one `ReportCache` in front of every read — it keeps “memory” in front of disk."
    q = 'put one ReportCache in front of every read - it keeps "memory" in front of disk'
    span = T.find_quote(doc, q)
    assert span is not None and doc[span[0]:span[1]].startswith("Put one `ReportCache`")


def test_find_quote_with_ellipsis_parts():
    doc = "Every source read goes through two caches that know nothing about each other: an in-process memo keyed by free-form strings and an on-disk file cache."
    q = "Every source read goes through two caches ... an in-process memo keyed by free-form strings"
    span = T.find_quote(doc, q)
    assert span is not None
    assert doc[span[0]:span[1]].startswith("Every source read") and doc[span[0]:span[1]].endswith("free-form strings")


def test_find_quote_rejects_short_long_and_missing():
    doc = "a b c d e f g h i j"
    assert T.find_quote(doc, "a b c") is None
    assert T.find_quote(doc, " ".join(["w"] * 61)) is None
    assert T.find_quote(doc, "these words are not there") is None


def test_sentences_and_shingles():
    s = T.sentences("One cache. Two tiers! Is it three? Yes.")
    assert s == ["One cache.", "Two tiers!", "Is it three?", "Yes."]
    a = T.shingles(["one", "cache", "with", "ttl"])
    b = T.shingles(["one", "cache", "with", "ttl", "now"])
    assert T.jaccard(a, b) > 0.5


def test_find_quote_includes_glued_formatting_and_ignores_table_pipes():
    doc = "Rows:\n| `Foo.bar` runs first | and then stops here |\n"
    span = T.find_quote(doc, "Foo.bar runs first and then stops here")
    assert span is not None and doc[span[0]:span[1]].startswith("`Foo.bar`")
