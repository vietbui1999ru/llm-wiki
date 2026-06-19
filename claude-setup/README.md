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
- `model: "github-copilot/claude-sonnet-4.5"` (full provider/model path)
- `permission:` with `edit: deny`, `bash: allow`, etc.
- `mode: subagent`, `color`, `temperature`

The prompt body is identical between both formats.

## Model mapping

| Claude Code tier | OpenCode model |
|---|---|
| `opus` | `github-copilot/claude-opus-4.5` |
| `sonnet` | `github-copilot/claude-sonnet-4.5` or `github-copilot/gpt-5.2-codex` |
| `haiku` | `github-copilot/gpt-5.4-mini` |

Implementation agents (code-writer, backend-debug-tester) use `gpt-5.2-codex` for cost efficiency. Review and design agents use Claude Opus/Sonnet for judgment quality.

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

## Agent tiers

### Opus tier (judgment, design, exploration)
- `agent-delegator` — routes all requests, decides delegation strategy
- `design-explorer` — brainstorm, ideate, explore alternatives
- `architecture-reviewer` — holistic system/code review
- `design-critic` — critique patterns, identify anti-patterns
- `infra-decision-maker` — agent team, testing strategy, devops decisions
- `security-auditor` — OWASP-depth security analysis (read-only)

### Sonnet tier (implementation, review, debugging)
- `code-writer` — implement features from clear requirements
- `code-reviewer` — review implementations (read-only)
- `backend-debug-tester` — find, fix, test backend bugs
- `frontend-debug-tester` — find, fix, test frontend bugs
- `visual-verifier` — Playwright DOM audit + screenshot gate (read-only)
- `production-platform-devops` — CI/CD, deployment, environment config
- `docs-writer` — write and maintain project documentation
- `project-health-monitor` — detect changes, report health (read-only)

### Haiku tier (fast execution, reporting)
- `cmd-executor` — shell commands with safety guardrails
- `code-writer-fast` — boilerplate and routine code generation
- `session-report-generator` — session summaries and git diffs (read-only)
