# LLM Wiki & Claude Setup — User Guide

Personal reference for Viet. Covers: active rules, the wiki, all installed skills, MCP tools, plugins, and scenario playbooks.

---

## 1. Rules in Effect

These behaviors are always active. No need to invoke them — Claude follows them automatically.

### Communication
| Rule                       | Behavior                                                                                                          |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Caveman mode**           | All natural language compressed — no articles, no filler, fragments OK. Does NOT apply to code, commits, or docs. |
| **50-line code limit**     | Long implementations broken into explained chunks. Say "give me the whole thing" to override.                     |
| **No sycophantic openers** | No "Sure!", "Great question!", etc. Ever.                                                                         |
| **No trailing summaries**  | Claude doesn't summarize what it just did at the end of responses.                                                |

### Skill discipline (superpowers)
- Before every substantive response, Claude checks: does a skill apply?
- If even 1% chance → invokes the skill. This is not optional.
- Order: `wiki-context` first → then process skills (debugging, brainstorming) → then implementation skills.

### Auto-invocation (wiki-startup)
| Trigger                                                 | Skill invoked         |
| ------------------------------------------------------- | --------------------- |
| Any technical task, design question, agent work         | `wiki-context`        |
| Multi-agent systems, subagent design, team coordination | `agent-orchestration` |

### Preference feedback loop (judge auto-invocation)
After any response containing:
- Code blocks with substantial implementation
- Numbered implementation plans or structured task breakdowns
- Architectural decisions or tradeoff analysis

Claude invokes `/judge` before ending the turn. Silent on first strike. On second consecutive low score for the same dimension, drafts a corrective rule for approval.

### Domain-specific rules
| Domain | Rule |
|---|---|
| **Learning** (C, Go, Embedded, CUDA, Kubernetes, Terraform, Ansible) | Small examples only, explain terms on first use, no scaffolds |
| **Intermediate** (Web/Backend, DevOps, Docker, Linux, Homelab) | Minimal working config, explain the why, show alternatives |
| **Research** (Rocq/Coq/Lean, FP) | One lemma/function at a time, types first, cite sources |
| **Applied AI** (ML, AI Engineering, Agent Orchestration) | Reference canonical sources, flag empirical vs theoretical claims |
| **TDD exclusion** | TDD is skipped in Learning domains unless you explicitly request it |

### Pre-ingest rule
Before adding any source to the wiki, Claude asks 3–5 comprehension questions. Say "skip review" to bypass.

---

## 2. The Wiki

### What it is
A personal knowledge base at `~/repos/llm-wiki/wiki/`. Claude owns and maintains it. You curate sources and ask questions.

### Structure
```
raw/          ← source documents (never edit these)
pdfs/         ← PDF sources (never edit these)
wiki/
  summaries/  ← one page per ingested source
  entities/   ← named things (tools, projects)
  concepts/   ← ideas and patterns
  comparisons/← side-by-side analyses
  syntheses/  ← cross-source conclusions
index.md      ← catalog of all pages (auto-updated on every ingest)
log.md        ← append-only operation history
```

### Wiki operations

| Say this | Does this |
|---|---|
| `ingest <file.md>` | Summary + entity/concept pages + index + log |
| `ingest <file.pdf>` | Triggers `pdf-ingest` skill (Docling parse → comprehension → wiki pages) |
| `lint the wiki` | Orphan check, stale claims, missing concepts, source gaps |
| `search the wiki for <topic>` | qmd search + load relevant pages into context |
| `query: <question>` | Answer from wiki, optionally file as new page |

### How to search

**In Claude Code** (preferred — uses MCP):
```
search the wiki for "context compression"
```

**Direct CLI:**
```bash
cd ~/repos/llm-wiki
qmd query "context compression degradation" --files --min-score 0.4
```

**Interactive graph-aware Q&A (LightRAG TUI):**
```bash
wiki-chat              # hybrid mode — recommended default
wiki-chat --mode local # entity/concept-focused questions
wiki-chat --mode global# cross-concept, community-level questions
```
Inside `wiki-chat`: `/mode local|global|hybrid|naive` to switch, `/reindex` to rebuild after ingests, `/status` for index stats, `q` to quit.

