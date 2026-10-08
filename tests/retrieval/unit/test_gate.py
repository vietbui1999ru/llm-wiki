"""Regression gate logic (spec: docs/specs/retrieval-eval-suite.md, section 10).

Warn when the mean nDCG@10 delta vs the baseline is below -epsilon; fail when additionally the paired bootstrap 95% CI of
the delta lies entirely below 0. Must-hit floor: a must_hit query that was in the top 3 at baseline and no longer is, fails.
Both sides are re-scored against the current labels, so a label edit never looks like a regression.
"""
import gate

TOP = ["wiki/a.md"]                      # target at rank 1: nDCG 1.0
SECOND = ["wiki/x.md", "wiki/a.md"]      # rank 2: nDCG 0.631
FOURTH = ["wiki/x.md", "wiki/y.md", "wiki/z.md", "wiki/a.md"]   # rank 4: out of the top 3
MISS = ["wiki/x.md"]


def golden(n, must_hit=()):
    return {"queries": [{"id": f"q{i}", "category": "exact", "must_hit": f"q{i}" in must_hit,
                         "relevant": [{"page": "wiki/a.md", "grade": 2}]} for i in range(n)]}


def rows(rankings):
    return [{"id": f"q{i}", "category": "exact", "ranked": r} for i, r in enumerate(rankings)]


def test_identical_runs_are_ok_with_zero_delta():
    out = gate.compare_backend(rows([TOP] * 20), rows([TOP] * 20), golden(20))
    assert out["verdict"] == "OK" and out["delta"] == 0 and out["n"] == 20


def test_a_consistent_large_drop_fails_because_the_whole_ci_is_below_zero():
    out = gate.compare_backend(rows([TOP] * 20), rows([MISS] * 20), golden(20))
    assert out["verdict"] == "FAIL" and out["delta"] == -1.0 and out["hi"] < 0


def test_a_mean_drop_beyond_epsilon_with_a_ci_that_spans_zero_only_warns():
    # 1 of 20 queries falls from rank 1 to a miss: mean delta -0.05, but 19 queries are unchanged so the CI includes 0
    out = gate.compare_backend(rows([TOP] * 20), rows([MISS] + [TOP] * 19), golden(20))
    assert out["verdict"] == "WARN" and out["delta"] < -gate.EPSILON and out["hi"] >= 0


def test_a_drop_smaller_than_epsilon_and_any_improvement_are_ok():
    assert gate.compare_backend(rows([TOP] * 100), rows([SECOND] + [TOP] * 99), golden(100))["verdict"] == "OK"
    assert gate.compare_backend(rows([SECOND] * 10), rows([TOP] * 10), golden(10))["verdict"] == "OK"


def test_losing_a_must_hit_query_from_the_top_3_fails_even_when_the_mean_is_fine():
    base, cur = rows([TOP] * 20), rows([FOURTH] + [TOP] * 19)
    out = gate.compare_backend(base, cur, golden(20, must_hit={"q0"}), epsilon=0.5)
    assert out["verdict"] == "FAIL" and out["must_hit_lost"] == ["q0"]


def test_a_must_hit_query_that_was_already_outside_the_top_3_at_baseline_is_not_blamed():
    out = gate.compare_backend(rows([FOURTH] + [TOP] * 19), rows([MISS] + [TOP] * 19), golden(20, must_hit={"q0"}),
                               epsilon=0.5)
    assert out["must_hit_lost"] == [] and out["verdict"] == "OK"


def test_queries_missing_from_the_baseline_are_excluded_and_counted():
    out = gate.compare_backend(rows([TOP] * 10), rows([TOP] * 15), golden(15))
    assert out["n"] == 10 and out["n_new"] == 5


def system_file(rankings_by_backend, **context):
    return {"context": context, "backends": {b: rows(r) for b, r in rankings_by_backend.items()}}


def run_file(rankings_by_backend, **run):
    return {"run": run, "rows": {b: rows(r) for b, r in rankings_by_backend.items()}}


