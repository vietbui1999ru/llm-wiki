---
title: "OWASP Web Security Cheat Sheets — Batch Stubs"
type: summary
tags: [security, OWASP, web-security, reference, next-js, sql, session, docker, aws]
sources:
  - "Authorization - OWASP Cheat Sheet Series.md"
  - "Content Security Policy - OWASP Cheat Sheet Series.md"
  - "Cross Site Scripting Prevention - OWASP Cheat Sheet Series.md"
  - "Cross-Site Request Forgery Prevention - OWASP Cheat Sheet Series.md"
  - "Database Security - OWASP Cheat Sheet Series.md"
  - "Docker Security - OWASP Cheat Sheet Series.md"
  - "Insecure Direct Object Reference Prevention - OWASP Cheat Sheet Series.md"
  - "Injection Prevention - OWASP Cheat Sheet Series.md"
  - "NPM Security - OWASP Cheat Sheet Series.md"
  - "OS Command Injection Defense - OWASP Cheat Sheet Series.md"
  - "Secrets Management - OWASP Cheat Sheet Series.md"
  - "Secure Cloud Architecture - OWASP Cheat Sheet Series.md"
  - "Server Side Request Forgery Prevention - OWASP Cheat Sheet Series.md"
  - "Session Management - OWASP Cheat Sheet Series.md"
  - "SQL Injection Prevention - OWASP Cheat Sheet Series.md"
  - "Vulnerable Dependency Management - OWASP Cheat Sheet Series.md"
  - "Denial of Service - OWASP Cheat Sheet Series.md"
  - "Error Handling - OWASP Cheat Sheet Series.md"
  - "GitHub Actions Security - OWASP Cheat Sheet Series.md"
  - "Logging - OWASP Cheat Sheet Series.md"
  - "Deserialization - OWASP Cheat Sheet Series.md"
  - "Transaction Authorization - OWASP Cheat Sheet Series.md"
  - "Secure Code Review - OWASP Cheat Sheet Series.md"
  - "DOM based XSS Prevention - OWASP Cheat Sheet Series.md"
  - "AJAX Security - OWASP Cheat Sheet Series.md"
  - "Third Party Javascript Management - OWASP Cheat Sheet Series.md"
created: 2026-05-21
updated: 2026-05-21
---

# OWASP Web Security Cheat Sheets — Batch Stubs

Batch ingest of OWASP Cheat Sheet Series reference docs. Organized by relevance to Next.js + ECS Fargate + Neon + ALB stack. Expand individual sections to dedicated pages when a targeted source is ingested.

*Stub — expand individual sections into dedicated pages when needed.*

## Critical for Next.js + Neon Stack

### SQL Injection Prevention
Parameterized queries only. Never concatenate user input into SQL strings. For Postgres/Neon: use `$1, $2` placeholders in pg driver, or ORM (Prisma, Drizzle). Second-order injection: sanitize stored data before re-using in queries. Detection tool: sqlmap.

### Session Management
Secure session tokens: min 128-bit entropy, `HttpOnly`, `Secure`, `SameSite=Strict`. Invalidate on logout (server-side). Rotate on privilege change (login, role elevation). Never in URL parameters. Next.js: verify next-auth session tokens follow these rules.

### Cross-Site Request Forgery (CSRF) Prevention
Synchronizer token pattern or `SameSite=Strict` cookies. For Next.js API routes: verify `Origin`/`Referer` headers. Custom request headers (e.g., `X-Requested-With`) as secondary defense. Exempt: `GET`, `HEAD`, `OPTIONS` (must be idempotent).

### Cross-Site Scripting (XSS) Prevention
Output encoding at render time. Next.js/React auto-escapes HTML in JSX — risk areas are raw HTML injection props and head tag injection. Content Security Policy as defense-in-depth. Avoid legacy DOM mutation APIs that interpret strings as HTML.

### DOM-Based XSS Prevention
Untrusted sources: `document.URL`, `location.hash`, `document.referrer`, `postMessage`. Dangerous sinks: raw HTML setters, eval, and similar string-to-code paths. Never pass untrusted source to dangerous sink without sanitization. DOMPurify for unavoidable client-side HTML rendering.

### Authorization
Every endpoint checks authorization server-side — not just UI. Positive model: deny by default, explicitly allow. Horizontal check: can user A access user B's resource? Verify by resource ownership, not just authenticated state. Next.js: middleware or per-route checks, not client-side redirect-only.

### Insecure Direct Object Reference (IDOR) Prevention
Validate that authenticated user owns the requested resource. Map internal IDs to per-user opaque tokens. Log access denials. Next.js API routes: always scope queries to `user_id` — never fetch by `id` alone.

