# LLM Wiki & Claude Setup — User Guide

Personal reference for Viet. Covers: the wiki, installed skills, MCP tools, and scenario playbooks.

---

## 1. The Wiki

### What it is
A personal knowledge base at `~/repos/llm-wiki/wiki/`. Claude owns and maintains it. You curate sources and ask questions.

### Structure
```
raw/          ← source documents (never edit these)
wiki/
  summaries/  ← one page per ingested source
  entities/   ← named things (tools, projects)
  concepts/   ← ideas and patterns
  syntheses/  ← cross-source conclusions
index.md      ← catalog of all pages (auto-updated)
log.md        ← append-only operation history
GUIDE.md      ← this file
```

### How to search
**In Claude Code** (preferred — uses MCP):
```
search the wiki for "context compression"
```
Claude invokes the `wiki-context` skill which searches via qmd and loads relevant pages.

**Direct CLI:**
```bash
cd ~/repos/llm-wiki
qmd query "context compression degradation" --files --min-score 0.4
```

**Read a specific page:**
```bash
cat ~/repos/llm-wiki/wiki/concepts/context-compression.md
```

### How to add content
1. Drop a source into `raw/`
2. Tell Claude: `ingest <filename>`
3. Claude reads it, runs comprehension questions (or skip: "skip review"), writes wiki pages, updates index + log

### Wiki operations
| Say this | Does this |
|---|---|
| `ingest <file>` | Full ingest: summary + entity/concept pages + index + log |
| `lint the wiki` | Orphan check, stale claims, missing concepts, source gaps |
| `search the wiki for <topic>` | qmd search + load relevant pages into context |
| `query: <question>` | Answer from wiki, optionally file as new page |

---

## 2. Skills

Skills are loaded on-demand via `/skill-name` or automatically when Claude detects they apply.
**Superpowers is enabled** — Claude checks for applicable skills before every response.

### Engineering workflow (mattpocock/skills)

| Skill | Invoke | When to use | Example |
|---|---|---|---|
| `/grill-me` | `/grill-me` | Before starting any feature — stress-test your plan | "I want to add auth — /grill-me" |
| `/grill-with-docs` | `/grill-with-docs` | Like grill-me but also builds `CONTEXT.md` glossary and ADRs | New project or module with unclear terminology |
| `/tdd` | `/tdd` | Build features or fix bugs with red-green-refactor | "Add user profile API — /tdd" |
| `/diagnose` | `/diagnose` | Hard bugs, flaky tests, performance regressions | "Auth is broken in prod — /diagnose" |
| `/zoom-out` | `/zoom-out` | Lost in unfamiliar code, need the big picture | "I don't understand this middleware — /zoom-out" |
| `/to-prd` | `/to-prd` | Synthesize a conversation into a GitHub issue (PRD) | After a grill session, capture it as an issue |
| `/to-issues` | `/to-issues` | Break a PRD into independently-grabbable vertical slices | After /to-prd, decompose into tickets |
| `/improve-codebase-architecture` | `/improve-codebase-architecture` | Find shallow modules, refactor opportunities | "The codebase feels messy — /improve-codebase-architecture" |
| `/setup-matt-pocock-skills` | `/setup-matt-pocock-skills` | First-time per-repo setup: issue tracker, triage labels, CONTEXT.md | Run once per new repo before using the above skills |

**Setup order for a new project:**
```
/setup-matt-pocock-skills  → configure repo
/grill-with-docs           → plan the change, build CONTEXT.md
/to-prd                    → capture as issue
/to-issues                 → break into tickets
/tdd                       → implement each ticket
/diagnose                  → when something breaks
```

---

### Knowledge & research

| Skill | Invoke | When to use |
|---|---|---|
| `wiki-context` | Auto (on technical/design topics) | Load relevant wiki patterns before designing systems |
| `agent-orchestration` | Auto (on agent/multi-step work) | Patterns for subagent design, team coordination, harness systems |
| `security-patterns` | Auto (on security review) | OWASP checklist + AI-specific threats |

These trigger automatically. You don't need to invoke them manually unless you want to force-load them.

---

### Superpowers (obra/superpowers)

These auto-trigger based on context. You don't call them directly — Claude invokes them.

