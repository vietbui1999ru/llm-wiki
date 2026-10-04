---
title: "Local Wiki RAG: LightRAG Graph Stack"
type: synthesis
tags: [rag, local-llm, ollama, lightrag, graph, mcp, wiki-chat, wiki-index, wiki-mcp]
sources: ["summaries/agentic-search-vs-rag", "summaries/local-rag-elasticsearch"]
created: 2026-05-11
updated: 2026-10-04
---

# Local Wiki RAG: LightRAG Graph Stack

The wiki uses a two-retrieval-path architecture: **qmd** for fast lexical+vector search inside Claude Code sessions, and **LightRAG** for graph-aware synthesis in the TUI and MCP server. qmd runs fully locally at zero cost. LightRAG retrieval (embeddings via ollama `nomic-embed-text` + graph traversal) is local, but extraction and synthesis call a hosted OpenCode Go model (OpenAI-compatible API); a self-hosted llama.cpp server is planned for the LLM (slot reserved, not wired) and later for embeddings.

---

## Architecture

```
wiki/ pages
    │
    ├─── qmd index (BM25 + vector)          ← wiki-context skill → Claude Code
    │    Updated by: post-commit hook (synchronous)
    │
    └─── LightRAG graph (.lightrag/)        ← wiki-chat TUI + wiki-mcp MCP server
         Updated by: wiki-index (background, post-commit)
```

### Why two paths

| Dimension | qmd | LightRAG |
|---|---|---|
| Retrieval type | BM25 + vector hybrid | entity/community graph traversal |
| Synthesis | Claude Sonnet (in-session) | OpenCode Go model |
| Latency | ~1s | not re-measured with OpenCode Go (was ~15–30s with a local LLM) |
| Best for | In-session lookup, citation | Cross-concept questions, relationships |
| Cost | API (synthesis) | OpenCode Go plan (flat monthly, with usage limits) |
| Available in | Claude Code, OpenCode | Anywhere (TUI or MCP) |

The agentic-search-vs-rag experiment validated the LightRAG path: graph search achieved 2× retrieval IoU with 99% fewer tokens vs flat RAG. See [[summaries/agentic-search-vs-rag]].

---

## Tools

### wiki-chat — interactive TUI

```bash
wiki-chat                   # hybrid mode (default)
wiki-chat --mode local      # entity/concept-focused
wiki-chat --mode global     # community summaries, big-picture
```

Uses the same backend selection as wiki-index (OpenCode Go; requires `OPENCODE_GO_API_KEY_LIGHTRAG`, otherwise queries return an error). Modes match LightRAG's query modes (local/global/hybrid/naive).

TUI prompt commands:
- `/mode local|global|hybrid|naive` — switch mid-session
- `/reindex` — trigger wiki-index for new pages
- `/status` — show manifest stats

### wiki-index — graph indexer

```bash
wiki-index              # incremental (new/changed pages only)
wiki-index --full       # wipe and rebuild from scratch
wiki-index --status     # show manifest stats without indexing
wiki-index --test       # verify LLM backend then exit
```

**Extraction backend** (first configured wins; env from `.env` or the shell):
- `LLAMACPP_BASE_URL` set → self-hosted llama.cpp. **Reserved, not wired yet**: setting it raises an error. The slot exists so a llama-server instance (OpenAI-compatible `/v1`) can be added later.
- `OPENCODE_GO_API_KEY_LIGHTRAG` set → OpenCode Go via its OpenAI-compatible endpoint (`https://opencode.ai/zen/go/v1`); default model `deepseek-v4.1-flash`, overridable with `OPENCODE_LIGHTRAG_MODEL` / `OPENCODE_LIGHTRAG_BASE_URL`. That model reasons by default and, probed 2026-10-04, spent the whole 4096-token budget on thinking for extraction prompts (empty content, `finish_reason=length`), so requests send `thinking: {"type": "disabled"}` (a sample prompt dropped from 2774 to 185 completion tokens); set `OPENCODE_LIGHTRAG_DISABLE_THINKING=0` for models that reject the field. OpenCode also rejects requests without an `x-opencode-session` header.
- neither → no backend: `wiki-index`/`--test` and queries exit with a clear error; `wiki-index --status` and `wiki_status` still work. The check runs before `--full` wipes the index.

