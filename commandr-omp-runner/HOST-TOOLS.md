# Host Tool Schema for Commandr Bus Integration (Level 2)

**Status:** Design doc (non-normative). Implementation blocked on RPC mode adoption. Nothing in this document is in SPEC v0.3; `approval_requested`, `artifact_created`, `.agents/approvals/<task>.pending`, `.denied`, and `workspaces/` are NOT normative and MUST NOT be emitted/written until added via a conformance-backed SPEC change.
**Scope:** Runner-agnostic interface — any L2 runner (omp, Claude Code, OpenCode) can implement.
**Storage:** Filesystem + NDJSON/JSONL only. No SQLite, no derived cache.
**SPEC schema note:** SPEC §6 EVENT-2 mandates `"ts"` and `"event"` keys. Examples below use those keys (corrected 2026-06-19 from an earlier `timestamp`/`type` form that would have failed conformance C08). Runners must also include `agent`/`machine` where §6 requires.

---

## Philosophy

Keep the contract small and concrete. Every host tool maps to exactly one filesystem operation.

| Principle | Rationale |
|---|---|
| One tool, one side effect | Easy to audit, easy to replay |
| Events are append-only | `events.jsonl` is source of truth for timeline |
| Artifacts live in workspace | Runner manages workspace; bus references them |
| Approvals are token files | `.agents/approvals/<task>.approved` already works |
| Policy violations are projected as neutral progress | Runner writes full action to a workspace artifact + emits a neutral `task_progress` note + ref. The commit-time `pre-commit-gate` is the enforceable block (no mid-turn gate). |

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
{"ts":"2026-06-19T12:00:00Z","event":"task_progress","task":"TASK-001","runner":"omp","milestone":"LSP diagnostics clean after refactor","metadata":{"files_changed":["src/auth.ts","src/jwt.ts"],"tests_passing":true}}
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
{"ts":"2026-06-19T12:00:00Z","event":"artifact_created","task":"TASK-001","runner":"omp","artifact_type":"diff","path":"workspaces/TASK-001/artifacts/auth-refactor.patch","summary":"JWT auth module refactor: 3 files changed, +142/-89 lines","tags":["auth","jwt","refactor"]}
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

Agent (or runner policy) detects a risky action. **The bus never sees the raw command** (SPEC §6 EVENT-4 forbids tool-call transcripts on the bus); the runner writes the full action details to a workspace artifact and emits a NEUTRAL progress milestone + reference. The enforceable human gate stays the commit-time `pre-commit-gate` (SPEC §7, `.agents/approvals/<task>.approved`). This tool does NOT create a second blocking gate.

```json
{
  "type": "host_tool_call",
  "toolName": "commandr_request_approval",
  "arguments": {
    "task": "TASK-001",
    "risk": "high",
    "note": "destructive bash blocked (high risk)",
    "reason": "Destructive filesystem operation in workspace root",
    "artifact_ref": "workspaces/TASK-001/artifacts/policy-0001.json"
  }
}
```

The runner writes the full action (tool, command, reason) to `workspaces/TASK-001/artifacts/policy-0001.json` (runner-local, not on the bus).

**Side effect (same at Level 1 and Level 2 — a neutral progress line + artifact reference; no `approval_requested` event, no `.pending` file, no mid-turn block):**
```jsonl
{"ts":"2026-06-19T12:00:00Z","event":"task_progress","task":"TASK-001","note":"policy: destructive bash blocked (high risk); see workspaces/TASK-001/artifacts/policy-0001.json"}
```

The human reviews the policy log + artifact in DiffViewer; the commit gate (`pre-commit-gate`, SPEC §7) is the enforceable block. Council (SPEC §12) stays advisory. There is no third parallel gate.

**Note on the earlier design:** a previous revision of this doc had the runner emit `approval_requested` with `status: logged_only` (Level 1) and create `.agents/approvals/<task>.pending` + block via `abort` (Level 2). Both are dropped: `approval_requested`/`artifact_created` are not in SPEC §6 (EVENT-3), `.pending`/`.denied` are not in SPEC §2/§9, and a turn-time blocking gate would be a third parallel human-gate conflicting with locked decision 9 + the `PLAN-next-steps.md` Non-Goals.

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
{"ts":"2026-06-19T12:00:00Z","event":"task_complete","task":"TASK-001","runner":"omp","result":"success","summary":"Refactored auth module to use JWT. All tests pass. LSP diagnostics clean.","artifacts":["workspaces/TASK-001/artifacts/auth-refactor.patch","workspaces/TASK-001/artifacts/test-output.log"],"next_steps":"Deploy to staging and run integration tests"}
```
2. Finalizes the claimed packet via `bin/complete` (NOT a raw `mv` — `bin/complete` performs the atomic `claimed/→done/` move and appends the `task_complete` event with the correct shape per SPEC §5 COMPLETE-1):
```bash
bin/complete <claimed-path> pass
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
{"ts":"2026-06-19T12:00:00Z","event":"task_failed","task":"TASK-001","runner":"omp","reason":"Type mismatch in JWT payload after refactor. Tests failing: src/jwt.test.ts:47.","recoverable":true,"suggested_retry":"Fix type annotation in src/jwt.ts:42 and re-run tests"}
```
2. Finalizes the claimed packet via `bin/complete` (NOT a raw `mv` — `bin/complete` performs the atomic `claimed/→done/` move and appends the `task_failed` event with the correct shape per SPEC §5 COMPLETE-2):
```bash
bin/complete <claimed-path> fail
```

---

## Policy Table (Auto-Approval)

Runner-enforced. Agent should know about this policy (system prompt injection) but enforcement is transparent.

```yaml
# ~/.config/commandr-runner/policy.yml (optional, per-host override)
# OR workspaces/<task>/policy.yml (per-task override)
# NOT under .agents/ — runner-private config must not live on the bus (SPEC ADAPTER-2).
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

