---
title: "Codex — Native Agents (TOML) and Skills"
type: summary
tags: [codex, openai, agents, skills, toml, cross-platform]
sources: ["Custom instructions with AGENTS.md – Codex.md", "Harness engineering leveraging Codex in an agent-first world.md"]
urls:
  - "https://developers.openai.com/codex/subagents"
  - "https://developers.openai.com/codex/guides/agents-md"
  - "https://developers.openai.com/codex/skills"
created: 2026-05-06
updated: 2026-05-22
---

# Codex — Native Agents (TOML) and Skills

Codex has a richer native extension model than the audit initially credited: AGENTS.md for ambient instructions, TOML custom agents, and a first-class skills concept. Correction to prior audit: **Codex subagents use TOML, not YAML**.

---

## AGENTS.md (Instructions Layer)

Codex natively reads `AGENTS.md` as layered custom instructions. Discovery follows the same global→CWD walk as documented in [[summaries/codex-agents-md]]: global `~/.codex/AGENTS.md` → project root → CWD, with `AGENTS.override.md` override. 32 KiB chain limit.

This is the ambient instruction layer — equivalent to CC's `CLAUDE.md`.

---

## Custom Agents — TOML Format

**Correction**: Codex custom agents use **TOML files**, not YAML.

Location: `~/.codex/agents/` (global) or `.codex/agents/` (project-scoped).

```toml
# ~/.codex/agents/code-reviewer.toml
name = "code-reviewer"
description = "Reviews implementation for correctness, security, and style"
developer_instructions = """
You are a code reviewer. Focus on:
- Correctness and edge cases
- Security vulnerabilities (OWASP Top 10)
- Code clarity and maintainability
Produce a structured report: [SEVERITY] Category — Location — Issue — Fix.
"""
model = "gpt-4.1"

[sandbox]
network = "none"
```

Schema fields:
- `name` — agent identifier
- `description` — routing signal; how the primary agent decides when to delegate
- `developer_instructions` — the system prompt for this agent (multiline TOML string)
- `model` — model to use for this agent (can differ from primary)
- `[sandbox]` — sandbox config (network, filesystem restrictions)

**Migration**: CC `agents/*.md` → Codex `.codex/agents/*.toml`. Content from frontmatter (`description`, system prompt body) maps to TOML fields; `model` field maps directly; `disallowedTools` maps to `[sandbox]` restrictions.

---

## Skills — First-Class Concept

Codex has a native filesystem skill system. The skill body lives in `skills/<name>/SKILL.md`. Optional product metadata lives in `skills/<name>/agents/openai.yaml`.

```text
skills/
  wiki-context/
    SKILL.md
    agents/openai.yaml
```

Example metadata:

```yaml
interface:
  display_name: "Wiki Context"
  short_description: "Load llm-wiki context before technical work"
  default_prompt: "Use $wiki-context to load relevant llm-wiki context before proceeding."
```

Skills differ from AGENTS.md instructions: they are namespaced, invocable on demand, and can carry product metadata or MCP dependencies. Closer to CC's `Skill` tool mechanism than to ambient rules.

**Migration**: CC `skills/*/SKILL.md` → Codex `skills/*/SKILL.md`, with optional `skills/*/agents/openai.yaml`.

---

## Hooks

Codex also supports repo-local hooks in `.codex/config.toml`.

Minimal shape:

```toml
[hooks]
PostToolUse = [
  { matcher = "exec_command|apply_patch", hooks = [
    { type = "command", command = "echo post-tool hook" }
  ] }
]
```

---

## Three-Layer Stack

Codex has three composable layers:

```
~/.codex/AGENTS.md          ← global ambient (user-level always-on)
.codex/AGENTS.md            ← project ambient
.codex/config.toml          ← project-local config + hooks
.codex/agents/*.toml        ← named agents (spawnable subagents)
skills/*/SKILL.md           ← native skills
skills/*/agents/openai.yaml ← optional skill metadata
```

Compared to CC's:
```
~/.claude/CLAUDE.md + @-imports   ← global ambient
project CLAUDE.md                 ← project ambient
claude-setup/agents/*.md          ← subagents (YAML frontmatter)
claude-setup/skills/*/SKILL.md    ← skills (Skill tool)
```

The layer-for-layer correspondence is close. The main format differences are: TOML (Codex agents) vs YAML (CC), plus Codex native `skills/*/SKILL.md` with optional per-skill `openai.yaml` metadata.

---

## Related Pages

- [[entities/codex]] — Codex entity page (now expanded from stub)
- [[summaries/codex-agents-md]] — AGENTS.md discovery and layering
- [[comparisons/cc-to-cross-platform-migration]] — full migration matrix
- [[concepts/agent-subagents]] — CC subagent model for comparison
- [[concepts/agent-skills]] — CC skills model for comparison
