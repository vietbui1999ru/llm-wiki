---
date: 2026-04-30
type: cli-flag
domain: docling
severity: low
---

# docling: --output not --output-dir

## What happened
Used `docling "file.pdf" --to md --output-dir /tmp/out/` — flag does not exist.

## What the fix was
`docling "file.pdf" --to md --output /tmp/out/` — correct flag is `--output`.

## Prevention rule
Run `<cmd> --help` before assuming flag names for any unfamiliar CLI tool.

## Context
Parsing research PDFs for wiki ingest. Three parallel docling calls all failed with same error.
