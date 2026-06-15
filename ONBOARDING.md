---
title: "Onboarding: Run llm-wiki as an Agent-First Harness"
type: guide
audience: adopters
created: 2026-06-12
updated: 2026-06-12
---

# Onboarding: Run llm-wiki as an Agent-First Harness

This guide is for someone adopting this repo as their own **agent-first knowledge harness** —
a system where an AI coding agent does the reading, writing, linking, and quality-checking, and
you stay in the loop as the curator and decision-maker.

It is a tutorial, not a reference. Follow it top to bottom once. For deep operational detail
afterward, see [`GUIDE.md`](GUIDE.md) (skills, MCP tools, scenario playbooks) and
[`README.md`](README.md) (architecture and install detail).

---

## What "agent-first, human-second" means here

Most documentation is written for humans, and an AI agent reads it as a side effect. This repo
inverts the priority: **the primary reader is the agent**, and the human-readable view is a
projection of the same content.

That inversion is cheaper than it sounds, because of one finding the wiki itself has on file
(see [[concepts/software-documentation]]):

> Practices that make docs LLM-friendly are the same practices that make docs human-friendly.

So you do not maintain two things. You maintain one corpus that is:

- **Self-contained per page** — an agent retrieves a single page out of context and it still
  makes sense. Humans benefit identically.
- **Consistently named** — stable terminology so retrieval matches and humans don't get
  whiplash from synonyms.
- **Semantically structured** — heading hierarchy and `[[wikilinks]]` encode relationships the
  agent (and a reader) can traverse.

The division of labor:

| You (human)                                       | The agent                                  |
| ------------------------------------------------- | ------------------------------------------ |
| Curate sources (drop files into `raw/` / `pdfs/`) | Read sources fully                         |
| Ask questions, make decisions                     | Write summary / concept / entity pages     |
| Approve direction, catch bad premises             | Maintain cross-links, `index.md`, `log.md` |
| Review periodically                               | Catch contradictions, log its own mistakes |

The agent **owns the wiki layer**. You **own the curation and the calls**.

---

## The harness, in one picture

This repo is not just a folder of markdown. It is a harness with four moving parts that make the
agent reliable across sessions:

