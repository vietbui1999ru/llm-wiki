---
title: "Agentic Sandbox Controls"
type: concept
tags: [security, sandboxing, agents, OS-controls, secret-injection]
sources: ["Practical Security Guidance for Sandboxing Agentic Workflows and Managing Execution Risk.md"]
created: 2026-04-22
updated: 2026-05-12
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
2. Host-native worktree isolation ([[entities/dangeresque]] approach) + fine-grained `permissions.allow`/`permissions.deny` in `.claude/settings.json`
3. [[entities/sandcastle]] workaround: Claude process runs on host, containers only for tool execution (sandboxing tool execution, not the Claude process)

This does not invalidate the NVIDIA guidance — it applies fully to API usage and partially to subscription users who can sandbox tool execution even if the Claude process runs on host.

## macOS Host-Native Sandbox (`sandbox-exec` + HTTP Proxy)

Apple's `sandbox-exec` provides a policy-based sandbox for any command without requiring Docker. Anthropic's [`sandbox-runtime`](https://github.com/anthropic-experimental/sandbox-runtime) OSS library (released Oct 2025) documents this pattern for Claude Code:

1. Run Claude Code under `sandbox-exec` with a policy that denies all outbound except `localhost:<proxy-port>`
2. Anthropic runs an HTTP proxy on that port
3. The proxy enforces a domain allowlist — the OS never sees a connection to non-allowlisted hosts

This is ToS-compliant (host-native, not Docker) and directly cuts the exfiltration leg of prompt injection attacks.

**Deprecation warning**: `sandbox-exec` has been marked deprecated in Apple docs since at least 2017. Still functional and used by Codex CLI as of 2025, but long-term availability is uncertain.

See: [[summaries/living-dangerously-with-claude]]

## Autonomous / Unattended Mode (`--dangerously-skip-permissions`)

Claude Code supports a flag that removes all approval prompts, enabling fully unattended operation. This flag is named accordingly — it is only safe if the sandbox is independently enforced.

**Critical rule**: `--dangerously-skip-permissions` maps to `defaultMode: "bypassPermissions"` in settings. It removes the approval layer entirely. Defense must come from the environment, not the agent:
- Run inside a disposable container or VM (non-root user, mounted project workspace only)
- No personal SSH keys or host home directory mounted
- Short-lived credentials provisioned per-task via credential broker
- `permissions.deny` list for high-risk Bash patterns
- Builder and deployer as separate network contexts with separate credentials
- Agent process has no prod deploy permissions

Using this flag on a developer machine with full credentials is equivalent to unrestricted shell access.

### Current `settings.json` schema

```jsonc
{
  "permissions": {
    "allow": ["Bash(git:*)", "Read(**)", "Edit(**)"],
    "ask":   ["Bash(npm:*)"],
    "deny":  ["Bash(rm -rf:*)", "Bash(curl * | sh:*)"],
    "defaultMode": "bypassPermissions",
    "disableBypassPermissionsMode": false,
    "skipDangerousModePermissionPrompt": false
  },
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "allowUnsandboxedCommands": false,
    "filesystem": {
      "allowWrite": ["./", "/tmp/"],
      "denyWrite":  ["~/.ssh/", "~/.aws/", "/etc/"]
    },
    "network": {
      "allowedDomains": ["registry.npmjs.org", "github.com"],
      "deniedDomains":  ["*"]
    }
  }
}
```

**`sandbox.enabled` scope**: only sandboxes Bash and its child processes. Built-in file tools (Read, Edit, Write, Glob, Grep) bypass the sandbox entirely. OS-level isolation (container/VM) is required to constrain file tools.

**Schema correction**: older sources and tutorials use `allowedTools`/`disallowedTools`/`allowedPaths`. These are outdated — the current schema uses `permissions.allow`/`permissions.deny`/`sandbox.filesystem`. Third-party orchestrators (Dangeresque, etc.) may still use the old names for their own config layers.

See: [[summaries/claude-code-permissions-settings]], [[concepts/self-healing-loop]], [[concepts/agentic-cicd]]

## Related concepts

- [[concepts/indirect-prompt-injection]]
- [[concepts/self-healing-loop]] — autonomous loop that requires sandbox isolation
- [[concepts/agentic-cicd]] — CI as external watchdog when agent runs unattended
- [[entities/ai-coding-agents]]
- [[entities/dangeresque]] — host-native alternative to container sandboxing
- [[entities/sandcastle]] — hybrid: Claude on host, tools in container
- [[summaries/agentic-sandbox-security]] — NVIDIA AI Red Team source; full tiered denylist and secret injection details
- [[summaries/docker-sandboxes]] — microVM isolation for coding agents; Docker-in-Docker safe; CC/Codex/Gemini/Copilot/Kiro support
- [[summaries/owasp-ai-security]] — OWASP S5 runtime sandboxing; --dangerously-skip-permissions risks; rules files as persistent steering
