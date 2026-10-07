---
title: "Retrieval Evaluation Suite: qmd vs LightRAG"
type: concept
tags: [retrieval, evaluation, rag, qmd, lightrag, ndcg, regression-gate, latency, golden-set]
sources: ["docs/specs/retrieval-eval-suite.md", "docs/retrieval-eval.md", "tests/retrieval/", "PRs #12 to #16 and the M5 PR of vietbui1999ru/llm-wiki", "run outputs of 2026-10-06 and 2026-10-07"]
created: 2026-10-07
updated: 2026-10-07
---

# Retrieval Evaluation Suite: qmd vs LightRAG

A repeatable measurement of how well the two retrieval systems over this wiki ([[entities/qmd]] and the LightRAG graph in [[systems/wiki-indexing-pipeline]]) find the right pages, how fast they are, and whether a change made them worse. Before it existed the wiki had no measured retrieval quality at all. Design and decisions: `docs/specs/retrieval-eval-suite.md`; how to run it: `docs/retrieval-eval.md`; code and committed baselines: `tests/retrieval/`.

## How it works

- **Unit of scoring is the wiki page.** qmd's collection covers the whole repo (including `raw/` clips and meta pages), LightRAG only `wiki/**`, so qmd results are filtered to `wiki/**` after retrieval.
- **Golden set:** 114 synthetic queries (paraphrase 25%, alias 20%, relational 20%, exact 18%, overview 9%, null 9%) with graded relevant pages and a 70/30 dev/held-out split. Queries were written by a Claude model, not the DeepSeek model that built the graph, and pass hard gates against leaking page-specific wording.
- **Metrics:** nDCG@10 (headline) and Recall@5/10 per query, averaged per category with 95% bootstrap CIs; paired permutation tests and the minimum detectable effect for system comparisons ([[concepts/rag-evaluation]] covers the split between retrieval metrics and answer-quality judging; answer quality is deliberately out of scope here).
- **Nine systems:** qmd bm25, vector, hybrid, full; LightRAG naive, local, global, hybrid, mix.
- **Gate:** committed per-query baselines; warn when the mean nDCG@10 falls more than 0.03, fail when the paired CI of the drop excludes zero or a `must_hit` query leaves the top 3; a rebuilt LightRAG index is report-only because extraction is non-deterministic.

## What it found (measured here, 2026-10-06, 104 non-null queries)

- **No detectable difference between qmd and LightRAG.** nDCG@10 ranges 0.645 to 0.711 across the eight non-BM25 systems with overlapping CIs; the designated comparisons (qmd full vs LightRAG mix, qmd hybrid vs LightRAG naive) are not significant and the minimum detectable effect is about 0.09. No graph mode beat flat retrieval on relational queries.
- **BM25 fails on natural language** (about 0.92 nDCG on exact titles, 0.03 to 0.12 elsewhere) because qmd ANDs all terms. Among the non-exact categories, overview queries score lowest for the non-BM25 systems (0.44 to 0.54), but there are only 10 of them.
- **Latency differs by orders of magnitude but is not like for like.** A novel qmd CLI query takes about 5 s without rerank and about 21 s with it; a repeat takes about 3 s because qmd caches expansion and rerank results. A LightRAG call in a warm process takes about 35 ms for `naive` and about 2 s for a novel graph-mode query (almost all keyword LLM), about 0.1 s once cached.
- **The numbers are provisional.** Labels are agent-reviewed only (the human spot-check is still open), about four in five returned top-10 pages have no label, and synthetic queries make absolute scores optimistic.

## Gotchas found while building it

- `qmd bench` returns at most 10 files per query and cannot be changed; after filtering to `wiki/**` only about 3 pages were left and Recall@5 equalled Recall@10. The runners call the qmd CLI with `-n 50` instead.
- Ten LightRAG chunks collapse to about 7 distinct pages, so `chunk_top_k` is 30 to make page-level Recall@10 meaningful.
- qmd caches query expansions by text, shared across backends, and rerank results too; a cache state you assume rather than control gives wrong "cold" numbers. qmd's cold expansion is bimodal (median 2.8 s, 23% above 8 s) for a reason not found.
- LightRAG does not cache a keyword extraction that returns no low-level keywords, so a few queries pay the LLM on every call. When nothing passes the thresholds `aquery_data` returns `status: failure, "No relevant document chunks found."`, which is an empty result, not an error.
- Labels adjusted by pooling the systems' own top results are not independent of those systems.

## Related

- [[systems/wiki-indexing-pipeline]]: what is being measured and how it is built
- [[entities/qmd]]: the BM25 + vector engine
- [[concepts/rag-evaluation]]: retrieval vs generation metrics
- [[concepts/llm-eval-pipeline]]: the wider eval methodology
- [[concepts/bm25]]: why lexical search fails on natural-language queries
