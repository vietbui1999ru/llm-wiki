---
title: "Our Stack vs omp"
type: comparison
tags: [omp, claude-code, pi-agent, feature-gap, harness-design, lsp, dap, hashline]
sources: ["omp oh-my-pi README (github.com/can1357/oh-my-pi)"]
created: 2026-06-17
updated: 2026-06-17
---

# Our Stack vs omp

Feature gap analysis. Our stack: Claude Code (primary) + Pi (council/multi-provider) + MCP servers (Playwright, Firecrawl, GitHub, Figma, context7, qmd) + superpowers skills.

---

## Verdict

~55% feature parity. Hard gaps cluster around **tool quality primitives** — hashline editing, LSP integration into writes, DAP debugging, stream rules. These require native/Rust implementation and can't be approximated with scripts or MCP servers. Our wins are in **orchestration patterns, knowledge management, and MCP ecosystem depth**.

omp is better *inside a single session* (fewer failed edits, real debugger, LSP-aware writes).  
Our setup is better *across sessions* (wiki, memory patterns, structured orchestration).

Control-plane implication: use omp as L2 execution substrate, not as L3 bus or L5 UI. The right integration is `commandr-omp-runner` first, then omp custom tools that speak [[entities/commandr]] events/approvals/artifacts. Do not collapse Commandr into omp session state.

---

## Feature Table

| Feature | omp | Our Stack | Gap |
|---|---|---|---|
| **Hashline editing** | Content-hash anchors; stale patch rejected before corruption; 61% fewer tokens on Grok 4 Fast | CC `Edit` uses string matching — fails on whitespace/drift | Hard gap — needs native impl |
| **LSP wired into writes** | `workspace/willRenameFiles` before file moves; cross-file renames atomic | CC has LSP via IDE extensions only; CLI workflow blind | Hard gap |
| **DAP debugger** | lldb/dlv/debugpy via `debug` tool; attach, step, inspect frame | None | Hard gap |
| **Time-traveling stream rules** | Regex aborts mid-token stream; injects rule; retries from same point; survives compaction | PreToolUse hooks between turns — no mid-stream interception | Hard gap — qualitatively different |
| **Persistent eval kernels** | Python + Bun cells; tool re-entry via loopback bridge | None natively | Hard gap |
| **Native in-process tools** | ripgrep/glob/find/brush in Rust; no fork/exec | CC shells out | Perf gap, not capability gap |
| **Subagents (first-class)** | `task` — worktree isolation; typed schema results; `irc` inter-agent prose | Agent tool + skills; no typed schema from subagents; no inter-agent comms | Partial |
| **Hindsight memory** | SQLite; project-scoped; retain/recall/reflect | Auto-memory (MEMORY.md) — manual, cross-project, no semantic search | Partial |
| **Web search** | 14 providers + specialized handlers (npm, arxiv, NVD/OSV CVEs, forums, code hosts) | Firecrawl MCP — rich but single-provider | Partial |
| **40+ providers** | Native; fallback chains; path-scoped model overrides; round-robin credentials | Pi council for cross-vendor; CC locked to Anthropic natively | Partial |
| **Conflict resolution** | `conflict://N` scheme; write `@theirs/@ours/@base`; atomic | Manual | Gap |
| **Preview/accept workflow** | `ast_edit` stages + `resolve` commits atomically | None | Gap |
| **Snapcompact** | Bitmap-frame context compression | None | Gap |
| **Internal `://` schemes** | `pr://`, `issue://`, `agent://`, `skill://` — all via `read` | GitHub MCP (separate surface); no unified scheme | Gap |
| **Browser** | Built-in Puppeteer/CDP; stealth on by default; can drive Electron apps (Slack, etc.) | Playwright MCP | Roughly equivalent |
| **Code review** | `/review` — P0-P3 ranked findings; per-dimension parallel subagents | `/code-review` skill — roughly equivalent output | Roughly equivalent |
| **GitHub integration** | `github` tool + `pr://`/`issue://` via `read` | GitHub MCP | Roughly equivalent |
| **Session management** | Named sessions; `--resume` flag; tab completion on sessions | CC sessions; no named resume from CLI | Roughly equivalent |
| **ACP (Zed editor)** | Native; buffer access, write through editor save path | None (CC has VS Code/JetBrains via extension) | Gap if you use Zed |
| **Image gen / TTS** | `generate_image` (Gemini/GPT/Grok), `tts` (xAI Grok Voice) | None | Gap |
| **MCP ecosystem** | Inherits existing MCP configs; omp-native tools cover most use cases | Deep MCP: Figma, context7, qmd, Firecrawl, Playwright, GitHub | **We win** |
| **Skill/knowledge system** | Extensions (TS modules); self-modifying (agent writes extensions on demand) | Superpowers skills + qmd wiki + MEMORY.md — more structured | **We win** |
| **Orchestration patterns** | `task` + `irc` + swarm extension | ralph-loop, Agent tool, workflow scripts, agent-orchestration skill | Roughly equivalent |
| **Cross-vendor council** | Enabled via 40+ providers; no formal pattern | Formal multi-vendor adversarial review via Pi AI — structured pattern | **We win on pattern** |
| **Config inheritance** | Auto-inherits from `.claude`/`.cursor`/`.codex`/`.cline`/`.github/copilot` etc. | CC reads `.claude` only | omp wins for polyglot teams |

