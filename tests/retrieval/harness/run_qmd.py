"""Score qmd retrieval against the golden set (stdlib only).

Spec: docs/specs/retrieval-eval-suite.md, sections 3.2, 3.4, 7.1. Deviation from 7.1: instead of `qmd bench`
(capped at 10 files per query, which leaves about 3 wiki pages after the wiki/**-only filter) each backend is
called through the qmd CLI with a larger -n. Verified on a probe query: the CLI top-10 is identical to bench's
for all four backends. Only the ranked file list is used; scoring is done by score.py.
"""
import argparse
import datetime
import json
import subprocess
import sys
import time
from pathlib import Path

import golden as golden_mod
import score

PREFIX = "qmd://wiki/"
RESULTS = 50  # files requested per query; qmd's collection is the whole repo, so most hits are raw/ or meta
BACKENDS = {"bm25": ["search"], "vector": ["vsearch"], "hybrid": ["query", "--no-rerank"], "full": ["query"]}
HEADLINE = ("ndcg@10", "recall@5", "recall@10")
CAVEATS = ("Caveats: synthetic queries make absolute scores optimistic, trust differences between systems; "
           "bm25 ANDs all terms so long natural-language queries score near zero on bm25; "
           "query expansion is cached per (query, model) so later backends can look faster than a cold run; "
           "latency_ms is wall-clock per CLI process (includes qmd start-up), not comparable to qmd bench or "
           "to the spec's latency protocol; ranked lists are wiki/** only (raw/ and meta hits are dropped).")


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


def rescore(rows, golden):
    """Recompute metrics from saved rankings against the current labels; no qmd run needed."""
    by_id = {q["id"]: q for q in golden["queries"]}
    return {backend: [{**r, "metrics": score.score_query(r["ranked"], by_id[r["id"]]["relevant"])} for r in rs]
            for backend, rs in rows.items()}


def report(rows, metric):
    """Per-backend, per-category mean and 95% CI of one metric, plus an ALL row."""
    return {backend: score.summarize(r, metric) for backend, r in rows.items()}


def cli_top_files(stdout):
    """Ranked file URIs from `qmd ... --json` output."""
    return [r["file"] for r in json.loads(stdout)]


def command(backend, query):
    return ["qmd", BACKENDS[backend][0], query, *BACKENDS[backend][1:], "-n", str(RESULTS), "--json", "-c", "wiki"]


def run_cli(backend, query):
    """Run one backend through the qmd CLI; return (ranked files, wall-clock milliseconds)."""
    start = time.monotonic()
    done = subprocess.run(command(backend, query), capture_output=True, text=True, check=True)
    return cli_top_files(done.stdout), round((time.monotonic() - start) * 1000)


def collect(queries, runner, backends=tuple(BACKENDS)):
    """Run every query on every backend. Output has the shape score_bench expects."""
    results = []
    for q in queries:
        outs = {}
        for backend in backends:
            files, ms = runner(backend, q["query"])
            outs[backend] = {"top_files": files, "latency_ms": ms}
        results.append({"id": q["id"], "backends": outs})
    return {"results": results}


def format_report(rows, caveats=CAVEATS, requested=RESULTS):
    """Headline tables per system and category. Other runners pass their own caveats and request size."""
    lines = []
    for metric in HEADLINE:
        lines.append(f"\n{metric}  (mean [95% CI], n)")
        for backend, groups in report(rows, metric).items():
            for name, g in groups.items():
                cell = "n/a" if g["mean"] is None else f"{g['mean']:.3f} [{g['lo']:.3f}, {g['hi']:.3f}]"
                lines.append(f"  {backend:<7} {name:<11} {cell}  n={g['n']}")
    lines.append(f"\nWiki pages left after dropping non-wiki hits (up to {requested} files requested per query; "
                 "@10 is only meaningful if this stays well above 10):")
    for backend, rs in rows.items():
        kept = sum(len(r["ranked"]) for r in rs) / len(rs)
        non_wiki = sum(r["non_wiki_hits"] for r in rs) / len(rs)
        lines.append(f"  {backend}: wiki pages kept per query {kept:.1f} of {requested}, non-wiki hits {non_wiki:.1f}")
    return "\n".join(lines) + "\n\n" + caveats


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--golden", default="tests/retrieval/golden/golden.json")
    ap.add_argument("--out-dir", default="tests/retrieval/results")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--rescore", metavar="RESULTS_JSON", help="re-score a saved run against the current labels")
    args = ap.parse_args(argv)
    gold = golden_mod.load(args.golden)
    problems = golden_mod.lint(gold, args.repo_root)
    if problems:
        sys.exit("golden set failed lint:\n" + "\n".join(problems))
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    if args.rescore:
        print(format_report(rescore(json.loads(Path(args.rescore).read_text())["rows"], gold)))
        return
    rows = score_bench(collect(gold["queries"], run_cli), gold)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (Path(args.out_dir) / f"qmd-{stamp}.json").write_text(json.dumps(
        {"run": {"date": stamp, "golden": args.golden, "results_per_query": RESULTS, "backends": BACKENDS},
         "rows": rows}, indent=2))
    print(format_report(rows))


if __name__ == "__main__":
    main()
