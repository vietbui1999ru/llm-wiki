---
title: "rtk (Rust Token Killer)"
type: entity
tags: [tool, cli, token-compression, context-management, agent-tooling, rust, hook]
sources: ["rtk-airtk CLI proxy that reduces LLM token consumption by 60-90% on common dev commands. Single Rust binary, zero dependencies.md"]
created: 2026-07-20
updated: 2026-07-20
---

# rtk (Rust Token Killer)

`rtk` is a CLI proxy that **filters and compresses command output before it reaches an LLM's context window**. A coding agent runs `git status`, `cat`, `cargo test`, etc.; rtk intercepts the command, runs the real tool, and returns a compact version — cutting the tokens the agent must ingest. Single Rust binary, 100+ supported commands, self-reported `<10ms` overhead, Apache-2.0. Repo: `rtk-ai/rtk`; site: rtk-ai.app. Version at capture: `0.28.2` (README also references v0.37.2 hook changes — versioning in the source is internally inconsistent).

**Name collisions** (disambiguate before installing/citing): another `rtk` = "Rust Type Kit" on crates.io; "RTK" also commonly means Redux Toolkit. This is the AI-token one — install via `cargo install --git https://github.com/rtk-ai/rtk`, not `cargo install rtk`.

## How it works

Positioned between the agent and the shell: `Claude → rtk → git` instead of `Claude → shell → git`. Four compression strategies applied per command type:

1. **Smart filtering** — strip comments, whitespace, boilerplate.
2. **Grouping** — aggregate similar items (files by directory, errors by type).
3. **Truncation** — keep relevant context, cut redundancy.
4. **Deduplication** — collapse repeated log lines with counts.

Editing/reading verbosity is tunable: `rtk read file.rs -l aggressive` returns **signatures only** (strips bodies); `rtk smart file.rs` gives a 2-line heuristic summary.

### Auto-rewrite hook (the intended mode)

`rtk init -g` installs a **PreToolUse hook** that transparently rewrites Bash tool calls (`git status` → `rtk git status`) before execution — the agent needs no awareness of rtk. Supports 15 agents via each one's interception mechanism: Claude Code / Copilot (PreToolUse hook, native binary), Gemini CLI (BeforeTool), Codex (AGENTS.md instructions), Cursor/Windsurf/Cline/Kilo/Antigravity/Kimi (project rules files), OpenCode/OpenClaw/Pi (TS plugin), Hermes (Python plugin), Factory Droid (hook).

**Important scope limit:** the hook only fires on **Bash tool calls**. Claude Code's built-in `Read`/`Grep`/`Glob` tools bypass it, so they are *not* auto-compressed — to get rtk output there you must call `rtk read`/`rtk grep`/`rtk find` or shell equivalents explicitly. (This is a real gap for Claude Code, whose agents lean heavily on the native Read/Grep/Glob tools.)

### tee fail-safe

On command failure, rtk saves the **full unfiltered output** to a `tee` log and points the agent at the path — so the LLM can read complete error detail without re-running the command. Configurable (`failures` / `always` / `never`).

## Token-savings claims — verify

The README's headline "60-90%" and its per-command table (e.g. `git push` −92%, `cargo test` −90%, session total ~118k → ~23.9k tokens, −80%) are **self-reported estimates**, explicitly qualified in-source as *"based on medium-sized TypeScript/Rust projects; actual savings vary."* No independent benchmark. Treat as **(claimed, unverified)** per wiki citation rules — a vendor illustration of expected magnitude, not measured performance. `rtk gain` reports *locally measured* savings per install, which is stronger evidence than the README table but still self-instrumented.

Telemetry is opt-in / disabled by default (GDPR-framed); collects aggregate counts and anonymized command names only, no source/args/paths.

## Connections

- Same "stateless CLI built for agents" niche as [[entities/ketch]] — but rtk *compresses existing tool output* rather than adding a new research surface; complementary, not competing.
- Attacks the tokens-per-tool-output cost, adjacent to the tokens-per-task framing in [[concepts/context-compression]]. Distinct from conversation compaction: rtk shrinks each observation at the source, before it ever enters the context window.
- Hook-based, cross-agent command interception is the same integration pattern surveyed for other tools in [[concepts/agent-harness]].
