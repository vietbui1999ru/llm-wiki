# anthropic/claude-sonnet-4-6

Per [[concepts/agent-skills]], [[concepts/agent-subagents]], [[syntheses/agent-primitive-selection]]:

---

## Core distinction

**Skill** = prompt injection into your current context window. No new process, no isolation — just enriched instructions + modified tool permissions.

**Subagent** = a new Claude instance with its own context window. Delegates a task; returns only a summary.

---

## The table that matters

| Dimension | Skill | Subagent |
|---|---|---|
| Context window | Shared (injected into caller) | Own isolated window |
| Executes code? | No — prepares Claude to act | Yes — independent execution |
| Parallelism | No | Yes (`background: true`) |
| Persists state | No | Only if it writes files |
| Tool restrictions | Via `allowed-tools` frontmatter | Via `tools` / `disallowedTools` frontmatter |
| Context pollution | Yes — content stays in main window | No — only summary returned |
| Token cost at load | ~100 tokens (metadata only) | Medium |
| Token cost at invoke | ~1,500+ (full SKILL.md injected) | Full conversation in new window |

---

## How each works mechanically

**Skill invocation:**
1. Claude sees skill metadata at startup (name + description, ~100 tokens)
2. LLM reasoning decides to fire the skill
3. Full `SKILL.md` injected as hidden `isMeta` message
4. Claude continues from enriched context — same window, same conversation

**Subagent invocation:**
1. Parent delegates a task via `Agent` tool (or `@name` mention)
2. New Claude instance spins up with its own system prompt (the subagent's markdown body)
3. Works independently — can have different model, MCP servers, hooks, permissions
4. Returns one summary message back to parent

---

## Decision rule (from the synthesis page)

```
Domain knowledge that fits in a prompt, reusable across sessions?
  → SKILL

Self-contained task that would pollute main context with verbose output?
  → SUBAGENT

Task needs different tool permissions than your current session?
  → SUBAGENT

Workers need to talk to each other?
  → AGENT TEAM
```

---

Key gotcha: **subagents don't inherit parent skills**. If you want a subagent to have skill `X`, you must list it explicitly in the subagent's `skills:` frontmatter. The skill's full content gets injected at subagent startup.
