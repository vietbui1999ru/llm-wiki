---
title: "Docling"
type: entity
tags: [document-parsing, pdf, rag, ai-tools, ibm]
sources:
  - "Docling.md"
  - "docling-projectdocling Get your documents ready for gen AI.md"
  - "From PDF to Markdown Why Document Parsing is Important For RAG..md"
created: 2026-04-30
updated: 2026-05-27
---

# Docling

Open-source document parsing library from IBM Research Zurich. Converts PDFs and other document formats into structured representations suitable for RAG pipelines, LLM ingestion, and agentic workflows.

## Core abstraction

All inputs parse to a **DoclingDocument** — a structured intermediate object from which you export Markdown, JSON, HTML, or DocTags. Programmatic access to individual components (tables, figures, text blocks) is available before export.

## Quick start

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
doc = converter.convert("https://arxiv.org/pdf/2408.09869").document
print(doc.export_to_markdown())
```

```bash
# CLI
docling https://arxiv.org/pdf/2206.01062

# VLM pipeline (Apple Silicon MLX accelerated)
docling --pipeline vlm --vlm-model granite_docling path/to/paper.pdf
```

## Key capabilities

- Layout-aware PDF parsing: reading order, multi-column, headers/footers
- Table structure extraction (rows, columns, multi-level headers)
- Formula → LaTeX conversion
- Figure classification and description generation
- OCR for scanned PDFs
- Audio transcription (ASR)
- Local / air-gapped execution

## Integration

- Python: `pip install docling`
- MCP server: `docling-mcp` (agent-accessible without custom code)
- Framework integrations: LangChain, LlamaIndex, Haystack, Crew AI

## vs. Firecrawl

| | Docling | Firecrawl |
|--|---------|-----------|
| Primary target | Local files + PDFs | Web URLs |
| Strength | High-fidelity document structure | HTML → clean markdown |
| OCR | Yes (scanned PDFs) | No |
| Table extraction | Deep (structure-aware) | Surface-level |
| Audio/images | Yes | No |
| Use case | Research papers, reports, contracts | Web pages, crawling, SPA content |

Complementary: Firecrawl for web, Docling for files. See [[entities/firecrawl]].

## RAG Pipeline Role

Docling slots at the ingestion layer — before chunking, embedding, or retrieval:

```
raw documents → Docling → DoclingDocument → Markdown/JSON → chunk → embed → vector store
```

Chunking guidance: split on `##` section headers, not fixed token counts. Keep figure/table blocks intact — splitting mid-table destroys the relational structure. Docling's block metadata makes section boundaries explicit.

Combined with [[concepts/contextual-retrieval]] (prepend context to chunks before embedding), Docling-quality parsing maximizes retrieval precision.

## Relation to other tools

- Complements [[entities/firecrawl]]: Firecrawl handles web URLs; Docling handles files and PDFs
- Works upstream of [[concepts/contextual-retrieval]]: clean Docling output → better chunk context → better retrieval
