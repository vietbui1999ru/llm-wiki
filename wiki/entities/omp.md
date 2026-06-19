---
title: "omp (oh-my-pi)"
type: entity
tags: [coding-agent, agent-harness, rust, lsp, dap, hashline, multi-provider, subagents, memory, native-tools]
sources: ["omp oh-my-pi README (github.com/can1357/oh-my-pi)", "Desktop AI Agent Control Plane Executive Summary (2026-06-17)"]
created: 2026-06-17
updated: 2026-06-17
---

# omp (oh-my-pi)

Fork of `badlogic/pi-mono` by `can1357`. Positions itself as the batteries-included coding agent: same TypeScript + TUI shell as Pi, but with a ~55k-line Rust native core and 32 built-in tools. MIT license.

GitHub: https://github.com/can1357/oh-my-pi
Docs: https://omp.sh

Install: `curl -fsSL https://omp.sh/install | sh` · Homebrew · Bun · Windows PowerShell · mise

---

## Why It Diverges From Pi

Pi's thesis: **minimal harness beats feature-heavy harness** (validated by Terminal Bench). omp accepts the data but identifies a different failure class: **tool quality failures** — string-match edits that fail on whitespace drift, missing debugger forcing print-statement debugging, no LSP integration for cross-file renames, fork/exec overhead on every search. omp's answer: replace unreliable primitives with native ones, then add the tools that eliminate entire categories of retry loops.

---

## Tool Surface (32 tools)

### Files & Search
| Tool | Description |
|---|---|
| `read` | Files, dirs, archives, SQLite, PDFs, notebooks, URLs, internal `://` schemes |
| `write` | File, archive entry, SQLite row |
| `edit` | Hashline patches (content-hash anchors + stale-anchor rejection) |
| `ast_edit` | Structural rewrite via ast-grep; preview card → `resolve` to commit |
| `ast_grep` | Structural code queries, 50+ tree-sitter grammars |
| `search` | Regex over files, globs, internal URLs |
| `find` | Glob path lookup |

### Runtime
| Tool | Description |
|---|---|
| `bash` | Workspace shell; optional PTY or background jobs |
| `eval` | Persistent Python + Bun kernels; tool re-entry via loopback bridge |
| `ssh` | One remote command against configured host |

### Code Intelligence
| Tool | Description |
|---|---|
| `lsp` | Diagnostics, navigation, symbols, renames, code actions, raw requests |
| `debug` | DAP sessions — breakpoints, stepping, threads, stack, variables |

### Coordination
| Tool | Description |
|---|---|
| `task` | Fan-out subagents; worktree isolation; typed schema results |
| `irc` | Short prose between live agents in-process |
| `todo` | Ordered mutations over session todo list |
| `job` | Wait/cancel background jobs |
| `ask` | Structured option picker for interactive runs |

### Outside the Box
| Tool | Description |
|---|---|
| `browser` | Puppeteer/CDP; headless Chromium; stealth on by default; can drive Electron apps |
| `web_search` | 14 providers; specialized handlers (GitHub, npm, arxiv, CVEs, forums, docs) |
| `github` | GitHub CLI ops; PR/issues/code search/Actions |
| `generate_image` | Via Gemini/GPT-image/Grok |
| `inspect_image` | Vision-model analysis |
| `tts` | Text-to-speech via xAI Grok Voice |

### Memory & State
| Tool | Description |
|---|---|
| `checkpoint` | Mark conversation state for later collapse |
| `rewind` | Prune exploratory context, keep concise report |
| `retain` | Queue durable facts into Hindsight bank |
| `recall` | Search Hindsight bank |
| `reflect` | Synthesize answer over Hindsight bank |

### Misc
| Tool | Description |
|---|---|
| `resolve` | Apply or discard a queued preview action |
| `search_tool_bm25` | BM25 over hidden tool index; activates top matches mid-session |

---

## Differentiating Primitives

### Hashline Edit Format
Content-hash anchors replace string matching. Stale anchors (file changed since read) are rejected before corruption. 61% fewer output tokens on Grok 4 Fast. 2.1× pass rate lift on MiniMax. +5pp over str_replace on Gemini 3 Flash.

