#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["lightrag-hku>=1.5.7,<1.6", "openai", "ollama", "numpy", "python-dotenv"]
# ///
"""LightRAG latency sampling (aquery_data, no answer generation), in one warm process.

Spec: docs/specs/retrieval-eval-suite.md, section 9. Stages per call: keyword-extraction LLM (llm_ms), embedding
(embed_ms, sum of call durations, calls may overlap) and graph plus vector lookup (lookup_ms, the remainder).
naive uses no LLM. Graph modes are sampled as pairs: a cold call on a text unique to the mode, pass and run (the
keyword prompt embeds the query, so no cache entry can exist) then a warm repeat that must hit the cache. Runs
against a scratch copy of the eval index so neither the real index nor the eval copy's cache is touched.
Process cold start (imports, storage load, first query) is measured separately with --cold-start-runs.
"""
import argparse
import asyncio
import datetime
import importlib.metadata
import json
import os
import random
import shutil
import subprocess
import sys
import time
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden as golden_mod  # noqa: E402
import latency  # noqa: E402
import latency_qmd  # noqa: E402
import run_lightrag  # noqa: E402

SCRATCH = Path.home() / ".cache/llm-wiki/lightrag-eval-latency"
MARKS = {"local": "?", "global": "!", "hybrid": "~", "mix": "."}
COLD_START_KEYS = ("wall_ms", "import_ms", "init_ms", "first_naive_ms", "second_naive_ms")


def variant(query, mode, p, salt):
    """Query text no other mode, pass or run has used, so its keyword extraction cannot be cached."""
    return f"{query} {MARKS[mode] * p} {salt}"


def make_plan(queries, passes, seed, salt):
    """Work items for {mode: passes}. naive: one plain call. Graph modes: a cold/warm pair on one fresh text."""
    plan = []
    for mode, n_passes in passes.items():
        for q in queries:
            for p in range(1, n_passes + 1):
                base = {"backend": mode, "id": q["id"], "pass": p}
                if mode == "naive":
                    plan.append({**base, "kind": "plain", "text": q["query"]})
                else:
                    plan.append({**base, "kind": "pair", "text": variant(q["query"], mode, p, salt)})
    random.Random(seed).shuffle(plan)
    return plan


def stage_split(total_ms, llm_ms, embed_ms, llm_calls):
    """Stage times for one aquery_data call; lookup is the remainder and never negative (calls can overlap)."""
    return {"total_ms": total_ms, "llm_ms": llm_ms, "embed_ms": embed_ms,
            "lookup_ms": max(0, total_ms - llm_ms - embed_ms), "llm_calls": llm_calls}


def cache_check(flat):
    """Per graph mode: cold samples that made no LLM call (cache hit) and warm samples that made one (cache miss)."""
    out = {}
    for s in flat:
        if s["condition"] == "plain":
            continue
        c = out.setdefault(s["backend"], {"cold_hit": 0, "cold_n": 0, "warm_miss": 0, "warm_n": 0})
        c[f"{s['condition']}_n"] += 1
        if s["condition"] == "cold" and s["llm_calls"] == 0:
            c["cold_hit"] += 1
        if s["condition"] == "warm" and s["llm_calls"] > 0:
            c["warm_miss"] += 1
    return out


def format_report(records):
    flat = latency_qmd.flatten(records)
    lines = latency_qmd.format_groups(flat)
    check = cache_check(flat)
    if check:
        lines.append("\ncache check (cold samples must call the keyword LLM, warm samples must hit the cache):")
        for mode, c in check.items():
            lines.append(f"  {mode}: cold samples that made no LLM call: {c['cold_hit']} of {c['cold_n']}; "
                         f"warm samples that made one: {c['warm_miss']} of {c['warm_n']}")
    return "\n".join(lines)


def summarize_cold_starts(probes):
    """p50/p95/max per phase over fresh-process probes (import, storage load, first query, second query)."""
    return {k: latency.summarize([p[k] for p in probes]) for k in COLD_START_KEYS} if probes else {}


def prepare_scratch(index_hash):
    """A throwaway copy of the eval index for latency runs; rebuilt only when the real index changed."""
    stamp = SCRATCH / ".latency-source-hash"
    if not (stamp.exists() and stamp.read_text() == index_hash):
        shutil.rmtree(SCRATCH, ignore_errors=True)
        shutil.copytree(run_lightrag.EVAL_COPY, SCRATCH)
        stamp.write_text(index_hash)


async def measure(rag, counter, text, mode):
    """One aquery_data call with its stage split (LLM and embedding time from the instrumented build_rag)."""
    from lightrag import QueryParam

    s = run_lightrag.SETTINGS
    before, start = dict(counter), time.monotonic()
    result = await rag.aquery_data(text, param=QueryParam(mode=mode, top_k=s["top_k"], chunk_top_k=s["chunk_top_k"],
                                                          enable_rerank=False))
    total = round((time.monotonic() - start) * 1000)
    if result.get("status") != "success":
        raise RuntimeError(f"aquery_data failed for mode {mode}: {result.get('message')}")
    return stage_split(total, counter["llm_ms"] - before["llm_ms"], counter["embed_ms"] - before["embed_ms"],
                       counter["llm_calls"] - before["llm_calls"])


