# Workflows

## Chart 1 — Claim Task Flow (Local Worktree Pool)

```mermaid
flowchart TD
    START([Orchestrator session starts])

    subgraph SETUP["Orchestrator: prep work"]
        GRILL["grill-me skill<br>align requirements"]
        PRD["to-prd skill<br>write PRD"]
        ISSUES["to-issues skill<br>break into vertical slices"]
        INBOX_WRITE["write TASK-*.md<br>to .agents/inbox/"]
        WORKTREES["create git worktrees<br>.trees/TASK-001/ etc."]
    end

    subgraph AGENTS["Parallel agent sessions — each in own worktree"]
        direction TB
        CLAIM["claim.sh: mv inbox/TASK-N.md<br>→ claimed/TASK-N.md<br>(atomic — POSIX mv)"]
        READ_TASK["read claimed task file<br>scope, acceptance criteria<br>do-not-touch list"]
        IMPL["implement in worktree<br>isolated filesystem"]
        COMMIT[git commit changes]
        MOVE_DONE["mv claimed/TASK-N.md<br>→ done/TASK-N.md"]
        STATUS["echo DONE ><br>claimed/TASK-N.status"]
    end

    subgraph RACE["Race condition: two agents, one task"]
        AG1["Agent A: mv inbox/TASK-3.md claimed/"]
        AG2["Agent B: mv inbox/TASK-3.md claimed/"]
        WIN["One succeeds → works on TASK-3"]
        LOSE["Other gets ENOENT → tries next task in inbox"]
    end

    subgraph KANBAN["/kanban-status at any time"]
        BOARD["╔ INBOX ╦ CLAIMED ╦ DONE ╗<br>║TASK-3 ║TASK-1 @A║TASK-2✓║<br>║TASK-4 ║TASK-5 @B║       ║"]
    end

    subgraph MERGE["Orchestrator: integrate"]
        REVIEW["code-reviewer agent<br>per completed task"]
        COUNCIL_GATE{"design-risk?"}
        COUNCIL_RUN["pi -p peer review<br>--model openai-codex/gpt-5.3-codex<br>--no-session"]
        MERGE_WT["merge worktrees<br>into main branch"]
        VERIFY["verify"]
    end

    START --> GRILL --> PRD --> ISSUES --> INBOX_WRITE --> WORKTREES
    WORKTREES -->|spawn N agents| CLAIM

    CLAIM --> READ_TASK --> IMPL --> COMMIT --> MOVE_DONE --> STATUS

    AG1 & AG2 -->|race| WIN & LOSE
    LOSE -->|try next| CLAIM

    STATUS -->|poll or notify| MERGE
    MOVE_DONE --> KANBAN

    MERGE --> REVIEW --> COUNCIL_GATE
    COUNCIL_GATE -->|yes| COUNCIL_RUN --> MERGE_WT
    COUNCIL_GATE -->|no| MERGE_WT --> VERIFY
```

---

## Chart 2 — Single Machine Day-to-Day Workflow

```mermaid
flowchart TD
    VIET([Viet — single machine])

    subgraph MORNING["Morning: knowledge intake"]
        DROP_SRC["drop source into raw/ or pdfs/"]
        PDF_HOOK["UserPromptSubmit hook<br>auto-runs docling on *.pdf"]
        INGEST["Claude: ingest source<br>Pre-Ingest comprehension check"]
        WIKI_WRITE["write wiki/ pages<br>update index.md + log.md"]
        GIT_CMT[git commit]
        QMD_HOOK["post-commit hook:<br>qmd update + embed<br>foreground"]
        LR_HOOK["post-commit hook:<br>wiki-index in background"]
    end

    subgraph QUERY["Anytime: query + review"]
        SKILL_Q["wiki-context skill<br>qmd BM25 + vector search"]
        CHAT_Q["wiki-chat TUI<br>LightRAG hybrid graph"]
        MCP_Q["wiki-mcp<br>Claude Code MCP tool"]
    end

    subgraph DESIGN["Design / decision"]
        COUNCIL_Q{"scope?"}
        QUICK["pi -p peer review<br>openai-codex/gpt-5.3-codex<br>--no-session<br>advisory output only"]
        FULL["council.py --chairman<br>Voice A: Sonnet (claude -p)<br>Voice B: Codex (pi -p)<br>Chair: Opus synthesis"]
        COUNCIL_OUT[".council/voice_*.md<br>+ synthesis.md<br>auto-committed"]
    end

    subgraph IMPL["Implementation work"]
        PLAN["to-prd + to-issues<br>decompose into tasks"]
        SHORT["in-process agents<br>≤5 tasks, <30 min each"]
        RALPH_S["ralph-structured<br>goal → tasks.json → /ralph-loop<br>one-task-per-iteration<br>stuckness protection (3 attempts)"]
        LONG["worktree pool<br>spawn-parallel-agents<br>claim-task protocol"]
    end

    subgraph EOD["End of session"]
        SAVE["save-session skill<br>write .claude/session-state.md<br>status: active"]
        NEXT["next session: startup hook<br>auto-injects session state<br>resume from where left off"]
    end

    subgraph MISTAKES["Continuous: error capture"]
        ERR_HOOK["PostToolUse:Bash hook<br>capture-bash-error.sh<br>→ mistakes/raw-log.md"]
        SYNTH["synthesize-mistakes<br>distill → global-prevention-rules.md"]
    end

    subgraph SAFETY["Always-on hooks"]
        BASH_GATE["PreToolUse:Bash<br>enforce-bash-safety.sh<br>blocks: rm -rf / home,<br>force-push main/master,<br>git reset --hard origin/"]
        JUDGE_REM["PostToolUse:Write/Edit<br>judge-reminder.sh<br>≥25 lines → JUDGE-REMINDER"]
        AGENT_WL["PreToolUse:Agent<br>enforce-agent-whitelist.sh<br>blocks unknown subagent_type<br>requires explicit model: param"]
    end

    VIET --> DROP_SRC --> PDF_HOOK --> INGEST --> WIKI_WRITE --> GIT_CMT
    GIT_CMT --> QMD_HOOK & LR_HOOK

    VIET -->|"ask question"| SKILL_Q & CHAT_Q & MCP_Q

    VIET -->|"architecture/security/irreversible"| COUNCIL_Q
    COUNCIL_Q -->|"quick check"| QUICK
    COUNCIL_Q -->|"full synthesis"| FULL --> COUNCIL_OUT

    VIET -->|"build something"| PLAN --> SHORT & RALPH_S & LONG

    VIET -->|"wrapping up"| SAVE --> NEXT

    ERR_HOOK -.->|"~100 entries"| SYNTH

    BASH_GATE -.-o IMPL
    JUDGE_REM -.-o IMPL
    AGENT_WL -.-o IMPL
```

