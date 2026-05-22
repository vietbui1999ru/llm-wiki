# anthropic/claude-sonnet-4-6

Per [[concepts/agent-skills]], [[concepts/agent-subagents]], and [[syntheses/agent-primitive-selection]]:

---

## Skill vs Subagent

**Skill** — prompt template injected into the *current* conversation context.

- No separate context window — Claude reads it and acts from the enriched context
- No code execution — it expands into instructions, modifies tool permissions, optionally switches model
- Loaded lazily: ~100 tokens at startup (metadata only); full content (~1.5k tokens) only when triggered
- Stateless — ends when the turn ends
- Use for: reusable domain knowledge, checklists, guided workflows, step-by-step procedures

**Subagent** — a separate Claude instance with its *own context window*.

- Parent delegates a task; subagent works independently, returns a summary
- Configurable: own tool allowlist/denylist, model, permissions, MCP servers, git worktree isolation
- No context bleed — verbose output (test runs, log analysis) stays out of main conversation
- Stateless by default, but can write to files or use `memory:` for persistence
- Use for: context-polluting tasks, enforced tool restrictions, parallelism, isolated file edits

---

`★ Insight ─────────────────────────────────────`
**The key abstraction boundary:** a skill enriches the *same* agent; a subagent is a *different* agent. Skills are prompt engineering. Subagents are process isolation.

**Progressive disclosure matters for skills:** only metadata loads at startup (~100 tokens/skill). Full content only lands when triggered — this is how you can have 20+ skills without burning context.

**Subagents don't inherit skills.** If a subagent needs a skill's instructions, you must list it explicitly in the subagent's `skills:` frontmatter. Parent's loaded skills are invisible to it.
`─────────────────────────────────────────────────`

---

**Decision shortcut** from [[syntheses/agent-primitive-selection]]:

| | Skill | Subagent |
|---|---|---|
| Own context? | No | Yes |
| Parallel? | No | Yes (`background: true`) |
| Isolation? | No | Optional (`worktree`) |
| Token cost | Low | Medium |
| Best for | Domain knowledge, checklists | Delegated tasks, context protection |

Rule of thumb: reach for a skill first. Upgrade to a subagent only when context isolation or parallelism matters.
