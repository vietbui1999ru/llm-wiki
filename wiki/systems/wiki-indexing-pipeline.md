---
title: "Wiki Indexing Pipeline: qmd and LightRAG"
type: concept
tags: [indexing, rag, lightrag, qmd, embeddings, knowledge-graph, incremental, operations, opencode-go]
sources: ["claude-setup/scripts/post-commit", "templates/wiki-index", "templates/wiki-mcp", "templates/wiki-chat", "LightRAG 1.5.7 source (lightrag/lightrag.py, lightrag/llm/openai.py)", "2026-10-04 rebuild and diagnosis sessions"]
created: 2026-10-04
updated: 2026-10-05
---

# Wiki Indexing Pipeline: qmd and LightRAG

This repo is indexed **two ways**, for two different jobs. qmd *finds pages*; LightRAG *connects them*. Architecture and tool usage are in [[syntheses/local-rag-wiki]]; this page records **how each index is built, kept current, and what goes wrong**. Facts are as of 2026-10-04.

| | qmd | LightRAG graph |
|---|---|---|
| Method | BM25 keyword search + vector similarity, query expansion and reranking ([[entities/qmd]]) | LLM-extracted entities and relations merged into a knowledge graph, plus vector indexes |
| Built by | `qmd update` + `qmd embed` | `wiki-index` (extraction LLM: [[entities/opencode-go]]; embeddings: local ollama) |
| Covers | three collections: `wiki` (this repo), `Obsidian`, `career`; 1,566 docs, ~8.2k vectors, ~69 MB | `wiki/**` only: 179 pages, **8,100 nodes, 11,369 edges**, ~165 MB |
| Used by | the `wiki-context` skill | `wiki-chat` (TUI) and `wiki-mcp` (MCP server) |
| Good at | "find the page about X" | cross-page questions ("how do X and Y relate?") |
| Store | sqlite, `~/.cache/qmd/` | JSON + GraphML under `.lightrag/` (gitignored) |

qmd's own embedding and rerank models are downloaded by `qmd pull`; I have not verified which ones.

## When indexing runs

The `post-commit` hook runs after every commit: `qmd update` and `qmd embed` **synchronously** (incremental, seconds), then `wiki-index` **in the background** (incremental; progress in `.lightrag/last-index.log`). `wiki-index --full --yes` is the manual full rebuild.

## LightRAG pipeline, step by step

