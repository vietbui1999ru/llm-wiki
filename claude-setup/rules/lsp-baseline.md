# LSP Baseline

Language servers are baseline code-agent tools, but they should be project-scoped and lazy.

Rules:

- Do not start all LSPs globally at session startup.
- Detect stack from `.claude/profile.md` or project files.
- Enable only matching servers: TypeScript/JS → `vtsls`, Python → `pyright`/`basedpyright`, Go → `gopls`, Rust → `rust-analyzer`, C/C++ → `clangd`.
- Start LSP on first code-changing task or first symbol/diagnostic query, not for chat-only sessions.
- Reuse one LSP per workspace/worktree for the active session.
- Treat LSP diagnostics as first-pass feedback only; still run typecheck/compiler, tests, and diff review.
- Do not write raw LSP caches or diagnostic streams into Commandr `.agents/`; project neutral progress or review artifacts only.

When a project profile has `lsp: lazy` or `lsp: enabled`, prefer LSP symbol/diagnostic queries before broad text edits or risky renames.

Neovim/Mason operator lane:

- If profile has `operator_ide: neovim` and `lsp_manager: mason`, do not enable duplicate global Claude LSP plugins by default.
- Treat Neovim/Mason/nvim-dap as the human review/debug surface.
- Agent runners may still use their own LSP lazily (`omp`, OpenCode LSP events, Claude LSP plugin) when autonomous code intelligence is needed.
- Prefer sending precise file/line/selection context from Neovim to agents over dumping whole files.
