---
title: "Compounding Knowledge Base"
type: concept
tags: [llm, knowledge-management, wiki, rag, epistemics]
sources: [llm-wiki.md]
created: 2026-04-21
updated: 2026-04-21
---

# Compounding Knowledge Base

A knowledge base where each new source and each query adds to a persistent, interlinked structure — rather than being processed in isolation at retrieval time.

## The core distinction: compilation vs. retrieval

**RAG** (Retrieval-Augmented Generation): raw documents sit indexed; at query time the LLM retrieves relevant chunks and generates an answer from scratch. Nothing is built up. Ask a question requiring synthesis across five documents and the LLM must find and piece together fragments every time.

**Compounding knowledge base**: the LLM *compiles* knowledge incrementally as sources arrive. Cross-references are already built. Contradictions already flagged. Synthesis already reflects everything ingested. Each new source strengthens or revises the existing structure rather than adding to a pile.

The difference is analogous to an **interpreted vs. compiled program**: RAG interprets source documents on every query; the compounding wiki compiles them once and keeps the result current.

## Why it compounds

- **Ingested sources** → summary + entity/concept page updates (one source touches many pages)
- **Answered queries** → good answers get filed back as new pages; explorations accumulate
- **Lint passes** → contradictions resolved, gaps identified, cross-references added

The wiki accretes value from all three operations, not just from ingestion.

## Why humans abandon wikis

The bottleneck isn't reading or thinking — it's bookkeeping. Updating cross-references, keeping summaries current, noting when new data contradicts old claims, maintaining consistency across dozens of pages. This cost grows faster than value. LLMs remove the bottleneck: they don't get bored, don't forget a cross-reference, can touch 15 files in one pass.

## The human's role

Curation, direction, and synthesis judgment. Specifically: which sources to ingest, what questions to ask, whether the LLM's synthesis is right, where to push deeper. The LLM handles all the maintenance.

## RAG nuance

> **Note (2026-04-22):** [[contextual-retrieval]] significantly improves RAG — −49% retrieval failure with contextual embeddings + BM25, −67% with reranking. The contrast above ("nothing accumulates") remains valid for standard RAG but overstates the ceiling. Improved RAG is a legitimate option for knowledge bases that don't need the cross-source synthesis a compiled wiki provides. The distinction is still real: RAG answers queries from raw sources; a compounding wiki builds durable structure. But the gap is smaller than implied when RAG is properly implemented.

## Related

- [[llm-wiki-pattern]] — the specific implementation of this pattern described by Karpathy
- [[qmd]] — search tool that enables efficient query operations as the wiki scales
- [[contextual-retrieval]] — technique that significantly narrows the RAG/wiki performance gap for retrieval tasks
