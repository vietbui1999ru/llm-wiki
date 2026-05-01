---
title: "Docling — Document Parsing for AI"
type: summary
tags: [document-parsing, rag, pdf, ai-tools, data-extraction]
sources:
  - "Docling.md"
  - "From PDF to Markdown Why Document Parsing is Important For RAG..md"
  - "docling-projectdocling Get your documents ready for gen AI.md"
created: 2026-04-30
updated: 2026-04-30
---

# Docling — Document Parsing for AI

Three sources: official homepage feature overview, a RAG rationale article (why parsing quality matters), and the GitHub README. Collectively cover the problem, solution, and implementation details.

---

## The Core Problem: Naive PDF Extraction Breaks RAG

RAG pipelines embed text chunks into a vector store and retrieve by similarity. Chunk quality determines retrieval quality. Naive PDF-to-text extraction degrades chunks in four ways:

| Failure | Effect on RAG |
|---------|--------------|
| Broken tables | Numbers and headers mixed into paragraphs; retrieval returns incomplete rows |
| Lost headings | No semantic hierarchy; chunk boundaries ignore section structure |
| Garbled layout | Multi-column docs produce jumbled reading order |
| Noise (headers/footers/page numbers) | Pollutes chunks, dilutes relevance scores |

The fix: layout-aware parsing that preserves structure before chunking.

## Why Markdown is the Right Intermediate Format

Markdown makes structure explicit (headings, tables, lists, code blocks) instead of encoding it in physical layout. Benefits for RAG:
- Natural chunk boundaries: split on `##` or block type, not arbitrary token counts
- Semantic units stay intact: a table row or code block doesn't span chunks
- LLMs embed it predictably (most training data is Markdown-formatted)

## What Docling Does

IBM Research Zurich project, now under LF AI & Data Foundation. Converts documents to a unified **DoclingDocument** internal representation, then exports to downstream formats.

### Input formats
- Rich: PDF, DOCX, PPTX
- Markup: Markdown, HTML, AsciiDoc, LaTeX, WebVTT
- Tabular: XLSX, CSV
- Images: PNG, JPEG, TIFF, BMP, WEBP
- Audio: MP3, WAV (via ASR)

### Export formats
- Markdown (primary for RAG)
- HTML, JSON (lossless), DocTags, plain text

### Layout intelligence
- Reading order detection (handles multi-column layouts)
- Table structure extraction: rows, columns, multi-level headers, complex cell content
- Formula detection → LaTeX conversion
- Code block detection + language classification
- Figure/chart extraction with classification (chart type, diagram type) and auto-generated descriptions
- Header/footer detection and optional exclusion from exports
- Bounding box metadata per component (for custom downstream processing)
- OCR support for scanned documents

### DoclingDocument: Unified Intermediate
Rather than converting PDF→Markdown directly, Docling parses into a structured document object. This allows:
- Multiple export targets from one parse (JSON, Markdown, HTML)
- Programmatic extraction of specific components (just tables, just figures)
- Chunk metadata (position, type, reading order index) for custom chunking strategies

## Integration Paths

| Path | How |
|------|-----|
| Python library | `pip install docling` → `DocumentConverter().convert(source)` |
| CLI | `docling <url or path>` |
| MCP server | `docling-mcp` — connects to any MCP-compatible agent |
| LangChain / LlamaIndex / Haystack / Crew AI | Native integrations |

MCP integration means Claude Code agents can invoke Docling directly without custom orchestration code. Relevant: [[concepts/tool-design-for-agents]].

## VLM Pipeline

Docling supports Visual Language Models for layout analysis. GraniteDocling (IBM, 258M params) runs locally with MLX acceleration on Apple Silicon:

```bash
docling --pipeline vlm --vlm-model granite_docling https://arxiv.org/pdf/...
```

Useful when standard layout model (Heron) struggles with complex research paper layouts.

## vs. Firecrawl

| | Docling | Firecrawl |
|--|---------|-----------|
| Primary target | Local files + PDFs | Web URLs |
| Strength | High-fidelity document structure | HTML → clean markdown |
| OCR | Yes (scanned PDFs) | No |
| Table extraction | Deep (structure-aware) | Surface-level |
| Audio/images | Yes | No |
| Use case | Research papers, reports, contracts | Web pages, crawling, SPA content |

See [[entities/firecrawl]] for Firecrawl details. The tools are complementary: Firecrawl for web, Docling for files.

## Research Paper Ingestion Pipeline

Two paths depending on use case:

**For wiki ingest (Claude reads the paper):**
Drop PDF into `pdfs/`. Claude reads it directly via the Read tool — no intermediate file. PDFs and markdown stay in separate directories. See `CLAUDE.md` → Ingest (PDF source).

**For RAG pipelines (programmatic ingestion):**
```
pdfs/paper.pdf
  → Docling parse → Markdown/JSON (output to a separate parsed/ dir or directly to vector store)
  → chunk by section headers: Abstract, Methods, Results, References
  → figure and table blocks as atomic chunks (caption + content together)
  → embed → vector store
```

Key decisions:
- Skip qmd conversion unless you need Quarto front matter or rendering — plain Markdown is sufficient
- Chunk by `#`/`##` boundaries, not by fixed token count; Docling's block metadata makes section boundaries explicit
- Keep figure/table blocks intact; splitting mid-table destroys the relational structure that makes tables useful for retrieval

This produces chunks that map to semantic units the authors intended, not arbitrary token windows.

## Relevance to RAG Pipeline

Docling slots in at the ingestion layer — before chunking, embedding, or retrieval:

```
raw documents → Docling → DoclingDocument → Markdown/JSON → chunk → embed → vector store
```

Combined with [[concepts/contextual-retrieval]] (prepend context to chunks before embedding), Docling-quality parsing maximizes retrieval precision by ensuring chunks carry real semantic content rather than parsing artifacts.
