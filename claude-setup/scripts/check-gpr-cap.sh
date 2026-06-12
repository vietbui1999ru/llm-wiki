#!/usr/bin/env bash
# Tier-0 size gate for mistakes/global-prevention-rules.md.
#
# This file is @-imported by the wiki's CLAUDE.md and loads into EVERY wiki
# session. Unbounded growth = unbounded startup cost + diluted attention.
# When this gate fires, do ONE of:
#   - prune a stale/low-value rule, or
#   - promote a section to a pull page (e.g. wiki/concepts/model-tier-routing.md)
#     and leave a one-line pointer behind.
#
# Counts non-blank lines (structure + rules), ignoring blank separators.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
FILE="$ROOT/mistakes/global-prevention-rules.md"
CAP=45

[[ -f "$FILE" ]] || { echo "check-gpr-cap: $FILE not found" >&2; exit 0; }

LINES="$(awk 'NF' "$FILE" | wc -l | tr -d ' ')"

if (( LINES > CAP )); then
  echo "✗ global-prevention-rules.md: $LINES non-blank lines (cap $CAP)." >&2
  echo "  Prune a stale rule or promote a section to a pull page before committing." >&2
  exit 1
fi

echo "✓ global-prevention-rules.md: $LINES/$CAP non-blank lines"
