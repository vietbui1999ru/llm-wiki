---
name: subagent-name              # required; lowercase, hyphens only; no spaces
description: |
  One-paragraph description Claude uses to decide when to delegate here.
  Include: what it does, when to use it, "Use proactively" if auto-delegation wanted.
  # required
tools: Read, Grep, Glob, Bash    # allowlist; omit = inherits all from parent
disallowedTools: Write, Edit     # denylist; applied before tools; remove field if unused
model: sonnet                    # sonnet | opus | haiku | full model ID | inherit (default)
permissionMode: default          # default | acceptEdits | auto | dontAsk | bypassPermissions | plan
maxTurns: 30                     # optional; cap agentic turns before stopping
skills:                          # optional; preload full skill content at startup
  - skill-name                   # subagents don't inherit parent skills; list explicitly
mcpServers:                      # optional; scope MCP servers to this subagent only
  - server-name:                 # inline definition: scoped to this subagent's lifetime
      type: stdio
      command: npx
      args: ["-y", "@package/mcp@latest"]
  # - github                     # string reference: reuses parent session's connection
hooks:                           # optional; lifecycle hooks scoped to this subagent
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/run-tests.sh"
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh"
memory: project                  # optional: user | project | local — cross-session memory
background: false                # optional: true = always run concurrently
effort: medium                   # optional: low | medium | high | xhigh | max
isolation: worktree              # optional: worktree = isolated git copy; auto-cleaned if no changes
color: blue                      # optional: red|blue|green|yellow|purple|orange|pink|cyan
# initialPrompt: "..."           # optional: auto-submitted as first turn when run via --agent
---

You are a [role description]. [What you do. What you don't do.]

## When invoked

[List the triggers: what user says, what other agents route here, what conditions]

## Process

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Output format

[How to structure the response: sections, severity levels, next steps]

## Constraints

[Hard rules: don't edit files, don't approve X without Y, always do Z]
