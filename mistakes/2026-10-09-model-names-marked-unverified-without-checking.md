---
date: 2026-10-09
type: bad-assumption
domain: model-names
severity: medium
---

# Marked a real model name and a real price change "unverified" using the model list in my own context

## What happened
While ingesting a blog post (PR #20) I wrote `Haiku 5.5` as `(reported, unverified in public catalogs)` and the Sonnet 5.5 cache-read price cut ($0.20 to $0.10 per million tokens) as `(claimed, unverified)`. I took the model list in my own session context (newest Haiku: 4.5) as the catalog and never opened the provider's release notes. I repeated "the newest Haiku I can confirm is 4.5" in the page, the log entry, the PR body and my reply.

## What the fix was
Another ingest of the same article (PR #21, merged first) had checked Anthropic's release notes and marked both as verified. I then fetched https://platform.claude.com/docs/en/release-notes/overview myself: `claude-haiku-5-5` has launched, and the Sonnet 5.5 cache-read price was lowered from $0.20 to $0.10 per million tokens. Both flags in my version were wrong; PR #20 is superseded and should be closed.

## Prevention rule
The "unverified" label is a claim that I looked and could not confirm, so it may only be written after checking the provider's current release notes or model page (a cheap firecrawl scrape). The model list in my own context can lag the docs and is not the catalog.

## Context
Wiki ingest of "How I use Claude Code subagents to make my Claude Pro limits last longer". The repo rule that applies is `global-prevention-rules.md`, "Citing model names". It was already there, but I applied it only in the direction of not adding unverified names, and skipped the check that the label itself requires. The figures I took from the article itself were cross-checked against its text; the error was confined to the two labels about external facts.
