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

## Ponytail Decision Matrix

Ponytail is a prompt-layer behavior constraint, not a model or plugin requirement. Default setup uses prompt-only rules in `code-writer`, `code-reviewer`, and `plan-writer`; do not install the Ponytail plugin unless a project needs commands or runtime mode switching.

| Project state | Use Ponytail? | Agent setup | Why |
|---|---|---|---|
| Current active app with recurring overbuild in diffs | Yes, default `full` behavior | `plan-writer` adds `Do not build`; `code-writer` runs the ladder; `code-reviewer` reports Ponytail findings | Highest ROI: reduces new files, wrappers, dependencies, and speculative abstractions |
| Current app with stable conventions and small diffs | Review-only or light implementation rule | Keep `code-reviewer` Ponytail findings; let `code-writer` use ladder only for small/CRUD/UI tasks | Avoids adding friction where repo already resists overbuild |
| Planned feature in existing product | Yes, before implementation | `plan-writer` must write explicit top-level and per-task `Do not build` lines | Prevents vague scope from becoming architecture work |
| New greenfield project | Yes, but conservative | Use Ponytail for MVP scope, but keep architecture-reviewer for boundaries and data model | Helps avoid framework shopping and premature layers while structure is still fluid |
| Prototype/spike | Yes, strong | `code-writer` should prefer stdlib/native/existing dependency and one-file edits | Prototype value comes from learning quickly, not durable abstractions |
| Refactor/cleanup | Yes, strong | `code-writer` minimizes changed surface; `code-reviewer` asks what can be deleted | Ponytail aligns with deletion-first refactoring |
| Security/auth/payment/data-loss/migration work | Limited | Keep Ponytail only as final overbuild check; do not use it to cut validation, audit, rollback, or compatibility paths | Correctness and safety dominate LOC reduction |
| Public API or compatibility-sensitive library | Limited | Require `architecture-reviewer`; Ponytail may only reject speculative additions outside compatibility contract | Minimal changes must not break external consumers |
| Infra/DevOps/platform automation | Case-by-case | Use Ponytail for scripts; avoid for rollout, rollback, observability, and policy gates | Some "extra" code is operational safety |
| Training/practice repo | Optional | Prefer `earn-it`/manual practice; Ponytail can be a review checklist | Too much prompt automation may hide learning signal |

### Trigger Heuristic

Before enabling Ponytail strongly, ask:

```text
Would a senior developer likely solve this by deleting scope, using stdlib/native behavior, or editing one existing file?
```

If yes, use Ponytail strongly. If no, keep normal architecture/review flow and use Ponytail only as a final "obvious overbuild?" check.

### Safety Boundary

Never put trust-boundary validation, security checks, data-loss handling, accessibility, tests, observability needed for operations, rollback paths, or required error handling in the deletion budget.