**Council trigger conditions** (use DESIGN path, not IMPL):
- New service, inter-system protocol, or data model design
- Auth, permissions, secrets, trust boundary changes
- Schema migrations or destructive git ops
- Use quick `pi -p` for a single advisory check; full `council.py` when synthesis across voices is needed

---

## Chart 3 — Multi-Machine Future Architecture (Planned)

```mermaid
flowchart TD
    subgraph M1["Machine A — primary (design + orchestration)"]
        VIET_A[Viet / orchestrator session]
        GRILL_A["grill-me + to-prd"]
        ISSUE_CREATE["gh issue create<br>--label ready-for-agent<br>(handoff body format)"]
        COUNCIL_A["council.py<br>design decisions"]
        SESSION_A["save-session<br>→ .claude/session-state.md"]
    end

    subgraph GH["GitHub — shared coordination layer"]
        ISSUES_DB["GitHub Issues<br>task queue + handoff artifacts"]
        LABEL_GATE{"label?<br>ready-for-agent"}
        ACTIONS["GH Actions<br>self-hosted runner dispatch"]
        COMMENTS["issue comments<br>return-handoff per hop"]
    end

    subgraph M2["Machine B — worker (AFK implementation)"]
        RUNNER["self-hosted runner<br>claude CLI + gh CLI"]
        CLAIM_GH["gh issue list<br>--label ready-for-agent<br>claim by re-labeling"]
        IMPL_B[implement in worktree]
        PUSH_B["push branch<br>comment result on issue"]
    end

    subgraph M3["Machine C — worker (parallel)"]
        RUNNER_C[self-hosted runner]
        CLAIM_C[claim different issue]
        IMPL_C[implement]
        PUSH_C[push + comment]
    end

    subgraph MERGE_FLOW["Back on Machine A — integrate"]
        PR_REVIEW["review PRs<br>code-reviewer agent"]
        HUMAN_GATE{"human merge<br>approval"}
        SHIP[merge to main]
        WIKI_UPDATE["ingest learnings<br>back to wiki"]
    end

    VIET_A --> GRILL_A --> ISSUE_CREATE --> ISSUES_DB
    VIET_A --> COUNCIL_A
    VIET_A --> SESSION_A

    ISSUES_DB --> LABEL_GATE
    LABEL_GATE -->|auto-dispatch| ACTIONS --> RUNNER
    LABEL_GATE -->|manual| RUNNER_C

    RUNNER --> CLAIM_GH --> IMPL_B --> PUSH_B --> COMMENTS
    RUNNER_C --> CLAIM_C --> IMPL_C --> PUSH_C --> COMMENTS

    COMMENTS -->|notify| VIET_A
    VIET_A --> PR_REVIEW --> HUMAN_GATE -->|approve| SHIP
    SHIP --> WIKI_UPDATE --> ISSUES_DB

    style GH fill:#1a1a2e,stroke:#4a4aff
    style M2 fill:#1a2e1a,stroke:#4aff4a
    style M3 fill:#1a2e1a,stroke:#4aff4a
    style MERGE_FLOW fill:#2e1a1a,stroke:#ff4a4a
```

### Multi-machine gap analysis (what needs building)

| Component                         | Status              | Blocker                                          |
| --------------------------------- | ------------------- | ------------------------------------------------ |
| GitHub issue as task queue        | concept/stub        | needs impl + label convention finalized          |
| Self-hosted runner + CC CLI auth  | not built           | `ANTHROPIC_API_KEY` secret + runner setup        |
| Atomic claim via label (not `mv`) | not designed        | GitHub label race condition less clean than `mv` |
| Return-handoff via issue comment  | designed, not built | polling model undefined                          |
| Wiki sync across machines         | git push/pull       | already works — wiki is a git repo               |
| Session state sync                | not designed        | `.claude/session-state.md` is local-only         |
