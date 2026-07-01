---
title: "ketch"
type: entity
tags: [cli, web-search, web-scraping, code-search, context7, ai-agents, go]
sources: ["1broseidonketch Fast, stateless CLI for web search and scrape. Built for AI agents..md"]
created: 2026-06-30
updated: 2026-06-30
---

# ketch

Stateless Go CLI (`github.com/1broseidon/ketch`) unifying three research surfaces — web search, OSS code search, and library docs — plus scraping/crawling, behind one binary with no daemon. Built to be called directly by AI agents.

## Commands

| Command | What it does |
|---|---|
| `search` | Web search via Brave, DuckDuckGo, SearXNG, or Exa; `--scrape` fetches full content per result |
| `code` | Code search across OSS via Grep (default), Sourcegraph, or GitHub Code Search |
| `docs` | Library/framework docs via Context7 (curated, version-aware snippets) |
| `scrape` | Fetch URL(s) → clean markdown, concurrent batch support |
| `crawl` | BFS or sitemap crawl, background execution + status tracking |
| `browser` | Manage headless Chrome for JS-rendered pages |
| `config` | Show effective config + available backends as JSON |
| `cache` | Show cache stats / clear cached pages |

`--json` is the only global flag (structured output on every command). `-b/--backend` is local to `search`, `code`, `docs`.

## Backend Abstraction

The core design: operator configures a backend once (`ketch config set backend searxng`), agent's system prompt just says "use ketch" — never names a provider or manages a key.

| Surface | Backends | Default | Setup |
|---|---|---|---|
| `search` | brave, ddg, searxng, exa | brave | Free API key (brave) / zero-config (ddg, exa) / self-hosted (searxng) |
| `code` | grepapp, sourcegraph, github | grepapp | Zero-config (grepapp, sourcegraph) / `gh auth login` or token (github) |
| `docs` | context7, local(planned) | context7 | Free key: `ketch config set context7_api_key <key>` |

`ketch config` returns the full discovery payload (active backends + token source) as JSON — an agent can inspect capabilities in one call instead of parsing help text.

**Code search default is `grepapp`** (Grep MCP, `mcp.grep.app`) over Sourcegraph/GitHub: zero config, no token, 1M+ public repos, literal/regex. Sourcegraph is the zero-config fallback with exact-line SSE streaming; GitHub Code Search requires auth (`gh auth token` chain: explicit config → `$GITHUB_TOKEN` → `$GH_TOKEN` → `gh auth token`) but has the tightest ranking (30 req/min cap, `repo` scope required).

## JS-Rendered Page Detection

`extract/detect.go` auto-detects JS-rendered pages (React SPAs, Salesforce Lightning, etc.) and transparently re-fetches via headless Chrome — `ketch scrape`/`ketch crawl` fall back to plain HTTP (fast path) for static pages. Covers classic SPAs plus modern hydration/streaming: Next.js App Router (`self.__next_f` RSC streaming), React 18 streaming hydration, Vue 3 (`data-v-app`), SvelteKit, Qwik, Astro islands, empty mount nodes.

**Override for the hard case**: pages whose server-rendered shell has enough visible text to *look* static, but whose real content streams in client-side — caught only when both a strong framework marker **and** a script payload that dwarfs the visible text are present together. Neither signal alone triggers the override. Extend coverage manually with `ketch config set spa_markers '["marker1","marker2"]'`.

## Relationship to Context7

`ketch docs` is a thin CLI wrapper around [[entities/context7]] — same resolve → fetch flow (auto-resolve library from query, or skip via `--library /org/repo`), same underlying doc index. ketch doesn't replace Context7; it's one of three surfaces unified under a single agent-facing binary, with `local` (FTS5 SQLite, offline/private docs) planned as a second docs backend.

## Comparison to Alternatives

| | ketch | [[entities/firecrawl]] | [[entities/context7]] (direct) | [[entities/qmd]] |
|---|---|---|---|---|
| Scope | search + code + docs + scrape/crawl, one binary | scrape/crawl/extract/search (web only) | library docs only | local markdown search only |
| Setup | Go binary, no daemon | Cloud API or self-hosted, MCP server | MCP server or `ctx7` CLI | Local index, CLI + MCP |
| Backend swap | Config-driven, agent-agnostic | Fixed to Firecrawl service | Fixed to Context7 | N/A (local only) |
| Code search | Yes (Grep/Sourcegraph/GitHub) | No | No | No |
| Crawl | BFS + sitemap, background jobs | Async multi-page crawl | N/A | N/A |

**Use ketch when**: an agent needs one CLI surface for web + code + docs research without per-provider integration work, and stateless/no-daemon matters.
**Use Firecrawl when**: need cloud-managed scraping with LLM-schema structured extraction or autonomous research agents — ketch has no equivalent to `firecrawl_extract`/`firecrawl_agent`.
**Use Context7 directly when**: only docs lookup is needed and the harness already has the MCP server wired in.

## Agent Integration Pattern

Documented CLAUDE.md/AGENTS.md snippet ships in the README: names the five core invocations (`search`, `search --scrape`, `scrape`, `crawl ... --background`, `code`, `docs`), notes JS-rendering is automatic, and tells the agent not to override the operator's configured backends without reason. Same delivery model as [[entities/context7]]'s per-platform integration table — operator configures once, agent invocation stays provider-agnostic.

## Cache

Crawled/scraped pages are cached (`cache_ttl` config, default 72h); re-running an identical crawl returns instantly from cache. `--no-cache` forces re-fetch.

## Links
- GitHub: [1broseidon/ketch](https://github.com/1broseidon/ketch)
- Install: `brew install 1broseidon/tap/ketch` or `go install github.com/1broseidon/ketch@latest`
