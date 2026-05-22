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

    subgraph REVIEW["Council / Review"]
        COUNCIL[council.py]
        VOICE_A[Voice A — Sonnet]
        VOICE_B[Voice B — GPT]
        CHAIR[Chairman — Opus]
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

    COUNCIL --> VOICE_A & VOICE_B
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
    participant VoiceA as Voice A (Sonnet)
    participant VoiceB as Voice B (GPT-5.4)
    participant Chair as Chairman (Opus)
    participant Files as .council/ files
    participant Git

    User->>council.py: question [--chairman] [--add MODEL]

    par parallel dispatch
        council.py->>VoiceA: ask via `claude -p --model`
        council.py->>VoiceB: ask via `codex exec -o tmpfile`
    end

    VoiceA-->>Files: voice_a.md
    VoiceB-->>Files: voice_b.md

    alt --chairman flag set
        council.py->>Chair: synthesis prompt\n(all voice files concatenated)
        Chair-->>Files: synthesis.md
    end

    council.py->>Git: git add .council/ && git commit
    council.py-->>User: stdout summary
```

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
    subgraph CLAUDE_HOOKS["Claude Code hooks (settings.local.json)"]
        UPS[UserPromptSubmit\nhook]
        PTU[PostToolUse:Bash\nhook]
    end

    subgraph GIT_HOOKS["Git hooks"]
        PC[post-commit hook]
    end

    UPS -->|detect 'ingest *.pdf'| DOCLING_RUN[run docling\n→ /tmp/docling-wiki-out/]

    PTU --> ERR_CAP[capture-bash-error.sh\nlog exit≠0 → mistakes/raw-log.md]
    PTU --> PUB_KB[publish-ai-kb.sh\nwhen log.md changes\n→ ~/.claude/wiki/ai-kb/00-index.md]

    PC -->|wiki/ or index.md changed| QMD_SYNC[qmd update + embed\nforeground, incremental]
    PC -->|.lightrag/ exists| LIGHTRAG_BG[wiki-index\nbackground, incremental]

    ERR_CAP -.->|accumulates| RAW_LOG[mistakes/raw-log.md]
    RAW_LOG -.->|synthesize-mistakes skill| GLOBAL_RULES[global-prevention-rules.md]
```

---

## Chart 7 — Agent Fleet

```mermaid
graph TD
    USER[User task]

    DELEGATOR[agent-delegator\norchestrator]

    subgraph IMPL["Implementation"]
        CW[code-writer]
        CWF[code-writer-fast\nboilerplate]
    end

    subgraph REVIEW["Review / QA"]
        CR[code-reviewer]
        AR[architecture-reviewer]
        DC[design-critic]
        SA[security-auditor]
    end

    subgraph DEBUG["Debug / Test"]
        BDT[backend-debug-tester]
        FDT[frontend-debug-tester]
        VV[visual-verifier\nPlaywright]
    end

    subgraph EXPLORE["Explore / Plan"]
        DE[design-explorer]
        PLAN[Plan agent]
        EX[Explore agent]
    end

    subgraph OPS["Ops / Docs"]
        PPD[production-platform-devops]
        DW[docs-writer]
        PHM[project-health-monitor]
        SSR[session-report-generator]
    end

    USER --> DELEGATOR
    DELEGATOR --> IMPL & REVIEW & DEBUG & EXPLORE & OPS

    CW -.->|triggers| CR
    CW -.->|triggers| PHM
    PHM -.->|reports bugs to| BDT & FDT
    DE -.->|feeds requirements to| CW
    AR -.->|validates before| CW
```
