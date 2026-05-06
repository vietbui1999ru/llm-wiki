---
title: "Docker Sandboxes for Coding Agents"
type: summary
tags: [sandbox, docker, microvm, agent-security, claude-code, isolation]
sources:
  - "Docker Sandboxes Run Claude Code and More Safely.md"
created: 2026-05-07
updated: 2026-05-07
---

# Docker Sandboxes for Coding Agents

Docker's hosted sandbox solution for running AI coding agents (Claude Code, Codex CLI, Copilot CLI, Gemini CLI, Kiro) in isolated microVM environments. Launched with microVM isolation for macOS and Windows.

---

## The Problem Solved

Three common sandboxing approaches all fail:

| Approach | Problem |
|---|---|
| OS-level sandbox (CC native Seatbelt/bubblewrap) | Interrupts workflows; not consistent across platforms |
| Containers | Agent can't run Docker itself (Docker-in-Docker) |
| Full VMs | Slow, manual, hard to reuse across projects |

Docker Sandboxes fill this gap: **microVM isolation with real dev environment inside**.

---

## What It Provides

**Defense-in-depth isolation:**
- Each agent runs in dedicated microVM (hypervisor-level boundary)
- Only project workspace mounted into sandbox
- Host machine remains untouched regardless of what agent does

**Full development environment:**
- Agents can install system packages, run services, modify files
- Unattended operation — no constant permission approvals

**Docker-in-Docker (safe):**
- Agents can build and run Docker containers inside the microVM
- No access to host Docker daemon — key security boundary

**Multi-agent support:**
- Same sandbox experience across Claude Code, Codex CLI, Copilot CLI, Gemini CLI, Kiro
- Fast reset: delete sandbox and spin up fresh in seconds

**Network controls:**
- Allow and deny lists for network access

---

## Comparison with CC Native Sandboxing

| | CC Native Sandbox (Seatbelt/bubblewrap) | Docker Sandboxes |
|---|---|---|
| **Isolation level** | OS-level (process namespace) | MicroVM (hypervisor) |
| **Docker support** | ❌ Incompatible | ✅ Containers inside microVM |
| **Platform** | macOS + Linux + WSL2 | macOS + Windows (Linux coming) |
| **Setup** | `/sandbox` command | Docker Desktop integration |
| **Permission prompts** | Auto-allow mode eliminates them | No prompts needed |
| **Reset** | N/A (session-based) | Delete sandbox → fresh microVM |

---

## When to Use Docker Sandboxes

Prefer Docker Sandboxes when:
- Agent needs to run Docker containers (can't use CC native sandbox)
- Want hypervisor-level isolation (stronger guarantee than OS-level)
- Running CC on Windows (CC native sandbox is macOS/Linux only)
- Multi-project isolation with fast reset between sessions

Use CC native sandbox when:
- On Linux/WSL2 with no Docker Desktop
- Lightweight filesystem/network isolation is sufficient
- Prefer zero external dependencies

---

## Status (at time of writing)

- MicroVM-based isolation: shipped for macOS + Windows
- Linux support: coming
- MCP Gateway support: coming
- Port exposure to host: coming

---

## Related Pages

- [[concepts/agentic-sandbox-controls]] — OS-level sandbox controls and CC native sandbox
- [[summaries/cc-auto-mode]] — auto mode as permission alternative to sandboxing
- [[summaries/claude-code-permissions-settings]] — CC permissions + sandbox configuration
- [[concepts/indirect-prompt-injection]] — what sandboxes defend against
