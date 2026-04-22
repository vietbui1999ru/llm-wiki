# publish-ai-kb.sh
# Exports wiki index to ~/.claude/wiki/ai-kb/00-index.md
# Run after every ingest to keep Claude's session context current.
#
# Usage: ./scripts/publish-ai-kb.sh

WIKI="$HOME/repos/llm-wiki"
AI_KB="${AI_KB:-$HOME/.claude/wiki/ai-kb}"

if [[ ! -f "$WIKI/index.md" ]]; then
  echo "ERROR: wiki index not found at $WIKI/index.md" >&2
  exit 1
fi

mkdir -p "$AI_KB"
cp "$WIKI/index.md" "$AI_KB/00-index.md"
echo "Exported index.md → $AI_KB/00-index.md ($(wc -l < "$AI_KB/00-index.md") lines)"