| Skill | Triggers when |
|---|---|
| `using-superpowers` | Every conversation start — establishes skill-check discipline |
| `test-driven-development` | Any feature/bugfix implementation |
| `systematic-debugging` | Any bug or test failure |
| `executing-plans` | You have a written plan file to execute |
| `dispatching-parallel-agents` | 2+ independent problems to solve concurrently |
| `finishing-a-development-branch` | Implementation complete, ready to merge/PR |

**Note:** superpowers skills defer to your CLAUDE.md rules. Caveman mode, 50-line limit, etc. all win.

---

### Productivity

| Skill | Invoke | When to use |
|---|---|---|
| `/caveman` | `/caveman` | Toggle ultra-compressed comms (already always on) |
| `/caveman-commit` | Auto | Write compressed but precise commit messages |
| `/caveman-review` | During PR review | Compressed code review comments |
| `qmd:qmd` | "search my notes for X" | Search any qmd-indexed markdown collection |

---

## 3. MCP Tools

MCP tools are available directly to Claude — no skill needed.

### Active servers

| Server | What it does | When Claude uses it |
|---|---|---|
| **firecrawl** | Web scraping, crawling, search, structured extraction, autonomous web research | "scrape this URL", "research X from the web", "extract data from these pages" |
| **github** | Read/write issues, PRs, branches, code search | "create issue", "list open PRs", "search code for X" |
| **playwright** | Browser automation, screenshots, UI testing | "take a screenshot of", "click X on this page", "verify UI renders correctly" |
| **context7** | Fetch live library/framework docs | "how does X work in Next.js", "Prisma migration syntax" |
| **qmd** | Search wiki + any qmd-indexed collection | Wiki searches (used by wiki-context skill) |
| **sentry** | Query error tracking, issues, events | "what errors are trending", "analyze this Sentry issue" |
| **CodeGraphContext** | Code graph analysis, dead code, complexity | "find dead code", "most complex functions", "analyze relationships" |
| **Figma** | Read designs, generate diagrams, code connect | When given a figma.com URL |

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

**Example:**
```
"Scrape the Anthropic pricing page and extract model names and prices as JSON"
→ Claude uses firecrawl_extract with a schema
```

---

## 4. Plugins

Enabled plugins that provide skills and hooks.

| Plugin | What it adds |
|---|---|
| `superpowers` | Full dev workflow: TDD, debugging, planning, parallel agents |
| `caveman` | Ultra-compressed communication mode |
| `qmd` | Wiki search skill |
| `context7` | Live library doc fetching |
| `playwright` | Browser testing skills |
| `feature-dev` | Guided feature development with codebase analysis |
| `code-review` | PR code review |
| `security-guidance` | Security review tools |
| `ralph-loop` | Long-running autonomous agent loops |
| `sentry` | Sentry error tracking integration |
| `obsidian` | Obsidian vault CLI/markdown tools |
| `frontend-design` | High-quality UI design skills |

---

## 5. Scenario Playbooks

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
→ Phase 2-6: reproduce → hypothesize → instrument → fix → cleanup
```

### "I need to research something from the web"
```
"Research the top LLM routing strategies and summarize them"
→ Claude uses firecrawl_search + firecrawl_scrape
→ Offer to ingest result as a wiki page
```

### "I want to understand an unfamiliar codebase section"
```
/zoom-out
→ Claude gives you a module map using the project's domain vocabulary
```

### "I want to add this new source to the wiki"
```
1. Drop file in raw/
2. "ingest <filename>"
3. Answer the 3-5 comprehension questions (or "skip review")
4. Wiki pages auto-created, index + log updated
```

### "I want to check if the wiki has anything on topic X"
```
"search the wiki for context degradation"
→ wiki-context skill invoked → relevant pages loaded → answer with citations
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
→ OWASP Top 10 + AI-specific threats (indirect prompt injection, agentic sandbox)
→ Structured threat report
```

---

## 6. Tips

**Force wiki search in any session:**
```
search the wiki for <topic>
```
Always works regardless of context.

**The skills auto-trigger. You don't need to say "use TDD" or "use the wiki"** — with superpowers + wiki-startup rules active, Claude checks for applicable skills and loads wiki context automatically.

**Caveman mode is always on** — all natural language responses are compressed. Code, commits, docs are written normally.

**50-line code limit** — Claude breaks long implementations into explained chunks. Say "give me the whole thing" to override.

**Per-repo setup** — run `/setup-matt-pocock-skills` once per project to configure issue tracker + domain glossary. After that, all engineering skills know the context.
