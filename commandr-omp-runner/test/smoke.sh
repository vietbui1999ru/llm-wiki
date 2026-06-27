#!/usr/bin/env bash
# commandr-omp-runner Level 1 smoke test
# Verifies bus integration via mocked PROGRESS_CMD, COMPLETE_CMD, OMP_BIN.
set -uo pipefail

RUNNER="$(cd "$(dirname "$0")/.." && pwd)/runner.sh"
PASS=0; FAIL=0

ok() {
  printf 'PASS: %s\n' "$1"; PASS=$((PASS+1))
}
fail() {
  printf 'FAIL: %s\n' "$1"; FAIL=$((FAIL+1))
}

# ─── Fixtures ─────────────────────────────────────────────────────────────────

TMP=""
setup() {
  TMP="$(mktemp -d)"
  export RUNNER_TEST_DIR="$TMP"
  mkdir -p "$TMP/bin" "$TMP/workspace" "$TMP/claimed"

  # Spy: progress — appends "<task-id> <note>" to progress.log
  cat > "$TMP/bin/progress" << 'MOCK'
#!/usr/bin/env bash
printf '%s %s\n' "$1" "$2" >> "$RUNNER_TEST_DIR/progress.log"
MOCK
  chmod +x "$TMP/bin/progress"
  export PROGRESS_CMD="$TMP/bin/progress"

  # Spy: complete — appends "<path> <result>" to complete.log
  cat > "$TMP/bin/complete" << 'MOCK'
#!/usr/bin/env bash
printf '%s %s\n' "$1" "$2" >> "$RUNNER_TEST_DIR/complete.log"
MOCK
  chmod +x "$TMP/bin/complete"
  export COMPLETE_CMD="$TMP/bin/complete"
}

teardown() { rm -rf "$TMP"; }

# Make a valid claimed packet; prints absolute path.
make_packet() {
  local id="${1:-TASK-001}"
  local path="$TMP/claimed/${id}.md"
  cat > "$path" << EOF
---
id: $id
type: implementation
scope: src/
---
## Context
Test task for smoke.
## Acceptance criteria
- [ ] done
## Files to touch
src/foo.ts
## Do not touch
.agents/
EOF
  printf '%s' "$path"
}

# Make a mock omp binary; stdout_content is what omp writes.
# stdout_content is written to a temp file so heredoc quoting is a non-issue.
make_omp() {
  local exit_code="${1:-0}"
  local stdout_content="${2:-}"
  local omp_env_log="$TMP/omp-env.log"
  local omp_out="$TMP/omp-fixture-output.txt"
  printf '%s\n' "$stdout_content" > "$omp_out"
  cat > "$TMP/bin/omp" << MOCK
#!/usr/bin/env bash
printf '%s\n' "\${AGENTS_TASK_ID:-UNSET}" >> "$omp_env_log"
cat "$omp_out"
exit $exit_code
MOCK
  chmod +x "$TMP/bin/omp"
  export OMP_BIN="$TMP/bin/omp"
}

# ─── Test 1: bus mode — omp succeeds ─────────────────────────────────────────

setup
make_omp 0
packet="$(make_packet TASK-001)"
bash "$RUNNER" --claimed "$packet" --workspace "$TMP/workspace" 2>/dev/null
ec=$?

[[ $ec -eq 0 ]]          && ok "T1: runner exits 0"    || fail "T1: runner exits 0"
grep -q "TASK-001 omp runner started" "$TMP/progress.log" 2>/dev/null \
                           && ok "T1: progress: started" || fail "T1: progress: started"
grep -q "TASK-001 omp complete"       "$TMP/progress.log" 2>/dev/null \
                           && ok "T1: progress: complete" || fail "T1: progress: complete"
grep -q "$packet pass"    "$TMP/complete.log" 2>/dev/null \
                           && ok "T1: complete: pass"   || fail "T1: complete: pass"
grep -q "TASK-001"        "$TMP/omp-env.log" 2>/dev/null \
                           && ok "T1: AGENTS_TASK_ID exported" || fail "T1: AGENTS_TASK_ID exported"
teardown

# ─── Test 2: bus mode — omp fails ────────────────────────────────────────────

setup
make_omp 1
packet="$(make_packet TASK-002)"
bash "$RUNNER" --claimed "$packet" --workspace "$TMP/workspace" 2>/dev/null || true

grep -q "TASK-002 omp failed:" "$TMP/progress.log" 2>/dev/null \
                               && ok "T2: progress: failed" || fail "T2: progress: failed"
grep -q "$packet fail"         "$TMP/complete.log" 2>/dev/null \
                               && ok "T2: complete: fail"   || fail "T2: complete: fail"
teardown

# ─── Test 3: offline mode — no bus calls ─────────────────────────────────────

setup
make_omp 0
# Use a simple JSON task file instead of --claimed
printf '{"prompt":"echo hello"}' > "$TMP/task.json"
bash "$RUNNER" --task "$TMP/task.json" --workspace "$TMP/workspace" 2>/dev/null
ec=$?

[[ $ec -eq 0 ]]           && ok "T3: runner exits 0"   || fail "T3: runner exits 0"
[[ ! -f "$TMP/progress.log" ]] \
                           && ok "T3: no bus progress"  || fail "T3: no bus progress"
[[ ! -f "$TMP/complete.log" ]] \
                           && ok "T3: no bus complete"  || fail "T3: no bus complete"
teardown

# ─── Test 4: policy hit — git push ───────────────────────────────────────────

setup
# git push triggers the "Remote mutation" medium-risk policy
risky_output='{"tool":"bash","command":"git push origin main"}'
make_omp 0 "$risky_output"
packet="$(make_packet TASK-003)"
bash "$RUNNER" --claimed "$packet" --workspace "$TMP/workspace" 2>/dev/null

grep -q "policy:" "$TMP/progress.log" 2>/dev/null \
                   && ok "T4: policy progress emitted"   || fail "T4: policy progress emitted"
artifact_count="$(find "$TMP/workspace/artifacts" -name 'policy-*.json' | wc -l | tr -d ' ')"
[[ "$artifact_count" -ge 1 ]] \
                   && ok "T4: policy artifact created"   || fail "T4: policy artifact created"
teardown

# ─── Test 5: missing frontmatter id — runner rejects ─────────────────────────

setup
make_omp 0
# Write a packet without a valid id field
bad_packet="$TMP/claimed/bad.md"
cat > "$bad_packet" << 'PACKET'
---
type: implementation
scope: src/
---
No id here.
PACKET
bash "$RUNNER" --claimed "$bad_packet" --workspace "$TMP/workspace" 2>/dev/null && ec=0 || ec=$?
[[ $ec -ne 0 ]] && ok "T5: rejects missing id" || fail "T5: rejects missing id"
teardown

# ─── Summary ──────────────────────────────────────────────────────────────────

printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"
[[ $FAIL -eq 0 ]]
