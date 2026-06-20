---
title: "Ponytail"
type: entity
tags: [agent-skill, ai-coding, yagni, opencode, claude-code, codex, pi-agent]
sources:
  - "DietrichGebertponytail Makes your AI agent think like the laziest senior dev in the room. The best code is the code you never wrote..md"
created: 2026-06-20
updated: 2026-06-20
---

# Ponytail

Ponytail is Dietrich Gebert's cross-agent coding skill/plugin for reducing agent overbuild. Its tagline is "the best code is the code you never wrote." The practical mechanism is a minimality ladder: do not build unnecessary work; prefer stdlib, native platform features, and existing dependencies before writing custom code.

## What it is

- A ruleset/skill/plugin for agent harnesses.
- A review lens for unnecessary abstractions and avoidable code.
- A portable adapter set across Claude Code, Codex, OpenCode, Gemini/Antigravity, Pi, Copilot CLI, OpenClaw, Cursor, Windsurf, Cline, Aider, Kiro, Zed, and CodeWhale.

## What it is not

- Not a model router.
- Not a replacement for tests or review.
- Not "code golf" if used correctly: safety, validation, security, data-loss handling, and accessibility remain required.

## Host integration notes

For [[entities/opencode]], the README describes running OpenCode from a Ponytail checkout and adding:

```json
{ "plugin": ["./.opencode/plugins/ponytail.mjs"] }
```

The plugin injects rules every turn and adds `/ponytail` commands. OpenCode also auto-loads Ponytail's `AGENTS.md` when run from the repo root, so the rules can hold even without the plugin, but mode switching requires the plugin/commands.

For [[entities/pi-agent]], the install path is:

```bash
pi install git:github.com/DietrichGebert/ponytail
```

For Claude Code and Codex, the source describes plugin marketplace installation plus lifecycle hooks. Node.js must be available in the non-interactive shell path for those hooks; otherwise the skills still work but always-on activation may stay quiet.

## Commands

| Command | Purpose |
|---|---|
| `/ponytail [lite|full|ultra|off]` | Set intensity or report current level |
| `/ponytail-review` | Review current diff for over-engineering and return a delete list |
| `/ponytail-audit` | Audit the whole repo for over-engineering |
| `/ponytail-debt` | Collect deferred `ponytail:` shortcuts into a ledger |
| `/ponytail-gain` | Show measured impact scoreboard from the project benchmark |
| `/ponytail-help` | Quick command reference |

## Adoption stance

Good candidate for our implementation and review agents, especially where [[concepts/ai-specific-pitfalls]] warns about over-engineering, defensive overreach, and cargo-cult patterns.

Adopt as an optional behavior constraint first, not as a global mandate. Start with implementation/review roles and keep verification gates unchanged.

## Related

- [[summaries/ponytail]] - source summary and claimed results.
- [[concepts/model-task-routing]] - model selection layer that Ponytail complements.
- [[patterns/principles]] - YAGNI/KISS basis.
- [[concepts/agent-skills]] - portable skill mechanism.
