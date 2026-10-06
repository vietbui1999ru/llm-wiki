"""Score `qmd bench` output against the golden set (stdlib only).

Spec: docs/specs/retrieval-eval-suite.md, sections 3.2, 3.4, 7.1. qmd's own precision/recall are
discarded; only top_files and latency_ms are used, and scoring is done by score.py.
"""
import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

import golden as golden_mod
import score

PREFIX = "qmd://wiki/"
HEADLINE = ("ndcg@10", "recall@5", "recall@10")
CAVEATS = ("Caveats: synthetic queries make absolute scores optimistic, trust differences between systems; "
           "bench bm25 ANDs all terms so long natural-language queries score near zero on bm25; "
           "expansion is cached per (query, model) so later backends look faster than a cold run; "
           "ranked lists are wiki/** only (raw/ and meta hits are dropped, see non_wiki_hits).")


def to_pages(top_files):
    """Strip the collection prefix, keep wiki/** pages in rank order, count everything else."""
    paths = [f[len(PREFIX):] if f.startswith(PREFIX) else f for f in top_files]
    pages = [p for p in paths if p.startswith("wiki/")]
    return pages, len(paths) - len(pages)


def score_bench(bench, golden):
    """Return {backend: [row, ...]} with one scored row per golden query that bench answered."""
    by_id = {q["id"]: q for q in golden["queries"]}
    rows = {}
    for result in bench["results"]:
        q = by_id[result["id"]]  # KeyError on an id the golden set does not know: fail loudly
        for backend, out in result["backends"].items():
            ranked, non_wiki = to_pages(out["top_files"])
            rows.setdefault(backend, []).append({
                "id": q["id"], "category": q["category"], "ranked": ranked,
                "metrics": score.score_query(ranked, q["relevant"]),
                "latency_ms": out["latency_ms"], "non_wiki_hits": non_wiki})
    return rows


def report(rows, metric):
    """Per-backend, per-category mean and 95% CI of one metric, plus an ALL row."""
    return {backend: score.summarize(r, metric) for backend, r in rows.items()}


def run_bench(fixture, out_dir):
    """Write the fixture and run `qmd bench` once over the wiki collection; return its parsed JSON."""
    fixture_path = Path(out_dir) / "qmd-fixture.json"
    fixture_path.write_text(json.dumps(fixture, indent=2))
    done = subprocess.run(["qmd", "bench", str(fixture_path), "--json", "-c", "wiki"],
                          capture_output=True, text=True, check=True)
    if done.stderr.strip():
        print(done.stderr.strip(), file=sys.stderr)
    return json.loads(done.stdout)


def format_report(rows):
    lines = []
    for metric in HEADLINE:
        lines.append(f"\n{metric}  (mean [95% CI], n)")
        for backend, groups in report(rows, metric).items():
            for name, g in groups.items():
                cell = "n/a" if g["mean"] is None else f"{g['mean']:.3f} [{g['lo']:.3f}, {g['hi']:.3f}]"
                lines.append(f"  {backend:<7} {name:<11} {cell}  n={g['n']}")
    return "\n".join(lines) + "\n\n" + CAVEATS


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--golden", default="tests/retrieval/golden/golden.json")
    ap.add_argument("--out-dir", default="tests/retrieval/results")
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args(argv)
    gold = golden_mod.load(args.golden)
    problems = golden_mod.lint(gold, args.repo_root)
    if problems:
        sys.exit("golden set failed lint:\n" + "\n".join(problems))
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    bench = run_bench(golden_mod.qmd_fixture(gold), args.out_dir)
    rows = score_bench(bench, gold)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (Path(args.out_dir) / f"qmd-{stamp}.json").write_text(json.dumps(
        {"run": {"date": stamp, "golden": args.golden, "qmd": "qmd bench --json -c wiki"}, "rows": rows}, indent=2))
    print(format_report(rows))


if __name__ == "__main__":
    main()
