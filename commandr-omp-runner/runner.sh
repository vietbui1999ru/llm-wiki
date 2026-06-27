#!/usr/bin/env bash
# commandr-omp-runner — Level 1 Commandr bus-integrated omp wrapper
#
# Usage (bus mode — pre-claimed packet):
#   commandr-omp-runner --claimed <abs-path> --workspace <dir> [--model <m>]
#
# Usage (offline / smoke mode — no bus integration):
#   commandr-omp-runner --task <file>|- --workspace <dir> [--model <m>]
#
# Bus mode: reads task id from packet frontmatter, exports AGENTS_TASK_ID,
# emits task_progress milestones, and calls bin/complete on exit.
#
# Env var testability seams:
#   OMP_BIN       omp binary (default: omp)
#   PROGRESS_CMD  bin/progress (default: progress)
#   COMPLETE_CMD  bin/complete (default: complete)
#
# Bus tools (progress, complete) self-locate via git rev-parse — run from
# inside the project repo or set CWD before invoking this script.

set -euo pipefail

OMP_BIN="${OMP_BIN:-omp}"
PROGRESS_CMD="${PROGRESS_CMD:-progress}"
COMPLETE_CMD="${COMPLETE_CMD:-complete}"

# ─── Parse args ───────────────────────────────────────────────────────────────

CLAIMED_PATH=""
TASK_FILE=""
WORKSPACE_DIR=""
MODEL=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --claimed)   CLAIMED_PATH="$2"; shift 2 ;;
    --task)      TASK_FILE="$2";    shift 2 ;;
    --workspace) WORKSPACE_DIR="$2"; shift 2 ;;
    --model)     MODEL="$2";        shift 2 ;;
    --help)      sed -n '2,18p' "$0"; exit 0 ;;
    *) printf 'commandr-omp-runner: unknown arg: %s\n' "$1" >&2; exit 1 ;;
  esac
done

[[ -n "$WORKSPACE_DIR" ]] || {
  printf 'commandr-omp-runner: --workspace required\n' >&2; exit 1
}
[[ -n "$CLAIMED_PATH" || -n "$TASK_FILE" ]] || {
  printf 'commandr-omp-runner: --claimed <path> or --task <file>|- required\n' >&2; exit 1
}

mkdir -p "$WORKSPACE_DIR/artifacts"

# ─── Load task packet ─────────────────────────────────────────────────────────

BUS_MODE=false
TASK_ID=""
PACKET_PATH=""
PACKET_CONTENT=""

if [[ -n "$CLAIMED_PATH" ]]; then
  BUS_MODE=true
  PACKET_PATH="$CLAIMED_PATH"
  [[ -f "$PACKET_PATH" ]] || {
    printf 'commandr-omp-runner: claimed packet not found: %s\n' "$PACKET_PATH" >&2; exit 1
  }
  PACKET_CONTENT="$(cat "$PACKET_PATH")"

  # Extract id from YAML frontmatter (same awk as bin/claim)
  TASK_ID="$(awk '
    NR==1 { if ($0 != "---") exit; next }
    /^---[[:space:]]*$/ { exit }
    index($0, "id:") == 1 {
      v = substr($0, 4); gsub(/^[[:space:]]+|[[:space:]]+$/, "", v); print v; exit
    }' "$PACKET_PATH")"
  [[ -n "$TASK_ID" ]] || {
    printf 'commandr-omp-runner: cannot read id from frontmatter: %s\n' "$PACKET_PATH" >&2; exit 1
  }
  export AGENTS_TASK_ID="$TASK_ID"
else
  if [[ "$TASK_FILE" == "-" ]]; then
    PACKET_CONTENT="$(cat)"
  else
    [[ -f "$TASK_FILE" ]] || {
      printf 'commandr-omp-runner: task file not found: %s\n' "$TASK_FILE" >&2; exit 1
    }
    PACKET_CONTENT="$(cat "$TASK_FILE")"
  fi
fi

# ─── Extract prompt ───────────────────────────────────────────────────────────

# Prefer markdown body (text after closing --- of frontmatter).
PROMPT="$(printf '%s\n' "$PACKET_CONTENT" | awk '
  BEGIN { in_front=0; past=0 }
  NR==1 && /^---[[:space:]]*$/ { in_front=1; next }
  in_front && /^---[[:space:]]*$/ { in_front=0; past=1; next }
  past { print }
