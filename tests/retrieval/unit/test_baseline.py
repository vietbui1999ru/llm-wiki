"""Baseline files: per-query metric values plus the top-10 pages (spec section 10), scored against the current labels."""
import json

import baseline

GOLDEN = {"queries": [
    {"id": "q1", "category": "exact", "relevant": [{"page": "wiki/a.md", "grade": 2}]},
    {"id": "q2", "category": "null", "relevant": []}]}
RESULTS = {"run": {"date": "20261006T000000Z", "index_hash": "abc", "settings": {"top_k": 20}},
           "rows": {"naive": [
               {"id": "q1", "category": "exact", "ranked": [f"wiki/p{i}.md" for i in range(12)] + ["wiki/a.md"],
                "metrics": {"ndcg@10": 0.0}, "latency_ms": 30, "non_wiki_hits": 0},
               {"id": "q2", "category": "null", "ranked": ["wiki/z.md"], "metrics": {}, "latency_ms": 31,
                "non_wiki_hits": 0}]}}


def test_build_keeps_per_query_metrics_scored_against_the_current_labels_and_only_the_top_ten_pages():
    b = baseline.build(RESULTS, GOLDEN, "lightrag", context={"golden_sha256": "g"})
    row = b["backends"]["naive"][0]
    assert b["version"] == 1 and b["system"] == "lightrag" and b["context"]["golden_sha256"] == "g"
    assert len(row["ranked"]) == 10 and "wiki/a.md" not in row["ranked"]
    assert row["metrics"]["ndcg@10"] == 0.0 and row["metrics"]["hit@3"] == 0 and row["id"] == "q1"
    assert b["backends"]["naive"][1]["metrics"]["ndcg@10"] is None  # null query: no relevance metrics


def test_build_rescoring_picks_up_label_changes_not_the_stale_metrics_in_the_results_file():
    relabelled = {"queries": [{"id": "q1", "category": "exact", "relevant": [{"page": "wiki/p0.md", "grade": 2}]},
                              GOLDEN["queries"][1]]}
    b = baseline.build(RESULTS, relabelled, "lightrag", context={})
    assert b["backends"]["naive"][0]["metrics"]["ndcg@10"] == 1.0


def test_context_records_run_provenance_and_marks_hashes_computed_at_build_time(tmp_path):
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki/a.md").write_text("x")
    g = tmp_path / "golden.json"
    g.write_text(json.dumps(GOLDEN))
    ctx = baseline.make_context(RESULTS, g, tmp_path, source="lightrag-x.json")
    assert ctx["index_hash"] == "abc" and ctx["source_run"] == "lightrag-x.json" and ctx["settings"] == {"top_k": 20}
    assert len(ctx["golden_sha256"]) == 64 and len(ctx["wiki_sha256"]) == 64
    assert ctx["provenance"] == "wiki and golden hashes computed at baseline build time (the source run predates recording)"


def test_dumps_round_trips_and_writes_one_line_per_query_row():
    b = baseline.build(RESULTS, GOLDEN, "lightrag", context={"golden_sha256": "g"})
    text = baseline.dumps(b)
    assert json.loads(text) == b
    assert sum(1 for line in text.splitlines() if line.strip().startswith('{"id"')) == 2  # two query rows, one line each


def test_context_prefers_hashes_recorded_by_the_run_itself(tmp_path):
    results = {"run": {**RESULTS["run"], "wiki_sha256": "w" * 64, "golden_sha256": "g" * 64}, "rows": {}}
    g = tmp_path / "golden.json"
    g.write_text("{}")
    ctx = baseline.make_context(results, g, tmp_path, source="x.json")
    assert ctx["wiki_sha256"] == "w" * 64 and ctx["golden_sha256"] == "g" * 64 and ctx["provenance"] == "recorded by the run"
