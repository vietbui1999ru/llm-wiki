---
title: "OpenAI Codex"
type: entity
status: stub
tags: [ai-coding-agents, openai, cli, agent-harness]
sources: ["Custom instructions with AGENTS.md – Codex.md"]
created: 2026-05-06
updated: 2026-05-06
---

# OpenAI Codex

OpenAI's AI coding CLI. Pioneered the AGENTS.md format; AGENTS.md was originally designed for Codex before being standardized under the Agentic AI Foundation.

Key mechanics:
- Discovers instructions via `AGENTS.md` + `AGENTS.override.md` layering from global (~/.codex/) down to CWD
- 32 KiB default instruction chain limit (`project_doc_max_bytes`)
- Supports `CODEX_HOME` env var for multiple profiles
- Configurable fallback filenames via `project_doc_fallback_filenames`

See [[summaries/codex-agents-md]] for full discovery/layering details.

*Stub — expand when a dedicated source is ingested.*
