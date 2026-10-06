"""LightRAG latency sampling: plan, stage split and cache check (spec section 9). The runs themselves are not unit-tested.

Graph modes call the keyword-extraction LLM once per (mode, query) unless that exact entry is cached. The runner works on
a scratch copy of the index whose keyword-cache entries are stripped, so the first call per (mode, query) is a genuine
miss on the real query text and its immediate repeat is a hit. (Suffixed variant texts, as used for qmd, make the LLM
return empty low-level keywords, which LightRAG does not cache, so they were rejected.) naive uses no LLM.
"""
import pytest

import latency_lightrag

QUERIES = [{"id": f"q-{i}", "query": f"query {i}"} for i in range(1, 5)]


def test_strip_keyword_entries_removes_only_keyword_cache_entries():
    cache = {"hybrid:keywords:aa": {"x": 1}, "mix:keywords:bb": {"x": 2}, "default:extract:cc": {"x": 3},
             "default:summary:dd": {"x": 4}}
    kept, removed = latency_lightrag.strip_keyword_entries(cache)
    assert removed == 2 and set(kept) == {"default:extract:cc", "default:summary:dd"}


def test_plan_gives_naive_plain_samples_and_graph_modes_pairs_on_the_real_query_text():
    plan = latency_lightrag.make_plan(QUERIES, {"naive": 2, "local": 1, "mix": 1}, seed=1)
    count = lambda m, k: sum(1 for s in plan if s["backend"] == m and s["kind"] == k)
    assert count("naive", "plain") == 8 and count("local", "pair") == 4 and count("mix", "pair") == 4
    assert {s["text"] for s in plan} == {q["query"] for q in QUERIES}


def test_a_second_pass_for_a_graph_mode_is_refused_because_its_cache_would_already_be_warm():
    with pytest.raises(ValueError, match="one pass"):
        latency_lightrag.make_plan(QUERIES, {"local": 2}, seed=1)


def test_plan_is_deterministic_for_a_seed():
    args = (QUERIES, {"naive": 1, "local": 1})
    assert latency_lightrag.make_plan(*args, seed=1) == latency_lightrag.make_plan(*args, seed=1)
    assert latency_lightrag.make_plan(*args, seed=1) != latency_lightrag.make_plan(*args, seed=2)


def test_stage_split_attributes_llm_and_embedding_time_and_leaves_the_rest_to_lookup():
    sample = latency_lightrag.stage_split(total_ms=1000, llm_ms=600, embed_ms=150, llm_calls=1)
    assert sample == {"total_ms": 1000, "llm_ms": 600, "embed_ms": 150, "lookup_ms": 250, "llm_calls": 1}


def test_stage_split_never_reports_negative_lookup_time_when_calls_overlap():
    assert latency_lightrag.stage_split(total_ms=500, llm_ms=400, embed_ms=300, llm_calls=1)["lookup_ms"] == 0


def test_report_shows_each_stage_per_mode_condition_and_the_cache_check():
    records = [{"backend": "mix", "id": f"q-{i}", "pass": 1, "kind": "pair", "text": "t",
                "cold": latency_lightrag.stage_split(2000 + i, 1500, 200, 1),
                "warm": latency_lightrag.stage_split(400 + i, 0, 150, 0)} for i in range(3)]
    records.append({"backend": "naive", "id": "q-1", "pass": 1, "kind": "plain", "text": "t",
                    "plain": latency_lightrag.stage_split(300, 0, 120, 0)})
    text = latency_lightrag.format_report(records)
    assert "mix / cold" in text and "mix / warm" in text and "naive / plain" in text and "llm_ms" in text
    assert "cold samples that made no LLM call: 0 of 3" in text and "warm samples that made one: 0 of 3" in text


def test_cold_start_summary_reports_each_phase_over_the_probes():
    probes = [{"wall_ms": 9000, "import_ms": 3000, "init_ms": 2000, "first_naive_ms": 900, "second_naive_ms": 300},
              {"wall_ms": 8000, "import_ms": 2500, "init_ms": 1900, "first_naive_ms": 800, "second_naive_ms": 310}]
    s = latency_lightrag.summarize_cold_starts(probes)
    assert s["wall_ms"]["n"] == 2 and s["wall_ms"]["max"] == 9000 and s["first_naive_ms"]["p50"] == 850
    assert latency_lightrag.summarize_cold_starts([]) == {}


def test_cache_check_flags_cold_samples_without_an_llm_call_and_warm_samples_with_one():
    flat = [{"backend": "mix", "condition": "cold", "llm_calls": 1}, {"backend": "mix", "condition": "cold", "llm_calls": 0},
            {"backend": "mix", "condition": "warm", "llm_calls": 1}, {"backend": "mix", "condition": "warm", "llm_calls": 0},
            {"backend": "naive", "condition": "plain", "llm_calls": 0}]
    assert latency_lightrag.cache_check(flat) == {"mix": {"cold_hit": 1, "cold_n": 2, "warm_miss": 1, "warm_n": 2}}
