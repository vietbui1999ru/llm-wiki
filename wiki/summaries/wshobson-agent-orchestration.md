---
title: "wshobson/agents: Production Agent Orchestration Marketplace"
type: summary
tags: [agent-engineering, plugins, orchestration, skills, three-tier-model, claude-code]
sources:
  - "wshobsonagents Intelligent automation and multi-agent orchestration for Claude Code.md"
created: 2026-04-26
updated: 2026-04-26
---

# wshobson/agents: Production Agent Orchestration Marketplace

A production-scale Claude Code agent ecosystem: 184 specialized agents (per repo header; tier breakdown sums to 153 — 31 agents unaccounted, discrepancy unresolved), 78 focused plugins, 150 skills, 16 orchestrators, 98 commands. Primary reference for how to structure a large multi-agent system using Claude Code's plugin architecture.

Source repo: `wshobson/agents` (add via `/plugin marketplace add wshobson/agents`)

## Key Design Principles

**Single responsibility per plugin.** Average 3.6 components per plugin. Each plugin loads only its specific agents, commands, and skills — no unnecessary resources in context.

**Progressive disclosure.** Skills load knowledge only when activated. Installing `python-development` loads 3 agents + 1 tool + 16 skills (~1,000 tokens), not the entire marketplace.

**100% agent coverage.** All 184 agents accessible; organized into 25 categories, 1–10 plugins each.

## Three-Tier Model Strategy

| Tier | Model | Agent count | Use case |
|---|---|---|---|
| 1 | Opus 4.7 | 42 | Architecture, security, ALL code review, production coding |
| 2 | Inherit | 42 | Complex tasks — user chooses; falls back to Sonnet 4.6 |
| 3 | Sonnet | 51 | Support with intelligence: docs, testing, debugging |
| 4 | Haiku | 18 | Fast operational: SEO, deployment, simple docs |

Orchestration pipeline: `Opus (architecture) → Sonnet (development) → Haiku (deployment)`

Opus 4.7 achieves 65% fewer tokens on complex tasks — often offsets higher rate.

## Notable Plugins

**agent-teams**: 7 team presets (review, debug, feature, fullstack, research, security, migration). Parallel code review with role-specific reviewers. Hypothesis-driven debugging.

**conductor**: Context → Spec → Plan → Implement workflow. Track-based development, TDD, semantic revert, state persistence across sessions.

**full-stack-orchestration**: Coordinates 7+ agents: backend-architect → database-architect → frontend-developer → test-automator → security-auditor → deployment-engineer → observability-engineer.

**security-scanning**: SAST + dependency scanning + code review. Multi-agent security assessment with OWASP, auth, dependencies, secrets.

**comprehensive-review**: architect-review + code-reviewer + security-auditor running in parallel.

## Plugin Structure

```
plugins/
└── python-development/
    ├── agents/          # 3 Python expert subagents
    ├── commands/        # Scaffolding tools
    └── skills/          # 5 specialized skills
```

All agents defined as markdown files with YAML frontmatter (Claude Code standard format).

## PluginEval Quality Framework

Three-layer evaluation:
1. **Static analysis** — instant, structural checks
2. **LLM judge** — semantic quality scoring
3. **Monte Carlo simulation** — statistical robustness

10 quality dimensions: triggering accuracy, orchestration fitness, output quality, scope calibration, progressive disclosure, token efficiency, robustness, structural completeness, code template quality, ecosystem coherence.

Grades: Platinum (★★★★★) → Bronze (★★).

Anti-patterns detected: `OVER_CONSTRAINED`, `EMPTY_DESCRIPTION`, `MISSING_TRIGGER`, `BLOATED_SKILL`, `ORPHAN_REFERENCE`, `DEAD_CROSS_REF`.

## Relationship to This Wiki

The wshobson architecture validates and extends the harness principles in [[concepts/agent-harness]]:
- Granular plugins = principle of least privilege for context loading
- Progressive disclosure = skills/context management strategy
- Three-tier routing = model tiering (Opus/Sonnet/Haiku) matches our agent-delegator pattern
- Security-scanning plugin = dedicated security-auditor agent

## Gaps vs Our Agent Setup (updated 2026-04-26)

1. ~~No dedicated security-auditor agent~~ — **Resolved**: `security-auditor.md` (Opus, read-only, OWASP depth, `security-patterns` skill preloaded)
2. ~~No visual verification agent~~ — **Resolved**: `visual-verifier.md` (Sonnet, Playwright DOM audit + screenshot gate)
3. ~~No full-stack orchestrator~~ — **Resolved**: `agent-delegator.md` manages sequential/parallel routing and security review loops
4. No PluginEval equivalent for quality-gating agent output — still a gap; no automated quality scoring for agent-generated artifacts
