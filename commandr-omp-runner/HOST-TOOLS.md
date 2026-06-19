# Host Tool Schema for Commandr Bus Integration (Level 2)

**Status:** Design complete. Implementation blocked on RPC mode adoption.
**Scope:** Runner-agnostic interface — any L2 runner (omp, Claude Code, OpenCode) can implement.
**Storage:** Filesystem + NDJSON/JSONL only. No SQLite, no derived cache.

---

## Philosophy

Keep the contract small and concrete. Every host tool maps to exactly one filesystem operation.

| Principle | Rationale |
|---|---|
| One tool, one side effect | Easy to audit, easy to replay |
| Events are append-only | `events.jsonl` is source of truth for timeline |
| Artifacts live in workspace | Runner manages workspace; bus references them |
| Approvals are token files | `.agents/approvals/<task>.approved` already works |
| Policy violations are logged | Level 1 can't block; Level 2 (RPC) can pause |

---

## Host Tools

### `commandr_progress`

Agent reports a milestone. Runner appends to `events.jsonl`.

```json
{
  "type": "host_tool_call",
  "toolName": "commandr_progress",
  "arguments": {
    "task": "TASK-001",
    "milestone": "LSP diagnostics clean after refactor",
    "metadata": {
      "files_changed": ["src/auth.ts", "src/jwt.ts"],
      "tests_passing": true
    }
  }
}
```

**Side effect:**
```jsonl
{"timestamp":"2026-06-19T12:00:00Z","type":"task_progress","task":"TASK-001","runner":"omp","milestone":"LSP diagnostics clean after refactor","metadata":{"files_changed":["src/auth.ts","src/jwt.ts"],"tests_passing":true}}
```

---

### `commandr_emit_artifact`

Agent declares an artifact. Runner writes to workspace + logs to events.

```json
{
  "type": "host_tool_call",
  "toolName": "commandr_emit_artifact",
  "arguments": {
    "task": "TASK-001",
    "artifact_type": "diff",
    "path": "artifacts/auth-refactor.patch",
    "summary": "JWT auth module refactor: 3 files changed, +142/-89 lines",
    "tags": ["auth", "jwt", "refactor"]
  }
}
```

**Side effects:**
1. Artifact already exists in workspace (agent created it via write/edit/bash)
2. Runner appends to `events.jsonl`:
```jsonl
{"timestamp":"2026-06-19T12:00:00Z","type":"artifact_created","task":"TASK-001","runner":"omp","artifact_type":"diff","path":"workspaces/TASK-001/artifacts/auth-refactor.patch","summary":"JWT auth module refactor: 3 files changed, +142/-89 lines","tags":["auth","jwt","refactor"]}
```

**Artifact types:**
| Type | Example | Created by |
|---|---|---|
| `diff` | `git diff` output | bash tool |
| `file` | New or modified source file | write/edit tool |
| `log` | Test output, build log | bash tool |
| `report` | Security scan, lint report | bash tool |
| `screenshot` | UI capture | browser tool |

---

### `commandr_request_approval`

Agent (or runner policy) requests human approval for a risky action.

```json
{
  "type": "host_tool_call",
  "toolName": "commandr_request_approval",
  "arguments": {
    "task": "TASK-001",
    "action": "Run bash command: rm -rf node_modules && npm install",
    "tool": "bash",
    "command": "rm -rf node_modules && npm install",
    "risk": "high",
    "reason": "Destructive filesystem operation in workspace root"
  }
}
```

**Side effects:**

**Level 1 (current, `--mode json`):**
- Cannot pause mid-turn
- Logs to `events.jsonl`:
```jsonl
{"timestamp":"2026-06-19T12:00:00Z","type":"approval_requested","task":"TASK-001","runner":"omp","action":"Run bash command: rm -rf node_modules && npm install","risk":"high","status":"logged_only","reason":"Level 1 runner cannot block mid-turn"}
```
- Continues execution
- Human reviews post-hoc in DiffViewer/Tauri

**Level 2 (future, `--mode rpc`):**
- Runner pauses turn via `abort`
- Creates `.agents/approvals/TASK-001.pending`:
```json
{"task":"TASK-001","action":"Run bash command: rm -rf node_modules && npm install","risk":"high","requested_at":"2026-06-19T12:00:00Z","timeout":300}
```
- Waits for `.agents/approvals/TASK-001.approved` or `.agents/approvals/TASK-001.denied`
- Resumes or fails task accordingly

---

### `commandr_complete`

Agent declares task complete. Runner finalizes bus state.

```json
{
  "type": "host_tool_call",
  "toolName": "commandr_complete",
  "arguments": {
    "task": "TASK-001",
    "result": "success",
    "summary": "Refactored auth module to use JWT. All tests pass. LSP diagnostics clean.",
    "artifacts": ["artifacts/auth-refactor.patch", "artifacts/test-output.log"],
    "next_steps": "Deploy to staging and run integration tests"
  }
}
```

**Side effects:**
1. Appends to `events.jsonl`:
```jsonl
{"timestamp":"2026-06-19T12:00:00Z","type":"task_complete","task":"TASK-001","runner":"omp","result":"success","summary":"Refactored auth module to use JWT. All tests pass. LSP diagnostics clean.","artifacts":["workspaces/TASK-001/artifacts/auth-refactor.patch","workspaces/TASK-001/artifacts/test-output.log"],"next_steps":"Deploy to staging and run integration tests"}
```
2. Moves claimed packet to `done/`:
```bash
mv .agents/claimed/*TASK-001* .agents/done/
```

