"""Cross-check the chunk-to-page mapping of a saved LightRAG run (stdlib only).

M2 acceptance: "mapping verified on 10 queries". The mapping (lr_map.page_of) derives the page from the chunk
id; this checks it against two independent records: the chunk's full_doc_id in the index's text-chunk store and
the file on disk. Usage: verify_mapping.py RESULTS_JSON [--queries 10]
"""
import argparse
import json
import sys
from pathlib import Path

import lr_map

EVAL_COPY = Path.home() / ".cache/llm-wiki/lightrag-eval"


def mismatches(chunk_ids, text_chunks, repo_root):
    problems = []
    for cid in chunk_ids:
        page = lr_map.page_of(cid)
        record = text_chunks.get(cid)
        if record is None:
            problems.append(f"unknown chunk {cid}")
        elif record["full_doc_id"] != page:
            problems.append(f"{cid}: full_doc_id {record['full_doc_id']} != mapped page {page}")
        if not (Path(repo_root) / page).is_file():
            problems.append(f"{cid}: missing file {page}")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("results")
    ap.add_argument("--queries", type=int, default=10)
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--index", default=str(EVAL_COPY))
    args = ap.parse_args(argv)
    extras = json.loads(Path(args.results).read_text())["extras"]
    text_chunks = json.loads((Path(args.index) / "kv_store_text_chunks.json").read_text())
    checked, bad = 0, []
    for qid in list(extras)[: args.queries]:
        for mode, e in extras[qid].items():
            checked += len(e["chunk_ids"])
            bad += [f"{qid}/{mode}: {p}" for p in mismatches(e["chunk_ids"], text_chunks, args.repo_root)]
    print(f"checked {checked} chunk ids across {min(args.queries, len(extras))} queries: {len(bad)} mismatch(es)")
    for line in bad:
        print(" ", line)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
