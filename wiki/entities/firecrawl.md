---
title: "Firecrawl"
type: entity
tags: [web-scraping, mcp, data-extraction, ai-tools, crawling]
sources: ["Firecrawl MCP Server.md"]
created: 2026-04-29
updated: 2026-05-27
---

# Firecrawl

Managed web scraping and crawling service purpose-built for LLM consumption. Converts arbitrary web pages into clean markdown or structured JSON. Available as a cloud API or self-hosted.

## What it does

Firecrawl handles the full stack of web data extraction:
- Clean HTML → markdown conversion (removes nav, ads, boilerplate)
- JavaScript-heavy SPA rendering
- Multi-page crawling with depth control
- Structured data extraction via LLM + JSON schema
- Autonomous web research (async agent mode)
- Interactive browser sessions via CDP

## MCP Integration

Firecrawl exposes an MCP server (`firecrawl-mcp`) with 14 tools, directly available to Claude Code and any MCP-compatible agent without custom code.

```sh
# Remote hosted (recommended)
claude mcp add firecrawl --url https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/v2/mcp

# Local via npx
claude mcp add firecrawl -e FIRECRAWL_API_KEY=<key> -- npx -y firecrawl-mcp
```

API keys: [firecrawl.dev/app/api-keys](https://www.firecrawl.dev/app/api-keys)

### Tool Inventory

| Tool | Purpose |
|---|---|
| `firecrawl_scrape` | Single URL → clean markdown/JSON |
| `firecrawl_map` | Discover all indexed URLs on a site |
| `firecrawl_crawl` | Async multi-page crawl with depth control |
| `firecrawl_check_crawl_status` | Poll crawl job status |
| `firecrawl_search` | Web search + optional page scraping of results |
| `firecrawl_extract` | LLM-powered structured extraction with JSON schema |
| `firecrawl_agent` | Autonomous web research agent — returns job ID, async |
| `firecrawl_agent_status` | Poll agent job (every 15–30s, timeout after 2–3 min) |
| `firecrawl_browser_create` | Create persistent browser session via CDP |
| `firecrawl_browser_execute` | Execute bash/Python/JS in session |
| `firecrawl_browser_delete` | Destroy session |
| `firecrawl_browser_list` | List active/destroyed sessions |
| `firecrawl_interact` | Scrape first, then click/fill/navigate on that page |
| `firecrawl_interact_stop` | Free interact session resources |

**When to use which:**
- Single page → `firecrawl_scrape`
- Discover site structure → `firecrawl_map`
- Multi-page crawl → `firecrawl_crawl`
- Web search with full page content → `firecrawl_search`
- Structured data from known pages → `firecrawl_extract` with schema
- Complex multi-source research, unknown URLs → `firecrawl_agent` (async)
- JavaScript-heavy SPAs → `firecrawl_interact` or `firecrawl_browser_*`

### Configuration

Cloud (default): `FIRECRAWL_API_KEY`. Self-hosted: `FIRECRAWL_API_URL` instead.

Retry env vars: `FIRECRAWL_RETRY_MAX_ATTEMPTS`, `FIRECRAWL_RETRY_INITIAL_DELAY`, `FIRECRAWL_RETRY_MAX_DELAY`, `FIRECRAWL_RETRY_BACKOFF_FACTOR`. Default: 3 attempts, exponential backoff (1s → 2s → 4s).

Credit alerts: `FIRECRAWL_CREDIT_WARNING_THRESHOLD`, `FIRECRAWL_CREDIT_CRITICAL_THRESHOLD`.

## Comparison to Alternatives

| | Firecrawl | [[entities/pydoll]] | Playwright MCP |
|---|---|---|---|
| Setup | Cloud/managed | OSS, self-run | Local npx |
| Fingerprint evasion | Limited | Strong (CDP-native) | None |
| Structured extraction | Yes (LLM schema) | No | No |
| Autonomous agent | Yes | No | No |
| Cost | API credits | Free | Free |

**Use Firecrawl when**: you need clean structured data, autonomous research, or don't want to manage browser infrastructure.
**Use Pydoll when**: fingerprint evasion matters (scraping anti-bot-protected sites).
**Use Playwright MCP when**: you need direct browser control for UI testing/interaction.

See also [[entities/ketch]] — stateless CLI covering scrape/crawl plus web/code/docs search in one binary; narrower per-surface than Firecrawl (no schema extraction or autonomous agent mode) but config-driven backend swap and no daemon/cloud dependency.

## Links
- GitHub: [firecrawl/firecrawl-mcp-server](https://github.com/firecrawl/firecrawl-mcp-server)
- API keys: [firecrawl.dev/app/api-keys](https://www.firecrawl.dev/app/api-keys)
