---
date: 2026-06-20
type: tool-misuse
domain: pre-digest
severity: low
---

# Pre-Digest Timeout Produced Empty File

## What happened
Ran the pre-digest Ollama command with a 120s timeout on a raw source, the command timed out, and the redirected digest file was empty.

## What the fix was
Treat the pre-digest as failed, verify the empty output, and ingest directly from the small raw source instead.

## Prevention rule
After any pre-digest command, verify the digest is non-empty before relying on it; if it times out or is empty, skip pre-digest and ingest directly for small sources.

## Context
Ingesting the Ponytail repository README from `raw/`. The source was only about 220 lines, so direct ingest was cheaper than retrying local model preprocessing.
