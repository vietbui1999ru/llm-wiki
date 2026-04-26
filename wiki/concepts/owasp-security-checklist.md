---
title: "OWASP Security Checklist"
type: concept
tags: [security, OWASP, code-review, checklist, web-security]
sources: []
created: 2026-04-26
updated: 2026-04-26
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

These extend the OWASP checklist for agent-based systems:

### Indirect Prompt Injection
- Agent reads external content (URLs, files, emails)? → treat as untrusted
- External content can't override system instructions or trigger tool calls
- Sandboxed: agent can't exfiltrate data via unexpected network calls

See [[concepts/indirect-prompt-injection]] for full treatment.

### Agentic Sandbox Controls
- Tool permissions minimal: only what the task requires
- Destructive operations (delete, overwrite) require explicit confirmation
- Secrets injected at runtime, not baked into prompts or config

See [[concepts/agentic-sandbox-controls]] for full treatment.

## Severity Classification

| Level | Criteria | Action |
|---|---|---|
| **Critical** | Auth bypass, SQL injection, RCE, secret exposure | Block; fix before merge |
| **High** | Missing auth check, IDOR, stored XSS, path traversal | Block; fix before merge |
| **Medium** | Rate limiting missing, open redirect, verbose errors | Fix in follow-up PR |
| **Low** | Missing security headers, minor info leakage | Fix when convenient |
| **Info** | Defense-in-depth additions | Optional |

## Related Pages

- [[concepts/indirect-prompt-injection]] — AI-specific attack vector; primary threat for agents
- [[concepts/agentic-sandbox-controls]] — OS-level controls for agent execution environments
- [[concepts/ai-code-review]] — broader code review process including security as one layer
- [[summaries/agentic-sandbox-security]] — NVIDIA AI Red Team source for AI-specific controls
