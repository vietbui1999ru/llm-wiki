#!/bin/zsh
# link-claude-to-dotfiles.sh
# Wires ~/dotfiles/claude/.claude/* → ~/repos/llm-wiki/claude-setup/*
# Then fixes ~/.claude/rules/ which was not stow-managed.
#
# Idempotent — safe to re-run. Backs up any file it replaces.
# Run once after init-claude-setup.sh, and again when adding new files.
#
# Usage: ./scripts/link-claude-to-dotfiles.sh

set -euo pipefail

WIKI="$HOME/repos/llm-wiki"
SETUP="$WIKI/claude-setup"
DOTFILES_CLAUDE="$HOME/dotfiles/claude/.claude"
CLAUDE_DIR="$HOME/.claude"

# Link a file in dotfiles → llm-wiki.
# Skips if already correctly linked. Backs up and replaces otherwise.
link_file() {
  local src="$1"   # llm-wiki/claude-setup/...
  local dst="$2"   # dotfiles/claude/.claude/...

  if [[ ! -e "$src" ]]; then
    echo "  warn (source missing): $src"
    return
  fi

  # Already a correct symlink — skip
  if [[ -L "$dst" && "$(readlink "$dst")" == "$src" ]]; then
    echo "  ok: $(basename "$dst")"
    return
  fi

  # Exists but not our symlink — back up
  if [[ -e "$dst" || -L "$dst" ]]; then
    mv "$dst" "${dst}.bak"
    echo "  backup: $(basename "$dst").bak"
  fi

  ln -s "$src" "$dst"
  echo "  linked: $(basename "$dst")"
}

echo "=== Linking dotfiles/claude/.claude → llm-wiki/claude-setup ==="
echo ""

# ── Top-level files ──────────────────────────────────────────────────────────
echo "Top-level:"
link_file "$SETUP/CLAUDE.md"        "$DOTFILES_CLAUDE/CLAUDE.md"
link_file "$SETUP/settings.json"    "$DOTFILES_CLAUDE/settings.json"
link_file "$SETUP/keybindings.json" "$DOTFILES_CLAUDE/keybindings.json"

# ── Rules ────────────────────────────────────────────────────────────────────
# Rules were not in dotfiles before — add them now so stow can manage them.
echo ""
echo "Rules:"
mkdir -p "$DOTFILES_CLAUDE/rules"
for f in "$SETUP/rules/"*.md; do
  [[ -f "$f" ]] || continue
  link_file "$f" "$DOTFILES_CLAUDE/rules/$(basename "$f")"
done

# ── Agents ───────────────────────────────────────────────────────────────────
echo ""
echo "Agents:"
for f in "$SETUP/agents/"*.md; do
  [[ -f "$f" ]] || continue
  link_file "$f" "$DOTFILES_CLAUDE/agents/$(basename "$f")"
done

# ── Plugin config ─────────────────────────────────────────────────────────────
echo ""
echo "Plugin config:"
link_file "$SETUP/plugins/config.json"             "$DOTFILES_CLAUDE/plugins/config.json"
link_file "$SETUP/plugins/known_marketplaces.json" "$DOTFILES_CLAUDE/plugins/known_marketplaces.json"

# ── Fix ~/.claude/rules/ stow gap ────────────────────────────────────────────
# ~/.claude/rules/ is a real directory (not stow-managed). Remove it so stow
# can create the correct symlink on the next stow run.
echo ""
echo "=== Fixing ~/.claude/rules/ stow gap ==="

if [[ -L "$CLAUDE_DIR/rules" ]]; then
  echo "  ok: ~/.claude/rules is already a symlink"
elif [[ -d "$CLAUDE_DIR/rules" ]]; then
  # Verify the content matches what's now in llm-wiki before deleting
  real_files=$(find "$CLAUDE_DIR/rules" -maxdepth 1 -type f -name "*.md" | wc -l | tr -d ' ')
  setup_files=$(find "$SETUP/rules" -maxdepth 1 -type f -name "*.md" | wc -l | tr -d ' ')

  if [[ "$real_files" -gt "$setup_files" ]]; then
    echo "  ERROR: ~/.claude/rules/ has $real_files files but claude-setup/rules/ only has $setup_files."
    echo "  Run init-claude-setup.sh first to copy all rules, then re-run this script."
    exit 1
  fi

  echo "  removing real ~/.claude/rules/ ($real_files files already in claude-setup/)"
  rm -rf "$CLAUDE_DIR/rules"
  echo "  removed"

  echo "  re-running stow for claude package..."
  (cd "$HOME/dotfiles" && stow --restow claude 2>&1)
  echo "  stow done"
else
  echo "  running stow for claude package..."
  (cd "$HOME/dotfiles" && stow --restow claude 2>&1)
  echo "  stow done"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "=== Done ==="
echo ""
echo "Edit source of truth in:"
echo "  ~/repos/llm-wiki/claude-setup/"
echo ""
echo "Changes auto-reflect in:"
echo "  ~/dotfiles/claude/.claude/  (via symlinks)"
echo "  ~/.claude/                  (via stow)"
echo ""
echo "To sync rules to other providers (OpenCode / Codex / Cursor):"
echo "  ~/dotfiles/scripts/sync-agent-rules.sh"
echo ""
echo "To add a new agent:"
echo "  1. Create ~/repos/llm-wiki/claude-setup/agents/<name>.md"
echo "  2. Re-run this script to link it"