async def take_samples(rag, counter, todo, path):
    """Run the work items, appending one JSON record each (pairs are written only when both calls finished)."""
    with open(path, "a") as f:
        for i, s in enumerate(todo, 1):
            if s["kind"] == "plain":
                record = {**s, "plain": await measure(rag, counter, s["text"], s["backend"])}
            else:
                cold = await measure(rag, counter, s["text"], s["backend"])
                record = {**s, "cold": cold, "warm": await measure(rag, counter, s["text"], s["backend"])}
            f.write(json.dumps(record) + "\n")
            f.flush()
            if i % 20 == 0:
                print(f"{i}/{len(todo)} work items", file=sys.stderr)


def _ms(since):
    return round((time.monotonic() - since) * 1000)


async def probe(query):
    """Inside a fresh process: import time, storage load (includes the remaining imports) and the first two naive calls."""
    t = time.monotonic()
    import lightrag  # noqa: F401
    import numpy  # noqa: F401
    import ollama  # noqa: F401
    import_ms = _ms(t)
    t = time.monotonic()
    rag, counter = await run_lightrag.build_rag(SCRATCH, graph_modes=False)
    init_ms = _ms(t)
    first = await measure(rag, counter, query, "naive")
    second = await measure(rag, counter, query, "naive")
    await rag.finalize_storages()
    return {"import_ms": import_ms, "init_ms": init_ms, "first_naive_ms": first["total_ms"],
            "second_naive_ms": second["total_ms"]}


def run_cold_starts(n, query):
    """n fresh processes; wall_ms is the whole process (uv, interpreter, imports, load, two queries, shutdown)."""
    probes = []
    for _ in range(n):
        start = time.monotonic()
        done = subprocess.run(["uv", "run", "--script", str(Path(__file__).resolve()), "--cold-start-probe",
                               "--probe-query", query], capture_output=True, text=True, check=True)
        line = next(x for x in done.stdout.splitlines() if x.startswith("PROBE "))
        probes.append({**json.loads(line[6:]), "wall_ms": _ms(start)})
    return probes


def metadata(args, passes, salt, index_hash):
    return {"date": datetime.datetime.now(datetime.timezone.utc).isoformat(), "run": args.run, "passes": passes,
            "seed": args.seed, "salt": salt, "machine": latency.machine_info(), "index_hash": index_hash,
            "lightrag_version": importlib.metadata.version("lightrag-hku"), "settings": run_lightrag.SETTINGS,
            "llm_model": os.environ.get("OPENCODE_LIGHTRAG_MODEL", "deepseek-v4.1-flash"),
            "embed_model": run_lightrag.SETTINGS["embed_model"], "note": "disk cache is warm after the first run"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--golden", default="tests/retrieval/golden/golden.json")
    ap.add_argument("--run", default=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    ap.add_argument("--out-dir", default="tests/retrieval/results")
    ap.add_argument("--passes", default="naive=2,local=1,global=1,hybrid=1,mix=1")
    ap.add_argument("--limit", type=int, help="only the first N non-null queries (smoke runs)")
    ap.add_argument("--warmup", type=int, default=5, help="unrecorded naive calls before sampling (spec: 5)")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--cold-start-runs", type=int, default=5)
    ap.add_argument("--cold-start-probe", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--probe-query", default="how do agents keep context from degrading", help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    if args.cold_start_probe:
        print("PROBE " + json.dumps(asyncio.run(probe(args.probe_query))))
        return
    queries = [q for q in golden_mod.load(args.golden)["queries"] if q["category"] != "null"][: args.limit]
    passes = {k: int(v) for k, v in (item.split("=") for item in args.passes.split(",") if item)}
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = out / f"latency-lightrag-{args.run}"
    samples_path, meta_path, cold_path = Path(f"{stem}.jsonl"), Path(f"{stem}.meta.json"), Path(f"{stem}.coldstart.json")
    index_hash = run_lightrag.sync_eval_copy()
    prepare_scratch(index_hash)
    salt = zlib.crc32(args.run.encode()) % 1000
    if not meta_path.exists():
        meta_path.write_text(json.dumps(metadata(args, passes, salt, index_hash), indent=2))
    todo = latency_qmd.pending(make_plan(queries, passes, args.seed, salt), latency_qmd.read_samples(samples_path))

    async def go():
        rag, counter = await run_lightrag.build_rag(SCRATCH, graph_modes=any(m != "naive" for m in passes))
        try:
            for q in queries[: args.warmup]:
                await measure(rag, counter, q["query"], "naive")
            await take_samples(rag, counter, todo, samples_path)
        finally:
            await rag.finalize_storages()

    if todo:
        asyncio.run(go())
    if args.cold_start_runs and not cold_path.exists():
        cold_path.write_text(json.dumps(run_cold_starts(args.cold_start_runs, queries[0]["query"]), indent=2))
    print(format_report(latency_qmd.read_samples(samples_path)))
    if cold_path.exists():
        print("\ncold start (fresh process each, ms):")
        for phase, st in summarize_cold_starts(json.loads(cold_path.read_text())).items():
            print(f"  {phase:<15} n={st['n']} p50={st['p50']:.0f}  max={st['max']:.0f}")


if __name__ == "__main__":
    main()
