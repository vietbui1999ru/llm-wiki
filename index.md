# Wiki Index

Catalog of all pages. Updated on every ingest operation.

## Summaries
- [[summaries/nurture-first-agent-development]] — Zhang 2026 (arXiv 2603.10808): grow domain-expert agents via conversation instead of code/prompt; Knowledge Crystallization Cycle over a 3-layer memory architecture; single-user case study *(illustrative, not validated)*
- [[summaries/how-to-build-an-agent]] — Thorsten Ball (Amp): code-editing agent in ~300 lines Go via the Anthropic **native** tool-use API; LLM+loop+3 tools (read/list/edit); model chains tools unprompted
- [[summaries/coding-agent-200-lines]] — Mihai Eric: ~200-line Python coding agent using a **prompt-parsed** `tool: NAME({json})` protocol (no native tool API); twin of how-to-build-an-agent; flags an OpenAI-vs-Anthropic source contradiction
- [[summaries/ponytail]] — Ponytail repo: cross-agent minimality ladder for coding agents; YAGNI/stdlib/native/dependency/one-line before custom code; self-reported LOC/token/cost/time reductions
- [[summaries/compound-engineering]] — Every guide: ideate→brainstorm→plan→work→review→polish→compound loop; turns tasks into durable system improvements
- [[summaries/builderio-skills]] — Builder.io skills: visual-plan, visual-recap, agent-watchdog, plan-arbiter, efficient-frontier; artifact-first planning/review
- [[summaries/builderio-agent-native]] — Builder.io Agent-Native: shared action surface for UI, agent, HTTP, MCP, A2A, and CLI over one SQL-backed app state
- [[summaries/omp-oh-my-pi]] — omp (oh-my-pi): Pi fork by can1357; hashline editing, LSP/DAP wired in, 55k LoC Rust native core, 32 tools, 40+ providers, Hindsight memory, TTSR stream rules
- [[summaries/omp-plugins]] — omp plugin system: hooks, custom tools, skills, commands, MCP, themes; install from npm/git/local/marketplace; Claude-Code-compatible catalogs
- [[summaries/what-is-an-agent-harness-parallel-ai]] — Parallel AI explainer: orchestrator/framework/harness taxonomy, DeepAgents, ICML 2025 modular harness, model-agnostic property; supplements [[concepts/agent-harness]]
- [[summaries/pi-building-in-world-of-slop]] — Pi origin story: minimal harness thesis, 4-tool architecture, self-modifying extensions, Terminal Bench 6th, anti-slop philosophy (Mario Zechner talk)
- [[summaries/opencode-headless-api]] — `opencode run` (subprocess), `opencode serve` (HTTP API), warm-server pattern, sync/async messages, SSE events, programmatic permission approval
- [[concepts/github-issue-handoff]] *(stub)* — GitHub issue as handoff artifact; bridges /handoff + /to-issues + shared-task-queue; auto-dispatch via Actions webhook
- [[summaries/claude-code-plugins-llm-wiki]] — Plugin structure, manifest, skill-to-wiki mapping, symlink gotcha, launch commands
- [[summaries/llm-wiki-pattern]] — Summary of Karpathy's LLM wiki pattern: architecture, operations, tooling, Memex connection
- [[summaries/agentic-search-vs-rag]] — Experiment: graph/agentic search vs flat RAG; 99% fewer tokens, 2× IoU; RAG only wins on dependency recall; validates LightRAG for wiki
- [[summaries/local-rag-elasticsearch]] — Local RAG with Elasticsearch + LocalAI: retrieval 14ms, LLM dominates (16s); model size/speed trade-offs; stack patterns
- [[summaries/ai-agent-technical-debt]] — Using AI agents for systematic debt reduction: two modes, agentic safety model, Copilot cloud agent workflow, metrics
- [[summaries/copilot-agent-structure]] — Copilot customization taxonomy: 5 artifact types (instructions/prompts/agents/skills/MCPs), file placement in .github/, custom agents vs portable skills, repo setup
- [[summaries/amazon-scraping-2026]] — DIY vs. managed API for Amazon scraping; detection mechanisms, legal context, data available
- [[summaries/autoresearch-karpathy]] — Karpathy's autonomous ML experiment loop: agent modifies train.py, 5-min runs, val_bpb metric, program.md as control layer
- [[summaries/claude-usage-limits]] — Usage vs. length limits; 200K product context window vs 1M API; shared budget across all surfaces; tools/connectors token-expensive per request
- [[summaries/sparc-cursor-cline-rules]] — SPARC framework: 5 principles, 5 workflow phases, Memory Bank integration; mostly a structured AGENTS.md template
- [[summaries/claude-code-permissions-settings]] — CC settings schema: permissions.allow/ask/deny/defaultMode, bypassPermissions, sandbox.enabled (Bash-only), filesystem+network rules; corrects old allowedTools schema
- [[summaries/cursor-rules-background-agents]] — Cursor .cursor/rules, background agents, parity gaps vs CC
- [[summaries/cursor-cloud-agents]] — Cursor Cloud Agents: microVM isolation, GitHub/GitLab workflow, remote desktop control, cross-agent support
- [[summaries/cc-auto-mode]] — CC auto mode: 2-stage classifier, threat model, 17% FNR on overeager actions, deny-and-continue
- [[summaries/aws-security-agent]] — AWS managed pen test service: target/accessible/out-of-scope domain split, credential injection patterns, IAM role scoping, out-of-scope URL hierarchy, launch checklist
- [[summaries/hamel-evals-skills]] — Claude Code plugin (`hamelsmu/evals-skills`): 7 skills including eval-audit, write-judge-prompt, validate-evaluator, evaluate-rag
- [[summaries/cloudflare-agent-memory]] — Managed cross-session memory service: 5-channel RRF retrieval (FTS+key+HyDE+vector+message), 4-type taxonomy (Facts/Events/Instructions/Tasks), compaction-integrated ingest
- [[summaries/rlhf-cai]] — RLHF/RLAIF/Constitutional AI/DPO: alignment training techniques; 3-stage RLHF pipeline; DPO as reward-model-free alternative; inspiration for preference-feedback-loop
- [[summaries/self-refinement]] — Madaan et al. 2023: same-model iterative generate→critique→refine loop; no training required; self-evaluation bias limitation
- [[summaries/awesome-software-architecture]] — mehdihadeli curated list: topic taxonomy for software architecture (DDD, microservices, distributed patterns, design principles, messaging tools, DevOps); reference index, not prose
- [[summaries/hn-junior-devs-and-ai]] — HN community: AI amplifies existing ability; juniors lack evaluation frame; repetition/debugging gap; agentic tools harmful for beginners; 7 actionable heuristics
- [[summaries/cc-linting-debugging-reddit]] — r/ClaudeCode community: Stop hook for file-modifying linters (file-state conflict); PostToolUse read-only only; noslop quality gates; layered shellcheck/biome/pre-commit setup; gdb/Replay MCP/JetBrains debugger
- [[concepts/llm-serialization-formats]] — Schema-first formats (ONTO, TOON) cutting LLM input overhead 40–60% via schema-once design; covers format comparison, tradeoffs, and caveats on synthetic benchmarks

