---
title: "Everything Claude Code (ECC)"
type: entity
tags: [claude-code, agent-harness, plugin, cross-platform, open-source]
sources:
  - "vietbui1999rueverything-claude-code The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and beyond..md"
created: 2026-05-19
updated: 2026-05-19
---

# Everything Claude Code (ECC)

Agent harness performance system by Affaan Mustafa (@affaanmustafa). MIT licensed. Claude Code plugin + npm package + manual install. Anthropic Hackathon winner (Feb 2026).

- GitHub: `affaan-m/everything-claude-code`
- Plugin ID: `ecc@ecc`
- npm: `ecc-universal`

---

## What It Is

A layered plugin for Claude Code (and 8 other harnesses) that adds: 60 agents, 232 skills, structured rules, hook-based automations, continuous learning, and security scanning. Framed explicitly as a "harness performance system" — the claim is that harness quality determines output quality as much as model quality does.

---

## Install Paths

**Plugin path (recommended for most users):**
```bash
/plugin marketplace add https://github.com/affaan-m/everything-claude-code
/plugin install ecc@ecc
# Then manually copy rules (plugins can't distribute rules):
mkdir -p ~/.claude/rules/ecc
cp -r everything-claude-code/rules/common ~/.claude/rules/ecc/
cp -r everything-claude-code/rules/typescript ~/.claude/rules/ecc/  # pick your stack
```

**Manual install (fallback):**
```bash
./install.sh --profile full   # or: npx ecc-install --profile full
```

**Do not stack methods** — plugin + manual full install causes duplicates.

**Selective (minimal):**
```bash
./install.sh --profile minimal --target claude  # rules + agents only, no hooks
```

---

## Cross-Harness Support Matrix

| Harness | Mechanism | Hook parity | Agent parity |
|---|---|---|---|
| Claude Code | Native plugin | 8 events | 60 agents |
| Cursor | DRY adapter (transforms to CC format) | 15 events | 48 agents (prefixed `ecc-*`) |
| OpenCode | `ecc-universal` npm plugin | 11 events (more than CC) | 12 agents |
| Codex (app + CLI) | AGENTS.md + `.codex/` | None (instruction-based) | Shared via AGENTS.md |
| GitHub Copilot | `.github/copilot-instructions.md` + prompts | None | None |
| Zed | `.zed/` adapter | Not available | Project-local |
| Antigravity | `.agent/` adapter | Per Antigravity spec | Shared |
| JoyCode/CodeBuddy | Project-local selective install | Per CodeBuddy spec | Shared |
| Qwen CLI | Home-directory adapter | Per Qwen spec | Shared |

**DRY adapter pattern**: Cursor's `adapter.js` transforms Cursor's stdin JSON to Claude Code's format, allowing the same `scripts/hooks/*.js` to run on both harnesses without duplication. OpenCode's plugin hook system has more events than Claude Code (11 vs 8 native types).

---

## Component Summary

| Component | Count | Surface |
|---|---|---|
| Agents | 60 | `agents/*.md` |
| Skills | 232 | `skills/` |
| Commands (maintained) | 75 | `commands/` |
| Rules (language packs) | 7 dirs | `rules/common`, `typescript`, `python`, `golang`, `swift`, `php`, `arkts` |
| Hook scripts | 20+ | `scripts/hooks/`, `hooks/hooks.json` |
| Context injection modes | 3 | `contexts/dev.md`, `review.md`, `research.md` |
| CLAUDE.md examples | 7 | `examples/` |

All counts self-reported from README (unverified independently).

---

## Key Skills

| Skill | Purpose |
|---|---|
| `tdd-workflow` | Red-green-improve cycle, 80%+ coverage |
| `eval-harness` | Eval-driven development, checkpoint/continuous modes |
| `verification-loop` | Build, test, lint, typecheck, security |
| `strategic-compact` | When/when-not to compact context |
| `continuous-learning-v2` | Instinct-based learning with confidence scoring |
| `security-scan` | Runs AgentShield from within Claude Code |
| `search-first` | Research-before-coding workflow |
| `iterative-retrieval` | Progressive context refinement for subagents |
| `skill-create` | Generate skills from git history |

---

## Hook Runtime Controls

```bash
export ECC_HOOK_PROFILE=minimal|standard|strict  # enforcement level
export ECC_DISABLED_HOOKS="pre:bash:tmux-reminder"  # comma-separated IDs
export ECC_SESSION_START_MAX_CHARS=4000  # cap context injection (default: 8000)
export ECC_SESSION_START_CONTEXT=off    # disable entirely for local/low-context
```

---

## ECC 2.0 (Alpha)

Rust control plane in `ecc2/` — builds locally, exposes `dashboard`, `start`, `sessions`, `status`, `stop`, `resume`, `daemon`. Not a general release; alpha quality. Tkinter desktop dashboard also available via `npm run dashboard` or `python3 ecc_dashboard.py`.

---

## Related Wiki Pages

- [[summaries/everything-claude-code]] — full feature summary and token optimization settings
- [[entities/agentshield]] — ECC's security scanning component
- [[concepts/instinct-clustering]] — continuous learning v2 pattern
- [[comparisons/cc-to-cross-platform-migration]] — cross-harness migration matrix
- [[concepts/agent-harness]] — the broader harness concept
- [[concepts/context-compression]] — strategic compaction (ECC's `strategic-compact` skill)
