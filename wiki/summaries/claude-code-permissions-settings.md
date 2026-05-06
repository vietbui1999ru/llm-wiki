---
title: "Claude Code Permissions & Settings Schema"
type: summary
tags: [claude-code, permissions, sandbox, settings, bypassPermissions, autonomous]
sources: []
urls:
  - "https://www.anthropic.com/engineering/claude-code-auto-mode"
  - "https://code.claude.com/docs/en/permission-modes"
  - "https://code.claude.com/docs/en/settings"
  - "https://www.truefoundry.com/blog/claude-code-dangerously-skip-permissions"
created: 2026-05-06
updated: 2026-05-06
---

# Claude Code Permissions & Settings Schema

Official Claude Code permission system. Key correction: the widely-cited `allowedTools` / `disallowedTools` / `allowedPaths` schema is **outdated**. The current schema uses `permissions.*` and `sandbox.*`.

---

## Permission Modes

Four permission modes controlling how Claude handles tool use:

| Mode | Behavior |
|---|---|
| `default` | Standard approval prompts for risky actions |
| `acceptEdits` | Auto-approves file edits; still prompts for other tools |
| `autoApprove` | Approves all tools automatically (risky without sandbox) |
| `bypassPermissions` | Fully unattended; no approval prompts at all |

`--dangerously-skip-permissions` CLI flag maps to `bypassPermissions` mode at runtime.

---

## `permissions.*` Schema (`settings.json`)

```jsonc
{
  "permissions": {
    "allow": ["Bash(git:*)", "Read(**)", "Edit(**)"],   // always allowed, no prompt
    "ask":   ["Bash(npm:*)", "WebFetch"],                // always prompts
    "deny":  ["Bash(rm -rf:*)", "Bash(curl:*)"],        // always blocked
    "defaultMode": "bypassPermissions",                  // mode for unspecified actions
    "disableBypassPermissionsMode": false,               // if true: prevents bypassPermissions even via CLI flag
    "skipDangerousModePermissionPrompt": false           // if true: skips the startup warning in bypass mode
  }
}
```

`allow`/`ask`/`deny` entries use glob patterns on tool names and optionally constrain arguments:
- `"Bash(git:*)"` — any git command in Bash
- `"Bash(rm -rf:*)"` — Bash with `rm -rf` anywhere in args

`disableBypassPermissionsMode: true` is the organizational lockout — prevents any session from entering bypass mode regardless of flags or settings.

---

## `sandbox.*` Schema

```jsonc
{
  "sandbox": {
    "enabled": true,                       // activates OS-level sandbox for Bash only
    "autoAllowBashIfSandboxed": true,      // if sandbox enabled, Bash auto-approved (no prompt)
    "allowUnsandboxedCommands": false,     // if false: no dangerouslyDisableSandbox escape hatch
    "excludedCommands": ["brew", "pip"],   // commands that bypass sandbox even when enabled

    "filesystem": {
      "allowWrite": ["./", "/tmp/"],       // writable paths
      "denyWrite":  ["/etc/", "~/.ssh/"], // blocked write paths
      "allowRead":  ["./", "~/.npmrc"],   // readable paths
      "denyRead":   ["~/.aws/", "/proc/"] // blocked read paths
    },

    "network": {
      "allowedDomains": ["registry.npmjs.org", "github.com"],
      "deniedDomains":  ["*"]             // default-deny; allowedDomains is the allowlist
    }
  }
}
```

**Critical**: `sandbox.enabled` only sandboxes **Bash and its child processes**. Built-in file tools (Read, Edit, Write, Glob, Grep) are NOT sandboxed by this setting — they bypass it entirely. OS-level isolation (container/VM) is required to constrain file tools.

`autoAllowBashIfSandboxed: true` — when sandbox is on, Bash runs without approval prompts (the sandbox IS the gate). Setting this false keeps approval prompts even inside sandbox.

---

## Combining Modes for Autonomous Operation

Safe unattended configuration pattern:

```jsonc
{
  "permissions": {
    "defaultMode": "bypassPermissions",
    "skipDangerousModePermissionPrompt": true,
    "deny": [
      "Bash(rm -rf:*)",
      "Bash(curl * | sh:*)",
      "Bash(wget * -O- | bash:*)"
    ]
  },
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "allowUnsandboxedCommands": false,
    "filesystem": {
      "allowWrite": ["./"],
      "denyWrite":  ["~/.ssh/", "~/.aws/", "/etc/", "~/.config/"]
    },
    "network": {
      "allowedDomains": ["registry.npmjs.org", "pypi.org", "github.com"],
      "deniedDomains": ["*"]
    }
  }
}
```

This disables approval prompts but restricts Bash to project directory writes and a domain allowlist. The file tool gap (Read/Edit/Write not sandboxed) must be closed by OS-level isolation.

---

## Key Corrections vs Older Sources

| Old schema (outdated) | Current schema |
|---|---|
| `allowedTools: [...]` | `permissions.allow: [...]` |
| `disallowedTools: [...]` | `permissions.deny: [...]` |
| `allowedPaths: [...]` | `sandbox.filesystem.allowWrite: [...]` |
| `sandbox: true` (bare) | `sandbox.enabled: true` |

Older tutorials, community posts, and third-party orchestrators (Dangeresque etc.) may still use the old names. They likely refer to their own config layer, not CC's native `settings.json`.

---

## Related Wiki Pages

- [[concepts/agentic-sandbox-controls]] — OS-level isolation; when settings.json is insufficient
- [[concepts/self-healing-loop]] — autonomous loop that uses bypassPermissions
- [[concepts/agentic-cicd]] — CI as external watchdog when agent runs in bypass mode
- [[entities/dangeresque]] — host-native orchestrator; uses its own tool filter config
