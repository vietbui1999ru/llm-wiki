---
title: "Linux Machine Setup Guide"
type: concept
tags: [setup, tooling, workflow, claude-code, dotfiles]
sources: []
created: 2026-06-09
updated: 2026-06-09
---

# Linux Machine Setup Guide

Authoritative step-by-step guide for bootstrapping the full AI workflow on a fresh Linux machine after cloning this repo. Written for AI agents (Claude, Codex, Gemini) to execute directly. Run steps in order — ordering constraints are load-bearing.

---

## TL;DR — AI Agent Quickstart

If you are an AI assistant asked to "set up this machine," run these in order:

```bash
# 1. System deps
sudo apt-get update && sudo apt-get install -y git curl zsh jq stow build-essential

# 2. nvm + node (if not present)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
source ~/.nvm/nvm.sh && nvm install --lts && nvm use --lts

# 3. ollama (if not present)
curl -fsSL https://ollama.com/install.sh | sh

# 4. Clone repos — llm-wiki FIRST (dotfiles symlinks point here)
mkdir -p ~/repos
git clone git@github.com:vietbui1999ru/llm-wiki.git ~/repos/llm-wiki
git clone git@github.com:vietbui1999ru/dotfiles.git ~/dotfiles

# 5. Stow dotfiles → ~/.claude
cd ~/dotfiles && stow claude

# 6. Install Claude Code
npm install -g @anthropic-ai/claude-code

# 7. Wiki toolchain (uv + wiki binaries + git hook + ollama models)
cd ~/repos/llm-wiki && bash claude-setup/scripts/install.sh

# 8. Set ANTHROPIC_API_KEY (required for wiki-index quality; also used by Claude Code)
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.zshrc && source ~/.zshrc

# 9. First claude run — downloads plugins (superpowers, qmd, caveman, context7, etc.)
claude --version   # triggers plugin sync; may take 1-2 min

# 10. Build wiki LightRAG index (one-time; ~30-60 min; costs ~$0.50 via Claude Haiku)
wiki-index --full
```

---

## Prerequisites

### System packages

```bash
sudo apt-get update && sudo apt-get install -y \
  git curl zsh jq stow build-essential ca-certificates
```

| Tool | Why |
|------|-----|
| `git` | Clone repos, git hooks |
| `jq` | Status line, hook scripts |
| `stow` | Dotfiles symlink management |
| `zsh` | Shell (hooks use zsh shebang) |
| `curl` | nvm and ollama installers |

### Node.js (via nvm, recommended)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
source ~/.bashrc  # or ~/.zshrc
nvm install --lts
nvm use --lts
node --version   # should be >= 18
```

### ollama (local models for wiki-chat and wiki-index fallback)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
```

Ollama must be **running** when install.sh pulls models. Start it: `ollama serve &`

### uv (Python package manager — installed by install.sh)

No manual step needed. `install.sh` installs uv automatically via:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Step 1: Clone repositories

**Order matters.** Dotfiles commits symlinks with absolute paths pointing to `~/repos/llm-wiki`. If llm-wiki is missing when you stow, all rule symlinks in `~/.claude/rules/` will be broken.

```bash
mkdir -p ~/repos

# llm-wiki FIRST
git clone git@github.com:vietbui1999ru/llm-wiki.git ~/repos/llm-wiki

# dotfiles second
git clone git@github.com:vietbui1999ru/dotfiles.git ~/dotfiles
```

