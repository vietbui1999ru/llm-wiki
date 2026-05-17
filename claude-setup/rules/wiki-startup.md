# Wiki and Agent Orchestration — Always Active

## Automatic invocation rules

These apply by default at every session. No user prompt needed.

### wiki-context (proactive)
Before any technical task, design discussion, architecture question, or agent work:
invoke `wiki-context` skill to load relevant patterns from ~/repos/llm-wiki.

Not conditional. Not "if relevant." The wiki index is already loaded — the skill
does the search. Invoke it, then proceed.

Skip only for: trivial one-line answers, pure shell commands, git operations.

### agent-orchestration (default for multi-step work)
For any task involving: multi-agent systems, subagent design, team coordination,
complex feature development, or agent harness work:
invoke `agent-orchestration` skill before designing the approach.

### CodeGraphContext startup check (coding projects only)

**Step 1 — instant flag check (always first, no bash, no analysis):**

```bash
grep "^codegraphcontext:" .claude/profile.md 2>/dev/null
```

This single grep determines everything. Do NOT run any other commands before this.

**State machine:**

| Result | Action | Ask? |
|---|---|---|
| `codegraphcontext: enabled` | Verify index live via `list_indexed_repositories`; re-index silently if missing | Never ask |
| `codegraphcontext: session` | Ask "Re-index with CGC?" (yes/no) — re-index only, never "add CGC?" | Never ask "add CGC?" |
| `codegraphcontext: disabled` | Stop. Do nothing. | Never ask — user already said no |
| No output (key missing) | Proceed to Step 2 | Ask Q1 + Q2 |

**Step 2 — first-time flow (only when key is missing):**

Ask two questions, one at a time:

> Q1: "Analyze this repo for CodeGraphContext eligibility?" (yes/no)

If yes → run the three analysis commands:
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
  -o -name "*.yaml" -path "*/.github/workflows/*" \) -not -path "*/.git/*" 2>/dev/null
```
Report: file count, languages, infra detected, threshold verdict (met = 2+ languages OR >100 files OR infra).

> Q2: "Add CodeGraphContext?" (session / daemon / no)

- `session`: `codegraphcontext index .` → write `codegraphcontext: session`
- `daemon`: `codegraphcontext watch .` → write `codegraphcontext: enabled`
- `no`: write `codegraphcontext: disabled` — permanently skip future sessions

If Q1 = no → write `codegraphcontext: disabled` immediately. Do not ask Q2.

**Override:** if user explicitly says "check CGC for this repo" or "add CGC", run Step 2 regardless of any existing flag — including `disabled`.

**Skip entirely for:** `~/repos/llm-wiki`, dotfiles repos, markdown-only repos (no source files detected).

### Linting status check (coding projects only)

At session start, after the CGC check:

```bash
grep "^linting:" .claude/profile.md 2>/dev/null
```

| Result | Action |
|---|---|
| `linting: enabled` | Remind: lint configs (`biome.json`, `eslint.config.*`, `.noslop`, etc.) are **protected** — do not edit them. Biome auto-fix runs at end of each turn. Pre-commit gate is active. |
| `linting: disabled` | Silent skip. |
| No output | Ask: "Enable linting for this project? (yes/no)" — if yes, run `/claude-init` linting step or install noslop manually. |

**Override:** if user explicitly says "add linting" or "set up linting", run setup regardless of existing flag.

### Slop register injection (coding projects only)

After the linting check:

```bash
# Project-level register (highest priority)
cat .claude/slop-register.md 2>/dev/null | grep -v "^#\|^$\|^\*empty" | wc -l

# Global register
grep -v "^#\|^$\|^\*(empty" ~/repos/llm-wiki/mistakes/slop-register.md 2>/dev/null | wc -l
```

| Result | Action |
|---|---|
| Project register has entries | Load `.claude/slop-register.md` into context — read it and treat every entry as a hard constraint on code generation |
| Only global register has entries | Load `~/repos/llm-wiki/mistakes/slop-register.md` — same treatment |
| Both empty or missing | Silent skip |

**What "loaded into context" means**: read the file at session start and apply every listed pattern as a constraint — do not generate code that repeats a registered slop pattern.

**Override:** if user says "show slop register" or "what's in the slop register", print the contents regardless of emptiness.

### skill check discipline (from superpowers)
When superpowers is enabled, the `using-superpowers` skill loads this at startup.
When it's not enabled, treat this rule as the equivalent:
- Before ANY substantive response, check: does a skill apply?
- If even 1% chance a skill applies → invoke it
- Process skills (debugging, design) before implementation skills

## Priority

User's explicit instructions > these rules > defaults.
If user says "just answer quickly" or "skip the skill" → skip it.