### LSP Wired Into Writes
Every write goes through `workspace/willRenameFiles`. Re-exports, barrel files, aliased imports update before the file moves. No post-rename breakage without IDE.

### Time-Traveling Stream Rules (TTSR)
Regex match aborts mid-token stream → injects rule as system reminder → retries from same point. No full-context tax. Injections survive compaction. Qualitatively different from PreToolUse hooks: fires mid-stream, not between turns.

### DAP Debugger
Drives lldb (C/C++/Rust), dlv (Go), debugpy (Python) via DAP protocol. Attach, step, inspect frame. Not a REPL workaround.

### Task (First-Class Subagents)
Worktree-isolated workers with typed schema-validated return objects. `irc` enables in-process inter-agent prose. No prose parsing of subagent output.

### Eval Kernels
Persistent Python + Bun cells that share a prelude and can call back into agent tools. Multi-kernel, multi-cell within one session.

### Conflict Resolution Scheme
`conflict://N` URL → write `@theirs`/`@ours`/`@base` → file resolves atomically. `conflict://*` for bulk.

### Preview/Accept Workflow
`ast_edit` returns a staged "(proposed)" card. Agent calls `resolve` to commit atomically. Structural rewrites have a gate between proposal and application.

### Hindsight Memory
SQLite memory engine, project-scoped. `retain` (write) / `recall` (search) / `reflect` (synthesize). Survives sessions. Qualitatively different from manually maintained MEMORY.md.

### Snapcompact
Bitmap-frame context compression — distinct from summarization-based compaction.

---

## Native Rust Core (~55k LoC)

In-process on libuv thread pool. No fork/exec on hot path.

| Module | What |
|---|---|
| shell | Embedded bash (brush-vendored); persistent sessions |
| grep | Parallel regex; glob + type filters; fuzzy find |
| summary | Tree-sitter structural summaries |
| ast | ast-grep pattern matching and structural rewrites |
| glob | Discovery; gitignore-aware |
| highlight | Syntax highlighting; 30+ aliases |
| pty | Native PTY for sudo/ssh |
| iso | Workspace isolation: APFS/btrfs/zfs reflinks, overlayfs, projfs |
| tokens | O200k/Cl100k BPE counting, tables embedded |
| sixel | Terminal image: PNG/JPEG/WebP/GIF → SIXEL |

---

## Provider Surface (40+)

Roles: `default`, `smol` (cheap fan-out), `slow` (deep reasoning), `plan`, `commit`. Cycle with `Ctrl+P`, swap mid-session with `/model`.

Features: fallback chains per role, path-scoped model overrides (different model set per repo prefix), round-robin credential rotation with per-key backoff.

Notable: Cursor (oauth), GitHub Copilot (oauth), Kimi Code, MiniMax Coding Plan, Alibaba Coding Plan, Qwen Portal, Xiaomi MiMo — plus all OpenAI-compatible local servers (Ollama, LM Studio, llama.cpp, vLLM, LiteLLM).

---

## Config Inheritance

Inherits from `.claude`, `.cursor`, `.windsurf`, `.gemini`, `.codex`, `.cline`, `.github/copilot`, `.vscode` on first run. Existing rules, skills, MCP servers carry over without migration.

---

## Entry Points

| Mode | Command |
|---|---|
| Interactive TUI | `omp` |
| One-shot | `omp -p "..."` |
| Node/TS SDK | `@oh-my-pi/pi-coding-agent` |
| NDJSON RPC | `omp --mode rpc` |
| ACP (Zed) | `omp acp` |

---

## Plugin Architecture

omp bundles skills, commands, hooks, custom tools, MCP servers, and themes in a single installable package. The surface is Claude-Code-compatible — existing `.claude-plugin/` catalogs work as-is.

| Piece | Discovery | What it does |
|---|---|---|
| Hooks | `hooks/pre/*.ts`, `hooks/post/*.ts` | Intercept `tool_call`, `tool_result`, `context`, session lifecycle |
| Custom Tools | `tools/<name>/index.ts` | Register new tools with Zod/TypeBox schemas |
| Skills | `skills/<name>/SKILL.md` | On-demand markdown playbooks |
| Commands | `commands/<name>.md` | Slash-command prompt templates |
| MCP | `mcp.json` | Extra `mcpServers` entries |

