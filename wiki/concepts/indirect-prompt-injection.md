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

## Mitigations

Indirect prompt injection cannot be fully solved at the model layer. The mitigations are structural:

- [[concepts/agentic-sandbox-controls]] — OS-level restrictions on what the agent can do even if injected
- Block writes to agent config files — prevents durable persistence via injected instructions
- Network egress controls — limits exfiltration even if injection succeeds
- Sandbox lifecycle management — clears any injected persistence between sessions
- Separate LLM call to summarize/validate untrusted external content before injecting into main context
- Restrict agent context to minimum files and content needed for the task

## Related concepts

- [[concepts/agentic-sandbox-controls]]
- [[entities/ai-coding-agents]]
- [[summaries/owasp-ai-security]] — dev-loop attack vectors; CI/CD confused deputy; MCP tool shadowing
- [[concepts/agent-context-instructions]] — rules files (CLAUDE.md, AGENTS.md) — the persistent steering surface