def test_check_passes_when_every_backend_is_ok_and_reports_warnings_without_failing():
    base = system_file({"a": [TOP] * 20, "b": [TOP] * 20})
    cur = run_file({"a": [TOP] * 20, "b": [MISS] + [TOP] * 19})   # b warns (delta -0.05, CI spans zero)
    report = gate.check(base, cur, golden(20))
    assert report["exit"] == 0 and [x["verdict"] for x in report["backends"]] == ["OK", "WARN"]
    assert "GATE: PASS (1 warning)" in gate.format_report(report)


def test_check_fails_the_gate_on_a_failing_or_missing_backend():
    base = system_file({"a": [TOP] * 20, "b": [TOP] * 20})
    failing = gate.check(base, run_file({"a": [TOP] * 20, "b": [MISS] * 20}), golden(20))
    assert failing["exit"] == 1 and "GATE: FAIL" in gate.format_report(failing)
    missing = gate.check(base, run_file({"a": [TOP] * 20}), golden(20))
    assert missing["exit"] == 1 and missing["backends"][1]["verdict"] == "MISSING"
    assert gate.check(base, run_file({"a": [TOP] * 20}), golden(20), backends=["a"])["exit"] == 0


def test_a_rebuilt_lightrag_index_makes_a_failing_backend_report_only():
    base = system_file({"naive": [TOP] * 20}, index_hash="old")
    report = gate.check(base, run_file({"naive": [MISS] * 20}, index_hash="new"), golden(20))
    only = report["backends"][0]
    assert only["verdict"] == "FAIL" and only["report_only"] and report["exit"] == 0
    assert any("index" in n and "re-baseline" in n for n in only["notes"])
    assert "REPORT-ONLY" in gate.format_report(report)


def test_provenance_differences_are_notes_not_verdicts():
    base = system_file({"a": [TOP] * 20}, wiki_sha256="w1", settings={"top_k": 20, "cosine": 0.3})
    cur = run_file({"a": [TOP] * 20}, wiki_sha256="w2", settings={"top_k": 20, "cosine": 0.9})
    notes = gate.check(base, cur, golden(20))["backends"][0]["notes"]
    assert any("wiki content changed" in n for n in notes) and any("cosine" in n and "top_k" not in n for n in notes)
    assert gate.check(base, cur, golden(20))["exit"] == 0


def test_a_changed_qmd_collection_is_noted_because_files_outside_wiki_can_shift_rankings():
    base = system_file({"a": [TOP] * 20}, qmd_collection_sha256="q1")
    changed = gate.check(base, run_file({"a": [TOP] * 20}, qmd_collection_sha256="q2"), golden(20))["backends"][0]["notes"]
    assert any("qmd collection changed" in n and "outside wiki" in n for n in changed)
    unrecorded = gate.check(base, run_file({"a": [TOP] * 20}), golden(20))["backends"][0]["notes"]
    assert any("no qmd collection hash" in n for n in unrecorded)
    same = gate.check(base, run_file({"a": [TOP] * 20}, qmd_collection_sha256="q1"), golden(20))["backends"][0]["notes"]
    assert same == []


def test_a_qmd_collection_that_changed_during_the_run_is_noted_as_mixed_results():
    base = system_file({"a": [TOP] * 20}, qmd_collection_sha256="q1")
    cur = run_file({"a": [TOP] * 20}, qmd_collection_sha256="q1", qmd_collection_changed_during_run=True)
    notes = gate.check(base, cur, golden(20))["backends"][0]["notes"]
    assert any("changed during the run" in n and "mix" in n for n in notes)
    steady = run_file({"a": [TOP] * 20}, qmd_collection_sha256="q1", qmd_collection_changed_during_run=False)
    assert gate.check(base, steady, golden(20))["backends"][0]["notes"] == []


def test_labels_are_the_current_ones_for_both_sides():
    relabelled = {"queries": [{"id": "q0", "category": "exact", "must_hit": False,
                               "relevant": [{"page": "wiki/x.md", "grade": 2}]}]}
    out = gate.compare_backend(rows([TOP]), rows([TOP]), relabelled)  # both sides now miss: no delta, not a regression
    assert out["delta"] == 0 and out["verdict"] == "OK"
