---
title: "Agentic Search vs RAG — Experimental Validation"
type: summary
tags: [rag, retrieval, agentic-search, context-trees, token-efficiency, code-retrieval]
sources:
  - "RyanNg1403agentic-search-vs-rag Experimental validation Agentic Search (context trees) vs traditional RAG for code retrieval. Agentic wins with 99% fewer tokens and 2× better accuracy. Fully reproducible with automated pipelines..md"
  - "RyanNg1403agentic-search-vs-rag Experimental validation Agentic Search (context trees) vs traditional RAG for code retrieval. Agentic wins with 99% fewer tokens and 2× better accuracy. Fully reproducible with automated pipelines. 1.md"
  - "RyanNg1403agentic-search-vs-rag Experimental validation Agentic Search (context trees) vs traditional RAG for code retrieval. Agentic wins with 99% fewer tokens and 2× better accuracy. Fully reproducible with automated pipelines. 2.md"
created: 2026-05-11
updated: 2026-05-11
---

# Agentic Search vs RAG — Experimental Validation

Reproducible benchmark comparing vector-based RAG with Agentic Search (context trees) for code retrieval. Codebase: gemini-cli (~1300 files, TypeScript). 30 questions across 4 query types.

---

## Setup

**RAG**: OpenAI `text-embedding-3-small` → Qdrant → top-5 file retrieval  
**Agentic**: ByteRover (`brv query`) context trees with 42 curated topics, adaptive 1–10 file retrieval

---

## Results

| Metric | RAG | Agentic | Delta |
|---|---|---|---|
| IoU Score | 0.036 | 0.073 | **+106%** |
| Precision | 0.053 | 0.117 | **+119%** |
| Recall | 0.108 | 0.097 | −9% |
| Tokens/query | 8,775 | 72 | **−99.2%** |

**Recall trade-off**: RAG retrieves a fixed 5 files per query → higher raw recall, but irrelevant files dilute context and increase hallucination risk. Agentic is adaptive (1–10 files).

---

## By Query Type

| Query type | RAG IoU | Agentic IoU | Winner |
|---|---|---|---|
| Direct (single file) | 0.050 | 0.188 | Agentic **3.7×** |
| Feature (module-wide) | 0.026 | 0.036 | Agentic 1.4× |
| Refactoring (impact analysis) | 0.037 | 0.048 | Agentic 1.3× |
| Dependency (multi-file relations) | 0.030 | 0.016 | **RAG 1.9×** |

RAG's only win is dependency queries — its fixed 5-file retrieval happens to catch more files in multi-file scenarios, despite low precision.

---

## Why RAG Fails for Graph-Structured Content

- Treats content as "bag of words" — ignores relationships
- Retrieves deprecated/test/backup files with similar keywords
- Cannot understand architectural boundaries or intent
- Fixed retrieval count regardless of query complexity

**Generalizes beyond code**: Any corpus where content is graph-structured (wiki concepts with cross-links, entity relationships, knowledge graphs) suffers the same failure mode.

---

## Why Agentic/Graph Search Wins

- Intent-based: understands *what* the query asks, not keyword similarity
- Dependency-aware: traverses relationships (import graphs → wikilinks)
- Adaptive: returns exactly as many results as needed
- Context-preserving: returns answers + paths, not full file dumps → 99% token reduction

---

## Wiki Relevance

This experiment directly validates the switch from BM25+ollama to LightRAG for this wiki:

- Wiki pages are concept nodes with dense `[[wikilinks]]` — structurally identical to a code graph
- LightRAG's entity/relation extraction builds the equivalent of context trees from wikilinks + text
- `hybrid` mode covers the dependency-query edge case where flat retrieval wins on recall
- The 99% token reduction means faster synthesis — smaller context = faster phi4-mini response

---

## Related Pages

- [[syntheses/local-rag-wiki]] — wiki-chat architecture; RAG upgrade path
- [[concepts/contextual-retrieval]] — flat RAG improvement baseline
- [[concepts/reranking]] — post-retrieval filtering (complementary to graph retrieval)
- [[summaries/local-rag-elasticsearch]] — local RAG implementation reference
- [[concepts/wikilink-graph-extraction]] — using Obsidian wikilinks to reduce LightRAG indexing cost; structural complement to context trees
