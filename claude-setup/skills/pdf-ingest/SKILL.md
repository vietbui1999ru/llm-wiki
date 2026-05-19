---
name: pdf-ingest
description: Use when ingesting a PDF from pdfs/ into the LLM wiki. Runs Docling to parse the PDF into structured markdown, then follows standard wiki ingest steps. Invoke whenever the user says "ingest" and the source is a .pdf file.
allowed-tools: "Bash,Read,Write,Edit"
---

# PDF Ingest — Docling-Powered Wiki Ingest

## When to invoke

The user says any of:
- "ingest pdfs/paper.pdf"
- "ingest [arxiv-id].pdf"
- "ingest" when the source is a file in `pdfs/`

## Step 1: Resolve the PDF path

Extract the filename. If the user didn't specify the full path, assume `pdfs/<filename>` relative to `~/repos/llm-wiki/`.

```bash
ls ~/repos/llm-wiki/pdfs/
```

Confirm the file exists before proceeding.

## Step 2: Resolve Docling CLI docs via context7

Before running any docling command, get the current CLI reference:

```
mcp__context7__resolve-library-id: {"libraryName": "docling"}
mcp__context7__query-docs: {"context7CompatibleLibraryID": "<id>", "topic": "CLI usage output format flags", "tokens": 2000}
```

Use the returned docs to confirm exact flag names. Do not assume flags from memory.

## Step 3: Check Docling is installed

```bash
command -v docling || uv tool list 2>/dev/null | grep docling
```

If not found:
```bash
uv tool install docling
```

If uv isn't available, fallback:
```bash
pip install docling
```

## Step 3: Parse with Docling

Create the output dir and run Docling:

```bash
mkdir -p /tmp/docling-wiki-out
cd ~/repos/llm-wiki && docling "pdfs/<filename>.pdf" --to md --output /tmp/docling-wiki-out/
```

Docling names the output file using the PDF's base name: `/tmp/docling-wiki-out/<filename>.md`

Verify:
```bash
ls /tmp/docling-wiki-out/
```

## Step 4: Read the parsed markdown

Read the Docling output from `/tmp/docling-wiki-out/<filename>.md`. This is your source for ingest — not the original PDF.

Pay attention to:
- Table structure (Docling preserves rows/columns — represent them faithfully)
- Formulas (Docling outputs LaTeX — include inline in the wiki page)
- Section headers (use these as chunk/section boundaries in the summary)
- Figure captions (Docling extracts these — include key ones)

## Step 5: Pre-ingest comprehension (unless user says skip)

Apply the standard comprehension rule: ask 3–5 questions to test understanding of:
1. What problem the paper addresses
2. Key technical contributions
3. How it connects to existing wiki pages

Skip if user says "skip review" or "just add".

## Step 6: Write wiki pages

Follow standard ingest steps from CLAUDE.md:

**Summary page** (`wiki/summaries/<slug>.md`):
- Structure for research papers: Abstract → Problem → Methods → Key Results → Limitations → Connections to existing wiki
- Preserve key quantitative results (numbers matter in papers)
- Note important tables/figures by name if they're central to the contribution

**Entity or concept pages** if the paper introduces a named system, model, technique, or algorithm.

Frontmatter `sources:` field — reference the **PDF**, not the temp markdown:
```yaml
sources: ["pdfs/1703.03864v2.pdf"]
```

## Step 7: Update index.md and log.md

Standard ingest log format:
```
## [YYYY-MM-DD] ingest | <Paper Title> (<arxiv-id or filename>) → summaries/<slug>[, entities/<name>]
```

## Step 8: Clean up temp output

```bash
rm -rf /tmp/docling-wiki-out/
```

## Fallback: Claude native PDF reading

If Docling fails (install error, parse error, unsupported file):
1. Read the PDF directly using the Read tool from `pdfs/<filename>.pdf`
2. Note in the log entry: `[native PDF reading — Docling unavailable]`
3. For tables and formulas: describe structure in prose if extraction is lossy
