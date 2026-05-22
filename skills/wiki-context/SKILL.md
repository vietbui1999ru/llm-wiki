---
name: "wiki-context"
description: "Search the llm-wiki for patterns, concepts, and prior decisions before technical work in this repo. Use before design, implementation, review, or workflow decisions."
---

# Wiki Context

Load repo knowledge before proceeding.

## Step 1

Extract 2–3 search terms from task.

## Step 2

Prefer qmd MCP if connected.

Fallback shell:

```bash
qmd query "<terms>" --files --min-score 0.4
```

If qmd shell fails, use the wiki index snapshot already present in ambient instructions and read targeted files directly.

## Step 3

Read top 1–3 relevant pages. Prefer:

- `wiki/concepts/*`
- `wiki/syntheses/*`
- then summaries only if needed

## Step 4

Apply result explicitly:

`Per [[concepts/...]], ...`

## Focus areas for this repo

- agent orchestration
- council pattern
- verification pipeline
- rules vs hooks
- context degradation and compression
- indirect prompt injection

## Failure rule

If no relevant page exists, say so. Do not pretend wiki support exists.
