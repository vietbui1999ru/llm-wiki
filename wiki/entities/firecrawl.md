---
title: "Firecrawl"
type: entity
tags: [web-scraping, mcp, data-extraction, ai-tools, crawling]
sources: ["Firecrawl MCP Server.md"]
created: 2026-04-29
updated: 2026-04-29
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

Firecrawl exposes an MCP server (`firecrawl-mcp`) with 14 tools. This makes its capabilities directly available to Claude Code and any MCP-compatible agent without custom code. See [[summaries/firecrawl-mcp-server]] for the full tool inventory.

Setup for Claude Code:
```sh
claude mcp add firecrawl --url https://mcp.firecrawl.dev/{API_KEY}/v2/mcp
```

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

## Links
- GitHub: [firecrawl/firecrawl-mcp-server](https://github.com/firecrawl/firecrawl-mcp-server)
- API keys: [firecrawl.dev/app/api-keys](https://www.firecrawl.dev/app/api-keys)
