---
title: "Everything Claude Code (ECC)"
type: summary
tags: [claude-code, agent-harness, skills, hooks, continuous-learning, security, cross-platform, token-optimization]
sources:
  - "vietbui1999rueverything-claude-code The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and beyond..md"
created: 2026-05-19
updated: 2026-05-19
---

# Everything Claude Code (ECC)

A battle-tested agent harness performance system built on top of Claude Code, authored by Affaan Mustafa over 10+ months of production use. Anthropic Hackathon winner (Cerebral Valley x Anthropic, Feb 2026). Available as a CC plugin, npm package, and manual install.

> "Not just configs. A complete system: skills, instincts, memory optimization, continuous learning, security scanning, and research-first development."

---

## The Harness-as-Performance-System Frame

ECC's core insight: model quality is only one input to agent output quality. The harness — hooks, rules, skills, memory — determines how much of the model's capability is actually applied to your task. A weak harness wastes strong models; a strong harness extracts more from cheaper models.

This reframes the question from "which model?" to "how well is the model steered?" Hook enforcement, structured compaction, runtime controls, and continuous learning are not convenience features — they are the performance system.

---

## Architecture

```
everything-claude-code/
├── agents/           # 60 specialized subagents for delegation
├── skills/           # 232 workflow definitions (primary surface)
├── commands/         # Maintained slash-entry compatibility
├── legacy-command-shims/  # Retired shims (/tdd, /eval, /verify)
├── rules/            # Always-follow guidelines (common + language dirs)
├── hooks/            # Trigger-based automations (hooks.json)
├── scripts/          # Cross-platform Node.js hook implementations
├── contexts/         # Dynamic system prompt injection (dev/review/research)
├── examples/         # Real-world CLAUDE.md templates (SaaS, Go, Django, Rust)
└── mcp-configs/      # MCP server configurations
```

60 agents, 232 skills, 75 legacy command shims (all counts claimed from README, unverified independently).

---

## Key Components

### Continuous Learning v2 — Instinct-Based Learning

The primary learning mechanism. See [[concepts/instinct-clustering]] for the full pattern.

**ECC v1 (Stop-hook)**: At session end, `evaluate-session.js` extracts patterns → writes to `skills/learned/`. Risk: duplicate accumulation without triage.

**ECC v2 (instinct-based)**:
- `/instinct-status` — view learned instincts with confidence scores
- `/instinct-import <file>` — import instincts from others
- `/instinct-export` — share your instincts
- `/evolve` — cluster related instincts into reusable skills
- `/prune` — delete expired pending instincts (30-day TTL)
- `/learn-eval` — extract + evaluate patterns before saving (prevents low-quality accumulation)

Confidence scoring addresses the duplicate/low-quality skill problem in v1.

### Hook Runtime Controls

Runtime-gated enforcement without editing hook files:

```bash
# Strictness profile (default: standard)
export ECC_HOOK_PROFILE=minimal|standard|strict

# Disable specific hooks by ID
export ECC_DISABLED_HOOKS="pre:bash:tmux-reminder,post:edit:typecheck"

# Cap or disable SessionStart context injection
export ECC_SESSION_START_MAX_CHARS=4000   # default: 8000 chars
export ECC_SESSION_START_CONTEXT=off      # disable entirely (local models, low-context)
```

`ECC_HOOK_PROFILE=minimal` intentionally excludes `hooks-runtime` — useful when hooks feel too global or you only want rules/agents/skills.

### Context Injection Modes

Three dynamic system prompt contexts in `contexts/`:
- `contexts/dev.md` — development mode: full enforcement, typecheck, format
- `contexts/review.md` — code review mode: read-only, analysis focus
- `contexts/research.md` — exploration mode: reduced enforcement, broader search

Relates to [[concepts/agent-context-instructions]] — ECC's implementation of mode-aware context.

### Skill Creator

Generate skills from your repository's git history without external services:

```
/skill-create                    # analyze current repo, generate SKILL.md files
/skill-create --instincts        # also generate instincts for continuous-learning-v2
```

For large repos (10k+ commits): ECC Tools GitHub App provides auto-PR and team sharing.

### Rules Architecture

```
rules/
  common/      # Language-agnostic (always install)
  typescript/  # TS/JS specific
  python/      # Python specific
  golang/      # Go specific
  swift/       # Swift specific
  php/         # PHP specific
  arkts/       # HarmonyOS / ArkTS
```

Key design: copy the whole language directory, not individual files, to preserve relative references.

---

## Token Optimization Settings

