---
title: "OpenAI Codex"
type: entity
tags: [ai-coding-agents, openai, cli, agent-harness, toml, skills]
sources: ["Custom instructions with AGENTS.md – Codex.md"]
urls:
  - "https://developers.openai.com/codex/subagents"
  - "https://developers.openai.com/codex/guides/agents-md"
  - "https://developers.openai.com/codex/skills"
created: 2026-05-06
updated: 2026-05-06
---

# OpenAI Codex

OpenAI's AI coding CLI. Pioneered the AGENTS.md format. Has a richer native extension model than the AGENTS.md standard alone: TOML custom agents, native skills concept, and layered instruction discovery.

---

## Instruction Layer (AGENTS.md)

Reads `AGENTS.md` as ambient layered instructions:
- Discovery: global `~/.codex/AGENTS.md` → project root → CWD walk
- Override: `AGENTS.override.md` takes precedence over `AGENTS.md`
- Limit: 32 KiB default instruction chain (`project_doc_max_bytes`)
- Profiles: `CODEX_HOME` env var for multiple setups

See [[summaries/codex-agents-md]] for full layering details.

---

## Custom Agents — TOML Format

**Note**: Codex agents use TOML, not YAML. This is the format reported in official docs as of 2026.

Location: `~/.codex/agents/` (global) or `.codex/agents/` (project-scoped).

```toml
# .codex/agents/code-reviewer.toml
name = "code-reviewer"
description = "Reviews implementation for correctness, security, and style"
developer_instructions = """
You are a code reviewer. Focus on:
- Correctness and edge cases
- Security vulnerabilities (OWASP Top 10)
Produce: [SEVERITY] Category — Location — Issue — Fix.
"""
model = "gpt-4.1"

[sandbox]
network = "none"
```

Schema:
- `name` — identifier; used for invocation and routing
- `description` — signal for when primary agent should delegate
- `developer_instructions` — multiline system prompt for this agent
- `model` — model override (can differ from primary session model)
- `[sandbox]` — network/filesystem restrictions for this agent

---

## Skills

Codex has a first-class skills concept. Metadata in `agents/openai.yaml`:

```yaml
skills:
  wiki-context:
    description: Search the personal LLM wiki for relevant patterns
    invocation: explicit          # must be invoked; not ambient
    tool_dependencies: [bash]
  security-audit:
    description: OWASP security review on specified scope
    invocation: auto              # Codex may auto-invoke when relevant
    tool_dependencies: [bash, read]
```

Skills are namespaced and invocable on demand — closer to CC's `Skill` tool mechanism than to ambient AGENTS.md rules.

---

## Three-Layer Stack

```
~/.codex/AGENTS.md          ← global ambient
.codex/AGENTS.md            ← project ambient
.codex/agents/*.toml        ← named spawnable agents
agents/openai.yaml          ← skill metadata
```

---

## Migration from Claude Code

| CC asset | Codex equivalent |
|---|---|
| `CLAUDE.md` + `@-imports` | `AGENTS.md` layered discovery |
| `agents/*.md` (YAML frontmatter) | `.codex/agents/*.toml` |
| `skills/*/SKILL.md` | `agents/openai.yaml` skill entries + prompt file |
| `settings.json` hooks | None |
| Plugins | None |

See [[comparisons/cc-to-cross-platform-migration]] for full matrix.

---

## Related Pages

- [[summaries/codex-agents-md]] — AGENTS.md layering and discovery
- [[summaries/codex-agents-skills]] — TOML agents and skills detail
- [[entities/agents-md-format]] — AGENTS.md cross-tool compatibility
- [[comparisons/cc-to-cross-platform-migration]] — full migration matrix
