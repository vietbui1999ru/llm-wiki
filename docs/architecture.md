# llm-wiki Architecture

## Chart 1 — System Overview

```mermaid
graph TD
    subgraph REPO["llm-wiki repo"]
        RAW[raw/ — immutable sources]
        WIKI[wiki/ — LLM-maintained pages]
        IDX[index.md + log.md]
        SKILLS[skills/ — local skill overrides]
        SETUP[claude-setup/ — config source of truth]
        TMPL[templates/ — executables]
        MISTAKES[mistakes/ — error log]
    end

    subgraph INDEXES["Search Indexes"]
        QMD[qmd — BM25 + vector]
        LIGHTRAG[.lightrag/ — graph index]
    end

    subgraph QUERY["Query Layer"]
        CHAT[wiki-chat — TUI]
        MCP[wiki-mcp — MCP server]
        SKILL_WC[wiki-context skill]
    end

    subgraph COUNCIL["Council / Review"]
        COUNCIL_PY[council.py]
        VOICE_A[Voice A — Sonnet<br>claude -p --model claude-sonnet-4-6]
        VOICE_B[Voice B — Codex<br>pi -p --model openai-codex/gpt-5.3-codex<br>--no-session]
        CHAIR[Chairman — Opus<br>claude -p --model claude-opus-4-7]
    end

    subgraph CONFIG["Config Distribution"]
        DOTFILES[~/dotfiles/claude/.claude]
        HOME_CLAUDE[~/.claude]
    end

    RAW -->|ingest| WIKI
    WIKI --> IDX
    WIKI -->|post-commit hook| QMD
    WIKI -->|post-commit hook| LIGHTRAG

    QMD --> SKILL_WC
    LIGHTRAG --> CHAT
    LIGHTRAG --> MCP

    SETUP -->|symlinks| DOTFILES
    DOTFILES -->|stow| HOME_CLAUDE

    COUNCIL_PY --> VOICE_A & VOICE_B
    VOICE_A & VOICE_B --> CHAIR
```

---

## Chart 2 — Knowledge Ingestion Pipeline

```mermaid
flowchart LR
    SRC_MD[raw/*.md\nweb-scraped sources]
    SRC_PDF[pdfs/*.pdf\nresearch papers]

    DOCLING[docling\nPDF → Markdown]
    CLAUDE_INGEST[Claude\ningest operator]

    subgraph WIKI_WRITE["Wiki Write"]
        SUMMARY[wiki/summaries/]
        CONCEPT[wiki/concepts/]
        ENTITY[wiki/entities/]
        COMPARE[wiki/comparisons/]
        SYNTH[wiki/syntheses/]
    end

    IDX[index.md\ncatalog]
    LOG[log.md\nappend-only log]

    GIT_COMMIT[git commit]

    subgraph HOOK["post-commit hook"]
        QMD_UPDATE[qmd update + embed\nBM25 + vector]
        WIKI_IDX[wiki-index\ngraph extraction\nbackground]
    end

    QMD_STORE[.qmd/ index]
    LR_STORE[.lightrag/ graph]

    SRC_MD --> CLAUDE_INGEST
    SRC_PDF --> DOCLING --> CLAUDE_INGEST

    CLAUDE_INGEST --> WIKI_WRITE
    CLAUDE_INGEST --> IDX
    CLAUDE_INGEST --> LOG

    WIKI_WRITE --> GIT_COMMIT
    IDX --> GIT_COMMIT
    LOG --> GIT_COMMIT

    GIT_COMMIT --> QMD_UPDATE --> QMD_STORE
    GIT_COMMIT --> WIKI_IDX --> LR_STORE
```

---

## Chart 3 — Retrieval Stack

```mermaid
graph TD
    Q[User query]

    subgraph QMD_LAYER["qmd — keyword + semantic"]
        LEX[BM25 lexical search]
        VEC[vector semantic search]
        HYDE[HyDE hypothetical doc]
        RERANK[score + rerank]
    end

    subgraph LIGHTRAG_LAYER["LightRAG — graph-aware"]
        LOCAL[local mode\nentity-focused]
        GLOBAL[global mode\ncommunity summaries]
        HYBRID[hybrid mode\nentity + community]
        NAIVE[naive mode\nflat vector]
        OLLAMA_EMB[nomic-embed-text\nvia ollama]
        LLM_SYNTH[synthesis LLM\nqwen2.5:3b or Haiku]
    end

    subgraph FRONTENDS["Access Points"]
        SKILL_WC[wiki-context skill\nClaude Code]
        CHAT_TUI[wiki-chat\nTUI REPL]
        MCP_SRV[wiki-mcp\nMCP server]
    end

    Q --> SKILL_WC --> LEX & VEC & HYDE --> RERANK
    Q --> CHAT_TUI --> HYBRID
    Q --> MCP_SRV --> HYBRID

    HYBRID --> LOCAL & GLOBAL
    LOCAL & GLOBAL --> OLLAMA_EMB
    OLLAMA_EMB --> LLM_SYNTH

    RERANK --> WIKI_PAGES[wiki/*.md pages\nreturned as context]
    LLM_SYNTH --> ANSWER[synthesized answer]
```

