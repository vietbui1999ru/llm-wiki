---
title: "Contextual Retrieval in AI Systems"
type: summary
tags: [rag, retrieval, embeddings, bm25, reranking, search]
sources: [Contextual Retrieval in AI Systems.md]
created: 2026-04-22
updated: 2026-04-22
---

# Contextual Retrieval in AI Systems

Source: `raw/Contextual Retrieval in AI Systems.md` — Anthropic blog post on improving RAG retrieval accuracy via chunk contextualization.

## Core problem

Traditional RAG splits documents into chunks and embeds them without preserving document context. A chunk like *"The company's revenue grew by 3% over the previous quarter"* has no company name or time period — retrieval fails because the chunk is ambiguous in isolation.

## Solution: Contextual Retrieval

Before embedding and before BM25 indexing, prepend a short (50-100 token) LLM-generated context to each chunk:

```
original: "The company's revenue grew by 3% over the previous quarter."
contextualized: "This chunk is from an SEC filing on ACME Corp's Q2 2023 performance; 
prior quarter revenue was $314M. The company's revenue grew by 3% over the previous quarter."
```

Two sub-techniques applied together:
- **Contextual Embeddings** — context prepended before vectorization
- **Contextual BM25** — context prepended before BM25 index creation

## Results (retrieval failure rate, top-20 chunks)

| Technique | Failure rate | Reduction |
|---|---|---|
| Baseline (BM25 + embeddings) | 5.7% | — |
| + Contextual Embeddings | 3.7% | −35% |
| + Contextual Embeddings + Contextual BM25 | 2.9% | −49% |
| + Reranking (all above) | 1.9% | −67% |

Best embeddings: Gemini Text 004, Voyage.

## Implementation

Context generated per-chunk via Claude 3 Haiku using a prompt that passes the full document + chunk. With **prompt caching**, the document is loaded once — cost: ~$1.02 per million document tokens.

## Reranking pipeline

1. Initial retrieval → top 150 chunks (BM25 + embeddings)
2. Reranking model scores all 150 against query
3. Top 20 passed to model as context

Reranker tested: Cohere. Adds latency but results stack with contextual retrieval gains.

## Simple alternative

If knowledge base < 200k tokens (~500 pages): skip RAG, include everything in the prompt. Prompt caching makes this fast and cheap.

## Implementation notes

- Chunk size/boundary/overlap matters — tune for your domain
- Custom contextualizer prompts (with domain glossary) outperform generic prompt
- Top-20 chunks outperforms top-10 and top-5
- Pass contextualized chunk to model, distinguish context from chunk content

## Relevance to this wiki

qmd (used for query operations here) uses BM25 + vector hybrid — the same combination this paper validates as superior to either alone. Contextual Retrieval is the next step if qmd ever exposes a pre-indexing hook.
