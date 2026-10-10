"""Statistics tests (spec section 8): bootstrap CIs, paired comparison, per-category summaries."""
import pytest

import score


def test_constant_values_have_a_degenerate_interval():
    assert score.bootstrap_ci([0.7] * 20) == pytest.approx((0.7, 0.7, 0.7))


def test_bootstrap_is_deterministic_for_a_seed_and_brackets_the_mean():
    vals = [0.0, 1.0, 0.5, 1.0, 0.25, 0.75, 1.0, 0.0, 0.5, 0.9]
    a, b = score.bootstrap_ci(vals, seed=7), score.bootstrap_ci(vals, seed=7)
    assert a == b
    mean, lo, hi = a
    assert lo <= mean <= hi


def test_none_values_are_ignored_and_empty_input_is_safe():
    assert score.bootstrap_ci([None, 1.0, 1.0])[0] == 1.0
    assert score.bootstrap_ci([None]) == (None, None, None)


def test_identical_systems_have_p_value_one():
    x = [0.2, 0.9, 0.5, 0.0, 1.0, 0.4]
    assert score.paired_permutation_test(x, list(x)) == 1.0


def test_a_clearly_better_system_is_significant_and_its_interval_excludes_zero():
    better, worse = [1.0] * 30, [0.0] * 30
    assert score.paired_permutation_test(better, worse, seed=1) < 0.01
    mean, lo, hi = score.paired_bootstrap_ci(better, worse)
    assert mean == 1.0 and lo > 0


def test_pairs_with_a_missing_side_are_dropped():
    assert score.paired_diffs([1.0, None, 0.5], [0.0, 1.0, None]) == [1.0]


def test_summarize_groups_by_category_and_adds_an_overall_row():
    rows = [{"category": "exact", "metrics": {"ndcg@10": 1.0}},
            {"category": "exact", "metrics": {"ndcg@10": 0.0}},
            {"category": "null", "metrics": {"ndcg@10": None}},
            {"category": "alias", "metrics": {"ndcg@10": 0.5}}]
    s = score.summarize(rows, "ndcg@10")
    assert s["exact"]["n"] == 2 and s["exact"]["mean"] == 0.5
    assert s["null"]["n"] == 0 and s["null"]["mean"] is None
    assert s["ALL"]["n"] == 3 and s["ALL"]["mean"] == 0.5
