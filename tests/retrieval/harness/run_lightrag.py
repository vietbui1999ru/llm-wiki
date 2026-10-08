#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["lightrag-hku>=1.5.7,<1.6", "openai", "ollama", "numpy", "python-dotenv"]
# ///
"""Score LightRAG retrieval (aquery_data, no answer generation) against the golden set.

Spec: docs/specs/retrieval-eval-suite.md, sections 3.3 and 7.2. Queries run against a persistent COPY of the
real .lightrag index so cache writes never touch it; the copy is refreshed when manifest.json changes. The LLM
(keyword extraction in graph modes) and embedding setup mirror templates/wiki-mcp; keep them in sync.
"""
import argparse
import asyncio
import datetime
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden as golden_mod  # noqa: E402
import lr_map  # noqa: E402
import provenance  # noqa: E402
import run_qmd  # noqa: E402

WIKI_DIR = Path.home() / "repos/llm-wiki"
REAL_INDEX = WIKI_DIR / ".lightrag"
EVAL_COPY = Path.home() / ".cache/llm-wiki/lightrag-eval"
MODES = ("naive", "local", "global", "hybrid", "mix")
SETTINGS = {"top_k": 20, "chunk_top_k": 30, "cosine_better_than_threshold": 0.3, "rerank": "off",
            "chunk_token_size": 800, "chunk_overlap_token_size": 64, "embed_model": "nomic-embed-text"}
CAVEATS = ("Caveats: synthetic queries make absolute scores optimistic, trust differences between systems; "
           "the 'requested' count above is chunks (chunk_top_k), several chunks map to one page, so pages kept is lower; "
           "graph-mode rank is the order of first appearance in data.chunks (a round-robin merge of entity-, "
           "relation- and vector-derived chunks, not a score sort), so MRR and nDCG are list-order metrics; "
           "pages reachable only through entities or relations are in extras.kg_only_pages, not in the ranking; "
           "latency_ms is one aquery_data call (cache hits skip the keyword LLM call, see llm_calls); "
           "the index chunker injects wikilinks as hints, so relational queries may look slightly optimistic.")


def parse_settings(items, base):
    """Apply 'key=value' overrides to the numeric settings (for controlled experiments such as a deliberate break).
    Returns a new dict; unknown, non-numeric or malformed overrides raise ValueError."""
    out = dict(base)
    for item in items:
        key, sep, value = item.partition("=")
        if not sep or key not in base or isinstance(base[key], bool) or not isinstance(base[key], (int, float)):
            raise ValueError(f"cannot override {item!r}: use key=value with one of "
                             f"{sorted(k for k, v in base.items() if isinstance(v, (int, float)))}")
        out[key] = type(base[key])(value)
    return out


def sync_eval_copy(real=REAL_INDEX, copy=EVAL_COPY):
    """Refresh the eval copy if the real index changed. Returns the index hash (SHA-256 of manifest.json)."""
    assert real.resolve() != copy.resolve(), "eval copy must not be the real index"
    index_hash = hashlib.sha256((real / "manifest.json").read_bytes()).hexdigest()
    stamp = copy / ".source-hash"
    if not (stamp.exists() and stamp.read_text() == index_hash):
        shutil.rmtree(copy, ignore_errors=True)
        shutil.copytree(real, copy)
        stamp.write_text(index_hash)
    return index_hash