## Entities
- [[entities/rtk]] — Rust CLI proxy that filters/compresses command output before it hits LLM context; PreToolUse hook across 15 agents; 4 strategies (filter/group/truncate/dedup); 60-90% token savings *(claimed, unverified — self-reported estimates)*
- [[entities/context7]] — Live library doc fetching (MCP + ctx7 CLI); per-platform: CC/Opencode/Codex/Pi/OMP
- [[entities/ponytail]] — Cross-agent coding skill/plugin that reduces AI overbuild via a minimality ladder; adapters for Claude Code, Codex, OpenCode, Gemini, Pi, Copilot CLI, and more
- [[entities/agent-native]] — Builder.io framework for agent-native apps: shared actions, SQL-backed state, rich UI + agent surfaces, MCP/A2A compatibility
- [[entities/headroom]] — Context compression proxy/library/MCP for AI agents; ContentRouter (JSON/AST/prose), CacheAligner, CCR reversible compression, cross-agent memory, `headroom learn` failure mining
- [[entities/everything-claude-code]] — Agent harness performance system (ECC): plugin + manual install; 9-harness support; DRY adapter pattern; instinct clustering; AgentShield
- [[entities/agentshield]] — Security scanner for CC configs: 5 scan categories (secrets/permissions/hooks/MCP/agents), 102 rules, 3-agent Opus red-team pipeline
- [[entities/docling]] — IBM open-source document parser; PDF/DOCX/PPTX → structured Markdown/JSON for RAG; layout-aware, table-preserving, MCP-integrated
- [[entities/eggroll]] — Low-rank ES optimizer from Oxford; 100× GPU speedup over naïve ES; trains non-differentiable (int8) architectures; companion to EGG model
- [[entities/qmd]] *(stub)* — Local hybrid markdown search engine (BM25 + vector); CLI + MCP server
- [[entities/ai-coding-agents]] — The class of AI coding tools (Claude Code, Codex, OpenCode, etc.): capability spectrum, safety model, use cases
- [[entities/pydoll]] — Async Python CDP-native browser automation library with fingerprint evasion and WebRTC leak protection
- [[entities/firecrawl]] — Managed web scraping/crawling service for LLM consumption; 14-tool MCP server; vs. Pydoll/Playwright comparison
- [[entities/ketch]] — Stateless Go CLI unifying web search/scrape/crawl, OSS code search, and Context7 library docs behind one agent-facing binary; config-driven backend swap
- [[entities/sandcastle]] — Matt Pocock's TS lib for parallel agents in worktrees; branch strategy (head/merge-to-head/branch), token telemetry, provider abstraction
- [[entities/dangeresque]] — Host-native CLI orchestrator; mandatory adversarial reviewer + human-merge gate; ToS-compliant (no container for CC)
- [[entities/mnemory]] — Self-hosted MCP cross-session memory: Qdrant vector search + S3/MinIO artifact store; OSS alternative to Anthropic memory tool
- [[entities/agentops]] — Repo-native `.agents/` corpus + `/council` multi-vendor consensus CLI; cross-vendor coordination layer
- [[entities/gemini-cli]] — Google's Gemini CLI: GEMINI.md + TOML commands + activate_skill; high parity with CC; hooks + subagents (experimental)
- [[entities/opencode]] — Open-source Claude Code alternative; plugin system, compaction hooks, custom tools, headless `run`/`serve` modes, full HTTP API
- [[entities/omp]] — oh-my-pi: batteries-included Pi fork; hashline/LSP/DAP/TTSR/eval kernels/Hindsight memory/Snapcompact/32 tools/40+ providers; see [[comparisons/our-stack-vs-omp]] for gap analysis
- [[entities/pi-agent]] — pi-coding-agent CLI (pi-mono); primary harness for open-model workloads + council/adversarial review layer; difficulty-tiered model routing; pueue parallel delegation; srt sandboxing; Pi Subagents extension; specialization fallback ladder (specialized → adjacent → general → temp session agent); forked by [[entities/omp]]
- [[entities/commandr]] — L3 bus (thin waist) of the 5-layer toolchain; .agents/ filesystem contract; SPEC v0.3 (28/0 conformance); bin/ tools; CC + OpenCode adapters; council gate; annotation loop
- [[entities/diffviewer]] — L5 UI; real-time diff review (browser + Neovim); Pi extension (mid-turn blocking); mobile companion MVP-0 (Tailscale PWA + bus approval); CodeBoarding arch tab; Phase 5 target = Tauri
- [[entities/opencode-go]] — OpenCode Go: $10/mo open-model subscription (DeepSeek V4 Pro, Kimi K2.6, Qwen3.6, etc.); subscription arbitrage alternative to Anthropic/OpenAI plans
- [[entities/karpathy-llm-council]] — Karpathy's 3-stage council web app: parallel dispatch → anonymized peer review → Chairman synthesis; OpenRouter-based reference implementation
- [[entities/agents-md-format]] — AGENTS.md format entity: origin, per-tool implementations (Codex/OpenCode/CC/Aider/Gemini), multi-file strategies
- [[entities/codex]] — OpenAI Codex CLI; AGENTS.md + TOML agents + native skills (3-layer stack); CC migration mapping; hooks via config.toml
- [[entities/opencode-dcp]] — `@tarquinen/opencode-dcp` npm plugin; Compress + dedup + purge-errors; global/project config; /dcp commands
- [[entities/lean-session]] — OpenCode plugin; injects `.agents/` state into compaction; writes checkpoint on idle; 3 hooks: compacting/diff/idle
- [[entities/dspy]] — Stanford DSPy framework: Signatures/Modules, expanded optimizer table (MIPROv2 internals, BetterTogether, Ensemble), pipeline patterns, two-LM optimization setup, practical caveats on metric gaming
- [[entities/spotme]] — OpenCode "gym mode" plugin; counter-based exercise scaffolding; lite/medium/hard difficulty; portable SKILL.md for other harnesses
- [[entities/codegraphcontext]] — Python MCP server + CLI; indexes codebases into graph DB (KuzuDB); Tree-sitter parsing; 20 languages; relationship discovery, blast radius, dead code; session or daemon persistence
- [[entities/pentagi]] — OSS autonomous pen testing system (vxcontrol); 20+ tools in sandboxed Docker; orchestrator + researcher/developer/executor agents; pgvector + Neo4j memory; chain summarization for context; reference for our pentest-agent design
- [[entities/opentelemetry]] — CNCF-graduated vendor-neutral observability framework; three signals, GenAI semantic conventions (incubating), instrumentation approaches, Collector config, compatible backends for AI workloads
- [[entities/obsidian-cli]] — Official Obsidian CLI (v1.12.4+, free); requires app running; key=value + bare-word flags (flag-syntax contradiction flagged); 100+ commands across search/daily/tasks/properties/dev
- [[entities/obsidian-cli-rest-mcp]] — Community REST API + MCP plugin wrapping the CLI; 2-tool Code Mode (search/execute); StreamableHTTP, Bearer auth, dangerous-command gating
- [[entities/obsidian-claude-code-mcp]] *(stub)* — Community WebSocket MCP bridge for live Claude Code ↔ vault connection; alternative to REST/MCP and raw CLI

