---
title: "Dynamic Context Pruning (DCP)"
type: concept
tags: [context-management, token-efficiency, agent-harness, opencode]
sources: ["Claude runaway... tried Kimi 2.6 and Deepseek v4 (5y fullstack dev).md"]
status: documented-not-adopted
created: 2026-05-04
updated: 2026-05-04
---

# Dynamic Context Pruning (DCP)

Continuous mid-session trimming of stale tool results and large file contents from the live context window. Distinct from compaction — DCP runs continuously as the session progresses; compaction is threshold-triggered and summarizes conversation history.

Implemented in `settings-opencode` via `@tarquinen/opencode-dcp` plugin.

---

## The Problem it Solves

Long coding sessions accumulate:
- Tool results from earlier turns (file reads, bash outputs) that are no longer relevant
- Large file contents loaded early but now outdated (file was edited since)
- Redundant search results from multiple query iterations

These take up context without contributing signal. The model's attention is diluted across stale content while the relevant current-state content competes for the same budget.

DCP prunes the stale entries continuously, before they compound into a saturation event requiring full compaction.

---

## How It Differs from Compaction

| Dimension | DCP | Compaction |
|---|---|---|
| Trigger | Continuous / per-turn | Threshold (token count or tool-call count) |
| What it removes | Stale tool results, large file contents | Summarizes conversation history |
| What it preserves | Current state, recent context | Structured summary of key decisions |
| Output | Pruned live context | Compressed summary replacing old turns |
| Reversibility | Entries removed from active window | Originals replaced by summary |
| Implementation | Plugin hook (per tool call) | `experimental.session.compacting` hook |

They are complementary: DCP keeps the active context lean between compaction events; compaction handles the full summarization when context crosses the threshold.

---

## Idle-Gated Auto-Compaction

Settings-opencode pairs DCP with idle-gated compaction (`auto-compact.js`):
- Tracks tool call count against `OC_COMPACT_THRESHOLD`
- Only triggers compaction when `session.idle` fires
- Avoids interrupting active work mid-task

Combined pattern:
```
active session → DCP prunes stale entries continuously
              → tool call count rises toward threshold
              → user pauses (session.idle)
              → auto-compaction triggers
              → session resumes with clean context
```

---

## Relation to Clear-Over-Compact

[[concepts/context-compression]] documents that clear-over-compact is now community consensus for coding workflows. DCP is the middle path:
- For sessions where clearing is possible → clear (Pocock workflow)
- For long interactive sessions where clearing loses state → DCP + idle-gated compaction
- For fully automated AFK loops → Dangeresque / SandCastle manage context via worktree isolation (each task gets fresh context)

DCP is most valuable for **interactive sessions** that run long without natural clear points.

---

## Configuration

```jsonc
// dcp.jsonc in settings-opencode
{
  "pruneAfterTurns": 5,        // remove tool result after N turns
  "maxFileContentTokens": 2000, // truncate large file reads
  "preserveLastN": 3           // always keep last N tool results
}
```

---

## Related Pages

- [[concepts/context-compression]] — compaction strategies; DCP extends this
- [[entities/opencode]] — plugin system implementing DCP
- [[concepts/context-degradation]] — failure modes DCP prevents (distraction, confusion)
- [[concepts/instinct-clustering]] — companion pattern from settings-opencode
