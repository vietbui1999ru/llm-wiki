# Wiki Log

Append-only. Format: `## [YYYY-MM-DD] <operation> | <title>`

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
