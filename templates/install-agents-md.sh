#!/usr/bin/env zsh
# install-agents-md.sh
# Copies templates/AGENTS.md to project roots.
#
# Usage:
#   ./install-agents-md.sh                    # scan ~/repos for git repos
#   ./install-agents-md.sh ~/repos/my-project # explicit targets
#   ./install-agents-md.sh --yes ~/repos/     # skip per-project confirm
#   ./install-agents-md.sh --dry-run          # preview only

set -euo pipefail

SCRIPT_DIR="${0:A:h}"
TEMPLATE="$SCRIPT_DIR/AGENTS.md"
AUTO_YES=0
DRY_RUN=0
SEARCH_ROOT="${HOME}/repos"
EXPLICIT_TARGETS=()

# ── parse args ───────────────────────────────────────────────────────────────

for arg in "$@"; do
  case "$arg" in
    --yes)     AUTO_YES=1 ;;
    --dry-run) DRY_RUN=1  ;;
    *)         EXPLICIT_TARGETS+=("$arg") ;;
  esac
done

# ── validate template ────────────────────────────────────────────────────────

if [[ ! -f "$TEMPLATE" ]]; then
  echo "Error: AGENTS.md template not found at $TEMPLATE"
  echo "Run from the llm-wiki/templates/ directory or pass the correct path."
  exit 1
fi

# ── find targets ─────────────────────────────────────────────────────────────

if [[ ${#EXPLICIT_TARGETS[@]} -gt 0 ]]; then
  TARGETS=("${EXPLICIT_TARGETS[@]}")
else
  # Auto-discover git repos under SEARCH_ROOT (depth 2 — immediate subdirs)
  echo "Scanning $SEARCH_ROOT for git repos..."
  TARGETS=()
  while IFS= read -r gitdir; do
    TARGETS+=("${gitdir:h}")  # strip /.git suffix → repo root
  done < <(find "$SEARCH_ROOT" -maxdepth 2 -name ".git" -type d 2>/dev/null | sort)
fi

if [[ ${#TARGETS[@]} -eq 0 ]]; then
  echo "No git repos found. Pass explicit paths or check SEARCH_ROOT=$SEARCH_ROOT"
  exit 0
fi

echo "\n${#TARGETS[@]} repo(s) found:\n"

# ── install ───────────────────────────────────────────────────────────────────

INSTALLED=0
SKIPPED=0
BACKED_UP=0

for repo in "${TARGETS[@]}"; do
  dest="$repo/AGENTS.md"
  name="${repo##*/}"

  # Skip non-directories
  [[ -d "$repo" ]] || continue

  # Skip this wiki repo itself
  [[ "$repo" == *llm-wiki* ]] && continue

  echo "  $name  ($repo)"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    [[ -f "$dest" ]] && echo "    → would overwrite existing AGENTS.md" \
                     || echo "    → would create AGENTS.md"
    continue
  fi

  # If AGENTS.md already exists, back it up
  if [[ -f "$dest" ]]; then
    if [[ "$AUTO_YES" -eq 0 ]]; then
      printf "    AGENTS.md exists. Overwrite? [y/N/b(ackup)] "
      read -r answer
      case "$answer" in
        y|Y) ;;
        b|B)
          cp "$dest" "${dest}.bak"
          echo "    → backed up to AGENTS.md.bak"
          (( BACKED_UP++ )) ;;
        *)
          echo "    → skipped"
          (( SKIPPED++ ))
          continue ;;
      esac
    else
      # --yes mode: backup automatically
      cp "$dest" "${dest}.bak"
      (( BACKED_UP++ ))
    fi
  fi

  cp "$TEMPLATE" "$dest"
  echo "    ✓ installed"
  (( INSTALLED++ ))

  # Add .agents/ to .gitignore if not already there
  gitignore="$repo/.gitignore"
  if [[ ! -f "$gitignore" ]] || ! grep -q "^\.agents/" "$gitignore" 2>/dev/null; then
    echo "\n.agents/" >> "$gitignore"
    echo "    ✓ added .agents/ to .gitignore"
  fi
done

echo "\nDone. Installed: $INSTALLED  Skipped: $SKIPPED  Backed up: $BACKED_UP"
echo "\nNext: create .agents/tasks.md in each project to start tracking work."
