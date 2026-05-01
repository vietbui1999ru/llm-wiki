---
title: "Docling"
type: entity
tags: [document-parsing, pdf, rag, ai-tools, ibm]
sources:
  - "Docling.md"
  - "docling-projectdocling Get your documents ready for gen AI.md"
created: 2026-04-30
updated: 2026-04-30
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

## Relation to other tools

- Complements [[entities/firecrawl]]: Firecrawl handles web URLs; Docling handles files and PDFs
- Works upstream of [[concepts/contextual-retrieval]]: clean Docling output → better chunk context → better retrieval

See [[summaries/docling]] for the full analysis including RAG pipeline context.
