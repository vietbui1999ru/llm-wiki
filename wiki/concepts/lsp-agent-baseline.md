---
title: "LSP as Agent Baseline"
type: concept
tags: [ai-agents, lsp, language-server, code-generation, agent-harness]
sources: ["cc-linting-debugging-reddit.md", "omp oh-my-pi README (github.com/can1357/oh-my-pi)", "Desktop AI Agent Control Plane Executive Summary (2026-06-17)", "https://github.com/mason-org/mason.nvim", "https://github.com/mfussenegger/nvim-dap", "https://xata.io/blog/configuring-neovim-coding-agents"]
created: 2026-06-18
updated: 2026-06-18
---

# LSP as Agent Baseline

Language Server Protocol (LSP) should be a baseline capability for serious coding agents, but not the source of truth for correctness.

LSP gives agents IDE-grade local facts:

- symbol lookup
- go-to-definition
- references
- diagnostics
- hover/type information
- safe rename support
- document symbols and workspace symbols

This reduces common agent failure modes: wrong import paths, hallucinated APIs, missed callers, stale type assumptions, and broad text edits when a symbol-aware edit would be safer.

---

## Role in the Agent Stack

LSP belongs in the execution substrate, not in the bus.

| Layer | LSP role |
|---|---|
| L1 driver | May expose LSP tools to the agent session. |
| L2 execution | Best home for warm language servers and symbol-aware tools. |
| L3 bus | Records neutral progress only; never stores LSP private state. |
| L4 knowledge | Stores durable docs and code graph summaries; complements LSP. |
| L5 UI | Displays diagnostics, symbol context, and blast-radius evidence. |

[[entities/omp]] is the current reference: it treats LSP/DAP as core worker infrastructure. That makes it a better L2 candidate for code-changing tasks than pure text-only subprocess agents.

---

## Startup Policy

Do not start every language server at global session startup. Use a lazy, per-project policy:

1. Detect stack from project profile or files.
2. Enable only matching LSP plugins/servers.
3. Start on first code task, not on chat-only sessions.
4. Reuse one server per workspace/worktree while the session is active.
5. Stop with the session or let the harness/plugin own lifecycle cleanup.

Always-on global LSPs are wasteful and can pollute diagnostics with irrelevant projects. Lazy project-scoped LSPs give most of the benefit with less overhead.

### Neovim/Mason exception

If the human operator uses Neovim as IDE replacement and Mason as LSP/DAP manager, distinguish two lanes:

| Lane | Startup |
|---|---|
| Human IDE lane | Mason/lspconfig starts LSPs when Neovim opens buffers; nvim-dap starts adapters on demand. |
| Agent execution lane | Runner starts its own LSP support lazily only when code intelligence is needed. |

Do not duplicate Mason-managed LSPs by globally enabling every Claude Code LSP plugin. Use Neovim/Mason as the operator evidence surface and LSP-aware runners as the autonomous execution surface.

---

## Recommended Server Mapping

| Stack | Server/plugin |
|---|---|
| TypeScript/JavaScript | `vtsls` or TypeScript language server |
| Python | `pyright` or `basedpyright` |
| Go | `gopls` |
| Rust | `rust-analyzer` |
| C/C++ | `clangd` |
| C# | OmniSharp |
| Ruby | `ruby-lsp` |
| OCaml | `ocaml-lsp` |
| JSON/YAML/CSS/HTML | VSCode language servers |

Claude Code plugin settings already expose these as optional LSP plugins; keep them disabled globally unless the project profile selects them.

---

## Verification Ladder

LSP is a fast feedback layer, not enough by itself.

Order for code agents:

1. LSP diagnostics for immediate local errors.
2. Typecheck/compiler for authoritative static correctness.
3. Unit/integration tests for behavior.
4. Diff review and human approval for intent and risk.

LSP catches many syntactic and symbol errors. It does not prove acceptance criteria, runtime behavior, security posture, or product intent.

---

## Commandr/DiffViewer Implication

Commandr should treat LSP as runner capability metadata, not bus state. A future `commandr-omp-runner` or LSP-aware runner can emit neutral progress such as "LSP diagnostics clean" or attach a review artifact, but it should not write raw language-server caches or diagnostics streams into `.agents/`.

DiffViewer/Tauri should surface LSP-derived evidence in the UI:

- diagnostics panel per task/session
- symbol/caller context on diff cards
- "diagnostics clean/dirty" badge on review packages
- safe-rename/blast-radius evidence when a change touches exported symbols

This keeps the bus stable while improving agent code quality at L2 and review quality at L5.

See [[syntheses/neovim-ai-operator-workflow]] for the Neovim/Mason/DAP operator workflow.
