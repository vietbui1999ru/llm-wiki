# Lean kit plan (draft)

Status: draft. Not approved. Branch `plan/lean-kit`. Date: 2026-11-26.

## 1. Goal

Publish an empty, domain-neutral knowledge base kit. The kit keeps the core behavior of this wiki and none of its content. A user can start a glossary, a study notebook, a legal reference, a product documentation base, or a business archive from the same kit.

## 2. Current state (verified on `main` at `3de2de5`)

- Content: 205 pages under `wiki/`, 48 files under `mistakes/`, 12 PDFs, a 46 KB `index.md` and a 143 KB `log.md`. All of it is personal content.
- Page format: frontmatter `title, type, tags, sources, created, updated`, optional `status`. Seven fixed types (concept, summary, entity, pattern, synthesis, comparison, implementation). Links use `[[dir/slug]]`.
- Machine index: none in the repo. qmd (external CLI) and LightRAG (`.lightrag/`, gitignored) hold the indexes.
- Retrieval: qmd (BM25 plus embeddings), LightRAG graph (`templates/wiki-index`), Ollama `nomic-embed-text` for embeddings. LightRAG needs an LLM to build its graph.
- Interfaces: `claude-setup/scripts/wiki` (deterministic CLI: status, lint, drift, reindex, queue). `wiki-mcp-ops` (FastMCP, same five tools). `templates/wiki-mcp` (wiki_query, wiki_status over LightRAG). `templates/wiki-chat` (terminal REPL).
- Evaluation: `tests/retrieval/golden/golden.json`, version 2, 113 queries with graded relevance, `must_hit`, and dev/test splits. Baselines exist for qmd and LightRAG.
- Web search: Firecrawl appears only as an MCP entry in `.codex/config.toml`. No script calls it.
- Scheduling: no cron or timer in the repo. CI runs markdownlint, aislop and a docs-site staleness check.
- User-specific coupling: hardcoded `~/repos/llm-wiki`, `~/dotfiles`, `~/secrets/.env`, the GitHub org name, the owner name, and `claude-setup/personal/`.

## 3. Tensions in the initial requirements

These conflicts need a decision before a spec. Each item gives the recommended resolution.

1. R2 against R6, R11 and R12. R2 says the LLM does not fetch, retrieve or search. R6 and R11 need a web search, and R12 lets the LLM reorganize the KB. Recommendation: retrieval and the web fallback are deterministic code paths. The code triggers the web fallback when the retrieval score is below a threshold. The LLM only reads the retrieved passages, writes the answer, and proposes edits. The LLM does not choose tools in the default `ask` path.
2. R3 assumes a local Firecrawl binary. Self-hosted Firecrawl is a Docker Compose stack (API on port 3002, Redis, a browser service). Its `/search` endpoint needs a SearXNG instance with JSON output enabled (`SEARXNG_ENDPOINT`). Recommendation: a `web` adapter interface. The default adapter is Firecrawl, self-hosted or cloud with an API key. A second adapter (plain SearXNG plus a simple HTML-to-markdown fetch) covers users without Docker.
3. R4 asks for markdown and JSON. Two hand-edited formats drift. Recommendation: markdown is the only source of truth. The indexer generates the JSON from the markdown. Nobody edits the JSON. CI fails when the JSON is stale.
4. R10 asks for "factual with high confidence". A golden set measures retrieval quality, not truth. Recommendation: two mechanisms. The retrieval golden set gates ranking changes. A separate truth layer uses required sources, a `reviewed` date, a review interval, a `confidence` field and a `status` field. A human sets `verified`. The LLM never sets it.
5. R13 asks for a graph and vectors. LightRAG builds its graph with an LLM, which costs tokens and makes the index depend on a model. Recommendation: build the graph from wikilinks, tags and frontmatter (deterministic, free). Use embeddings for the vector side. Keep LLM entity extraction as an optional R12 job that proposes new links as edits.
6. Domain neutrality against fixed page types. Recommendation: the page types live in a kit config file. The kit ships three presets (glossary, research notes, documentation base). Lint reads the types from the config.

## 4. Requirements, tightened

Each line gives the testable form. Items marked "assume" are open until the user confirms.

