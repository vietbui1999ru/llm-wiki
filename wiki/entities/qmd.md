---
title: "qmd"
type: entity
status: stub
tags: [tooling, search, markdown, cli, mcp]
sources: [llm-wiki.md]
created: 2026-04-21
updated: 2026-04-21
---

# qmd

A local search engine for markdown files. Used in this wiki for query operations.

## What it does

Hybrid search: BM25 keyword + vector semantic search + LLM re-ranking, all on-device. Available as both a CLI (for shell invocations) and an MCP server (for native tool use in Claude Code).

## Role in this wiki

Configured as an MCP server. Used by Claude to search wiki pages when answering queries. At small scale the index file is sufficient; qmd becomes more valuable as the wiki grows past ~100 pages.

---
*Stub — expand when a dedicated source is ingested.*
