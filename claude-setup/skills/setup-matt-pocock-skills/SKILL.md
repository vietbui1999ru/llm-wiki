---
name: setup-matt-pocock-skills
description: Sets up an `## Agent skills` block in AGENTS.md/CLAUDE.md and `docs/agents/` so the engineering skills know this repo's issue tracker (GitHub or local markdown), triage label vocabulary, and domain doc layout. Run before first use of `to-issues`, `to-prd`, `triage`, `diagnose`, `tdd`, `improve-codebase-architecture`, or `zoom-out` — or if those skills appear to be missing context about the issue tracker, triage labels, or domain docs.
disable-model-invocation: true
---

# Setup Matt Pocock's Skills

Scaffold the per-repo configuration that the engineering skills assume:

- **Issue tracker** — where issues live (GitHub by default; local markdown is also supported)
- **Triage labels** — the strings used for the five canonical triage roles
- **Domain docs** — where `CONTEXT.md` and ADRs live, and the consumer rules for reading them

This is a prompt-driven skill, not a deterministic script. Explore, present what you found, confirm with the user, then write.

## Process

### 1. Explore

Look at the current repo to understand its starting state:
- `git remote -v` — is this a GitHub repo? Which one?
- `AGENTS.md` and `CLAUDE.md` at the repo root — does either exist? Is there already an `## Agent skills` section?
- `CONTEXT.md` and `CONTEXT-MAP.md` at the repo root
- `docs/adr/` and any `src/*/docs/adr/` directories
- `docs/agents/` — does this skill's prior output already exist?
- `.scratch/` — sign that a local-markdown issue tracker is already in use

### 2. Present findings and ask

Summarise what's present and what's missing. Walk the user through three decisions **one at a time**.

**Section A — Issue tracker.**
Default: GitHub (if remote points there), GitLab (if remote points there), otherwise ask.
Options: GitHub, GitLab, local markdown (`.scratch/`), other (freeform).

**Section B — Triage label vocabulary.**
Five canonical roles (defaults):
- `needs-triage` — maintainer needs to evaluate
- `needs-info` — waiting on reporter
- `ready-for-agent` — fully specified, AFK-ready
- `ready-for-human` — needs human implementation
- `wontfix` — will not be actioned

Ask if the user wants to override any.

**Section C — Domain docs.**
- **Single-context**: one `CONTEXT.md` + `docs/adr/` at root (most repos)
- **Multi-context**: `CONTEXT-MAP.md` pointing to per-context files (monorepo)

### 3. Confirm and edit

Show the user a draft of:
- The `## Agent skills` block to add to CLAUDE.md/AGENTS.md
- The contents of `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, `docs/agents/domain.md`

Let them edit before writing.

### 4. Write

**Pick the file to edit:**
- If `CLAUDE.md` exists, edit it
- Else if `AGENTS.md` exists, edit it
- If neither exists, ask the user which one to create

Never create `AGENTS.md` when `CLAUDE.md` already exists (or vice versa). If an `## Agent skills` block already exists, update in-place rather than appending.

The block:
```markdown
## Agent skills

### Issue tracker
[one-line summary]. See `docs/agents/issue-tracker.md`.

### Triage labels
[one-line summary]. See `docs/agents/triage-labels.md`.

### Domain docs
[single-context or multi-context]. See `docs/agents/domain.md`.
```

Then write the three docs files in `docs/agents/`.

### 5. Done

Tell the user setup is complete and which engineering skills will now read from these files.
