# commandr-omp-runner

Commandr L2 runner wrapper for [omp](https://omp.sh) (oh-my-pi).

**Status: scaffold / smoke test only (2026-06-19).** `runner.sh` launches omp in `--mode json` and tees NDJSON to a side file + stderr. It is NOT yet bus-integrated: it does not call `bin/claim`, does not set `AGENTS_TASK_ID`, does not write `.agents/events.jsonl`, does not emit `task_progress`/`task_complete`/`task_failed`, does not move packets to `done/`, performs no approval/policy logic, and has no tests. See `PLAN-control-plane-runner-packages.md` "Level 1 acceptance criteria" for the TODO list to make this real.

## What it does (current)

Translates between Commandr's L3 bus protocol and omp's CLI interface — *aspirationally*. Today it runs omp with a task packet, streams omp's raw NDJSON to a runner-local progress file + stderr, and propagates the exit code. Bus integration (claim, progress, complete/fail events on `.agents/events.jsonl`) is not yet implemented.

## Architecture

```
Commandr (L3 bus)
  │ claim task (bin/claim) — NOT yet done by this runner
  │ write task packet
  ▼
commandr-omp-runner  (scaffold)
  │ create workspace
  │ run omp -p "<task>" --mode json
  │ stream NDJSON output (to runner-local file + stderr, NOT events.jsonl)
  │ TODO: extract neutral progress → bin/progress
  ▼
omp (L2 runner)
  │ execute task
  │ use tools (read, edit, bash, lsp, debug, ...)
  │ optionally use pi-headroom plugin for compression
  ▼
commandr-omp-runner
  │ TODO: report complete/fail → bin/complete (task_complete/task_failed + done/ move)
  │ write artifacts to workspace
  ▼
Commandr (L3 bus)
  │ mark done (via bin/complete) — NOT yet done by this runner
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

## Progress Events (runner-local — NOT `.agents/events.jsonl`)

The runner emits NDJSON progress events to stderr and optionally to a file. **These are runner-local, not bus events** — they use `event` names `start`/`omp_launch`/`output`/`complete`/`fail` that are NOT SPEC §6 event types and do not appear on `.agents/events.jsonl`. Bus integration (writing `task_progress`/`task_complete`/`task_failed` via `bin/progress`/`bin/complete`) is a TODO.

```json
{"timestamp":"2026-06-19T01:00:00Z","runner":"omp","event":"start","data":{"workspace":"./workspaces/task-123","model":"claude-sonnet-4"}}
{"timestamp":"2026-06-19T01:00:01Z","runner":"omp","event":"omp_launch","data":{"prompt_length":245}}
{"timestamp":"2026-06-19T01:00:05Z","runner":"omp","event":"output","data":"{\"type\":\"turn_start\"}"}
{"timestamp":"2026-06-19T01:02:00Z","runner":"omp","event":"complete","data":{"exit_code":0}}
```

## Integration Levels

Per [[entities/omp]] integration ladder (corrected 2026-06-19 — Level 1 is scaffold, not complete):

| Level | Status | Description |
|---|---|---|
| 0 | ✅ | `omp -p "<task>"` subprocess; capture stdout/stderr |
| 1 | ⚠️ scaffold | This wrapper runs omp + tees NDJSON, but does NOT yet: claim task, set `AGENTS_TASK_ID`, emit `task_progress`/`task_complete`/`task_failed` to `.agents/events.jsonl`, move packets to `done/`, or run any approval/policy logic. No tests. |
| 2 | 🚧 design only | RPC host tools (`commandr_progress`, `commandr_request_approval`, `commandr_emit_artifact`, `commandr_complete`, `commandr_fail`); schema in `HOST-TOOLS.md` (non-normative); blocked on `omp --mode rpc`. |
| 3 | 📋 future | Plugin-based bidirectional sync. |

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
