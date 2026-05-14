---
title: "SpotMe"
type: entity
tags: [agentic-coding, deliberate-practice, opencode, skill, learning]
sources: ["wtfzambospotme Gym mode for agentic coding. OpenCode plugin that scaffolds exercises and reviews your work. Keep your edge..md"]
created: 2026-05-13
updated: 2026-05-13
---

# SpotMe

OpenCode plugin (and portable SKILL.md) that introduces "gym mode" for agentic coding sessions. Instead of completing 100% of implementation, the agent scaffolds a logical unit, hands it off, watches the user implement it, then reviews and resumes.

Motivation: research shows heavy AI delegation reduces critical thinking. SpotMe forces deliberate practice within the AI-assisted workflow.

## How it works

Every N code-writing actions (configurable), the agent scaffolds the next unit with a `# SPOTME: ...` marker instead of completing it. The user implements the marked section in their editor, then calls `/spotme:done` to trigger review and resume.

## Commands

| Command | Description |
|---|---|
| `/spotme:on [lite\|medium\|hard] [--every N]` | Enable gym mode (default: medium, every 2) |
| `/spotme:off` | Disable — agent writes normally |
| `/spotme:status` | Show current state |
| `/spotme:rep` | Request an on-demand exercise |
| `/spotme:done` | Submit implementation for review |
| `/spotme:hint` | Get one targeted hint |
| `/spotme:solve` | Concede — agent completes the exercise |
| `/spotme:skip` | Skip this exercise, no note |

## Difficulty levels

| Level | Agent provides | User writes |
|---|---|---|
| `lite` | Signature + docstring + structure | Just the body |
| `medium` | Signature + `# SPOTME:` spec comment | All logic |
| `hard` | Plain English spec comment only | Everything |

## Installation

- **OpenCode**: add `"plugin": ["spotme"]` to `opencode.json`
- **Skill-only (CC and others)**: copy `SKILL.md` into harness skills directory — commands work, but counter-based auto-trigger won't fire

## Design philosophy

The agent as spotter: it sets up the lift, stands by while you push, catches you if you call for help. The work is yours.

The counter-based trigger (`--every N`) is the core OpenCode-specific feature. In CC or other harnesses using the SKILL.md only, the user manually calls `/spotme:rep` to request exercises — same discipline, no automation.

## Related Pages

- [[concepts/agent-skills]] — skill architecture and SKILL.md format
- [[entities/opencode]] — OpenCode plugin system
- [[concepts/ai-specific-pitfalls]] — cognitive atrophy from over-delegation is one named risk
- [[summaries/hn-junior-devs-and-ai]] — community discussion of AI dependency and skill degradation