1. **Rules** — `CLAUDE.md` + `@`-imported rule files + `mistakes/global-prevention-rules.md`.
   Loaded every session. They encode model-tier routing, epistemic discipline ("default stance:
   uncertain"), and citation rules. This is the agent's standing operating procedure.
2. **Skills** — invokable procedures (`wiki-context`, `pdf-ingest`, `capture-mistake`, `judge`,
   `council`, …). Deterministic triggers decide when each fires. See [[concepts/agent-skills]].
3. **Hooks** — a post-commit hook re-indexes the knowledge graph automatically after every
   wiki commit. The human never re-runs indexing by hand.
4. **Retrieval (RAG)** — three tools over the same corpus: in-session search (`wiki-context` via
   qmd), a standalone terminal Q&A TUI (`wiki-chat`), and an MCP server (`wiki-mcp`) for other
   agents. See [[syntheses/local-rag-wiki]].

The compounding effect: every source you ingest enriches existing pages, surfaces
contradictions, and adds cross-links — so the agent's answers get better over time instead of
staying flat.

---

## 15-minute quickstart

> Prerequisites and full install detail live in [`README.md`](README.md#setup). This is the
> condensed path to a working loop.

### 1. Clone and install

Prerequisites (install these yourself first — `install.sh` does **not** install them):

| Tool | Why | Install |
|---|---|---|
| [qmd](https://github.com/antiloger/qmd) | Hybrid search; called by the `post-commit` hook | `cargo install qmd` or [binary release](https://github.com/antiloger/qmd/releases) |
| [Node.js](https://nodejs.org) | Runs the `docs-site/` generator + `pre-push` hook | `nvm install --lts` or distro package |
| [zsh](https://www.zsh.org) | The shipped `post-commit` and `pre-push` hooks have `#!/bin/zsh` shebangs | `sudo apt install zsh` (or rewrite the shebangs to `bash`) |
| [ollama](https://ollama.com) | Local LLM for `wiki-index` / `wiki-chat` | Download from ollama.com |

Then:

```bash
git clone git@github.com:vietbui1999ru/llm-wiki.git ~/repos/llm-wiki
cd ~/repos/llm-wiki
bash claude-setup/scripts/install.sh
```

`install.sh` handles the rest: `uv` (if missing), copies `wiki-index` / `wiki-chat` / `wiki-mcp`
to `~/.local/bin`, pulls `nomic-embed-text` and `qwen2.5:3b` via ollama, installs the
`post-commit` and `pre-push` git hooks. Ensure `~/.local/bin` is on `$PATH`:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

### 2. Point Claude Code at the harness config

```bash
# Fresh machine (no existing ~/.claude):
ln -s ~/repos/llm-wiki/claude-setup ~/.claude
# Existing ~/.claude: merge skills/, rules/, plugins/ manually.
```

This is what makes a session **agent-first**: the rules, skills, and prevention log load
automatically.

### 3. Run your first ingest

```bash
cp ~/Downloads/some-article.md ~/repos/llm-wiki/raw/
```

In Claude Code:

```
ingest some-article.md
```

The agent asks a few comprehension questions (to confirm *you* understood the source, not just
it), then writes the pages, updates `index.md` and `log.md`, and commits. The post-commit hook
indexes the new pages in the background. Skip the questions with `"just ingest it"`.

### 4. Query what you just built

```
search the wiki for <topic from the article>
```

The `wiki-context` skill searches, loads the relevant pages, and the agent answers with
`[[page]]` citations. That round trip — curate → ingest → query — is the entire system.

---

## The daily loop

Once set up, day-to-day work is one repeating cycle:

```
   you curate a source        →   raw/ or pdfs/
        │
   "ingest <file>"            →   agent reads, writes pages, links, commits
        │
   post-commit hook           →   qmd + graph index update (automatic)
        │
   later sessions             →   "search the wiki for X" pulls it back, cited
```

Two habits keep it healthy:

- **`lint the wiki`** periodically — the agent scans for orphan pages, stale claims, and missing
  concepts, and suggests sources to ingest next.
- **Let it log its own mistakes** — when the agent self-corrects, the `capture-mistake` skill
  files the error so the same one doesn't recur. Distilled rules live in
  `mistakes/global-prevention-rules.md` and load every session.

---

## What makes the agent trustworthy

The harness encodes a few rules worth understanding before you rely on its output (full set in
[`README.md`](README.md#authoring-rules-for-the-llm) and `mistakes/global-prevention-rules.md`):

- **Default stance: uncertain.** Claims are provisional unless backed by a cited wiki page or
  verified current docs. Unsourced claims are prefixed `(training data — verify)`.
- **Numbers need provenance.** Self-reported README figures are not benchmarks; unverified
  numbers are marked `(claimed, unverified)`.
- **Model-tier routing.** The agent classifies task complexity (Haiku / Sonnet / Opus) before
  acting and sets the model explicitly when spawning sub-agents. See [[concepts/model-tier-routing]].

These are not decoration — they are why an agent-maintained knowledge base doesn't quietly rot
into confident nonsense.

---

## Make it yours

### Swap the domain

The taxonomy (`summaries` / `entities` / `concepts` / `comparisons` / `syntheses` / `systems` /
`patterns`) is domain-agnostic. To repurpose:

1. Fork, then clear `raw/`, `wiki/`, `index.md`, `log.md`.
2. Keep `CLAUDE.md`, `claude-setup/`, and `mistakes/global-prevention-rules.md`.
3. Edit `CLAUDE.md` to describe your domain.
4. Start ingesting. The harness behavior carries over unchanged.

### Add the lean workflow to an existing project

```bash
~/repos/llm-wiki/templates/install-agents-md.sh /path/to/project
```

This drops a cross-provider `AGENTS.md` so the same agent rules apply in your other repos.

### Tune the rules

Rule files under `claude-setup/rules/` are `@`-imported into `CLAUDE.md`. Edit them to change
model routing, communication style, or skill triggers. Changes take effect next session.

---

## Where to go next

| You want to… | Go to |
|---|---|
| Look up a specific skill, MCP tool, or scenario playbook | [`GUIDE.md`](GUIDE.md) |
| Understand the system architecture (diagrams) | [`docs/architecture.md`](docs/architecture.md) |
| See the day-to-day and multi-machine workflows | [`docs/workflows.md`](docs/workflows.md) |
| Read the knowledge itself | the published docs site, or `wiki/` directly |
| Install detail, prerequisites, RAG cost warnings | [`README.md`](README.md) |

---

*Adopting this means accepting one trade: you give the agent ownership of a layer, and in return
you stop forgetting 90% of what you read. Curate well, review often, and let it compound.*
