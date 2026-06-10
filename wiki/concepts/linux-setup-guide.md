---
title: "Linux Machine Setup Guide"
type: concept
tags: [setup, tooling, workflow, claude-code, opencode, headroom, dotfiles]
sources: []
created: 2026-06-09
updated: 2026-06-09
---

# Linux Machine Setup Guide

Authoritative step-by-step guide for bootstrapping the full AI workflow on a fresh Linux machine after cloning this repo. Written for AI agents (Claude, Codex, Gemini) to execute directly. Run steps in order — ordering constraints are load-bearing.

**Full AI stack covered:** Claude Code · opencode · pi · headroom · Gemini CLI · wiki toolchain (qmd + LightRAG)

---

## TL;DR — AI Agent Quickstart

```bash
# 1. System deps
sudo apt-get update && sudo apt-get install -y git curl zsh jq stow build-essential ca-certificates

# 2. nvm + node >= 18
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
source ~/.nvm/nvm.sh && nvm install --lts && nvm use --lts

# 3. Homebrew (needed for opencode + gemini-cli on Linux)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"  # or /usr/local for x86

# 4. ollama (local models)
curl -fsSL https://ollama.com/install.sh | sh

# 5. Clone repos — llm-wiki FIRST (dotfiles symlinks point here)
mkdir -p ~/repos
git clone git@github.com:vietbui1999ru/llm-wiki.git ~/repos/llm-wiki
git clone git@github.com:vietbui1999ru/dotfiles.git ~/dotfiles

# 6. Stow all dotfiles modules
cd ~/dotfiles && stow claude opencode gemini codex

# 7. Fix hardcoded macOS paths in opencode config
sed -i "s|/Users/vietquocbui|$HOME|g" ~/.config/opencode/opencode.json

# 8. Install Claude Code
npm install -g @anthropic-ai/claude-code

# 9. Install pi (council voice B / AFK loop worker)
npm install -g @earendil-works/pi-coding-agent

# 10. Install opencode
brew install opencode

# 11. Install Gemini CLI
npm install -g @google/gemini-cli

# 12. Install wiki toolchain (uv + wiki-chat/index/mcp + git hook + ollama models)
cd ~/repos/llm-wiki && bash claude-setup/scripts/install.sh

# 13. Install headroom (context compression) — requires uv from step 12
uv tool install headroom-ai

# 14. Set environment variables (edit and reload)
cat >> ~/.zshrc << 'EOF'
export ANTHROPIC_API_KEY="sk-ant-..."
export GITHUB_TOKEN="ghp_..."         # optional: council Voice B (GitHub Models)
export PATH="$HOME/.local/bin:$PATH"
source ~/repos/llm-wiki/templates/env-model-routing.sh  # opencode model routing
EOF
source ~/.zshrc

# 15. Fix qmd path in opencode.json (qmd installed by Claude Code plugin, not yet available)
#     Run this AFTER first `claude` invocation in step 16
# sed -i "s|/Users/vietquocbui/.nvm/versions/node/v[0-9.]*/bin/qmd|$(which qmd)|g" ~/.config/opencode/opencode.json

# 16. First claude run — downloads all plugins (qmd, superpowers, caveman, context7, etc.)
claude --version

# 17. Fix qmd path now that the binary exists
sed -i "s|/Users/vietquocbui/.nvm/versions/node/v[0-9.]*/bin/qmd|$(which qmd)|g" \
  ~/.config/opencode/opencode.json

# 18. Build wiki LightRAG index (one-time; ~30-60 min; costs ~$0.50 via Claude Haiku)
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
| `curl` | nvm, ollama, brew installers |

### Homebrew (Linux)

Required for `opencode` and `gemini-cli` (both distributed via brew formula):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# Add to shell after install:
echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.zshrc
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
```

On x86 Linux, path may be `/usr/local` instead of `/home/linuxbrew/.linuxbrew`.

### Node.js (via nvm)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
source ~/.bashrc   # or ~/.zshrc
nvm install --lts && nvm use --lts
node --version    # must be >= 18
```

### ollama (local models)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &     # start daemon before install.sh runs
```

Models pulled by `install.sh`:
- `nomic-embed-text` — embeddings for qmd and LightRAG
- `qwen2.5:3b` — local LLM fallback for wiki-mcp synthesis

---

## Step 1: Clone repositories

**Order matters.** Dotfiles commits symlinks with absolute paths pointing to `~/repos/llm-wiki`. Clone llm-wiki first or stow creates broken symlinks in `~/.claude/rules/`.

