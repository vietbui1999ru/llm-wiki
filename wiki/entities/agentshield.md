---
title: "AgentShield"
type: entity
tags: [security, claude-code, static-analysis, agent-harness, red-team]
sources:
  - "vietbui1999rueverything-claude-code The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and beyond..md"
created: 2026-05-19
updated: 2026-05-19
---

# AgentShield

Static analysis security scanner for Claude Code configurations. Scans CLAUDE.md, hooks, MCP configs, agent definitions, skills, and settings.json for vulnerabilities, misconfigurations, and injection risks. Built at Cerebral Valley x Anthropic Hackathon (Feb 2026) as part of [[entities/everything-claude-code]].

- GitHub: `affaan-m/agentshield`
- npm: `ecc-agentshield`
- 1282 tests, 102 rules, 98% coverage (all claimed from README, unverified independently)

---

## What It Scans

Five scan categories:
1. **Secrets detection** — 14 patterns (API keys, tokens, credentials embedded in config files)
2. **Permission auditing** — overly broad tool permissions, missing deny rules
3. **Hook injection analysis** — user-controlled data flowing into hook commands without sanitization
4. **MCP server risk profiling** — untrusted MCP servers, overprivileged tool access
5. **Agent config review** — agent definitions that lack isolation or have overly broad tool access

Targets: `CLAUDE.md`, `settings.json`, `.claude/`, MCP configs, hook definitions, `agents/*.md`, `skills/`.

---

## The 3-Agent Opus Pipeline (`--opus` flag)

Deep analysis mode runs three Claude Opus 4.6 agents in a red-team pipeline:

```
Attacker agent    → finds exploit chains
Defender agent    → evaluates existing protections
Auditor agent     → synthesizes into prioritized risk assessment
```

"Adversarial reasoning, not just pattern matching." This is a concrete instance of [[concepts/multi-vendor-adversarial-review]] applied to security configuration rather than code review.

---

## Usage

```bash
# Quick scan (no install)
npx ecc-agentshield scan

# Auto-fix safe issues
npx ecc-agentshield scan --fix

# Deep analysis (3-agent Opus pipeline)
npx ecc-agentshield scan --opus --stream

# Generate secure config from scratch
npx ecc-agentshield init
```

From within Claude Code (ECC installed):
```
/security-scan
```

**CI integration**: Exit code 2 on critical findings — usable as a build gate.

**Output formats**: Terminal (A–F grade), JSON, Markdown, HTML. GitHub Action available at `affaan-m/agentshield`.

---

## Scope vs. Existing Security Concepts

AgentShield is **config-layer security**, not code-layer security. The distinction matters:

| Layer | Tool | What it catches |
|---|---|---|
| Config (CLAUDE.md, hooks, MCP) | AgentShield | Secrets in configs, injection in hooks, overprivileged MCPs |
| Code (src/) | `/security-review` skill, OWASP checklist | OWASP Top 10, SQL injection, XSS |
| Agent behavior | [[concepts/agentic-sandbox-controls]] | OS-level isolation, sandbox escapes |
| Prompt inputs | [[concepts/indirect-prompt-injection]] | Adversarial instructions in third-party content |

These are complementary, not overlapping. A codebase can pass code review and still have hooks that pass user-controlled strings to shell commands without sanitization.

---

## Related Wiki Pages

- [[entities/everything-claude-code]] — parent project
- [[concepts/owasp-security-checklist]] — code-layer security (complementary)
- [[concepts/agentic-sandbox-controls]] — OS-level isolation (complementary)
- [[concepts/indirect-prompt-injection]] — prompt-layer attack vectors (complementary)
- [[concepts/multi-vendor-adversarial-review]] — pattern AgentShield's `--opus` flag instantiates