Install: `omp install ./path` (symlinks + watches), `omp install github:user/repo`, `omp install @scope/plugin`. Project-scoped with `-l`.

### Headroom Compression Plugin (Local)

A working example lives at `pi-headroom/` in this repo:

- **`hooks/pre/headroom-compress.ts`** — `tool_result` hook that compresses or truncates large tool outputs before the model sees them using `headroom-ai`
- **`tools/headroom-retrieve/index.ts`** — custom tool that lets the model fetch original uncompressed content on demand

Install:
```bash
cd pi-headroom && npm install
omp install ./pi-headroom
```

**Tested on omp v16.0.9:**

| Feature | Status |
|---|---|
| `tool_result` hook | ✅ Fires and modifies content the model sees |
| `headroom_retrieve` tool | ✅ Registered and callable |
| `context` hook `{ messages }` | ❌ Return contract ignored in v16.0.9 |
| Headroom compression | ⚠️ Requires proxy passthrough or cloud API key; fallback truncation works |

The plugin uses `tool_result` instead of `context` because omp 16.0.9 does not support message-array replacement via `context` hook returns. This still covers the bulk of token bloat (tool outputs). See `pi-headroom/README.md` for full test results and configuration.

## Role in Commandr Stack

omp is the strongest practical L2 runner candidate: a high-quality worker, not the bus. Its value is execution quality inside a task: hashline edits, LSP/DAP, typed subagent outputs, internal schemes, persistent eval kernels, and provider routing. [[entities/commandr]] should still own claim/progress/approval/complete lifecycle.

Integration ladder:

| Level | Shape |
|---|---|
| 0 | `omp -p "<task packet>"` subprocess; Tauri captures stdout/stderr |
| 1 | `commandr-omp-runner` wrapper claims next packet, creates workspace, runs omp, streams logs, emits progress, completes/fails |
| 2 | omp custom tools for Commandr: progress, request approval, emit artifact, complete |
| 3 | omp plugin intercepts tool calls/events and writes turn snapshots/approval requests directly |

Start at Level 1. Level 2 becomes useful once task/event/approval schemas stabilize. Level 3 (plugin-based bidirectional sync) is where the headroom plugin pattern also lives — a plugin can both intercept context and register tools that talk back to Commandr's bus.

---

## Internal Schemes (`://`)

`pr://`, `issue://`, `agent://`, `skill://`, `rule://` and others resolve through the same FS-shaped tools. `read pr://owner/repo/1428` returns the same shape as `read src/foo.ts`. `agent://<id>/findings.0.path` extracts a field from subagent output.

---

## Monorepo Packages (omp-specific additions)

| Package | Purpose |
|---|---|
| `@oh-my-pi/pi-natives` | Rust N-API addon aggregating all native crates |
| `@oh-my-pi/pi-mnemopi` | Hindsight SQLite memory engine |
| `@oh-my-pi/snapcompact` | Bitmap-frame context compression |
| `@oh-my-pi/hashline` | Hashline patch format and applier |
| `@oh-my-pi/swarm-extension` | Swarm orchestration extension |
| `@oh-my-pi/collab-web` | Browser guest client for collab live sessions |
| `@oh-my-pi/omp-stats` | Local observability dashboard |

---

## Related Pages

- [[entities/pi-agent]] — upstream fork; minimal harness design; Terminal Bench data
- [[summaries/omp-oh-my-pi]] — full source summary
- [[comparisons/our-stack-vs-omp]] — feature gap vs our Claude Code + Pi setup
- [[entities/commandr]] — L3 bus omp should speak through
- [[entities/diffviewer]] — L5 UI consuming omp artifacts through Commandr/DiffViewer sidecars
- [[concepts/agent-harness]] — harness engineering framing
- [[comparisons/claude-code-vs-opencode-plugins]] — adjacent harness comparison
