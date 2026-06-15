#!/usr/bin/env zsh
# install-claude-symlink.sh — point ~/.claude at this repo's claude-setup/
#
# Replaces the manual "merge skills/, rules/, plugins/" step in README/ONBOARDING.
# Behavior:
#   - ~/.claude is a symlink      → verify it points to this repo, fix if not
#   - ~/.claude is a real dir     → move to ~/.claude.bak-<timestamp>, then symlink
#   - ~/.claude does not exist    → symlink fresh
#   - ~/.claude is a regular file → refuse (user must remove it manually)
#
# Idempotent. Re-running after a clean symlink is a no-op.
# Run from anywhere: bash claude-setup/scripts/install-claude-symlink.sh
# Or with an explicit source: bash install-claude-symlink.sh /path/to/claude-setup

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../.." && pwd)"
SRC="${1:-$REPO_DIR/claude-setup}"
DST="$HOME/.claude"

if [[ ! -d "$SRC" ]]; then
  echo "error: source not a directory: $SRC" >&2
  exit 1
fi

SRC_REAL="$(cd "$SRC" && pwd -P)"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

# Resolve any existing path at $DST
if [[ -L "$DST" ]]; then
  EXIST_REAL="$(readlink -f "$DST" 2>/dev/null || greadlink -f "$DST" 2>/dev/null || echo "")"
  if [[ "$EXIST_REAL" == "$SRC_REAL" ]]; then
    echo "==> ~/.claude is already a symlink to $SRC_REAL — nothing to do"
    exit 0
  fi
  echo "==> ~/.claude is a symlink to ${EXIST_REAL:-<unresolved>}, not $SRC_REAL"
  echo "    Remove it first: rm ~/.claude"
  exit 1
fi

if [[ -d "$DST" ]]; then
  BACKUP="$HOME/.claude.bak-$TIMESTAMP"
  if [[ -e "$BACKUP" ]]; then
    echo "error: backup target already exists: $BACKUP" >&2
    echo "       move it aside and re-run" >&2
    exit 1
  fi
  echo "==> Backing up existing ~/.claude → $BACKUP"
  mv "$DST" "$BACKUP"
elif [[ -e "$DST" ]]; then
  echo "error: ~/.claude exists and is not a directory or symlink" >&2
  echo "       remove it manually and re-run: rm -f $DST" >&2
  exit 1
fi

ln -s "$SRC_REAL" "$DST"
echo "==> ~/.claude → $SRC_REAL"

echo ""
echo "Done. Claude Code will now load this repo's rules/, skills/, plugins/, hooks/."
