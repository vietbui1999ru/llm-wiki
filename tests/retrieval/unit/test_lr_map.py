"""LightRAG result mapping (spec: docs/specs/retrieval-eval-suite.md, section 3.3).

Page id = chunk_id minus its '-chunk-NNN' suffix (file_path is flattened to the basename, so it is never used).
Rank = order of first appearance in data.chunks, deduplicated. Pages reachable only through entities or
relationships are a separate diagnostic, never part of the ranking.
"""
import lr_map

SEP = "<SEP>"


def chunk(page, n=0):
    return {"chunk_id": f"{page}-chunk-{n:03d}", "file_path": page.split("/")[-1], "content": "x"}


def result(chunks, entities=(), relationships=()):
    return {"status": "success", "data": {"chunks": chunks, "entities": list(entities), "relationships": list(relationships)},
            "metadata": {"query_mode": "mix", "keywords": {"high_level": ["h"], "low_level": ["l1", "l2"]}}}


def test_page_of_strips_only_the_trailing_chunk_suffix():
    assert lr_map.page_of("wiki/concepts/a.md-chunk-007") == "wiki/concepts/a.md"
    assert lr_map.page_of("wiki/concepts/a-chunk-1.md-chunk-002") == "wiki/concepts/a-chunk-1.md"


def test_ranked_pages_dedupe_in_first_appearance_order():
    chunks = [chunk("wiki/b.md"), chunk("wiki/a.md"), chunk("wiki/b.md", 1), chunk("wiki/c.md")]
    assert lr_map.ranked_pages(result(chunks)) == ["wiki/b.md", "wiki/a.md", "wiki/c.md"]


def test_kg_only_pages_come_from_source_ids_and_exclude_ranked_pages():
    res = result([chunk("wiki/a.md")],
                 entities=[{"source_id": f"wiki/a.md-chunk-000{SEP}wiki/z.md-chunk-004"}],
                 relationships=[{"source_id": "wiki/y.md-chunk-001"}, {"source_id": ""}])
    assert lr_map.kg_only_pages(res) == ["wiki/y.md", "wiki/z.md"]


def test_diagnostics_count_entities_relations_and_keywords():
    res = result([chunk("wiki/a.md")], entities=[{}, {}], relationships=[{}])
    d = lr_map.diagnostics(res)
    assert d == {"entities": 2, "relationships": 1, "chunks": 1, "ll_keywords": 2, "hl_keywords": 1}


def test_a_failed_query_is_an_error_not_an_empty_ranking():
    import pytest
    with pytest.raises(RuntimeError, match="boom"):
        lr_map.ranked_pages({"status": "failure", "message": "boom", "data": {}})
