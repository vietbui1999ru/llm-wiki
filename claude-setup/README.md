# Provider-Agnostic Agent Setup

This directory contains agent definitions shared between **Claude Code** and **OpenCode**.

## Directory structure

```
claude-setup/
├── README.md                  # This file
├── SYSTEM-REDESIGN-PLAN.md
├── settings.json, keybindings.json
├── personal/                  # personal notes
├── plugins/                   # plugin config, installed plugins, marketplaces
├── rules/                     # always-loaded and domain rule files (core, applied-ai, learning, ...)
├── scripts/                   # install, post-commit and pre-push hooks, drift and cap checks, docs-site build
├── skills/                    # skill sources (wiki-context, capture-mistake, judge, pdf-ingest, ...)
└── templates/                 # agent-team-plan, hooks, plan, project-template, skill, subagent
```

**There is no agent roster in this repo.** `claude-setup/agents/` does not exist, and neither does `.opencode/agents/`. The user-level Claude Code subagents live in `~/dotfiles/claude/.claude/agents/` (`scout`, read-only recon, and `worker`, bounded edits; both Haiku 5.5). An earlier version of this README documented 17 agents (`agent-delegator`, `code-writer`, `code-reviewer`, `architecture-reviewer`, `security-auditor` and others); they were removed. Define a custom agent only when a repeated job justifies its own prompt and tool limits; see `wiki/concepts/model-tier-routing.md` and `wiki/concepts/subagent-cost-model.md`.

## How it works

### Claude Code
Subagents are Markdown files with frontmatter in `~/.claude/agents/` (user) or `.claude/agents/` (project); `templates/subagent.md` is the starting point and `wiki/concepts/agent-subagents.md` has the field reference.

### OpenCode
`scripts/sync-agents.py` is the generator: it emits `.opencode/agents/<name>.md` (OpenCode frontmatter, same prompt body) for every `claude-setup/agents/<name>.md` it finds. With no canonical files it emits nothing. Its remembered presets for agents that used to exist apply only if a canonical file with a matching name reappears. OpenCode frontmatter uses a full provider/model path (for example `opencode-go/kimi-k2.7-code`), a `permission:` block (`edit: deny`, `bash: allow`, ...), `mode: subagent`, `color` and `temperature`.

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

## Adding an agent

1. Add `claude-setup/agents/<name>.md` with Claude Code frontmatter (start from `templates/subagent.md`).
2. Run `scripts/sync-agents.py` (`--check` is a dry run that reports drift) to generate the OpenCode version.

## Ponytail Decision Matrix

Ponytail is a prompt-layer behavior constraint, not a model or plugin requirement. Apply it as prompt-only rules in the planning, implementation and review steps (no named agents are required); do not install the Ponytail plugin unless a project needs commands or runtime mode switching.

| Project state | Use Ponytail? | Agent setup | Why |
|---|---|---|---|
| Current active app with recurring overbuild in diffs | Yes, default `full` behavior | the planning step adds `Do not build`; the implementing agent runs the ladder; the review step reports Ponytail findings | Highest ROI: reduces new files, wrappers, dependencies, and speculative abstractions |
| Current app with stable conventions and small diffs | Review-only or light implementation rule | Keep the review step Ponytail findings; let the implementing agent use ladder only for small/CRUD/UI tasks | Avoids adding friction where repo already resists overbuild |
| Planned feature in existing product | Yes, before implementation | the planning step must write explicit top-level and per-task `Do not build` lines | Prevents vague scope from becoming architecture work |
| New greenfield project | Yes, but conservative | Use Ponytail for MVP scope, but keep an architecture review for boundaries and data model | Helps avoid framework shopping and premature layers while structure is still fluid |
| Prototype/spike | Yes, strong | the implementing agent should prefer stdlib/native/existing dependency and one-file edits | Prototype value comes from learning quickly, not durable abstractions |
| Refactor/cleanup | Yes, strong | the implementing agent minimizes changed surface; the review step asks what can be deleted | Ponytail aligns with deletion-first refactoring |
| Security/auth/payment/data-loss/migration work | Limited | Keep Ponytail only as final overbuild check; do not use it to cut validation, audit, rollback, or compatibility paths | Correctness and safety dominate LOC reduction |
| Public API or compatibility-sensitive library | Limited | Require an architecture review; Ponytail may only reject speculative additions outside compatibility contract | Minimal changes must not break external consumers |
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
