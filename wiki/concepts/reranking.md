---
title: "Reranking"
type: concept
tags: [rag, retrieval, search, ranking]
sources: [Contextual Retrieval in AI Systems.md]
created: 2026-04-22
updated: 2026-04-22
---

# Reranking

A post-retrieval filtering step in RAG pipelines. Takes a large candidate set from initial retrieval, scores each chunk against the query with a dedicated reranking model, passes only the top-K to the LLM.

## Pipeline position

```
query
  → initial retrieval (BM25 + embeddings) → top ~150 candidates
  → reranker scores each candidate vs. query
  → top 20 passed to LLM as context
```

Initial retrieval optimizes for recall (broad net). Reranking optimizes for precision (tight filter).

## Why it helps

Initial retrieval is fast but coarse — embedding similarity doesn't perfectly reflect query relevance. Rerankers are cross-encoders: they see query and chunk together, enabling richer relevance judgments than embedding cosine similarity.

## Trade-offs

| | Value |
|---|---|
| Latency | small addition (chunks scored in parallel) |
| Cost | per-query reranker call on 150 chunks |
| Benefit | −67% retrieval failure when combined with contextual retrieval (vs. −49% without) |

Tune retrieval pool size vs. reranking cost for your latency budget.

## Models

Cohere Rerank (tested by Anthropic). Voyage also offers a reranker. Cross-encoder models generally.

## Related

- [[concepts/contextual-retrieval]] — gains stack: contextual retrieval + reranking = −67% vs. baseline
- [[concepts/bm25]] — part of initial retrieval that feeds the reranker
