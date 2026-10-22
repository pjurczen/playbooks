from design import rubrics as R


def test_frontmatter_block_and_inline_lists():
    meta, body = R.parse_frontmatter("---\nid: x\nneeds: [mechanical, judge]\nsources:\n  - One source, with a comma\n  - Two\nbatch: 5\n---\nbody text\n")
    assert meta["needs"] == ["mechanical", "judge"] and meta["sources"] == ["One source, with a comma", "Two"] and meta["batch"] == 5
    assert body == "body text"


def test_shipped_rubrics_load_and_match_file_names():
    rs = R.load_rubrics()
    assert rs and all(r.id == r.path.stem for r in rs.values())
    assert all(r.sources for r in rs.values()), "every rubric names its sources"
