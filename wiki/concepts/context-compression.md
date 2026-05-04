---
title: "Context Compression Strategies"
type: concept
tags: [agent-engineering, context-management, compaction, harness, long-horizon]
sources: []
created: 2026-04-25
updated: 2026-04-25
---

# Context Compression Strategies

When agent sessions grow long, compression is mandatory. The wrong optimization target is *tokens per request* (minimize context size). The correct target is **tokens per task** — total tokens to complete a task, including re-fetch costs when compression loses critical information.

## Three Strategies

### 1. Anchored Iterative Summarization (recommended)
Maintain a structured persistent summary with named sections: session intent, files modified, decisions made, next steps. When compaction triggers, summarize only the newly-truncated span and **merge** it into the existing summary — don't regenerate.

**Why it works**: Structure forces preservation — each section is a dedicated slot that must be filled. Incremental merging prevents compounding loss across multiple compression cycles.

**When to use**: Long-running coding sessions, multi-step tasks, anything where the agent needs to track file modifications and decisions across context windows.

```
[SUMMARY]
Intent: Implement auth middleware for the API
Files modified: src/auth/middleware.ts (added), src/routes/api.ts (updated)
Key decisions: Using JWT with 1h expiry; refresh token in httpOnly cookie
Blocked on: CORS configuration for cross-origin refresh token flow
Next: Write tests for token refresh path
```

---

### 2. Opaque Compression
Produce a compressed representation optimized for reconstruction fidelity rather than human readability. Achieves highest compression ratios (99%+) but sacrifices interpretability.

**Why it works**: Optimizes for what the model needs to reconstruct context, not what a human would find readable.

**When to use**: High-volume automated pipelines where you don't need to inspect the compressed summary; when compression ratio matters more than debuggability.

**Caveat**: Cannot verify what was preserved. Harder to debug when compression loses critical information.

---

### 3. Regenerative Full Summary
Generate a fresh detailed summary from scratch on each compression trigger.

**Why it's worse**: Each regeneration can lose details that prior compressions handled correctly. Compounding across multiple cycles causes drift. Produces readable output but less reliable than anchored iterative across long sessions.

**When acceptable**: Short sessions with a single compression event; when simplicity matters more than accuracy.

## Token Budget Allocation

Understanding where tokens go helps decide what to protect vs. compress:

| Component | Typical Range | Compress? |
|---|---|---|
| System prompt | 500–2000 tokens | Never |
| Tool definitions | 100–500 per tool | No |
| Active task state | Variable | Never |
| Critical decisions | Variable | No — move to summary |
| Recent turns (last 3–5) | Variable | No |
| Tool outputs (current) | Variable | Partial — keep head+tail |
| Old message history | Grows unbounded | Yes — primary compression target |
| Retrieved documents | Often largest | Selective — mask served-purpose docs |

## KV-Cache Optimization

KV-cache hit rate determines recomputation cost. Cache hits require prefix stability — the beginning of the prompt must be identical across requests.

**Design rules:**
1. Place system prompts and tool definitions at the very start — they're stable across turns
2. Never put timestamps, session IDs, or request-specific data in the system prompt
3. Keep dynamic content (current task, user query) at the end
4. Consistent formatting across requests — even whitespace changes invalidate cache

```python
# Cache-unfriendly: timestamp in system prompt
system = f"Current time: {datetime.now().isoformat()}\nYou are..."

# Cache-friendly: stable system prompt, dynamic data appended
system = "You are a code assistant. Current time is provided per-request."
```

## Practical Decision Rule

- **Single session, no explicit complexity**: default to anchored iterative summarization
- **High-volume pipeline, compression ratio critical**: opaque compression
- **Quick prototype, one compression expected**: regenerative is fine
- **Never**: aggressive deletion without a summary — you will lose file modification history

## Clear Over Compact — Now Community Consensus

Matt Pocock (see [[summaries/mattpocockworkflow]]) argues against compacting and prefers hard context clears:

> "I much prefer my AI to behave like the guy from Memento because this state is always the same. Every time you do it, you clear and you go back to the beginning."

His argument: compaction introduces "sediment" — each compressed summary is imperfect, and multiple cycles compound drift. Clearing gives a deterministic, reproducible starting state.

**Updated (2026-05-04)**: Community evidence from r/ClaudeCode (30+ practitioners) shows clear-over-compact is now the **majority practice** for AI coding workflows — not a contrarian position. Every active framework (GSD, Dangeresque, SandCastle, vanilla loops) enforces fresh context per task. Anchored iterative summarization remains the recommendation for workflows *without* a durable filesystem layer.

**When clear-over-compact is valid**: filesystem stores all state (issue files, commits, PRDs); harness re-injects state at session start. The key design principle: **make clearing safe, then prefer clearing**.

**When anchored iterative summarization is still better**: no durable filesystem layer; long interactive sessions where rebuilding state from scratch is expensive; conversational continuity that can't be reconstructed from files.

**OpenCode hook extension**: OpenCode exposes `experimental.session.compacting` — a hook that lets plugins inject domain state into compaction summaries or replace the compaction prompt entirely. This enables custom anchored iterative summarization at the harness level, more reliable than system-prompt instructions. See [[comparisons/claude-code-vs-opencode-plugins]].

## Related Pages

- [[concepts/context-degradation]] — the failure modes compression prevents
- [[concepts/agent-harness]] — where compaction fits in the harness component model
- [[concepts/ralph-loop]] — filesystem as durable state across clean context windows (the complement to compression)
- [[summaries/mattpocockworkflow]] — Pocock's workflow that makes clearing safe by externalizing state
