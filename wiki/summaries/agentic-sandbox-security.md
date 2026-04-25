---
title: "Practical Security Guidance for Sandboxing Agentic Workflows"
type: summary
tags: [security, agents, sandboxing, prompt-injection]
sources: ["Practical Security Guidance for Sandboxing Agentic Workflows and Managing Execution Risk.md"]
created: 2026-04-22
updated: 2026-04-22
---

# Practical Security Guidance for Sandboxing Agentic Workflows

Source: NVIDIA AI Red Team blog post.

## Core threat

AI coding agents run with the same OS permissions as the developer. They execute arbitrary code by design (to observe test results, run scripts). This makes the **attack surface equivalent to a computer use agent**.

The primary attack is [[concepts/indirect-prompt-injection]]: adversarial content embedded in repos, PRs, git history, `.cursorrules`, `CLAUDE.md`, or MCP responses that causes the agent to take attacker-directed actions.

## Why application-level controls are insufficient

Agentic tools can intercept tool calls before execution, but once control passes to a subprocess, the app has no visibility into that process. Attackers use indirection — calling restricted operations through approved tools. **OS-level controls** (macOS Seatbelt, Linux Bubblewrap) operate beneath the application layer and cover every spawned process regardless of how it started.

## Mandatory controls

These three are considered non-negotiable by the NVIDIA AI Red Team:

| Control | What it blocks |
|---|---|
| Network egress to arbitrary sites | Data exfiltration, reverse shells, remote access |
| File writes outside workspace | Persistence via `~/.zshrc`, backdoored binaries in `~/.local/bin`, redirect via `~/.gitconfig` |
| Writes to any agent config file | Poisoning hooks, MCP configs, skills, `CLAUDE.md`, `copilot-instructions.md` |

Note: config file protection applies even within the workspace, and **no user approval should override it**.

## Recommended controls

| Control | Threat mitigated |
|---|---|
| Block reads outside workspace | Host enumeration, secret exfiltration (`~/.ssh`, `.env`) |
| Sandbox entire IDE + hooks/MCP/skills | Hooks often run outside sandbox; unsandboxed paths enable bypass |
| Virtualization (microVM, Kata, full VM) | Kernel exploits from arbitrary code execution |
| Per-action approval, never cached | Cached approvals enable future adversarial reuse of prior legitimate permission |
| Secret injection (not inheritance) | Limits blast radius — agent gets only task-scoped credentials |
| Sandbox lifecycle management | Prevents accumulation of stale secrets, IP, exploitable artifacts |

## Tiered control implementation

1. **Enterprise denylist** — critical paths blocked regardless of user approval (e.g., `~/.ssh`, dotfiles)
2. **Workspace allowlist** — read/write within workspace without approval (except config files)
3. **Specific allowlist** — enumerated exceptions (e.g., read `~/.ssh/gitlab-key` for git ops)
4. **Default-deny** — everything else requires manual per-action user approval

## Approval caching anti-pattern

Approvals must never be cached. A single legitimate "allow" for `~/.zshrc` opens that path to all future agent actions — including adversarial ones triggered later in the same session.

## Secret injection pattern

See [[concepts/agentic-sandbox-controls]] for the full pattern. Key principle: start with an empty credential set, inject only what the current task requires, ideally via a credential broker that issues short-lived tokens rather than long-lived env vars.

## Remaining vulnerabilities (even with mandatory controls)

- Malicious hooks or MCP init commands ingested before sandboxing activates
- Kernel exploits (mitigated by virtualization)
- Agent access to secrets (mitigated by secret injection)
- Approval caching bugs in the agentic IDE
- Stale sandbox state accumulation
