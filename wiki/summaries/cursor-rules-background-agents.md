---
title: "Cursor — Rules and Background Agents"
type: summary
tags: [cursor, rules, background-agents, cross-platform]
sources: []
urls:
  - "https://dev.to/anshul_02/mastering-cursor-rules-your-complete-guide-to-ai-powered-coding-excellence-2j5h"
  - "https://forum.cursor.com/t/cursor-rules-in-background-agents/105598"
  - "https://stevekinney.com/courses/ai-development/cursor-background-agents"
created: 2026-05-06
updated: 2026-05-06
---

# Cursor — Rules and Background Agents

Cursor's instruction and automation systems. Weakest cross-platform parity of the four: rules work, background agents exist, but no native skill or subagent dispatch equivalent. Community evidence is stronger than official docs for background agent behavior.

---

## Rules — `.cursor/rules`

Project rules live in `.cursor/rules/` as individual Markdown files. Created via Cursor's rules UI or command flow (not by directly writing files, though files can be written manually).

```
.cursor/rules/
├── core.md           # General coding behavior
├── communication.md  # Output style
├── editing.md        # Diff policy, minimal edits
└── security.md       # Security review checklist
```

Each file is a Markdown instruction doc. Cursor loads them as ambient context — equivalent to CC's CLAUDE.md `@-imports` or OpenCode's `rules` array.

**No explicit invocation**: rules are always-on ambient context, not invokable on demand. This means all skill content must be inlined as rules sections rather than lazy-loaded.

**Migration**:
- CC `claude-setup/rules/*.md` → `.cursor/rules/*.md` — direct file content reuse
- CC `claude-setup/skills/*/SKILL.md` → `.cursor/rules/skill-name.md` as always-on section — no on-demand invocation
- CC `templates/AGENTS.md` content → `.cursor/rules/workflow.md`

---

## Background Agents

Cursor has remote background agents that run tasks autonomously (AFK-loop equivalent). Key properties per community forum evidence:
- Run on Cursor's remote infrastructure (not local)
- Initially did **not** support rules; rules support in background agents was added later
- As of the forum post, `.cursor/rules` files now work inside background agent sessions

This makes background agents viable for the autonomous loop pattern, but with caveats:
- **Remote execution**: agent runs on Cursor's servers, not your machine — credential injection model differs from local CC setup
- **Network access**: Cursor controls the sandbox; you don't configure it via settings.json equivalents
- **No TOML/YAML agent definitions**: no formal agent spec file like Codex TOML or CC agent YAML

**Gap**: No mechanism equivalent to CC's per-agent `model`, `disallowedTools`, or `isolation: worktree`. Background agents are a single-tier execution model.

---

## What Doesn't Translate to Cursor

| CC asset | Cursor status |
|---|---|
| `agents/*.md` subagent definitions | No equivalent — no subagent dispatch system |
| `skills/*.md` on-demand invocation | No equivalent — must be inlined as always-on rules |
| `settings.json` hooks | No equivalent |
| Plugins (superpowers, qmd, etc.) | No equivalent — Cursor extension marketplace is different |
| `permissions.allow/deny` | Cursor controls sandbox on remote agents; not user-configurable |
| council.py | Works if Cursor can run shell commands — invoke manually |

---

## Search Backlog (Lower Confidence)

These still need official sources:
- `Cursor official docs background agents` — forum/guide evidence used here; official docs may have changed
- `Cursor official docs .cursor/rules` — community guide used; official spec may differ

---

## Related Pages

- [[comparisons/cc-to-cross-platform-migration]] — full migration matrix
- [[concepts/agent-context-instructions]] — what rules implement
- [[concepts/agentic-sandbox-controls]] — how Cursor's remote sandbox differs from local CC sandbox
