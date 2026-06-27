# commandr-omp-runner

> Relocated: canonical source now lives in `~/repos/Commandr/adapters/omp/`. This directory is archival reference only; do not extend runner behavior here.

Commandr L2 runner wrapper for [omp](https://omp.sh) (oh-my-pi).

**Status: Level 1 complete (2026-06-20).** `runner.sh` is bus-integrated: accepts pre-claimed packet (`--claimed`), exports `AGENTS_TASK_ID`, calls `PROGRESS_CMD` for neutral milestones, calls `COMPLETE_CMD pass/fail` on exit, scans omp NDJSON for policy hits (neutral progress + workspace artifact; no mid-turn blocking gate). `OMP_BIN`/`PROGRESS_CMD`/`COMPLETE_CMD` env seams; 13-case smoke test at `test/smoke.sh`, all pass. Canonical implementation is `~/repos/Commandr/adapters/omp/`.

## What it does

Bridges Commandr's L3 bus protocol and omp's CLI interface.

```
Commandr (L3 bus)
  │ orchestrator pre-claims task: bin/claim → claimed/<host>_<pid>_TASK.md
  ▼
commandr-omp-runner
  │ reads claimed packet, extracts task id
  │ export AGENTS_TASK_ID
  │ PROGRESS_CMD <id> "omp runner started"
  │ run: OMP_BIN --no-lsp --mode json -p "<prompt>" > workspace/omp.stdout
  │ scan omp.stdout NDJSON for policy hits → PROGRESS_CMD neutral milestone + artifact
  │ PROGRESS_CMD <id> "omp complete" OR "omp failed: exit N"
  │ COMPLETE_CMD <claimed-path> pass|fail
  ▼
Commandr (L3 bus)
  │ events.jsonl: task_progress* + task_complete or task_failed
  │ done/<host>_<pid>_TASK.md
```

## Setup

```bash
# One-time bootstrap: installs omp + pi-headroom plugin
./commandr-omp-runner/setup.sh
```

## Usage

```bash
# Bus mode: pass a pre-claimed packet (orchestrator calls bin/claim first)
commandr-omp-runner \
  --claimed /path/to/.agents/claimed/host_123_TASK-001.md \
  --workspace ./workspaces/TASK-001 \
  --model claude-sonnet-4-6

# Offline / smoke mode: no bus integration, omp exits with its own exit code
commandr-omp-runner \
  --task task.json \
  --workspace ./workspaces/TASK-001
```

## Env var seams (testability)

| Var | Default | Purpose |
|---|---|---|
| `OMP_BIN` | `omp` | Path to omp binary |
| `PROGRESS_CMD` | `progress` | `bin/progress` from Commandr on PATH |
| `COMPLETE_CMD` | `complete` | `bin/complete` from Commandr on PATH |

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