> First time: run `wiki-index --full` to build the graph. Takes ~30–60 min for ~150 pages with local `qwen2.5:3b` (free). **With `ANTHROPIC_API_KEY` set, expect $10–30+** — LightRAG runs 3 extraction phases per page. Use local LLM for full builds; unset `ANTHROPIC_API_KEY` or pass `--yes` to confirm API cost.

**Read a specific page:**
```bash
cat ~/repos/llm-wiki/wiki/concepts/context-compression.md
```

---

## 3. Skills

Skills load on-demand via `/skill-name` or auto-trigger based on context. Superpowers is enabled — Claude checks before every response.

---

### 3.1 Wiki & knowledge

| Skill                 | Invoke                         | When to use                                                                             |
| --------------------- | ------------------------------ | --------------------------------------------------------------------------------------- |
| `wiki-context`        | Auto (technical/design topics) | Loads relevant wiki patterns before responding                                          |
| `pdf-ingest`          | `ingest <file.pdf>`            | Parses PDF via Docling, runs comprehension check, writes wiki pages                     |
| `pre-digest`          | `/pre-digest`                  | Runs gemma4:e4b locally to pre-process a source file into a digest before full ingest   |
| `agent-orchestration` | Auto (agent/multi-step work)   | Multi-agent coordination patterns, subagent design, harness systems                     |
| `security-patterns`   | Auto (security review)         | OWASP checklist + AI-specific threats (indirect prompt injection, agentic sandbox)      |
| `wiki-index`          | `wiki-index` in terminal       | Build/update LightRAG graph index; incremental by default; `--full` wipes+rebuilds; `--yes` bypasses $10–30+ cost confirmation when API key is set |
| `wiki-chat`           | `wiki-chat` in terminal        | Interactive graph-aware Q&A (LightRAG); 4 modes: hybrid (default), local, global, naive |

---

### 3.2 Feature development

| Skill                            | Invoke                                                      | When to use                                                                                                | Example                                        |
| -------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| `docs-writer`                    | Auto (after code-writer; or "document this" / "write docs") | Write/update structured markdown docs to `docs/`; follows Diátaxis (tutorial/how-to/reference/explanation) | "document the new auth module"                 |
| `/grill-me`                      | `/grill-me`                                                 | Stress-test a plan before starting                                                                         | "I want to add auth — /grill-me"               |
| `/grill-with-docs`               | `/grill-with-docs`                                          | Like grill-me but also builds `CONTEXT.md` + ADRs                                                          | New project or module with unclear terminology |
| `/tdd`                           | `/tdd`                                                      | Build features or fix bugs with red-green-refactor                                                         | "Add user profile API — /tdd"                  |
| `/zoom-out`                      | `/zoom-out`                                                 | Need the big picture of unfamiliar code                                                                    | "I don't understand this middleware"           |
| `/to-prd`                        | `/to-prd`                                                   | Synthesize a conversation into a GitHub issue (PRD)                                                        | After a grill session, capture as issue        |
| `/to-issues`                     | `/to-issues`                                                | Break a PRD into independently-grabbable vertical slices                                                   | After /to-prd, decompose into tickets          |
| `/improve-codebase-architecture` | `/improve-codebase-architecture`                            | Find shallow modules, refactor opportunities                                                               | "Codebase feels messy"                         |
| `feature-dev:feature-dev`        | Auto (guided feature dev)                                   | Codebase analysis → architect → implement                                                                  | Complex feature with exploration phase         |
| `/setup-matt-pocock-skills`      | `/setup-matt-pocock-skills`                                 | First-time per-repo setup: issue tracker, triage labels, CONTEXT.md                                        | Run once per new repo                          |

**New project setup order:**
```
/setup-matt-pocock-skills  → configure repo
/grill-with-docs           → plan the change, build CONTEXT.md
/to-prd                    → capture as issue
/to-issues                 → break into tickets
/tdd                       → implement each ticket
/diagnose                  → when something breaks
```

---

### 3.3 Quality & feedback

