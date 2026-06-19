#!/usr/bin/env bash
# commandr-omp-runner bootstrap
# One-time setup: installs omp, pi-headroom plugin, and runner config

set -euo pipefail

RUNNER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="${RUNNER_DIR}/../pi-headroom"
OMP_BIN="${OMP_BIN:-$(command -v omp 2>/dev/null || true)}"

echo "=== commandr-omp-runner bootstrap ==="

# 1. Install omp if missing
if [ -z "$OMP_BIN" ] || ! command -v omp >/dev/null 2>&1; then
  echo "omp not found. Installing..."
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL https://omp.sh/install | sh
  else
    echo "ERROR: curl not found. Install omp manually: https://omp.sh"
    exit 1
  fi
  # Re-check PATH
  OMP_BIN="$(command -v omp 2>/dev/null || true)"
  if [ -z "$OMP_BIN" ]; then
    echo "ERROR: omp installed but not in PATH. Add ~/.bun/bin to PATH."
    exit 1
  fi
fi

echo "omp: $OMP_BIN ($($OMP_BIN --version 2>/dev/null || echo 'unknown version'))"

# 2. Install pi-headroom plugin
if [ -d "$PLUGIN_DIR" ]; then
  echo "Installing pi-headroom plugin..."
  cd "$PLUGIN_DIR"
  if [ ! -d "node_modules" ]; then
    npm install 2>/dev/null || echo "WARN: npm install failed; plugin may not function"
  fi
  $OMP_BIN install "$PLUGIN_DIR" 2>/dev/null || echo "WARN: plugin install failed; may already be installed"
else
  echo "WARN: pi-headroom plugin not found at $PLUGIN_DIR"
fi

# 3. Verify plugin loaded
if $OMP_BIN list 2>/dev/null | grep -q "pi-headroom"; then
  echo "pi-headroom: installed"
else
  echo "WARN: pi-headroom not showing in omp list (may need manual install)"
fi

# 4. Copy hook + tool to agent dirs (fallback if plugin discovery fails)
mkdir -p ~/.omp/agent/hooks/pre ~/.omp/agent/tools/headroom-retrieve
if [ -f "$PLUGIN_DIR/hooks/pre/headroom-compress.ts" ]; then
  cp "$PLUGIN_DIR/hooks/pre/headroom-compress.ts" ~/.omp/agent/hooks/pre/
  echo "hook: ~/.omp/agent/hooks/pre/headroom-compress.ts"
fi
if [ -f "$PLUGIN_DIR/tools/headroom-retrieve/index.ts" ]; then
  cp "$PLUGIN_DIR/tools/headroom-retrieve/index.ts" ~/.omp/agent/tools/headroom-retrieve/
  echo "tool: ~/.omp/agent/tools/headroom-retrieve/index.ts"
fi

echo "=== bootstrap complete ==="
