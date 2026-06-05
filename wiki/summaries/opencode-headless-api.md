---
title: "OpenCode Headless & Programmatic Interface"
type: summary
tags: [opencode, headless, api, orchestration, cli, server]
sources: ["CLI.md", "Server.md"]
created: 2026-05-28
updated: 2026-05-28
---

# OpenCode Headless & Programmatic Interface

Two official OpenCode docs covering the CLI command surface and the HTTP server API. Primary relevance: enabling programmatic/headless use of OpenCode as an orchestration target.

---

## Headless Invocation (`opencode run`)

`opencode run` is the non-interactive mode — the `pi -p` equivalent:

```bash
opencode run "Explain async/await in JavaScript"
opencode run --model anthropic/claude-sonnet-4-6 --agent Build "Refactor auth module"
```

Key flags:

| Flag | Purpose |
|---|---|
| `--model provider/model` | Override model for this run |
| `--agent` | Override agent (Build, Plan, custom) |
| `--attach http://host:port` | Attach to a running `opencode serve` instance |
| `--continue` / `--session` | Continue an existing session |
| `--fork` | Fork session on continue |
| `--file` | Attach files to message |
| `--format json` | Raw JSON event output (for machine parsing) |
| `--variant` | Provider-specific reasoning effort |
| `--dangerously-skip-permissions` | Auto-approve non-denied permissions (unattended automation) |

---

## Server Architecture

Every `opencode` invocation (TUI mode) starts an embedded HTTP server; the TUI is a client to that server. Running `opencode serve` exposes the same server standalone, without the TUI.

```bash
# Standalone headless server
opencode serve --port 4096 --hostname 127.0.0.1

# Warm-server pattern: persistent server, stateless callers
opencode serve &   # start once
opencode run --attach http://localhost:4096 "task 1"
opencode run --attach http://localhost:4096 "task 2"
```

**Why warm-server matters**: avoids MCP cold-boot overhead on every invocation. IDE plugins use the `/tui` endpoint to drive the TUI through an already-running server.

Auth: `OPENCODE_SERVER_PASSWORD` enables HTTP basic auth.

---

## HTTP API Surface (Key Endpoints)

Full OpenAPI 3.1 spec at `http://<host>:<port>/doc`.

### Sessions

```
POST   /session                         # create session
POST   /session/:id/message             # send prompt, wait for response (sync)
POST   /session/:id/prompt_async        # send prompt, return 204 immediately (async)
POST   /session/:id/command             # execute slash command
POST   /session/:id/fork                # fork session at a message
POST   /session/:id/abort               # abort running session
POST   /session/:id/permissions/:id     # respond to permission request programmatically
DELETE /session/:id                     # delete session
```

### Events (SSE)

```
GET /event           # per-server SSE stream — all bus events
GET /global/event    # global SSE stream
GET /session/:id     # includes status, todo list
```

### TUI Control

```
POST /tui/append-prompt     # prefill the prompt box
POST /tui/submit-prompt     # submit current prompt
POST /tui/execute-command   # fire a slash command in TUI
```

Used by IDE plugins to drive TUI from an external process.

### Config & Agents

```
GET  /config               # current config
PATCH /config              # update config at runtime
GET  /agent                # list available agents
GET  /provider             # list providers + auth status
POST /mcp                  # add MCP server dynamically
```

---

## ACP Protocol

`opencode acp` starts an Agent Client Protocol server communicating via **stdin/stdout nd-JSON** — designed for IDE/extension embedding where HTTP overhead is unwanted.

---

## Programmatic Permission Handling

In unattended orchestration, permission prompts block execution. Two approaches:
1. `--dangerously-skip-permissions` on `opencode run` — auto-approves everything not explicitly denied
2. `POST /session/:id/permissions/:permissionID` with `{ response, remember? }` — fine-grained programmatic approval via HTTP

---

## Experimental Features Relevant to Orchestration

| Env var | Effect |
|---|---|
| `OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS` | Enable background subagent task execution |
| `OPENCODE_EXPERIMENTAL_SCOUT` | Enable Scout subagent (read-only fast search) |
| `OPENCODE_EXPERIMENTAL_PLAN_MODE` | Enable plan mode |
| `OPENCODE_EXPERIMENTAL_PARALLEL` | Enable parallel web search |

---

## Orchestration Patterns Enabled

### Subprocess (like `pi -p`)
```bash
opencode run --model opencode-go/deepseek-v4-pro "task"
```

### Warm server + stateless calls (avoids cold boot)
```bash
opencode serve --port 4096 &
opencode run --attach http://localhost:4096 "task 1"
opencode run --attach http://localhost:4096 "task 2"
```

### HTTP API (from any language)
```bash
SESSION=$(curl -s -X POST http://localhost:4096/session | jq -r '.id')
curl -s -X POST http://localhost:4096/session/$SESSION/message \
  -H "Content-Type: application/json" \
  -d '{"parts": [{"type": "text", "text": "Refactor the auth module"}]}'
```

### Async dispatch + SSE polling
```bash
curl -X POST http://localhost:4096/session/$SESSION/prompt_async -d '...'  # returns 204
curl -N http://localhost:4096/event  # stream events until completion
```

---

## Relation to Existing Wiki

- [[entities/opencode]] — core entity; this summary adds the headless/API layer
- [[entities/pi-agent]] — `opencode run` is equivalent to `pi -p` for subprocess delegation
- [[concepts/agent-harness]] — OpenCode's server-first architecture is a harness pattern
- [[comparisons/claude-code-vs-opencode-plugins]] — CC has no equivalent HTTP API layer
