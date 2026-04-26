---
title: "Contextual Retrieval"
type: concept
tags: [rag, retrieval, embeddings, bm25, search, llm]
sources: [Contextual Retrieval in AI Systems.md]
created: 2026-04-22
updated: 2026-04-22
---

# Contextual Retrieval

A RAG preprocessing technique that prepends chunk-specific context to each chunk before embedding and BM25 indexing — preserving document provenance that traditional chunking strips away.

## The problem it solves

Standard RAG chunks split documents at token boundaries with no awareness of where they came from. Chunks become decontextualized fragments. Retrieval fails when the query's intent maps to document-level context that no longer exists in the chunk.

## Mechanism

For each chunk, an LLM generates a short (50-100 token) context string that situates the chunk within its source document. This context is prepended to the chunk text before both:
- Vectorization (Contextual Embeddings)
- BM25 index construction (Contextual BM25)

The chunk itself is unchanged. Only the indexed representation gains context.

## Why both BM25 and embeddings

Embeddings capture semantic similarity; BM25 captures exact lexical matches. Neither alone is sufficient:
- Embeddings miss exact identifiers ("error code TS-999", specific names)
- BM25 misses paraphrase and semantic proximity

Applied together with context, their weaknesses don't overlap.

## Cost model

LLM context generation is the expensive step. With prompt caching (full document cached, only chunk varies per call): ~$1.02/million document tokens using Claude 3 Haiku.

## Performance

−49% retrieval failure vs baseline (BM25 + embeddings without context). Adding reranking: −67%.

## Related

- [[concepts/bm25]] — the lexical retrieval half of the pipeline
- [[concepts/reranking]] — post-retrieval filtering that stacks with contextual retrieval gains
- [[concepts/compounding-knowledge-base]] — alternative pattern where context is pre-compiled into wiki pages rather than prepended at index time
- [[entities/qmd]] — local search engine using the BM25 + vector hybrid this technique validates
- [[summaries/contextual-retrieval]] — Anthropic source; full performance numbers and cost model