## Infrastructure / AWS

### Docker Security
Run as non-root user. Read-only filesystem where possible. No secrets in ENV vars in Dockerfile — use Secrets Manager. Minimal base image (distroless/alpine). Drop capabilities. Scan images with Trivy. ECS Fargate: task definition must not have `privileged: true`.

### Secure Cloud Architecture
Defense in depth: VPC isolation, security groups (least-privilege ingress), no open-to-world ingress except ALB port 443. Private subnets for ECS tasks. Secrets in AWS Secrets Manager, not env vars. CloudTrail enabled. IMDSv2 only. No public S3 buckets unless intentional.

### Secrets Management
Never in code, git history, or plaintext env vars. AWS hierarchy: Secrets Manager > Parameter Store > env vars. Rotation: automated for DB passwords. Access via IAM role for ECS task, not long-lived access keys. Scan git history for leaks (trufflehog, gitleaks).

### GitHub Actions Security
OIDC for AWS auth — no long-lived access keys in secrets. Pin action versions to commit SHA or tagged release, not `@main`. `GITHUB_TOKEN` scoped to minimum. No secrets in log output. Sanitize untrusted input before passing to expression contexts. See [[concepts/owasp-security-checklist]] CI/CD section.

## Application-Level

### Injection Prevention
Never construct commands or queries from raw user input. Parameterize everything. Next.js risk: shell injection via child_process with user data, LDAP injection, XML injection via parsers.

### OS Command Injection Defense
Never pass user input directly to exec/spawn/system calls. If shell commands needed: allowlist valid arguments, never pass raw input. Prefer language APIs over shell. High risk in Next.js server actions that invoke system tools.

### Server-Side Request Forgery (SSRF) Prevention
Validate and allowlist URLs before server-side fetching. Block internal IP ranges: AWS metadata endpoint (169.254.x.x), RFC1918 ranges. Disable or validate HTTP redirects. Next.js: server components and server actions that call `fetch()` with user-supplied URLs are SSRF vectors.

### Error Handling
Never expose stack traces, file paths, or internal details to clients. Log details server-side; return generic message to client. Next.js: custom error pages, never surface raw error objects. Avoid timing differences between error types (timing oracle).

### Logging
Log: auth events (login, logout, failures), access control denials, input validation failures. Do NOT log: passwords, tokens, PII, full request bodies with sensitive fields. Use structured JSON logging. Forward to external sink (CloudWatch) — local-only logs are insufficient.

## Dependency / Supply Chain

### NPM Security
`npm audit` on every install. Commit lock file. Verify package names before installing (typosquatting). Minimize devDependencies in production image. Pin versions in package.json for reproducibility.

### Vulnerable Dependency Management
Track CVEs: `npm audit`, Dependabot, Snyk. Update policy: critical within 24h, high within 1 week. Include transitive dependencies. AI-suggested packages: verify registry existence and creation date — see slopsquatting in [[concepts/owasp-security-checklist]].

## Advanced / Reference

### Denial of Service Prevention
Rate limit all public endpoints (especially auth, search, file upload). Set request size limits. Connection timeouts. Avoid regex backtracking (ReDoS). Async processing for expensive operations. ALB: health check tuning, connection draining.

### Deserialization
Never deserialize untrusted data directly into objects. Validate type before deserializing. Use schema validation (zod, joi) on JSON.parse results. Sign serialized tokens. Avoid language-native object serialization of user-supplied data.

### Transaction Authorization
Re-authenticate for high-value actions (account deletion, payment). Step-up auth patterns. Idempotency keys for financial transactions. Audit log of all state-changing operations with before/after values.

### AJAX Security
Enforce same-origin for XHR. Avoid JSONP. Validate Content-Type on POST. CORS: explicit allowlist, never wildcard on credentialed requests.

### Third-Party JavaScript Management
Subresource Integrity (SRI) for CDN-hosted scripts. CSP to allowlist script sources. Audit third-party scripts for data exfiltration risk. Next.js: use the built-in Script component with explicit loading strategy.

### Secure Code Review
Review order: auth, input validation, crypto, error handling, logging. Automated: SAST (Semgrep, ESLint security rules). Manual: business logic, auth flows, trust boundaries. See [[concepts/ai-code-review]] for AI-assisted review patterns.

## Related Pages

- [[concepts/owasp-security-checklist]] — operational checklist (OWASP Top 10 + AI risks)
- [[summaries/owasp-ai-security]] — AI agent security (OWASP 2026)
- [[summaries/owasp-mcp-security]] — MCP-specific security
- [[concepts/pentest-agent-design]] — agent that tests for these vulnerabilities