**Policy enforcement behavior (revised 2026-06-19 — no blocking gate; the commit-time `pre-commit-gate` is the single enforceable human gate):**

| Level | Behavior |
|---|---|
| Level 1 (`--mode json`) | Emit a NEUTRAL `task_progress` milestone (e.g. `"policy: destructive bash blocked (high risk)"`) + write the full action to a workspace artifact + reference it from the progress line. Continue execution. Human reviews in DiffViewer; commit gate enforces. |
| Level 2 (`--mode rpc`) | Same neutral-progress + artifact-ref projection, plus real-time streaming + bidirectional steer via RPC. Does NOT create `.pending`/`.denied`; does NOT block mid-turn. The commit gate remains the only enforceable block. |

---

## Runner-Agnostic Interface

Any L2 runner implementing this schema must expose (corrected 2026-06-19 — the prior table marked Level 1 ✅ on capabilities the current `runner.sh` does NOT have):

| Capability | Level 1 (current `runner.sh`) | Level 2 (future RPC) |
|---|---|---|
| Parse task packet | ✅ (accepts `--task` path / stdin) | ✅ |
| Claim task (`bin/claim`) | ❌ NOT implemented | ❌ (still the runner's job to call `bin/claim`) |
| Set `AGENTS_TASK_ID` | ❌ NOT implemented | ✅ |
| Emit `task_progress` to `events.jsonl` | ❌ NOT implemented (writes raw NDJSON to a side file, not the bus) | ✅ (explicit host tools, via `bin/progress`) |
| Emit `artifact_created` | ❌ NOT implemented; event not in SPEC §6 | ❌ held (SPEC-forbidden until conformance case) |
| Emit `approval_requested` | ❌ NOT implemented; event not in SPEC §6 | ❌ dropped — emit neutral `task_progress` + artifact ref instead |
| Block on approval | ❌ | ❌ dropped — no second blocking gate; commit `pre-commit-gate` is the enforceable gate |
| Handle `commandr_complete`/`commandr_fail` | ❌ NOT implemented (uses runner-local `complete`/`fail`, no `done/` move, no `events.jsonl`) | ✅ (shell to `bin/complete`) |

---

## Implementation Path

### Phase 1 (current, incomplete): `--mode json` runner

`commandr-omp-runner/runner.sh` is a scaffold — it launches omp and tees NDJSON to a side file + stderr. It does NOT yet integrate with the bus. To meet Level 1:
- Call `bin/claim` (or document the pre-claimed-path contract) and export `AGENTS_TASK_ID`.
- Shell to `bin/progress` for neutral `task_progress` (no raw NDJSON transcripts on the bus).
- Shell to `bin/complete` for `task_complete`/`task_failed` + `done/` move.
- Parse the policy table (runner-local) and project hits as neutral progress + workspace artifact refs (NOT `approval_requested`).
- Default `$OMP_BIN=omp`, gate under `set -u`, add a smoke test.

### Phase 2 (future): `--mode rpc` with explicit host tools

- Start omp as long-running RPC process.
- Register host tools on startup.
- Handle `host_tool_call` frames.
- Project approvals as neutral progress + artifact refs (no blocking gate, no `.pending`).
- Agent must be taught to call `commandr_emit_artifact` and `commandr_complete`.

### Phase 3 (future): Agent-native awareness

- Inject policy summary into agent system prompt.
- Agent learns to call `commandr_request_approval` proactively.
- Agent learns to emit artifacts at natural boundaries.

---

## Filesystem Contract Summary

```
.agents/                      # BUS (normative, SPEC v0.3) — runner must NOT write here directly;
                              # shell to bin/claim, bin/progress, bin/complete.
  inbox/                      # unclaimed packets
  claimed/                    # hostname_pid_task.md
  done/                       # completed/failed packets
  approvals/                  # <task>.approved (token file; SPEC §7). .pending/.denied NOT defined.
  annotations/                # <task>/<turn>-<seq>.json (SPEC §14)
  events.jsonl                # append-only: task_claimed, task_progress, task_complete,
                              # task_failed, council_verdict, task_annotation.
                              # NOTE: artifact_created / approval_requested are NOT in SPEC §6;
                              # do not emit them until a conformance-backed SPEC change.

workspaces/                   # RUNNER-LOCAL (non-normative, not a bus contract)
  TASK-001/
    artifacts/                # artifact files referenced by neutral progress lines
    omp.stdout                # NDJSON stream from runner
    omp.stderr                # stderr from runner
    progress.ndjson           # runner progress events (runner-local, NOT events.jsonl)

~/.config/commandr-runner/    # runner-private config (NOT under .agents/ — SPEC ADAPTER-2)
  policy.yml                  # optional per-host policy override
```
```

---

## Related

- [[entities/commandr]] — L3 bus specification
- [[entities/omp]] — L2 runner; RPC mode documentation
- [[research/omp-snapcompact-rpc]] — RPC protocol research
- [[syntheses/control-plane-expansion-plan]] — integration ladder
