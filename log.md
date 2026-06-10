# Wiki Log

Append-only. Format: `## [YYYY-MM-DD] <operation> | <title>`

## [2026-06-09] create | Linux Machine Setup Guide

New page:
- wiki/concepts/linux-setup-guide.md — AI-executable bootstrap guide: system deps, dotfiles stow, Claude Code, plugin install, wiki toolchain, LightRAG index, ordering constraints, file ownership map

## [2026-06-08] ingest | What is an Agent Harness? — Parallel AI

New pages:
- wiki/summaries/what-is-an-agent-harness-parallel-ai.md — Parallel AI explainer; orchestrator/framework/harness taxonomy, DeepAgents, ICML 2025 modular harness, model-agnostic property

Updated:
- wiki/concepts/agent-harness.md — added Harness vs. Orchestrator vs. Framework section; model-agnostic property (with caveat); Real-World Harness Examples table; updated sources frontmatter
- index.md — added summary entry; updated concept entry description

Key new material vs existing wiki:
- Explicit 3-way taxonomy: framework (building blocks) → orchestrator (control flow) → harness (capabilities/side-effects); previously conflated
- DeepAgents: LangChain's general-purpose harness positioned as open-source Claude Code; default prompts + file system + planning utils baked in
- ICML 2025 modular harness: toggleable perception/memory/reasoning modules; improved win rates in game environments vs. unharnessed baseline
- Model-agnostic property: one harness, swappable models via standard tool-call interfaces; routing between models possible; caveat: overfitting risk documented in wiki
- "Test harness" (SE) disambiguation: different concept, context-specific usage only

Comprehension check: skipped (user explicit)

## [2026-06-08] ingest | Headroom — context compression layer (chopratejas/headroom)

Created: wiki/entities/headroom.md
Updated: wiki/concepts/context-compression.md (added CCR as 5th strategy, content-type-aware routing section)
Updated: index.md

Net new vs existing wiki:
- CCR (reversible compression with retrieval) — fifth compression pattern; complements anchored iterative
- Content-type-aware routing — JSON/AST/prose dispatch to different algorithms
- CacheAligner — automated prefix stabilization (vs our manual KV-cache design rules)
- `headroom learn` — automated CLAUDE.md failure mining (vs manual capture-mistake workflow)

Benchmark claims marked (claimed, unverified) — self-reported README only.
Comprehension check: skipped (user explicit)

## [2026-06-05] synthesis | Pi Orchestration Architecture
Created: wiki/syntheses/pi-orchestration-architecture.md
Distilled from grill session: orchestrator choice, pueue dispatch, task scoping, OpenCode Go model routing, status artifact design (resolved/unresolvedFiles/retryCount/needsHuman), two review modes (interactive vs headless), retry limit (MAX_RETRIES=3), human-commits-last.
Implemented: pi-diff-review extension in DiffViewer repo — status artifact, retry tracking, Myers diff, session_compacted cleanup.

