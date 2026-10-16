#!/usr/bin/env bash
# PostToolUse hook: captures unresolved Bash failures to mistakes/raw-log.md
# Only logs exit code != 0. Signal/noise filtering happens in capture-mistake distillation.

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

# raw-log.md is tracked in git: mask secret-shaped text before it reaches the file.
redact() {
    python3 -c '
import re, sys
s = sys.stdin.read()
R = "[REDACTED]"
rules = [
    (r"(?i)(authorization\s*[:=]\s*)(\S+(\s+\S+)?)", r"\1" + R),
    (r"(?i)\b(bearer|basic|token)\s+[A-Za-z0-9._~+/=-]{8,}", r"\1 " + R),
    (r"(?i)\b([A-Za-z0-9_]*(key|token|secret|passw(or)?d|credential|auth)[A-Za-z0-9_]*\s*[:=]\s*)(\"[^\"]*\"|\x27[^\x27]*\x27|[^\s\"\x27&]+)", r"\1" + R),
    (r"(?i)(--?[a-z0-9-]*(key|token|secret|password)[a-z0-9-]*(\s+|=))[^\s-]\S*", r"\1" + R),
    (r"(://)[^/\s:@]+:[^/\s@]+@", r"\1" + R + "@"),
    (r"\b(sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|fc-[A-Za-z0-9]{16,}|xox[abpsr]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+)", R),
]
for pat, rep in rules:
    s = re.sub(pat, rep, s)
# Long mixed-case alphanumeric runs (likely keys). Plain hex such as git SHAs is kept.
s = re.sub(r"[A-Za-z0-9+/_=-]{32,}", lambda m: R if re.search("[a-z]", m.group()) and re.search("[A-Z]", m.group()) and re.search("[0-9]", m.group()) else m.group(), s)
sys.stdout.write(s)
' 2>/dev/null || echo "[REDACTION FAILED]"
}
CMD=$(printf '%s' "$CMD" | redact)
ERR=$(printf '%s' "$ERR" | redact)

LOGFILE="$HOME/repos/llm-wiki/mistakes/raw-log.md"
TS=$(date '+%Y-%m-%d %H:%M')

printf '\n## [%s] exit=%s\n```\n%s\n```\nerror: %s\n---\n' \
    "$TS" "$EXIT_CODE" "$CMD" "$ERR" >> "$LOGFILE"
