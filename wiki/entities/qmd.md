---
title: "qmd"
type: entity
tags: [tooling, search, markdown, cli, mcp, retrieval]
sources: ["llm-wiki.md", "qmd --help (qmd 2.8.3, read 2026-10-14)", "docs/retrieval-eval.md", "docs/experiments/laya-rerank/README.md"]
created: 2026-04-21
updated: 2026-10-14
---

# qmd

A local search engine for markdown files ("Quick Markdown Search"), used here as the retrieval engine behind the wiki-context skill and the `qmd query` lookups the project instructions require. This setup runs qmd 2.8.3. It is a CLI and an MCP server (`qmd mcp`, stdio) over one sqlite index at `~/.cache/qmd/index.sqlite`.

## Search modes

| Command | What it does | LLM involved |
|---|---|---|
| `qmd search` | BM25 keyword search | no |
| `qmd vsearch` | vector similarity only | embeddings only |
| `qmd query --no-rerank` | hybrid: BM25 plus vector, fused | query expansion |
| `qmd query` | hybrid plus automatic query expansion and reranking (the recommended mode, called `full` in the eval suite) | expansion and reranker |

`qmd query` also accepts a multi-line structured document whose lines are typed `lex:`, `vec:` or `hyde:` (with an optional `intent:` line) when you want to control the sub-queries yourself. `qmd get <file>[:from[:count]]` and `qmd multi-get` fetch documents by path, glob or `#docid`.

## Setup in this repo

- **Collections:** `wiki`, `Obsidian` and `career`. On 2026-10-11 the index held 1,589 files and 9,032 embedded chunks. The `wiki` collection's pattern is `**/*.md` over the whole repo, so results include `raw/` clips and meta pages as well as `wiki/**` pages; filter to `wiki/**` when you score or cite.
- **Keeping it current:** the `post-commit` hook runs `qmd update` and `qmd embed` synchronously after each commit (incremental, seconds); see [[systems/wiki-indexing-pipeline]]. `qmd pull` downloads its embedding, generation and rerank models; I have not verified which models it uses.
- **Housekeeping:** `qmd status` reported 688 orphaned embedding chunks (8%) on 2026-10-11; `qmd cleanup --dry-run` shows what it would drop.

## Measured here

From the retrieval evaluation suite ([[systems/retrieval-eval-suite]]; 114 synthetic queries, labels agent-reviewed, so absolute scores are optimistic):

- nDCG@10 on 104 scored queries, fresh run 2026-10-12: `hybrid` 0.681, `full` 0.713. Both reproduce the committed baseline (0.676 and 0.715).
- No detectable difference between qmd and the LightRAG graph in the suite's pre-designated comparisons.
- BM25 fails on natural-language queries because qmd ANDs every term; it is only good for exact titles.
- Latency per CLI call: about 5 s without rerank and about 21 s with it; repeats are faster because qmd caches expansions and rerank results by text.
- An external reranker did not help: zero-shot Laya reranking of the `hybrid` candidates scored 0.651 (and 0.507 to 0.629 in three variants), below both `hybrid` and `full` ([[entities/laya]], `docs/experiments/laya-rerank/README.md`).

## Gotchas

- `qmd bench` returns at most 10 files per query; after the `wiki/**` filter only about 3 pages remain, so the suite calls the CLI with `-n 50` instead.
- Adding a file outside `wiki/` can shift rankings, because the collection is the whole repo.
- Rankings 2 to 12 of `full` come from near-flat reranker scores and reshuffle under small corpus changes, so treat `full`'s must-hit losses as informational and `hybrid` as the reference.

## Related

- [[concepts/bm25]] — the lexical half of the hybrid mode
- [[concepts/reranking]] — what the `full` mode adds
- [[systems/wiki-indexing-pipeline]] — how the index is built and refreshed
- [[systems/retrieval-eval-suite]] — how it was measured