- R1 Atomicity. One concept or one claim set per note. Lint warns above a word limit (assume 600 words). Each claim that an answer can cite has an Obsidian block ID (`^id`). Search returns block-level hits with the note path and the block ID.
- R2 LLM role. Search, ranking, filtering and fetching are code. The LLM gets the top passages and writes a cited answer. A test asserts that `ask` makes zero LLM calls before retrieval ends.
- R3 Web search. Behind the `web` adapter (section 3, item 2). Configured with a local endpoint or an API key. Off by default.
- R4 Formats. Markdown with YAML frontmatter is the source. The indexer writes `.kb/notes.jsonl` (one record per note and per block), `.kb/links.json` (graph edges) and `.kb/index.sqlite` (full-text and vector tables). `.kb/` is gitignored except an optional committed `notes.jsonl` for tools that cannot run the indexer.
- R5 Obsidian. The vault root is the repo root. Links use `[[note]]`, `[[note#heading]]` and `[[note^block]]` with Obsidian resolution rules (shortest unique path). The kit ships a minimal `.obsidian/` config with templates enabled. Lint fails on unresolved links.
- R6 Provenance. Every answer has a label: `KB`, `WEB` or `KB+WEB`. Every KB claim cites a note and block. Every web claim cites a URL. When the KB has no hit above the threshold and web is off, the answer is "not in the knowledge base" and the tool suggests a capture. Web results never enter the KB directly. They land in `inbox/` as `status: draft`, `confidence: low`, with the URL and retrieval date.
- R7 Tools. One core library. The CLI and the MCP server are thin wrappers with the same tool names and JSON schemas. Every tool has a schema, an example and a stable exit code. `kb tools --json` prints the schemas so a harness can load them without guessing.
- R8 Scheduling. Jobs are declared in the kit config. One system entry (`kb run-due`, called by cron or a systemd timer every 15 minutes) runs the jobs that are due. Jobs: reindex, lint, stale scan, golden eval, inbox report, source link check.
- R9 Templates. One template per page type in `templates/`. The same file works with the Obsidian Templates plugin (`{{title}}`, `{{date}}`) and with `kb new <type> <title>`. Agents call `kb add` with JSON that the tool validates against the type schema.
- R10 Freshness and truth. Golden set v2 format is kept and made domain-neutral. Metrics: recall@k, nDCG@10, MRR, must_hit rate. CI fails on a drop past a tolerance against the committed baseline. A fact-check set (question, expected answer, expected note) catches content drift. The stale scan lists notes past `reviewed + review_interval`, notes with no sources, and notes whose sources return errors.
- R11 Chat. A terminal REPL over the same `ask` path, with the provenance label on each answer. Local model through an OpenAI-compatible endpoint (Ollama serves one) or a hosted API key.
- R12 Reorganize. LLM jobs propose split, merge, retag, relink and rename operations as a patch on a branch. The patch runs the golden eval before and after. A human accepts the patch. The LLM never commits to the main branch.
- R13 Hybrid retrieval. BM25 (SQLite FTS5) plus vector similarity, fused with reciprocal rank fusion, then one-hop graph expansion over wikilinks, then an optional reranker. Each stage is switchable so the golden eval can measure it.

## 5. Proposed shape

```
question
  -> retrieve (code): BM25 + vector -> RRF -> graph expand -> rerank
  -> score >= threshold ? answer from KB (LLM writes, cites ^blocks)  [KB]
  -> else web enabled  ? web adapter -> answer, cites URLs, draft to inbox/  [WEB]
  -> else              : "not in the knowledge base"
```

Note frontmatter (domain-neutral):

```yaml
id: 01JD...            # stable, survives renames
title: Photosynthesis
type: concept          # from kb config
aliases: []
tags: []
sources: [{ref: "https://...", retrieved: 2026-11-26}]
created: 2026-11-26
updated: 2026-11-26
reviewed: 2026-11-26
review_interval: 365d
confidence: medium     # low | medium | high
status: draft          # draft | verified | stale | superseded
superseded_by: null
```

Kit layout:

