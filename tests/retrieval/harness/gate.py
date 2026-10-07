"""Regression gate over committed baselines (stdlib only).

Spec: docs/specs/retrieval-eval-suite.md, section 10. Per system backend: warn when the mean nDCG@10 delta against the
baseline is below -epsilon; fail when additionally the paired bootstrap 95% CI of the delta lies entirely below 0; fail
when a must_hit query that was in the top 3 at baseline is not any more. Baseline and current rankings are both
re-scored against the CURRENT golden labels, so editing a label never shows up as a regression. Queries added to the
golden set since the baseline are excluded from the comparison and counted.
"""
import score

EPSILON = 0.03  # initial value, not sourced (spec 10); revisit with observed variance


def _metrics(rows, golden):
    by_id = {q["id"]: q for q in golden["queries"]}
    return {r["id"]: score.score_query(r["ranked"], by_id[r["id"]]["relevant"]) for r in rows if r["id"] in by_id}


def compare_backend(baseline_rows, current_rows, golden, epsilon=EPSILON):
    """Verdict OK / WARN / FAIL (ERROR when no query is comparable) for one backend, with the evidence."""
    base, cur = _metrics(baseline_rows, golden), _metrics(current_rows, golden)
    common = [i for i in cur if i in base]
    pairs = [(cur[i]["ndcg@10"], base[i]["ndcg@10"]) for i in common]
    n = len(score.paired_diffs([p[0] for p in pairs], [p[1] for p in pairs]))
    out = {"n": n, "n_new": len(cur) - len(common), "delta": None, "lo": None, "hi": None, "must_hit_lost": []}
    if n == 0:
        return {**out, "verdict": "ERROR"}
    out["delta"], out["lo"], out["hi"] = score.paired_bootstrap_ci([p[0] for p in pairs], [p[1] for p in pairs])
    must = {q["id"] for q in golden["queries"] if q.get("must_hit")}
    out["must_hit_lost"] = [i for i in common if i in must and base[i]["hit@3"] == 1 and cur[i]["hit@3"] == 0]
    dropped = out["delta"] < -epsilon
    out["verdict"] = "FAIL" if out["must_hit_lost"] or (dropped and out["hi"] < 0) else "WARN" if dropped else "OK"
    return out
