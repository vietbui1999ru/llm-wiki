---
title: "Local RAG with Elasticsearch + LocalAI"
type: summary
tags: [rag, local-llm, elasticsearch, localai, embeddings, privacy, latency]
sources:
  - "Local RAG personal knowledge assistant LocalAI and Elasticsearch.md"
created: 2026-05-11
updated: 2026-05-11
---

# Local RAG with Elasticsearch + LocalAI

End-to-end local RAG system on a mid-range laptop (8GB RAM). Elasticsearch for vector storage and semantic search; LocalAI (Docker, OpenAI-compatible API) for inference. Zero cloud dependencies.

---

## Stack

| Component | Tool | Notes |
|---|---|---|
| Vector DB | Elasticsearch 9.x (Docker) | `start-local` single-command setup |
| Embeddings | multilingual-e5-small | Built into Elasticsearch, auto-deployed |
| Inference | LocalAI (Docker) | OpenAI-compatible `/v1/chat/completions` |
| Python client | `elasticsearch` + `openai` packages | Standard libraries |

---

## Model Comparison (same query, same hardware)

| Model | Memory | Latency | Tokens/s |
|---|---|---|---|
| dolphin3.0-qwen2.5-0.5b | ~200 MB | 16,044 ms | 9.5 |
| llama-smoltalk-3.2-1b-instruct | ~700 MB | 21,019 ms | 5.8 |
| smollm2-1.7b-instruct | ~1 GB | 47,561 ms | 4.8 |

**Key finding**: smallest model (0.5B) produced best tokens/s. Retrieval latency was 14ms — LLM inference dominates total latency (16s out of 17s total). Retrieval is never the bottleneck.

---

## Architecture Pattern

```
Documents → Elasticsearch (e5-small embed) → semantic_text field
Query → semantic_search() → top-3 hits → prompt → LocalAI LLM → answer
```

1. **Index**: Elasticsearch `semantic_text` field type handles embedding automatically via inference endpoint
2. **Retrieve**: `{"query": {"semantic": {"field": "semantic_field", "query": query}}}` → 14ms
3. **Synthesize**: LocalAI chat completion with citations — 16,000ms for 0.5B model

---

## Key Advantages of Local Stack

- **Privacy**: data never leaves machine; suitable for sensitive/air-gapped environments
- **Cost**: no per-token API fees for embeddings or completion
- **Flexibility**: swap models by changing one variable; LocalAI model gallery + third-party embeddings
- **Speed**: can be faster than cloud for small models with no network overhead

---

## Practical Notes

- Docker memory: 1.9 GB for Elasticsearch + 200 MB for LocalAI (0.5B model) = comfortable in 8 GB
- LocalAI consumes 100% CPU during inference (0.5B model, 6 cores)
- Air-gapped e5-small install: documented in Elasticsearch official docs
- Token counting: `LocalAI` returns `usage.completion_tokens` for tokens/s calc

---

## Relevance to This Wiki

- Confirms: retrieval (14ms) is never the bottleneck; LLM synthesis always dominates
- Our stack (nomic-embed-text + phi4-mini via ollama) follows the same pattern
- Elasticsearch approach scales better for large corpora; LightRAG/ollama is simpler for single-machine wiki
- For the wiki's ~149 pages, LightRAG graph is the right tier; Elasticsearch becomes relevant at 1000+ docs

---

## Related Pages

- [[syntheses/local-rag-wiki]] — wiki-chat architecture and RAG upgrade path
- [[summaries/agentic-search-vs-rag]] — why graph retrieval beats flat RAG for structured content
- [[concepts/contextual-retrieval]] — prepending context to chunks for better retrieval
- [[concepts/bm25]] — lexical complement to semantic search
