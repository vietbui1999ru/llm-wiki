---
title: "OWASP Top 10 Checklist"
type: concept
tags: [security, OWASP, code-review, checklist, web-security]
sources: ["Authorization - OWASP Cheat Sheet Series.md", "Injection Prevention - OWASP Cheat Sheet Series.md", "SQL Injection Prevention - OWASP Cheat Sheet Series.md", "OS Command Injection Defense - OWASP Cheat Sheet Series.md", "Secrets Management - OWASP Cheat Sheet Series.md", "Vulnerable Dependency Management - OWASP Cheat Sheet Series.md", "Error Handling - OWASP Cheat Sheet Series.md", "Logging - OWASP Cheat Sheet Series.md", "Server Side Request Forgery Prevention - OWASP Cheat Sheet Series.md", "Database Security - OWASP Cheat Sheet Series.md", "Docker Security - OWASP Cheat Sheet Series.md", "NPM Security - OWASP Cheat Sheet Series.md", "Secure Cloud Architecture - OWASP Cheat Sheet Series.md", "Secure Code Review - OWASP Cheat Sheet Series.md"]
created: 2026-10-04
updated: 2026-10-04
---

# OWASP Top 10 Checklist

Review checklist organised by the OWASP Top 10 (A01-A10). Split out of [[concepts/owasp-security-checklist]] on 2026-10-04; the hub page keeps the severity scale.

## A01 — Broken Access Control
- Authorization checked on every route/endpoint (not just UI)
- Horizontal privilege escalation: can user A access user B's resources?
- Direct object references validated (IDs in URLs, query params)
- Admin/elevated actions gated by role, not just authenticated state
- CORS configured restrictively; no wildcard `*` on credentialed endpoints

## A02 — Cryptographic Failures
- Sensitive data (PII, tokens, passwords) not stored in plaintext
- Passwords hashed with bcrypt/argon2/scrypt (not MD5/SHA1)
- TLS enforced; no HTTP fallback for sensitive routes
- Secrets not in code, git history, or log output
- Tokens with appropriate expiry; refresh token rotation

## A03 — Injection
- SQL: parameterized queries or ORM only; no string concatenation into queries
- Shell: no user input in exec/spawn/system calls
- Template injection: user input never rendered as template code
- NoSQL: operators like `$where`, `$regex` not constructed from user input

## A04 — Insecure Design
- Business logic: can the normal flow be abused? (negative quantities, skipping steps)
- Rate limiting on auth endpoints, password reset, OTP verification
- Enumeration: error messages don't reveal whether a user exists
- Multi-step processes: each step validates prior step completed

## A05 — Security Misconfiguration
- Default credentials changed; debug endpoints disabled in production
- Error messages sanitized: no stack traces, file paths, or internal details to clients
- Security headers present: CSP, HSTS, X-Frame-Options, X-Content-Type
- Unnecessary features/endpoints/routes disabled

## A06 — Vulnerable Components
- Known CVEs in direct dependencies? (`npm audit`, `pip-audit`, `go mod`)
- Indirect/transitive dependencies not pinned to vulnerable versions

## A07 — Authentication Failures
- Session tokens: sufficient entropy, invalidated on logout, rotated on privilege change
- Brute force: lockout or progressive delay on repeated failures
- Password reset: tokens time-limited, single-use, invalidated after use
- JWT: algorithm verified server-side; `alg: none` rejected; secret not weak
- OAuth/OIDC: state parameter validated; redirect_uri allowlisted

## A08 — Software and Data Integrity
- Deserialization of untrusted data: type-checked before use
- Webhook signatures verified before processing payload
- File uploads: type validated server-side; stored outside webroot

## A09 — Logging and Monitoring
- Auth events logged: login, logout, failures, privilege changes
- Sensitive data excluded from logs (passwords, tokens, PII)
- Log injection: user-controlled input sanitized before logging

## A10 — SSRF
- URL inputs validated against allowlist; no arbitrary external fetches
- Internal metadata endpoints (169.254.x.x, cloud metadata APIs) blocked
- Redirects: open redirects validated against allowlist

## Related Pages

- [[concepts/owasp-security-checklist]] — hub: severity classification and the other OWASP pages
- [[concepts/owasp-web-security-reference]] — stack-agnostic stubs for controls not covered above
- [[concepts/owasp-ai-agent-risks]] — AI-specific risks appended to the Top 10
- [[concepts/ai-code-review]] — broader code review process including security as one layer
