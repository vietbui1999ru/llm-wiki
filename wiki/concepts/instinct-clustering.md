---
title: "Instinct Clustering (Homunculus Pattern)"
type: concept
tags: [memory, behavioral-learning, agent-harness, context-management, opencode]
sources: ["Claude runaway... tried Kimi 2.6 and Deepseek v4 (5y fullstack dev).md"]
status: documented-not-adopted
created: 2026-05-04
updated: 2026-05-04
---

# Instinct Clustering (Homunculus Pattern)

Behavioral pattern mining from tool-call telemetry. Observes what the agent does across sessions, clusters high-frequency patterns into "instincts," and injects only high-confidence instincts at session start. Implemented in `fmflurry/settings-opencode`.

Unlike [[concepts/agentic-memory-tool]] (explicit memory calls) and [[concepts/agent-self-correction]] (query-on-deviation), instinct clustering is **implicit and continuous** — it learns from behavior, not from conversation.

---

## Three-Plugin Pipeline

```
instinct-observer.ts
  hooks: tool.execute.before + tool.execute.after
  → appends to ~/.claude/homunculus/projects/<id>/observations.jsonl
  → captures: tool name, args, result, context, timestamp

background daemon (instinct-clustering)
  → reads observations.jsonl periodically
  → clusters high-frequency behavioral patterns
  → assigns confidence scores
  → writes to instincts.json

instinct-injector.ts
  hooks: experimental.chat.system.transform
  → reads instincts.json at session start
  → filters by confidence threshold
  → injects top-N instincts into system prompt

instinct-digest.ts
  → shows diff of new/updated instincts per session
  → allows human review and manual triage
```

---

## What Instincts Look Like

Instincts are not conversation summaries — they are **behavioral regularities** extracted from tool use:

- "Agent consistently runs `npm test` after editing `src/` files"
- "Agent always reads `CONTEXT.md` before touching domain logic"
- "Agent uses `git worktree add` before any multi-file refactor"
- "Agent queries `qmd` when context exceeds 80K tokens"

These are patterns the agent itself discovered through repeated behavior, not things the user told it.

---

## Storage

- Observations: `~/.claude/homunculus/projects/<id>/observations.jsonl` (gitignored)
- Instincts: `~/.claude/homunculus/projects/<id>/instincts.json`
- Shared between OpenCode and Claude Code (same path)

Cross-harness sharing is a deliberate design: instincts learned in CC sessions are available in OpenCode sessions and vice versa.

---

## Auto-Learned Skill Problem

The homunculus system also auto-generates skills at session end (v1 pipeline: `continuous-learning-stop-hook.js` → `evaluate-session.js` → `skills/learned/`). Without triage, duplicate skills accumulate:

```
skills/learned/
  summary-routing-spec-error-resolution.md
  summary-routing-spec-error-resolution-2.md
  summary-routing-spec-error-resolution-3.md
```

Mitigation: `instinct-digest.ts` shows the diff; human triages periodically. When running multiple harnesses (CC + OpenCode), this compounds — each harness generates its own learned skills from the same sessions.

**If adopting this pattern**: schedule periodic triage. Do not let learned skills accumulate more than 1 week without review.

---

## Vs. Other Memory Patterns

| Pattern | Explicit? | What it stores | Injection timing |
|---|---|---|---|
| Instinct clustering | Implicit (behavioral) | Patterns from tool-call telemetry | Session start (filtered) |
| [[concepts/agentic-memory-tool]] | Explicit (agent writes) | Facts, decisions, patterns | On-demand query |
| [[entities/mnemory]] | Explicit (agent writes) | Cross-session facts, artifacts | On-demand query |
| [[concepts/agent-self-correction]] | Explicit (agent queries) | Wiki knowledge | On deviation |
| `.agents/` corpus | Manual + hook | Per-repo task state | Compaction hook |

Instinct clustering is the only **implicit** pattern — it requires no agent action to learn from behavior.

---

## Honcho

`toadi` in the r/opencodeCLI thread mentioned [Honcho](https://github.com/plastic-labs/honcho) as an alternative memory system: "It captures well. But my problem is that I can not make the models use the memories well." This is the adoption problem — memory systems that capture well but aren't queried are inert. Instinct injection at session start sidesteps this by pushing high-confidence patterns rather than waiting for the agent to pull.

---

## Related Pages

- [[concepts/agent-self-correction]] — complementary explicit deviation detection
- [[concepts/agentic-memory-tool]] — explicit cross-session memory (Anthropic)
- [[entities/mnemory]] — explicit cross-session memory (OSS)
- [[entities/opencode]] — plugin system that implements this pattern
- [[concepts/context-compression]] — what gets injected competes with task context