```
kb.toml          types, retrieval weights, thresholds, providers, jobs
notes/           user notes (empty at start, plus 3 example notes)
inbox/           captures and web drafts
templates/       one file per type
golden/          retrieval and fact-check sets (empty, with a sample)
.kb/             generated index (gitignored)
.obsidian/       minimal vault config
src/kb/          core library, CLI, MCP server, chat
tests/
```

## 6. What moves from this repo

- Keep and rewrite: the `wiki` CLI and `wiki-mcp-ops` (merge into one tool set), `templates/wiki-chat`, the retrieval eval harness and golden v2 format, the lint checks (orphans, broken links, frontmatter, index drift), the ingest, query and lint rules in `CLAUDE.md`, the index and log conventions, the PDF ingest skill (Docling), `quality.yml`.
- Replace: qmd and LightRAG with the SQLite hybrid index (section 4, R13). The hand-maintained `index.md` with a generated index.
- Drop: all `wiki/` content except three example notes, `log.md` history, `mistakes/`, `SPEC-HARNESS-MIGRATION.md`, `claude-setup/` except the items above, `.codex/`, `.opencode/`, `pi-headroom/`, `council.py`, `skills/`, `docs/experiments/`, `pdfs/`, `docs-site/` (regenerate later if a site is wanted), and every hardcoded path and name in section 2.

## 7. Phases

Each phase ends with its tests passing and the golden eval run.

0. Decisions: answer section 8. Then write the spec.
1. Schema, `kb init` with presets, templates, lint, Obsidian config.
2. Indexer and hybrid search, `notes.jsonl`, golden eval with a sample set.
3. `ask` with provenance, threshold, citations, the "not in KB" path.
4. Web adapter (Firecrawl, SearXNG) and the inbox flow.
5. MCP server with CLI parity and `kb tools --json`.
6. Jobs and `kb run-due`, stale scan, source link check.
7. Chat REPL.
8. Reorganize jobs as patches with eval gating.
9. Publish: license, README, three example vaults, release.

## 8. Grill questions

Recommended default in brackets. Questions 1 to 5 block the spec.

1. Repo: a new public repo with no history, or this repo stripped? [New repo. This repo's history holds personal content and secret paths. The personal wiki later runs on the kit.]
2. Language and install: Python with `uvx` install, or a Go single binary? [Python. The existing CLI, MCP server, chat and eval harness are Python. The MCP SDK and Docling are Python.]
3. Web search: accept the adapter design in section 3, item 2, with Firecrawl as the default adapter? [Yes.]
4. Index stack: replace qmd and LightRAG with SQLite FTS5 plus a vector table? [Yes. One file, no server. LightRAG needs an LLM to index.]
5. Answer threshold: when the KB has weak hits, does the kit answer from the KB with a warning, or go to the web? [Answer from the KB with a "low coverage" note, and offer the web search as a second step.]
6. Web drafts: may a web result ever become a KB note without a human edit? [No.]
7. Who may set `confidence: high` and `status: verified`? [Only a human, through `kb verify`.]
8. Atomicity limit: word cap per note, and are block IDs required on every paragraph or only on cited claims? [600 words; block IDs added by the indexer on first citation.]
9. Multi-user: is a business shared KB (several editors, access control) in v1? [No. Single user, git for sharing.]
10. Chat surface: terminal only, or also a small local web page? [Terminal only in v1.]
11. Non-markdown sources in v1: PDF, web pages, others (audio, video transcripts, email)? [PDF and web pages.]
12. Providers: is an OpenAI-compatible endpoint enough (Ollama, OpenRouter, most hosts), or is a native Anthropic adapter needed in v1? [Compatible endpoint plus a native Anthropic adapter.]
13. Scheduler: cron and systemd timers only, or also macOS launchd and Windows Task Scheduler? [cron and systemd in v1, launchd documented.]
14. License and name? [MIT or Apache-2.0; name to decide.]
15. Does the public kit ship agent instruction files (`AGENTS.md`, `CLAUDE.md`) that describe the ingest, query and lint rules? [Yes, one `AGENTS.md`, generated from one rules file.]

## 9. Out of scope for v1

Web UI, sync service, access control, hosted service, automatic truth verification.
