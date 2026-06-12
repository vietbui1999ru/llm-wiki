---
title: "Rules vs. Hooks"
type: concept
tags: [agent-context-instructions, hooks, dynamic-context, agent-harness]
sources: ["AGENTS md gets it wrong in 2 ways.md", "Rules.md", "AGENTS.md"]
created: 2026-05-06
updated: 2026-05-06
---

# Rules vs. Hooks

Two competing architectural approaches for providing AI agents with project context and behavioral constraints.

---

## Rules (Static Injection)

Rules files are markdown documents injected into the agent's system prompt at session start. The agent reads them and is expected to comply. Examples: AGENTS.md, CLAUDE.md, .cursorrules, .clinerules.

**Strengths**:
- Zero setup — just a file in the repo
- Cross-provider portable (AGENTS.md works across Codex, OpenCode, Amp, etc.)
- Human-readable and maintainable
- Versioned alongside code

**Weaknesses**:
- Static — loaded once at start, can't respond to session-specific context (which files are being edited, current intent, recent git changes)
- Single file limit — one file per directory level; navigability collapses at scale
- Compliance is not enforced — agent is expected to follow rules about which rules to follow, which is circular and unreliable
- Content guidance defaults to shallow: build commands + style, missing domain/business context

---

## Hooks (Dynamic Context Injection)

Hooks are shell commands that execute on events (session start, file edit, tool call, etc.). They can inspect the environment, query external systems, and inject custom content into the agent's context.

Claude Code's hook system supports: PreToolUse, PostToolUse, Stop, Notification. OpenCode exposes a broader surface including `tool.execute.before`, `session.idle`, `experimental.session.compacting`, LSP events, etc.

**Strengths**:
- Dynamic — can load path-specific rules, git-change-aware context, issue tracker content, LLM-selected documentation
- Composable — multiple hooks can each contribute context independently
- Enforceable — hooks run regardless of agent behavior; no compliance assumption needed
- Can call another LLM to decide what context to inject based on first user message

**Weaknesses**:
- Setup cost — requires writing code (shell script, JS/TS plugin)
- Not portable across tools (Claude Code hooks ≠ OpenCode plugin events ≠ Cursor)
- Execution timing matters — hooks that run at session start vs. mid-session have different guarantees

---

## Hybrid Patterns

Most real setups are hybrid: a rules file that instructs the agent to invoke a hook or load additional files.

**repomix compile (Memory Bank)**:
```
# In AGENTS.md / CLAUDE.md:
# Your first response must be:
# npx repomix --quiet --include _memory/ --ignore _memory/knowledgeBase --style markdown --stdout
```
The rules file bootstraps a compile step that loads a structured memory hierarchy. See [[concepts/memory-bank-pattern]].

**OpenCode `instructions` field**:
```json
{ "instructions": ["CONTRIBUTING.md", "docs/guidelines.md", ".cursor/rules/*.md"] }
```
Not a hook — static multi-file injection — but escapes the single-file limitation.

**@-imports (Claude Code)**:
CLAUDE.md references other files via `@path/to/file.md`. Static but navigable.

**Path-to-rules map (Wand's system)**:
```
{"/frontend/users": "users.md", "/backend/users": "users.md"}
```
A hook inspects the file being edited and injects the relevant rules file.

---

## The Compliance Problem

Both rules and hooks that instruct the agent to invoke commands (e.g., "run tests before finishing") face the same fundamental problem: the agent is asked to self-enforce its own constraints. This works better with hooks (the system runs the command) than with rules (the agent decides whether to run it).

From the AGENTS.md critique (Wand, 2026-05-06):
> "No agent will reliably follow any such instructions — even assuming there is no ambiguity — nor is such behavior enforceable by the orchestrator managing the agent."

---

## Choosing Between Them

| Situation | Preferred approach |
|---|---|
| Small project, single team, cross-provider | Rules (AGENTS.md) |
| Large monorepo with many concerns | Multi-file rules + @imports |
| Need context that varies per file/task | Hooks or Memory Bank |
| Enforcement required (not just guidance) | Hooks (PreToolUse gate) |
| Long-horizon multi-session projects | Memory Bank pattern |
| Cross-session memory without hooks | Memory Bank pattern |

---

## Related Pages

- [[entities/agents-md-format]] — the rules approach (AGENTS.md format)
- [[concepts/agent-context-instructions]] — what both approaches implement
- [[concepts/memory-bank-pattern]] — hybrid approach that escapes single-file limits
- [[concepts/agent-self-correction]] — hooks as enforcement mechanism
- [[entities/opencode]] — compaction hook and plugin event surface
- [[concepts/slash-commands]] — session-command decision guide; the third config surface alongside rules and hooks
