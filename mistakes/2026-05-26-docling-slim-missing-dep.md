---
date: 2026-05-26
type: bad-assumption
domain: docling
severity: medium
---

# docling-slim missing pypdfium2 at runtime

## What happened
Assumed `docling` installed via `uv tool install docling-slim` was functional. Running `docling ... --to md --output` failed with `ModuleNotFoundError: No module named 'pypdfium2'`.

## What the fix was
Fall back to native PDF reading via Claude's Read tool. Log entry notes `[native PDF reading — Docling unavailable]`.

## Prevention rule
Before running docling, verify runtime works: `docling --version` or `python -c "import pypdfium2"`. `docling-slim` omits pypdfium2 — full install requires `uv tool install docling` (not slim).

## Context
PDF ingest of `pdfs/17241_Autoencoding_Free_Contex.pdf` during wiki ingest session.