1. **Page selection.** `wiki-index` lists `wiki/**/*.md` and compares each file's mtime with `.lightrag/manifest.json`; only new or changed pages go through.
2. **Chunking.** A custom chunker prepends a *graph-structure header* (the page title, type, tags and up to 25 confirmed wikilinks) so the LLM only extracts what the links do not already state ([[concepts/wikilink-graph-extraction]]), then cuts ~800-token chunks with 64 tokens of overlap.
3. **Extraction.** Each chunk goes to the LLM (default `deepseek-v4.1-flash` via OpenCode Go's OpenAI-compatible endpoint, `thinking` disabled) to produce entities and relations. LightRAG then runs relation processing and merges duplicates into the graph (the 1.5.7 logs show extraction, relation processing, merging).
4. **Embedding.** Entity, relation and chunk texts are embedded locally by ollama `nomic-embed-text` (768 dimensions) in small batches.
5. **Persist.** Written to `graph_chunk_entity_relation.graphml`, `vdb_{entities,relationships,chunks}.json` (nano-vectordb) and the `kv_store_*.json` files. The manifest entry is saved **after each page**, so an interrupted run resumes.

**Query** (`wiki-chat`, `wiki-mcp`): embed the question, retrieve from the graph and vectors, then have the LLM write the answer. Modes: `local` (specific entities), `global` (community-level, cross-concept), `hybrid` (both, default), `naive` (flat vector search).

## Keeping it correct

- **Same file name means duplicate.** LightRAG silently drops an insert whose file *basename* already exists (and logs a `dup-*` record). Before the fix this meant changed pages were never re-indexed and same-named pages in different directories collided (found 2026-10-05: 6 stale pages, 3 missing, 12 stray records). `wiki-index` now passes a path-unique name (`wiki__concepts__x.md`), replaces a changed page by deleting its old record before inserting, and removes pages deleted from disk on the next run.
- **Failed or skipped pages are not recorded.** `ainsert` logs pipeline errors instead of raising, so after each insert `wiki-index` checks that the status is `processed` and that the stored text equals the page (compared after LightRAG's own sanitising: strip, HTML-unescape, control characters). A page that fails either check stays out of the manifest, is retried next run, and the run exits 1.
- **`wiki-index --verify` / `--reconcile`.** `--verify` compares the index with the wiki on disk (missing, failed, stale and deleted-but-indexed pages, stray `dup-*` records) and exits 1 on any difference, without needing the LLM; `--reconcile` repairs them (re-index needs the LLM). Run `--verify` after any bulk change or restore.
- **Full rebuilds drop dead entries.** The 2026-10-04 audit found 67 of 209 manifest entries pointing at missing files before a `--full` rebuild cleared them. Back up `.lightrag/` first (`--full` wipes it before rebuilding).
- **No backend, no wipe.** With no LLM backend configured, `wiki-index` exits *before* `--full` would wipe the index.
- **Full rebuilds are heavy.** Many LLM calls per page; on OpenCode Go they count against 5-hour, weekly and monthly usage limits, hence `--yes`. The 2026-10-04 rebuild of 175 pages took roughly 1.5 hours (estimate from the log).

## Gotchas found in practice

- **A long `sources:` frontmatter line can stall a page.** One page with 31 source filenames timed out on chunk 0 every time (3 attempts, 2 models) while the same text indexed in 28 s with `sources` emptied, and each section indexed alone. Fix: keep `sources` short; the page was split into a hub plus three topical pages (see [[concepts/owasp-security-checklist]]).
- **Reasoning models eat `max_tokens`.** With `deepseek-v4.1-flash`'s default thinking, extraction prompts spent the whole 4096 budget on reasoning and returned empty content. Sending `thinking: {"type": "disabled"}` cut a sample prompt from 2774 to 185 completion tokens. `OPENCODE_LIGHTRAG_DISABLE_THINKING=0` opts out for models that reject the field.
- **OpenCode requires an `x-opencode-session` header** (HTTP 400 `MissingSessionID` without it). The scripts send it per request via `extra_headers`, because LightRAG overwrites client-level `default_headers`.
- **LightRAG's API moves.** 1.5.7 dropped `max_extract_input_tokens`, renamed `cosine_threshold` to `cosine_better_than_threshold`, and moved `chunking_by_token_size` to `lightrag.chunker`. The scripts pin `lightrag-hku>=1.5.7,<1.6`.
- **OpenCode has no embeddings.** Neither the Go nor the Zen catalog lists an embedding model and `POST /embeddings` is 404 on both, so embeddings stay on local ollama until a self-hosted llama.cpp server takes over. Changing the embedding model or dimension probably needs a full rebuild (training data — verify: LightRAG vector stores are tied to the embedding dimension).
- **`install.sh` copies from the checkout.** It copies `templates/wiki-*` out of the main checkout into `~/.local/bin`, so pull *before* installing or you reinstall stale scripts.

## Related

- [[syntheses/local-rag-wiki]]: the two-path architecture, tool usage and design choices
- [[concepts/wikilink-graph-extraction]]: why the chunker prepends the wikilink header
- [[entities/qmd]]: the BM25 + vector engine
- [[entities/opencode-go]]: the extraction LLM provider and its usage limits
- [[concepts/bm25]]: lexical retrieval used by qmd
- [[concepts/linux-setup-guide]]: installing the indexing tools on a fresh machine
