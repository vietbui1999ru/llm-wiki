# Wiki Index

Catalog of all pages. Updated on every ingest operation.

## Summaries
- [[summaries/mattpocockskills]] — Matt Pocock's engineering skills: 4 failure modes, 9 skills (grill-me, grill-with-docs, tdd, diagnose, zoom-out, to-prd, to-issues, improve-architecture, setup)
- [[summaries/mattpocockworkflow]] — Full AI coding workflow: grill→PRD→kanban DAG→AFK loop; smart zone; clear-over-compact; deep modules; push/pull standards; SandCastle parallelization
- [[summaries/firecrawl-mcp-server]] — Firecrawl MCP: 14 tools for web scraping/crawling/search/extraction/browser automation for AI agents
- [[summaries/superpowers-plugin]] — Superpowers v5.0.7: zero-dependency workflow plugin; Iron Law TDD/debugging; skill-first discipline; subagent execution
- [[summaries/unit-testing-best-practices]] — 2 sources: 15 practices (naming, AAA, mocks, flaky tests, coverage philosophy), IBM fundamentals
- [[summaries/cicd-testing]] — testing pyramid, 6 test types, pipeline stage map, shift-left, continuous testing
- [[summaries/context-window-cluster]] — 5 sources: context window fundamentals, context engineering, 6 management techniques, memory tool API
- [[summaries/software-documentation]] — 2 sources: principles (clear/concise/structured), doc types, README template, organization
- [[summaries/claude-code-plugins-llm-wiki]] — Plugin structure, manifest, skill-to-wiki mapping, symlink gotcha, launch commands
- [[summaries/wshobson-agent-orchestration]] — wshobson/agents: 184 agents, 78 plugins, 150 skills; three-tier Opus/Sonnet/Haiku model routing; PluginEval framework
- [[summaries/exit-code-0-quality]] — 198 agents, 30 campaigns: four-tier verification pipeline, campaign persistence, parallel worktree isolation, five protocol rules from failures
- [[summaries/automated-security-reviews]] — Claude Code /security-review command + GitHub Actions; built-in, no custom agent needed
- [[summaries/llm-wiki-pattern]] — Summary of Karpathy's LLM wiki pattern: architecture, operations, tooling, Memex connection
- [[summaries/contextual-retrieval]] — Anthropic's Contextual Retrieval: chunk context prepending reduces RAG retrieval failure by 49–67%
- [[summaries/agentic-sandbox-security]] — NVIDIA AI Red Team: mandatory OS-level sandbox controls for AI coding agents; indirect prompt injection as primary threat
- [[summaries/ai-agent-technical-debt]] — Using AI agents for systematic debt reduction: two modes, agentic safety model, metrics
- [[summaries/ai-code-vetting-practices]] — Condensed checklist for vetting AI-generated code: static analysis → readability → security → tests
- [[summaries/optimized-review-process-with-agents]] — Automated review pipeline with AI agents: context instructions, security autofix, human role
- [[summaries/reviewing-ai-generated-code]] — 8-step process for reviewing AI-generated code; AI-specific pitfalls and self-reviewing agent pattern
- [[summaries/anti-bot-evasion-tactics]] — Community techniques for bypassing anti-bot systems: fingerprinting layers, Cloudflare, proxy rotation, free vs. hybrid stacks
- [[summaries/amazon-scraping-2026]] — DIY vs. managed API for Amazon scraping; detection mechanisms, legal context, data available
- [[summaries/pydoll-network-fingerprinting]] — Pydoll deep-dive: OSI layers, TCP/TLS fingerprinting, WebRTC leaks, GDPR/CFAA legal framework
- [[summaries/agent-harness-engineering]] — LangChain harness anatomy + OpenAI 5-month Codex case study: harness components, repo-as-record, mechanical enforcement
- [[summaries/autoresearch-karpathy]] — Karpathy's autonomous ML experiment loop: agent modifies train.py, 5-min runs, val_bpb metric, program.md as control layer
- [[summaries/docling]] — 3 sources: Docling document parser for AI; why parsing quality matters for RAG; layout-aware PDF → Markdown; vs Firecrawl; research paper pipeline
- [[summaries/openai-es-2017]] — OpenAI 2017: ES as scalable RL alternative; shared random seed trick; linear worker scaling; solved MuJoCo humanoid in 10 min
- [[summaries/es-llm-finetuning-2025]] — Cognizant+MIT 2025: first billion-param ES LLM fine-tuning; pop size 30; outperforms GRPO/PPO on Countdown; no reward hacking
- [[summaries/eggroll-2025]] — Oxford 2025: EGGROLL low-rank perturbations; 100× GPU speedup; 91% batch inference throughput; trains integer quantized models
- [[summaries/claude-usage-limits]] — Usage vs. length limits; 200K product context window vs 1M API; shared budget across all surfaces; tools/connectors token-expensive per request
- [[summaries/spec-driven-frameworks-reddit]] — r/ClaudeCode community synthesis: frameworks vs native CC; Dangeresque/SandCastle/Mnemory/AgentOps; clear-over-compact as consensus; OpenCode plugins
- [[summaries/opencode-model-switching-reddit]] — r/opencodeCLI community: harness > model; GLM-5.1 > Kimi K2.6; DeepSeek Flash max reasoning unlock; multi-model pipeline patterns
- [[summaries/agents-md-spec]] — AGENTS.md format spec: 60k+ projects, Linux Foundation steward, nested precedence, cross-tool compatibility table
- [[summaries/codex-agents-md]] — Codex layering: global→CWD walk, AGENTS.override.md, 32 KiB limit, profile via CODEX_HOME
- [[summaries/agents-md-critique]] — Critique of AGENTS.md: single-file abstraction wrong, compliance unenforceable, content too shallow; hooks + Memory Bank as alternatives
- [[summaries/sparc-cursor-cline-rules]] — SPARC framework: 5 principles, 5 workflow phases, Memory Bank integration; mostly a structured AGENTS.md template
- [[summaries/opencode-dcp]] — OpenCode DCP plugin: Compress (model-driven, range/message modes) + deduplication + purge-errors; ~85% cache hit vs 90% without; /dcp commands
- [[summaries/claude-code-permissions-settings]] — CC settings schema: permissions.allow/ask/deny/defaultMode, bypassPermissions, sandbox.enabled (Bash-only), filesystem+network rules; corrects old allowedTools schema
- [[summaries/self-healing-cicd-implementations]] — Dagger (AI diagnose→patch→validate), ArgoCD (revision-based rollback), Windmill (per-step retry + exponential backoff)
- [[summaries/error-budget-agentic]] — SRE error budget origin; agentic adaptation: retry/token/runtime/session budgets; progress score; rollback as first-class pattern
- [[summaries/gemini-cli-rules]] — GEMINI.md: global/workspace/JIT discovery, @file.md imports, TOML commands, CC migration mapping
- [[summaries/opencode-commands-agents]] — OpenCode commands (.opencode/commands/*.md), rules array, agents JSON config, command→agent binding
- [[summaries/codex-agents-skills]] — Codex TOML agents (.codex/agents/*.toml), native skills (agents/openai.yaml), 3-layer stack, CC migration mapping
- [[summaries/cursor-rules-background-agents]] — Cursor .cursor/rules, background agents, parity gaps vs CC
- [[summaries/cursor-cloud-agents]] — Cursor Cloud Agents: microVM isolation, GitHub/GitLab workflow, remote desktop control, cross-agent support
- [[summaries/cc-auto-mode]] — CC auto mode: 2-stage classifier, threat model, 17% FNR on overeager actions, deny-and-continue
- [[summaries/cc-agent-teams]] — CC agent teams (experimental): shared task list, teammate direct messaging, TeammateIdle/TaskCompleted hooks
- [[summaries/context-engineering-anthropic]] — Anthropic context engineering: JIT retrieval, compaction, note-taking, sub-agents; context editing API
- [[summaries/docker-sandboxes]] — Docker Sandboxes: microVM isolation for coding agents; Docker-in-Docker safe; CC/Codex/Gemini/Copilot/Kiro support
- [[summaries/llm-as-judge]] — 3 sources: LLM-as-judge evaluation pattern; pairwise vs direct scoring; G-Eval chain-of-thought; production monitoring incident; best practices and limitations
- [[summaries/cloudflare-agent-memory]] — Managed cross-session memory service: 5-channel RRF retrieval (FTS+key+HyDE+vector+message), 4-type taxonomy (Facts/Events/Instructions/Tasks), compaction-integrated ingest
- [[summaries/rlhf-cai]] — RLHF/RLAIF/Constitutional AI/DPO: alignment training techniques; 3-stage RLHF pipeline; DPO as reward-model-free alternative; inspiration for preference-feedback-loop
- [[summaries/self-refinement]] — Madaan et al. 2023: same-model iterative generate→critique→refine loop; no training required; self-evaluation bias limitation
- [[summaries/dspy]] — DSPy signatures/modules/optimizers stack; GEPA error-driven prompt augmentation; when to use vs plain prompting; limitations

## Entities
- [[entities/docling]] — IBM open-source document parser; PDF/DOCX/PPTX → structured Markdown/JSON for RAG; layout-aware, table-preserving, MCP-integrated
- [[entities/eggroll]] — Low-rank ES optimizer from Oxford; 100× GPU speedup over naïve ES; trains non-differentiable (int8) architectures; companion to EGG model
- [[entities/qmd]] *(stub)* — Local hybrid markdown search engine (BM25 + vector); CLI + MCP server
- [[entities/ai-coding-agents]] — The class of AI coding tools (Claude Code, Codex, OpenCode, etc.): capability spectrum, safety model, use cases
- [[entities/pydoll]] — Async Python CDP-native browser automation library with fingerprint evasion and WebRTC leak protection
- [[entities/firecrawl]] — Managed web scraping/crawling service for LLM consumption; 14-tool MCP server; vs. Pydoll/Playwright comparison
- [[entities/sandcastle]] — Matt Pocock's TS lib for parallel agents in worktrees; branch strategy (head/merge-to-head/branch), token telemetry, provider abstraction
- [[entities/dangeresque]] — Host-native CLI orchestrator; mandatory adversarial reviewer + human-merge gate; ToS-compliant (no container for CC)
- [[entities/mnemory]] — Self-hosted MCP cross-session memory: Qdrant vector search + S3/MinIO artifact store; OSS alternative to Anthropic memory tool
- [[entities/agentops]] — Repo-native `.agents/` corpus + `/council` multi-vendor consensus CLI; cross-vendor coordination layer
- [[entities/gemini-cli]] — Google's Gemini CLI: GEMINI.md + TOML commands + activate_skill; high parity with CC; hooks + subagents (experimental)
- [[entities/opencode]] — Open-source Claude Code alternative; plugin system with compaction hooks, custom tools, 30+ event surface
- [[entities/pi-agent]] — TypeScript unified multi-provider LLM API (pi-mono); council/adversarial review layer; GitHub Copilot Models integration
- [[entities/karpathy-llm-council]] — Karpathy's 3-stage council web app: parallel dispatch → anonymized peer review → Chairman synthesis; OpenRouter-based reference implementation
- [[entities/agents-md-format]] — AGENTS.md format entity: origin, per-tool implementations (Codex/OpenCode/CC/Aider/Gemini), multi-file strategies
- [[entities/codex]] *(stub)* — OpenAI Codex CLI; pioneered AGENTS.md format; AGENTS.override.md layering; 32 KiB chain limit
- [[entities/opencode-dcp]] — `@tarquinen/opencode-dcp` npm plugin; Compress + dedup + purge-errors; global/project config; /dcp commands
- [[entities/lean-session]] — OpenCode plugin; injects `.agents/` state into compaction; writes checkpoint on idle; 3 hooks: compacting/diff/idle
- [[entities/dspy]] — Stanford framework for programming LMs via Signatures/Modules/Optimizers; GEPA optimizer: error-driven prompt refinement; automated prompt optimization without manual prompt engineering

## Concepts
- [[concepts/unit-testing]] — AAA pattern, test doubles, naming convention, coverage philosophy, flaky test quarantine
- [[concepts/cicd-testing]] — Testing pyramid, 6 test types, shift-left, pipeline stage map, relationship to verification-pipeline
- [[concepts/context-window]] — Transformer constraint: O(n²) attention, KV cache, context rot, context awareness feature
- [[concepts/context-engineering]] — Discipline of curating minimal high-signal tokens: JIT retrieval, compaction, note-taking, sub-agents
- [[concepts/agentic-memory-tool]] — memory_20250818 API, context editing, cross-session learning, memory poisoning security; Mnemory as OSS parallel
- [[concepts/software-documentation]] — Doc types, audiences, principles, structure for doc-hosting platforms
- [[concepts/claude-code-plugins]] — Plugin structure, manifest format, namespacing, symlink gotcha, when to use plugins vs. personal config
- [[concepts/compounding-knowledge-base]] — Knowledge bases that accumulate compiled structure vs. RAG's per-query retrieval
- [[concepts/contextual-retrieval]] — RAG preprocessing technique: LLM-generated context prepended to chunks before embedding + BM25 indexing
- [[concepts/bm25]] — Lexical ranking function; exact-match complement to semantic embeddings in hybrid search
- [[concepts/reranking]] — Post-retrieval filtering: score top ~150 candidates, pass top 20 to LLM; stacks with contextual retrieval
- [[concepts/ai-code-review]] — Reviewing AI-generated code: automated + human layers, 8-point checklist, core risk of intent misalignment
- [[concepts/ai-specific-pitfalls]] — Failure modes unique to AI code: hallucinated APIs, slopsquatting, deleted tests, "looks right" logic errors
- [[concepts/agent-context-instructions]] — Standards documents that align agent output to team conventions before generation
- [[concepts/indirect-prompt-injection]] — Primary attack vector on AI agents: adversarial instructions embedded in third-party content the agent reads
- [[concepts/agentic-sandbox-controls]] — OS-level security controls for AI agents; Anthropic ToS constraint on CC in containers; host-native alternative
- [[concepts/web-fingerprinting]] — Multi-layer browser/network/behavioral fingerprinting used by anti-bot systems; evasion principles
- [[concepts/proxy-rotation]] — Proxy types by OSI layer, rotation strategies, limits vs. full fingerprinting evasion
- [[concepts/webrtc-ip-leak]] — WebRTC UDP bypass of proxy configuration; ICE/STUN mechanism and mitigations
- [[concepts/agent-harness]] — Model + harness = agent; core components: filesystem, bash, sandbox, context management, long-horizon loops
- [[concepts/ralph-loop]] — Harness pattern: intercept exit, reinjecting original prompt with clean context + durable filesystem state
- [[concepts/context-degradation]] — Five named failure modes: lost-in-middle, poisoning, distraction, confusion, clash; thresholds and mitigations
- [[concepts/context-compression]] — Three strategies; clear-over-compact now community consensus for coding; OpenCode compaction hooks
- [[concepts/tool-design-for-agents]] — Dual audience principle; error messages as agent recovery instructions; naming conventions
- [[concepts/agent-skills]] — Skills as prompt templates: progressive disclosure, meta-tool architecture, SKILL.md structure, three loading levels
- [[concepts/agent-subagents]] — Subagents: own context window, YAML frontmatter format, all fields, scopes, invocation patterns, fork mode
- [[concepts/agent-teams]] — Agent teams: lead+teammates+task list+mailbox; when to use vs subagents; quality gate hooks; best practices
- [[concepts/verification-pipeline]] — Four-tier quality ladder: typecheck → visual verification → screenshot gate → design critique; origin failures; protocol rules
- [[concepts/owasp-security-checklist]] — OWASP Top 10 checklist with AI-specific extensions (indirect prompt injection, agentic sandbox); severity classification table
- [[concepts/domain-glossary]] — CONTEXT.md pattern: shared language between dev and agent; token efficiency, consistent naming, reduced context distraction
- [[concepts/deep-modules]] — Ousterhout's deep vs shallow modules; narrow interface, wide implementation; test boundary design; why AI produces shallow codebases by default
- [[concepts/evolution-strategies]] — Black-box optimization via parameter perturbation; ES vs RL trade-offs; shared random seed trick; progression from gaming (2017) to LLM fine-tuning (2025)
- [[concepts/multi-vendor-adversarial-review]] — Using different model/vendor to review agent work; catches single-model blind spots; same-tier vs cross-vendor vs /council
- [[concepts/branch-strategy-for-agents]] — head vs merge-to-head vs branch; when to use each; relation to worktrees and human-merge gates
- [[concepts/agent-self-correction]] — wiki-as-runtime-oracle; deviation trigger table; qmd queries for re-alignment; zero startup overhead
- [[concepts/instinct-clustering]] *(documented-not-adopted)* — behavioral pattern mining from tool-call telemetry; observe→cluster→inject pipeline; homunculus pattern
- [[concepts/dynamic-context-pruning]] — mid-session context reduction via Compress tool (model-driven) + deduplication + purge-errors; complements compaction; `@tarquinen/opencode-dcp`
- [[concepts/council-pattern]] — 3-stage multi-model deliberation: parallel dispatch → optional anonymized peer review → Chairman or human synthesis; Stage 2 optional; cost model; when to use
- [[concepts/worktree-isolation]] — git worktrees for agent filesystem isolation; ToS-compliant sandboxing alternative; scope overlap detection; merge-before-cleanup protocol
- [[concepts/rules-vs-hooks]] — static rules files vs. dynamic hook injection; compliance problem; hybrid patterns; when to use each
- [[concepts/memory-bank-pattern]] — Josh Wand's `_memory/` hierarchy for cross-session persistence; repomix compile; yak-shaving tracking; mode-based workflow
- [[concepts/self-healing-loop]] — failure→bounded retry→rollback→escalation; failure signature detection; guardrails; composes with ralph-loop; Dagger/ArgoCD/Windmill implementations
- [[concepts/agentic-cicd]] — CI as external watchdog when agent IS the developer; gate sequence; staging-first; diff size cap; builder/deployer network split
- [[concepts/error-budget]] — SRE error budget adapted to agent loops; retry/token/runtime/session budget axes; progress score; no-progress detection
- [[concepts/llm-as-judge]] — LLM evaluates another LLM's output via structured prompt; pairwise vs direct scoring vs G-Eval; failure modes (self-bias, reward hacking, sycophancy); relation to RLHF
- [[concepts/preference-feedback-loop]] — cross-vendor judge evaluates agent outputs on 4-dimension rubric; pattern-triggered rule extraction; human approval gate; extends mistakes/ + memory/feedback_*

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

## Comparisons
- [[comparisons/spec-driven-frameworks-vs-native]] — Heavy frameworks vs lean skills vs vanilla vs custom harness; community consensus; discrepancies with prior wiki
- [[comparisons/claude-code-vs-opencode-plugins]] — Hook surface, compaction control, custom tools; OpenCode's compaction hook as key differentiator
- [[comparisons/cc-to-cross-platform-migration]] — Full migration matrix: CC rules/skills/subagents/hooks/plugins → Gemini/OpenCode/Codex/Cursor; parity rating per layer

## Syntheses
- [[syntheses/agent-primitive-selection]] — Decision tree for skill vs subagent vs team; model tier routing; multi-vendor adversarial review pattern
- [[syntheses/lean-agentic-workflow]] — Full stack: grill→PRD→slices→AFK→verify; council, dangeresque, lean-session plugin, model routing, failure modes