| Skill                     | Invoke                                  | When to use                                                                                      |
| ------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `/judge`                  | Auto (after code/plan/design responses) | LLM-as-judge evaluation on 4-dimension rubric; silent first strike                               |
| `/judge-report`           | `/judge-report`                         | Show current session's judge evaluation history                                                  |
| `/earn-it`                | `/earn-it`                              | Claude becomes Socratic — you write the code, Claude guides. Enforces hand-code-first discipline |
| `simplify`                | `/simplify`                             | Review recently changed code for reuse, quality, and efficiency                                  |
| `code-review:code-review` | `/code-review`                          | Code review a pull request                                                                       |
| `/review`                 | `/review`                               | Review a pull request (alias)                                                                    |
| `/security-review`        | `/security-review`                      | Full OWASP + AI-specific security audit; structured threat report                                |

---

### 3.4 Debugging & diagnosis

| Skill                              | Invoke                  | When to use                                                    |
| ---------------------------------- | ----------------------- | -------------------------------------------------------------- |
| `/diagnose`                        | `/diagnose`             | Hard bugs, flaky tests, performance regressions — 6-phase loop |
| `superpowers:systematic-debugging` | Auto (bug/test failure) | Disciplined root-cause analysis before fixing                  |

`/diagnose` phases: build feedback loop → reproduce → hypothesize → instrument → fix → cleanup.

---

### 3.5 Session & memory

| Skill                  | Invoke                            | When to use                                                                 |
| ---------------------- | --------------------------------- | --------------------------------------------------------------------------- |
| `/save-session`        | `/save-session`                   | Before clearing context or ending a long session — full summary saved       |
| `/capture-mistake`     | Auto (after Claude self-corrects) | Files the mistake immediately to `mistakes/`                                |
| `/synthesize-mistakes` | `/synthesize-mistakes`            | Distill `raw-log.md` + structured entries into `global-prevention-rules.md` |

The mistakes pipeline: `capture-mistake` → individual `mistakes/YYYY-MM-DD-*.md` → `synthesize-mistakes` → `global-prevention-rules.md` → loaded every session.

---

### 3.6 Project setup & config

| Skill                                     | Invoke                      | When to use                                                                |
| ----------------------------------------- | --------------------------- | -------------------------------------------------------------------------- |
| `/claude-init`                            | `/claude-init`              | Project onboarding — aggressive questions to set up CLAUDE.md              |
| `/init`                                   | `/init`                     | Initialize a new CLAUDE.md file                                            |
| `update-config`                           | `/update-config`            | Configure settings.json: permissions, hooks, env vars, automated behaviors |
| `keybindings-help`                        | `/keybindings-help`         | Customize keyboard shortcuts, rebind keys, chord bindings                  |
| `fewer-permission-prompts`                | `/fewer-permission-prompts` | Scan transcripts for common read-only ops, add allowlist to reduce prompts |
| `claude-md-management:revise-claude-md`   | Auto (end of session)       | Update CLAUDE.md with session learnings                                    |
| `claude-md-management:claude-md-improver` | `/improve-claude-md`        | Audit and improve CLAUDE.md files                                          |

---

### 3.7 Background & automation

| Skill | Invoke | When to use |
|---|---|---|
| `loop` | `/loop <interval> <command>` | Run a prompt or slash command on a recurring interval |
| `schedule` | `/schedule` | Create/manage scheduled remote agents (cron-based routines) |
| `ralph-loop:ralph-loop` | `/ralph-loop` | Start a long-running autonomous agent loop |
| `ralph-loop:cancel-ralph` | `/cancel-ralph` | Cancel an active Ralph Loop |
| `ralph-loop:help` | `/ralph-loop help` | Explain Ralph Loop plugin and available commands |

`ralph-loop` pattern: intercepts exit, reinjects original prompt with clean context + durable filesystem state. Enables extended AFK sessions.

---

### 3.8 AI & SDK development

| Skill | Invoke | When to use |
|---|---|---|
| `claude-api` | Auto (when code imports `anthropic` or `@anthropic-ai/sdk`) | Build/debug/optimize Claude API apps with prompt caching |
| `agent-sdk-dev:new-sdk-app` | `/new-sdk-app` | Create and set up a new Claude Agent SDK application |

`claude-api` also handles: migrating between model versions, caching tuning, tool use, batch API, files API.

---

### 3.9 Superpowers (auto-trigger)

These are invoked by Claude, not by you. They override nothing — they defer to your CLAUDE.md rules.