---

## Hard Gaps — Closing Cost

These require native implementation. Can't be closed with MCP servers or shell hooks:

| Gap | Effort to close | Workaround today |
|---|---|---|
| Hashline editing | High — needs Rust or tight JS patch library | Live with string-match failures; re-read and retry |
| LSP into writes | High — needs LSP server integration in CC CLI | Manual: run `tsc --watch`, paste errors back |
| DAP debugger | High — needs DAP protocol impl | lldb/gdb manually in bash; no agent-native stepping |
| Stream rules (TTSR) | Very high — needs CC core access | PreToolUse hook (between turns, not mid-stream) |
| Eval kernels | Medium — could build via MCP + persistent subprocess | bash + state in files; no tool re-entry from kernel |

---

## Our Wins — What omp Doesn't Match

| Area | Our Advantage |
|---|---|
| **Wiki/knowledge base** | qmd (BM25 + vector search over 1984 docs); JIT context loading; cross-session knowledge accumulation |
| **Skill system depth** | Superpowers plugin: ~30 skills with trigger table, caveman mode, output styles, learning mode |
| **Orchestration patterns** | ralph-loop (structured long-horizon); Agent tool (model-tiered routing); workflow scripts |
| **Cross-vendor council** | Formal adversarial review via Pi AI; multi-vendor consensus documented in [[concepts/multi-vendor-adversarial-review]] |
| **MCP ecosystem** | Figma (design sync), context7 (live docs), qmd (wiki), Firecrawl (web), GitHub, Playwright, Sentry |
| **Per-session memory targeting** | MEMORY.md types (user/feedback/project/reference) with deliberate curation; omp Hindsight is fact-bag |
| **Security/audit tooling** | AgentShield, security-auditor agent, indirect-prompt-injection patterns |

---

## Migration Considerations

omp inherits existing `.claude` config, rules, and MCP servers on first run. Switching primary agent from CC to omp would preserve:
- MCP server connections (Figma, context7, Firecrawl, etc.)
- AGENTS.md / CLAUDE.md rules
- Existing skills (as TS extensions or SKILL.md files)

What would be lost immediately:
- CC-specific hook system (PreToolUse/PostToolUse/Stop) — omp has extension hooks but different surface
- CC permission model (allowlist/denylist settings.json) — omp is YOLO by default (use `srt` for sandboxing)
- Claude oauth session (CC uses device auth; omp uses its own oauth per provider)

---

## Related Pages

- [[entities/omp]] — full omp capability reference
- [[entities/pi-agent]] — upstream minimal harness; council/adversarial review layer
- [[comparisons/claude-code-vs-opencode-plugins]] — adjacent comparison
- [[concepts/agent-harness]] — harness primitives framing
- [[syntheses/lean-agentic-workflow]] — our current full-stack workflow
