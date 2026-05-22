---
name: "agent-orchestration"
description: "Choose between direct work, skills, subagents, and council. Use when shaping multi-agent workflow or delegation in this repo."
---

# Agent Orchestration

Concise decision aid for this repo.

## Primitive choice

- Reusable workflow knowledge -> skill
- Specialist isolated judgment -> subagent
- Cross-vendor durable decision -> council
- Simple bounded task -> direct execution

## Repo defaults

- Load `$wiki-context` before technical design
- Use `agent-delegator` for routing
- Use `architecture-reviewer` before major structure changes
- Use `code-reviewer` after non-trivial implementation
- Use `$council` for architecture and security tradeoffs

## Stop conditions

Do not spawn extra structure when:

- one agent can finish cleanly
- task is routine
- no genuine decision tradeoff exists

## Cite

Prefer wiki support:

- `[[concepts/agent-harness]]`
- `[[concepts/agent-skills]]`
- `[[concepts/agent-subagents]]`
- `[[concepts/agent-teams]]`
- `[[syntheses/agent-primitive-selection]]`
