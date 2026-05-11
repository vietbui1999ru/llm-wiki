#!/usr/bin/env bash
# install.sh — set up wiki-chat, wiki-index, wiki-mcp on any machine
# Run from the repo root after cloning: bash claude-setup/scripts/install.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

echo "==> Copying binaries to $BIN_DIR"
cp "$REPO_DIR/templates/wiki-chat"  "$BIN_DIR/wiki-chat"
cp "$REPO_DIR/templates/wiki-index" "$BIN_DIR/wiki-index"
cp "$REPO_DIR/templates/wiki-mcp"   "$BIN_DIR/wiki-mcp"
chmod +x "$BIN_DIR/wiki-chat" "$BIN_DIR/wiki-index" "$BIN_DIR/wiki-mcp"

echo "==> Installing Python deps"
pip install --quiet lightrag-hku ollama rich prompt_toolkit mcp numpy

echo "==> Installing git hook"
cp "$REPO_DIR/claude-setup/scripts/post-commit" "$REPO_DIR/.git/hooks/post-commit"
chmod +x "$REPO_DIR/.git/hooks/post-commit"

echo "==> Checking ollama"
if ! command -v ollama &>/dev/null; then
  echo "  [!] ollama not found — install from https://ollama.com then re-run"
  exit 1
fi

echo "==> Pulling ollama models (this may take a few minutes)"
ollama pull nomic-embed-text
ollama pull qwen2.5:3b

echo ""
echo "Done. Next step — build the knowledge graph (one-time, ~30-60 min):"
echo ""
echo "  wiki-index --full"
echo ""
echo "Then query interactively:"
echo "  wiki-chat"
echo ""
echo "For OpenCode MCP integration, add to ~/.config/opencode/opencode.json:"
echo '  "wiki-rag": {"type": "local", "command": ["'"$BIN_DIR"'/wiki-mcp"], "enabled": true}'
