---
title: "Dynamic Context Pruning (DCP)"
type: concept
tags: [context-management, token-efficiency, agent-harness, opencode]
sources:
  - "Opencode-DCPopencode-dynamic-context-pruning Dynamic context pruning plugin for OpenCode - intelligently manages conversation context to optimize token usage.md"
  - "Quick Start Install DCP Plugin  opencode-dynamic-context-pruning.md"
  - "Claude runaway... tried Kimi 2.6 and Deepseek v4 (5y fullstack dev).md"
created: 2026-05-04
updated: 2026-05-06
---

# Dynamic Context Pruning (DCP)

Mid-session reduction of the context payload sent to the LLM, performed without modifying the underlying session history. Where compaction summarizes everything at a hard threshold, DCP runs as a combination of model-driven compression and automatic cleanup strategies that fire on each LLM fetch — pruned spans are replaced with placeholders before the request is dispatched.

Reference implementation: [[entities/opencode-dcp]] — the `@tarquinen/opencode-dcp` plugin for [[entities/opencode]]. Install:

```bash
opencode plugin @tarquinen/opencode-dcp@latest --global
```

---

## The Problem It Solves

Long coding sessions accumulate three classes of dead weight in the active context:

- Repeated tool calls (same tool, same args invoked across turns)
- Errored tool inputs whose large input payload is no longer relevant once the error has been read
- Closed/finished spans of conversation that the model no longer needs verbatim

These dilute attention and inflate per-request cost without contributing signal. DCP attacks each class with a different mechanism rather than waiting for full compaction.

---

## Three Mechanisms

DCP composes three independent prune paths. Pruned content never leaves the session log on disk — it is only replaced with a placeholder in the outgoing request.

### 1. Compress (model-driven)

A `compress` tool exposed to the model. The model decides when to call it based on task completion, picking which spans no longer need verbatim representation. This is **not** automatic per turn — the model triggers it.

Two modes:

- `range` (default) — compresses contiguous spans of conversation into block summaries. When a new compression overlaps an earlier one, the earlier summary is **nested** inside the new one to preserve information across compression layers rather than dilute it.
- `message` (experimental) — compresses individual raw messages independently. Allows much more surgical context management.

In both modes, protected tool outputs (subagents, skills, todos) and protected file patterns are appended to compression summaries, ensuring critical state is never lost. `protectUserMessages` keeps user messages verbatim during compression — but this means large pasted prompts (e.g. log files) will never be compressed away.

DCP injects nudges to encourage compression based on context size:

- Below `minContextLimit` (default 50K tokens): no reminders
- Between min and max: reminders active, but soft
- Above `maxContextLimit` (default 100K tokens): strong nudges, fires every `nudgeFrequency` fetches

Both limits accept an absolute number or a `"X%"` of the model's context window. Per-model overrides via `modelMinLimits` / `modelMaxLimits`.

### 2. Deduplication (automatic)

Identifies repeated tool calls (same tool name, same arguments) and keeps only the most recent output. Recalculated **on LLM fetch** — i.e. when the request is being assembled, not on every tool-call event. Prompt cache impact is therefore aligned with compression events, not interspersed mid-turn.

### 3. Purge Errors (automatic)

Prunes the **input** payload of errored tool calls after a configurable number of turns (default: 4). Error messages themselves are preserved — only the potentially large input content is removed. Recalculated alongside compress.

---

## How It Differs From Compaction

| Dimension | DCP | Compaction |
|---|---|---|
| Trigger | Model-driven (compress) + automatic on LLM fetch (dedup, purge) | Threshold (token count or session-end signal) |
| Scope | Surgical — specific messages or spans | Whole conversation |
| What it removes | Stale tool inputs, duplicates, closed spans | Replaces full history with summary |
| What it preserves | Recent state, protected tools/files, optionally user messages | Structured summary of decisions |
| Reversibility | `decompress`/`recompress` commands restore by ID | Originals replaced; not reversible from session |
| Implementation | Plugin (`@tarquinen/opencode-dcp`) | OpenCode `experimental.session.compacting` hook |

The two are **complementary**: DCP keeps the active payload lean continuously; compaction handles wholesale summarization at end of session or near hard limits.

---

## Commands

DCP exposes a `/dcp` slash command:

| Command | Purpose |
|---|---|
| `/dcp` | Show available DCP commands |
| `/dcp context` | Token-usage breakdown of current session by category, plus tokens saved |
| `/dcp stats` | Cumulative pruning stats across all sessions |
| `/dcp sweep [n]` | Prune all tools since last user message (or last n). Respects `commands.protectedTools` |
| `/dcp manual [on\|off]` | Toggle manual mode — disables autonomous context tools |
| `/dcp compress [focus]` | Trigger one compress execution. Optional focus text directs what to compress |
| `/dcp decompress <n>` | Restore a compression by ID (no arg lists available IDs and topics) |
| `/dcp recompress <n>` | Re-apply a user-decompressed compression by ID |

---

## Protected Tools

By default these tools are never pruned:

```
task, skill, todowrite, todoread, compress, batch, plan_enter, plan_exit, write, edit
```

The `commands.protectedTools` and `strategies.deduplication.protectedTools` / `strategies.purgeErrors.protectedTools` arrays **add** to this default list. The `compress.protectedTools` array works differently — those tool outputs get appended to compression summaries rather than excluded.

---

## Prompt Cache Trade-Off

LLM providers cache prompts based on exact prefix matching. Because DCP rewrites the outgoing request — replacing pruned content with placeholders — it invalidates cached prefixes from the prune point forward.

Reported numbers from the plugin's testing:

- ~85% cache hit rate **with** DCP
- ~90% cache hit rate **without** DCP

Lost cache reads are traded for token savings on reduced context size and fewer hallucinations from stale content. In long sessions, savings outweigh cache miss cost.

**No impact** for:

- Request-based billing (e.g. GitHub Copilot — charges per request, not tokens)
- Uniform token pricing (e.g. Cerebras — same rate for cached and uncached)

---

## Relation to Clear-Over-Compact

[[concepts/context-compression]] documents that clear-over-compact has become community consensus for harness-based AFK workflows. DCP fits the **interactive** path:

- Sessions with safe clear points → clear (Pocock workflow)
- Long interactive sessions where clearing loses unrecoverable state → DCP + compaction
- Fully automated AFK loops → worktree isolation gives each task fresh context (no DCP needed)

DCP is most valuable for interactive sessions with no natural clear point, especially with smaller-context models (GitHub Copilot, local) where the `minContextLimit` / `maxContextLimit` values should be lowered to match.

---

## Relation to Lean-Session

The `lean-session` plugin (custom, in `templates/`) and DCP solve overlapping problems via different hook surfaces:

- **lean-session** uses OpenCode's `experimental.session.compacting` hook — intervenes in the compaction process itself.
- **DCP** introduces a `compress` tool plus automatic `tool.execute`-time strategies — works mostly outside compaction.

They are **complementary, not competing**: lean-session shapes the compaction summary when compaction does fire; DCP keeps the active context lean so compaction fires later, less often, and on cleaner input.

---

## Related Pages

- [[entities/opencode-dcp]] — the plugin itself (config reference, commands, prompt cache trade-off)
- [[concepts/context-compression]] — compression strategy taxonomy
- [[entities/opencode]] — host harness
- [[concepts/context-degradation]] — failure modes DCP prevents (distraction, confusion)
- [[comparisons/claude-code-vs-opencode-plugins]] — why this plugin exists in OpenCode and not Claude Code