## Concepts
- [[concepts/lsp-agent-baseline]] — Language servers as lazy project-scoped baseline for coding agents; L2 capability, not L3 bus state; pairs with typecheck/tests/diff review
- [[concepts/compound-engineering]] — AI-native workflow principle: every task should leave durable knowledge, guardrails, or capabilities that make future work easier
- [[concepts/mobile-design-patterns]] — mobile-first doctrine, MFRI scoring, Fitts' Law, gesture design, iOS/Android divergence matrix, RN/Flutter performance patterns, release checklist
- [[concepts/unit-testing]] — AAA pattern, test doubles, naming convention, coverage philosophy, flaky test quarantine
- [[concepts/cicd-testing]] — Testing pyramid, 6 test types, shift-left, pipeline stage map, relationship to verification-pipeline
- [[concepts/context-window]] — Transformer constraint: O(n²) attention, KV cache, context rot, context awareness feature
- [[concepts/context-engineering]] — Discipline of curating minimal high-signal tokens: JIT retrieval, compaction, note-taking, sub-agents
- [[concepts/agentic-memory-tool]] — Anthropic beta API for file-based cross-session memory (memory_20250818) + in-session context editing (clear_tool_uses + clear_thinking); canonical config pattern, semantic learning, memory poisoning security
- [[concepts/software-documentation]] — Doc types (Diátaxis), audiences (including AI agents), principles, structure for doc-hosting platforms
- [[concepts/claude-code-plugins]] — Plugin structure, manifest format, namespacing, symlink gotcha, when to use plugins vs. personal config
- [[concepts/compounding-knowledge-base]] — Knowledge bases that accumulate compiled structure vs. RAG's per-query retrieval
- [[concepts/contextual-retrieval]] — RAG preprocessing technique: LLM-generated context prepended to chunks before embedding + BM25 indexing
- [[concepts/bm25]] — Lexical ranking function; exact-match complement to semantic embeddings in hybrid search
- [[concepts/reranking]] — Post-retrieval filtering: score top ~150 candidates, pass top 20 to LLM; stacks with contextual retrieval
- [[concepts/ai-code-review]] — Reviewing AI-generated code: automated + human layers, 8-point checklist, core risk of intent misalignment
- [[concepts/ai-specific-pitfalls]] — Failure modes unique to AI code: hallucinated APIs, slopsquatting, deleted tests, "looks right" logic errors, over-engineering mitigations
- [[concepts/agent-context-instructions]] — Standards documents that align agent output to team conventions before generation
- [[concepts/indirect-prompt-injection]] — Primary attack vector on AI agents: adversarial instructions in third-party content; dev-loop vectors; rules files as persistent steering; CI/CD confused deputy; MCP tool shadowing; typoglycemia; Best-of-N power-law scaling; RAG poisoning; dual-LLM pattern
- [[concepts/agentic-sandbox-controls]] — OS-level security controls for AI agents; Anthropic ToS constraint on CC in containers; host-native alternative
- [[concepts/web-fingerprinting]] — Multi-layer browser/network/behavioral fingerprinting used by anti-bot systems; evasion principles
- [[concepts/proxy-rotation]] — Proxy types by OSI layer, rotation strategies, limits vs. full fingerprinting evasion
- [[concepts/webrtc-ip-leak]] — WebRTC UDP bypass of proxy configuration; ICE/STUN mechanism and mitigations
- [[concepts/agent-harness]] — Model + harness = agent; core components: filesystem, bash, sandbox, context management, long-horizon loops; orchestrator/harness/framework distinction; model-agnostic property
- [[concepts/nurture-first-development]] — Grow domain-expert agents through conversation vs code-first/prompt-first build-then-deploy; 3-layer memory (Constitutional/Skill/Experiential) + Knowledge Crystallization Cycle + dual-workspace; theory behind this wiki's own memory system; *(proposed, single-source)*
- [[concepts/knowledge-crystallization-cycle]] — Four-phase mechanism (Immersion → Accumulation → Crystallization → Application) turning tagged conversational fragments into Skill Layer assets; maps our partial implementation (raw-log.md, synthesize-mistakes) against the full cycle; *(proposed, single-source — pending review, see `claude-setup/rules/nfd-knowledge-capture.md`)*
- [[concepts/ralph-loop]] — Harness pattern: intercept exit, reinjecting original prompt with clean context + durable filesystem state
- [[concepts/context-degradation]] — Five named failure modes: lost-in-middle, poisoning, distraction, confusion, clash; thresholds and mitigations
- [[concepts/context-compression]] — Five strategies + serialization format axis (ONTO/TOON 40–60% reduction); clear-over-compact consensus; KV-cache cost trap; SAC as learned soft compression alternative
- [[concepts/tool-design-for-agents]] — Dual audience principle; error messages as agent recovery instructions; naming conventions
- [[concepts/agent-skills]] — Skill meta-tool: SKILL.md schema, three-tier loading, isMeta dual-message execution, supply chain risk, composition patterns, grill-* antipatterns, when NOT to use skills
- [[concepts/agent-subagents]] — Subagents: own context window, YAML frontmatter format, all fields, scopes, invocation patterns, fork mode
- [[concepts/agent-teams]] — Agent teams: lead+teammates+task list+mailbox; when to use vs subagents; quality gate hooks; best practices
- [[concepts/model-tier-routing]] — Haiku/Sonnet/Opus selection table; escalate/downgrade criteria; explicit `model` param on spawns; tier→subagent_type mapping; missing-model fallback (same-provider closest-tier before cross-provider); authoritative pull target for the routing rule
- [[concepts/model-task-routing]] — OpenCode Go concrete model ID → task mapping; per-model profiles (DeepSeek V4 Pro/Flash, Kimi K2.6); thinking budget suffixes; benchmark tracking table; Go fallback chain
- [[concepts/worker-coordination]] — Partial result passing between parallel workers: contract-first, pipeline, filesystem blackboard, actor mailbox; decision table; failure modes
- [[concepts/wikilink-graph-extraction]] — Reducing LightRAG indexing cost by injecting Obsidian wikilink structure as extraction hints; ~40-55% token reduction; chunking_func hook; future direct graph injection path
- [[concepts/verification-pipeline]] — Four-tier quality ladder: typecheck → visual verification → screenshot gate → design critique; origin failures; protocol rules
- [[concepts/owasp-security-checklist]] — OWASP Top 10 checklist + AI-specific extensions: tool least-privilege, memory security, DoW, slopsquatting, test fabrication, CI/CD confused deputy, rules file injection; severity classification table
- [[concepts/pentest-agent-design]] — Blueprint for Next.js + ECS Fargate + Neon pen test agent: supervisor + recon/web/db specialists, two-phase (black-box HTTP + gray-box AWS), safety constraints (scope lock, rate cap, read-only), findings.json + report.md output, wiki ingest pipeline
- [[concepts/domain-glossary]] — CONTEXT.md pattern: shared language between dev and agent; token efficiency, consistent naming, reduced context distraction
- [[concepts/deep-modules]] — Ousterhout's deep vs shallow modules; narrow interface, wide implementation; test boundary design; why AI produces shallow codebases by default
- [[concepts/evolution-strategies]] — Black-box optimization via parameter perturbation; ES vs RL trade-offs; shared random seed trick; progression from gaming (2017) to LLM fine-tuning (2025)
- [[concepts/multi-vendor-adversarial-review]] — Using different model/vendor to review agent work; catches single-model blind spots; same-tier vs cross-vendor vs /council
- [[concepts/branch-strategy-for-agents]] — head vs merge-to-head vs branch; when to use each; relation to worktrees and human-merge gates
- [[concepts/agent-self-correction]] — wiki-as-runtime-oracle; deviation trigger table; qmd queries for re-alignment; zero startup overhead
- [[concepts/instinct-clustering]] — behavioral pattern mining from tool-call telemetry; observe→cluster→inject pipeline; homunculus pattern; ECC v2 is the reference implementation (confidence scoring, /evolve, /prune)
- [[concepts/dynamic-context-pruning]] — mid-session context reduction via Compress tool (model-driven) + deduplication + purge-errors; complements compaction; `@tarquinen/opencode-dcp`
- [[concepts/council-pattern]] — 3-stage multi-model deliberation: parallel dispatch → optional anonymized peer review → Chairman or human synthesis; Stage 2 optional; cost model; when to use
- [[concepts/worktree-isolation]] — git worktrees for agent filesystem isolation; ToS-compliant sandboxing alternative; scope overlap, merge-before-cleanup; runtime isolation gap (ports); worktree-per-task vs per-agent; git worktree lock, rerere, sparse-checkout
- [[concepts/shared-task-queue]] — filesystem inbox in main checkout; atomic claim via POSIX mv; git-common-dir trick to find inbox from any worktree; 3 startup layers (CLAUDE.md/orchestrator/skill); pull vs push model
- [[concepts/rules-vs-hooks]] — static rules files vs. dynamic hook injection; compliance problem; hybrid patterns; when to use each
- [[concepts/memory-bank-pattern]] — Josh Wand's `_memory/` hierarchy for cross-session persistence; repomix compile; yak-shaving tracking; mode-based workflow
- [[concepts/self-healing-loop]] — failure→bounded retry→rollback→escalation; failure signature detection; guardrails; composes with ralph-loop; Dagger/ArgoCD/Windmill implementations
- [[concepts/agentic-cicd]] — CI as external watchdog when agent IS the developer; gate sequence; staging-first; diff size cap; builder/deployer network split
- [[concepts/error-budget]] — SRE error budget adapted to agent loops; retry/token/runtime/session budget axes; progress score; no-progress detection
- [[concepts/llm-as-judge]] — LLM evaluates another LLM's output via structured prompt; pairwise vs direct scoring vs G-Eval; failure modes (self-bias, reward hacking, sycophancy); relation to RLHF
- [[concepts/llm-eval-pipeline]] — Continuous quality system for LLM products: error analysis flywheel, golden/eval/regression datasets, code assertion vs LLM-judge split, CI gates, production monitoring, guardrails vs evaluators
- [[concepts/rag-evaluation]] — RAG eval split: retrieval (Recall@k, Precision@k, MRR, nDCG) vs generation (faithfulness, answer relevance, context utilization); Ragas/DeepEval; Jason Liu 6-RAG-evals framework
- [[concepts/preference-feedback-loop]] — cross-vendor judge evaluates agent outputs on 4-dimension rubric; pattern-triggered rule extraction; human approval gate; extends mistakes/ + memory/feedback_*
- [[concepts/actor-model]] — actors as unit of concurrency; 3 primitives (send/spawn/become); mailbox semantics; no shared state; supervision trees + let-it-crash; virtual actor model (Orleans grains/silos); Erlang/Akka/Orleans/ProtoActor implementations
- [[concepts/llm-observability]] — Observability patterns for LLM and agent systems: OpenTelemetry GenAI semantic conventions (incubating), span types, metrics, sampling, multi-agent trace correlation, production monitoring tools
- [[concepts/slash-commands]] — Decision guide for Claude Code session commands: when to use /goal, /loop, /ralph-structured, /clear, /compact, /save-session, /handoff, and how they differ
- [[concepts/linux-setup-guide]] — Authoritative step-by-step guide for bootstrapping the full AI workflow on a fresh Linux machine; AI-executable; covers dotfiles, Claude Code, plugins, wiki toolchain, LightRAG index
- [[concepts/cli-driven-vault-automation]] — Wrapper-script + cron patterns over the Obsidian CLI; doctor/health-check convention, "Obsidian must be running" guard, small-stable-verb-set instinct shared with MCP Code Mode

