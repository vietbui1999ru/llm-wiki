#!/usr/bin/env bash
# commandr-omp-runner
# Commandr L2 runner wrapper for omp (oh-my-pi)
#
# Usage:
#   commandr-omp-runner --task <task.json> --workspace <dir> [--progress <file>]
#   cat task.json | commandr-omp-runner --workspace <dir>
#
# Interface (runner-agnostic):
#   INPUT:  Task packet JSON (stdin or --task file)
#   OUTPUT: NDJSON stream to stdout (turns, tool calls, completions)
#   PROGRESS: Optional file path; runner appends progress events as JSON lines
#   EXIT:   0 on success, 1 on failure

set -euo pipefail

# --- Parse args ---
TASK_FILE=""
WORKSPACE_DIR=""
PROGRESS_FILE=""
MODEL=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --task) TASK_FILE="$2"; shift 2 ;;
    --workspace) WORKSPACE_DIR="$2"; shift 2 ;;
    --progress) PROGRESS_FILE="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --help)
      sed -n '2,12p' "$0"
      exit 0
      ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# --- Validate ---
if [ -z "$WORKSPACE_DIR" ]; then
  echo "ERROR: --workspace required" >&2
  exit 1
fi

mkdir -p "$WORKSPACE_DIR"
cd "$WORKSPACE_DIR"

# --- Read task ---
if [ -n "$TASK_FILE" ]; then
  TASK_JSON="$(cat "$TASK_FILE")"
else
  TASK_JSON="$(cat)"
fi

# Extract prompt from task packet (simple jq-less fallback)
PROMPT="$(echo "$TASK_JSON" | grep -o '"prompt"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*:"//;s/"$//' || true)"
if [ -z "$PROMPT" ]; then
  PROMPT="$(echo "$TASK_JSON" | grep -o '"description"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*:"//;s/"$//' || true)"
fi
if [ -z "$PROMPT" ]; then
  PROMPT="$TASK_JSON"  # Fallback: use raw JSON as prompt
fi

# --- Progress helper ---
emit_progress() {
  local event="$1"
  local data="$2"
  local ts
  ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  local line="{\"timestamp\":\"$ts\",\"runner\":\"omp\",\"event\":\"$event\",\"data\":$data}"
  if [ -n "$PROGRESS_FILE" ]; then
    echo "$line" >> "$PROGRESS_FILE"
  fi
  # Also echo to stderr so caller can stream it
  echo "$line" >&2
}

emit_progress "start" "{\"workspace\":\"$WORKSPACE_DIR\",\"model\":\"${MODEL:-default}\"}"

# --- Build omp args ---
OMP_ARGS=(--no-lsp --mode json)
[ -n "$MODEL" ] && OMP_ARGS+=(--model "$MODEL")

# --- Run omp ---
emit_progress "omp_launch" "{\"prompt_length\":${#PROMPT}}"

# Run omp and tee output for progress extraction
$OMP_BIN "${OMP_ARGS[@]}" -p "$PROMPT" 2>"$WORKSPACE_DIR/omp.stderr" | tee "$WORKSPACE_DIR/omp.stdout" | while read -r line; do
  # Emit raw output line as progress
  emit_progress "output" "$(echo "$line" | sed 's/"/\\"/g' | sed 's/^/"/;s/$/"/')"
  echo "$line"  # Pass through to stdout
done

OMP_EXIT="${PIPESTATUS[0]}"

# --- Completion ---
if [ "$OMP_EXIT" -eq 0 ]; then
  emit_progress "complete" "{\"exit_code\":0}"
else
  emit_progress "fail" "{\"exit_code\":$OMP_EXIT,\"stderr\":\"$(head -c 200 "$WORKSPACE_DIR/omp.stderr" | sed 's/"/\\"/g')\"}"
fi

exit "$OMP_EXIT"