async def build_rag(work_dir, graph_modes):
    """Construct LightRAG exactly as templates/wiki-mcp does. Returns (rag, call counter)."""
    import numpy as np
    import ollama
    from dotenv import load_dotenv
    from lightrag import LightRAG
    from lightrag.llm.openai import openai_complete_if_cache
    from lightrag.utils import EmbeddingFunc

    load_dotenv(WIKI_DIR / ".env")
    load_dotenv(Path.home() / "secrets/.env")
    key = os.environ.get("OPENCODE_GO_API_KEY_LIGHTRAG", "")
    if graph_modes and not key:
        sys.exit("graph modes need OPENCODE_GO_API_KEY_LIGHTRAG (in ~/secrets/.env); use --modes naive for a zero-LLM run")
    model = os.environ.get("OPENCODE_LIGHTRAG_MODEL", "deepseek-v4.1-flash")
    url = os.environ.get("OPENCODE_LIGHTRAG_BASE_URL", "https://opencode.ai/zen/go/v1")
    # llm_ms and embed_ms are sums of call durations (calls may overlap), used by latency_lightrag.py for stage splits
    counter = {"llm_calls": 0, "llm_ms": 0, "embed_ms": 0}

    async def llm(prompt, system_prompt=None, history_messages=None, **kw):
        started = time.monotonic()
        counter["llm_calls"] += 1
        kw.setdefault("max_tokens", 4096)
        kw.setdefault("extra_body", {"thinking": {"type": "disabled"}})
        headers = {"User-Agent": "llm-wiki-lightrag/1.0", "x-opencode-session": f"retrieval-eval-{os.getpid()}"}
        out = await openai_complete_if_cache(model, prompt, system_prompt=system_prompt, base_url=url, api_key=key,
                                             history_messages=history_messages or [], extra_headers=headers, **kw)
        text = "".join([c async for c in out]) if hasattr(out, "__aiter__") else out
        counter["llm_ms"] += round((time.monotonic() - started) * 1000)
        return text

    async def embed(texts):
        started = time.monotonic()
        resp = await asyncio.get_event_loop().run_in_executor(
            None, lambda: ollama.embed(model=SETTINGS["embed_model"], input=texts))
        counter["embed_ms"] += round((time.monotonic() - started) * 1000)
        return np.array(resp.embeddings, dtype=np.float32)

    rag = LightRAG(working_dir=str(work_dir), llm_model_func=llm, llm_model_name=model, llm_model_max_async=4,
                   chunk_token_size=SETTINGS["chunk_token_size"], chunk_overlap_token_size=SETTINGS["chunk_overlap_token_size"],
                   top_k=SETTINGS["top_k"], cosine_better_than_threshold=SETTINGS["cosine_better_than_threshold"],
                   embedding_func=EmbeddingFunc(embedding_dim=768, max_token_size=8192, func=embed))
    await rag.initialize_storages()
    return rag, counter


async def run_queries(rag, counter, queries, modes):
    """Sequential on purpose: clean per-call wall-clock and gentle on the API. A failure aborts the run; the
    LLM cache keeps every completed call, so a rerun resumes cheaply."""
    from lightrag import QueryParam

    runs = {}
    for q in queries:
        runs[q["id"]] = {}
        for mode in modes:
            before, start = counter["llm_calls"], time.monotonic()
            param = QueryParam(mode=mode, top_k=SETTINGS["top_k"], chunk_top_k=SETTINGS["chunk_top_k"],
                               enable_rerank=False)
            result = await rag.aquery_data(q["query"], param=param)
            runs[q["id"]][mode] = {"result": result, "ms": round((time.monotonic() - start) * 1000),
                                   "llm_calls": counter["llm_calls"] - before}
        print(f"{q['id']} done", file=sys.stderr)
    return runs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--golden", default="tests/retrieval/golden/golden.json")
    ap.add_argument("--out-dir", default="tests/retrieval/results")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--modes", default=",".join(MODES), help="comma list of: " + ", ".join(MODES))
    ap.add_argument("--limit", type=int, help="only the first N golden queries (smoke runs)")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="override a numeric setting, e.g. cosine_better_than_threshold=0.9 (recorded in the results)")
    args = ap.parse_args(argv)
    SETTINGS.update(parse_settings(args.set, SETTINGS))
    modes = [m for m in args.modes.split(",") if m]
    bad = sorted(set(modes) - set(MODES))
    if bad:
        sys.exit(f"unknown modes {bad}; choose from {list(MODES)}")
    gold = golden_mod.load(args.golden)
    problems = golden_mod.lint(gold, args.repo_root)
    if problems:
        sys.exit("golden set failed lint:\n" + "\n".join(problems))
    queries = gold["queries"][: args.limit]
    index_hash = sync_eval_copy()

    async def go():
        rag, counter = await build_rag(EVAL_COPY, graph_modes=any(m != "naive" for m in modes))
        try:
            return await run_queries(rag, counter, queries, modes)
        finally:
            await rag.finalize_storages()

    bench, extras = lr_map.to_bench(asyncio.run(go()))
    rows = run_qmd.score_bench(bench, {**gold, "queries": queries})
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    (Path(args.out_dir) / f"lightrag-{stamp}.json").write_text(json.dumps(
        {"run": {"date": stamp, "golden": args.golden, "index_hash": index_hash, "modes": modes, "settings": SETTINGS,
                 "wiki_sha256": provenance.wiki_sha256(args.repo_root),
                 "golden_sha256": provenance.file_sha256(args.golden)},
         "rows": rows, "extras": extras}, indent=2))
    print(run_qmd.format_report(rows, caveats=CAVEATS, requested=SETTINGS["chunk_top_k"]))


if __name__ == "__main__":
    main()
