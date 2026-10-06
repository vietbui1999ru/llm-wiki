"""qmd latency sampling plan, resume and report (spec section 9). The CLI calls themselves are not unit-tested."""
import json

import latency_qmd

QUERIES = [{"id": f"q-{i}", "query": f"query {i}"} for i in range(1, 6)]


def test_cold_expansion_variants_differ_from_the_original_and_from_each_other():
    v1, v2 = latency_qmd.variant("agent harness", 1), latency_qmd.variant("agent harness", 2)
    assert len({"agent harness", v1, v2}) == 3 and v1.startswith("agent harness")


def test_plan_gives_bm25_one_condition_and_llm_backends_warm_and_cold_with_the_requested_passes():
    plan = latency_qmd.make_plan(QUERIES, {"bm25": 2, "hybrid": 2, "full": 1}, seed=1)
    count = lambda b, c: sum(1 for s in plan if s["backend"] == b and s["condition"] == c)
    assert count("bm25", "plain") == 10 and count("bm25", "warm") == 0
    assert count("hybrid", "warm") == 10 and count("hybrid", "cold") == 10
    assert count("full", "warm") == 5 and count("full", "cold") == 5


def test_plan_is_shuffled_but_deterministic_and_each_cold_sample_uses_a_fresh_variant_text():
    a = latency_qmd.make_plan(QUERIES, {"hybrid": 2}, seed=1)
    assert a == latency_qmd.make_plan(QUERIES, {"hybrid": 2}, seed=1) and a != latency_qmd.make_plan(QUERIES, {"hybrid": 2}, seed=2)
    cold = [(s["id"], s["text"]) for s in a if s["condition"] == "cold"]
    assert len(set(cold)) == len(cold) and all(t != f"query {i[2:]}" for i, t in cold)


def test_done_keys_let_a_rerun_skip_samples_already_recorded(tmp_path):
    path = tmp_path / "run.jsonl"
    plan = latency_qmd.make_plan(QUERIES, {"bm25": 1}, seed=1)
    path.write_text(json.dumps({**plan[0], "total_ms": 5}) + "\n" + json.dumps({**plan[1], "total_ms": 6}) + "\n")
    assert latency_qmd.pending(plan, latency_qmd.read_samples(path)) == plan[2:]


def test_report_groups_by_backend_and_condition_with_stage_rows():
    samples = [{"backend": "full", "condition": "warm", "total_ms": t, "rerank_ms": t - 100} for t in (1000, 2000, 3000)]
    text = latency_qmd.format_report(samples)
    assert "full" in text and "warm" in text and "rerank_ms" in text and "n=3" in text
