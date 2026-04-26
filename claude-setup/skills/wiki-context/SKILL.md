---
name: wiki-context
description: Search the personal LLM wiki for concepts, patterns, and decisions relevant to the current task. Use when you need to look up agent engineering patterns, context management strategies, security concepts, or any topic that may have a wiki page. Invoke before designing systems, reviewing patterns, or answering architecture questions.
allowed-tools: "Bash,Read"
---

# Wiki Context

Load relevant wiki knowledge into context before proceeding with the task.

## Step 1: Identify search terms

Extract 2–3 keywords from the current task. Examples:
- "design agent system" → search `agent orchestration delegation`
- "review for security" → search `security code review patterns`
- "context window filling" → search `context compression degradation`

## Step 2: Search the wiki

Preferred — use the qmd MCP tool (already connected, no bash needed):
```
qmd query: [{type:'lex', query:'TERM1'}, {type:'vec', query:'TERM2 TERM3'}]
intent: 'brief description of what you're looking for'
collection: 'wiki'
minScore: 0.4
```

Fallback — CLI:
```bash
cd ~/repos/llm-wiki && qmd query "TERM1 TERM2" --files --min-score 0.4
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

**Agent engineering**: agent-harness, ralph-loop, agent-skills, agent-subagents, agent-teams, verification-pipeline, context-degradation, context-compression, tool-design-for-agents, agent-context-instructions, agentic-sandbox-controls, indirect-prompt-injection

**Code quality**: ai-code-review, ai-specific-pitfalls, contextual-retrieval, reranking, bm25

**Infra**: web-fingerprinting, proxy-rotation, webrtc-ip-leak

**Tools**: entities/qmd, entities/pydoll, entities/ai-coding-agents
