"""qmd latency sampling: plan, resume and report (stdlib only).

Spec: docs/specs/retrieval-eval-suite.md, section 9. qmd is called through its CLI (as run_qmd.py does), so every
sample is one process: start-up and model load are inside the wall-clock total and cannot be split from the stage
lines qmd prints (expansion, embedding, rerank). Conditions: "plain" (bm25, no LLM); for the LLM backends a pair on
one text: "cold" (text nobody has queried, so query expansion cannot be cached; expansions are cached by text and shared
across backends, hence a text unique per backend, pass and run) then "warm" (an immediate repeat, a guaranteed hit).
The report cross-checks the observed expansion time against the intended state.
"""
import argparse
import datetime
import hashlib
import json
import random
import subprocess
import sys
import time
import zlib
from collections import defaultdict
from pathlib import Path

import golden as golden_mod
import latency
import run_qmd


HIT_MS = 100  # an expansion stage faster than this was served from qmd's cache
MARKS = {"vector": "?", "hybrid": "!", "full": "."}


def variant(query, backend, p, salt):
    """Text that no other backend, pass or run has queried, so its expansion cannot be cached (the cache is keyed by
    query text and shared by backends). Verified: a trailing punctuation or case change bypasses the cache."""
    return f"{query} {MARKS[backend] * p} {salt}"


def make_plan(queries, passes, seed, salt):
    """Work items for {backend: passes}. bm25 has no LLM: one plain call. Other backends: a pair, the cold call on a
    fresh text immediately followed by a warm repeat of the same text (a guaranteed cache hit). Shuffled by seed."""
    plan = []
    for backend, n_passes in passes.items():
        for q in queries:
            for p in range(1, n_passes + 1):
                base = {"backend": backend, "id": q["id"], "pass": p}
                if backend == "bm25":
                    plan.append({**base, "kind": "plain", "text": q["query"]})
                else:
                    plan.append({**base, "kind": "pair", "text": variant(q["query"], backend, p, salt)})
    random.Random(seed).shuffle(plan)
    return plan


def _key(s):
    return (s["backend"], s["id"], s["pass"])


def flatten(records):
    """One sample per measurement, tagged with its condition (plain, cold or warm)."""
    flat = []
    for r in records:
        meta = {k: r[k] for k in ("backend", "id", "pass")}
        for condition in (("plain",) if r["kind"] == "plain" else ("cold", "warm")):
            flat.append({**meta, "condition": condition, **r[condition]})
    return flat


def cache_check(flat):
    """Per backend that prints an expansion time: cold samples that hit the cache and warm samples that missed."""
    out = {}
    for s in flat:
        if "expansion_ms" not in s or s["condition"] == "plain":
            continue
        c = out.setdefault(s["backend"], {"cold_hit": 0, "cold_n": 0, "warm_miss": 0, "warm_n": 0})
        hit = s["expansion_ms"] < HIT_MS
        c[f"{s['condition']}_n"] += 1
        c["cold_hit" if s["condition"] == "cold" else "warm_miss"] += hit if s["condition"] == "cold" else not hit
    return out


def read_samples(path):
    path = Path(path)
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def pending(plan, done):
    finished = {_key(s) for s in done}
    return [s for s in plan if _key(s) not in finished]


def format_report(records):
    flat = flatten(records)
    groups = defaultdict(list)
    for s in flat:
        groups[(s["backend"], s["condition"])].append(s)
    lines = []
    for (backend, condition), group in groups.items():
        stages = latency.stage_summaries([{k: v for k, v in s.items() if k.endswith("_ms")} for s in group])
        lines.append(f"{backend} / {condition}  ({len(group)} samples)")
        for stage, st in stages.items():
            lines.append(f"  {stage:<13} n={st['n']:<4} p50={st['p50']:.0f}ms  p95={st['p95']:.0f}ms  max={st['max']:.0f}ms")
        note = latency.small_sample_note(len(group))
        if note:
            lines.append(f"  note: {note}")
    check = cache_check(flat)
    if check:
        lines.append("\ncache check (cold samples must miss the expansion cache, warm samples must hit it; vector and "
                     "bm25 print no expansion time):")
        for backend, c in check.items():
            lines.append(f"  {backend}: cold samples with a cache hit: {c['cold_hit']} of {c['cold_n']}; "
                         f"warm samples with a cache miss: {c['warm_miss']} of {c['warm_n']}")
    return "\n".join(lines)


def time_cli(backend, text):
    """One qmd CLI call. total_ms is wall-clock for the process; stage lines come from stderr; other_ms is the rest
    (process start, model load not inside a stage, lexical search, output)."""
    start = time.monotonic()
    done = subprocess.run(run_qmd.command(backend, text), capture_output=True, text=True, check=True)
    total = round((time.monotonic() - start) * 1000)
    stages = latency.parse_qmd_stages(done.stderr)
    return {"total_ms": total, **stages, "other_ms": total - sum(stages.values())}


def _out(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()


def metadata(args, passes):
    return {"date": datetime.datetime.now(datetime.timezone.utc).isoformat(), "run": args.run, "passes": passes,
            "seed": args.seed, "machine": latency.machine_info(), "qmd_version": _out(["qmd", "--version"]),
            "qmd_status_head": _out(["qmd", "status"]).splitlines()[:9],
            "models_per_spec": "embeddinggemma-300M, Qwen3-Reranker-0.6B, qmd-query-expansion-1.7B (not verified at run time)",
            "results_per_query": run_qmd.RESULTS, "index_sqlite_sha256": _file_hash(Path.home() / ".cache/qmd/index.sqlite")}


def _file_hash(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--golden", default="tests/retrieval/golden/golden.json")
    ap.add_argument("--run", default=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    ap.add_argument("--out-dir", default="tests/retrieval/results")
    ap.add_argument("--passes", default="bm25=2,vector=2,hybrid=2,full=1")
    ap.add_argument("--limit", type=int, help="only the first N non-null queries (smoke runs)")
    ap.add_argument("--warmup", type=int, default=5, help="unrecorded calls before sampling (spec: 5)")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args(argv)
    queries = [q for q in golden_mod.load(args.golden)["queries"] if q["category"] != "null"][: args.limit]
    passes = {k: int(v) for k, v in (item.split("=") for item in args.passes.split(",") if item)}
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    samples_path, meta_path = out / f"latency-qmd-{args.run}.jsonl", out / f"latency-qmd-{args.run}.meta.json"
    if not meta_path.exists():
        meta_path.write_text(json.dumps(metadata(args, passes), indent=2))
    salt = zlib.crc32(args.run.encode()) % 1000
    todo = pending(make_plan(queries, passes, args.seed, salt), read_samples(samples_path))
    if todo:
        for q in queries[: args.warmup]:
            time_cli("full", q["query"])
    with open(samples_path, "a") as f:
        for i, s in enumerate(todo, 1):
            if s["kind"] == "plain":
                record = {**s, "plain": time_cli(s["backend"], s["text"])}
            else:  # cold on a text nobody has queried, then an immediate repeat that must hit the expansion cache
                record = {**s, "cold": time_cli(s["backend"], s["text"]), "warm": time_cli(s["backend"], s["text"])}
            f.write(json.dumps(record) + "\n")
            f.flush()
            if i % 20 == 0:
                print(f"{i}/{len(todo)} work items", file=sys.stderr)
    print(format_report(read_samples(samples_path)))


if __name__ == "__main__":
    main()
