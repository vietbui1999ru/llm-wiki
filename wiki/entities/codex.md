---
title: "OpenAI Codex"
type: entity
tags: [ai-coding-agents, openai, cli, agent-harness, toml, skills]
sources: ["Custom instructions with AGENTS.md – Codex.md", "Harness engineering leveraging Codex in an agent-first world.md"]
urls:
  - "https://developers.openai.com/codex/subagents"
  - "https://developers.openai.com/codex/guides/agents-md"
  - "https://developers.openai.com/codex/skills"
created: 2026-05-06
updated: 2026-05-27
---

# OpenAI Codex

OpenAI's AI coding CLI. Pioneered the AGENTS.md format. Has a richer native extension model than the AGENTS.md standard alone: TOML custom agents, native skills concept, and layered instruction discovery.

---

## Instruction Layer (AGENTS.md)

Reads `AGENTS.md` as ambient layered instructions:
- Discovery: global `~/.codex/AGENTS.md` → project root → CWD walk
- Override: `AGENTS.override.md` takes precedence over `AGENTS.md` at the same directory level (useful for temporary local overrides; `rm AGENTS.override.md` to restore default)
- Limit: 32 KiB default instruction chain (`project_doc_max_bytes`)
- Merge order: root→CWD concatenated, joined by blank lines; **later (closer to CWD) wins**
- Profiles: `CODEX_HOME` env var for multiple setups (e.g., `CODEX_HOME=$(pwd)/.codex codex exec "..."`)

Raise the 32 KiB limit or add fallback filenames in `~/.codex/config.toml`:

```toml
project_doc_max_bytes = 65536
project_doc_fallback_filenames = ["TEAM_GUIDE.md", ".agents.md"]
```

**Verification:**
```bash
# See what instructions Codex loaded
codex --ask-for-approval never "Summarize the current instructions."
```

**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| Nothing loads | Empty file / wrong workspace root | Verify `codex status` |
| Wrong guidance | AGENTS.override.md higher in tree | Find and remove override |
| Fallback name ignored | Not in `project_doc_fallback_filenames` | Add to config, restart |
| Instructions truncated | Hit 32 KiB limit | Raise `project_doc_max_bytes` or split files |

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

Codex has a first-class skills concept. The native entrypoint is `skills/<name>/SKILL.md`, with optional product metadata in `skills/<name>/agents/openai.yaml`.

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

Skills are invocable on demand and can also be injected implicitly when allowed by policy. This is closer to CC's `Skill` tool mechanism than to ambient AGENTS.md rules.

---

## Hooks

Codex supports repo-local hooks in `config.toml`, including events such as `PostToolUse`.

Minimal pattern:

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

```
~/.codex/AGENTS.md          ← global ambient
.codex/AGENTS.md            ← project ambient
.codex/config.toml          ← project-local hooks and config
.codex/agents/*.toml        ← named spawnable agents
skills/*/SKILL.md           ← native skills
skills/*/agents/openai.yaml ← optional skill UI metadata
```

---

## Migration from Claude Code

| CC asset | Codex equivalent |
|---|---|
| `CLAUDE.md` + `@-imports` | `AGENTS.md` layered discovery |
| `agents/*.md` (YAML frontmatter) | `.codex/agents/*.toml` |
| `skills/*/SKILL.md` | `skills/*/SKILL.md` + optional `skills/*/agents/openai.yaml` |
| `settings.json` hooks | `.codex/config.toml` hooks |
| Plugins | None |

See [[comparisons/cc-to-cross-platform-migration]] for full matrix.

---

## Related Pages

- [[entities/agents-md-format]] — AGENTS.md cross-tool compatibility
- [[comparisons/cc-to-cross-platform-migration]] — full migration matrix
- [[concepts/agent-subagents]] — CC subagent model for comparison
- [[concepts/agent-skills]] — CC skills model for comparison
