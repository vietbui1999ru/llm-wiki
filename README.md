# llm-wiki

A personal knowledge base on AI and agent engineering, maintained collaboratively by a human and an LLM. The human curates sources. The LLM writes, links, and maintains wiki pages. Both sides query and build on the accumulated knowledge over time.

This is not a static documentation site. It is a **compounding knowledge system**: each source ingested enriches existing pages, surfaces contradictions, and creates new cross-links. Over time it becomes a queryable second brain on its domain.

---

## Purpose

Most people who read about AI engineering forget 90% of it. This wiki makes forgetting structurally harder:

- Every source is summarized in a format designed for retrieval, not archiving
- Concepts are linked across sources so patterns become visible
- The LLM is the maintainer — it knows the schema, enforces cross-links, catches contradictions
- A mistakes log prevents the same errors from recurring across sessions

**Primary domain:** AI agent engineering — orchestration, context management, harness design, multi-model coordination, memory systems, tool design.

---

## Architecture

```
llm-wiki/
│
├── raw/                  # Source documents (web-scraped markdown, notes)
├── pdfs/                 # PDF sources (research papers)
│
├── wiki/                 # LLM-maintained knowledge pages
│   ├── summaries/        # One page per ingested source
│   ├── entities/         # Named things: tools, projects, people
│   ├── concepts/         # Ideas and patterns
│   ├── comparisons/      # Side-by-side analyses
│   └── syntheses/        # Cross-source conclusions
│
├── index.md              # Catalog of all pages (auto-updated on every ingest)
├── log.md                # Append-only history of all operations
│
├── mistakes/             # Error log and prevention system
│   ├── raw-log.md        # Hook-captured raw entries
│   ├── YYYY-MM-DD-*.md   # Structured mistake entries
│   ├── log.md            # Synthesize-mistakes run log
│   └── global-prevention-rules.md  # Distilled rules loaded every session
│
├── templates/            # Operational templates for the lean workflow
│   ├── AGENTS.md         # Cross-provider agent rules (copy to your projects)
│   ├── council.py        # Multi-model deliberation script (GitHub Models API)
│   ├── env-model-routing.sh         # Model routing env vars
│   ├── lean-compaction-plugin.ts    # OpenCode compaction + checkpoint plugin
│   └── install-agents-md.sh        # Script to install AGENTS.md to a project
│
├── claude-setup/         # Claude Code configuration (symlinked to ~/.claude)
│   ├── skills/           # Custom skills (wiki-context, pdf-ingest, etc.)
│   ├── rules/            # CLAUDE.md rule files (@-imported)
│   ├── plugins/          # Installed plugins (superpowers, caveman, qmd, etc.)
│   └── CLAUDE.md         # Root config with @-imports
│
├── CLAUDE.md             # Claude Code operating instructions for this repo
├── GUIDE.md              # User reference: skills, MCP tools, scenario playbooks
└── README.md             # This file
```

### Data flow

```
Source (URL, PDF, note)
    │
    ▼
raw/ or pdfs/          ← human drops file here
    │
    ▼
ingest operation       ← human says "ingest <filename>"
    │
    ├─→ wiki/summaries/<source>.md       (always created)
    ├─→ wiki/entities/<tool>.md          (if source introduces a named thing)
    ├─→ wiki/concepts/<pattern>.md       (if source introduces a pattern)
    ├─→ index.md                         (updated with new page entries)
    └─→ log.md                           (operation appended)
    │
    ▼
qmd index              ← BM25 + vector search over all wiki/ pages
    │
    ▼
query / grill / council  ← human asks questions; LLM retrieves and synthesizes
```

---

## Prerequisites

### Required

