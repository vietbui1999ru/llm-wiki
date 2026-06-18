---
title: "omp (oh-my-pi) — Batteries-Included Pi Fork"
type: summary
tags: [coding-agent, agent-harness, lsp, dap, rust, native-tools, hashline, multi-provider, subagents]
sources: ["omp oh-my-pi README (github.com/can1357/oh-my-pi)"]
created: 2026-06-17
updated: 2026-06-17
---

# omp (oh-my-pi) — Batteries-Included Pi Fork

README survey of `can1357/oh-my-pi`. omp is a fork of Mario Zechner's `badlogic/pi-mono`, rewritten as a feature-complete coding agent with a native Rust core.

---

## Problem Addressed

Pi's minimal-harness thesis (4 tools, tiny system prompt) is validated by Terminal Bench data — but minimalism has a ceiling. `can1357` identified a different class of failures: **tool quality**, not tool count. Bad string-match edits, no debugger, no LSP integration, fork/exec overhead on every search — these cause retry loops and token waste regardless of model. omp's answer: replace the brittle parts with native, reliable primitives, then add the missing tools.

---

## Architecture

Fork of pi-mono with same TypeScript monorepo structure, extended with:

| Layer | Pi original | omp |
|---|---|---|
| Tools | 4 (read/write/edit/bash) | 32 |
| Edit format | String match (`str_replace`) | Hashline (content-hash anchors) |
| Native core | None (shells out) | ~55k LoC Rust N-API addon |
| LSP | None | Wired into every write |
| Debugger | None | DAP (lldb/dlv/debugpy) |
| Providers | Multi (pi-ai abstraction) | 40+ with fallback chains |
| Memory | None | Hindsight (SQLite, project-scoped) |
| Context compression | None | Snapcompact (bitmap-frame) |
| Subagents | Community extension | First-class `task` tool |
| Editor protocol | None | ACP (Zed / Agent Client Protocol) |

---

## Key Innovations

### Hashline Editing
Content-hash anchors instead of line-content matching. Patch rejected if anchors diverge (stale file). Result: 61% fewer output tokens on Grok 4 Fast — the retry loop disappears. Benchmarks: +5pp over str_replace on Gemini 3 Flash; 2.1× pass rate on MiniMax; 10× lift on Grok Code Fast 1.

### LSP Wired Into Every Write
`workspace/willRenameFiles` fires before file moves → re-exports, barrel files, and aliased imports update atomically. No post-rename breakage.

### Time-Traveling Stream Rules (TTSR)
Regex match aborts stream mid-token, injects rule as system reminder, retries from same point. Course-correction without full-context tax. Rules survive compaction.

### DAP Debugger
`debug` tool drives lldb/dlv/debugpy via DAP protocol. Attach, breakpoint, step, read frame — the agent debugs instead of sprinkling print statements.

### First-Class Subagents
`task` tool fans out into worktree-isolated workers. Returns typed schema-validated objects (no prose parsing). `irc` tool provides short prose between live agents in-process.

### Persistent Eval Kernels
`eval` runs persistent Python and Bun workers. Either kernel can call back into the agent's tools (`read`, `search`, `task`) via loopback bridge. Multi-kernel cells in one session.

### Conflict Resolution Scheme
`conflict://N` and `conflict://*` URLs. Write `@theirs`/`@ours`/`@base` to resolve. Atomic.

### Native Rust Core (~55k LoC)
In-process: ripgrep, glob, find, AST grep (tree-sitter, 50+ grammars), brush shell (embedded bash), syntax highlighting, PTY, image decode, BPE counting. No fork/exec on the hot path.

### Hindsight Memory
SQLite memory engine per project. Agent writes facts with `retain`, retrieves with `recall`, synthesizes with `reflect`. Between-session persistence without manual MEMORY.md.

### Snapcompact
Bitmap-frame context compression package. Distinct from standard summarization compaction.

---

## Provider Surface

40+ providers: Anthropic (oauth), OpenAI, Gemini, xAI, Groq, Cerebras, Fireworks, Together, HuggingFace, NVIDIA, OpenRouter, Perplexity, Cursor (oauth), GitHub Copilot (oauth), Kimi Code, MiniMax, Alibaba, Qwen, and more. Plus OpenAI-compatible local (Ollama, LM Studio, llama.cpp, vLLM, LiteLLM).

Routing features: fallback chains per role, path-scoped model overrides, round-robin credential rotation with per-key backoff.

---

## Config Inheritance

On first run, reads existing configs from `.claude`, `.cursor`, `.windsurf`, `.gemini`, `.codex`, `.cline`, `.github/copilot`, `.vscode`. No migration script needed.

---

## Entry Points

| Mode | How |
|---|---|
| Interactive TUI | `omp` |
| One-shot | `omp -p "prompt"` |
| Node SDK | `@oh-my-pi/pi-coding-agent` package |
| RPC (NDJSON stdio) | `omp --mode rpc` |
| ACP (Zed) | `omp acp` |

---

## Related Pages

- [[entities/omp]] — entity page with capability table
- [[entities/pi-agent]] — the upstream fork; minimal harness design
- [[comparisons/our-stack-vs-omp]] — feature gap vs Claude Code + Pi setup
- [[concepts/agent-harness]] — harness engineering context
