---
name: claude-init
description: Project onboarding. Asks aggressive questions to determine minimal plugin set, writes profile.md and project CLAUDE.md. Run once per project.
---

# Claude Init — Project Onboarding

## Purpose
Determine the minimal plugin set for this project. Ask precisely enough to avoid wrong assumptions. Write durable config so future sessions resume accurately.

## Hard Rules
- Ask one question at a time. Wait for answer before next.
- Never assume the stack — confirm everything.
- If answer is ambiguous, ask a sharper follow-up before moving on.
- Do NOT write any files or suggest plugins until all questions are answered.
- Check for existing `.claude/profile.md` first — if it exists, show current profile and ask what changed.

## Step 0 — Check for Existing Profile

```bash
cat .claude/profile.md 2>/dev/null || echo "NO_PROFILE"
```

If profile exists: show it, ask "What changed?" and update rather than full re-init.
If no profile: proceed to Step 0.5.

## Step 0.5 — CodeGraphContext Decision

**First: instant flag check — always before any bash or questions:**
```bash
grep "^codegraphcontext:" .claude/profile.md 2>/dev/null
```

| Result | Action |
|---|---|
| `codegraphcontext: enabled` | Index live — skip rest of Step 0.5 |
| `codegraphcontext: session` | Index exists, no daemon — skip rest of Step 0.5 |
| `codegraphcontext: disabled` | User declined — skip rest of Step 0.5, write nothing |
| No output | Proceed to analysis below |

**If flag missing — run analysis (claude-init is explicit, Q1 is implicit):**

```bash
find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \
  -o -name "*.go" -o -name "*.rs" -o -name "*.java" -o -name "*.kt" -o -name "*.rb" \
  -o -name "*.php" -o -name "*.swift" -o -name "*.cs" -o -name "*.cpp" -o -name "*.c" -o -name "*.h" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/vendor/*" \
  -not -path "*/dist/*" -not -path "*/__pycache__/*" | wc -l

find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" \
  -o -name "*.go" -o -name "*.rs" -o -name "*.java" -o -name "*.cpp" -o -name "*.c" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/vendor/*" \
  | sed 's/.*\.//' | sort -u

find . -maxdepth 4 \( -name "Dockerfile" -o -name "docker-compose*.yml" -o -name "*.tf" \
  -o -name "*.yaml" -path "*/.github/workflows/*" \) \
  -not -path "*/.git/*" 2>/dev/null | head -5
```

Report: file count, languages, infra detected, threshold verdict (2+ languages OR >100 files OR infra).

**Ask Q2 — one question, regardless of whether threshold was met:**
> "Add CodeGraphContext to this project?" (session / daemon / no)

| Answer | Action | Write to profile.md |
|---|---|---|
| `session` | `codegraphcontext index .` | `codegraphcontext: session` |
| `daemon` | `codegraphcontext watch .` | `codegraphcontext: enabled` |
| `no` | Nothing | `codegraphcontext: disabled` — never ask again |

**If session or daemon — also add query routing to project `CLAUDE.md`** under `## Codebase search routing`:
```
"where is X defined"             → grep/ripgrep
"what calls X / dependencies"    → CodeGraphContext: analyze_code_relationships
"blast radius of changing X"     → CodeGraphContext: analyze_code_relationships
"dead code / unused exports"     → CodeGraphContext: find_dead_code
"design pattern for X"           → qmd wiki search
"overall structure / complexity" → CodeGraphContext: get_repository_stats + find_most_complex_functions
```

Proceed to Step 1.

## Step 1 — Ask These Questions (one at a time)

1. **Project type** — pick one or combine:
   `web-app | api-backend | cli-tool | agent/ai | data-pipeline | library | learning/exploration | other`

2. **Primary language + framework** (e.g. "Go + chi", "Python + FastAPI", "TypeScript + Next.js")

3. **External services** — which apply?
   `GitHub API | Sentry | browser automation/e2e | database (which?) | third-party APIs (which?) | none`

4. **Production or learning?**
   - Production: TDD applies, code review matters, security matters
   - Learning: small examples, no TDD discipline

5. **Security-sensitive?** (auth flows, payments, PII, secrets management) — yes/no

6. **Agent/AI work?** (Claude SDK, multi-agent orchestration, harness engineering) — yes/no

7. **Long-running autonomous loops?** (ralph-loop, overnight agents) — yes/no

## Step 2 — Map Answers to Plugins

| Condition | Enable |
|---|---|
| web-app or UI component work | `frontend-design@claude-plugins-official` |
| browser automation or e2e testing | `playwright@claude-plugins-official` |
| production + any coding | `feature-dev@claude-plugins-official`, `code-review@claude-plugins-official` |
| refactoring or cleanup planned | `code-simplifier@claude-plugins-official` |
| Sentry in external services | `sentry@claude-plugins-official` |
| security-sensitive = yes | `security-guidance@claude-plugins-official` |
| agent/AI work = yes | `agent-sdk-dev@claude-plugins-official` |
| long-running loops = yes | `ralph-loop@claude-plugins-official` |
| first-time scaffold / new project | `claude-code-setup@claude-plugins-official` |

## Step 3 — Present Plugin Diff and Get Approval

Show:
```
Current global baseline (always on):
  superpowers, caveman, qmd, context7, claude-md-management, learning-output-style, explanatory-output-style

Suggested additions for this project:
  + <plugin-1>  — reason
  + <plugin-2>  — reason

Linting: enabled | disabled
  enabled = noslop quality gates (pre-commit) + biome auto-fix (Stop hook) + shellcheck always-on

Approve? (yes / modify / skip)
```

**Linting recommendation**: enable if `mode: production`. Skip if `mode: learning`.

If linting enabled — after approval, install noslop for the primary language pack:
```bash
# TypeScript
npx noslop@latest init ts

# Python (if applicable)
npx noslop@latest init py
```
Then write `linting: enabled` to profile.md.
If linting skipped — write `linting: disabled` to profile.md.

Do NOT apply until user approves.

## Step 4 — On Approval, Write Config

### 4a. Write `.claude/profile.md`
```markdown
# Project Profile
type: <type>
stack: <language + framework>
services: <list>
mode: production | learning
security_sensitive: yes | no
agent_work: yes | no
linting: enabled | disabled
codegraphcontext: enabled | session | disabled
plugins_enabled:
  - <plugin-1>
  - <plugin-2>
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
```

### 4b. Write or update project `CLAUDE.md`
Add a `## Project Context` section with:
- stack summary
- which tools/MCPs are relevant
- any project-specific constraints

Do NOT auto-commit. Show what will be written, then ask: "Write these files? (yes/no)"

### 4c. Update global settings.json plugins

Use the update-config skill to enable the approved plugins in `~/.claude/settings.json`.

After writing: tell user to restart Claude Code for plugin changes to take effect.

### 4d. Initialize session state

Write `.claude/session-state.md`:
```markdown
# Session State
project: <name>
initialized: <YYYY-MM-DD>
status: initialized
last_active: <YYYY-MM-DD>
in_progress: none
```

## Step 5 — Done

Tell user:
1. Profile written to `.claude/profile.md`
2. Plugins enabled in global settings — restart Claude Code
3. Future sessions will auto-load context from profile + session-state
