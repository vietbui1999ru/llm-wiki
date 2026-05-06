---
title: "OpenCode DCP — Dynamic Context Pruning Plugin"
type: summary
tags: [opencode, plugin, context-management, token-efficiency, compression]
sources:
  - "Opencode-DCPopencode-dynamic-context-pruning Dynamic context pruning plugin for OpenCode - intelligently manages conversation context to optimize token usage.md"
  - "Quick Start Install DCP Plugin  opencode-dynamic-context-pruning.md"
created: 2026-05-06
updated: 2026-05-06
---

# OpenCode DCP — Dynamic Context Pruning Plugin

Synthesis of the official `@tarquinen/opencode-dcp` README and the Quick Start install guide.

## What It Is

A published [[entities/opencode]] plugin that reduces token usage by transforming the request payload sent to the LLM. The session history on disk is never modified — DCP only replaces pruned content with placeholders in outgoing requests. See concept page: [[concepts/dynamic-context-pruning]].

## Install

CLI (auto-adds to global config):

```bash
opencode plugin @tarquinen/opencode-dcp@latest --global
```

Or manually in `opencode.jsonc`:

```jsonc
{
  "plugin": ["@tarquinen/opencode-dcp@latest"]
}
```

Restart OpenCode. Verify with `/dcp` — should display the command help.

## Three Mechanisms

| Mechanism | Trigger | What it does |
|---|---|---|
| **Compress** | Model-driven via `compress` tool | Replaces closed conversation spans with high-fidelity technical summaries |
| **Deduplication** | Automatic, on LLM fetch | Keeps only the most recent output for repeated tool calls (same tool, same args) |
| **Purge Errors** | Automatic, after N turns (default 4) | Prunes the input of errored tool calls; error messages preserved |

Compress runs in two modes:

- `range` (default) — contiguous spans become block summaries; overlapping new compressions **nest** prior summaries instead of regenerating
- `message` (experimental) — per-message independent compression for surgical control

## Key Config Knobs

DCP creates `~/.config/opencode/dcp.jsonc` on first run, initially containing only `$schema`. All defaults live in code; only override what you need.

**Compress thresholds** (govern when nudges encourage compression):

```jsonc
"compress": {
  "mode": "range",                  // or "message" (experimental)
  "permission": "allow",            // "allow" | "ask" | "deny"
  "minContextLimit": 50000,         // below: reminders off
  "maxContextLimit": 100000,        // above: strong nudges, every nudgeFrequency fetches
  "nudgeFrequency": 5,
  "iterationNudgeThreshold": 15,    // messages since last user msg
  "nudgeForce": "soft",             // "soft" | "strong"
  "summaryBuffer": true,
  "protectUserMessages": false,     // true = pasted prompts never compressed away
  "protectedTools": []              // outputs appended to summary
}
```

Both limits accept absolute numbers or `"X%"` of model context. Per-model overrides via `modelMinLimits` / `modelMaxLimits`.

**Strategies:**

```jsonc
"strategies": {
  "deduplication": { "enabled": true, "protectedTools": [] },
  "purgeErrors":   { "enabled": true, "turns": 4, "protectedTools": [] }
}
```

**Other top-level knobs:**

- `enabled`, `debug`
- `pruneNotification`: `"off" | "minimal" | "detailed"`
- `pruneNotificationType`: `"chat" | "toast"`
- `manualMode.enabled` — disables autonomous context tools; `automaticStrategies` still runs unless explicitly disabled
- `turnProtection` — protect tools from pruning for N turns past invocation
- `protectedFilePatterns` — glob patterns matched against tool `parameters.filePath`
- `experimental.allowSubAgents`, `experimental.customPrompts`

**Protected tools (default, always preserved):**

```
task, skill, todowrite, todoread, compress, batch, plan_enter, plan_exit, write, edit
```

User-supplied `protectedTools` arrays in `commands` / `strategies` **add** to this list. `compress.protectedTools` instead controls which tool outputs get appended into compression summaries (defaults to `task`, `skill`, `todowrite`, `todoread`).

## Commands Reference

| Command | Purpose |
|---|---|
| `/dcp` | Show DCP command help |
| `/dcp context` | Per-category token breakdown of current session + tokens saved |
| `/dcp stats` | Cumulative pruning stats across all sessions |
| `/dcp sweep [n]` | Prune all tools (or last n) since last user message — respects `commands.protectedTools` |
| `/dcp manual [on\|off]` | Toggle manual mode |
| `/dcp compress [focus]` | Trigger one compress run; optional focus text directs target content |
| `/dcp decompress <n>` | Restore a compression by ID (no arg → list IDs and topics) |
| `/dcp recompress <n>` | Re-apply a user-decompressed compression |

## Prompt Cache Trade-Off

DCP rewrites outgoing requests, which invalidates prompt-cache prefixes from the prune point onward. Plugin author's measurements:

- ~85% cache hit rate with DCP
- ~90% cache hit rate without

Lost cache reads are traded against token savings on reduced context plus fewer hallucinations from stale content. In long sessions, savings dominate.

**No cache impact** for request-based billing (e.g. GitHub Copilot) or uniform-rate token pricing (e.g. Cerebras).

## Multi-Level Configuration

DCP searches config files in this order, with later levels overriding earlier:

1. **Global**: `~/.config/opencode/dcp.jsonc` (or `.json`) — auto-created on first run
2. **Custom directory**: `$OPENCODE_CONFIG_DIR/dcp.jsonc` — if env var set
3. **Project**: `.opencode/dcp.jsonc` — relative to project root

Project settings override global. Restart OpenCode after config changes.

For models with smaller context windows (Copilot, local models): lower `compress.minContextLimit` and `compress.maxContextLimit` to match available context.

## Prompt Overrides (experimental)

Disabled by default. Set `experimental.customPrompts: true` to activate. Six editable prompts: `system`, `compress-range`, `compress-message`, `context-limit-nudge`, `turn-nudge`, `iteration-nudge`. Defaults written to `~/.config/opencode/dcp-prompts/defaults/`; create override files with same names in an overrides directory to customize.

## Relation to Lean-Session and Built-in Compaction

| Layer | Where it intervenes | Trigger |
|---|---|---|
| **OpenCode built-in compaction** | End-of-context summarization | Token threshold |
| **lean-session** plugin | `experimental.session.compacting` hook — shapes the compaction prompt | Same as built-in |
| **DCP** | `compress` tool + automatic strategies on LLM fetch | Model decision (compress) + every fetch (dedup/purge) |

These layers compose. lean-session controls **what** compaction outputs when it does fire. DCP keeps the active payload lean so compaction fires later and less often, on cleaner input. Built-in compaction remains the final safety net at hard threshold.

## Related Pages

- [[concepts/dynamic-context-pruning]] — concept page (the *what* and *why*)
- [[entities/opencode-dcp]] — entity page (npm package, GitHub org, install)
- [[entities/opencode]] — host harness
- [[concepts/context-compression]] — broader compression strategy taxonomy
- [[comparisons/claude-code-vs-opencode-plugins]] — hook surface comparison
