"""Paired comparison of two scored systems (stdlib only).

Spec: docs/specs/retrieval-eval-suite.md, section 8: per-query paired differences, a paired permutation test and
a paired bootstrap CI on the mean difference, fixed seed. The minimum detectable effect is recomputed from the
observed sd of the paired differences (about 2.8 * sd / sqrt(n) for 80% power at alpha 0.05).
"""
import statistics

import score


def paired_values(a_rows, b_rows, metric):
    """Aligned metric values for the queries both systems answered, dropping pairs where either is undefined."""
    b_by_id = {r["id"]: r["metrics"][metric] for r in b_rows}
    pairs = [(r["metrics"][metric], b_by_id[r["id"]]) for r in a_rows
             if r["id"] in b_by_id and r["metrics"][metric] is not None and b_by_id[r["id"]] is not None]
    return [p[0] for p in pairs], [p[1] for p in pairs]


def hole_at_10(rows, golden):
    """Share of returned top-10 pages that no label covers (label-sparsity diagnostic, spec section 6)."""
    judged = {q["id"]: {r["page"] for r in q["relevant"]} for q in golden["queries"]}
    tops = [(r["id"], p) for r in rows for p in r["ranked"][:10]]
    return sum(p not in judged[qid] for qid, p in tops) / len(tops) if tops else None


def compare(a_rows, b_rows, metric):
    """a minus b: mean difference, 95% CI, permutation p-value, n and the minimum detectable effect."""
    a, b = paired_values(a_rows, b_rows, metric)
    if not a:
        return {"n": 0, "diff": None, "lo": None, "hi": None, "p": None, "mde": None}
    diff, lo, hi = score.paired_bootstrap_ci(a, b)
    sd = statistics.stdev(score.paired_diffs(a, b)) if len(a) > 1 else None
    return {"n": len(a), "diff": diff, "lo": lo, "hi": hi, "p": score.paired_permutation_test(a, b),
            "mde": None if sd is None else 2.8 * sd / len(a) ** 0.5}


DESIGNATED = (("qmd full", "lightrag mix"), ("qmd hybrid", "lightrag naive"))  # fixed in advance (spec 8)
CATEGORIES = ("exact", "paraphrase", "alias", "relational", "overview")


def load_systems(qmd_path, lightrag_path, gold):
    """{system name: rows}, every system re-scored against the same current labels."""
    import json
    from pathlib import Path

    import run_qmd

    systems = {}
    for prefix, path in (("qmd", qmd_path), ("lightrag", lightrag_path)):
        for backend, rows in run_qmd.rescore(json.loads(Path(path).read_text())["rows"], gold).items():
            systems[f"{prefix} {backend}"] = rows
    return systems


def format_comparison(systems, gold):
    cell = lambda g: "n/a" if g["mean"] is None else f"{g['mean']:.3f} [{g['lo']:.3f}, {g['hi']:.3f}]"
    out = ["system          nDCG@10 [95% CI]       Recall@5  Recall@10  Hole@10   n"]
    for name, rows in systems.items():
        n10, r5, r10 = (score.summarize(rows, m)["ALL"] for m in ("ndcg@10", "recall@5", "recall@10"))
        out.append(f"{name:<15} {cell(n10):<22} {r5['mean']:.3f}     {r10['mean']:.3f}      "
                   f"{hole_at_10(rows, gold):.2f}     {n10['n']}")
    out.append("\nnDCG@10 by category (mean; n per category: " + ", ".join(
        f"{c} {sum(q['category'] == c for q in gold['queries'])}" for c in CATEGORIES) + ")")
    for name, rows in systems.items():
        by = score.summarize(rows, "ndcg@10")
        out.append(f"{name:<15} " + "  ".join(f"{c[:5]} {by[c]['mean']:.2f}" if c in by and by[c]["mean"] is not None
                                              else f"{c[:5]} n/a" for c in CATEGORIES))
    out.append("\nPre-designated paired comparisons (first minus second), nDCG@10 and Recall@10:")
    for a, b in DESIGNATED:
        for metric in ("ndcg@10", "recall@10"):
            c = compare(systems[a], systems[b], metric)
            small = "  BELOW MDE: do not claim a difference" if abs(c["diff"]) < c["mde"] else ""
            out.append(f"  {a} vs {b} {metric}: diff {c['diff']:+.3f} [{c['lo']:+.3f}, {c['hi']:+.3f}] "
                       f"p={c['p']:.3f} n={c['n']} mde={c['mde']:.3f}{small}")
    return "\n".join(out)


def main(argv=None):
    import argparse

    import golden as golden_mod

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--qmd", required=True)
    ap.add_argument("--lightrag", required=True)
    ap.add_argument("--golden", default="tests/retrieval/golden/golden.json")
    args = ap.parse_args(argv)
    gold = golden_mod.load(args.golden)
    print(format_comparison(load_systems(args.qmd, args.lightrag, gold), gold))


if __name__ == "__main__":
    main()
