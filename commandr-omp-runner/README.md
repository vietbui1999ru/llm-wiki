# commandr-omp-runner

Commandr L2 runner wrapper for [omp](https://omp.sh) (oh-my-pi).

## What it does

Translates between Commandr's L3 bus protocol and omp's CLI interface. Commandr calls this wrapper with a task packet; the wrapper runs omp, streams progress back, and reports completion/failure.

## Architecture

```
Commandr (L3 bus)
  │ claim task
  │ write task packet
  ▼
commandr-omp-runner
  │ create workspace
  │ run omp -p "<task>" --mode json
  │ stream NDJSON output
  │ extract progress events
  ▼
omp (L2 runner)
  │ execute task
  │ use tools (read, edit, bash, lsp, debug, ...)
  │ optionally use pi-headroom plugin for compression
  ▼
commandr-omp-runner
  │ report complete/fail
  │ write artifacts to workspace
  ▼
Commandr (L3 bus)
  │ mark done
```

## Setup

```bash
# One-time bootstrap: installs omp + pi-headroom plugin
./commandr-omp-runner/setup.sh
```

## Usage

```bash
# From Commandr: run a task packet through omp
./commandr-omp-runner/runner.sh \
  --task task.json \
  --workspace ./workspaces/task-123 \
  --progress ./workspaces/task-123/progress.ndjson \
  --model claude-sonnet-4

# Or pipe task JSON directly
cat task.json | ./commandr-omp-runner/runner.sh \
  --workspace ./workspaces/task-123
```

## Task Packet Format

```json
{
  "id": "task-123",
  "prompt": "Refactor the auth module to use JWT",
  "context": {
    "repo": "my-app",
    "branch": "feat/jwt-auth"
  },
  "constraints": {
    "max_turns": 50,
    "approved_tools": ["read", "edit", "bash", "lsp"]
  }
}
```

## Progress Events

The runner emits NDJSON progress events to stderr and optionally to a file:

```json
{"timestamp":"2026-06-19T01:00:00Z","runner":"omp","event":"start","data":{"workspace":"./workspaces/task-123","model":"claude-sonnet-4"}}
{"timestamp":"2026-06-19T01:00:01Z","runner":"omp","event":"omp_launch","data":{"prompt_length":245}}
{"timestamp":"2026-06-19T01:00:05Z","runner":"omp","event":"output","data":"{\"type\":\"turn_start\"}"}
{"timestamp":"2026-06-19T01:02:00Z","runner":"omp","event":"complete","data":{"exit_code":0}}
```

## Integration Levels

Per [[entities/omp]] integration ladder:

| Level | Status | Description |
|---|---|---|
| 0 | ✅ | `omp -p "<task>"` subprocess; capture stdout/stderr |
| 1 | ✅ | This wrapper: claim task, create workspace, run omp, stream logs, emit progress, complete/fail |
| 2 | 🚧 | omp custom tools for Commandr: `commandr_progress`, `commandr_request_approval`, `commandr_emit_artifact` |
| 3 | 📋 | Plugin-based bidirectional sync: omp plugin writes turn snapshots directly to Commandr bus |

## pi-headroom Plugin

The runner bootstrap auto-installs the [pi-headroom](../pi-headroom/) plugin for context compression. This reduces token usage on large tool outputs (read files, search results, bash output).

## Runner-Agnostic Interface

This wrapper exposes a runner-agnostic interface to Commandr:

- **Input**: Task packet JSON (stdin or `--task`)
- **Output**: NDJSON stream (stdout)
- **Progress**: NDJSON events (stderr + optional `--progress` file)
- **Exit**: 0 = success, 1 = failure

Commandr should not depend on omp-specific behavior. Any L2 runner (Claude Code, OpenCode, Codex) can implement the same interface.

## Related

- [[entities/omp]] — omp capability reference
- [[entities/commandr]] — L3 bus specification
- [pi-headroom](../pi-headroom/) — context compression plugin
- [[syntheses/control-plane-expansion-plan]] — bootstrap path
