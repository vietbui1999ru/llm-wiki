---
name: pre-digest
description: Run gemma4:e4b locally to pre-process a source file into structured bullet points before Claude ingests it. Cuts source reading tokens by ~80%. Run before any ingest operation.
---

# Pre-Digest — Local Model Source Processing

## Purpose
Use gemma4:e4b (local, free) to extract structured notes from a raw source.
Claude then works from the pre-digest instead of the full source — saving ~80% of source-reading tokens.

## When to Use
- Before any `ingest` operation on a file in `raw/`
- User says "pre-digest [filename]" or "prep [filename] for ingest"
- Automatically: run this before invoking the ingest workflow on large sources (>500 lines)

## Step 1 — Run gemma4:e4b

```bash
ollama run gemma4:e4b \
  "Extract from this source into structured bullet points:
1) Main problem addressed
2) Key technical claims (max 5)
3) Novel contributions
4) Limitations or caveats
5) Connections to: agent engineering, context management, LLM training, RAG, scraping, security
Be concise — bullet points only, no prose, no preamble.\n\n$(cat raw/<FILENAME>)" \
  2>/dev/null | col -b | sed -n '/\.\.\.done thinking\./,$ p' | tail -n +2 \
  > .claude/pre-digest/<FILENAME>.digest.md
```

Replace `<FILENAME>` with the actual filename from `raw/`.

If source has no thinking block (no `...done thinking.` line), skip the `sed` filter:
```bash
... | col -b > .claude/pre-digest/<FILENAME>.digest.md
```

## Step 2 — Verify Output

```bash
cat .claude/pre-digest/<FILENAME>.digest.md
```

Check:
- All 5 sections present
- No escape codes or garbled characters
- Key claims look accurate (spot-check 1-2 against source)

If output is garbled or missing sections: re-run once. If still bad, skip pre-digest and ingest directly with Claude.

## Step 3 — Hand Off to Claude

Tell Claude:
> "Pre-digest ready at `.claude/pre-digest/<FILENAME>.digest.md`. Use this for the ingest — read the digest first, verify against source only if needed."

Claude reads the digest (~300-500 tokens) instead of the full source (~2000-5000 tokens).

## Step 4 — Cleanup

After ingest is complete:
```bash
rm .claude/pre-digest/<FILENAME>.digest.md
```

Or keep digests as a cache — useful if ingest is interrupted and resumed.

## Setup (first time only)

```bash
mkdir -p .claude/pre-digest
```

Add to `.gitignore`:
```
.claude/pre-digest/
```

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| `Error: model not found` | gemma4:e4b not pulled | `ollama pull gemma4:e4b` |
| Escape codes in output | TTY codes not stripped | `col -b` already handles this |
| Output cuts off mid-section | Context limit hit | Source too long — split into chunks first |
| Thinking block not stripped | No `...done thinking.` line | Remove the `sed` filter |
| Ollama not running | Server not started | `ollama serve` in a separate terminal |