---

## Chart 4 — Council System

```mermaid
sequenceDiagram
    participant User
    participant council.py
    participant VoiceA as Voice A (Sonnet / claude -p)
    participant VoiceB as Voice B (Codex / pi -p)
    participant Chair as Chairman (Opus / claude -p)
    participant Files as .council/ files
    participant Git

    User->>council.py: question [--chairman] [--add MODEL]

    par parallel dispatch
        council.py->>VoiceA: claude -p --model claude-sonnet-4-6
        council.py->>VoiceB: pi -p --model openai-codex/gpt-5.3-codex --no-session
    end

    VoiceA-->>Files: voice_a.md
    VoiceB-->>Files: voice_b.md

    alt --chairman flag set
        council.py->>Chair: claude -p --model claude-opus-4-7\n(synthesis prompt — all voice files concatenated)
        Chair-->>Files: synthesis.md
    end

    council.py->>Git: git add .council/ && git commit
    council.py-->>User: stdout summary
```

**Voice B is a Pi subprocess** — `pi -p --no-session` produces clean stdout. `opencode run` also writes response to stdout but with a 3-line ANSI header; strip it with:
```bash
opencode run "question" -m github-copilot/gpt-5.2-codex 2>/dev/null \
  | sed 's/\x1b\[[0-9;]*m//g' | grep -v "^>" | grep -v "^[[:space:]]*$"
```

**Quick council (no council.py):**
```bash
# Voice B — Pi (GPT-5.3-codex, clean stdout)
pi -p "peer review: [question]" --model openai-codex/gpt-5.3-codex --no-session --no-extensions --no-skills

# Voice C — OpenCode run (GPT-5.2-codex via Copilot, filterable stdout)
opencode run "peer review: [question]" -m github-copilot/gpt-5.2-codex 2>/dev/null \
  | sed 's/\x1b\[[0-9;]*m//g' | grep -v "^>" | grep -v "^[[:space:]]*$"
```

**Provider status (validated):**
- `openai-codex/` via Pi → ✅ clean stdout (ChatGPT Team subscription)
- `github-copilot/gpt-5.2-codex` via `opencode run` → ✅ filterable stdout (Copilot subscription)
- `github-copilot/claude-sonnet-4.5` via `opencode run` → ❌ model_not_supported (Claude via Copilot unsupported in run mode)
- `opencode/` via Pi → ⏳ add payment method at opencode.ai/workspace billing to unlock

---

## Chart 5 — Config Distribution (Source of Truth)

```mermaid
graph LR
    subgraph LLMWIKI["llm-wiki/claude-setup/  ← source of truth"]
        CS_CLAUDE[CLAUDE.md]
        CS_RULES[rules/*.md]
        CS_AGENTS[agents/*.md]
        CS_SKILLS[skills/*/SKILL.md]
        CS_PLUGINS[plugins/config.json]
        CS_SETTINGS[settings.json]
    end

    subgraph DOTFILES["~/dotfiles/claude/.claude/  ← symlinks to llm-wiki"]
        DF_CLAUDE[CLAUDE.md →]
        DF_RULES[rules/*.md →]
        DF_AGENTS[agents/*.md →]
        DF_SKILLS[skills/ →]
        DF_SETTINGS[settings.json →]
    end

    subgraph ACTIVE["~/.claude/  ← stow-managed symlinks"]
        AC_CLAUDE[CLAUDE.md]
        AC_RULES[rules/]
        AC_AGENTS[agents/]
        AC_SKILLS[skills/]
        AC_SETTINGS[settings.json]
    end

    subgraph SHARED["~/dotfiles/shared/  ← generated"]
        SH_AGENTS[AGENTS.md\nsync-agent-rules.sh]
    end

    subgraph OTHER["Other AI tools"]
        GEMINI[~/.gemini/]
        CODEX_DIR[~/.codex/]
        OPENCODE[~/.config/opencode/]
    end

    CS_RULES -->|ln -s| DF_RULES
    CS_AGENTS -->|ln -s| DF_AGENTS
    CS_CLAUDE -->|ln -s| DF_CLAUDE
    CS_SETTINGS -->|ln -s| DF_SETTINGS

    DF_CLAUDE -->|stow| AC_CLAUDE
    DF_RULES -->|stow| AC_RULES
    DF_AGENTS -->|stow| AC_AGENTS
    DF_SETTINGS -->|stow| AC_SETTINGS

    CS_RULES -->|sync-agent-rules.sh| SH_AGENTS
    SH_AGENTS -->|cp| GEMINI
    SH_AGENTS -->|cp| CODEX_DIR
    SH_AGENTS -->|cp| OPENCODE
```

---

## Chart 6 — Hooks / Automation

