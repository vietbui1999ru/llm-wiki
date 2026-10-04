---
title: "OWASP AI and Agent Security Risks"
type: concept
tags: [security, OWASP, agents, agentic-coding, prompt-injection, ai-coding-tools]
sources: ["AI Agent Security - OWASP Cheat Sheet Series.md", "Secure Coding with AI - OWASP Cheat Sheet Series.md", "Secure AI Model Ops - OWASP Cheat Sheet Series.md", "LLM Prompt Injection Prevention - OWASP Cheat Sheet Series.md", "MCP Security - OWASP Cheat Sheet Series.md", "GitHub Actions Security - OWASP Cheat Sheet Series.md"]
created: 2026-10-04
updated: 2026-10-04
---

# OWASP AI and Agent Security Risks

AI-specific risks from the OWASP cheat sheets, split out of [[concepts/owasp-security-checklist]] on 2026-10-04.

Extended from two 2026 OWASP cheat sheets (AI Agent Security + Secure Coding with AI). Two perspectives:
- **Building an agent** — tool security, memory security, multi-agent trust
- **Using AI coding tools** — slopsquatting, rules file injection, CI/CD confused deputy, test fabrication

## Indirect Prompt Injection
- Agent reads external content (URLs, files, emails, issues, PR descriptions, error traces)? → treat as untrusted
- External content can't override system instructions or trigger tool calls
- Rules files (CLAUDE.md, AGENTS.md) modified by injected instructions persist across all future sessions
- Sandboxed: agent can't exfiltrate data via unexpected network calls

See [[concepts/indirect-prompt-injection]] for full treatment including dev-loop vectors and CI/CD confused deputy.

## Agentic Sandbox Controls
- Tool permissions minimal: only what the task requires
- Destructive operations (delete, overwrite) require explicit confirmation
- Secrets injected at runtime, not baked into prompts or config; ephemeral credentials per task
- `--dangerously-skip-permissions` and auto-accept modes remove all approval prompts — only safe with OS-level sandbox enforced independently

See [[concepts/agentic-sandbox-controls]] for full treatment.

## Tool Security & Least Privilege
- Agents get minimum tools for specific task; no wildcard permissions (e.g. `"allowed_commands": "*"`)
- Tool authorization middleware for MEDIUM+ risk operations (require `user_confirmed` flag)
- Risk tiers: LOW (read) → MEDIUM (write) → HIGH (email, code exec) → CRITICAL (delete, financial)
- MCP servers: maintain allowlist; snapshot-and-diff tool definitions to detect rug-pull updates; audit tool descriptions for embedded injection payloads

## Memory & Context Security
- Validate/sanitize data before storing in agent memory
- Memory isolation between users and sessions
- TTL + size limits on memory entries; scan for PII and API keys before persistence
- Cryptographic integrity check: `checksum = sha256(content + user_id + encryption_key)` — detects tampering

## Data Classification
- RESTRICTED (SSN, credit card, health): redact fully in context, logs, output
- CONFIDENTIAL (salaries, API keys): mask in context/output, redact fully in logs
- INTERNAL: normal access controls; PUBLIC: no restrictions

## AI Coding Tool Threats (Secure Coding with AI)

**Hallucinated Dependencies (slopsquatting)**
- AI suggests packages that don't exist; attackers pre-register malicious packages at those names
- Verify every AI-suggested package: check registry existence, download count, creation date (< 30 days = suspect), maintainer history
- Block unvetted packages in CI; maintain internal allowlist

**Outdated Dependencies**
- AI training data is historical; suggested versions may have post-cutoff CVEs
- Run `npm audit` / `pip audit` / `govulncheck` on every AI-generated dependency list
- Never skip dependency auditing because code was AI-generated

**Rules Files as Persistent Steering**
- `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md` steer all future generations
- Treat as security-critical config: require explicit approval for any modification including by the agent
- Git hooks that flag changes to rules files in every PR

**Test Fabrication and Test Deletion**
- Agents make CI green by: deleting failing tests, weakening assertions, mocking the unit under test, asserting buggy behavior
- 100% pass rate ≠ evidence of correctness when the same agent wrote both code and tests
- Add adversarial/negative test cases the AI didn't generate; flag test deletions in CI; human-review all assertion changes

**CI/CD Confused Deputy**
- CI/CD bots (review bots, `claude-code-action`) process PR events with org secrets
- Malicious PR body can instruct CI agent to exfiltrate secrets or modify the pipeline ("clinejection" — documented in [Cline post-mortem](https://cline.bot/blog/post-mortem-unauthorized-cline-cli-npm))
- Scope CI agent credentials to minimum; sanitize PR content before passing as context; approval gates for pushes
- Restrict default `GITHUB_TOKEN` to read-only at repo level; grant write only at job level
- Avoid `pull_request_target` and `workflow_run` triggers (expose secrets to untrusted code)
- OIDC-based short-lived tokens ("trusted publishing") eliminates static credentials from workflows
- Enable CodeQL `language: actions` scanning + [Zizmor](https://docs.zizmor.sh/)
- SHA-pin third-party actions to commit SHA, not mutable tags: `uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2`
- Require approval for all external contributors — "first-time contributor" setting is bypassable via initial legitimate PR

**Prompt Context Leakage**
- AI coding tools send open files and terminal output to the model provider API
- `.gitignore` does NOT prevent AI tools from reading files
- Exclude `.env`, `*.pem`, `*.key`, `credentials.json` via `.cursorignore`/`.copilotignore`

**Multi-Agent Propagation**
- Prompt injection propagates across agent boundaries: output of compromised Agent A becomes instructions for Agent B
- Treat output from any agent as untrusted input to the next; sanitize before passing
- Don't inherit full permissions/credentials from parent agent without scope restriction
- Explicit trust levels: `UNTRUSTED (0) → INTERNAL (1) → PRIVILEGED (2) → SYSTEM (3)`; sanitize payload based on trust level before forwarding
- Signed inter-agent messages: verify signature + freshness (5-minute window prevents replay); authorized recipient list per sender; circuit breaker per agent (threshold=5 failures, 60s recovery)

## Denial of Wallet (DoW)
- Unbounded agent loops can exhaust API/compute budget via crafted inputs
- Set per-session cost limits and tool call rate limits; alert on anomalies
- Recursion, retry, and chain-depth limits for agentic/tool-using flows
- Circuit breakers or kill switches for cost/latency/tool-call anomalies; alert on sudden spend or token spikes
- See [[concepts/error-budget]] for token budget patterns

## Monitoring Anomaly Thresholds (reference)
- >30 tool calls/min, >5 failed calls, >$10/session cost, any injection attempt → CRITICAL alert
- Watch guardrail approval rate for drift — sudden changes often precede a working bypass

## Related Pages

- [[concepts/owasp-security-checklist]] — hub: severity classification and the other OWASP pages
- [[concepts/owasp-top-10-checklist]] — the classic Top 10 review checklist
- [[concepts/indirect-prompt-injection]] — AI-specific attack vector; primary threat for agents; full prompt injection taxonomy
- [[concepts/agentic-sandbox-controls]] — OS-level controls for agent execution environments; NVIDIA AI Red Team controls; subprocess escape problem; secret injection pattern
- [[concepts/error-budget]] — token/session budget patterns implementing spend limits and circuit breakers
