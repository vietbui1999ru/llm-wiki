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


def test_to_bench_shapes_runs_for_the_shared_scorer_and_keeps_diagnostics_aside():
    runs = {"q-1": {"naive": {"result": result([chunk("wiki/a.md"), chunk("wiki/b.md")]), "ms": 40, "llm_calls": 0},
                    "mix": {"result": result([chunk("wiki/b.md")], entities=[{"source_id": "wiki/z.md-chunk-001"}]),
                            "ms": 900, "llm_calls": 1}}}
    bench, extras = lr_map.to_bench(runs)
    assert bench["results"][0] == {"id": "q-1", "backends": {
        "naive": {"top_files": ["wiki/a.md", "wiki/b.md"], "latency_ms": 40},
        "mix": {"top_files": ["wiki/b.md"], "latency_ms": 900}}}
    assert extras["q-1"]["mix"]["kg_only_pages"] == ["wiki/z.md"] and extras["q-1"]["mix"]["llm_calls"] == 1
    assert extras["q-1"]["naive"]["entities"] == 0
    assert extras["q-1"]["naive"]["chunk_ids"] == ["wiki/a.md-chunk-000", "wiki/b.md-chunk-000"]  # kept for audit


def test_nothing_found_is_an_empty_ranking_not_an_error():
    # LightRAG reports status failure with this message when no chunk passes the thresholds: a legitimate empty result
    # (and exactly what a retrieval regression looks like), so it must be scored, not crash the run
    nothing = {"status": "failure", "message": "No relevant document chunks found.", "data": {}, "metadata": {}}
    assert lr_map.ranked_pages(nothing) == [] and lr_map.kg_only_pages(nothing) == []
    assert lr_map.diagnostics(nothing) == {"entities": 0, "relationships": 0, "chunks": 0, "ll_keywords": 0, "hl_keywords": 0}


def test_to_bench_handles_a_nothing_found_result_end_to_end():
    nothing = {"status": "failure", "message": "No relevant document chunks found.", "data": {}, "metadata": {}}
    bench, extras = lr_map.to_bench({"q-1": {"naive": {"result": nothing, "ms": 20, "llm_calls": 0}}})
    assert bench["results"][0]["backends"]["naive"]["top_files"] == []
    assert extras["q-1"]["naive"]["chunk_ids"] == [] and extras["q-1"]["naive"]["chunks"] == 0


def test_a_failed_query_is_an_error_not_an_empty_ranking():
    import pytest
    with pytest.raises(RuntimeError, match="boom"):
        lr_map.ranked_pages({"status": "failure", "message": "boom", "data": {}})
