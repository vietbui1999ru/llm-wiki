"""qmd bench output parsing and scoring (spec: docs/specs/retrieval-eval-suite.md, sections 3.2, 3.4, 7.1)."""
import pytest

import run_qmd

GOLDEN = {"version": 1, "queries": [
    {"id": "q-1", "query": "x", "category": "exact", "relevant": [{"page": "wiki/concepts/a.md", "grade": 2}]},
    {"id": "q-2", "query": "y", "category": "null", "relevant": []}]}


def bench(top_files_q1, top_files_q2=()):
    def backend(files):
        return {"bm25": {"top_files": list(files), "latency_ms": 7}}
    return {"results": [{"id": "q-1", "backends": backend(top_files_q1)},
                        {"id": "q-2", "backends": backend(top_files_q2)}]}


def test_to_pages_strips_collection_prefix_and_counts_non_wiki_hits():
    pages, non_wiki = run_qmd.to_pages([
        "qmd://wiki/raw/clip.md", "qmd://wiki/wiki/concepts/a.md", "qmd://wiki/log.md"])
    assert pages == ["wiki/concepts/a.md"] and non_wiki == 2


def test_score_bench_scores_wiki_pages_only_and_keeps_latency_and_diagnostics():
    rows = run_qmd.score_bench(bench(["qmd://wiki/raw/clip.md", "qmd://wiki/wiki/concepts/a.md"]), GOLDEN)
    row = rows["bm25"][0]
    assert row["id"] == "q-1" and row["category"] == "exact"
    assert row["metrics"]["mrr"] == 1.0  # raw/ hit is dropped before ranking, so a.md is rank 1
    assert row["latency_ms"] == 7 and row["non_wiki_hits"] == 1 and row["ranked"] == ["wiki/concepts/a.md"]


def test_null_query_row_records_whether_anything_was_returned():
    rows = run_qmd.score_bench(bench([], ["qmd://wiki/wiki/concepts/a.md"]), GOLDEN)
    assert rows["bm25"][1]["metrics"]["returned_any"] is True


def test_unknown_query_id_in_bench_output_is_an_error():
    bad = {"results": [{"id": "q-99", "backends": {"bm25": {"top_files": [], "latency_ms": 1}}}]}
    with pytest.raises(KeyError):
        run_qmd.score_bench(bad, GOLDEN)


def test_format_report_prints_headline_metrics_ci_n_and_caveats():
    rows = run_qmd.score_bench(bench(["qmd://wiki/wiki/concepts/a.md"]), GOLDEN)
    text = run_qmd.format_report(rows)
    assert "ndcg@10" in text and "recall@5" in text and "1.000 [1.000, 1.000]  n=1" in text
    assert "n/a  n=0" in text and "optimistic" in text  # null category has no relevance mean; caveats always present


def test_format_report_shows_how_many_wiki_pages_survive_the_filter():
    rows = run_qmd.score_bench(bench(["qmd://wiki/raw/x.md", "qmd://wiki/raw/y.md", "qmd://wiki/wiki/concepts/a.md"]), GOLDEN)
    text = run_qmd.format_report(rows)
    assert f"bm25: wiki pages kept per query 0.5 of {run_qmd.RESULTS}, non-wiki hits 1.0" in text  # q-1 keeps 1 of 3, q-2 keeps 0


def test_cli_top_files_reads_the_file_field_in_rank_order():
    out = '[{"file": "qmd://wiki/wiki/a.md", "score": 0.9}, {"file": "qmd://wiki/raw/b.md", "score": 0.5}]'
    assert run_qmd.cli_top_files(out) == ["qmd://wiki/wiki/a.md", "qmd://wiki/raw/b.md"]


def test_collect_builds_bench_shaped_output_so_scoring_is_unchanged():
    calls = []

    def runner(backend, query):
        calls.append((backend, query))
        return [f"qmd://wiki/wiki/{backend}.md"], 12

    out = run_qmd.collect(GOLDEN["queries"], runner, backends=("bm25", "full"))
    assert calls == [("bm25", "x"), ("full", "x"), ("bm25", "y"), ("full", "y")]
    first = out["results"][0]
    assert first["id"] == "q-1" and first["backends"]["full"] == {"top_files": ["qmd://wiki/wiki/full.md"], "latency_ms": 12}
    assert run_qmd.score_bench(out, GOLDEN)["bm25"][1]["id"] == "q-2"


def test_command_for_each_backend_asks_for_many_results_in_the_wiki_collection():
    assert run_qmd.command("bm25", "q")[:3] == ["qmd", "search", "q"]
    assert "--no-rerank" in run_qmd.command("hybrid", "q") and "--no-rerank" not in run_qmd.command("full", "q")
    for backend in run_qmd.BACKENDS:
        cmd = run_qmd.command(backend, "q")
        assert cmd[cmd.index("-n") + 1] == str(run_qmd.RESULTS) and cmd[cmd.index("-c") + 1] == "wiki" and "--json" in cmd


def test_format_report_accepts_other_systems_caveats_and_request_size():
    rows = run_qmd.score_bench(bench(["qmd://wiki/wiki/concepts/a.md"]), GOLDEN)
    text = run_qmd.format_report(rows, caveats="CUSTOM CAVEAT", requested=10)
    assert "CUSTOM CAVEAT" in text and "optimistic" not in text and "of 10, non-wiki" in text


def test_rescore_recomputes_metrics_from_saved_rankings_after_a_label_change():
    rows = run_qmd.score_bench(bench(["qmd://wiki/wiki/concepts/b.md", "qmd://wiki/wiki/concepts/a.md"]), GOLDEN)
    assert rows["bm25"][0]["metrics"]["mrr"] == 0.5
    relabelled = {"queries": [{**GOLDEN["queries"][0], "relevant": [{"page": "wiki/concepts/b.md", "grade": 2}]},
                              GOLDEN["queries"][1]]}
    again = run_qmd.rescore(rows, relabelled)
    assert again["bm25"][0]["metrics"]["mrr"] == 1.0
    assert again["bm25"][0]["ranked"] == rows["bm25"][0]["ranked"] and again["bm25"][0]["latency_ms"] == 7


def test_report_gives_per_category_n_and_ci():
    rows = run_qmd.score_bench(bench(["qmd://wiki/wiki/concepts/a.md"]), GOLDEN)
    out = run_qmd.report(rows, "ndcg@10")["bm25"]
    assert out["exact"]["n"] == 1 and out["exact"]["mean"] == 1.0 and out["null"]["n"] == 0