---

### `commandr_fail`

Agent declares task failed. Runner finalizes bus state.

```json
{
  "type": "host_tool_call",
  "toolName": "commandr_fail",
  "arguments": {
    "task": "TASK-001",
    "reason": "Type mismatch in JWT payload after refactor. Tests failing: src/jwt.test.ts:47.",
    "recoverable": true,
    "suggested_retry": "Fix type annotation in src/jwt.ts:42 and re-run tests"
  }
}
```

**Side effects:**
1. Appends to `events.jsonl`:
```jsonl
{"timestamp":"2026-06-19T12:00:00Z","type":"task_failed","task":"TASK-001","runner":"omp","reason":"Type mismatch in JWT payload after refactor. Tests failing: src/jwt.test.ts:47.","recoverable":true,"suggested_retry":"Fix type annotation in src/jwt.ts:42 and re-run tests"}
```
2. Moves claimed packet to `done/`:
```bash
mv .agents/claimed/*TASK-001* .agents/done/
```

---

## Policy Table (Auto-Approval)

Runner-enforced. Agent should know about this policy (system prompt injection) but enforcement is transparent.

```yaml
# .agents/runner-policy.yml (optional, per-repo override)
# Default policy if missing:
policy:
  - pattern:
      tool: bash
      regex: "\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*|-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*)"
    risk: high
    action: request_approval
    reason: "Destructive recursive delete"

  - pattern:
      tool: bash
      regex: "\bsudo\b"
    risk: high
    action: request_approval
    reason: "Privilege escalation"

  - pattern:
      tool: bash
      regex: "\bdocker\s+(run|exec|rm)\b"
    risk: medium
    action: request_approval
    reason: "Container mutation"

  - pattern:
      tool: bash
      regex: "\bgit\s+push\b"
    risk: medium
    action: request_approval
    reason: "Remote mutation"

  - pattern:
      tool: write
      regex: "\\.env($|\\.)"
    risk: high
    action: request_approval
    reason: "Environment file mutation"

  - pattern:
      tool: write
      regex: "~/.ssh/"
    risk: high
    action: request_approval
    reason: "SSH key mutation"

  - pattern:
      tool: read
    risk: low
    action: allow

  - pattern:
      tool: edit
    risk: low
    action: allow
    log_artifact: true
```

**Policy enforcement behavior:**

| Level | Behavior |
|---|---|
| Level 1 (`--mode json`) | Log violation to `events.jsonl` as `approval_requested` with `status: logged_only`. Continue execution. Human reviews post-hoc. |
| Level 2 (`--mode rpc`) | Pause turn. Create `.agents/approvals/<task>.pending`. Wait for `.approved` or `.denied`. Resume or abort. |

---

## Runner-Agnostic Interface

Any L2 runner implementing this schema must expose:

| Capability | Level 1 | Level 2 |
|---|---|---|
| Parse task packet | ✅ | ✅ |
| Emit `task_progress` events | ✅ (inferred from NDJSON) | ✅ (explicit host tools) |
| Emit `artifact_created` events | ✅ (inferred from NDJSON) | ✅ (explicit host tools) |
| Log `approval_requested` | ✅ (policy violations) | ✅ (policy + explicit) |
| Block on approval | ❌ | ✅ (RPC mode) |
| Handle `commandr_complete` | ✅ (inferred from exit code) | ✅ (explicit) |
| Handle `commandr_fail` | ✅ (inferred from exit code) | ✅ (explicit) |

---

## Implementation Path

### Phase 1 (current): `--mode json` with inferred events

`commandr-omp-runner/runner.sh` already does this. Extend it to:
- Parse policy table (YAML or inline)
- Log policy violations to `events.jsonl`
- Infer artifacts from `write`/`edit`/`bash` tool calls in NDJSON
- No agent changes needed

### Phase 2 (future): `--mode rpc` with explicit host tools

- Start omp as long-running RPC process
- Register host tools on startup
- Handle `host_tool_call` frames
- Pause/resume for approvals
- Agent must be taught to call `commandr_emit_artifact` and `commandr_complete`

### Phase 3 (future): Agent-native awareness

- Inject policy summary into agent system prompt
- Agent learns to call `commandr_request_approval` proactively
- Agent learns to emit artifacts at natural boundaries

---

## Filesystem Contract Summary

```
.agents/
  inbox/           # unclaimed packets
  claimed/         # hostname_pid_task.md
  done/            # completed/failed packets
  approvals/       # <task>.approved (token file)
  events.jsonl     # append-only: task_claim, task_progress, artifact_created,
                   # approval_requested, task_complete, task_failed
  runner-policy.yml # optional per-repo policy override

workspaces/
  TASK-001/
    artifacts/     # artifact files referenced in events
    omp.stdout     # NDJSON stream from runner
    omp.stderr     # stderr from runner
    progress.ndjson # runner progress events
```

---

## Related

- [[entities/commandr]] — L3 bus specification
- [[entities/omp]] — L2 runner; RPC mode documentation
- [[research/omp-snapcompact-rpc]] — RPC protocol research
- [[syntheses/control-plane-expansion-plan]] — integration ladder
