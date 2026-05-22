# anthropic/claude-sonnet-4-6

`★ Insight ─────────────────────────────────────`
The core architectural distinction: a skill is **prompt expansion** (same context window, knowledge injection), while a subagent is **context isolation** (separate window, returns only a summary). Skills are cheaper (~1.5k tokens on invoke), subagents are heavier but keep main context clean. Think of skills as "load a specialist's mental model" and subagents as "delegate the task entirely."
`─────────────────────────────────────────────────`

---

## Skill vs Subagent

**Skill** — injects instructions into the *current* context window when triggered. No separate model call, no isolation. The caller's conversation gains domain expertise and follows a workflow. Think: a specialist arriving in the same room and whispering a checklist.

**Subagent** — runs in a *separate* context window with its own model, tools, and permission mode. Parent delegates; subagent works independently; only a summary returns. Main context stays clean. Think: delegating to another person who reports back.

### At a glance

| Dimension | Skill | Subagent |
|---|---|---|
| Context window | Caller's (no isolation) | Own window |
| Token cost to trigger | ~1,500 tokens (prompt injection) | Medium–high (full inference loop) |
| State / memory | None (session only) | None unless writes files or has `memory:` set |
| Parallel execution | No | Yes (`background: true`) |
| Tool restrictions | Via `allowed-tools:` in SKILL.md | Via `tools:` / `disallowedTools:` frontmatter |
| File isolation | No | Optional (`isolation: worktree`) |
| Best for | Reusable checklists, domain knowledge, workflow templates | Context-polluting tasks (test runs, log analysis), tool-restricted delegation |

### When to reach for each

**Skill** → domain knowledge fits in a prompt, reusable across sessions, no need to isolate side effects. Example: a TDD skill injects red-green-refactor discipline into the current session.

**Subagent** → task is self-contained, produces verbose output, benefits from tool restriction, or runs concurrently. Example: a `security-auditor` subagent audits auth code and returns a threat report — keeping all 200 lines of findings out of the main session.

### How they interact

Skills can be *preloaded into subagents* via `skills:` frontmatter — the subagent starts with that domain knowledge injected at turn 0. Subagents do NOT inherit the parent's currently-active skills automatically.

Per [[syntheses/agent-primitive-selection]]: if neither fits, the next step up is an **agent team** — multiple subagents with direct communication via shared task list and mailbox.