Recommended `~/.claude/settings.json`:

```json
{
  "model": "sonnet",
  "env": {
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50",
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"
  }
}
```

| Setting | Default | Recommended | Impact |
|---|---|---|---|
| `model` | opus | **sonnet** | ~60% cost reduction (claimed) |
| `MAX_THINKING_TOKENS` | 31,999 | **10,000** | ~70% reduction in hidden thinking cost (claimed) |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 95 | **50** | Earlier compaction → better quality in long sessions |
| `CLAUDE_CODE_SUBAGENT_MODEL` | inherits | **haiku** | Subagents use cheaper model |

All impact numbers claimed from ECC README; not independently verified. The pattern (compact earlier, cap thinking tokens, use smaller model for subagents) aligns with community consensus on token efficiency.

**MCP context cost**: ECC reports that too many active MCP servers can reduce the effective 200K context window to ~70K (claimed, unverified). Recommended cap: under 10 MCPs, under 80 active tools. Disable unused servers via `/mcp` in Claude Code (written to `~/.claude.json`).

### Strategic Compaction

ECC's `strategic-compact` skill adds explicit when/when-not guidance on top of the compaction system:

**Compact at:**
- After research/exploration, before implementation
- After completing a milestone, before starting the next
- After a failed approach, before trying a new one

**Do not compact mid-implementation** — you'll lose variable names, file paths, partial state.

See [[concepts/context-compression]] for the full strategy comparison.

---

## AgentShield — Security Scanner

See [[entities/agentshield]] for the full entry.

Built at the Feb 2026 hackathon. Scans CC configurations (CLAUDE.md, hooks, MCP configs, agents, skills, settings.json) for vulnerabilities across 5 categories:
- Secrets detection (14 patterns)
- Permission auditing
- Hook injection analysis
- MCP server risk profiling
- Agent config review

Runs a 3-agent red-team/blue-team/auditor Opus pipeline for deep analysis. 1282 tests, 102 rules (claimed). Use `/security-scan` in Claude Code to run it.

---

## Cross-Harness Support

ECC targets 9+ harnesses. See [[entities/everything-claude-code]] for the full cross-harness matrix.

| Harness | Status |
|---|---|
| Claude Code | Native — primary target |
| Cursor | DRY adapter pattern: Cursor hooks delegate to same Node.js scripts as CC |
| OpenCode | Full plugin support (`ecc-universal` npm package) |
| Codex | First-class (app + CLI); AGENTS.md + .codex/ |
| GitHub Copilot | Instruction + prompt layer only (no hook/agent API) |
| Zed | `.zed/` adapter, project-local |
| Antigravity | `.agent/` adapter |
| JoyCode/CodeBuddy | Project-local selective install |
| Qwen CLI | Home-directory adapter |

**DRY adapter pattern (Cursor)**: Cursor has more hook events (15 types vs CC's 8). ECC's `adapter.js` transforms Cursor's stdin JSON to CC's format, letting the same `scripts/hooks/*.js` run on both without duplication.

---

## Limitations / Caveats

- **Do not stack install methods** — plugin install + manual `install.sh --profile full` causes duplicate skills and hook conflicts. Pick one path.
- **Rules not distributable via plugins** — CC plugin system cannot distribute `rules/` automatically (upstream limitation). Must copy manually to `~/.claude/rules/ecc/`.
- **Hooks auto-loading** — CC v2.1+ auto-loads `hooks/hooks.json` from plugins; do NOT add a `"hooks"` field to `plugin.json` (triggers duplicate detection error).
- **`multi-*` commands require `ccg-workflow` runtime** separately — not covered by base install.
- **ECC 2.0 Rust control plane** (`ecc2/`) is alpha — builds locally but not a general release.
- Star/fork counts (182K+/28K+) and component counts (60 agents, 232 skills) are self-reported from README; independently unverified.

---

## Related Wiki Pages

- [[concepts/instinct-clustering]] — the continuous learning pattern ECC implements (upgraded from documented-not-adopted)
- [[entities/agentshield]] — security scanner for CC configs
- [[entities/everything-claude-code]] — entity entry (install paths, cross-harness matrix)
- [[concepts/context-compression]] — strategic compaction decision guide
- [[concepts/context-window]] — MCP context cost impact
- [[comparisons/cc-to-cross-platform-migration]] — updated with ECC's cross-harness data
- [[concepts/agent-skills]] — skill architecture that ECC builds on
- [[concepts/agent-harness]] — the broader harness concept ECC instantiates
