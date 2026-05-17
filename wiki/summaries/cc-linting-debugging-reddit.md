---
title: "CC Linting & Debugging — r/ClaudeCode Community"
type: summary
tags: [linting, hooks, pre-commit, shellcheck, biome, noslop, debugging, static-analysis, claude-code]
sources:
  - "ve been too afraid to ask, but... do we have linting and debugging in Claude Code? Be kind.md"
created: 2026-05-15
updated: 2026-05-15
---

# CC Linting & Debugging — r/ClaudeCode Community

Source: r/ClaudeCode thread, April 2026. OP asked about static analysis and debugger support in Claude Code. High-signal comment thread with practitioners sharing production setups.

---

## Core Problem

LLM coding agents lack the IDE hygiene layer developers relied on for 30 years: static analysis, unused variable detection, dead code warnings, and interactive debugging. OP's framing: "don't waste tokens on deterministic work."

---

## Community Consensus on Linting

### Hook placement — critical timing constraint

**`zbignew` (well-upvoted):** Linting that *edits* files after a CC Write/Edit will interrupt the next edit — CC's Edit tool only works if the file hasn't changed since last read. The safe window for file-modifying linters is the **Stop hook** (end of turn), not PostToolUse.

PostToolUse is safe for **read-only** linters (shellcheck, ESLint check-only) — they report without touching files.

### Layered setup (emerged from multiple comments)

| Layer | Tool | When |
|---|---|---|
| Always-on reporters | shellcheck, jq | PostToolUse on Write/Edit (read-only) |
| Auto-fixers | biome --write, ruff --fix | Stop hook (safe — no file-state conflict) |
| Hard gate | pre-commit hooks | On git commit — outside LLM entirely |

### noslop — opinionated quality gate repo

**`Numerous_Pickle_9678`** (github.com/45ck/noslop): installs quality gates as pre-commit hooks for 19 languages. Used across 110 repos. Standards enforced:

| Category | Threshold |
|---|---|
| Cyclomatic complexity | ≤ 10 |
| Cognitive complexity | ≤ 15 |
| Function length | ≤ 80 lines |
| File length | ≤ 350 lines |
| Parameter count | ≤ 4 |
| Nesting depth | ≤ 4 |
| Type safety | strictest mode |
| Unused code | error |

TypeScript pack uses ESLint + sonarjs + ts-eslint. Python uses ruff (C901, PLR0913, F401) + mypy strict.

**Key insight from same commenter**: block Claude from editing lint config files — otherwise it writes rule exceptions for every constraint it finds inconvenient. Hooks that prevent config edits are what make the system durable.

### LSP — frequently mentioned

Enable relevant LSPs in CC settings (TypeScript, Python, Go, etc.). Gives Claude type-aware feedback without routing through the LLM. CC has native LSP support via plugins.

### Token efficiency

Multiple comments converge: run linters as shell commands in hooks. Do NOT route linting through the LLM. Only surface the relevant error snippet back to Claude when intervention is needed.

---

## Community Consensus on Debugging

Less consensus than linting. Key points:

- **Print statements vs. debugger**: `carson63000` — "an AI agent may get better results adding print statements and rapidly rerunning. Brute force is more effective when not running at human speed." Contested.
- **gdb integration**: `Prudent_Sentence` — got CC to use gdb machine interface to attach to processes and set breakpoints. "Just tell Claude to use the gdb machine interface."
- **Replay MCP** (replayio): browser debugging MCP server — Claude Code + Replay MCP for web app runtime debugging. Step-through, breakpoints, stack inspection via MCP tools.
- **JetBrains Debugger MCP**: `ghostmastergeneral` — JetBrains plugin (plugin ID 29233) provides debugger MCP server for IDE-level step debugging.

Debugger support is not a standard pattern yet — it requires explicit setup and works best in specific environments.

---

## Relation to Existing Wiki

- [[concepts/agentic-cicd]] — linting gates fit into the agentic CI/CD pattern
- [[concepts/verification-pipeline]] — linting as the base tier below visual/screenshot gates
- [[concepts/llm-eval-pipeline]] — linting is a code-assertion evaluator (deterministic, zero LLM cost)
- [[concepts/tool-design-for-agents]] — hook output as agent recovery instructions; shellcheck errors as structured feedback
