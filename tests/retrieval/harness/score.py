"""Retrieval metrics and statistics for the wiki evaluation suite (stdlib only).

Spec: docs/specs/retrieval-eval-suite.md, sections 6 and 8. Page-level scoring: callers map each
system's results to wiki page paths first. Gain is the grade itself (2 primary, 1 supporting).
"""
import math
import random


def _dedupe(ranked):
    """Keep the first occurrence of each page, preserving order."""
    seen, out = set(), []
    for page in ranked:
        if page not in seen:
            seen.add(page)
            out.append(page)
    return out


def _dcg(grades):
    return sum(g / math.log2(i + 2) for i, g in enumerate(grades))


def score_query(ranked, relevant, ks=(1, 3, 5, 10)):
    """Metrics for one query.

    ranked:   page paths in rank order (duplicates collapsed to first rank).
    relevant: [{"page": ..., "grade": 1|2}, ...]; empty means a null query (nothing should be found).
    """
    ranked = _dedupe(ranked)
    grades = {r["page"]: r["grade"] for r in relevant}
    m = {"returned_any": bool(ranked)}
    first = next((i + 1 for i, p in enumerate(ranked) if p in grades), None)
    m["mrr"] = None if not grades else (1 / first if first else 0.0)
    ideal = sorted(grades.values(), reverse=True)
    for k in ks:
        top = ranked[:k]
        hits = sum(p in grades for p in top)
        if not grades:
            m.update({f"recall@{k}": None, f"precision@{k}": None, f"hit@{k}": None, f"ndcg@{k}": None})
            continue
        m[f"recall@{k}"] = hits / len(grades)
        m[f"precision@{k}"] = hits / k
        m[f"hit@{k}"] = 1 if hits else 0
        m[f"ndcg@{k}"] = _dcg([grades.get(p, 0) for p in top]) / _dcg(ideal[:k])
    return m


def bootstrap_ci(values, n_boot=2000, seed=0, alpha=0.05):
    """Percentile bootstrap CI for the mean. None values are ignored. Returns (mean, lo, hi)."""
    vals = [v for v in values if v is not None]
    if not vals:
        return None, None, None
    n, rng = len(vals), random.Random(seed)
    means = sorted(sum(rng.choices(vals, k=n)) / n for _ in range(n_boot))
    return sum(vals) / n, means[int(alpha / 2 * n_boot)], means[int((1 - alpha / 2) * n_boot) - 1]


def paired_diffs(a, b):
    """Per-query differences a - b, dropping queries where either side is None."""
    return [x - y for x, y in zip(a, b) if x is not None and y is not None]


def paired_permutation_test(a, b, n_perm=10000, seed=0):
    """Two-sided sign-flip permutation test on the mean paired difference. Returns a p-value."""
    d = paired_diffs(a, b)
    if not d:
        return None
    observed, rng = abs(sum(d) / len(d)), random.Random(seed)
    extreme = sum(abs(sum(x if rng.random() < 0.5 else -x for x in d) / len(d)) >= observed - 1e-12
                  for _ in range(n_perm))
    return (extreme + 1) / (n_perm + 1)


def paired_bootstrap_ci(a, b, **kw):
    """Bootstrap CI for the mean paired difference a - b."""
    return bootstrap_ci(paired_diffs(a, b), **kw)


def summarize(rows, metric, group_key="category"):
    """Mean and 95% CI of one metric per group, plus an 'ALL' row. rows: {group_key, metrics: {...}}."""
    groups = {"ALL": []}
    for r in rows:
        groups.setdefault(r[group_key], [])
        groups[r[group_key]].append(r["metrics"][metric])
        groups["ALL"].append(r["metrics"][metric])
    out = {}
    for name, vals in groups.items():
        mean, lo, hi = bootstrap_ci(vals)
        out[name] = {"n": sum(v is not None for v in vals), "mean": mean, "lo": lo, "hi": hi}
    return out
