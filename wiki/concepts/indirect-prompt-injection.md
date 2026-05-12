---
title: "Indirect Prompt Injection"
type: concept
tags: [security, prompt-injection, agents, attack-vector, agentic-coding, ci-cd, mcp]
sources: ["Practical Security Guidance for Sandboxing Agentic Workflows and Managing Execution Risk.md", "Secure Coding with AI - OWASP Cheat Sheet Series.md", "AI Agent Security - OWASP Cheat Sheet Series.md"]
created: 2026-04-22
updated: 2026-05-12
---

# Indirect Prompt Injection

The primary attack vector against AI coding agents. An adversary embeds instructions in content that the agent will ingest — not in the user's direct prompt, but in data the agent reads as part of its task.

## How it works

The agent ingests malicious content from a **third-party source** the user didn't author:

- Cloned repositories or pull requests containing injected instructions
- Git history with embedded commands
- `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, `copilot-instructions.md` files in a repo
- MCP server responses returning adversarial content
- Web pages fetched during research

The LLM then treats this content as legitimate instruction and takes attacker-directed actions — exfiltrating files, establishing persistence, modifying configs.

## Why it's especially dangerous for coding agents

Coding agents have broad OS-level permissions (same as the developer) and execute arbitrary code by design. A successful injection can:

- Read `~/.ssh`, `.env`, credentials directories and exfiltrate via network
- Write to `~/.zshrc` or `~/.local/bin` for persistence and sandbox escape
- Modify agent config files (`CLAUDE.md`, hooks) to maintain control across future sessions
- Redirect git/curl operations to attacker-controlled URLs via `~/.gitconfig` / `~/.curlrc`

## Distinction from direct prompt injection

| Type | Source | Example |
|---|---|---|
| Direct | User's own prompt | Jailbreak in the chat input |
| Indirect | Third-party content agent reads | Malicious instruction in a cloned repo's README |

## The Lethal Trifecta

Simon Willison's term for the highest-risk subset of prompt injection scenarios. A system is in the lethal trifecta when it combines:

1. **Access to private data** (source code, credentials, env vars)
2. **Exposure to untrusted content** (fetched files, repos, web pages)
3. **Ability to externally communicate** (arbitrary outbound network)

When all three are present, a single successful injection can exfiltrate private data to the attacker. Removing any one leg breaks the attack chain — network egress control is typically the most tractable mitigation. See [[summaries/living-dangerously-with-claude]].

## Attack Vectors in the Development Loop

When using AI coding tools (Claude Code, Cursor, Codex, Aider), the injection surface expands beyond what the user writes:

| Source | Attack |
|---|---|
| Issue bodies / PR descriptions | Agent asked to "fix issue #123" reads embedded instructions and executes them |
| PR review comments | Agent asked to "address feedback" follows attacker-written "feedback" modifying unrelated files |
| README / documentation | Cloned repos or fetched docs contain invisible-to-humans instructions |
| Error traces / log output | Crafted error messages inject instructions when agent reads terminal output to debug |
| Dependency changelogs | Agent reads changelog to understand version difference; injected content exploited |
| Fetched web pages | Agents with web access influenced by page content |

### Rules Files: Persistent Steering = Durable Injection Target

Files that steer all future agent generations (`.cursorrules`, `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `.windsurfrules`) are the most dangerous injection surface. A one-shot injection that *modifies* these files controls every subsequent agent session on the repository — indefinitely.

**Why worse than a normal injection:** ordinary injection affects one session; rules file modification is persistent across all future sessions, survives context resets, and is invisible to users who don't audit the file.

**Controls:**
- Treat rules files as security-critical config (same scrutiny as CI/CD pipeline changes)
- Require explicit human approval for any modification, including modifications by the agent itself
- Git hooks that flag changes to known rules files in every PR
- Audit existing rules files for instructions that weaken security controls or disable safety features

### CI/CD Confused Deputy

AI-powered CI/CD agents (review bots, `claude-code-action`, Copilot review) process PR events with access to org secrets and repository write access. A malicious PR body can instruct the CI agent to exfiltrate secrets, modify the build pipeline, or push unauthorized commits. This is confused deputy at scale.

**Defense:** scope CI agent credentials to minimum required; filter and sanitize PR content before passing as context; require approval gates before CI agents can push commits or access sensitive resources.

### MCP Tool Shadowing

A malicious MCP server registers a tool with the same name as a legitimate one. The agent calls what it believes is the trusted tool but hits the attacker's implementation. Also: tool descriptions are part of the agent's context and can contain prompt injection payloads — tool metadata is not trusted prose.