| Skill | Triggers when |
|---|---|
| `using-superpowers` | Every conversation start — establishes skill-check discipline |
| `brainstorming` | Before any creative work (creating features, designing systems) |
| `writing-plans` | You have a spec/requirements for a multi-step task |
| `executing-plans` | You have a written plan file to execute |
| `test-driven-development` | Any feature/bugfix implementation (Learning domains excluded) |
| `systematic-debugging` | Any bug or test failure |
| `dispatching-parallel-agents` | 2+ independent problems to solve concurrently |
| `subagent-driven-development` | Executing implementation plans with isolated parallel tasks |
| `using-git-worktrees` | Feature work that needs branch isolation |
| `requesting-code-review` | Completing tasks, implementing major features |
| `receiving-code-review` | Receiving code review feedback before implementing |
| `finishing-a-development-branch` | Implementation complete, ready to merge/PR |
| `verification-before-completion` | Before claiming work is complete, fixed, or passing |
| `writing-skills` | Creating or editing skills |

---

### 3.10 Plugin: Caveman

| Skill | Invoke | When to use |
|---|---|---|
| `/caveman` | `/caveman` | Toggle ultra-compressed comms (already always on) |
| `caveman:caveman-commit` | Auto | Compressed but precise commit messages |
| `caveman:caveman-review` | During PR review | Compressed code review comments |
| `caveman:compress` | `/compress` | Compress natural language memory files (CLAUDE.md, todos, plans) |

---

### 3.11 Plugin: Sentry

| Skill | Invoke | When to use |
|---|---|---|
| `sentry:seer` | "ask Sentry about X" | Natural language questions about your Sentry environment |
| `sentry:sentry-code-review` | `/sentry-code-review` | Analyze and resolve Sentry comments on GitHub PRs |
| `sentry:sentry-setup-tracing` | `/sentry-setup-tracing` | Setup Sentry Performance Monitoring |
| `sentry:sentry-setup-logging` | `/sentry-setup-logging` | Setup Sentry Logging |
| `sentry:sentry-setup-metrics` | `/sentry-setup-metrics` | Setup Sentry Metrics |
| `sentry:sentry-setup-ai-monitoring` | `/sentry-setup-ai-monitoring` | Setup Sentry AI Agent Monitoring |
| `sentry:sentry-ios-swift-setup` | `/sentry-ios-setup` | Setup Sentry in iOS/Swift apps |

---

### 3.12 Other

| Skill | Invoke | When to use |
|---|---|---|
| `qmd:qmd` | "search my notes for X" | Search any qmd-indexed markdown collection |
| `frontend-design:frontend-design` | `/frontend-design` | Create distinctive, production-grade frontend interfaces |
| `statusline-setup` | `/statusline-setup` | Configure Claude Code status line |
| `claude-code-setup:claude-automation-recommender` | `/automation-recommender` | Analyze codebase and recommend CC automations |

---

## 4. MCP Tools

MCP tools are available directly to Claude — no skill needed.

### Active servers

| Server               | What it does                                                                   | When Claude uses it                                                           |
| -------------------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| **firecrawl**        | Web scraping, crawling, search, structured extraction, autonomous web research | "scrape this URL", "research X from the web", "extract data from these pages" |
| **github**           | Read/write issues, PRs, branches, code search                                  | "create issue", "list open PRs", "search code for X"                          |
| **playwright**       | Browser automation, screenshots, UI testing                                    | "take a screenshot of", "click X on this page", "verify UI renders correctly" |
| **context7**         | Fetch live library/framework docs                                              | "how does X work in Next.js", "Prisma migration syntax"                       |
| **qmd**              | Search wiki + any qmd-indexed collection                                       | Wiki searches (used by wiki-context skill)                                    |
| **sentry**           | Query error tracking, issues, events                                           | "what errors are trending", "analyze this Sentry issue"                       |
| **CodeGraphContext** | Code graph analysis, dead code, complexity                                     | "find dead code", "most complex functions", "analyze relationships"           |
| **Figma**            | Read designs, generate diagrams, code connect                                  | When given a figma.com URL                                                    |
| **MermaidChart**     | Create and validate Mermaid diagrams                                           | "generate a diagram of X", "create a flowchart"                               |

### Firecrawl tool selection guide

