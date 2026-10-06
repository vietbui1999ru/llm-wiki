"""One headline table over the qmd and LightRAG latency runs (stdlib only).

Spec: docs/specs/retrieval-eval-suite.md, section 9. Usage:
latency_report.py --qmd latency-qmd-RUN.jsonl --lightrag latency-lightrag-RUN.jsonl
total_ms is wall-clock per call: a whole qmd CLI process, or one in-process LightRAG aquery_data call, so the two
systems are not like for like (see the spec); per-stage numbers are in each runner's own report.
"""
import argparse

import latency
import latency_qmd

CONDITION_ORDER = {"plain": 0, "cold": 1, "warm": 2}


def headline_rows(records_by_system):
    """[{system, backend, condition, n, p50, p95, max}] over total_ms, in system/backend/cold-before-warm order."""
    rows = []
    for system, records in records_by_system.items():
        groups, order = {}, []
        for s in latency_qmd.flatten(records):
            key = (s["backend"], s["condition"])
            if key not in groups:
                order.append(key)
            groups.setdefault(key, []).append(s["total_ms"])
        backends = list(dict.fromkeys(b for b, _ in order))
        for backend, condition in sorted(groups, key=lambda k: (backends.index(k[0]), CONDITION_ORDER[k[1]])):
            rows.append({"system": system, "backend": backend, "condition": condition,
                         **latency.summarize(groups[(backend, condition)])})
    return rows


def format_table(rows):
    lines = [f"{'system':<9}{'backend':<9}{'condition':<10}{'n':>5}{'p50 ms':>9}{'p95 ms':>9}{'max ms':>9}"]
    for r in rows:
        lines.append(f"{r['system']:<9}{r['backend']:<9}{r['condition']:<10}{r['n']:>5}"
                     f"{r['p50']:>9.0f}{r['p95']:>9.0f}{r['max']:>9.0f}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--qmd", required=True)
    ap.add_argument("--lightrag", required=True)
    args = ap.parse_args(argv)
    records = {"qmd": latency_qmd.read_samples(args.qmd), "lightrag": latency_qmd.read_samples(args.lightrag)}
    print(format_table(headline_rows(records)))


if __name__ == "__main__":
    main()