```mermaid
flowchart TD
    subgraph PRETOOL["PreToolUse hooks"]
        PTU_BASH[PreToolUse:Bash]
        PTU_WRITE[PreToolUse:Write/Edit]
        PTU_AGENT[PreToolUse:Agent]
    end

    subgraph POSTTOOL["PostToolUse hooks"]
        POST_BASH[PostToolUse:Bash]
        POST_WRITE[PostToolUse:Write/Edit]
    end

    subgraph STOP_HOOK["Stop hook"]
        STOP[Stop]
    end

    subgraph UPS_HOOK["UserPromptSubmit hook"]
        UPS[UserPromptSubmit]
    end

    subgraph GIT_HOOKS["Git hooks"]
        PC[post-commit hook]
    end

    PTU_BASH --> BASH_GATE["enforce-bash-safety.sh<br>blocks: rm -rf / or ~<br>git push --force to main/master<br>git reset --hard origin/"]

    PTU_WRITE --> LINT_PROTECT["protect-lint-configs.sh<br>blocks edits to:<br>biome.json, .eslintrc*, .noslop,<br>.golangci.yml, .shellcheckrc"]

    PTU_AGENT --> AGENT_WL["enforce-agent-whitelist.sh<br>blocks unknown subagent_type<br>requires explicit model: param<br>whitelist = ~/.claude/agents/*.md"]

    POST_BASH --> ERR_CAP["capture-bash-error.sh<br>exit≠0 → mistakes/raw-log.md"]
    POST_BASH --> PUB_KB["publish-ai-kb.sh<br>when log.md changes<br>→ ~/.claude/wiki/ai-kb/00-index.md"]

    POST_WRITE --> JUDGE_REM["judge-reminder.sh<br>≥25 lines written to code file<br>→ JUDGE-REMINDER in context"]
    POST_WRITE --> LINT_REPORT["lint-on-write.sh (read-only)<br>.sh → shellcheck<br>.json → jq validation<br>.ts → biome check"]

    STOP --> LINT_FIX["lint-autofix.sh<br>biome check --write on .ts/.tsx<br>(if linting:enabled)<br>+ session_end event"]

    UPS --> DOCLING_RUN["detect 'ingest *.pdf'<br>→ run docling<br>→ /tmp/docling-wiki-out/"]

    PC -->|wiki/ or index.md changed| QMD_SYNC[qmd update + embed\nforeground, incremental]
    PC -->|.lightrag/ exists| LIGHTRAG_BG[wiki-index\nbackground, incremental]

    ERR_CAP -.->|accumulates| RAW_LOG[mistakes/raw-log.md]
    RAW_LOG -.->|synthesize-mistakes skill| GLOBAL_RULES[global-prevention-rules.md]
```

**Hook enforcement layer** (deterministic — shell exit code, not model reasoning):
- `exit 2` = block the tool call entirely (bash safety, agent whitelist, lint protection)
- `exit 0` = allow, with optional stdout message to model context (judge reminder, lint report)
- Stop hook fires at end of every turn regardless of tool calls

---

## Chart 7 — Agent Fleet

```mermaid
graph TD
    USER[User task]

    DELEGATOR[agent-delegator\norchestrator]

    subgraph IMPL["Implementation"]
        CW[code-writer\nSonnet]
        CWF[code-writer-fast\nHaiku — boilerplate]
    end

    subgraph REVIEW["Review / QA"]
        CR[code-reviewer\nSonnet]
        AR[architecture-reviewer\nOpus]
        DC[design-critic\nSonnet]
        SA[security-auditor\nOpus]
    end

    subgraph DEBUG["Debug / Test"]
        BDT[backend-debug-tester]
        FDT[frontend-debug-tester]
        VV[visual-verifier\nPlaywright]
    end

    subgraph EXPLORE["Explore / Plan"]
        DE[design-explorer\nOpus]
        PLAN[Plan agent\nOpus]
        EX[Explore agent\nHaiku — read-only]
    end

    subgraph OPS["Ops / Docs"]
        PPD[production-platform-devops]
        DW[docs-writer]
        PHM[project-health-monitor]
        SSR[session-report-generator]
    end

    subgraph COUNCIL["Council (subprocess — not fleet)"]
        PI_SUB["pi -p --model openai-codex/gpt-5.3-codex<br>--no-session<br>Codex peer review — advisory only<br>reads stdout, not .agents/ bus"]
    end

    USER --> DELEGATOR
    DELEGATOR --> IMPL & REVIEW & DEBUG & EXPLORE & OPS

    CW -.->|triggers| CR
    CW -.->|triggers| PHM
    PHM -.->|reports bugs to| BDT & FDT
    DE -.->|feeds requirements to| CW
    AR -.->|validates before| CW

    DELEGATOR -.->|arch/security/irreversible| PI_SUB
```

**Pi is not in the agent fleet.** It is a thin subprocess called via Bash when a Codex second opinion is needed. It does not share the Claude Code hooks system, `.agents/` coordination bus, or skill invocation contract.
