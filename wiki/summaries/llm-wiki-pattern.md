---
title: "LLM Wiki Pattern"
type: summary
tags: [llm, knowledge-management, wiki, rag, obsidian]
sources: [llm-wiki.md]
created: 2026-04-21
updated: 2026-04-21
---

# LLM Wiki Pattern

Source: `raw/llm-wiki.md` — a pattern document for building LLM-maintained personal knowledge bases.

## Core idea

Most LLM+document setups are RAG: the LLM retrieves raw chunks at query time and re-derives answers from scratch on every question. Nothing accumulates.

The LLM wiki pattern is different. The LLM **builds and maintains a persistent wiki** between you and your raw sources. When a new source arrives, the LLM reads it, integrates the knowledge into existing pages, flags contradictions, and strengthens the synthesis. The wiki is a **compounding artifact** — it gets richer with every source and every question.

## Architecture (3 layers)

- **Raw sources** — immutable documents you curate. The LLM reads but never modifies.
- **The wiki** — LLM-generated markdown. Summaries, entity pages, concept pages, comparisons, syntheses. The LLM owns this layer entirely.
- **The schema** — a config document (CLAUDE.md, AGENTS.md) that tells the LLM how the wiki is structured and what workflows to follow. Co-evolved by you and the LLM over time.

## Operations

- **Ingest**: Drop a source, LLM reads it, writes summary, updates relevant pages, logs the operation. One source might touch 10–15 pages.
- **Query**: Ask a question, LLM searches the wiki, synthesizes with citations. Good answers get filed back as new pages — explorations compound too.
- **Lint**: Periodic health check — contradictions, stale claims, orphan pages, missing concepts, gaps to fill.

## Indexing and logging

- **index.md** — content catalog; LLM reads it first when answering queries to find relevant pages.
- **log.md** — append-only chronological record; parseable with unix tools via consistent `## [YYYY-MM-DD]` prefix.

## Tooling mentioned

- [[qmd]] — local hybrid BM25/vector search over markdown; CLI + MCP server
- Obsidian — browse wiki in real time while LLM edits; graph view shows structure
- Obsidian Web Clipper — converts web articles to markdown for raw/
- Marp — markdown slide decks from wiki content
- Dataview — Obsidian plugin for querying frontmatter

## Historical connection

Related to Vannevar Bush's **Memex** (1945): a personal, curated knowledge store with associative trails between documents. Bush's vision was closer to this than to what the web became. The part he couldn't solve — who does the maintenance — is what LLMs handle.

## Key framing

> "The human's job is to curate sources, direct the analysis, ask good questions, and think about what it all means. The LLM's job is everything else."
