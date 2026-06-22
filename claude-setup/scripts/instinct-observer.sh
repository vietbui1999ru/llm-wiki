#!/usr/bin/env bash
# instinct-observer.sh — Record session-end marker for instinct clustering.
# Called from Stop hook. Never calls LLM — lightweight append only.
# Distillation (observations → instincts.json) runs via /instinct-triage.

PROJECT_ID=$(git rev-parse --short HEAD 2>/dev/null || echo "global")
CWD="$(pwd)"
STORE_DIR="$HOME/.claude/homunculus/projects/$PROJECT_ID"
mkdir -p "$STORE_DIR"

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

printf '{"timestamp":"%s","type":"session_end","cwd":"%s","project_id":"%s"}\n' \
    "$TIMESTAMP" "$CWD" "$PROJECT_ID" >> "$STORE_DIR/observations.jsonl"
