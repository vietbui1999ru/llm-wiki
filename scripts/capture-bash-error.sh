#!/usr/bin/env bash
# PostToolUse hook: captures unresolved Bash failures to mistakes/raw-log.md
# Only logs exit code != 0. Signal/noise filtering happens in synthesize-mistakes skill.

set -euo pipefail

INPUT=$(cat)

EXIT_CODE=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    r = d.get('tool_result', d.get('result', {}))
    # try multiple field names different CC versions use
    code = r.get('exit_code', r.get('returncode', r.get('exitCode', None)))
    print('' if code is None else str(code))
except Exception:
    print('')
" 2>/dev/null | tr -d '[:space:]')

# Skip if no exit code or exit code is 0
[ -z "$EXIT_CODE" ] || [ "$EXIT_CODE" = "0" ] || [ "$EXIT_CODE" = "None" ] && exit 0

CMD=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', '')[:400])
except Exception:
    print('')
" 2>/dev/null)

ERR=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    r = d.get('tool_result', d.get('result', {}))
    out = r.get('output', r.get('content', r.get('stderr', '')))
    if isinstance(out, list):
        out = ' '.join(str(x) for x in out)
    print(str(out)[:600])
except Exception:
    print('')
" 2>/dev/null)

# Only write if we got a command (guard against spurious fires)
[ -z "$CMD" ] && exit 0

LOGFILE="$HOME/repos/llm-wiki/mistakes/raw-log.md"
TS=$(date '+%Y-%m-%d %H:%M')

printf '\n## [%s] exit=%s\n```\n%s\n```\nerror: %s\n---\n' \
    "$TS" "$EXIT_CODE" "$CMD" "$ERR" >> "$LOGFILE"
