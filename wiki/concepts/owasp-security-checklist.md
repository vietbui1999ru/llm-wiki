---
title: "OWASP Security Checklist"
type: concept
tags: [security, OWASP, code-review, checklist, web-security, agents, agentic-coding]
sources: []
created: 2026-04-26
updated: 2026-10-04
---

# OWASP Security Checklist

Structured checklist for web application security review. Based on OWASP Top 10. Applied during code review and security audits. AI-specific risks appended.

The full operational checklist lives in the `security-patterns` skill (preloaded into `security-auditor`). This page is the reference copy for the wiki.

This page is the hub. The checklist was split on 2026-10-04 into topical pages so each stays small and indexable; the 31 OWASP cheat-sheet sources are distributed across them by topic (not as per-claim citations):

- [[concepts/owasp-top-10-checklist]] — A01-A10 review checklist (14 sources)
- [[concepts/owasp-ai-agent-risks]] — indirect prompt injection, sandbox controls, tool/memory security, AI coding tool threats, denial of wallet (6 sources)
- [[concepts/owasp-web-security-reference]] — session management, CSRF, DOM XSS, IDOR, transaction authorization, third-party scripts, deserialization, DoS (11 sources)

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
