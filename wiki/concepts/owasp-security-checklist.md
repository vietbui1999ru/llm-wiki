---
title: "OWASP Security Checklist"
type: concept
tags: [security, OWASP, code-review, checklist, web-security, agents, agentic-coding]
sources: ["AI Agent Security - OWASP Cheat Sheet Series.md", "Secure Coding with AI - OWASP Cheat Sheet Series.md", "Secure AI Model Ops - OWASP Cheat Sheet Series.md", "GitHub Actions Security - OWASP Cheat Sheet Series.md", "Authorization - OWASP Cheat Sheet Series.md", "Content Security Policy - OWASP Cheat Sheet Series.md", "Cross Site Scripting Prevention - OWASP Cheat Sheet Series.md", "Cross-Site Request Forgery Prevention - OWASP Cheat Sheet Series.md", "Database Security - OWASP Cheat Sheet Series.md", "Docker Security - OWASP Cheat Sheet Series.md", "Insecure Direct Object Reference Prevention - OWASP Cheat Sheet Series.md", "Injection Prevention - OWASP Cheat Sheet Series.md", "NPM Security - OWASP Cheat Sheet Series.md", "OS Command Injection Defense - OWASP Cheat Sheet Series.md", "Secrets Management - OWASP Cheat Sheet Series.md", "Secure Cloud Architecture - OWASP Cheat Sheet Series.md", "Server Side Request Forgery Prevention - OWASP Cheat Sheet Series.md", "Session Management - OWASP Cheat Sheet Series.md", "SQL Injection Prevention - OWASP Cheat Sheet Series.md", "Vulnerable Dependency Management - OWASP Cheat Sheet Series.md", "Denial of Service - OWASP Cheat Sheet Series.md", "Error Handling - OWASP Cheat Sheet Series.md", "Logging - OWASP Cheat Sheet Series.md", "Deserialization - OWASP Cheat Sheet Series.md", "Transaction Authorization - OWASP Cheat Sheet Series.md", "Secure Code Review - OWASP Cheat Sheet Series.md", "DOM based XSS Prevention - OWASP Cheat Sheet Series.md", "AJAX Security - OWASP Cheat Sheet Series.md", "Third Party Javascript Management - OWASP Cheat Sheet Series.md", "LLM Prompt Injection Prevention - OWASP Cheat Sheet Series.md", "MCP Security - OWASP Cheat Sheet Series.md"]
created: 2026-04-26
updated: 2026-05-27
---

# OWASP Security Checklist

Structured checklist for web application security review. Based on OWASP Top 10. Applied during code review and security audits. AI-specific risks appended.

The full operational checklist lives in the `security-patterns` skill (preloaded into `security-auditor`). This page is the reference copy for the wiki.

## OWASP Top 10

### A01 — Broken Access Control
- Authorization checked on every route/endpoint (not just UI)
- Horizontal privilege escalation: can user A access user B's resources?
- Direct object references validated (IDs in URLs, query params)
- Admin/elevated actions gated by role, not just authenticated state
- CORS configured restrictively; no wildcard `*` on credentialed endpoints

### A02 — Cryptographic Failures
- Sensitive data (PII, tokens, passwords) not stored in plaintext
- Passwords hashed with bcrypt/argon2/scrypt (not MD5/SHA1)
- TLS enforced; no HTTP fallback for sensitive routes
- Secrets not in code, git history, or log output
- Tokens with appropriate expiry; refresh token rotation

### A03 — Injection
- SQL: parameterized queries or ORM only; no string concatenation into queries
- Shell: no user input in exec/spawn/system calls
- Template injection: user input never rendered as template code
- NoSQL: operators like `$where`, `$regex` not constructed from user input

### A04 — Insecure Design
- Business logic: can the normal flow be abused? (negative quantities, skipping steps)
- Rate limiting on auth endpoints, password reset, OTP verification
- Enumeration: error messages don't reveal whether a user exists
- Multi-step processes: each step validates prior step completed

### A05 — Security Misconfiguration
- Default credentials changed; debug endpoints disabled in production
- Error messages sanitized: no stack traces, file paths, or internal details to clients
- Security headers present: CSP, HSTS, X-Frame-Options, X-Content-Type
- Unnecessary features/endpoints/routes disabled

### A06 — Vulnerable Components
- Known CVEs in direct dependencies? (`npm audit`, `pip-audit`, `go mod`)
- Indirect/transitive dependencies not pinned to vulnerable versions

### A07 — Authentication Failures
- Session tokens: sufficient entropy, invalidated on logout, rotated on privilege change
- Brute force: lockout or progressive delay on repeated failures
- Password reset: tokens time-limited, single-use, invalidated after use
- JWT: algorithm verified server-side; `alg: none` rejected; secret not weak
- OAuth/OIDC: state parameter validated; redirect_uri allowlisted

### A08 — Software and Data Integrity
- Deserialization of untrusted data: type-checked before use
- Webhook signatures verified before processing payload
- File uploads: type validated server-side; stored outside webroot

### A09 — Logging and Monitoring
- Auth events logged: login, logout, failures, privilege changes
- Sensitive data excluded from logs (passwords, tokens, PII)
- Log injection: user-controlled input sanitized before logging

### A10 — SSRF
- URL inputs validated against allowlist; no arbitrary external fetches
- Internal metadata endpoints (169.254.x.x, cloud metadata APIs) blocked
- Redirects: open redirects validated against allowlist

## AI-Specific Risks

