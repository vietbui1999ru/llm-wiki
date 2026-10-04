---
title: "OWASP Web Security Reference"
type: concept
tags: [security, OWASP, web-security, reference, stubs]
sources: ["Session Management - OWASP Cheat Sheet Series.md", "Cross-Site Request Forgery Prevention - OWASP Cheat Sheet Series.md", "DOM based XSS Prevention - OWASP Cheat Sheet Series.md", "Insecure Direct Object Reference Prevention - OWASP Cheat Sheet Series.md", "Transaction Authorization - OWASP Cheat Sheet Series.md", "Third Party Javascript Management - OWASP Cheat Sheet Series.md", "Deserialization - OWASP Cheat Sheet Series.md", "Denial of Service - OWASP Cheat Sheet Series.md", "Content Security Policy - OWASP Cheat Sheet Series.md", "Cross Site Scripting Prevention - OWASP Cheat Sheet Series.md", "AJAX Security - OWASP Cheat Sheet Series.md"]
created: 2026-10-04
updated: 2026-10-04
---

# OWASP Web Security Reference

Stack-agnostic stubs for web controls the Top 10 checklist does not cover in depth. Split out of [[concepts/owasp-security-checklist]] on 2026-10-04. Expand to dedicated pages when targeted sources are ingested.

**Session Management**: min 128-bit entropy tokens, `HttpOnly`, `Secure`, `SameSite=Strict`; invalidate on logout server-side; rotate on privilege change; never in URL parameters.

**CSRF**: synchronizer token pattern or `SameSite=Strict` cookies; verify `Origin`/`Referer` headers; custom request headers as secondary defense; exempt GET/HEAD/OPTIONS (must be idempotent).

**DOM-Based XSS**: untrusted sources include `document.URL`, `location.hash`, `document.referrer`, `postMessage`; dangerous sinks include raw HTML setters and eval; never pass untrusted source to dangerous sink without DOMPurify.

**IDOR**: validate authenticated user owns the requested resource; map internal IDs to per-user opaque tokens; log access denials; scope queries to user_id — never fetch by id alone.

**Transaction Authorization**: re-authenticate for high-value actions (account deletion, payment); idempotency keys for financial transactions; audit log of all state-changing operations with before/after values.

**Third-Party Scripts**: Subresource Integrity (SRI) for CDN-hosted scripts; CSP to allowlist script sources; audit third-party scripts for data exfiltration risk.

**Deserialization**: never deserialize untrusted data directly into objects; validate type before deserializing; use schema validation (zod, joi) on JSON.parse results; sign serialized tokens.

**DoS**: rate limit all public endpoints (especially auth, search, file upload); request size limits; avoid regex backtracking (ReDoS); connection timeouts.

## Related Pages

- [[concepts/owasp-security-checklist]] — hub: severity classification and the other OWASP pages
- [[concepts/owasp-top-10-checklist]] — the classic Top 10 review checklist
