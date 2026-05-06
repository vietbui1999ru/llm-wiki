---
title: "Cursor Cloud Agents"
type: summary
tags: [cursor, cloud-agents, background-agents, parallel-agents]
sources:
  - "Cloud Agents  Cursor Docs.md"
created: 2026-05-07
updated: 2026-05-07
---

# Cursor Cloud Agents

Cursor's hosted background agent offering. Formerly called "Background Agents." Runs in isolated cloud VMs, not on local machine.

---

## Key Properties

**Parallel execution**: run unlimited agents simultaneously without requiring local machine connection.

**Full VM environment**: agents can build, test, and interact with modified software; computer use for desktop/browser control.

**GitHub/GitLab workflow**: clones repo from remote, works on separate branch, pushes changes as merge-ready PR. Requires read-write access to repo and dependent repos/submodules.

**Model**: curated selection, always runs in Max Mode (cannot disable).

**MCP support**: configured team MCP servers (HTTP + stdio, OAuth).

---

## Access Points

- **Cursor Web**: `cursor.com/agents` — start and manage from any device
- **Cursor Desktop**: Cloud dropdown under agent input
- **Slack**: `@cursor` command
- **GitHub**: `@cursor` comment on PR or issue
- **Linear**: `@cursor` command
- **API**: programmatic access

PWA available for mobile (iOS Safari, Android Chrome).

---

## Key Features

**Artifacts and verification**:
- Screenshots, videos, logs showing what changed and how agent verified its work
- Remote desktop control: user can take control of agent's desktop to test software without checking out branch locally, then release back to agent

**Hooks**: runs `.cursor/hooks.json` (project hooks); Enterprise runs team + managed hooks.

**Plan approval**: can require teammate to plan before implementing.

---

## Comparison with CC Agent Teams

| | CC Agent Teams | Cursor Cloud Agents |
|---|---|---|
| **Host** | Local machine | Cloud VM |
| **Isolation** | Session-based | VM per agent |
| **Parallel** | Limited by local resources | Unlimited |
| **Requires online** | No (local) | Yes |
| **Direct agent interaction** | Yes (Shift+Down) | Yes (remote desktop) |
| **Branch strategy** | Worktrees | Separate branch → PR |
| **Status** | Experimental | GA |

---

## Related Pages

- [[summaries/cc-agent-teams]] — CC's experimental multi-agent system
- [[summaries/cursor-rules-background-agents]] — Cursor .cursor/rules + background agent config
- [[comparisons/cc-to-cross-platform-migration]] — cross-platform migration matrix
- [[concepts/worktree-isolation]] — CC's approach to agent filesystem isolation
