---
title: "Indirect Prompt Injection"
type: concept
tags: [security, prompt-injection, agents, attack-vector]
sources: ["Practical Security Guidance for Sandboxing Agentic Workflows and Managing Execution Risk.md"]
created: 2026-04-22
updated: 2026-04-22
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

## Mitigations

Indirect prompt injection cannot be fully solved at the model layer. The mitigations are structural:

- [[concepts/agentic-sandbox-controls]] — OS-level restrictions on what the agent can do even if injected
- Block writes to agent config files — prevents durable persistence via injected instructions
- Network egress controls — limits exfiltration even if injection succeeds
- Sandbox lifecycle management — clears any injected persistence between sessions

## Related concepts

- [[concepts/agentic-sandbox-controls]]
- [[entities/ai-coding-agents]]