| Task | Tool |
|---|---|
| Get clean content from one URL | `firecrawl_scrape` |
| Find all URLs on a site | `firecrawl_map` |
| Web search with full page content | `firecrawl_search` |
| Crawl multiple pages of a site | `firecrawl_crawl` |
| Extract structured data (with schema) | `firecrawl_extract` |
| Complex research, unknown URLs | `firecrawl_agent` (async — wait for result) |
| Click/fill/navigate a page | `firecrawl_interact` |

---

## 5. Plugins

Enabled plugins that provide skills and hooks.

| Plugin | What it adds |
|---|---|
| `superpowers` | Full dev workflow: TDD, debugging, planning, parallel agents, skill-check discipline |
| `caveman` | Ultra-compressed communication mode |
| `qmd` | Wiki search skill + MCP server |
| `context7` | Live library doc fetching |
| `playwright` | Browser automation + visual verification skills |
| `feature-dev` | Guided feature development with codebase analysis |
| `code-review` | PR code review |
| `security-guidance` | Security review tools |
| `ralph-loop` | Long-running autonomous agent loops with clean context reinject |
| `sentry` | Sentry error tracking integration + AI monitoring setup |
| `obsidian` | Obsidian vault CLI/markdown tools |
| `frontend-design` | High-quality UI design skills |
| `claude-md-management` | CLAUDE.md audit, improvement, and session learning capture |
| `claude-code-setup` | CC automation analysis and configuration |
| `agent-sdk-dev` | Claude Agent SDK app scaffolding |

---

## 6. Scenario Playbooks

### "I want to build a new feature"
```
1. /grill-with-docs  → plan it, build CONTEXT.md
2. /to-prd           → capture as GitHub issue
3. /to-issues        → break into vertical slices
4. For each slice: /tdd → implement with red-green-refactor
5. When done: superpowers:finishing-a-development-branch triggers automatically
```

### "I have a bug I can't figure out"
```
/diagnose
→ Phase 1: build a fast feedback loop (test, curl, CLI invocation)
→ Phase 2–6: reproduce → hypothesize → instrument → fix → cleanup
```

### "I want Claude to grade its own output"
```
After any code/plan/design response:
→ /judge triggers automatically (preference feedback loop)
→ /judge-report to see the full session evaluation history
→ On second consecutive low score for a dimension: rule drafted for approval
```

### "I want to learn by doing (not just copy)"
```
/earn-it
→ Claude becomes Socratic: asks questions, guides design, you write the code
→ No code dumps; you earn each implementation piece
```

### "I need to research something from the web"
```
"Research the top LLM routing strategies and summarize them"
→ Claude uses firecrawl_search + firecrawl_scrape
→ Offer to ingest result as a wiki page
```

### "I want to add a markdown source to the wiki"
```
1. Drop file in raw/
2. "ingest <filename>"
3. Answer the 3–5 comprehension questions (or "skip review")
4. Wiki pages auto-created, index + log updated
```

### "I want to add a PDF research paper to the wiki"
```
1. Drop PDF in pdfs/
2. "ingest <filename.pdf>"
3. pdf-ingest skill invokes: Docling parse → comprehension check → wiki pages
```

### "I want to check if the wiki has anything on topic X"
```
"search the wiki for context degradation"
→ wiki-context skill invoked → relevant pages loaded → answer with [[page]] citations
```

### "I want to query the wiki interactively (deep exploration)"
```
wiki-chat                     # in terminal, outside Claude Code
→ Hybrid mode: entity graph + community summaries
→ /mode local   — specific concept/entity questions
→ /mode global  — big-picture cross-concept questions
→ /reindex      — rebuild graph after new ingests
→ q to quit

Prerequisite: wiki-index must have run at least once.
After bulk ingests: wiki-index (incremental) or wiki-index --full (rebuild)
```

### "I want to document a new feature or module"
```
Say: "document this" / "write docs" / "update the docs"
→ docs-writer agent invoked
→ outputs structured markdown to project's docs/ folder
→ 4 Diátaxis types: tutorial (learning-oriented), how-to (goal-oriented),
  reference (information-oriented), explanation (understanding-oriented)
→ AI agents treated as explicit audience (machine-readable navigation)
```

