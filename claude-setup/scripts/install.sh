#!/usr/bin/env bash
# install.sh — set up wiki-chat, wiki-index, wiki-mcp on any machine
# Run from repo root: bash claude-setup/scripts/install.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

# ── uv ──────────────────────────────────────────────────────────────────────
if ! command -v uv &>/dev/null; then
  echo "==> Installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
echo "==> uv $(uv --version)"

# ── binaries ────────────────────────────────────────────────────────────────
echo "==> Copying binaries to $BIN_DIR"
cp "$REPO_DIR/templates/wiki-chat"  "$BIN_DIR/wiki-chat"
cp "$REPO_DIR/templates/wiki-index" "$BIN_DIR/wiki-index"
cp "$REPO_DIR/templates/wiki-mcp"   "$BIN_DIR/wiki-mcp"
chmod +x "$BIN_DIR/wiki-chat" "$BIN_DIR/wiki-index" "$BIN_DIR/wiki-mcp"

# Scripts use PEP 723 inline metadata — uv resolves deps on first run.
# No pip install needed. uv caches the venv; subsequent runs are instant.

# ── git hooks ───────────────────────────────────────────────────────────────
echo "==> Installing git hooks"
cp "$REPO_DIR/claude-setup/scripts/post-commit" "$REPO_DIR/.git/hooks/post-commit"
chmod +x "$REPO_DIR/.git/hooks/post-commit"
chmod +x "$REPO_DIR/claude-setup/scripts/detect-tier0-drift.sh"
# pre-push: rebuild docs-site/ and block the push if it drifts from wiki sources
cp "$REPO_DIR/claude-setup/scripts/pre-push" "$REPO_DIR/.git/hooks/pre-push"
chmod +x "$REPO_DIR/.git/hooks/pre-push"

# ── ollama ──────────────────────────────────────────────────────────────────
if ! command -v ollama &>/dev/null; then
  echo "  [!] ollama not found — install from https://ollama.com then re-run"
  exit 1
fi

echo "==> Pulling ollama embedding model (embeddings only; the LLM backend is OpenCode Go)"
ollama pull nomic-embed-text

# ── done ────────────────────────────────────────────────────────────────────
echo ""
echo "Done. First-run note: uv will build a venv on the first invocation (~30s, cached after)."
echo ""
echo "Next — point Claude Code at this repo's harness (backs up any existing ~/.claude):"
echo "  bash $REPO_DIR/claude-setup/scripts/install-claude-symlink.sh"
echo ""
echo "Then set OPENCODE_GO_API_KEY_LIGHTRAG (e.g. in ~/secrets/.env) and build the knowledge graph (one-time):"
echo "  wiki-index --test && wiki-index --full --yes"
echo ""
echo "Then query interactively:"
echo "  wiki-chat"
echo ""
echo "For OpenCode MCP, add to ~/.config/opencode/opencode.json under 'mcp':"
echo '  "wiki-rag": {"type": "local", "command": ["'"$BIN_DIR"'/wiki-mcp"], "enabled": true}'