```bash
mkdir -p ~/repos

# llm-wiki FIRST
git clone git@github.com:vietbui1999ru/llm-wiki.git ~/repos/llm-wiki

# dotfiles second
git clone git@github.com:vietbui1999ru/dotfiles.git ~/dotfiles
```

If already inside the cloned repo: skip the first clone.

---

## Step 2: Stow dotfiles

Each dotfiles module maps to a different AI tool's config directory:

```bash
cd ~/dotfiles
stow claude     # → ~/.claude/ (Claude Code config, rules, hooks, settings)
stow opencode   # → ~/.config/opencode/ (opencode.json + plugins)
stow gemini     # → ~/.gemini/ (GEMINI.md, settings.json, commands/)
stow codex      # → ~/.codex/ (Codex config)
```

**Verify Claude:**
```bash
ls -la ~/.claude/rules/applied-ai.md   # should be a symlink → llm-wiki/claude-setup/rules/
cat ~/.claude/CLAUDE.md | head -3      # "Global Claude Configuration"
```

**Verify opencode:**
```bash
cat ~/.config/opencode/opencode.json | head -5   # should show $schema line
```

---

## Step 3: Fix hardcoded paths in opencode config

The opencode config was created on macOS and has `/Users/vietquocbui` hardcoded. Fix before first use:

```bash
sed -i "s|/Users/vietquocbui|$HOME|g" ~/.config/opencode/opencode.json
```

This fixes: skills paths, instruction paths, wiki-mcp command. The `qmd` path fix comes after Step 7 (qmd CLI is installed by the Claude Code plugin, not yet available).

---

## Step 4: Set environment variables

Add to `~/.zshrc`:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."    # required: Claude Code + wiki-index + wiki-mcp
export GITHUB_TOKEN="ghp_..."           # optional: council Voice B via GitHub Models
export PATH="$HOME/.local/bin:$PATH"    # wiki-chat, wiki-index, wiki-mcp

# opencode model routing (sets OPENCODE_MODEL_PRIMARY, _WORKER, _MINI, _COUNCIL, etc.)
source ~/repos/llm-wiki/templates/env-model-routing.sh
```

Reload: `source ~/.zshrc`

Key uses by tool:
| Key | Required by |
|-----|------------|
| `ANTHROPIC_API_KEY` | Claude Code, wiki-index (Haiku extraction), wiki-mcp synthesis |
| `GITHUB_TOKEN` (models:read scope) | Pi council voice (openai/gpt-5.4 via GitHub Models endpoint) |

---

## Step 5: Install AI tools

### Claude Code

```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

### Pi (council Voice B + AFK loop worker)

```bash
npm install -g @earendil-works/pi-coding-agent
pi --version
```

Pi is used as a stateless subprocess in the council workflow:
```bash
pi -p "Peer review: [decision]. Flag concerns." \
   --model openai-codex/gpt-5.3-codex \
   --no-session --no-extensions --no-skills
```

### opencode

```bash
brew install opencode
opencode --version
```

opencode is used for: TUI sessions with open models, council Voice C, warm-server pattern for headless API calls.

### Gemini CLI

```bash
npm install -g @google/gemini-cli
gemini --version   # should show 0.4x.x
```

Gemini CLI is configured via `~/.gemini/` (stowed in Step 2). On first use, authenticate:
```bash
gemini auth login
```

### Wiki toolchain (uv + wiki-chat/index/mcp + git hook + ollama models)

```bash
cd ~/repos/llm-wiki
bash claude-setup/scripts/install.sh
```

What it does:
1. Installs `uv` (Python package manager via curl)
2. Copies `wiki-chat`, `wiki-index`, `wiki-mcp` → `~/.local/bin/`
3. Installs post-commit git hook (auto-runs qmd indexing after wiki commits)
4. Pulls ollama models: `nomic-embed-text`, `qwen2.5:3b`

Exits 1 if `ollama` not found — start `ollama serve` first.

### headroom (context compression)

Requires `uv` from step above:

```bash
uv tool install headroom-ai
headroom --version
```

Usage patterns:
```bash
headroom wrap claude     # wraps Claude Code — transparent compression
headroom wrap opencode   # wraps opencode
headroom proxy --port 8787   # zero-code proxy; point ANTHROPIC_BASE_URL at it
```

See [[entities/headroom]] for deployment modes and CCR details.

---

## Step 6: First Claude Code run — plugin installation

```bash
claude --version
```

This triggers download of all enabled plugins from `~/.claude/settings.json`:

| Plugin | Purpose |
|--------|---------|
| `superpowers@claude-plugins-official` | Skills (brainstorming, debugging, tdd, etc.) |
| `qmd@qmd` | Wiki search MCP + `qmd` CLI binary |
| `caveman@caveman` | Compressed output style |
| `context7@claude-plugins-official` | Live library doc fetching |
| `code-review@claude-plugins-official` | PR review skills |
| `feature-dev@claude-plugins-official` | Guided feature development |
| `ralph-loop@claude-plugins-official` | Long-running autonomous agent loops |

