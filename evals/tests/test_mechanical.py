from design import mechanical as M

SAMPLE = """# Title

Status: approved · Ticket: X-1

## Problem

First paragraph sentence one. Sentence two.

- item one is here
  continued line
- item two

| a | b |
|---|---|
| 1 | 2 |

What replaces what?

```mermaid
flowchart LR
  A[Loader] -->|get| C[Cache]
  B[Builder] --> C
  D --> C
```

```python
def f(): ...
```

> quoted thing

We will probably need this. Maybe not.
"""


def test_blocks_and_ids():
    ex = M.extract(SAMPLE)
    kinds = [(u.id, u.kind, u.meta.get("form")) for u in ex.units if u.kind != "duplicate_pair"]
    assert kinds[0] == ("h01", "heading", None)
    assert ("p01", "paragraph", "header") in kinds  # the Status line
    assert ("p03", "paragraph", "list_item") in kinds
    assert ("p05", "paragraph", "table") in kinds and ex.get("p05").meta["rows"] == 2
    assert ex.get("p06").meta.get("caption_for") == "g01"  # "What replaces what?" introduces the diagram
    assert any(k[1] == "diagram" and k[0] == "g01" for k in kinds)
    assert any(k[1] == "code_block" and k[0] == "c01" for k in kinds)
    assert any(k[2] == "blockquote" for k in kinds)
    list_item = ex.get("p03")
    assert list_item.text == "item one is here\ncontinued line"
    assert ex.covariates["code_lines"] == 1 and ex.covariates["diagrams"] == 1


def test_offsets_point_at_the_text(fixture_design):
    ex = M.extract(fixture_design)
    for u in ex.units:
        if u.kind in ("paragraph", "heading", "code_block", "diagram"):
            assert fixture_design[u.start:u.end].strip() != ""
    assert ex.covariates["diagrams"] == 1 and ex.covariates["code_blocks"] == 3


def test_mermaid_parse():
    ex = M.extract(SAMPLE)
    g = ex.by_kind("diagram")[0].meta
    assert g["type"] == "flowchart" and g["direction"] == "LR"
    assert g["nodes"] == 4 and g["labelled_nodes"] == 3
    assert g["edges"] == 3 and g["labelled_edges"] == 1
    assert g["caption"] == "What replaces what?"


def test_fixture_mermaid_has_subgraphs(fixture_design):
    g = M.extract(fixture_design).by_kind("diagram")[0].meta
    assert g["subgraphs"] == 2 and g["nodes"] == 10 and g["labelled_nodes"] == 10 and g["edges"] == 9
    assert g["caption"] == "What replaces what?"


def test_hedges_and_long_paragraphs():
    ex = M.extract(SAMPLE)
    assert ex.covariates["stray_hedges"] == 2
    long = M.extract("## X\n\n" + " ".join(f"Sentence {i} ends here." for i in range(9)) + "\n")
    assert long.covariates["long_paragraphs"] == 1


def test_duplicate_pairs():
    a = "The cache owns key naming and validity for every entry in the system."
    b = "Note again that the cache owns key naming and validity for every entry in the system."
    ex = M.extract(f"## A\n\n{a}\n\n## B\n\nSomething else entirely here.\n\n{b}\n")
    dups = ex.by_kind("duplicate_pair")
    assert len(dups) == 1 and dups[0].meta["a"]["unit"] == "p01" and dups[0].meta["similarity"] >= 0.5


def test_link_definitions_are_not_prose():
    ex = M.extract("# T\n\nSee [the story][s] for context.\n\n[s]: https://example.org/story\n[other]: ../x.md\n")
    assert [u.meta["form"] for u in ex.by_kind("paragraph")] == ["paragraph"]