## [2026-06-04] ingest | Building pi in a World of Slop — Mario Zechner
Created: wiki/summaries/pi-building-in-world-of-slop.md
Updated: wiki/entities/pi-agent.md (design philosophy, Terminal Bench result, self-modifying, YOLO security, pi as OpenCode's agent core)

## [2026-05-27] consolidation | wiki restructure — summary→concept/entity merge

Merged ~66 summaries into existing concept/entity/synthesis pages. Strategy: concept wins (compounding knowledge base pattern). Three buckets: entity absorptions (15), concept absorptions (~43), kept as-is (~22). Net reduction: ~188 → ~122 pages. index.md and wikilinks cleaned.

## [2026-05-26] synthesis | Agent Diff Viewer — Real-Time Code Review Tool

## [2026-05-22] ingest | Acon: Optimizing Context Compression for Long-horizon LLM Agents
Created: wiki/summaries/acon-context-compression.md
Updated: wiki/concepts/context-compression.md (added Strategy 4: adaptive guideline-optimized compression; KV-cache cost trap)
Key finding: history compression can cost more than no compression due to KV-cache invalidation; observation compression avoids this.
Note: "Top techniques to Manage Context Lengths in LLMs 1.md" is a duplicate of the already-ingested source — skipped.

## [2026-05-22] update | ralph-structured skill + auto-suggestion rule

New skill: claude-setup/skills/ralph-structured/ — structured ralph loop with task
decomposition, one-task-per-iteration, stuckness protection (3 attempts), iteration log, optional
kanban sync. Updated rule: applied-ai.md — auto-suggestion for multi-step tasks.

## [2026-05-22] ingest | Agent Harness Explained in 8min (Caleb Bright, YouTube)

Source: "Agent Harness explained in 8min...md"
New summary: summaries/agent-harness-8min
Updated concepts:
  - concepts/context-engineering — added Historical Origin section (4K token pressure narrative); added Three-Layer Stack section (additive framing)
  - concepts/agent-harness — added "Why Harness Engineering Emerged" section: summarization false-completion failure mode as the motivating problem; term coined early 2026
  - concepts/ralph-loop — added "Canonical Loop Architecture" section: PRD→JSON→single-task-per-iteration pattern; one-task design rule
Novel content: historical pressure narrative, summarization-as-fidelity-bottleneck failure mode, PRD→JSON→single-task loop as named architecture, additive 3-layer stack framing

## [2026-05-22] update | Council setup — CLI-based, file output, git auto-commit

Updated: skills/council/SKILL.md — new invocation (`council` alias), architecture (claude + codex CLIs, no API keys, .council/ file output, auto-commit)
Updated: concepts/council-pattern.md — implementations table: replaced stale "Our AGENTS.md /council" row with current setup (Sonnet 4.6 + GPT-5.4 voices, Opus 4.6 chairman)
Architecture: templates/council.py uses subprocess to claude/codex CLIs; codex exec -o writes plain text (no JSON parsing); voices → .council/voice_*.md; synthesis → .council/synthesis.md; git commit fires after each run

## [2026-05-22] ingest | Codex native stack — TOML agents, skills, .codex/ setup

Sources: "Custom instructions with AGENTS.md – Codex.md", "Harness engineering leveraging Codex in an agent-first world.md"
Updated entities: entities/codex — expanded from stub; full 3-layer stack (AGENTS.md + config.toml + TOML agents + skills); migration table from CC
Updated summaries: summaries/codex-agents-skills — corrected YAML→TOML; added skills layer; sources populated
Updated comparisons: comparisons/cc-to-cross-platform-migration — Codex skills row updated with native skills/openai.yaml
Updated entities: entities/agents-md-format — Codex row expanded with full layer description
Applied to repo: .codex/ (AGENTS.md, config.toml, agents/*.toml), skills/ (wiki-context, council, security-patterns, agent-orchestration)

## [2026-05-21] update | GitHub Issue as Handoff Artifact — gap patches
- concepts/github-issue-handoff.md — patched: issue body format spec, return-handoff via comment, lean-session checkpoint interaction, fixed .agents/inbox/ materialization format, fixed GH Actions (self-hosted runner req), added recommendation + open questions

## [2026-05-21] stub | GitHub Issue as Handoff Artifact
- concepts/github-issue-handoff.md *(stub)* — synth of /handoff + /to-issues + shared-task-queue; GitHub issue as persistent handoff artifact; auto-dispatch via Actions webhook
- index.md, log.md updated

## [2026-05-21] ingest | Matt Pocock /handoff Skill
- summaries/mattpoccock-handoff-skill.md — /handoff: parallel session fork via focused context slice; handoff vs compact; grilling→prototype→back; cross-agent; GitHub issue as handoff artifact
- summaries/mattpocockskills.md — added /handoff to Productivity skill table
- index.md, log.md updated

## [2026-05-21] ingest | Pen Testing — AWS Security Agent + PentAGI + OWASP Web Security Batch
- summaries/aws-security-agent.md — AWS managed pen test service; target/accessible/out-of-scope domain split; credential injection; IAM scope patterns
- entities/pentagi.md — OSS autonomous pen test system; orchestrator + 3 specialists; pgvector + Neo4j memory; chain summarization; Flow→Task→SubTask hierarchy
- concepts/pentest-agent-design.md — synthesis blueprint for Next.js + ECS + Neon pen test agent; supervisor+specialists; two-phase (black-box + gray-box AWS); safety constraints; output pipeline
- summaries/owasp-web-security-stubs.md — batch stubs for 26 OWASP cheat sheets (SQLi, session, CSRF, XSS, IDOR, Docker, cloud, secrets, SSRF, DoS, deserialization, supply chain)
- index.md, log.md updated

## [2026-05-19] ingest | Agentic Engineering Control Plane (product concept) — summaries/agentic-control-plane-concept.md; 4-layer architecture (execution/coordination/quality/experience); Phase 0–5 roadmap; Phase 0.5 five concrete additions; buy vs build decisions; cross-links to shared-task-queue, worktree-isolation, council-pattern

## [2026-05-19] ingest | Control Plane Expansion Plan (synthesis) — syntheses/control-plane-expansion-plan.md; Phase 1 gap analysis table (6 requirements, coverage vs gap); tool landscape (buy: CodeRabbit/Langfuse/PromptFoo/GitHub Projects; build: registry/event-log/kanban-skill/approval-workflow); Phase 2 git-branch atomic claim design; Phase 3 council quality gate wiring

## [2026-05-12] new | concepts/worker-coordination — partial result coordination between parallel agents: contract-first, pipeline, filesystem blackboard, actor mailbox patterns; decision table; failure modes (silent dependency, partial write race, scope bleed)

## [2026-05-12] update | agent-primitive-selection — added partial-results branch to decision tree; links to concepts/worker-coordination

## [2026-05-12] update | wiki-index + wiki-mcp — added OpenRouter as 3rd backend stub (OPENROUTER_API_KEY env var, NotImplementedError until wired); updated docstring

## [2026-05-12] update | agent-delegator — removed dead wiki_query/wiki-mcp branch (tool not available in Claude Code sessions)

## [2026-05-12] update | syntheses/local-rag-wiki — complete rewrite; removed stale qmd+ollama "current state" framing; documented actual deployed stack: wiki-chat (LightRAG TUI, local-only), wiki-index (incremental, hybrid backend), wiki-mcp (MCP server, OpenCode integration), post-commit hook; updated index.md entry

## [2026-05-12] ingest | Codebases are uniquely hard to search semantically (Greptile, Daksh) — absorbed into concepts/contextual-retrieval; added code search section: cosine sim 0.728 (code) vs 0.815 (NL description), noise dilution data; explains why wiki NL pages avoid the code search problem

## [2026-05-12] update | claude-setup/agents/agent-delegator.md — added wiki-mcp (wiki_query MCP tool) as graph-aware synthesis path alongside qmd fast lookup; split knowledge access into fast lookup vs graph-aware query sections

## [2026-05-13] lint — fixed broken wikilink concepts/self-refinement→summaries/self-refinement in preference-feedback-loop; added backlinks: codegraphcontext→ai-code-review, llm-eval-pipeline→agentic-cicd + verification-pipeline; patterns/ cluster (13 files) remains systemic orphan

## [2026-05-13] ingest | CodeGraphContext README — entities/codegraphcontext.md; claude-init Step 0.5 (codebase scan + CGC decision gate + hybrid persistence); agent-delegator + code-reviewer updated with CGC query routing table; GUIDE.md §4 + §6 updated

## [2026-05-13] ingest | LLM Eval Pipeline — 4 sources: pragmatic-engineer-llm-evals, hamel-evals-faq, selecting-ai-evals-tool, hamel-evals-skills; concepts/llm-eval-pipeline + concepts/rag-evaluation created

## [2026-05-11] update | GUIDE.md — added wiki-chat/wiki-index (LightRAG RAG) to §2 search, §3.1 skills, §6 playbooks; added docs-writer agent to §3.2 feature dev; added interactive wiki query and documentation playbooks

## [2026-05-11] build | wiki-chat TUI (LightRAG v2) — migrated from qmd+ollama to LightRAG graph-aware retrieval; phi4-mini + nomic-embed-text (768 dim); manifest-based incremental indexing; modes: local/global/hybrid/naive; ~/.local/bin/wiki-chat + wiki-index; summaries/agentic-search-vs-rag.md + summaries/local-rag-elasticsearch.md ingested to validate RAG stack choice

## [2026-05-11] build | wiki-chat TUI — ~/.local/bin/wiki-chat; qmd+ollama local assistant; qmd index refreshed (349 pages, 1818 chunks embedded); syntheses/local-rag-wiki.md future-dev note created

## [2026-05-10] ingest | Actor Model (2 sources: thesis + Orleans docs)
- New concept page: concepts/actor-model — 3 primitives, mailbox semantics, no-shared-state rule, location transparency, actor vs threads vs CSP, supervision trees (one_for_one/one_for_all/rest_for_one), virtual actor model (Orleans grains/silos), implementations table (Erlang/Elixir/Akka/Akka.NET/Orleans/ProtoActor), when-to-use guide
- Updated: summaries/awesome-software-architecture — WIKI-CANDIDATE flag removed
- Updated: index.md — new entry under Concepts

## [2026-05-10] ingest | Awesome Software Architecture (mehdihadeli curated list — 2 sources, link dump)
- New summary: summaries/awesome-software-architecture — topic taxonomy extraction; cross-linked to existing systems/ and patterns/ pages; WIKI-CANDIDATE flagged for Actor Model

## [2026-05-10] ingest | HN: How should junior programmers use AI for programming?
- New summary: summaries/hn-junior-devs-and-ai — AI as multiplier not substitute; repetition/debugging gap; 70/30 heuristic; agentic tools harmful for juniors; 7 actionable heuristics; community atrophy concern

## [2026-05-10] skip | anthropic claude-cookbooks — shallow README, link catalog only, no technique depth or pattern explanations; no wiki page created

## [2026-05-10] ingest | Living dangerously with Claude (Simon Willison talk)
- New summary: summaries/living-dangerously-with-claude — YOLO mode UX vs. lethal trifecta risk; sandbox-exec macOS proxy pattern; AI-layer defenses insufficient
- Updated: concepts/agentic-sandbox-controls — added macOS sandbox-exec + HTTP proxy section with deprecation warning
- Updated: concepts/indirect-prompt-injection — added lethal trifecta named subset

## [2026-05-07] ingest | DSPy (4 sources: Stanford README, dbreunig pipeline walkthrough, HuggingFace GEPA cookbook, DSPy docs)
- New entity: entities/dspy — Signatures/Modules/Optimizers stack; GEPA error-driven prompt augmentation; module/optimizer comparison tables
- New summary: summaries/dspy — architecture, GEPA mechanics, performance claims marked (claimed, unverified), limitations, decision criteria

## [2026-05-07] write | Preference Feedback Loop + RLHF/RLAIF/Self-Refine cluster — created concepts/preference-feedback-loop.md, summaries/rlhf-cai.md, summaries/self-refinement.md; updated concepts/agent-self-correction.md with Self-Refine relation section and new cross-links; updated index.md

## [2026-05-07] ingest | Cloudflare Agent Memory (Agents that remember introducing Agent Memory.md)

## [2026-05-06] ingest | patterns/api-design

## [2026-04-20] init | Wiki scaffolded
## [2026-04-21] ingest | LLM Wiki Pattern (llm-wiki.md)
## [2026-04-22] ingest | Contextual Retrieval in AI Systems (Contextual Retrieval in AI Systems.md)
## [2026-04-22] ingest | AI Agent Dev Workflows (4 sources: Using GitHub Copilot to reduce technical debt.md, General Best Practices for vetting AI Code.md, Build an optimized review process with Copilot.md, Review AI-generated code.md)
## [2026-04-22] ingest | Practical Security Guidance for Sandboxing Agentic Workflows and Managing Execution Risk.md
## [2026-04-23] ingest | Anti-Bot Evasion Tactics (5 sources: Anti-bot score and scope.md, Bypassing Cloudflare with Puppeteer Stealth Mode.md, How can one rotate proxies.md, Max success in web scraping.md, Pros and Cons of Free Paid Hybrid Stack.md)
## [2026-04-23] re-ingest | Moved to raw/: Max success in web scraping.md, Pros and Cons of Free Paid Hybrid Stack.md — content already captured in summaries/anti-bot-evasion-tactics
## [2026-04-23] ingest | Amazon Scraping 2026 (How to Scrape Amazon Data in 2026 with Python.md)
## [2026-04-23] ingest | Pydoll Network & Fingerprinting (3 sources: Overview - Pydoll.md, Network Fundamentals - Pydoll.md, Legal & Ethical - Pydoll.md)
## [2026-04-25] ingest | Agent Harness Engineering (2 sources: The Anatomy of an Agent Harness.md, Harness engineering leveraging Codex in an agent-first world.md)
## [2026-04-25] ingest | Autoresearch: Autonomous ML Experimentation (karpathyautoresearch AI agents running research on single-GPU nanochat training automatically.md)
## [2026-04-25] synthesis | Context engineering consolidation — absorbed context-engineering-marketplace plugins into wiki (context-degradation, context-compression, tool-design-for-agents); updated agent-harness.md with token budget and KV-cache rules; updated applied-ai.md with agent engineering heuristics
## [2026-04-26] ingest | Agent orchestration cluster (7 sources): wshobsonagents, Create custom subagents, Orchestrate teams of Claude Code sessions, Agent Skills, Claude Agent Skills First Principles Deep Dive, Automated Security Reviews in Claude Code, Exit Code 0 Is Not Quality
## [2026-04-26] ingest | Agent Skills pair (2 sources): Agent Skills.md, Claude Agent Skills A First Principles Deep Dive.md → concepts/agent-skills.md
## [2026-04-26] synthesis | Claude Code agent architecture — new concept pages: agent-skills, agent-subagents, agent-teams, verification-pipeline; new summaries: exit-code-0-quality, wshobson-agent-orchestration, automated-security-reviews; new templates: subagent.md, skill.md, agent-team-plan.md
## [2026-04-26] lint | Link audit: fixed 29 broken wikilinks (bare slug → full path), resolved 17 orphans → 0 by adding backlinks to concept pages; 39 pages, 0 orphans, 0 broken links
## [2026-04-27] ingest | Context window cluster (5 sources: Context windows.md, LLM context windows what they are & how they work.md, Top techniques to Manage Context Lengths in LLMs.md [×2 duplicate], Effective context engineering for AI agents.md, Memory & context management with Claude Sonnet 4.6.md) → summaries/context-window-cluster, concepts/context-window, concepts/context-engineering, concepts/agentic-memory-tool
## [2026-04-27] ingest | Software Documentation (2 sources: How to write software documentation.md, Documentation done right A developer's guide.md) → summaries/software-documentation, concepts/software-documentation
## [2026-04-27] ingest | Testing cluster (3 sources: 15 Unit Testing Best Practices.md, Unit Testing Best Practices.md, CICD Testing Explained.md) → summaries/unit-testing-best-practices, summaries/cicd-testing, concepts/unit-testing, concepts/cicd-testing; skipped pre-ingest quiz per user request
## [2026-04-27] rules | Added: caveman ultra mode rule (communication.md), 50-line code generation limit (editing.md), pre-ingest comprehension quiz, progress retention, periodic review (CLAUDE.md); new docs-writer agent in dotfiles
## [2026-04-26] ingest | Claude Code Plugins — llm-wiki as plugin (Claude Code Plugins - llm-wiki as plugin.md) → summaries/claude-code-plugins-llm-wiki, concepts/claude-code-plugins; created ~/dotfiles/llm-wiki-plugin scaffold with plugin.json + 3 skills (wiki, agent-patterns, security)
## [2026-04-26] synthesis | Wiki/dotfiles gap audit — new pages: concepts/owasp-security-checklist (from security-patterns skill), syntheses/agent-primitive-selection (decision tree from agent-orchestration skill); updated stale gap notes in automated-security-reviews and wshobson-agent-orchestration; 41 pages, 0 orphans, 0 broken links
## [2026-04-29] ingest | Matt Pocock Skills (mattpocockskills Skills for Real Engineers. Straight from my .claude directory..md) → summaries/mattpocockskills, concepts/domain-glossary; 9 skills installed to ~/.claude/skills/
## [2026-04-29] ingest | Firecrawl MCP Server (Firecrawl MCP Server.md) → summaries/firecrawl-mcp-server, entities/firecrawl
## [2026-04-29] ingest | Superpowers Plugin v5.0.7 (local cache) → summaries/superpowers-plugin; enabled plugin in settings.json
## [2026-04-29] integration | Startup auto-context: added rules/wiki-startup.md → CLAUDE.md; wiki-context skill updated with new content; superpowers enabled
## [2026-04-30] ingest | Matt Pocock Full Walkthrough Workflow (Full Walkthrough Workflow for AI Coding — Matt Pocock.md) → summaries/mattpocockworkflow, concepts/deep-modules; updated context-compression (clear-over-compact), context-degradation (smart zone/dumb zone), mattpocockskills (cross-ref)
## [2026-04-30] ingest | Docling (3 sources: Docling.md, From PDF to Markdown Why Document Parsing is Important For RAG..md, docling-projectdocling Get your documents ready for gen AI.md) → summaries/docling, entities/docling
## [2026-04-30] update | Added pdfs/ to directory layout in CLAUDE.md; added PDF ingest operation; updated summaries/docling with two-path pipeline (wiki vs RAG)
## [2026-04-30] ingest | Evolution Strategies cluster — 3 PDFs via Docling
- pdfs/1703.03864v2.pdf (OpenAI ES 2017) → summaries/openai-es-2017
- pdfs/2509.24372v2.pdf (ES LLM Fine-tuning 2025) → summaries/es-llm-finetuning-2025
- pdfs/2511.16652v2.pdf (EGGROLL 2025) → summaries/eggroll-2025, entities/eggroll
- new: concepts/evolution-strategies (ties all 3 together)
## [2026-05-01] ingest | Claude Usage and Length Limits (How do usage and length limits work?.md) → summaries/claude-usage-limits; updated concepts/context-window with product vs API context window distinction (200K product vs 1M API)
## [2026-05-04] ingest | OpenCode Model Switching + Pi Agent (2 sources)
- Claude runaway... tried Kimi 2.6 and Deepseek v4.md → summaries/opencode-model-switching-reddit
- pi-monopackagescoding-agent at main.md → entities/pi-agent
- New concepts: concepts/agent-self-correction, concepts/instinct-clustering, concepts/dynamic-context-pruning
- Updated: multi-vendor-adversarial-review (GitHub Copilot council models)
- New templates: templates/AGENTS.md, templates/lean-compaction-plugin.ts, templates/env-model-routing.sh
## [2026-05-05] ingest | Karpathy LLM Council (karpathyllm-council LLM Council works together to answer your hardest questions.md)
- New entity: entities/karpathy-llm-council (3-stage protocol, anonymized peer review, Chairman synthesis)
- New concept: concepts/council-pattern (fills reviewer gap; general pattern across all implementations)
- Updated: concepts/multi-vendor-adversarial-review (added Karpathy as implementation); index.md
- Key additions: anonymization technique, Chairman vs human synthesis tradeoff, council cost model (~10-15x single query)
## [2026-05-04] council-review | Adversarial review + structural audit of full wiki
- Council (devil's advocate): challenged 8 core theses; Top 3 improvements applied
- Applied: agent-self-correction (known limitation + harness-enforced hooks), context-compression (when-compact-wins + scoped evidence), mattpocockworkflow (for-whom + fails-when), spec-driven-frameworks (demoted "consensus" to scoped n≈30), agent-primitive-selection (harness>model scope + DeepSeek max-reasoning limits + vertical-slices fails-when)
- Fixed: GPT-4.1 naming in pi-agent.md, mattpocockworkflow "Contrarian position" label, auto-commit trigger page pointer
- Coverage gaps flagged (future pages): Council pattern, AGENTS.md cross-provider spec, Worktree isolation
- Known debt: YAML quoting in ~11 sources: fields; 17.2x DeepMind citation unverified; wshobson agent count discrepancy (184 vs 153)
## [2026-05-04] ingest | Spec-Driven Frameworks vs Native CC (Reddit thread + Plugins for Opencode.md) — 2 sources
- New summaries: summaries/spec-driven-frameworks-reddit
- New entities: entities/sandcastle, entities/dangeresque, entities/mnemory, entities/agentops, entities/opencode
- New concepts: concepts/multi-vendor-adversarial-review, concepts/branch-strategy-for-agents
- New comparisons dir + pages: comparisons/spec-driven-frameworks-vs-native, comparisons/claude-code-vs-opencode-plugins
- Updated: mattpocockworkflow (Dangeresque/SandCastle alternatives), agentic-memory-tool (Mnemory parallel), agentic-sandbox-controls (Anthropic ToS constraint), context-compression (clear-over-compact = consensus), agent-primitive-selection (multi-vendor review pattern); index.md
## [2026-05-06] ingest | AGENTS.md ecosystem — 8 sources
- Sources: AGENTS.md (spec), Custom instructions with AGENTS.md – Codex.md, Agents-opencode.md, AGENTS md gets it wrong in 2 ways.md, Rules.md, SPARC CursorCline Rules guide.md, coding-agent-rulesmemory.md at main.md, coding-agent-rulesmemory.md at main 1.md
- New summaries: summaries/agents-md-spec, summaries/codex-agents-md, summaries/agents-md-critique, summaries/sparc-cursor-cline-rules
- New entities: entities/agents-md-format, entities/codex (stub)
- New concepts: concepts/rules-vs-hooks, concepts/memory-bank-pattern
- Updated: entities/opencode (agent model: primary/subagent/hidden, AGENTS.md precedence, instructions field), concepts/agent-context-instructions (AGENTS.md ecosystem section, multi-file strategies, nested precedence)
- Key additions: Linux Foundation stewardship of AGENTS.md; compliance-vs-enforcement distinction; Memory Bank as cross-session state via repomix; rules-vs-hooks as architectural choice
- Committed: concepts/worktree-isolation (was pending from previous session)
## [2026-05-06] synthesize | Lean Agentic Workflow
- New synthesis: syntheses/lean-agentic-workflow
- Ties together: grill→PRD→AFK loop, council, lean-session plugin, model routing, .agents/ state, failure modes
- Also fixed: templates/AGENTS.md cross-provider claim (Opus issue A); pi-agent.md AGENTS.md support marked unverified
## [2026-05-06] ingest | OpenCode DCP plugin — 2 sources
- Sources: Opencode-DCPopencode-dynamic-context-pruning.md, Quick Start Install DCP Plugin opencode-dynamic-context-pruning.md
- New summary: summaries/opencode-dcp
- New entity: entities/opencode-dcp
- Updated: concepts/dynamic-context-pruning (removed status: documented-not-adopted; corrected mechanism descriptions; removed fabricated config block; added real commands, thresholds, cache trade-off)
- Key corrections: Compress is model-triggered (not per-turn automatic); dedup runs on LLM fetch; config fields pruneAfterTurns/maxFileContentTokens/preserveLastN were invented — none exist in real plugin
- index.md: dynamic-context-pruning promoted (removed documented-not-adopted marker); new entries for summary + entity
## [2026-05-06] ingest | Cross-platform migration audit — 5 sources (Gemini, OpenCode, Codex, Cursor)
- New summaries: gemini-cli-rules, opencode-commands-agents, codex-agents-skills, cursor-rules-background-agents
- New comparison: comparisons/cc-to-cross-platform-migration — full 6-layer migration matrix (rules/skills/subagents/hooks/plugins/settings) across 4 platforms; parity ratings
- Updated: entities/codex (expanded from stub — TOML agents + native skills + 3-layer stack); entities/agents-md-format (corrected Gemini + Cursor rows, expanded Codex row)
- Key corrections from audit: Codex agents are TOML (not YAML); Gemini uses GEMINI.md with @file.md imports (not AGENTS.md); OpenCode commands can bind directly to agents (stronger than CC skills); Cursor background agents now support rules but have no subagent/skill equivalent
- Search backlog added: cursor.com/docs/cloud-agent, opencode.ai/docs/config, blakecrosley AGENTS.md patterns, Gemini custom tools docs
## [2026-05-06] ingest | Autonomous agent docs cluster — 4 sources (CC permissions, self-healing CI/CD, error budget)
- New summaries: claude-code-permissions-settings, self-healing-cicd-implementations, error-budget-agentic
- New concept: concepts/error-budget — SRE error budget adapted to agent loops; 4 budget axes; progress score; rollback design
- Updated concepts: self-healing-loop (Dagger/ArgoCD/Windmill impl table), agentic-sandbox-controls (rewritten autonomous section with correct settings.json schema)
- Schema correction propagated: allowedTools/disallowedTools/allowedPaths → permissions.allow/deny + sandbox.filesystem in 4 files (agentic-sandbox-controls, worktree-isolation, comparisons/spec-driven-frameworks-vs-native, dangeresque)
- Critical finding: sandbox.enabled only sandboxes Bash; Read/Edit/Write built-in tools bypass it — OS-level isolation still required
## [2026-05-06] ingest | Autonomous full-stack agent setup prompt → 2 new concepts + sandbox update
- Source: user prompt describing autonomous CC setup, self-healing loop, agentic CI/CD
- New: concepts/self-healing-loop — failure signature detection, retry budgets by type, rollback protocol, composition with ralph-loop
- New: concepts/agentic-cicd — CI as external watchdog, 10-gate sequence, staging-first, builder/deployer network split, diff size cap, no destructive migration auto-run
- Updated: concepts/agentic-sandbox-controls — added --dangerously-skip-permissions section with critical safety rule; builder/deployer network pattern; docs-needed marker for settings.json schema
- Gaps flagged (need online sources): CC settings.json allowedTools/allowedPaths exact schema, "sandbox":true behavior, real self-healing pipeline implementations, error budget as agent loop guardrail
## [2026-05-06] fix | Structural gap fixes — 4 gaps from council review
- Gap 1 (new): entities/lean-session — plugin entity page from templates/lean-compaction-plugin.ts; 3 hooks documented
- Gap 2 (cross-link): lean-agentic-workflow.md Session State section — added [[entities/agentops]] anchor; lean-session section — added [[entities/lean-session]] link
- Gap 3 (scope): agent-self-correction.md verification trigger — split into UI/visual (verification-pipeline) and backend/logic (unit-testing + cicd-testing)
- Gap 5 (symmetry): agent-self-correction.md Related Pages — added [[concepts/rules-vs-hooks]]
- Gap 4 confirmed resolved: agentic-sandbox-controls already had ToS/Docker section
- index.md: added lean-session entity entry
## [2026-05-06] ingest | patterns/backend + architectural-patterns update
- Sources: Design Patterns for Modern Backend Development – with Example Use Cases.md, Design Patterns for Modern Backend Development.md, mehdihadeliawesome-software-architecture (link index — used for pattern taxonomy only)
- Replaced stub: wiki/patterns/backend.md — middleware chains (composition order, error/auth placement), JWT vs session, OAuth2 flows, RBAC vs ABAC, service layer, repository pattern, queue/worker (at-least-once, DLQ, task queue vs event stream), DI (constructor vs service locator), API gateway, anti-pattern taxonomy
- Updated: wiki/systems/architectural-patterns.md — added Modular Monolith and Vertical Slice Architecture sections; Awesome Software Architecture sources are link indexes only (no substantive content beyond section names)
- index.md: backend promoted from stub; architectural-patterns description updated

## [2026-05-07] ingest | CC permissions deep-dive + auto mode (Configure permissions.md, Claude Code auto mode.md)
## [2026-05-07] ingest | CC sandboxing official docs (Sandboxing.md)
## [2026-05-07] ingest | CC agent teams official docs (Orchestrate teams of Claude Code sessions.md)
## [2026-05-07] ingest | CC skills official docs + first-principles deep dive (Agent Skills.md, Claude Agent Skills A First Principles Deep Dive.md)
## [2026-05-07] ingest | Gemini CLI tools reference + full feature audit (Tools reference.md, Gemini CLI documentation.md, Provide context with GEMINI.md files.md, Gemini CLI Custom slash commands.md, Custom commands.md)
## [2026-05-07] ingest | Cursor Cloud Agents (Cloud Agents Cursor Docs.md)
## [2026-05-07] ingest | Context engineering Anthropic (Effective context engineering for AI agents.md, Memory & context management with Claude Sonnet 4.6.md)
## [2026-05-07] ingest | Context window management techniques (Top techniques to Manage Context Lengths in LLMs.md)
## [2026-05-07] ingest | Docker Sandboxes for coding agents (Docker Sandboxes Run Claude Code and More Safely.md, Claude Code Sandbox Guide.md)
## [2026-05-07] update | gemini-cli-rules.md — added TOML commands section; corrected Skills parity row (Low→High)
## [2026-05-07] update | cc-to-cross-platform-migration.md — updated Gemini Skills row (parity Low→High; TOML format)
## [2026-05-07] create | entities/gemini-cli.md — full entity with tool table, TOML commands, Skills, feature parity matrix
## [2026-05-07] create | summaries/cc-auto-mode.md — 2-stage classifier, threat model, block categories, metrics
## [2026-05-07] create | summaries/cc-agent-teams.md — architecture, hooks, limitations, subagent definitions as teammates
## [2026-05-07] create | summaries/context-engineering-anthropic.md — JIT retrieval, compaction, note-taking, sub-agents, context editing API
## [2026-05-07] create | summaries/docker-sandboxes.md — microVM isolation, Docker-in-Docker, multi-agent support
## [2026-05-07] create | summaries/cursor-cloud-agents.md — VM isolation, GitHub workflow, remote desktop, access points
## [2026-05-06] scaffold | patterns/ + systems/ wiki directories
## [2026-05-06] expand | patterns/refactoring + patterns/algorithmic — both promoted from stub to full pages
- patterns/refactoring: 13 Fowler techniques (triggers, before/after snippets, anti-patterns, order-of-operations guide); source: Refactoring and Design Patterns.md (thin — Fowler catalog applied from domain knowledge)
- patterns/algorithmic: 15 pattern families (problem shape, recognition trigger, complexity, templates); source: Common Algorithm Patterns Cheat Sheet.md
## [2026-05-06] expand | patterns/design-patterns-creational — replaced stub with full page covering all 5 GoF creational patterns
- Sources: Factory Method.md, Abstract Factory.md, Abstract Factory in Go.md, Builder.md, Prototype.md, Singleton.md, Design Patterns in TypeScript.md
- Structure per pattern: intent + when-to-use + when-NOT-to-use + TypeScript sketch + anti-patterns; comparison table at end
- index.md: removed stub marker, updated description
## [2026-05-06] expand | patterns/design-patterns-behavioral — replaced stub with full page covering all 10 GoF behavioral patterns + Domain Event
- Sources: Chain of Responsibility.md, Command.md, Iterator.md, Mediator.md, Memento.md, Observer.md, State.md, Strategy.md, Template Method.md, Visitor.md, Domain Event.md, Design Patterns in TypeScript.md
- Structure per pattern: intent + when-to-use + when-NOT-to-use + TypeScript sketch + anti-patterns
- Includes confusion table: Observer vs Mediator, Strategy vs State, Command vs CoR
- Cross-links: concepts/agent-skills (Strategy basis), patterns/principles, patterns/design-patterns-creational, patterns/design-patterns-structural
- index.md: removed stub marker, updated description
## [2026-05-06] expand | patterns/design-patterns-structural — replaced stub with full page covering all 7 GoF structural patterns
- Sources: Adapter.md, Bridge.md, Composite.md, Decorator.md, Facade.md, Flyweight.md, Proxy.md, Design Patterns in TypeScript.md
- Structure per pattern: intent + when-to-use + when-NOT-to-use + TypeScript sketch + anti-patterns
- Includes Adapter/Facade/Proxy confusion table (interface change, scope, purpose, transparency)
- Includes pattern selection signal table (code smell → pattern mapping)
- Cross-links: patterns/principles, patterns/design-patterns-creational, patterns/design-patterns-behavioral, concepts/deep-modules
- index.md: removed stub marker, updated description

## [2026-05-06] expand | systems/ — replaced all 6 stubs with full pages
- Sources: system-design-primerREADME.md at master.md, Decompose monoliths into microservices by using CQRS and event sourcing - AWS Prescriptive Guidance.md, Machine-Learning-InterviewssrcMLSDml-system-design.md at main.md
- systems/distributed-systems: CAP theorem (CP vs AP), eventual consistency conflict resolution (LWW/vector clocks/CRDTs), idempotency patterns, circuit breaker (state machine), backpressure strategies, saga choreography vs orchestration, 2PC avoidance, distributed locks + fencing tokens
- systems/architectural-patterns: monolith vs microservices (decision criteria), event-driven architecture failure modes, CQRS (when warranted, AWS DynamoDB Streams reference implementation), event sourcing, hexagonal architecture, layered architecture, strangler fig migration
- systems/system-design-process: 6-step process (requirements → capacity estimation → component decomposition → data flow → tradeoff articulation → scaling), latency reference table, common interview mistakes table
- systems/scalability-reliability: 4 cache update strategies (cache-aside/write-through/write-behind/refresh-ahead), sharding shard key selection + failure modes, 5 rate limiting algorithms, L4 vs L7 load balancing, RED/USE observability methods, SLO/SLA/availability numbers table
- systems/data-modeling: 5 DB type decision criteria table, normalization (1NF-3NF) vs denormalization decision, expand-contract schema evolution, event sourcing data model, polyglot persistence tradeoffs, access-pattern-driven design
- systems/ai-ml: 9-step ML system design process, offline/online metrics, feature stores (training-serving consistency), model selection heuristic, batch vs real-time vs hybrid serving, edge inference (quantization/pruning/distillation), A/B/shadow/canary deployment, covariate vs concept drift; AI agent patterns → wiki/concepts/ pointers
- index.md: all 6 systems/ entries promoted from stubs to substantive descriptions

## [2026-05-06] expand | patterns/frontend + patterns/concurrency + patterns/database — replaced all three stubs with full reference pages
- Sources: Design Patterns for React Interviews.md, Persson Dennis - 21 Fantastic React Design Patterns and When to Use Them.md, Mastering Concurrency A Guide for Software Engineers.md, Mastering Concurrency A Senior Engineer's Survival Guide.md, A detailed guide on Database Indexes.md
- patterns/frontend: 9 component patterns (custom hooks, container/presentational, compound components, headless, HOC, render props, provider, error boundary, portal, atomic design); state management decision table; CSR/SSR/SSG/ISR; performance (memo/lazy/virtualization); CSS architecture; SOLID in React
- patterns/concurrency: thread safety fundamentals, mutex/semaphore/RWLock/atomic/condition variables, memory models (ordering, false sharing), race condition detection, deadlock (Coffman conditions + prevention strategies), async/await pitfalls table, actor model, CSP, parallel algorithm patterns, backpressure
- patterns/database: indexing strategies (B-tree/hash/composite/covering/bitmap/filtered/full-text) with when-to-use; EXPLAIN / query plan reading; N+1 detection and fix; connection pooling (parameters, PgBouncer modes); ACID, isolation levels, optimistic vs pessimistic locking; read/write splitting; denormalization triggers
- index.md: removed stub markers, updated descriptions for all three

## [2026-05-06] expand | patterns/principles + patterns/code-quality — replaced both stubs with full reference pages
- Sources: The SOLID Principles of Object-Oriented Programming Explained in Plain English.md, What Is Clean Code? A Guide to Principles and Best Practices.md
- patterns/principles: SOLID (each principle: definition, rationale, violation, fix, anti-patterns), DRY, YAGNI, KISS, LoD, SoC, composition over inheritance; decision table
- patterns/code-quality: naming conventions, function discipline (size/SRP/abstraction/params), cognitive complexity mitigations, comment discipline, magic numbers/constants, code smell taxonomy (structural + AI-specific); AI-generated code pitfall section
- index.md: removed stub markers, updated descriptions for both

## [2026-05-07] ingest | LLM-as-Judge (3 sources: evidentlyai guide, Monte Carlo best practices, Datadog custom evaluations)
- New concept: concepts/llm-as-judge — evaluation modes (pairwise/direct/G-Eval/span/trace), rubric axes, failure modes, RLHF relation, implementation notes
- New summary: summaries/llm-as-judge — problem statement, core technique, production incident (Monte Carlo compliance drop), best practices, limitations
- Updated: concepts/multi-vendor-adversarial-review — added LLM-as-judge as the evaluation mechanism section; added [[concepts/llm-as-judge]] to relation links; updated sources + frontmatter date
- index.md: added entries for both new pages

## [2026-05-06] ingest | patterns/error-handling
- Sources: Best practices for exceptions.md, Error handling patterns.md, General error handling rules    Technical Writing.md
- patterns/error-handling: error taxonomy (expected/unexpected, recoverable/fatal, business/technical), fail-fast, exceptions vs Result types, railway-oriented programming, propagation and rethrow discipline, exponential backoff with jitter, API error response design, logging discipline, anti-pattern table
- index.md: removed stub marker, updated description

## [2026-05-11] ingest | opencode-config
- Sources: Config.md
- summaries/opencode-config: 8-level config precedence, merge semantics, TUI/server/compaction/permission options, variable substitution ({env:VAR}, {file:path}), MDM managed settings
- entities/opencode: added Config.md to sources; added Config Precedence section
- summaries/opencode-commands-agents: fixed empty sources field → ["Agents-opencode.md", "Rules.md"]
- index.md: added summaries/opencode-config entry

## [2026-05-11] ingest | mintlify-docs-guide
- Sources: Introduction.md, Content types.md, Organize navigation.md, Style and tone.md, Maintenance.md, Tracking success.md, Understand your audience.md, Using media.md
- summaries/mintlify-docs-guide: Diátaxis 4-type framework, AI agents as explicit audience, navigation for LLM retrieval, maintenance strategies
- concepts/software-documentation: added Diátaxis framework table, AI agents as explicit audience section, new sources/references
- index.md: added summaries/mintlify-docs-guide, updated concepts/software-documentation description

## [2026-05-11] ingest | agentic-search-vs-rag + local-rag-elasticsearch
- Sources: 3× RyanNg agentic-search-vs-rag files + Local RAG Elasticsearch.md
- summaries/agentic-search-vs-rag: 30-question benchmark; graph search 2× IoU, 99% fewer tokens vs flat RAG; RAG only wins dependency recall; validates LightRAG choice for wiki
- summaries/local-rag-elasticsearch: Elasticsearch+LocalAI stack; retrieval 14ms, LLM 16s; model size/latency table
- templates/wiki-index + wiki-chat: optimized LightRAG config (chunk_token_size=800, top_k=20, cosine_threshold=0.3, ids/file_paths passed to ainsert)
- index.md: added 2 new summary entries, updated local-rag-wiki entry

## [2026-05-12] ingest | OWASP AI Security Cheat Sheets (2 sources)
- Sources: AI Agent Security + Secure Coding with AI (OWASP Cheat Sheet Series)
- summaries/owasp-ai-security: combined summary; AI Agent Security (8 best practices, 11 risks); Secure Coding with AI (14 threat sections: slopsquatting, rules file injection, CI/CD confused deputy, test fabrication, MCP tool shadowing)
- concepts/indirect-prompt-injection: added dev-loop attack vectors (issues, PRs, changelogs, error traces), rules files as persistent steering, CI/CD confused deputy, MCP tool shadowing section
- concepts/owasp-security-checklist: expanded AI-specific risks section with tool security, memory security, DoW, slopsquatting, test fabrication, CI/CD confused deputy, multi-agent propagation
- index.md: added owasp-ai-security summary entry, updated owasp-security-checklist + indirect-prompt-injection entries

## [2026-05-12] ingest | OWASP AI Model Ops + GitHub Actions Security
- Sources: Secure AI Model Ops + GitHub Actions Security (OWASP Cheat Sheet Series)
- summaries/owasp-ai-security: extended with Secure AI Model Ops section (circuit breakers, chain-depth limits, spend limits for agentic flows) and GitHub Actions Security section ("clinejection" real-world attack name, SHA pinning, impostor commit detection)
- index.md: updated owasp-ai-security entry to reflect 4 sources

## [2026-05-12] lint
- 154 pages total; 14 orphans found, 24 low-inbound (1 link)
- Fixed 6 critical orphans: added backlinks to wikilink-graph-extraction, context-engineering-anthropic, docker-sandboxes, error-budget-agentic, llm-as-judge, opencode-model-switching-reddit
- Updated concepts/ai-specific-pitfalls: added test fabrication, out-of-scope edits, rules file injection, CI/CD confused deputy from OWASP; linked to owasp-ai-security and owasp-security-checklist
- Remaining structural orphans (acceptable): patterns/algorithmic, patterns/backend, patterns/frontend (reference pages), summaries/awesome-software-architecture, summaries/cursor-cloud-agents, summaries/hn-junior-devs-and-ai, summaries/sparc-cursor-cline-rules
- Broken links (false positives): [[wikilinks]] and [[links]] in wikilink-graph-extraction are prose, not page refs; self-healing-cicd code block artifact — no action needed
- Source gaps: OWASP LLM Prompt Injection Prevention, OWASP MCP Security Cheat Sheet, OpenTelemetry for AI agents, OWASP Top 10 for LLMs not yet ingested

## [2026-05-12] ingest | OWASP LLM Prompt Injection Prevention + OWASP MCP Security
- Sources: LLM Prompt Injection Prevention + MCP Security (OWASP Cheat Sheet Series)
- Created summaries/owasp-prompt-injection: 9+ attack types (typoglycemia, Best-of-N 89% GPT-4o/78% Claude 3.5 via power-law scaling, multimodal steganography, RAG poisoning), 4-layer SecureLLMPipeline, dual-LLM pattern, model-based guardrails at 3 placements (input/output/action screening)
- Created summaries/owasp-mcp-security: 9 key risks, 12 best practices incl. SHA-256 tool hash pinning, ECDSA message signing + nonce/timestamp replay protection, mcp-scan, bind to 127.0.0.1, JSON Schema additionalProperties:false
- Updated concepts/indirect-prompt-injection: added LLM-Level Attack Techniques section (encoding/obfuscation, typoglycemia with Levenshtein defense note, Best-of-N with power-law caveat, multimodal injection, RAG poisoning); added dual-LLM pattern and model-based guardrails to Mitigations; added links to new summaries
- Updated summaries/owasp-ai-security: added cross-references to owasp-prompt-injection and owasp-mcp-security
- index.md: added owasp-prompt-injection and owasp-mcp-security entries; updated indirect-prompt-injection entry

## [2026-05-12] ingest | Git Worktrees for Parallel AI Agent Execution
- Sources: "How to Use Git Worktrees for Parallel AI Agent Execution.md" + "Parallel agents + git worktrees real-world experience?.md"
- Created summaries/worktrees-parallel-agents: 4 failure modes table, what worktrees fix vs don't fix (runtime isolation gap, logical conflicts), worktree-per-task vs per-agent heuristic (task duration / cache reuse), dependency handling strategies, git worktree lock, git rerere, sparse-checkout, Galactic (per-worktree IP), Block agent-task-queue, Switchman, Overstory, Intent 3-tier architecture
- Created concepts/shared-task-queue: filesystem inbox in main checkout accessible from any worktree via git-common-dir trick; atomic POSIX mv claim protocol; 3 startup layers (CLAUDE.md instruction / orchestrator pre-claim / claim-task skill); task file format; state machine (inbox→claimed→done with failure return); relation to Pocock/SandCastle planner model vs pull model
- Updated concepts/worktree-isolation: added per-task vs per-agent decision table, runtime isolation gap section (Galactic, Block agent-task-queue, composite Dagger Container-Use pattern), git worktree lock, git rerere, sparse-checkout; updated sources and date
- index.md: added worktrees-parallel-agents summary, shared-task-queue concept; updated worktree-isolation entry

## [2026-05-12] lint
- 158 pages total; 8 orphans, 29 low-inbound
- Acceptable orphans (unchanged from prior lint): patterns/algorithmic, patterns/backend, patterns/frontend, summaries/awesome-software-architecture, summaries/cursor-cloud-agents, summaries/hn-junior-devs-and-ai, summaries/sparc-cursor-cline-rules
- Fixed entities/docling (new orphan): added Related Pages section to summaries/docling linking back
- Fixed summaries/cc-agent-teams (1 inbound from dead-end): added to concepts/agent-teams Related Pages
- Stale claim: concepts/agent-teams + syntheses/agent-primitive-selection had no WORKTREE POOL branch; updated both to add worktree pool (>30 min or >5 tasks) as a fourth parallel primitive alongside agent teams
- Missing concept pages: OpenTelemetry for AI agents (3 raw sources uningested); no entity pages for Galactic or Switchman tools
- Source gaps: OpenTelemetry for AI Agents (3 sources), Cloudflare Workers/AI inference (2 sources)

## [2026-05-12] lint
- 151 unique basenames across 158 files (7 basename collisions discovered — first time flagged)
- Basename collisions (wikilink ambiguity): dspy (summary+entity), docling (summary+entity), opencode-dcp (summary+entity), cicd-testing (concept+summary), software-documentation (concept+summary), contextual-retrieval (concept+summary), llm-as-judge (concept+summary)
- True orphans (7): all acceptable carry-overs from prior lint — patterns/algorithmic, patterns/backend, patterns/frontend, summaries/awesome-software-architecture, summaries/cursor-cloud-agents, summaries/hn-junior-devs-and-ai, summaries/sparc-cursor-cline-rules
- 2nd-degree orphan (new): systems/ai-ml only linked from summaries/hn-junior-devs-and-ai (itself an orphan); fixed by adding link from summaries/autoresearch-karpathy
- Fixed concepts/dynamic-context-pruning (1 inbound from entity only): added link from concepts/context-compression Related Pages
- Fixed concepts/wikilink-graph-extraction (1 inbound): added link from summaries/agentic-search-vs-rag Related Pages
- Stale claim (unconfirmed — needs ingest): syntheses/agent-primitive-selection treats background execution as subagent flag; new CC docs (raw/ "1" variants) may define background agents as a distinct primitive via agent view UI
- Missing concept pages: OpenTelemetry/AI observability (3 raw sources uningested), entities/galactic, entities/switchman
- Source gaps: OpenTelemetry AI (3 sources in raw/), Cloudflare Workers AI inference (1 source in raw/), new CC docs — background agents/agent view (8 files in raw/)

## [2026-05-13] ingest | SpotMe — gym mode OpenCode plugin for deliberate practice

## [2026-05-13] ingest | LLM Eval Pipeline — 4 sources (Pragmatic Engineer, Hamel FAQ, tool selection, evals skills plugin)

Sources ingested: "A pragmatic guide to LLM evals for devs.md", "LLM Evals Everything You Need to Know.md", "Selecting The Right AI Evals Tool.md", "hamelsmuevals-skills...".
New summaries: pragmatic-engineer-llm-evals, hamel-evals-faq, selecting-ai-evals-tool, hamel-evals-skills.
New concept pages: llm-eval-pipeline, rag-evaluation.
## [2026-05-13] ingest | Gesture Navigation Best Practices + Mobile Design SKILL.md + Top 8 Claude Skills for UI/UX

## [2026-05-15] ingest | CC Linting & Debugging — r/ClaudeCode Community

Source: "ve been too afraid to ask, but... do we have linting and debugging in Claude Code? Be kind.md"
New summary: cc-linting-debugging-reddit.
Key insight captured: file-modifying linters must run in Stop hook (not PostToolUse) to avoid CC Edit file-state conflict.
Informed linting hook architecture: lint-on-write.sh (PostToolUse, read-only), lint-autofix.sh (Stop, biome --write), protect-lint-configs.sh (PreToolUse, blocks config edits).

## [2026-05-17] ingest | How to Avoid AI Code Slop + Clean Code in AI-Assisted Workflows

Sources: "How to Avoid AI Code Slop.md", "What Is Clean Code? A Guide to Principles and Best Practices.md"
New summaries: avoiding-ai-code-slop, clean-code-ai-assisted.
Updated concept: ai-specific-pitfalls — added over-engineering, defensive overreach, cargo-cult patterns (3 new failure modes from Aviator source).
Key new concepts: intent-driven verification (spec-first workflow), slop register (per-codebase AI failure pattern registry).

## [2026-05-19] ingest | Everything Claude Code (ECC)

Sources: "vietbui1999rueverything-claude-code The agent harness performance optimization system...md"
New summaries: summaries/everything-claude-code
New entities: entities/everything-claude-code, entities/agentshield
Updated concepts:
  - concepts/instinct-clustering — removed documented-not-adopted status; added ECC v2 as reference implementation (confidence scoring, /evolve, /prune, /learn-eval)
  - concepts/context-compression — added strategic compaction checkpoints; token optimization settings (MAX_THINKING_TOKENS, CLAUDE_AUTOCOMPACT_PCT_OVERRIDE, CLAUDE_CODE_SUBAGENT_MODEL)
  - concepts/context-window — added MCP server context cost section (claimed: 200K→~70K with too many MCPs; cap <10 servers, <80 tools)
Updated comparisons:
  - comparisons/cc-to-cross-platform-migration — updated hooks section with event counts (CC:8, OpenCode:20+, Cursor:15); added GitHub Copilot and Zed sections; DRY adapter pattern
Key new patterns: hook runtime controls (ECC_HOOK_PROFILE env var), context injection modes (dev/review/research), skill creator from git history, AgentShield 3-agent security pipeline
Note: component counts (60 agents, 232 skills, 102 rules) and impact numbers are claimed from ECC README — not independently verified.

## [2026-05-24] ingest | Simple Pi Subagents (YouTube — Amos Blomqvist)

Source: `raw/Simple Pi Subagents.md` (YouTube transcript + repo link)
Repo: https://github.com/amosblomqvist/pi-subagents

New summaries: summaries/pi-subagents-extension
Updated entities:
  - entities/pi-agent — added Pi Subagents Extension section; added source to frontmatter
Updated concepts:
  - concepts/agent-subagents — added Model Tiering for Subagent Types section (Haiku/Sonnet/Opus heuristic)
Updated index.md:
  - Added summaries/pi-subagents-extension entry
  - Updated entities/pi-agent entry description

Key patterns: proactive exploration offloading (delegate planning-phase file reads to cheap subagents before context bloat occurs); model tiering heuristic (mechanical/read-only→Haiku, reasoning/research→Sonnet, full capability→Sonnet/Opus); spawn depth limiting via frontmatter allowlist; per-subagent observability (nested tool call tree + cost metrics per agent).

## [2026-05-25] ingest | OpenCode Go + pi as Primary Coding Harness

Source: "Why You Should Try OpenCode Go and pi-coding-agent.md"
New summaries: summaries/opencode-go-pi-primary-harness
New entities: entities/opencode-go
Updated entities:
  - entities/pi-agent — corrected framing from "council layer only" to "primary coding agent + council"; added AGENTS.md confirmation; added difficulty-tiered model routing table; added pueue parallel delegation pattern; added srt sandboxing section; added OpenCode Go to related pages
Updated index.md:
  - Added summaries/opencode-go-pi-primary-harness
  - Updated entities/pi-agent description (primary harness framing)
  - Added entities/opencode-go

Key patterns captured:
- Subscription arbitrage: OpenCode Go ($10/mo) for bulk open-model tokens; Codex for high-reasoning tasks — similar cost to $100 plan
- Difficulty-tiered model routing in AGENTS.md: high/medium/low tiers with explicit fallback chains across providers
- pueue for background parallel agent delegation (persistent queue, log inspection, wait primitives)
- srt (Anthropic Sandbox Runtime) as standalone sandboxing tool for harnesses without built-in permission systems

Skipped (off-topic): "Code Smells.md", "Replace Magic Number with Symbolic Constant.md", "Too long..md"

## [2026-05-25] batch-ingest | OpenTelemetry cluster + Memory/Context + CC Teams + Skills + DSPy

Parallel ingest of 15 source files across 3 specialist agents. Delegate-pi skill created as harness artifact.

New pages:
- wiki/concepts/llm-observability.md — 8 OTel sources synthesized; GenAI semantic conventions, span types, metrics, multi-agent trace correlation, production tools
- wiki/entities/opentelemetry.md — OTel entity: three signals, incubating GenAI conventions, instrumentation approaches, Collector config
- wiki/summaries/cc-memory-context-docs.md — Anthropic memory cookbook: memory_20250818 + context editing API
- wiki/summaries/cc-agent-persistence.md — /goal command mechanics and evaluator internals
- wiki/summaries/opencode-plugins-overview.md — OpenCode plugin system: event surface, compaction hooks
- wiki/summaries/skills-first-principles-deep-dive.md — Skill meta-tool architecture: isMeta dual-message, three-tier loading, supply chain risk
- wiki/summaries/grill-skills-antipatterns.md — 9 failure modes for grill-me/grill-with-docs

Updated pages:
- wiki/concepts/agentic-memory-tool.md — canonical context editing config + semantic learning patterns
- wiki/summaries/cc-agent-teams.md — agent view UI, supervisor process, worktree isolation details
- wiki/concepts/agent-skills.md — composition patterns, grill-* antipatterns, when NOT to use skills
- wiki/entities/dspy.md — MIPROv2 internals, BetterTogether/Ensemble optimizers, pipeline patterns

Harness artifact:
- ~/.claude/skills/delegate-pi/SKILL.md — new skill wrapping pi subprocess delegation (council/delegate/subagent modes)

Key patterns captured:
- OTel GenAI semantic conventions still incubating — flag in all observability recommendations
- /goal command is distinct from /loop — condition-driven, not iteration-driven
- isMeta flag in SKILL.md enables dual-message execution (skill-as-meta-tool architecture)
- Grill-* antipatterns: 9 failure modes catalogued; high-fidelity vs low-fidelity question distinction key

## [2026-05-25] improvements | observe-session hook + slash-commands + otel-council + skill audit

Implementing harness improvements proposed after batch ingest.

New files:
- ~/.claude/hooks/observe-session.sh — PostToolUse hook; appends {ts, tool, session, ok} to ~/.claude/logs/session-YYYYMMDD.jsonl after every tool call
- wiki/concepts/slash-commands.md — decision guide for /goal vs /loop vs /ralph-structured vs /clear vs /compact vs /handoff
- wiki/systems/otel-council.md — OTel instrumentation spec for council.py; three span types; stdlib-only JSONL output; GenAI semantic conventions

Updated:
- ~/.claude/settings.json (via dotfiles) — added PostToolUse[".*"] hook entry for observe-session
- ~/.claude/skills/delegate-pi/SKILL.md — added allowed-tools: "Bash"

Skill audit findings:
- zoom-out: disable-model-invocation: true — vague description is intentional (user-only)
- No skills had overly broad allowed-tools violations
- delegate-pi was the only skill missing required allowed-tools declaration

Key decisions:
- isMeta is NOT a SKILL.md frontmatter field — it's an internal CC message flag; proposed "isMeta audit" was a misread of the skills deep dive; skipped
- memory-sync Stop hook deferred — memory_20250818 API too new; file-based approach still appropriate

## [2026-05-25] ingest | ONTO + TOON + Factory eval + SAC (autoencoding-free context compression)

Sources:
- raw/ONTO A Token-Efficient Columnar Notation for LLM Input Optimization.md
- raw/TOON vs. JSON Deconstructing the Token Economy of Data Serialization in Large Language Model….md
- raw/Evaluating Context Compression for AI Agents.md
- pdfs/17241_Autoencoding_Free_Contex.pdf (parsed via Docling)

New pages:
- wiki/concepts/llm-serialization-formats.md — ONTO/TOON schema-first formats; 40-60% token reduction; format comparison table; packaging vs distillation distinction
- wiki/summaries/factory-context-compression-eval.md — Factory.ai eval: anchored iterative summarization wins; probe-based eval methodology; 36K real coding-agent messages
- wiki/summaries/sac-context-compression.md — SAC: anchor tokens + bidirectional attention; no AE objective; 6.7-23.5% F1 gain at 15× compression; scales to 8B

Updated:
- wiki/concepts/context-compression.md — added Serialization Format section (orthogonal to compression strategies)

Key insights:
- ONTO/TOON are indie/research projects; benchmarks are synthetic — flag as unverified in production recommendations
- SAC eliminates autoencoding objective; AE and LM gradients are near-orthogonal (interference is the mechanism)
- Factory eval confirms anchored iterative summarization > opaque (OpenAI) > regenerative (Anthropic) on real coding sessions
- SAC is training-time infrastructure choice, not an operational tactic; distinct from ACON (test-time) and anchored summarization (runtime)

Comprehension check: skipped (user explicit)

## [2026-05-26] ingest | Copilot Agent Customization Structure (awesome-copilot-agents)
- Created: wiki/summaries/copilot-agent-structure.md
- Updated: wiki/summaries/ai-agent-technical-debt.md — added Copilot cloud agent specifics section
- Updated: index.md

## [2026-05-28] ingest | OpenCode Headless & Programmatic Interface (CLI.md + Server.md)

New pages:
- wiki/summaries/opencode-headless-api.md — `opencode run`, `opencode serve`, HTTP API, warm-server pattern, async/sync messages, SSE, ACP protocol, experimental orchestration flags

Updated:
- wiki/entities/opencode.md — added Headless & Programmatic Mode section; updated sources frontmatter
- index.md — added summary entry, updated opencode entity description

Key insights:
- `opencode run "prompt"` = headless subprocess mode (pi -p equivalent) — confirms Claude → OpenCode → Pi chain is viable
- Architecture is server-first: every opencode invocation embeds a server; TUI is just a client
- Warm-server pattern: `opencode serve` once, `opencode run --attach` for repeated calls — avoids MCP cold-boot
- HTTP API enables full programmatic control: create sessions, send sync/async prompts, fork sessions, respond to permissions, stream events via SSE
- `OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS` and `SCOUT` flags signal native parallel delegation coming

Comprehension check: skipped (user explicit)
