---
title: "Local Wiki RAG: LightRAG Graph Stack"
type: synthesis
tags: [rag, local-llm, ollama, lightrag, graph, mcp, wiki-chat, wiki-index, wiki-mcp]
sources: ["summaries/agentic-search-vs-rag", "summaries/local-rag-elasticsearch"]
created: 2026-05-11
updated: 2026-05-12
---

# Local Wiki RAG: LightRAG Graph Stack

The wiki uses a two-retrieval-path architecture: **qmd** for fast lexical+vector search inside Claude Code sessions, and **LightRAG** for graph-aware synthesis in the TUI and MCP server. Both run locally at zero cost by default; LightRAG can optionally use Claude Haiku for higher-quality synthesis.

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
| Synthesis | Claude Sonnet (in-session) | qwen2.5:3b local or Claude Haiku |
| Latency | ~1s | ~15–30s (LLM synthesis) |
| Best for | In-session lookup, citation | Cross-concept questions, relationships |
| Cost | API (synthesis) | Free local; optional Haiku for quality |
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

Always uses **qwen2.5:3b via ollama** — no API cost, no API key required. Modes match LightRAG's query modes (local/global/hybrid/naive).

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

**Extraction backend** (controlled by `.env`):
- `ANTHROPIC_API_KEY` set → Claude Haiku (better entity/relation extraction)
- unset → qwen2.5:3b via ollama (free, sufficient for most pages)

Incremental by default: a `manifest.json` tracks `{path: mtime}`. Only changed/new pages are re-extracted. The manifest is saved after each page so partial runs resume automatically.

The **post-commit hook** triggers `wiki-index` in the background after any commit touching `wiki/`. Progress: `tail -f .lightrag/last-index.log`.

### wiki-mcp — MCP server

Zero-cost wiki queries from Claude Code or OpenCode. Exposes two tools:
- `wiki_query(question, mode="hybrid")` — graph-aware synthesis
- `wiki_status()` — show index stats

Synthesis backend: same hybrid logic as wiki-index (Haiku if key set, qwen2.5:3b otherwise). LightRAG graph is initialized once as a singleton; retrieval is always local (nomic-embed-text + graph traversal).

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

`install.sh` handles: copying binaries to `~/.local/bin`, setting up the post-commit hook, pulling `qwen2.5:3b` and `nomic-embed-text` via ollama. uv handles Python deps via PEP 723 inline metadata — no pip or venv needed.

One-time graph build (required before wiki-chat or wiki-mcp):
```bash
wiki-index --test      # verify backend
wiki-index --full      # build (~30–60 min for ~150 pages with local LLM)
```

After initial build, the post-commit hook keeps the graph current automatically.

---

## Design choices

### Graph over flat RAG

Per [[summaries/agentic-search-vs-rag]]: graph search wins on cross-concept queries (99% fewer tokens, 2× IoU). Flat RAG only wins on explicit dependency recall. The wiki's primary use case — "how do X and Y relate?", "what patterns apply to problem Z?" — is exactly where graph search wins.

### One concept per page = natural graph nodes

The wiki rule "one thing per page" (CLAUDE.md) makes each page a clean entity for LightRAG to extract. Entities extracted from `concepts/context-degradation` naturally link to `concepts/context-compression`, `concepts/ralph-loop`, etc. Cross-links become graph edges.

### qwen2.5:3b for local synthesis

Better structured output for entity extraction than phi4-mini. Fits comfortably in M1 Pro 16GB and RTX 2060 6GB. For higher-quality extraction at index time: use `ANTHROPIC_API_KEY` — Haiku costs ~$0.001 per page at current pricing.

### Manifest-based incremental indexing

Building the full graph from scratch takes ~30–60 min for 150 pages with a local LLM. The manifest approach means each new ingest only costs extraction time for the new pages (typically 1–3 pages). Post-commit automation makes this transparent.

---

## Performance

| Metric | Value |
|---|---|
| Initial build (qwen2.5:3b, ~150 pages) | ~30–60 min |
| Incremental update (1–3 new pages) | ~1–5 min |
| Query latency (wiki-chat, local) | ~15–30s |
| Retrieval quality vs flat RAG | 2× IoU, 99% fewer tokens |

---

## Related

- [[summaries/agentic-search-vs-rag]] — experiment validating graph search for this wiki
- [[summaries/local-rag-elasticsearch]] — stack comparison; retrieval latency benchmarks
- [[concepts/contextual-retrieval]] — chunk context technique; wiki pages are pre-contextualized (one concept per page)
- [[concepts/bm25]] — lexical retrieval used by qmd (wiki-context path)
- [[concepts/reranking]] — post-retrieval filtering; not yet applied here
- [[entities/qmd]] — BM25 + vector engine for the wiki-context skill path