## Patterns
- [[patterns/principles]] — SOLID (SRP/OCP/LSP/ISP/DIP), DRY, YAGNI, KISS, Law of Demeter, SoC, composition over inheritance; per-principle violation patterns and decision table
- [[patterns/code-quality]] — naming conventions, function discipline (size/SRP/params/abstraction), cognitive complexity, comment discipline, magic numbers, code smell taxonomy (structural + AI-specific)
- [[patterns/design-patterns-creational]] — All 5 GoF creational patterns: Factory Method, Abstract Factory, Builder, Prototype, Singleton; intent, triggers, anti-patterns, TypeScript sketches, comparison table
- [[patterns/design-patterns-structural]] — All 7 GoF structural patterns: Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy; intent, triggers, TypeScript sketches, anti-patterns, Adapter/Facade/Proxy confusion table
- [[patterns/design-patterns-behavioral]] — All 10 GoF behavioral patterns + Domain Event: intent, when to use/not, TypeScript sketch, anti-patterns, confusion table for Observer/Mediator, Strategy/State, Command/CoR
- [[patterns/refactoring]] — 13 Fowler-style techniques: Extract Method/Variable, Inline, Move, Replace Temp with Query, Introduce Parameter Object, Replace Conditional with Polymorphism, Decompose Conditional, Magic Number → Constant, Error Code → Exception, Pull Up/Push Down, Extract/Inline Class; each with trigger, before/after snippet, anti-patterns
- [[patterns/algorithmic]] — 15 pattern families: sliding window, two pointers, fast/slow pointers, binary search, merge intervals, BFS, DFS, backtracking, DP (memo vs tabulation), greedy, topological sort, union-find, top-K heap, modified binary search, monotonic stack/queue; each with problem shape, recognition trigger, complexity, template
- [[patterns/api-design]] — Resource-oriented URL design, HTTP method semantics, field masks, structured error bodies, URL vs header versioning, cursor/offset pagination, idempotency keys, long-running operations (LRO), and API anti-pattern table
- [[patterns/error-handling]] — error taxonomy (expected/unexpected, recoverable/fatal, business/technical); fail-fast; exceptions vs Result types; railway-oriented programming; error propagation and rethrow discipline; exponential backoff with jitter; API error response design; logging discipline; anti-pattern table
- [[patterns/frontend]] — React component patterns (custom hooks, container/presentational, compound components, headless, HOC, render props, provider, portals, atomic design); state management decision table (local/lifted/server/global); rendering strategies (CSR/SSR/SSG/ISR); performance (memo/lazy/virtualization); CSS architecture (BEM/CSS Modules/Tailwind/CSS-in-JS)
- [[patterns/backend]] — middleware chain composition order, JWT vs session auth, RBAC vs ABAC enforcement placement, service layer / repository pattern, queue/worker at-least-once delivery + DLQ, DI anti-patterns, API gateway, backend anti-pattern taxonomy
- [[patterns/concurrency]] — thread safety fundamentals, synchronization primitives (mutex/semaphore/RWLock/atomic), memory models, race condition detection/prevention, deadlock patterns, async/await pitfalls, actor model, CSP, parallel algorithm patterns (map-reduce/fork-join/thread-pool/producer-consumer), backpressure
- [[patterns/database]] — indexing strategies (B-tree/hash/composite/covering/bitmap/filtered/full-text); EXPLAIN / query plan reading; N+1 detection and fix; connection pooling parameters and modes; ACID, isolation levels, optimistic vs pessimistic locking; read/write splitting; when to denormalize

