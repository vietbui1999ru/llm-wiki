#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["lightrag-hku>=1.5.7,<1.6", "openai", "ollama", "numpy", "python-dotenv"]
# ///
"""LightRAG latency sampling (aquery_data, no answer generation), in one warm process.

Spec: docs/specs/retrieval-eval-suite.md, section 9. Stages per call: keyword-extraction LLM (llm_ms), embedding
(embed_ms, sum of call durations, calls may overlap) and graph plus vector lookup (lookup_ms, the remainder).
naive uses no LLM. Graph modes are sampled as pairs on the real query text: the scratch copy of the eval index has its
query-time keyword-cache entries stripped, so the first call per (mode, query) is a genuine miss (cold) and its immediate
repeat hits the cache (warm). Neither the real index nor the eval copy's cache is touched. (Suffixed variant texts, as
used for qmd, were tried first and rejected: they make the extraction LLM return empty keywords, which is not cached.)
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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden as golden_mod  # noqa: E402
import latency  # noqa: E402
import latency_qmd  # noqa: E402
import run_lightrag  # noqa: E402

SCRATCH = Path.home() / ".cache/llm-wiki/lightrag-eval-latency"
COLD_START_KEYS = ("wall_ms", "import_ms", "init_ms", "first_naive_ms", "second_naive_ms")


def strip_keyword_entries(cache):
    """Drop every query-time keyword-extraction entry ('<mode>:keywords:<hash>') from the LLM response cache, so
    the next call per (mode, query) is a genuine miss. Index-time extraction and summary entries are kept."""
    kept = {k: v for k, v in cache.items() if ":keywords:" not in k}
    return kept, len(cache) - len(kept)


def make_plan(queries, passes, seed):
    """Work items for {mode: passes} on the real query text. naive: plain calls (any number of passes). Graph modes:
    one cold/warm pair (cold = the stripped keyword cache misses, warm = the immediate repeat hits); a second pass
    would already be warm, so it is refused."""
    plan = []
    for mode, n_passes in passes.items():
        if mode != "naive" and n_passes != 1:
            raise ValueError(f"{mode}: graph modes support one pass (a repeat pair would already be cached)")
        for q in queries:
            for p in range(1, n_passes + 1):
                kind = "plain" if mode == "naive" else "pair"
                plan.append({"backend": mode, "id": q["id"], "pass": p, "kind": kind, "text": q["query"]})
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
        lines.append("\ncache check (cold samples must call the keyword LLM, warm samples should hit the cache). A warm "
                     "sample that made an LLM call is a query whose keywords LightRAG did not cache (it does not cache "
                     "an extraction that returned no low-level keywords), so that query pays the LLM on every call:")
        for mode, c in check.items():
            lines.append(f"  {mode}: cold samples that made no LLM call: {c['cold_hit']} of {c['cold_n']}; "
                         f"warm samples that made one: {c['warm_miss']} of {c['warm_n']}")
    return "\n".join(lines)


def summarize_cold_starts(probes):
    """p50/p95/max per phase over fresh-process probes (import, storage load, first query, second query)."""
    return {k: latency.summarize([p[k] for p in probes]) for k in COLD_START_KEYS} if probes else {}


def prepare_scratch(index_hash, run):
    """A throwaway copy of the eval index with the keyword cache stripped, rebuilt for every new run. Resuming the same
    run keeps it, so pairs already measured stay cached and the pending ones are still genuine misses."""
    stamp = SCRATCH / ".latency-stamp"
    if stamp.exists() and stamp.read_text() == f"{index_hash}:{run}":
        return 0
    shutil.rmtree(SCRATCH, ignore_errors=True)
    shutil.copytree(run_lightrag.EVAL_COPY, SCRATCH)
    cache_path = SCRATCH / "kv_store_llm_response_cache.json"
    kept, removed = strip_keyword_entries(json.loads(cache_path.read_text()))
    cache_path.write_text(json.dumps(kept))
    stamp.write_text(f"{index_hash}:{run}")
    return removed


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


def metadata(args, passes, index_hash):
    return {"date": datetime.datetime.now(datetime.timezone.utc).isoformat(), "run": args.run, "passes": passes,
            "seed": args.seed, "machine": latency.machine_info(), "index_hash": index_hash,
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
    stripped = prepare_scratch(index_hash, args.run)
    if not meta_path.exists():
        meta_path.write_text(json.dumps({**metadata(args, passes, index_hash), "keyword_entries_stripped": stripped}, indent=2))
    todo = latency_qmd.pending(make_plan(queries, passes, args.seed), latency_qmd.read_samples(samples_path))

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
