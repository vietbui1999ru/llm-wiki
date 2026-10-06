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
import random

MARKS = {"local": "?", "global": "!", "hybrid": "~", "mix": "."}


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