Plugin cache: `~/.claude/plugins/cache/` — downloaded fresh, not in dotfiles.

**The `qmd` CLI comes from the plugin**, not npm. After this step, `qmd` is in PATH.

---

## Step 7: Fix qmd path in opencode config

Now that qmd is installed (via Claude Code plugin), update opencode.json:

```bash
sed -i "s|/Users/vietquocbui/.nvm/versions/node/v[0-9.]*/bin/qmd|$(which qmd)|g" \
  ~/.config/opencode/opencode.json
```

Verify:
```bash
grep '"qmd"' ~/.config/opencode/opencode.json -A 5
# "command" should show the correct qmd path on this machine
```

---

## Step 8: Build wiki LightRAG index (one-time)

```bash
wiki-index --full
```

**Cost warning:** Uses Claude Haiku by default when `ANTHROPIC_API_KEY` is set. ~200 wiki pages costs ~$0.30–$0.80. To use local ollama instead (free, slower):

```bash
unset ANTHROPIC_API_KEY && wiki-index --full && export ANTHROPIC_API_KEY="sk-ant-..."
```

**Time:** 30–60 min with Haiku; 2–4 hours with local qwen2.5:3b.

**Progress:**
```bash
tail -f ~/repos/llm-wiki/.lightrag/last-index.log
```

After this, the post-commit hook handles incremental updates automatically.

---

## Step 9: Verify

```bash
# Claude Code + plugins
claude --version
qmd query "agent orchestration" --limit 3

# Wiki binaries
wiki-index --status
wiki-chat --help

# opencode
opencode --version
cat ~/.config/opencode/opencode.json | jq '.mcp | keys'
# should include: "context7", "qmd", "wiki-rag"

# Pi
pi --version

# headroom
headroom --version

# Gemini CLI
gemini --version

# Hooks
ls ~/.claude/hooks/
# should include: context-threshold-check.sh, enforce-agent-whitelist.sh,
#                 enforce-bash-safety.sh, judge-reminder.sh, lint-autofix.sh, etc.
```

---

## Gotchas and ordering constraints

| Constraint | Why |
|-----------|-----|
| Clone llm-wiki before `stow` | dotfiles rule symlinks use absolute path `~/repos/llm-wiki/...` |
| `ollama serve` before `install.sh` | install.sh pulls models — needs daemon running |
| `claude --version` before `qmd` | qmd binary comes from Claude Code plugin |
| `claude --version` before qmd path fix in opencode.json | need `which qmd` to resolve |
| `uv` (install.sh) before `headroom-ai` | `uv tool install` requires uv |
| `ANTHROPIC_API_KEY` before `wiki-index --full` | falls back to local model without it |
| `$HOME/.local/bin` in PATH before `wiki-*` | install.sh copies binaries there |
| Fix opencode.json paths before using opencode | config has hardcoded `/Users/vietquocbui` |

---

## File ownership map

```
~/.claude/                         ← stow claude
~/.claude/CLAUDE.md                ← real file in dotfiles
~/.claude/settings.json            ← real file in dotfiles
~/.claude/rules/                   ← mix: real files + symlinks → llm-wiki/claude-setup/rules/
~/.claude/hooks/                   ← real files in dotfiles
~/.claude/plugins/cache/           ← downloaded on first claude run (not in dotfiles)

~/.config/opencode/opencode.json   ← stow opencode (paths fixed by sed in Step 3+7)
~/.config/opencode/plugins/        ← stow opencode

~/.gemini/GEMINI.md               ← stow gemini
~/.gemini/settings.json           ← stow gemini
~/.gemini/commands/               ← stow gemini

~/.codex/                         ← stow codex

~/.local/bin/wiki-chat            ← install.sh
~/.local/bin/wiki-index           ← install.sh
~/.local/bin/wiki-mcp             ← install.sh

~/repos/llm-wiki/.git/hooks/post-commit  ← install.sh
~/repos/llm-wiki/.lightrag/             ← wiki-index --full
```

---

## Related pages

- [[entities/headroom]] — context compression modes (proxy, wrap, library, MCP)
- [[entities/pi-agent]] — pi CLI, council workflow, pueue delegation
- [[entities/opencode]] — opencode TUI, headless API, warm-server pattern
- [[syntheses/lean-agentic-workflow]] — how these tools compose in practice
- [[concepts/council-pattern]] — when/how to invoke multi-vendor review
