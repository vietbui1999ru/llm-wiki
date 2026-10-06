"""Cross-system comparison (spec: docs/specs/retrieval-eval-suite.md, section 8): paired, per query."""
import pytest

import compare


def rows(values):
    """One system's scored rows: {query id: ndcg@10}; None marks a query where the metric is undefined."""
    return [{"id": qid, "category": "c", "metrics": {"ndcg@10": v}} for qid, v in values.items()]


def test_paired_values_align_by_query_id_and_drop_undefined_pairs():
    a = rows({"q1": 1.0, "q2": 0.5, "q3": None, "q4": 0.2})
    b = rows({"q4": 0.0, "q1": 0.5, "q2": None, "q3": 0.9})
    assert compare.paired_values(a, b, "ndcg@10") == ([1.0, 0.2], [0.5, 0.0])


def test_compare_reports_mean_difference_ci_p_value_and_n():
    a = rows({f"q{i}": 1.0 for i in range(10)})
    b = rows({f"q{i}": 0.0 for i in range(10)})
    out = compare.compare(a, b, "ndcg@10")
    assert out["n"] == 10 and out["diff"] == 1.0 and out["lo"] == 1.0 and out["hi"] == 1.0
    assert out["p"] < 0.01


def test_identical_systems_have_zero_difference_and_p_one():
    a = rows({f"q{i}": 0.5 for i in range(6)})
    out = compare.compare(a, a, "ndcg@10")
    assert out["diff"] == 0.0 and out["p"] == pytest.approx(1.0)


def test_no_overlapping_queries_gives_n_zero_not_a_crash():
    out = compare.compare(rows({"q1": 1.0}), rows({"q2": 1.0}), "ndcg@10")
    assert out["n"] == 0 and out["diff"] is None


def test_hole_at_10_is_the_share_of_top_pages_not_in_the_labels():
    gold = {"queries": [{"id": "q1", "relevant": [{"page": "wiki/a.md", "grade": 2}]}, {"id": "q2", "relevant": []}]}
    sys_rows = [{"id": "q1", "ranked": ["wiki/a.md", "wiki/x.md", "wiki/y.md"]},
                {"id": "q2", "ranked": ["wiki/z.md"]}]
    assert compare.hole_at_10(sys_rows, gold) == 3 / 4  # x, y, z unjudged of 4 returned pages


def test_format_comparison_lists_every_system_the_designated_pairs_and_the_mde_warning():
    def sys_rows(v, phase=0):  # per-query values alternate, so paired differences have a non-zero sd
        return [{"id": f"q{i}", "category": "exact", "ranked": ["wiki/a.md"],
                 "metrics": {"ndcg@10": v + ((i + phase) % 2) * 0.1, "recall@5": v,
                             "recall@10": v + ((i + phase) % 2) * 0.1}} for i in range(8)]
    gold = {"queries": [{"id": f"q{i}", "category": "exact", "relevant": [{"page": "wiki/a.md", "grade": 2}]}
                        for i in range(8)]}
    systems = {"qmd full": sys_rows(0.50), "lightrag mix": sys_rows(0.51, phase=1),
               "qmd hybrid": sys_rows(0.60), "lightrag naive": sys_rows(0.61, phase=1)}
    text = compare.format_comparison(systems, gold)
    assert all(name in text for name in systems)
    assert "qmd full vs lightrag mix ndcg@10" in text and "qmd hybrid vs lightrag naive recall@10" in text
    assert "BELOW MDE" in text  # a 0.01 difference is far below the detectable effect at n=8


def test_min_detectable_effect_is_reported_from_the_observed_sd():
    a = rows({f"q{i}": float(i % 2) for i in range(20)})
    b = rows({f"q{i}": 0.5 for i in range(20)})
    out = compare.compare(a, b, "ndcg@10")
    assert out["mde"] == pytest.approx(2.8 * 0.5 / 20 ** 0.5, rel=0.1)  # 2.8 * sd / sqrt(n), sd of paired diffs ~0.5
