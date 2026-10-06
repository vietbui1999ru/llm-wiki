"""qmd latency sampling plan, resume and report (spec section 9). The CLI calls themselves are not unit-tested.

Cache state is deterministic by construction: a cold sample uses a text no backend has run before (expansions are
cached by query text across backends), and its warm sample is an immediate repeat of the same text.
"""
import json

import latency_qmd

QUERIES = [{"id": f"q-{i}", "query": f"query {i}"} for i in range(1, 6)]


def test_variants_are_distinct_across_backends_passes_and_runs():
    texts = {latency_qmd.variant("agent harness", b, p, salt)
             for b in ("vector", "hybrid", "full") for p in (1, 2) for salt in (11, 12)}
    assert len(texts) == 12 and all(t.startswith("agent harness") for t in texts)


def test_plan_gives_bm25_plain_samples_and_llm_backends_cold_warm_pairs():
    plan = latency_qmd.make_plan(QUERIES, {"bm25": 2, "hybrid": 2, "full": 1}, seed=1, salt=5)
    count = lambda b, k: sum(1 for s in plan if s["backend"] == b and s["kind"] == k)
    assert count("bm25", "plain") == 10 and count("hybrid", "pair") == 10 and count("full", "pair") == 5
    assert all(s["text"] == next(q["query"] for q in QUERIES if q["id"] == s["id"]) for s in plan if s["kind"] == "plain")


def test_plan_is_shuffled_but_deterministic_and_no_pair_text_repeats_or_equals_a_golden_query():
    a = latency_qmd.make_plan(QUERIES, {"vector": 2, "hybrid": 2, "full": 2}, seed=1, salt=5)
    assert a == latency_qmd.make_plan(QUERIES, {"vector": 2, "hybrid": 2, "full": 2}, seed=1, salt=5)
    assert a != latency_qmd.make_plan(QUERIES, {"vector": 2, "hybrid": 2, "full": 2}, seed=2, salt=5)
    texts = [s["text"] for s in a if s["kind"] == "pair"]
    assert len(set(texts)) == len(texts) and not set(texts) & {q["query"] for q in QUERIES}


def test_pending_skips_samples_already_recorded_by_backend_id_and_pass(tmp_path):
    path = tmp_path / "run.jsonl"
    plan = latency_qmd.make_plan(QUERIES, {"bm25": 1}, seed=1, salt=5)
    path.write_text("".join(json.dumps({**s, "plain": {"total_ms": 5}}) + "\n" for s in plan[:2]))
    assert latency_qmd.pending(plan, latency_qmd.read_samples(path)) == plan[2:]


def test_flatten_turns_records_into_one_sample_per_measurement_with_its_condition():
    records = [{"backend": "full", "id": "q-1", "pass": 1, "kind": "pair", "text": "t",
                "cold": {"total_ms": 20000, "expansion_ms": 3000}, "warm": {"total_ms": 17000, "expansion_ms": 0}},
               {"backend": "bm25", "id": "q-1", "pass": 1, "kind": "plain", "text": "t", "plain": {"total_ms": 300}}]
    flat = latency_qmd.flatten(records)
    assert [(s["backend"], s["condition"]) for s in flat] == [("full", "cold"), ("full", "warm"), ("bm25", "plain")]
    assert flat[0]["total_ms"] == 20000


def test_cache_check_counts_cold_samples_that_hit_and_warm_samples_that_missed():
    flat = [{"backend": "hybrid", "condition": "cold", "expansion_ms": 0}, {"backend": "hybrid", "condition": "cold", "expansion_ms": 2800},
            {"backend": "hybrid", "condition": "warm", "expansion_ms": 2000}, {"backend": "hybrid", "condition": "warm", "expansion_ms": 1},
            {"backend": "vector", "condition": "cold", "total_ms": 5000}]
    check = latency_qmd.cache_check(flat)
    assert check == {"hybrid": {"cold_hit": 1, "cold_n": 2, "warm_miss": 1, "warm_n": 2}}  # vector prints no expansion time


def test_report_groups_by_backend_and_condition_and_shows_the_cache_check():
    records = [{"backend": "full", "id": f"q-{i}", "pass": 1, "kind": "pair", "text": "t",
                "cold": {"total_ms": 20000 + i, "rerank_ms": 14000, "expansion_ms": 3000},
                "warm": {"total_ms": 17000 + i, "rerank_ms": 14000, "expansion_ms": 0}} for i in range(3)]
    text = latency_qmd.format_report(records)
    assert "full / cold" in text and "full / warm" in text and "rerank_ms" in text and "n=3" in text
    assert "cache check" in text and "cold samples with a cache hit: 0 of 3" in text
