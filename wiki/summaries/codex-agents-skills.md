---
title: "Codex — Native Agents (TOML) and Skills"
type: summary
tags: [codex, openai, agents, skills, toml, cross-platform]
sources: []
urls:
  - "https://developers.openai.com/codex/subagents"
  - "https://developers.openai.com/codex/guides/agents-md"
  - "https://developers.openai.com/codex/skills"
created: 2026-05-06
updated: 2026-05-06
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

Codex has a native skills concept. Configuration references `agents/openai.yaml` for skill metadata:

```yaml
# agents/openai.yaml
skills:
  wiki-context:
    description: Search the personal LLM wiki for patterns and concepts
    invocation: explicit          # user must invoke; not ambient
    tool_dependencies: [bash]     # tools this skill may use
  security-audit:
    description: Run OWASP security review on specified scope
    invocation: auto              # Codex may auto-invoke when relevant
    tool_dependencies: [bash, read]
```

Skills differ from AGENTS.md instructions: they are namespaced, invocable on demand, and can declare tool dependencies. Closer to CC's `Skill` tool mechanism than to ambient rules.

**Migration**: CC `skills/*/SKILL.md` → Codex `agents/openai.yaml` skill entries + associated prompt file.

---

## Three-Layer Stack

Codex has three composable layers:

```
~/.codex/AGENTS.md          ← global ambient (user-level always-on)
.codex/AGENTS.md            ← project ambient
.codex/agents/*.toml        ← named agents (spawnable subagents)
agents/openai.yaml          ← skill metadata (invocable on demand)
```

Compared to CC's:
```
~/.claude/CLAUDE.md + @-imports   ← global ambient
project CLAUDE.md                 ← project ambient
claude-setup/agents/*.md          ← subagents (YAML frontmatter)
claude-setup/skills/*/SKILL.md    ← skills (Skill tool)
```

The layer-for-layer correspondence is close. The format differences are: TOML (Codex agents) vs YAML (CC), and `agents/openai.yaml` (Codex skills) vs `SKILL.md` (CC).

---

## Related Pages

- [[entities/codex]] — Codex entity page (now expanded from stub)
- [[summaries/codex-agents-md]] — AGENTS.md discovery and layering
- [[comparisons/cc-to-cross-platform-migration]] — full migration matrix
- [[concepts/agent-subagents]] — CC subagent model for comparison
- [[concepts/agent-skills]] — CC skills model for comparison
