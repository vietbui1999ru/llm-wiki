---
title: "Copilot Agent Customization Structure"
type: summary
tags: [copilot, ai-agents, customization, instructions, skills, mcp]
sources: ["Code-and-Sortsawesome-copilot-agents ✨ A curated list of awesome GitHub instructions, prompt, skills, MCPs and agent markdown files for enhancing your GitHub Copilot AI experience..md"]
created: 2026-05-26
updated: 2026-05-26
---

# Copilot Agent Customization Structure

Source: curated list of Copilot customization artifacts — instructions, prompts, agents, skills, MCPs. See [[entities/ai-coding-agents]] for the broader AI coding agent taxonomy.

## Five artifact types

| Type | File convention | Directory | Purpose |
|---|---|---|---|
| Instructions | `*.instructions.md` | `.github/instructions/` | Repo-specific context: coding standards, frameworks, workflows |
| Prompts | `*.prompt.md` | `.github/prompts/` | Reusable task/workflow prompts (e.g. PRD creation, task generation) |
| Custom agents | `*.agent.md` | `.github/agents/` | AI personas for specific dev roles (Architect, Debugger, Clean Code) |
| Skills | `SKILL.md` in named folder | anywhere | Portable capability packages; open standard (agentskills.io) |
| MCPs | config entry | `.vscode/mcp.json` or settings | Protocol servers extending agent to external tools/APIs |

Single global instruction: `.github/copilot-instructions.md` (flat file, applies workspace-wide).

## Custom agents vs agent skills

**Custom agents** — AI personas scoped to VS Code. Each has its own instructions, tools, and behavior. Built-in: Agent, Ask, Edit, Plan, AIAgentExpert. Custom: defined via `*.agent.md`. Support **handoffs** — pass context from one persona to another (e.g. Architect → Debugger → Clean Code pipeline).

**Agent skills** — portable, open-standard capability packages (`SKILL.md` in a versioned folder). Cross-compatible across Copilot, Claude Code, and other skill-aware agents. Agents discover and load skills on demand. Examples: Jira CLI skill, Playwright CLI skill, pdf/docx/xlsx manipulation skills. See [[entities/ai-coding-agents]] for cross-agent context.

Key distinction: agents = role/persona; skills = reusable domain capability.

## MCPs (Model Context Protocol)

Extend what an agent can do beyond plain chat. Standardized connection to external tools, APIs, and local capabilities. Useful MCPs for development:

- **Filesystem** — batch file read/write, search
- **GitHub** — repo/workflow management
- **Context7** — inject version-specific library docs into agent context
- **Playwright** — browser automation and testing
- **Sequential Thinking** — structured problem decomposition

Cloud MCPs: Azure MCP, AWS Documentation, gcloud, KubeStellar.

## Repo setup (how to use in repos)

```
.github/
  copilot-instructions.md          # global instruction (all Copilot interactions)
  instructions/
    python.instructions.md         # language/stack-specific
    terraform.instructions.md
  prompts/
    prd-creation.prompt.md         # reusable task prompts
    task-generation.prompt.md
  agents/
    architect.agent.md             # custom agent personas
    debugger.agent.md
skills/
  jira-cli/
    SKILL.md                       # portable skill (cross-agent compatible)
```

YAML front matter on each file: `applyTo`, `mode`, `description` fields control behavior.

## Custom instructions quality

Instructions are a force multiplier — better instructions → Copilot suggestions aligned to team patterns → fewer review debates. See [[summaries/ai-agent-technical-debt]] for cloud agent workflow and [[concepts/ai-code-review]] for how instructions improve PR review quality.

## Key connections

- Skills open standard: same `SKILL.md` convention as Claude Code skills — cross-compatible
- MCP standard: same protocol as Claude Code MCP servers
- Custom agents with handoffs: comparable to [[concepts/agent-harness]] supervisor/worker patterns