### "I want to improve the architecture of this codebase"
```
/improve-codebase-architecture
→ Claude walks the codebase, finds shallow modules
→ Proposes deepening opportunities using CONTEXT.md vocabulary
→ You pick candidates → grilling session → CONTEXT.md updated
```

### "I need to review a PR for security"
```
/security-review
→ OWASP Top 10 + AI-specific threats:
  - Indirect prompt injection (including dev-loop vectors: issues, PRs, changelogs)
  - Rules file injection (CLAUDE.md, AGENTS.md as persistent steering surface)
  - CI/CD confused deputy ("clinejection" attack pattern)
  - Test fabrication / test deletion
  - Hallucinated dependencies (slopsquatting)
  - Agentic sandbox controls
→ Structured threat report
```

### "I want to update the LightRAG graph after new ingests"
```
wiki-index                    # incremental — picks up new/changed pages only
wiki-index --status           # see what's indexed vs. pending
tail -f .lightrag/last-index.log   # watch progress

# Full rebuild (local LLM, free):
wiki-index --full

# Full rebuild (Haiku, $10–30+):
wiki-index --full --yes
```
The post-commit hook runs `wiki-index` (incremental) automatically after commits touching `wiki/`.
New pages that were ingested this session are queued automatically on next run.

### "I want to run a long autonomous task"
```
/ralph-loop
→ Claude works until it exits
→ ralph-loop intercepts exit, reinjects original prompt + durable filesystem state
→ Continues until task complete or you /cancel-ralph
```

### "I want to set up a recurring background task"
```
/loop 30m /your-command
→ Runs /your-command every 30 minutes, self-pacing within the loop
/schedule
→ Creates a cron-based remote agent routine (persists across sessions)
```

### "A mistake was made — prevent recurrence"
```
Claude auto-invokes /capture-mistake after any self-correction
→ Files to mistakes/YYYY-MM-DD-<topic>.md

Periodically: /synthesize-mistakes
→ Distills all structured entries into global-prevention-rules.md
→ Rules loaded every session from that point on
```

### "Context is getting long — ending the session"
```
/save-session
→ Full session summary saved to disk
→ Safe to /clear or close Claude Code
→ Resume next session: "continue from save-session summary"
```

---

## 7. Git Worktrees (Optional Dev Setup)

Worktrees let you work on multiple branches simultaneously without `git stash` or branch switching. Each branch gets its own directory with a clean working tree.

### Setup (one-time)

`.worktrees/` is already in `.gitignore` — safe to create without polluting git status.

```bash
# Create a worktree for an existing branch
git worktree add .worktrees/<branch-name> <branch-name>

# Example — set up all three branches at once:
git worktree add .worktrees/personal-profile personal-profile
git worktree add .worktrees/wiki-for-AI-LLM wiki-for-AI-LLM
git worktree add .worktrees/wiki-for-DSA wiki-for-DSA
```

### Useful commands

```bash
git worktree list                    # see all active worktrees
git worktree remove .worktrees/name  # clean up when done
```

### Notes

- Each worktree is fully independent: separate staged files, separate HEAD
- The main repo and any worktree can both be open simultaneously
- A branch can only be checked out in one worktree at a time
- Superpowers `using-git-worktrees` skill auto-triggers when starting isolated feature work

---

## 8. Tips

**Force wiki search in any session:**
```
search the wiki for <topic>
```
Always works regardless of context.

**Skills auto-trigger.** With superpowers + wiki-startup rules active, Claude checks for applicable skills and loads wiki context automatically. You don't need to say "use TDD" or "use the wiki."

**Caveman mode is always on** — natural language output compressed. Code, commits, and docs are written normally.

**50-line code limit** — Claude breaks long implementations into explained chunks. Say "give me the whole thing" to override.

**Per-repo setup** — run `/setup-matt-pocock-skills` once per project to configure issue tracker + domain glossary. After that, all engineering skills know the context.

**Judge is always watching** — after substantial code/plan/design outputs, Claude auto-invokes `/judge`. Use `/judge-report` to see the session's quality history.

**Skip comprehension on ingest** — if you already know a source well, say "skip review" or "just ingest it" to bypass the 3–5 question check.

**Shell commands in session** — prefix with `!` to run in the current Claude Code session: `! gcloud auth login`.
