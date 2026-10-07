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


def test_labels_are_the_current_ones_for_both_sides():
    relabelled = {"queries": [{"id": "q0", "category": "exact", "must_hit": False,
                               "relevant": [{"page": "wiki/x.md", "grade": 2}]}]}
    out = gate.compare_backend(rows([TOP]), rows([TOP]), relabelled)  # both sides now miss: no delta, not a regression
    assert out["delta"] == 0 and out["verdict"] == "OK"
