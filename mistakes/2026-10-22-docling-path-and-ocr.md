---
date: 2026-10-22
type: tool-failure
domain: docling
severity: low
---

# docling not on PATH; default OCR crashes in rapidocr

## What happened
1. `docling` returned "command not found". It is installed as a uv tool (v2.107.0), but neither `~/.local/bin/docling` nor a PATH shim exists; the binary is at `~/.local/share/uv/tools/docling/bin/docling`.
2. The first run with the full path failed: `ValueError: Unsupported configuration: torch.PP-OCRv6.det.small` from rapidocr. The default pipeline enables OCR even for PDFs that have a text layer.

## What the fix was
Ran `~/.local/share/uv/tools/docling/bin/docling <pdf>... --no-ocr --to md --output <job tmp>/`. Both PDFs parsed. The output embeds images as base64 `data:image` lines (1.3 MB for a 33-page paper), so strip them (`rg -v 'data:image'`) before reading. Equations come out as `<!-- formula-not-decoded -->`.

## Prevention rule
If `docling` is not found, use `~/.local/share/uv/tools/docling/bin/docling` (or `uv tool update-shell`). For text-layer PDFs pass `--no-ocr`. Strip `data:image` lines before reading the output.

## Context
PDF ingest of `pdfs/self-healing-agentic-orchestrator-LLM-research.pdf` and `pdfs/confidence-aware-routing-for-llm-reliability-system-one-laya-jev-open-source.pdf`.
