---
title: "OpenCode Commands, Rules, and Agents"
type: summary
tags: [opencode, commands, rules, agents, subagents, cross-platform]
sources: ["Agents-opencode.md", "Rules.md"]
urls:
  - "https://opencode.ai/docs/commands/"
  - "https://opencode.ai/docs/rules/"
  - "https://opencode.ai/docs/agents/"
created: 2026-05-06
updated: 2026-05-06
---

# OpenCode Commands, Rules, and Agents

OpenCode's three mechanisms for migrating CC skills, rules, and subagents. Stronger extension model than CC in some ways: commands can bind directly to agents, rules can be modular without @-import syntax.

---

## Commands — Skill Equivalent

Commands are `.opencode/commands/*.md` files (or global `~/.config/opencode/commands/`). Each file is a Markdown template that becomes a slash command.

```markdown
<!-- .opencode/commands/wiki-context.md -->
---
name: wiki-context
description: Search the personal LLM wiki for relevant patterns
---

Search the wiki for: {{query}}

Run: qmd query "{{query}}" --files --min-score 0.4
Read up to 3 returned pages. Apply and cite.
```

Features:
- **Arguments** — `{{argument_name}}` template slots; user fills on invocation
- **Shell injection** — `$(command)` runs shell commands and injects output into the prompt
- **File references** — `@path/to/file.md` injects file content into the command context
- **Agent binding** — commands can target a specific agent or subagent, forcing subtask execution

Invocation: `/wiki-context "agent harness"` in OpenCode chat.

**Migration**: CC skills (`SKILL.md`) → `.opencode/commands/*.md`. Content translates directly; format changes from YAML-frontmatter + prose to Markdown template with `{{args}}`.

---

## Rules — Ambient Context Equivalent

OpenCode can load reusable instruction files without putting everything in AGENTS.md:

```jsonc
// opencode.json
{
  "rules": [
    "~/.config/opencode/rules/core.md",
    "~/.config/opencode/rules/communication.md",
    ".opencode/rules/project.md"
  ]
}
```

Rules files are loaded into every session as ambient context — equivalent to CC's `@-imports` in CLAUDE.md. No invocation needed; always present.

**Migration**: CC `claude-setup/rules/*.md` → OpenCode `rules` array in `opencode.json`. Same files, different loading mechanism.

---

## Agents — Subagent Equivalent

OpenCode has native primary/subagent support:

```jsonc
// opencode.json or .opencode/agents/*.json
{
  "agents": {
    "code-reviewer": {
      "model": "anthropic/claude-opus-4-7",
      "description": "Reviews implementation for correctness, security, and patterns",
      "instructions": "~/.config/opencode/agents/code-reviewer.md",
      "task_permissions": ["read", "shell"],
      "type": "subagent"
    }
  }
}
```

Invocation: `@code-reviewer review this PR diff` in primary agent session.

**Agent types:**
- **Primary** (Build/Plan): main session agent; full permissions
- **Subagent** (General/Explore): spawned by primary; scoped permissions; own context window
- **Hidden**: background agents (compaction, title, summary) — not user-facing

**Task permissions**: `read`, `shell`, `write`, `network` — explicit allowlist per agent.

**Migration**: CC `agents/*.md` YAML frontmatter → OpenCode `agents/*.json` config + separate instructions `.md` file.

---

## Command → Agent Binding

Commands can force execution via a specific agent:

```markdown
---
name: security-audit
agent: security-auditor
---
Run a full OWASP security audit on: {{scope}}
```

This is stronger than CC's skill model — CC skills load content into the current session; OpenCode commands can route to a different model/agent entirely.

---

## Related Pages

- [[entities/opencode]] — OpenCode entity; full event surface
- [[entities/opencode-dcp]] — DCP plugin; shows full OpenCode plugin extension model
- [[comparisons/cc-to-cross-platform-migration]] — full migration matrix
- [[concepts/agent-skills]] — CC skills concept; what commands replace
- [[concepts/agent-subagents]] — CC subagent model; what OpenCode agents replace
