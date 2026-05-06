---
title: "AGENTS.md Format Specification"
type: summary
tags: [agent-context-instructions, cross-provider, standards, linux-foundation]
sources: ["AGENTS.md"]
created: 2026-05-06
updated: 2026-05-06
---

# AGENTS.md Format Specification

The AGENTS.md website (agents.md) documents an open, markdown-based format for cross-agent project instructions. Adopted by 60k+ open-source projects. Stewarded by the [Agentic AI Foundation](https://aaif.io/) under the Linux Foundation. Originated from collaborative work across OpenAI Codex, Amp, Jules (Google), Cursor, and Factory.

---

## Core Concept

AGENTS.md is a README for agents: a dedicated, predictable file containing the extra context AI coding agents need — build steps, tests, conventions — that would clutter a human README.

Intentionally minimal: plain markdown, no required fields, no schema. The agent parses whatever text you provide.

---

## Nested File Precedence

For monorepos: place AGENTS.md in each package directory. The rule is **closest file wins** — agents read the nearest AGENTS.md in the directory tree. Explicit user prompts override everything.

The [openai/codex repo](https://github.com/openai/codex) maintains 88 AGENTS.md files at time of writing.

---

## What to Include

Popular sections from the spec:

- Project overview
- Build and test commands
- Code style guidelines
- Testing instructions
- Security considerations
- Commit message format, PR instructions

---

## Migration

```bash
# Rename existing AGENT.md and create backward-compatible symlink
mv AGENT.md AGENTS.md && ln -s AGENTS.md AGENT.md
```

---

## Tool-Specific Configuration

Some agents don't read AGENTS.md natively and need configuration:

**Aider** (`.aider.conf.yml`):
```yaml
read: AGENTS.md
```

**Gemini CLI** (`.gemini/settings.json`):
```json
{ "context": { "fileName": "AGENTS.md" } }
```

---

## Tool Compatibility Status (as of 2026-05)

| Tool | Native AGENTS.md support |
|---|---|
| OpenAI Codex | Yes — primary discovery mechanism |
| OpenCode | Yes — AGENTS.md > CLAUDE.md precedence |
| Amp | Yes |
| Jules (Google) | Yes |
| Cursor | No — uses .cursorrules |
| Claude Code | **No** — uses CLAUDE.md |
| Aider | Via config only |
| Gemini CLI | Via settings.json config |

Claude Code reads CLAUDE.md, not AGENTS.md. When working cross-provider, maintain both or symlink.

---

## Limitations Noted in Critique

See [[summaries/agents-md-critique]] for the counter-argument: single-file abstraction is not navigable at scale, nested-file conflict resolution relies on agent compliance (not enforced), and content guidance is too narrow (coding style only; misses business context, lifecycle, user personas).

---

## Related Pages

- [[entities/agents-md-format]] — entity page for the format itself
- [[summaries/codex-agents-md]] — Codex-specific layering: AGENTS.override.md, 32 KiB limit
- [[summaries/agents-md-critique]] — critique: wrong abstraction + inadequate content guidance
- [[concepts/agent-context-instructions]] — the broader concept this format implements
- [[concepts/rules-vs-hooks]] — static rules file vs. dynamic hooks as competing approaches
- [[entities/opencode]] — OpenCode AGENTS.md parsing + instructions field