## Systems
- [[systems/distributed-systems]] — CAP theorem (CP vs AP), eventual consistency conflict resolution, idempotency patterns, circuit breaker, backpressure strategies, saga (choreography vs orchestration), 2PC avoidance, distributed locks + fencing tokens
- [[systems/architectural-patterns]] — monolith vs microservices (decision criteria), event-driven architecture, CQRS (when warranted + AWS reference), event sourcing, hexagonal architecture, layered architecture, modular monolith, vertical slice architecture, strangler fig migration
- [[systems/system-design-process]] — requirements clarification framework (functional/non-functional), capacity estimation (QPS/storage/bandwidth), component decomposition, data flow mapping, API contract-first, tradeoff articulation, common design mistakes
- [[systems/scalability-reliability]] — caching strategies (cache-aside/write-through/write-behind; layer placement; invalidation), database sharding (shard key selection, failure modes), rate limiting algorithms (token bucket/leaky bucket/sliding window), load balancing (L4 vs L7, sticky sessions), observability (RED/USE methods, structured logs, distributed tracing), SLO/SLA/availability numbers
- [[systems/data-modeling]] — relational/document/wide-column/graph/time-series decision criteria, normalization (1NF-3NF) vs denormalization (when to break rules), schema evolution (expand-contract, versioned events), event sourcing as data model, polyglot persistence tradeoffs, access-pattern-driven design
- [[systems/ai-ml]] — 9-step ML system design process, metrics (offline/online, counter metrics), data labeling strategies, feature stores (training-serving consistency), model selection heuristic, batch vs real-time serving, edge inference (quantization/pruning/distillation), A/B/shadow/canary deployment, monitoring (covariate vs concept drift); AI agent patterns → wiki/concepts/
- [[systems/otel-council]] — OTel instrumentation for council.py: three span types (session/voice/chairman), zero-dependency JSONL file output, GenAI semantic convention attributes, jq trace queries