| Tool | Purpose | Install |
|---|---|---|
| [Claude Code](https://claude.ai/code) | LLM interface — runs the wiki operations | Download from claude.ai |
| [qmd](https://github.com/antiloger/qmd) | Hybrid search (BM25 + vector) over wiki pages | `cargo install qmd` or binary release |
| Git | Version control for wiki pages | Standard |

### Optional (for full lean workflow)

| Tool | Purpose | Install |
|---|---|---|
| [OpenCode](https://opencode.ai) | AFK agent orchestration, compaction hooks | `npm i -g opencode-ai` |
| GitHub PAT | Access GitHub Models API for cross-vendor council | [github.com/settings/tokens](https://github.com/settings/tokens) — `models:read` scope |
| Python 3.10+ + openai package | Run `council.py` | `pip install openai` |
| [Bun](https://bun.sh) | OpenCode plugin runtime | `curl -fsSL https://bun.sh/install \| bash` |

---

## Setup

### 1. Clone the repo

```bash
git clone <your-fork> ~/repos/llm-wiki
cd ~/repos/llm-wiki
```

### 2. Install qmd and index the wiki

```bash
# Install qmd (check repo for latest install method)
cargo install qmd

# Index the wiki
cd ~/repos/llm-wiki
qmd init
qmd add wiki/
```

### 3. Link Claude Code configuration

The `claude-setup/` directory contains skills, rules, and plugins for Claude Code. Symlink it to `~/.claude`:

```bash
# If starting fresh (no existing ~/.claude):
ln -s ~/repos/llm-wiki/claude-setup ~/.claude

# If you have an existing ~/.claude, merge manually:
# Copy skills/, rules/, plugins/ from claude-setup/ into your ~/.claude
```

Verify by opening Claude Code in any project — the wiki-context skill and superpowers plugin should be active.

### 4. Configure model routing (optional)

For the lean multi-model workflow, source the env vars:

```bash
# Add to ~/.zshrc or per-project .envrc (direnv)
source ~/repos/llm-wiki/templates/env-model-routing.sh

# For council (GitHub Models API):
export GITHUB_TOKEN=<your PAT with models:read scope>
```

### 5. Install council script (optional)

```bash
cp ~/repos/llm-wiki/templates/council.py ~/bin/council
chmod +x ~/bin/council
# Requires: pip install openai
```

### 6. Install OpenCode lean-session plugin (optional)

```bash
# The installed version should be JS, not TS
# Copy to OpenCode plugins dir:
cp ~/repos/llm-wiki/templates/lean-compaction-plugin.ts \
   ~/.config/opencode/plugins/lean-session.js
# Note: compile TS → JS first if OpenCode doesn't handle TS natively
```

---

## Main Use Cases

### 1. Add a source to the wiki

Drop any markdown file, scraped article, or note into `raw/`:

```bash
cp ~/Downloads/interesting-article.md ~/repos/llm-wiki/raw/
```

Then in Claude Code:

```
ingest interesting-article.md
```

Claude reads the source, asks 3–5 comprehension questions, then writes:
- A summary page in `wiki/summaries/`
- Entity or concept pages for anything new
- Updates `index.md` and `log.md`

To skip the comprehension check: `"skip review"` or `"just ingest it"`.

### 2. Ask a question

```
search the wiki for context degradation strategies
```

Claude invokes `wiki-context` skill → searches qmd → loads relevant pages → synthesizes an answer with `[[page]]` citations.

### 3. Ingest a PDF (research paper)

```bash
cp ~/Downloads/paper.pdf ~/repos/llm-wiki/pdfs/
```

In Claude Code: `ingest paper.pdf` → triggers `pdf-ingest` skill (uses Docling to parse → comprehension check → wiki pages).

### 4. Run a council on a design decision

```bash
# Quick 2-voice sanity check
council "should we use worktrees or containers for agent isolation?"

# Full 3-stage: peer review + Chairman synthesis
council --chairman "what's the right memory architecture for a long-horizon agent?"
```

### 5. Lint the wiki

```
lint the wiki
```

Claude scans for: orphan pages, stale claims contradicted by newer sources, concepts mentioned without their own page, and suggests 3–5 next sources to find.

### 6. Copy the agent workflow to a project

```bash
# Install AGENTS.md to a project
~/repos/llm-wiki/templates/install-agents-md.sh /path/to/your/project
```

This copies the lean workflow rules (grill→PRD→AFK loop→verify), council auto-triggers, and self-correction protocol to your project.

---

## Wiki Page Schema

Every wiki page requires this frontmatter:

```yaml
---
title: "Page Title"
type: entity | concept | summary | comparison | synthesis
tags: [tag1, tag2]
sources: ["raw/filename.md"]   # files in raw/ that informed this page
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Optional fields:
```yaml
status: stub                   # thin page; expand when source is ingested
```

### Page types

| Type | Location | Purpose |
|---|---|---|
| `summary` | `wiki/summaries/` | One page per ingested source |
| `entity` | `wiki/entities/` | Named things: tools, projects, people, systems |
| `concept` | `wiki/concepts/` | Ideas, patterns, techniques |
| `comparison` | `wiki/comparisons/` | Side-by-side analysis of two+ approaches |
| `synthesis` | `wiki/syntheses/` | Cross-source conclusions; your actual opinions |

### Cross-linking

Use Obsidian-style wikilinks:
```markdown
See [[concepts/context-compression]] and [[entities/opencode]].
```

Links in `index.md` use the same syntax. Every new page must be added to `index.md`.

---

## Mistakes System

Every session-level error is logged to prevent recurrence:

```
mistakes/
├── raw-log.md              # Hook-captured raw entries (auto-populated)
├── YYYY-MM-DD-<topic>.md   # Structured mistake entry per incident
├── log.md                  # Synthesize-mistakes run history
└── global-prevention-rules.md  # Max 30 lines of distilled rules, loaded every session
```

`global-prevention-rules.md` is @-imported into `CLAUDE.md` and loaded at every session start — the rules are always active. Individual mistake files provide context; the global file provides the actionable rules.

When a mistake is made: `capture-mistake` skill files it. Periodically: `synthesize-mistakes` skill distills new entries into `global-prevention-rules.md`.

---

## Adapting to Your Own Workflow

This wiki is domain-specific (AI/agent engineering) and person-specific (one person's workflow). To adapt:

### Minimal adoption (wiki only)

1. Fork this repo, clear `raw/`, `wiki/`, `index.md`, `log.md`
2. Keep `CLAUDE.md`, `claude-setup/`, `mistakes/global-prevention-rules.md`
3. Start ingesting sources in your domain
4. The schema, cross-linking convention, and ingest workflow carry over unchanged

### Change the domain

Edit `CLAUDE.md` to describe your domain. The wiki taxonomy (summaries/entities/concepts/comparisons/syntheses) is domain-agnostic — it works for any knowledge area.

### Add the lean workflow to an existing project

```bash
# Copy AGENTS.md to any project
~/repos/llm-wiki/templates/install-agents-md.sh /path/to/project

# The AGENTS.md encodes:
# - grill→PRD→AFK loop→verify workflow
# - Council auto-trigger rules
# - Model routing via env vars
# - Self-correction protocol (qmd query before deviating)
# - .agents/ session state (tasks.md, checkpoint.md, decisions.md)
```

### Use council without the full wiki

```bash
# council.py works standalone — just needs GITHUB_TOKEN
export GITHUB_TOKEN=<your PAT>
pip install openai
council "your question here"
council --chairman "your question here"
```

---

## Key Concepts (Quick Reference)

| Concept | What it is | Wiki page |
|---|---|---|
| Lean workflow | grill→PRD→AFK loop→verify cycle | `syntheses/lean-agentic-workflow` |
| Council pattern | 3-stage multi-model deliberation | `concepts/council-pattern` |
| Worktree isolation | Git worktrees for parallel agent safety | `concepts/worktree-isolation` |
| Clear-over-compact | Fresh context per task > compaction | `concepts/context-compression` |
| Memory Bank | `_memory/` + repomix for cross-session state | `concepts/memory-bank-pattern` |
| Rules vs hooks | Static files vs dynamic injection | `concepts/rules-vs-hooks` |
| Multi-vendor review | Cross-provider adversarial review | `concepts/multi-vendor-adversarial-review` |
| Agent self-correction | Wiki-as-runtime-oracle for deviation detection | `concepts/agent-self-correction` |

---

## Authoring Rules (for the LLM)

These rules apply whenever Claude writes or updates wiki pages. They are distilled from the `mistakes/` log:

- **Cite sources precisely.** Self-reported README claims are not benchmarks. Write `(claimed, unverified)` for unverified numbers.
- **Verify model names.** Check against a public provider catalog before adding to routing tables.
- **Keep index.md in sync.** After updating a page's core claim, grep for all cross-references and check for drift.
- **Respect status flags.** `documented-not-adopted` patterns must be labeled in the index and never described as "preferred" or "more reliable."
- **One thing per page.** Concept pages cover one concept. Entity pages cover one entity. Split when scope creeps.
- **Never modify `raw/` or `pdfs/`.** These are immutable source records.

Full rules in `mistakes/global-prevention-rules.md`.

---

## License

This repo structure and tooling is open. The wiki content itself is personal knowledge — adapt freely, attribute if you reproduce wholesale.
