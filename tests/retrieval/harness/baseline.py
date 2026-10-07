"""Build committed baselines from a saved run (stdlib only).

Spec: docs/specs/retrieval-eval-suite.md, section 10. A baseline holds, per backend and query, the top-10 pages and the
per-query metrics (not just means), scored against the current labels. Usage:
baseline.py --results tests/retrieval/results/qmd-RUN.json --system qmd --out tests/retrieval/baselines/qmd.json
"""
import argparse
import datetime
import json
from pathlib import Path

import golden as golden_mod
import provenance
import run_qmd

METRIC_KEYS = ("ndcg@10", "recall@5", "recall@10", "hit@3")


def build(results, golden, system, context, keep=10):
    rescored = run_qmd.rescore(results["rows"], golden)
    backends = {b: [{"id": r["id"], "category": r["category"], "ranked": r["ranked"][:keep],
                     "metrics": {k: r["metrics"][k] for k in METRIC_KEYS}} for r in rows]
                for b, rows in rescored.items()}
    return {"version": 1, "system": system, "context": context, "backends": backends}


def make_context(results, golden_path, repo_root, source):
    run = results["run"]
    recorded = "wiki_sha256" in run and "golden_sha256" in run
    return {"source_run": source, "created": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "index_hash": run.get("index_hash"), "settings": run.get("settings"),
            "golden_sha256": run.get("golden_sha256") or provenance.file_sha256(golden_path),
            "wiki_sha256": run.get("wiki_sha256") or provenance.wiki_sha256(repo_root),
            "provenance": "recorded by the run" if recorded else
            "wiki and golden hashes computed at baseline build time (the source run predates recording)"}


def dumps(b):
    """JSON with one line per query row, so baseline diffs stay reviewable."""
    head = json.dumps({k: v for k, v in b.items() if k != "backends"}, indent=2)[:-2]
    blocks = [f'    {json.dumps(name)}: [\n' + ",\n".join("      " + json.dumps(r, separators=(",", ":")) for r in rows)
              + "\n    ]" for name, rows in b["backends"].items()]
    return head + ',\n  "backends": {\n' + ",\n".join(blocks) + "\n  }\n}\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", required=True)
    ap.add_argument("--system", required=True, choices=("qmd", "lightrag"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--golden", default="tests/retrieval/golden/golden.json")
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args(argv)
    results = json.loads(Path(args.results).read_text())
    context = make_context(results, args.golden, args.repo_root, Path(args.results).name)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(dumps(build(results, golden_mod.load(args.golden), args.system, context)))
    print(f"wrote baseline {args.out} ({sum(len(v) for v in results['rows'].values())} query rows)")


if __name__ == "__main__":
    main()
