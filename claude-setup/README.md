# Provider-Agnostic Agent Setup

This directory contains agent definitions shared between **Claude Code** and **OpenCode**.

## Directory structure

```
claude-setup/
├── agents/                    # Source of truth — Claude Code format
│   ├── agent-delegator.md
│   ├── architecture-reviewer.md
│   ├── backend-debug-tester.md
│   ├── cmd-executor.md
│   ├── code-reviewer.md
│   ├── code-writer.md
│   ├── code-writer-fast.md
│   ├── design-critic.md
│   ├── design-explorer.md
│   ├── docs-writer.md
│   ├── frontend-debug-tester.md
│   ├── infra-decision-maker.md
│   ├── production-platform-devops.md
│   ├── project-health-monitor.md
│   ├── security-auditor.md
│   ├── session-report-generator.md
│   └── visual-verifier.md
└── README.md                  # This file

.opencode/agents/              # OpenCode-compatible versions (generated from claude-setup/agents/)
~/.config/opencode/agents/     # Symlinks to .opencode/agents/ for global availability
```

## How it works

### Claude Code
Reads agents directly from `claude-setup/agents/*.md` with Claude Code frontmatter:
- `model: sonnet | opus | haiku`
- `disallowedTools`, `skills`, `isolation`, `memory`

### OpenCode
Reads agents from `.opencode/agents/*.md` (project-level) or `~/.config/opencode/agents/` (global) with OpenCode frontmatter:
- `model: "opencode-go/kimi-k2.7-code"` (full provider/model path)
- `permission:` with `edit: deny`, `bash: allow`, etc.
- `mode: subagent`, `color`, `temperature`

The prompt body is identical between both formats.

## Model mapping

| Claude Code tier | OpenCode model |
|---|---|
| `opus` | `opencode-go/deepseek-v4-pro` |
| `sonnet` | `opencode-go/kimi-k2.7-code` |
| `haiku` | `opencode-go/deepseek-v4-flash` |
| planning | `opencode-go/glm-5.2` |

OpenCode Go routing follows [[concepts/model-task-routing]]: DeepSeek V4 Pro for orchestration, review, architecture, and security judgment; Kimi K2.7 Code for creative exploration and standard implementation; DeepSeek V4 Flash for boilerplate and routine read-only work; GLM-5.2 for sequential plan file decomposition (community Mimo→GLM→Kimi→DS workflow pattern).

## Field mapping

| Claude Code | OpenCode |
|---|---|
| `disallowedTools: Edit, Write, NotebookEdit, MultiEdit` | `permission: edit: deny` |
| `disallowedTools: WebSearch` | `permission: websearch: deny` |
| `tools: Bash, Read, Glob, Grep` | `permission: bash: allow` + `edit: deny` |
| `skills: [security-patterns]` | Referenced in prompt body |
| `isolation: worktree` | Not supported (documented in prompt) |
| `memory: project` | Not supported (documented in prompt) |

## Updating agents

1. Edit the source file in `claude-setup/agents/<name>.md`
2. Update the corresponding `.opencode/agents/<name>.md` with the same prompt body but OpenCode frontmatter
3. Symlinks in `~/.config/opencode/agents/` update automatically

## OpenCode Go agent roles

### DeepSeek V4 Pro reasoning agents
- `agent-delegator` — routes all requests, decides delegation strategy
- `architecture-reviewer` — holistic system/code review
- `design-critic` — critique patterns, identify anti-patterns
- `infra-decision-maker` — agent team, testing strategy, devops decisions
- `code-reviewer` — review implementations (read-only)
- `security-auditor` — OWASP-depth security analysis (read-only)

### GLM-5.2 planning agent
- `plan-writer` — decompose settled design into ordered task file; sits between design-explorer and code-writer

### Kimi K2.7-code creative and implementation agents
- `design-explorer` — brainstorm, ideate, explore alternatives
- `code-writer` — implement features from clear requirements
- `backend-debug-tester` — find, fix, test backend bugs
- `frontend-debug-tester` — find, fix, test frontend bugs
- `visual-verifier` — Playwright DOM audit + screenshot gate (read-only)
- `production-platform-devops` — CI/CD, deployment, environment config
- `docs-writer` — write and maintain project documentation

### DeepSeek V4 Flash fast agents
- `cmd-executor` — shell commands with safety guardrails
- `code-writer-fast` — boilerplate and routine code generation
- `project-health-monitor` — detect changes, report health (read-only)
- `session-report-generator` — session summaries and git diffs (read-only)