**Usage warning:** LightRAG runs 3 extraction phases per page (entity → relation → community), each with multiple LLM calls. OpenCode Go enforces 5-hour, weekly and monthly dollar-denominated usage limits per model ([limits](https://opencode.ai/docs/go/#usage-limits)), so a full rebuild of ~150 pages can exhaust the 5-hour window. `--full` therefore requires `--yes`; incremental updates (1–3 new pages per ingest) are cheap.

Incremental by default: a `manifest.json` tracks `{path: mtime}`. Only changed/new pages are re-extracted. The manifest is saved after each page so partial runs resume automatically.

The **post-commit hook** triggers `wiki-index` in the background after any commit touching `wiki/`. Progress: `tail -f .lightrag/last-index.log`.

### wiki-mcp — MCP server

Graph-aware wiki queries from Claude Code or OpenCode (synthesis counts against the OpenCode Go plan limits). Exposes two tools:
- `wiki_query(question, mode="hybrid")` — graph-aware synthesis
- `wiki_status()` — show index stats

Synthesis backend: same backend selection as wiki-index (OpenCode Go if `OPENCODE_GO_API_KEY_LIGHTRAG` is set; otherwise `wiki_query` returns an error). LightRAG graph is initialized once as a singleton; retrieval is always local (nomic-embed-text + graph traversal).

Wire into OpenCode (`~/.config/opencode/opencode.json`):
```json
"wiki-rag": {
  "type": "local",
  "command": ["/Users/<user>/.local/bin/wiki-mcp"],
  "enabled": true
}
```

---

## Setup

```bash
cd ~/repos/llm-wiki
bash claude-setup/scripts/install.sh
```

`install.sh` handles: copying binaries to `~/.local/bin`, setting up the post-commit hook, pulling the `nomic-embed-text` embedding model via ollama. uv handles Python deps via PEP 723 inline metadata — no pip or venv needed.

One-time graph build (required before wiki-chat or wiki-mcp):
```bash
wiki-index --test      # verify backend
wiki-index --full --yes   # build (requires OPENCODE_GO_API_KEY_LIGHTRAG; duration not measured)
```

After initial build, the post-commit hook keeps the graph current automatically.

---

## Design choices

### Graph over flat RAG

Per [[summaries/agentic-search-vs-rag]]: graph search wins on cross-concept queries (99% fewer tokens, 2× IoU). Flat RAG only wins on explicit dependency recall. The wiki's primary use case — "how do X and Y relate?", "what patterns apply to problem Z?" — is exactly where graph search wins.

### One concept per page = natural graph nodes

The wiki rule "one thing per page" (CLAUDE.md) makes each page a clean entity for LightRAG to extract. Entities extracted from `concepts/context-degradation` naturally link to `concepts/context-compression`, `concepts/ralph-loop`, etc. Cross-links become graph edges.

### Hosted LLM, local embeddings

Extraction and synthesis use OpenCode Go (billed against the plan's usage limits, not per page); embeddings stay local on ollama (`nomic-embed-text`) because OpenCode has no embedding offering: probed 2026-10-04, neither the Go (36 models) nor the Zen (50 models) catalog lists an embedding model, and `POST /embeddings` returns 404 on both endpoints. The earlier local-LLM path (qwen2.5 via ollama) was removed. A self-hosted llama.cpp server is the planned replacement for the LLM (env slot `LLAMACPP_BASE_URL`, reserved but not wired) and for embeddings (not started). When embeddings move, rebuild the index if the embedding model or dimension changes (training data — verify: LightRAG vector stores are tied to the embedding dimension).

### Manifest-based incremental indexing

Building the full graph from scratch is the expensive operation (3 extraction phases per page). The manifest approach means each new ingest only costs extraction time for the new pages (typically 1–3 pages). Post-commit automation makes this transparent.

---

## Performance

| Metric | Value |
|---|---|
| Initial build (OpenCode Go, ~150 pages) | not measured; may hit the 5-hour usage limit |
| Incremental update (1–3 new pages, OpenCode Go) | not measured; counts against plan limits |
| Query latency (wiki-chat, OpenCode Go) | not measured |
| *Historical (removed qwen2.5:3b local backend)*: initial build / incremental / query | ~30–60 min / ~5–15 min / ~15–30s |
| Retrieval quality vs flat RAG | 2× IoU, 99% fewer tokens |

---

## Related

- [[summaries/agentic-search-vs-rag]] — experiment validating graph search for this wiki
- [[summaries/local-rag-elasticsearch]] — stack comparison; retrieval latency benchmarks
- [[concepts/contextual-retrieval]] — chunk context technique; wiki pages are pre-contextualized (one concept per page)
- [[concepts/bm25]] — lexical retrieval used by qmd (wiki-context path)
- [[concepts/reranking]] — post-retrieval filtering; not yet applied here
- [[entities/qmd]] — BM25 + vector engine for the wiki-context skill path
- [[concepts/wikilink-graph-extraction]] — Obsidian wikilink hints injected at chunk time to reduce LightRAG extraction cost ~40–55%
