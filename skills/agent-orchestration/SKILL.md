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
- No custom agent roster is installed. Route with the harness's built-in roles and an explicit `model` per [[concepts/model-tier-routing]]
- Review architecture before major structure changes and non-trivial implementation after it, in the main session; use a dedicated review only for risky changes
- Keep small, fully known edits in the main session: a handoff that costs as much as the edit is not a saving ([[concepts/subagent-cost-model]])
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