Extended from two 2026 OWASP cheat sheets (AI Agent Security + Secure Coding with AI). Two perspectives:
- **Building an agent** — tool security, memory security, multi-agent trust
- **Using AI coding tools** — slopsquatting, rules file injection, CI/CD confused deputy, test fabrication

### Indirect Prompt Injection
- Agent reads external content (URLs, files, emails, issues, PR descriptions, error traces)? → treat as untrusted
- External content can't override system instructions or trigger tool calls
- Rules files (CLAUDE.md, AGENTS.md) modified by injected instructions persist across all future sessions
- Sandboxed: agent can't exfiltrate data via unexpected network calls

See [[concepts/indirect-prompt-injection]] for full treatment including dev-loop vectors and CI/CD confused deputy.

### Agentic Sandbox Controls
- Tool permissions minimal: only what the task requires
- Destructive operations (delete, overwrite) require explicit confirmation
- Secrets injected at runtime, not baked into prompts or config; ephemeral credentials per task
- `--dangerously-skip-permissions` and auto-accept modes remove all approval prompts — only safe with OS-level sandbox enforced independently

See [[concepts/agentic-sandbox-controls]] for full treatment.

### Tool Security & Least Privilege
- Agents get minimum tools for specific task; no wildcard permissions (e.g. `"allowed_commands": "*"`)
- Tool authorization middleware for MEDIUM+ risk operations (require `user_confirmed` flag)
- Risk tiers: LOW (read) → MEDIUM (write) → HIGH (email, code exec) → CRITICAL (delete, financial)
- MCP servers: maintain allowlist; snapshot-and-diff tool definitions to detect rug-pull updates; audit tool descriptions for embedded injection payloads

### Memory & Context Security
- Validate/sanitize data before storing in agent memory
- Memory isolation between users and sessions
- TTL + size limits on memory entries; scan for PII and API keys before persistence
- Cryptographic integrity check: `checksum = sha256(content + user_id + encryption_key)` — detects tampering

### Data Classification
- RESTRICTED (SSN, credit card, health): redact fully in context, logs, output
- CONFIDENTIAL (salaries, API keys): mask in context/output, redact fully in logs
- INTERNAL: normal access controls; PUBLIC: no restrictions

### AI Coding Tool Threats (Secure Coding with AI)

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

### Denial of Wallet (DoW)
- Unbounded agent loops can exhaust API/compute budget via crafted inputs
- Set per-session cost limits and tool call rate limits; alert on anomalies
- Recursion, retry, and chain-depth limits for agentic/tool-using flows
- Circuit breakers or kill switches for cost/latency/tool-call anomalies; alert on sudden spend or token spikes
- See [[concepts/error-budget]] for token budget patterns

### Monitoring Anomaly Thresholds (reference)
- >30 tool calls/min, >5 failed calls, >$10/session cost, any injection attempt → CRITICAL alert
- Watch guardrail approval rate for drift — sudden changes often precede a working bypass

## Web Security Reference (Stack-Agnostic Stubs)

Key controls not fully covered above. Expand to dedicated pages when targeted sources are ingested.

**Session Management**: min 128-bit entropy tokens, `HttpOnly`, `Secure`, `SameSite=Strict`; invalidate on logout server-side; rotate on privilege change; never in URL parameters.

**CSRF**: synchronizer token pattern or `SameSite=Strict` cookies; verify `Origin`/`Referer` headers; custom request headers as secondary defense; exempt GET/HEAD/OPTIONS (must be idempotent).

**DOM-Based XSS**: untrusted sources include `document.URL`, `location.hash`, `document.referrer`, `postMessage`; dangerous sinks include raw HTML setters and eval; never pass untrusted source to dangerous sink without DOMPurify.

**IDOR**: validate authenticated user owns the requested resource; map internal IDs to per-user opaque tokens; log access denials; scope queries to user_id — never fetch by id alone.

**Transaction Authorization**: re-authenticate for high-value actions (account deletion, payment); idempotency keys for financial transactions; audit log of all state-changing operations with before/after values.

**Third-Party Scripts**: Subresource Integrity (SRI) for CDN-hosted scripts; CSP to allowlist script sources; audit third-party scripts for data exfiltration risk.

**Deserialization**: never deserialize untrusted data directly into objects; validate type before deserializing; use schema validation (zod, joi) on JSON.parse results; sign serialized tokens.

**DoS**: rate limit all public endpoints (especially auth, search, file upload); request size limits; avoid regex backtracking (ReDoS); connection timeouts.

## Severity Classification

| Level | Criteria | Action |
|---|---|---|
| **Critical** | Auth bypass, SQL injection, RCE, secret exposure | Block; fix before merge |
| **High** | Missing auth check, IDOR, stored XSS, path traversal | Block; fix before merge |
| **Medium** | Rate limiting missing, open redirect, verbose errors | Fix in follow-up PR |
| **Low** | Missing security headers, minor info leakage | Fix when convenient |
| **Info** | Defense-in-depth additions | Optional |

## Related Pages

- [[concepts/indirect-prompt-injection]] — AI-specific attack vector; primary threat for agents; full prompt injection taxonomy
- [[concepts/agentic-sandbox-controls]] — OS-level controls for agent execution environments
- [[concepts/ai-code-review]] — broader code review process including security as one layer
- [[concepts/agentic-sandbox-controls]] — NVIDIA AI Red Team OS-level controls; subprocess escape problem; secret injection pattern
- [[concepts/error-budget]] — token/session budget patterns implementing spend limits and circuit breakers
