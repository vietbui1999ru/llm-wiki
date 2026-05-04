---
title: "Agentic Sandbox Controls"
type: concept
tags: [security, sandboxing, agents, OS-controls, secret-injection]
sources: ["Practical Security Guidance for Sandboxing Agentic Workflows and Managing Execution Risk.md"]
created: 2026-04-22
updated: 2026-04-22
---

# Agentic Sandbox Controls

OS-level security controls for AI coding agents, as defined by the NVIDIA AI Red Team. The core insight: application-level controls (tool call interception, allowlists) are insufficient because they lose visibility once a subprocess starts. Effective controls must operate at the OS layer.

## The subprocess escape problem

An agent can invoke a "safe" tool that itself spawns a subprocess the app cannot observe. OS-level sandboxes (macOS Seatbelt, Linux Bubblewrap, Windows AppContainer) cover every spawned process regardless of origin — closing this gap.

## Mandatory controls (NVIDIA AI Red Team classification)

**Network egress blocking**
Block all outbound connections to arbitrary addresses. Use tightly-scoped allowlists (HTTP proxy, IP, port) for legitimate dependencies. DNS resolution should go through designated resolvers to prevent DNS-based exfiltration.

**Block writes outside the workspace**
Writing to `~/.zshrc`, `~/.local/bin`, `~/.gitconfig`, `~/.curlrc` enables persistence, sandbox escape, and data redirect. Must be enforced at OS level, not just application level.

**Block writes to any agent config file**
Applies to: `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `copilot-instructions.md`, hooks configs, MCP configs, skills scripts — including files within the workspace. Only direct manual user edits are acceptable. No user approval of agent-initiated writes should be possible.

## Secret injection pattern

Instead of letting the agent inherit the developer's full credential set:

1. Start the sandbox with a minimal or empty credential set
2. Identify what credentials the current task actually needs
3. Inject only those credentials, ideally via a **credential broker** that issues short-lived tokens on demand
4. Continue enforcing least privilege on injected credentials

This limits blast radius: a compromised agent can only use credentials explicitly provisioned for that task.

## Sandbox lifecycle management

Long-running sandboxes accumulate stale secrets, old dependencies, and previously generated code — all of which expand the attack surface. Two approaches:

- **Ephemeral**: sandbox exists only for the duration of one task or command (e.g., Kata container per execution)
- **Periodic reset**: sandbox is destroyed and recreated on a schedule (e.g., weekly for VM-based setups)

## Approval caching anti-pattern

Per-action user approvals should never be cached or persisted. A single legitimate approval for a sensitive path (e.g., `~/.zshrc`) creates a reusable permission that future adversarial injections can exploit without re-approval.

## Tiered implementation model

1. **Enterprise denylist** — unconditionally blocked paths/operations, not overridable by user approval
2. **Workspace allowlist** — read/write without approval, except config files
3. **Specific allowlist** — enumerated exceptions for required external reads (e.g., SSH key for git)
4. **Default-deny** — everything else requires fresh per-action user confirmation

## Virtualization for kernel isolation

Sandboxes that share the host kernel (Docker, Bubblewrap, Seatbelt) are vulnerable to kernel exploits from arbitrary code execution. Mitigations in order of strength:
- **Full VM / microVM** — strongest; separate kernel entirely
- **Kata containers** — VM-level isolation with container UX
- **gVisor** — user-space kernel mediating syscalls; weaker than full virtualization but stronger than shared-kernel approaches

## Scope of sandboxing

Sandboxing must cover the entire agent execution environment, not just shell/command-line tool invocations. Hooks, MCP startup scripts, skills, and file-editing tools often run outside sandbox scope by default — this must be explicitly closed.

## Anthropic ToS Constraint (Claude Code Subscription)

Anthropic's Terms of Service restrict running Claude Code subscription keys inside Docker containers. This creates tension with the NVIDIA AI Red Team's "mandatory OS-level sandboxing" recommendation:

- NVIDIA: container/VM isolation is mandatory
- Anthropic ToS: CC subscription keys cannot run inside containers

**Resolution paths:**
1. Use the Anthropic API (not subscription) — no container restriction
2. Host-native worktree isolation ([[entities/dangeresque]] approach) + fine-grained `allowedTools`/`disallowedTools`
3. [[entities/sandcastle]] workaround: Claude process runs on host, containers only for tool execution (sandboxing tool execution, not the Claude process)

This does not invalidate the NVIDIA guidance — it applies fully to API usage and partially to subscription users who can sandbox tool execution even if the Claude process runs on host.

## Related concepts

- [[concepts/indirect-prompt-injection]]
- [[entities/ai-coding-agents]]
- [[entities/dangeresque]] — host-native alternative to container sandboxing
- [[entities/sandcastle]] — hybrid: Claude on host, tools in container
- [[summaries/agentic-sandbox-security]] — NVIDIA AI Red Team source; full tiered denylist and secret injection details
