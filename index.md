# Wiki Index

Catalog of all pages. Updated on every ingest operation.

## Summaries
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

## Entities
- [[entities/qmd]] *(stub)* — Local hybrid markdown search engine (BM25 + vector); CLI + MCP server
- [[entities/ai-coding-agents]] — The class of AI coding tools (Claude Code, Codex, OpenCode, etc.): capability spectrum, safety model, use cases
- [[entities/pydoll]] — Async Python CDP-native browser automation library with fingerprint evasion and WebRTC leak protection

## Concepts
- [[concepts/compounding-knowledge-base]] — Knowledge bases that accumulate compiled structure vs. RAG's per-query retrieval
- [[concepts/contextual-retrieval]] — RAG preprocessing technique: LLM-generated context prepended to chunks before embedding + BM25 indexing
- [[concepts/bm25]] — Lexical ranking function; exact-match complement to semantic embeddings in hybrid search
- [[concepts/reranking]] — Post-retrieval filtering: score top ~150 candidates, pass top 20 to LLM; stacks with contextual retrieval
- [[concepts/ai-code-review]] — Reviewing AI-generated code: automated + human layers, 8-point checklist, core risk of intent misalignment
- [[concepts/ai-specific-pitfalls]] — Failure modes unique to AI code: hallucinated APIs, slopsquatting, deleted tests, "looks right" logic errors
- [[concepts/agent-context-instructions]] — Standards documents that align agent output to team conventions before generation
- [[concepts/indirect-prompt-injection]] — Primary attack vector on AI agents: adversarial instructions embedded in third-party content the agent reads
- [[concepts/agentic-sandbox-controls]] — OS-level security controls for AI agents: tiered denylist, secret injection, lifecycle management, approval anti-patterns
- [[concepts/web-fingerprinting]] — Multi-layer browser/network/behavioral fingerprinting used by anti-bot systems; evasion principles
- [[concepts/proxy-rotation]] — Proxy types by OSI layer, rotation strategies, limits vs. full fingerprinting evasion
- [[concepts/webrtc-ip-leak]] — WebRTC UDP bypass of proxy configuration; ICE/STUN mechanism and mitigations
- [[concepts/agent-harness]] — Model + harness = agent; core components: filesystem, bash, sandbox, context management, long-horizon loops
- [[concepts/ralph-loop]] — Harness pattern: intercept exit, reinjecting original prompt with clean context + durable filesystem state
- [[concepts/context-degradation]] — Five named failure modes: lost-in-middle, poisoning, distraction, confusion, clash; thresholds and mitigations
- [[concepts/context-compression]] — Three strategies: anchored iterative summarization (default), opaque, regenerative; token budget table; KV-cache rules
- [[concepts/tool-design-for-agents]] — Dual audience principle; error messages as agent recovery instructions; naming conventions

## Comparisons
<!-- side-by-side analyses -->

## Syntheses
<!-- cross-source insights and theses -->
