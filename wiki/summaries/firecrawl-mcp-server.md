---
title: "Firecrawl MCP Server"
type: summary
tags: [mcp, web-scraping, firecrawl, ai-tools, data-extraction]
sources: ["Firecrawl MCP Server.md"]
created: 2026-04-29
updated: 2026-04-29
---

# Firecrawl MCP Server

Source: [github.com/firecrawl/firecrawl-mcp-server](https://github.com/firecrawl/firecrawl-mcp-server)

An MCP server exposing Firecrawl's web scraping and crawling capabilities as tools for AI agents. Turns Claude (and any MCP-compatible agent) into a capable web research and data extraction agent.

## What it is

Firecrawl converts web pages into clean, structured data (markdown, JSON) suitable for LLM consumption. The MCP server wraps the Firecrawl API into 14 callable tools covering: scraping, crawling, searching, structured extraction, autonomous browsing, and interactive page sessions.

## Setup (Claude Code)

```sh
# Remote hosted (recommended — no local process)
claude mcp add firecrawl --url https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/v2/mcp

# Or local via npx
claude mcp add firecrawl -e FIRECRAWL_API_KEY=<key> -- npx -y firecrawl-mcp
```

API keys: [firecrawl.dev/app/api-keys](https://www.firecrawl.dev/app/api-keys)

## Tool Inventory

### Core scraping
| Tool | Purpose |
|---|---|
| `firecrawl_scrape` | Single URL → clean markdown/JSON |
| `firecrawl_map` | Discover all indexed URLs on a site |
| `firecrawl_crawl` | Async multi-page crawl with depth control |
| `firecrawl_check_crawl_status` | Poll crawl job status |

### Search + extraction
| Tool | Purpose |
|---|---|
| `firecrawl_search` | Web search + optional page scraping of results |
| `firecrawl_extract` | LLM-powered structured extraction with JSON schema |

### Autonomous agent
| Tool | Purpose |
|---|---|
| `firecrawl_agent` | Autonomous web research agent — returns job ID, async |
| `firecrawl_agent_status` | Poll agent job; poll every 15–30s, timeout after 2–3 min |

### Browser sessions (CDP)
| Tool | Purpose |
|---|---|
| `firecrawl_browser_create` | Create persistent browser session via CDP |
| `firecrawl_browser_execute` | Execute bash/Python/JS in session |
| `firecrawl_browser_delete` | Destroy session |
| `firecrawl_browser_list` | List active/destroyed sessions |

### Interactive page sessions
| Tool | Purpose |
|---|---|
| `firecrawl_interact` | Scrape first, then click/fill/navigate on that page |
| `firecrawl_interact_stop` | Free interact session resources |

## When to use which tool

- **Single page, clean content** → `firecrawl_scrape`
- **Discover site structure** → `firecrawl_map`
- **Multi-page crawl** → `firecrawl_crawl`
- **Web search with full page content** → `firecrawl_search`
- **Structured data from known pages** → `firecrawl_extract` with schema
- **Complex multi-source research, don't know exact URLs** → `firecrawl_agent` (async)
- **JavaScript-heavy SPAs, interaction required** → `firecrawl_interact` or `firecrawl_browser_*`

## Configuration

Cloud API (default): requires `FIRECRAWL_API_KEY`.
Self-hosted: set `FIRECRAWL_API_URL` instead.

Optional tuning:
- Retry: `FIRECRAWL_RETRY_MAX_ATTEMPTS`, `FIRECRAWL_RETRY_INITIAL_DELAY`, `FIRECRAWL_RETRY_MAX_DELAY`, `FIRECRAWL_RETRY_BACKOFF_FACTOR`
- Credit alerts: `FIRECRAWL_CREDIT_WARNING_THRESHOLD`, `FIRECRAWL_CREDIT_CRITICAL_THRESHOLD`

Default retry: 3 attempts, exponential backoff (1s → 2s → 4s).

## Relation to Existing Wiki
- Complements [[entities/pydoll]] — Firecrawl is managed/cloud, Pydoll is OSS/CDP-native with fingerprint evasion
- `firecrawl_agent` is an agentic loop pattern; see [[concepts/agent-harness]]
- The async job+poll pattern (`firecrawl_agent` / `firecrawl_crawl`) is a standard async tool design; see [[concepts/tool-design-for-agents]]
- Relevant to [[summaries/amazon-scraping-2026]] — Firecrawl is the "managed API" option in that comparison
