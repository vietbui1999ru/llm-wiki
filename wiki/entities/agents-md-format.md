---
title: "AGENTS.md (format)"
type: entity
tags: [agent-context-instructions, cross-provider, standards, linux-foundation]
sources: ["AGENTS.md", "Custom instructions with AGENTS.md – Codex.md", "Rules.md"]
created: 2026-05-06
updated: 2026-05-22
---

# AGENTS.md (format)

An open, unschematized markdown format for providing cross-agent project instructions. Named after the file it lives in: `AGENTS.md` at the repo root.

Website: [agents.md](https://agents.md/)
Steward: [Agentic AI Foundation](https://aaif.io/) / Linux Foundation

---

## Origin

Emerged from multi-vendor collaboration: OpenAI Codex, Amp, Jules (Google), Cursor, Factory. OpenAI Codex first popularized the format; the Agentic AI Foundation now stewards it as a neutral open standard.

Adopted by 60k+ open-source projects as of 2026.

---

## Format Rules

- Plain markdown. No schema. No required fields.
- Any heading structure is valid.
- Closest file in directory tree wins (nested-AGENTS.md for monorepos).
- User chat prompts override file contents.

---

## Implementations by Tool

Each tool implements its own discovery and layering on top of the format:

| Tool | Discovery details |
|---|---|
| **Codex** | `~/.codex/` global + project root→CWD walk; `AGENTS.override.md` override; 32 KiB limit. Also has TOML custom agents (`.codex/agents/*.toml`), repo-local hooks in `.codex/config.toml`, and native skills (`skills/*/SKILL.md`, optional `skills/*/agents/openai.yaml`) as separate layers beyond AGENTS.md. |
| **OpenCode** | `AGENTS.md > CLAUDE.md` per directory; `~/.config/opencode/AGENTS.md` global; `rules:` array in `opencode.json` for multi-file without duplicating into AGENTS.md |
| **Claude Code** | Does not read AGENTS.md; uses CLAUDE.md with @-import for multi-file composition |
| **Aider** | Requires `read: AGENTS.md` in `.aider.conf.yml` |
| **Gemini CLI** | `GEMINI.md` (not AGENTS.md); supports global `~/.gemini/GEMINI.md`, workspace discovery, JIT per-subdirectory, and `@file.md` imports for modular composition |
| **Cursor** | `.cursor/rules/*.md` (not AGENTS.md); created via Cursor UI; ambient only (no on-demand invocation) |

---

## Multi-file Strategies

The base format is single-file. Tools extend it differently:

- **Codex**: `AGENTS.override.md` layering + `project_doc_fallback_filenames` for alternate names
- **OpenCode**: `instructions` field in `opencode.json` — glob patterns, multiple files, remote URLs
- **Claude Code**: CLAUDE.md with `@path/to/file.md` imports
- **Manual**: Teach agent to lazy-load referenced files via `@docs/file.md` references in instructions

---

## Related Pages

- [[summaries/agents-md-spec]] — detailed spec and compatibility table
- [[summaries/codex-agents-md]] — Codex layering mechanisms
- [[summaries/agents-md-critique]] — why single-file is the wrong abstraction
- [[concepts/rules-vs-hooks]] — static rules vs. dynamic hooks
- [[concepts/agent-context-instructions]] — the concept this format implements