' | sed '/^[[:space:]]*$/d')"

# Fallback: JSON "prompt" field, then "description", then raw content.
if [[ -z "$PROMPT" ]]; then
  PROMPT="$(printf '%s' "$PACKET_CONTENT" \
    | grep -o '"prompt"[[:space:]]*:[[:space:]]*"[^"]*"' \
    | sed 's/.*:"//;s/"$//' || true)"
fi
if [[ -z "$PROMPT" ]]; then
  PROMPT="$(printf '%s' "$PACKET_CONTENT" \
    | grep -o '"description"[[:space:]]*:[[:space:]]*"[^"]*"' \
    | sed 's/.*:"//;s/"$//' || true)"
fi
if [[ -z "$PROMPT" ]]; then
  PROMPT="$PACKET_CONTENT"
fi

# ─── Bus helpers ──────────────────────────────────────────────────────────────

bus_progress() {
  if $BUS_MODE; then
    "$PROGRESS_CMD" "$TASK_ID" "$1"
  fi
}

# ─── Policy table (runner-local; no blocking gate) ────────────────────────────

# The commit-time pre-commit-gate is the single enforceable human gate (SPEC §7).
# Policy hits are projected as neutral task_progress + workspace artifact.
POLICY_SEQ=0

policy_check_bash() {
  local cmd="$1"
  local risk="" reason=""

  if printf '%s' "$cmd" | grep -qE '\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)'; then
    risk=high; reason="Destructive recursive delete"
  elif printf '%s' "$cmd" | grep -qE '\bsudo\b'; then
    risk=high; reason="Privilege escalation"
  elif printf '%s' "$cmd" | grep -qE '\bdocker\s+(run|exec|rm)\b'; then
    risk=medium; reason="Container mutation"
  elif printf '%s' "$cmd" | grep -qE '\bgit\s+push\b'; then
    risk=medium; reason="Remote mutation"
  fi

  [[ -n "$risk" ]] || return 0

  POLICY_SEQ=$((POLICY_SEQ + 1))
  local ts artifact_name artifact_path
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  artifact_name="$(printf 'policy-%04d.json' "$POLICY_SEQ")"
  artifact_path="$WORKSPACE_DIR/artifacts/$artifact_name"

  local cmd_esc="${cmd//\\/\\\\}"; cmd_esc="${cmd_esc//\"/\\\"}"
  local reason_esc="${reason//\\/\\\\}"; reason_esc="${reason_esc//\"/\\\"}"
  printf '{"ts":"%s","tool":"bash","risk":"%s","reason":"%s","cmd":"%s"}\n' \
    "$ts" "$risk" "$reason_esc" "$cmd_esc" > "$artifact_path"

  bus_progress "policy: $reason ($risk risk); see $artifact_name"
}

# ─── Run omp ──────────────────────────────────────────────────────────────────

bus_progress "omp runner started"

OMP_ARGS=(--no-lsp --mode json)
[[ -n "$MODEL" ]] && OMP_ARGS+=(--model "$MODEL")

OMP_EXIT=0
"$OMP_BIN" "${OMP_ARGS[@]}" -p "$PROMPT" \
  > "$WORKSPACE_DIR/omp.stdout" \
  2> "$WORKSPACE_DIR/omp.stderr" || OMP_EXIT=$?

# Scan NDJSON output for policy violations; pass through to stdout.
# || [[ -n "$line" ]] handles files without a trailing newline.
while IFS= read -r line || [[ -n "$line" ]]; do
  if printf '%s' "$line" | grep -q '"tool"[[:space:]]*:[[:space:]]*"bash"'; then
    bash_cmd="$(printf '%s' "$line" \
      | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' \
      | sed 's/.*:"//;s/"$//' || true)"
    [[ -n "$bash_cmd" ]] && policy_check_bash "$bash_cmd"
  fi
  printf '%s\n' "$line"
done < "$WORKSPACE_DIR/omp.stdout"

# ─── Finalize ─────────────────────────────────────────────────────────────────

if [[ "$OMP_EXIT" -eq 0 ]]; then
  bus_progress "omp complete"
  $BUS_MODE && "$COMPLETE_CMD" "$PACKET_PATH" pass
else
  bus_progress "omp failed: exit $OMP_EXIT"
  $BUS_MODE && "$COMPLETE_CMD" "$PACKET_PATH" fail
fi

exit "$OMP_EXIT"
