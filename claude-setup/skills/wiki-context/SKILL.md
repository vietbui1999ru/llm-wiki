---
name: wiki-context
description: Search the personal LLM wiki for concepts, patterns, and decisions relevant to the current task. Invoke before designing systems, reviewing patterns, or answering architecture questions — any topic that may have a wiki page.
allowed-tools: "Bash,Read"
---

# Wiki Context

Load relevant wiki knowledge into context before proceeding with the task.

## Step 0: Resolve library/tool docs via context7 (if applicable)

If the task involves a specific library, framework, CLI tool, SDK, or API:

```
# 1. Resolve the library ID
mcp__context7__resolve-library-id: {"libraryName": "<library name>"}

# 2. Query relevant docs
mcp__context7__query-docs: {"context7CompatibleLibraryID": "<id>", "topic": "<specific question>", "tokens": 3000}
```

When to invoke context7:
- Before writing code that uses a library API or CLI
- When uncertain about a flag, parameter, or method name
- Before any `pip install`, `npm install`, or CLI invocation you haven't used recently
- When the wiki summary for a tool exists but may be out of date

Skip context7 when: the task is pure reasoning, git ops, or file manipulation with no external library.

## Step 1: Identify search terms

Extract 2–3 keywords from the current task. Examples:
- "design agent system" → search `agent orchestration delegation`
- "review for security" → search `security code review patterns`
- "context window filling" → search `context compression degradation`

## Step 2: Search wiki + mistakes

Always search both collections:

```
# Wiki knowledge
qmd query: [{type:'lex', query:'TERM1'}, {type:'vec', query:'TERM2 TERM3'}]
intent: 'what you're looking for'
collection: 'wiki'
minScore: 0.4

# Past mistakes relevant to the task domain
qmd query: [{type:'lex', query:'TERM1 error fix'}, {type:'vec', query:'TERM1 mistake prevention'}]
intent: 'past errors in this domain'
collection: 'wiki'
minScore: 0.5
```

If qmd MCP unavailable, CLI fallback:
```bash
cd ~/repos/llm-wiki && qmd query "TERM1 TERM2" --files --min-score 0.4
cat mistakes/global-prevention-rules.md
```

## Step 3: Load relevant pages

For each returned file path with score > 0.4:
```bash
# via MCP: qmd get <path>
# via CLI: cat ~/repos/llm-wiki/wiki/<path>
```

Load up to 3 pages. Prioritize concept pages over summaries.

## Step 4: Apply and cite

Apply patterns found. Always cite the page:
> Per [[concepts/agent-harness]]: ...

If you discover a reusable pattern not in the wiki, flag:
> `WIKI-CANDIDATE: <description of the pattern>`

## What's in the wiki

**Agent engineering**: agent-harness, ralph-loop, agent-skills, agent-subagents, agent-teams, verification-pipeline, context-degradation, context-compression, tool-design-for-agents, agent-context-instructions, agentic-sandbox-controls, indirect-prompt-injection, claude-code-plugins, domain-glossary

**Development workflow**: unit-testing, cicd-testing, software-documentation, deep-modules

**Code quality**: ai-code-review, ai-specific-pitfalls, contextual-retrieval, reranking, bm25

**ML / AI research**: evolution-strategies, summaries/openai-es-2017, summaries/es-llm-finetuning-2025, summaries/eggroll-2025, entities/eggroll

**Infra / scraping**: web-fingerprinting, proxy-rotation, webrtc-ip-leak, entities/pydoll, entities/firecrawl

**Document parsing / RAG**: entities/docling, summaries/docling, summaries/contextual-retrieval

**Tools / entities**: entities/qmd, entities/ai-coding-agents

**Plugins/workflows**: summaries/superpowers-plugin, summaries/mattpocockskills, summaries/mattpocockworkflow, summaries/firecrawl-mcp-server, summaries/claude-code-plugins-llm-wiki

**Mistakes** (auto-loaded at startup): mistakes/global-prevention-rules.md — check before unfamiliar CLI ops
