"""LightRAG latency sampling: plan, stage split and cache check (spec section 9). The runs themselves are not unit-tested.

Graph modes call the keyword-extraction LLM once per (mode, query) unless that exact text is cached, so a cold sample
uses a text unique to the mode, pass and run (miss guaranteed) and its warm repeat hits the cache. naive uses no LLM.
"""
import latency_lightrag

QUERIES = [{"id": f"q-{i}", "query": f"query {i}"} for i in range(1, 5)]


def test_variants_are_distinct_across_modes_passes_and_runs():
    texts = {latency_lightrag.variant("agent harness", m, p, salt)
             for m in ("local", "global", "hybrid", "mix") for p in (1, 2) for salt in (3, 4)}
    assert len(texts) == 16 and all(t.startswith("agent harness") for t in texts)


def test_plan_gives_naive_plain_samples_and_graph_modes_pairs():
    plan = latency_lightrag.make_plan(QUERIES, {"naive": 2, "local": 1, "mix": 1}, seed=1, salt=5)
    count = lambda m, k: sum(1 for s in plan if s["backend"] == m and s["kind"] == k)
    assert count("naive", "plain") == 8 and count("local", "pair") == 4 and count("mix", "pair") == 4
    golden_texts = {q["query"] for q in QUERIES}
    assert all(s["text"] in golden_texts for s in plan if s["kind"] == "plain")
    pair_texts = [s["text"] for s in plan if s["kind"] == "pair"]
    assert len(set(pair_texts)) == len(pair_texts) and not set(pair_texts) & golden_texts


def test_plan_is_deterministic_for_a_seed():
    args = (QUERIES, {"naive": 1, "local": 1}, 1, 5)
    assert latency_lightrag.make_plan(*args) == latency_lightrag.make_plan(*args)
    assert latency_lightrag.make_plan(*args) != latency_lightrag.make_plan(QUERIES, {"naive": 1, "local": 1}, 2, 5)


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