**Defense:** pin tool definitions and diff on each session (snapshot-and-diff for rug-pull detection); maintain MCP server allowlist; audit tool descriptions for hidden instructions.

## LLM-Level Attack Techniques

These attacks target the model's input/output processing rather than the agent's permissions, and apply to both direct and indirect injection.

### Encoding & Obfuscation
Base64 / hex encoding hides injection strings from regex filters. Unicode zero-width characters embed invisible content. KaTeX white-on-white text (`$\color{white}{\text{malicious}}$`) is invisible to humans but processed by the model.

### Typoglycemia Attacks
LLMs read words with scrambled middle letters if the first and last letters are intact — the same cognitive shortcut humans use. `"ignroe all prevoius systme instructions"` reaches the model as `"ignore all previous system instructions"`.

**Detection approach:** same-first-last-letter + anagram check is the minimal implementation. Production systems should use Levenshtein distance (threshold 1–2) or Jaro-Winkler against a keyword blocklist — covers insertions, deletions, transpositions beyond simple anagram scrambles. Libraries: `rapidfuzz` (Python), `apache-commons-text` (Java). Reference: [arxiv.org/abs/2410.01677](https://arxiv.org/abs/2410.01677)

### Best-of-N (BoN) Jailbreaking
Systematically generate prompt variations until one bypasses safety: random capitalization, character spacing, word shuffling, framing changes. Due to **power-law scaling**, success probability approaches 1 with sufficient attempts.

**Measured results** (Hughes et al., [arxiv.org/abs/2412.03556](https://arxiv.org/abs/2412.03556)):
- 89% success on GPT-4o, 78% on Claude 3.5 Sonnet

All current defenses (rate limiting, content filters, circuit breakers, safety training, temperature reduction) only increase attacker cost — they do not prevent eventual success. Defense in depth is the current only viable posture; no single control is sufficient.

### Multimodal Injection
Instructions hidden in images via steganography or invisible characters, or in document metadata, processed by multimodal LLMs. The model executes instructions embedded in a PNG or PDF that look like a normal file to humans. Reference: [arxiv.org/abs/2506.02456](https://arxiv.org/abs/2506.02456)

### RAG Poisoning
Adversarial content injected into the vector database backing a RAG system. Retrieval returns attacker-controlled documents as if they were trusted knowledge — instructions in those documents reach the primary LLM in the trusted context position. Example: embedding a document that says "Ignore all previous instructions" in a shared knowledge base.

---

## Mitigations

Indirect prompt injection cannot be fully solved at the model layer. The mitigations are structural:

- [[concepts/agentic-sandbox-controls]] — OS-level restrictions on what the agent can do even if injected
- Block writes to agent config files — prevents durable persistence via injected instructions
- Network egress controls — limits exfiltration even if injection succeeds
- Sandbox lifecycle management — clears any injected persistence between sessions
- Separate LLM call to summarize/validate untrusted external content before injecting into main context
- Restrict agent context to minimum files and content needed for the task

### Dual-LLM Pattern (Architectural Defense)
[Simon Willison's pattern](https://simonwillison.net/2023/Apr/25/dual-llm-pattern/): split into a **privileged LLM** (holds tools, takes actions, never reads untrusted content) and a **quarantined LLM** (reads untrusted content, cannot act, returns only structured summaries to the privileged model). Injected instructions in external content never reach the actor.

### Model-Based Guardrails
A separate purpose-trained classifier (Llama Guard, ShieldGemma, IBM Granite Guardian, Prompt Guard) screening at three placements:

| Placement | What it covers |
|---|---|
| **Input screening** | User prompts + all retrieved/fetched content before primary LLM |
| **Output screening** | Primary model response before returning to user or downstream tools |
| **Action screening** | Each proposed tool call vs. original user intent (without untrusted context) |

Guardrails are one defense layer — they are themselves LLMs susceptible to injection. A purpose-trained classifier with a different architecture is preferable to a general-purpose model from the same family (same jailbreaks transfer more readily).

## Related concepts

- [[concepts/agentic-sandbox-controls]]
- [[entities/ai-coding-agents]]
- [[summaries/owasp-ai-security]] — dev-loop attack vectors; CI/CD confused deputy; MCP tool shadowing
- [[summaries/owasp-prompt-injection]] — full OWASP attack taxonomy; typoglycemia; Best-of-N; dual-LLM pattern
- [[summaries/owasp-mcp-security]] — MCP-specific threat model; tool shadowing; rug pull; hash pinning
- [[concepts/agent-context-instructions]] — rules files (CLAUDE.md, AGENTS.md) — the persistent steering surface