If you already cloned llm-wiki (you're reading this from inside it): skip the first clone.

---

## Step 2: Stow dotfiles → `~/.claude`

```bash
cd ~/dotfiles
stow claude
```

This creates `~/.claude/` with symlinks to `~/dotfiles/claude/.claude/`. Rules inside `~/.claude/rules/` are themselves symlinks → `~/repos/llm-wiki/claude-setup/rules/`.

**Verify:**
```bash
ls -la ~/.claude/rules/applied-ai.md   # should be a symlink
cat ~/.claude/CLAUDE.md | head -5      # should show "Global Claude Configuration"
```

---

## Step 3: Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

---

## Step 4: Set environment variables

Add to `~/.zshrc` (or `~/.bashrc`):

```bash
export ANTHROPIC_API_KEY="sk-ant-..."    # required: Claude Code + wiki-index quality
export PATH="$HOME/.local/bin:$PATH"     # required: wiki-chat, wiki-index, wiki-mcp
```

Reload:
```bash
source ~/.zshrc
```

`ANTHROPIC_API_KEY` is **required** for:
- Claude Code to work
- `wiki-index` to use Claude Haiku for extraction (falls back to local qwen2.5:3b without it, but lower quality)
- `wiki-mcp` synthesis backend

Optional keys (for council/multi-provider workflow):
- `GITHUB_TOKEN` (models:read) — GitHub Models endpoint for council voice B (openai/gpt-5.4)

---

## Step 5: Run wiki install.sh

From the repo root:

```bash
cd ~/repos/llm-wiki
bash claude-setup/scripts/install.sh
```

**What it does:**
1. Installs `uv` (if missing)
2. Copies `wiki-chat`, `wiki-index`, `wiki-mcp` → `~/.local/bin/` and makes them executable
3. Installs the post-commit git hook (auto-updates qmd index after wiki commits)
4. Pulls ollama models: `nomic-embed-text` (embeddings), `qwen2.5:3b` (fallback LLM)

**Expected output:**
```
==> uv X.Y.Z
==> Copying binaries to /home/user/.local/bin
==> Installing git hook
==> Pulling ollama models (may take a few minutes)
Done.
```

The script exits 1 if ollama is not found. Install it first (Step 0).

---

## Step 6: First Claude Code run — plugin installation

Run Claude Code once to trigger plugin downloads:

```bash
claude --version
# or just: claude
```

Plugins enabled in `~/.claude/settings.json` (sourced from dotfiles) auto-install on first run. This includes:

| Plugin | Purpose |
|--------|---------|
| `superpowers@claude-plugins-official` | Skills (brainstorming, debugging, tdd, etc.) |
| `qmd@qmd` | Wiki search MCP + `qmd` CLI |
| `caveman@caveman` | Caveman output style |
| `context7@claude-plugins-official` | Library docs lookup |
| `code-review@claude-plugins-official` | Review skills |
| `feature-dev@claude-plugins-official` | Feature development workflow |
| `ralph-loop@claude-plugins-official` | Multi-step task orchestration |
| `explanatory-output-style@claude-plugins-official` | Learning mode |
| `learning-output-style@claude-plugins-official` | Learning mode |

Plugin cache: `~/.claude/plugins/cache/` (not in dotfiles — downloaded fresh each machine).

The `qmd` CLI is **provided by the qmd plugin**, not a separate npm install. It becomes available after the first `claude` run completes plugin install.

---

## Step 7: Build the wiki LightRAG index (one-time)

```bash
wiki-index --full
```

**Cost warning:** Uses Claude Haiku for entity/relation extraction. A full index of ~200 wiki pages costs approximately $0.30–$0.80.

Without `ANTHROPIC_API_KEY`, falls back to local `qwen2.5:3b` via ollama (slower, lower quality).

**Expected time:** 30–60 minutes for full corpus.

**Check progress:**
```bash
cat ~/repos/llm-wiki/.lightrag/last-index.log
```

After this, qmd incremental indexing handles new pages automatically via the post-commit hook.

---

## Step 8: Verify everything works

```bash
# Claude Code
claude --version

# qmd CLI (from plugin — requires claude to have been run at least once)
qmd query "agent orchestration"

# wiki binaries
wiki-chat --help
wiki-index --status

# Hooks
ls -la ~/.claude/hooks/   # should list: context-threshold-check.sh, enforce-agent-whitelist.sh, etc.

# LightRAG index
wiki-index --status   # should show manifest stats, not empty
```

---

## Step 9: Optional — opencode MCP integration

If using opencode, add the wiki-mcp server:

```bash
mkdir -p ~/.config/opencode
# Edit ~/.config/opencode/opencode.json and add under "mcp":
```

```json
{
  "mcp": {
    "wiki-rag": {
      "type": "local",
      "command": ["~/.local/bin/wiki-mcp"],
      "enabled": true
    }
  }
}
```

For opencode model routing, source the env config:
```bash
echo 'source ~/repos/llm-wiki/templates/env-model-routing.sh' >> ~/.zshrc
```

---

## Gotchas and ordering constraints

| Constraint | Why |
|-----------|-----|
| Clone llm-wiki before stow | dotfiles rule symlinks have absolute path `~/repos/llm-wiki/...` |
| ollama before install.sh | install.sh exits 1 if `ollama` not found |
| claude run before qmd CLI | qmd binary comes from plugin, not npm global |
| ANTHROPIC_API_KEY before wiki-index --full | falls back to local model without it |
| `$HOME/.local/bin` in PATH before wiki-* | install.sh copies binaries there |

---

## File ownership map

After setup, these paths should exist:

```
~/.claude/                  ← symlinks from dotfiles stow
~/.claude/CLAUDE.md         ← real file in dotfiles
~/.claude/settings.json     ← real file in dotfiles
~/.claude/rules/            ← mix: some real files, some symlinks → llm-wiki/claude-setup/rules/
~/.claude/hooks/            ← real files in dotfiles
~/.claude/plugins/cache/    ← downloaded on first claude run (not in dotfiles)
~/.local/bin/wiki-chat      ← copied by install.sh
~/.local/bin/wiki-index     ← copied by install.sh
~/.local/bin/wiki-mcp       ← copied by install.sh
~/repos/llm-wiki/.git/hooks/post-commit  ← installed by install.sh
~/repos/llm-wiki/.lightrag/ ← created by wiki-index --full
```