## Comparisons
- [[comparisons/our-stack-vs-omp]] — Feature gap: Claude Code + Pi + MCP stack vs omp; hard gaps (hashline/LSP/DAP/TTSR); our wins (wiki/skills/council); ~55% parity
- [[comparisons/spec-driven-frameworks-vs-native]] — Heavy frameworks vs lean skills vs vanilla vs custom harness; community consensus; discrepancies with prior wiki
- [[comparisons/claude-code-vs-opencode-plugins]] — Hook surface, compaction control, custom tools; OpenCode's compaction hook as key differentiator
- [[comparisons/cc-to-cross-platform-migration]] — Full migration matrix: CC rules/skills/subagents/hooks/plugins → Gemini/OpenCode/Codex/Cursor/Copilot/Zed; parity rating per layer; hook event counts; DRY adapter pattern

## Syntheses
- [[syntheses/minimal-coding-agent]] — Cross-source thesis from Ball (Go) + Eric (Python): the coding-agent core is LLM+loop+3 tools with no secret; the one real axis is native-API vs prompt-parsed tool protocol (two layers of one idea); leverage lives in the surrounding "elbow grease"
- [[syntheses/builderio-control-plane-integration]] — Concrete Builder.io integration plan for Commandr + DiffViewer: shared action vocabulary, visual plan/recap artifacts, SPEC-safe bus mapping, Mermaid workflows, implementation slices
- [[syntheses/neovim-ai-operator-workflow]] — Neovim as human operator cockpit for AI agents: Mason LSP/DAP lane, diffview auto-refresh, selection context, CodeCompanion/Avante/MCPHub/claudecode.nvim roles
- [[syntheses/pi-orchestration-architecture]] — Pueue-dispatched pi workers, diff-review gate, status artifact, retry limit, two-mode review (interactive vs headless), human-commits-last
- [[syntheses/agent-primitive-selection]] — Decision tree for skill vs subagent vs team; model tier routing; multi-vendor adversarial review pattern
- [[syntheses/lean-agentic-workflow]] — Full stack: grill→PRD→slices→AFK→verify; council, dangeresque, lean-session plugin, model routing, failure modes
- [[syntheses/local-rag-wiki]] — two-path RAG stack: qmd (BM25+vector, Claude Code) + LightRAG graph (wiki-chat TUI + wiki-mcp MCP); qwen2.5:3b local or Haiku hybrid; manifest-based incremental indexing; post-commit automation
- [[syntheses/control-plane-expansion-plan]] — Gap analysis and bootstrap path: cockpit action registry, agent-control skills, commandr-omp-runner; Phase 0.5–3 roadmap
- [[syntheses/desktop-control-plane]] — *(local-only)* Big-picture synthesis: 5-layer toolchain (Commandr bus + DiffViewer/Tauri UI + omp workers + SKILL.md packages); Mermaid architecture/workflow diagrams; action registry; evidence-first cockpit vision
- [[syntheses/agent-diff-viewer]] *(partially-superseded)* — Localhost real-time diff viewer for Claude Code: original design; see [[entities/diffviewer]] for current state

## Project Tools
- `pi-headroom/` — Headroom context compression plugin for omp (tool_result hook + headroom_retrieve custom tool); tested on omp v16.0.9; complementary to snapcompact
- `commandr-omp-runner/` — L2 runner wrapper: bootstrap (`setup.sh`) + runner (`runner.sh`) with runner-agnostic interface; scaffold/smoke only; RPC host tools path for Level 2+
  - `HOST-TOOLS.md` — Host tool schema for Commandr bus integration: progress, artifacts, approvals, complete/fail; policy table; runner-agnostic interface

## Research
- [[research/omp-snapcompact-rpc]] — Deep dive: snapcompact tool-result truncation defaults, RPC mode protocol, host tools as polyglot bus bridge
