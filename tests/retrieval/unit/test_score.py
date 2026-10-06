"""Metric tests with hand-computed expectations (spec: docs/specs/retrieval-eval-suite.md, section 6).

Fixture used throughout:  ranked = [A, B, C, D, E];  relevant = {B: grade 2, D: grade 1}.
Worked by hand:
  recall@3 = 1/2 (only B in top 3)      recall@5 = 2/2
  precision@3 = 1/3                     hit@1 = 0, hit@3 = 1
  MRR = 1/2 (first relevant B at rank 2)
  DCG@5  = 2/log2(3) + 1/log2(5) = 1.26186 + 0.43068 = 1.69254
  IDCG@5 = 2/log2(2) + 1/log2(3) = 2 + 0.63093       = 2.63093
  nDCG@5 = 1.69254 / 2.63093 = 0.6433
"""
import pytest

import score

RANKED = ["A", "B", "C", "D", "E"]
RELEVANT = [{"page": "B", "grade": 2}, {"page": "D", "grade": 1}]


def test_hand_computed_metrics():
    m = score.score_query(RANKED, RELEVANT, ks=(1, 3, 5))
    assert m["recall@3"] == 0.5 and m["recall@5"] == 1.0
    assert m["precision@3"] == pytest.approx(1 / 3)
    assert m["hit@1"] == 0 and m["hit@3"] == 1
    assert m["mrr"] == 0.5
    assert m["ndcg@5"] == pytest.approx(0.6433, abs=1e-3)


def test_perfect_ranking_has_ndcg_one():
    m = score.score_query(["B", "D", "X"], RELEVANT, ks=(3,))
    assert m["ndcg@3"] == pytest.approx(1.0) and m["mrr"] == 1.0


def test_duplicates_are_collapsed_keeping_first_rank():
    m = score.score_query(["A", "A", "B"], RELEVANT, ks=(3,))
    assert m["mrr"] == 0.5  # B is rank 2 after de-duplication, not rank 3


def test_k_larger_than_the_list_is_fine():
    assert score.score_query(["B"], RELEVANT, ks=(10,))["recall@10"] == 0.5


def test_null_query_has_no_relevance_metrics_but_reports_what_was_returned():
    m = score.score_query(["A", "B"], [], ks=(3,))
    assert m["recall@3"] is None and m["ndcg@3"] is None and m["mrr"] is None
    assert m["returned_any"] is True
    assert score.score_query([], [], ks=(3,))["returned_any"] is False
