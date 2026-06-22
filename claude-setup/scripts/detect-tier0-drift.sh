#!/usr/bin/env bash
# detect-tier0-drift.sh — Flag Tier 0 drift after wiki page commits.
# Called from the post-commit hook. Writes to pending-sync.md. Never calls LLM.

WIKI_ROOT="$(git rev-parse --show-toplevel)"
PENDING="$WIKI_ROOT/pending-sync.md"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

TIER0_FILES=(
    "claude-setup/rules/applied-ai.md"
    "mistakes/global-prevention-rules.md"
)

# Get changed files — handle first commit edge case
if git rev-parse HEAD~1 >/dev/null 2>&1; then
    CHANGED_FILES="$(git diff --name-only HEAD~1 HEAD 2>/dev/null)"
else
    CHANGED_FILES="$(git diff-tree --no-commit-id -r --name-only HEAD 2>/dev/null)"
fi

# Filter to wiki/ pages only
WIKI_CHANGED="$(printf '%s\n' "$CHANGED_FILES" | grep -E '^wiki/' || true)"
[[ -z "$WIKI_CHANGED" ]] && exit 0

# Initialize pending-sync.md if needed
if [[ ! -f "$PENDING" ]]; then
    printf '# pending-sync.md\n# Runtime state — gitignored. Do not edit manually.\n# Written by detect-tier0-drift.sh, resolved by /sync-tier0.\n' > "$PENDING"
fi

# Return 0 (true) if an identical pending entry already exists for this wiki_page+tier0_file pair
is_duplicate() {
    local wp="$1" tf="$2"
    [[ ! -f "$PENDING" ]] && return 1
    awk -v wp="$wp" -v tf="$tf" '
        /^---/ { wpage=""; tfile=""; status=""; next }
        /^wiki_page:/ { sub(/^wiki_page: /, ""); wpage=$0 }
        /^tier0_file:/ { sub(/^tier0_file: /, ""); tfile=$0 }
        /^status:/ { sub(/^status: /, ""); status=$0 }
        status != "" && wpage == wp && tfile == tf && status == "pending" { found=1; exit }
        END { exit !found }
    ' "$PENDING"
}

while IFS= read -r WIKI_FILE; do
    [[ -z "$WIKI_FILE" ]] && continue

    # Derive [[wikilink]] from git path: wiki/concepts/foo.md → [[concepts/foo]]
    WIKILINK_PATH="${WIKI_FILE#wiki/}"
    WIKILINK_PATH="${WIKILINK_PATH%.md}"
    WIKILINK="[[${WIKILINK_PATH}]]"

    for T0_FILE in "${TIER0_FILES[@]}"; do
        T0_FULL="$WIKI_ROOT/$T0_FILE"
        [[ ! -f "$T0_FULL" ]] && continue

        # -F: treat [[...]] as literal string, not regex
        if grep -qF "$WIKILINK" "$T0_FULL"; then
            is_duplicate "$WIKI_FILE" "$T0_FILE" && continue

            {
                printf '\n---\n'
                printf 'timestamp: %s\n' "$TIMESTAMP"
                printf 'wiki_page: %s\n' "$WIKI_FILE"
                printf 'tier0_file: %s\n' "$T0_FILE"
                printf 'wikilink: %s\n' "$WIKILINK"
                printf 'status: pending\n'
            } >> "$PENDING"
        fi
    done
done <<< "$WIKI_CHANGED"
