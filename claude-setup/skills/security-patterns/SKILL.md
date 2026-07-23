---
name: security-patterns
description: Load the security review checklist and OWASP patterns. Invoke during code review when security analysis is needed, when auditing auth/authz code, or when reviewing APIs and data handling.
allowed-tools: "Read,Grep,Bash"
---

# Security Patterns

Structured security review checklist. Work through each category systematically.

## OWASP Top 10 Checklist

### A01 — Broken Access Control
- [ ] Authorization checked on every route/endpoint (not just UI)
- [ ] Horizontal privilege escalation: can user A access user B's resources?
- [ ] Direct object references validated (IDs in URLs, query params)
- [ ] Admin/elevated actions gated by role, not just authenticated state
- [ ] CORS configured restrictively; no wildcard `*` on credentialed endpoints

### A02 — Cryptographic Failures
- [ ] Sensitive data (PII, tokens, passwords) not stored in plaintext
- [ ] Passwords hashed with bcrypt/argon2/scrypt (not MD5/SHA1)
- [ ] TLS enforced; no HTTP fallback for sensitive routes
- [ ] Secrets not in code, git history, or log output
- [ ] Tokens with appropriate expiry; refresh token rotation

### A03 — Injection
- [ ] SQL: parameterized queries or ORM only; no string concatenation into queries
- [ ] Shell: no user input in exec/spawn/system calls
- [ ] Template injection: user input never rendered as template code
- [ ] LDAP/XML/XPath: inputs sanitized before use in queries
- [ ] NoSQL: operators like `$where`, `$regex` not constructed from user input

### A04 — Insecure Design
- [ ] Business logic: can the normal flow be abused? (negative quantities, skipping steps)
- [ ] Rate limiting on auth endpoints, password reset, OTP verification
- [ ] Enumeration: error messages don't reveal whether user exists
- [ ] Multi-step processes: each step validates prior step completed

### A05 — Security Misconfiguration
- [ ] Default credentials changed; debug endpoints disabled in production
- [ ] Error messages sanitized: no stack traces, file paths, or internal details to clients
- [ ] Security headers present: CSP, HSTS, X-Frame-Options, X-Content-Type
- [ ] Unnecessary features/endpoints/routes disabled

### A06 — Vulnerable Components
- [ ] Known CVEs in direct dependencies? (check `npm audit`, `pip-audit`, `go mod`)
- [ ] Indirect/transitive dependencies not pinned to vulnerable versions
- [ ] Outdated dependencies with security patches available

### A07 — Authentication Failures
- [ ] Session tokens: sufficient entropy, invalidated on logout, rotated on privilege change
- [ ] Brute force: lockout or progressive delay on repeated failures
- [ ] Password reset: tokens time-limited, single-use, invalidated after use
- [ ] JWT: algorithm verified server-side; `alg: none` rejected; secret not weak
- [ ] OAuth/OIDC: state parameter validated; redirect_uri allowlisted

### A08 — Software and Data Integrity
- [ ] Deserialization of untrusted data: type-checked before use
- [ ] Webhook signatures verified before processing payload
- [ ] File uploads: type validated server-side, not just MIME; stored outside webroot

### A09 — Logging and Monitoring
- [ ] Auth events logged: login, logout, failures, privilege changes
- [ ] Sensitive data excluded from logs (passwords, tokens, PII)
- [ ] Log injection: user-controlled input sanitized before logging

### A10 — SSRF
- [ ] URL inputs validated against allowlist; no arbitrary external fetches
- [ ] Internal metadata endpoints (169.254.x.x, cloud metadata APIs) blocked
- [ ] Redirects: open redirects validated against allowlist

## AI-Specific Security Risks

From [[summaries/agentic-sandbox-security]]:

### Indirect Prompt Injection
- [ ] Agent reads external content (URLs, files, emails)? → treat as untrusted
- [ ] External content can't override system instructions or trigger tool calls
- [ ] Sandboxed: agent can't exfiltrate data via unexpected network calls

### Agentic Sandbox Controls
- [ ] Tool permissions minimal: only what the task requires
- [ ] Destructive operations (delete, overwrite) require explicit confirmation
- [ ] Secrets injected at runtime, not baked into prompts or config

## Memory Poisoning (Agentic Memory Tool)

Memory files are read back into Claude's context — they are a prompt injection vector.

- [ ] Memory stored per-project in isolated dirs (`/memories/<project>/`) — not globally shared
- [ ] Content sanitized before storing (strip markdown-instruction patterns)
- [ ] Memory writes logged — audit trail for unexpected stores
- [ ] System prompt explicitly tells agent to ignore instruction-like content in memory files
- [ ] Review memory files before sensitive operations if external input could have written them

Source: [[concepts/agentic-memory-tool]]

## MCP Security Controls

- [ ] Tool definitions hash-pinned (SHA-256 over canonical JSON of name + description + input schema) at discovery time — rehash before execution; mismatch = reject and alert
- [ ] Cross-server tool shadowing checked: two servers with identical tool names is a conflict; block the later-registered one
- [ ] Run `mcp-scan` before installing or trusting a new MCP server — detects poisoned descriptions and shadowing
- [ ] MCP server source reviewed before installation — treat like a software package (see [[concepts/indirect-prompt-injection]] supply-chain risk)
- [ ] Tool descriptions from external sources (user-provided URLs, dynamic registration) treated as untrusted input

Source: [[concepts/indirect-prompt-injection]]

## Severity Classification

| Level | Criteria | Action |
|---|---|---|
| **Critical** | Auth bypass, SQL injection, RCE, secret exposure | Block; fix before merge |
| **High** | Missing auth check, IDOR, stored XSS, path traversal | Block; fix before merge |
| **Medium** | Rate limiting missing, open redirect, verbose errors | Fix in follow-up PR |
| **Low** | Missing security headers, minor info leakage | Fix when convenient |
| **Info** | Improvement suggestions, defense-in-depth additions | Optional |

## Output Format for Findings

For each finding:
```
[SEVERITY] Category — Brief description
Location: file:line
Issue: What the vulnerability is and how it can be exploited
Fix: Specific remediation
```
