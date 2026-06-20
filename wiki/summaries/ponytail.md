---
title: "Ponytail"
type: summary
tags: [agent-skills, ai-coding, yagni, code-quality, opencode, claude-code, codex]
sources:
  - "DietrichGebertponytail Makes your AI agent think like the laziest senior dev in the room. The best code is the code you never wrote..md"
created: 2026-06-20
updated: 2026-06-20
---

# Ponytail

Ponytail is an agent skill/plugin that steers coding agents toward minimum necessary implementation: skip what does not need to exist, prefer stdlib/native platform/installed dependencies, use one line when sufficient, and only then write the smallest custom code that works.

It is best understood as a concrete anti-overengineering rule layer for [[entities/ai-coding-agents]], not as a model replacement.

## Core ladder

Before writing code, the agent checks:

1. Does this need to exist? If not, skip it.
2. Does the standard library already do it?
3. Does the native platform already do it?
4. Does an installed dependency already do it?
5. Can it be one line?
6. Only then, write the minimum custom implementation that works.

The source emphasizes "lazy, not negligent": trust-boundary validation, data-loss handling, security, and accessibility are not supposed to be removed.

## Claimed results

Ponytail's README claims, against a no-skill baseline in headless Claude Code sessions on `tiangolo/full-stack-fastapi-template`, 12 feature tasks, n=4, Haiku 4.5:

| Metric | Claimed delta vs no-skill baseline |
|---|---|
| LOC | -54% |
| tokens | -22% |
| cost | -20% |
| time | -27% |
| safety | 100% |

These numbers are self-reported by the project and not independently verified. Treat them as a benchmark claim with useful methodology detail, not established fact.

Older single-shot numbers claimed 80-94% less code, but the README itself now qualifies that result as partly inflated by a conversational baseline that padded answers with prose and options.

## Supported hosts

Ponytail ships adapters or rule files for many coding-agent hosts:

- Claude Code plugin marketplace
- Codex plugin marketplace and desktop app
- GitHub Copilot CLI
- [[entities/pi-agent]] via `pi install git:github.com/DietrichGebert/ponytail`
- [[entities/opencode]] via local plugin path in `opencode.json`
- [[entities/gemini-cli]] / Antigravity extension
- CodeWhale, OpenClaw, Cursor, Windsurf, Cline, Aider, Kiro, Zed, GitHub Copilot editor through copied rule files

Commands include `/ponytail [lite|full|ultra|off]`, `/ponytail-review`, `/ponytail-audit`, `/ponytail-debt`, `/ponytail-gain`, and `/ponytail-help` where the host supports skills/commands.

## Fit for our stack

Best target in our [[concepts/model-task-routing]] setup:

- Implementation agents: apply the ladder before code generation, especially for [[entities/opencode-go]] Kimi implementation paths.
- Review agents: add Ponytail-style overbuild review alongside correctness/security review.
- Plan writer: include explicit "do not build" boundaries in plan slices.
- Fast agents: useful for rote edits, but likely smaller impact because those tasks are already bounded.

Do not turn this into global "fewest tokens" pressure. The source explicitly says the rule is not token minimization; lower cost and latency are side effects only when the model follows the minimality ladder without spending extra reasoning tokens.

## Caveats

- Benchmark claims are self-reported by the project.
- Ultra mode can be risky if interpreted as code golf; keep safety checks explicit.
- Minimal code still needs verification. Ponytail reduces scope pressure but does not replace tests, typecheck, security review, or human review.
- Models that deliberate heavily over each ladder rung may spend more thinking tokens even if they write fewer code tokens.

## Wiki connections

- [[entities/ponytail]] - entity page for the repo and host adapters.
- [[concepts/ai-specific-pitfalls]] - over-engineering and defensive overreach are AI-specific code risks.
- [[patterns/principles]] - YAGNI and KISS are the underlying design principles.
- [[patterns/code-quality]] - minimum code still needs naming, function discipline, and clear structure.
- [[concepts/agent-skills]] - Ponytail is a portable skill/ruleset pattern.
- [[concepts/model-task-routing]] - apply behavior constraints after selecting the model.
