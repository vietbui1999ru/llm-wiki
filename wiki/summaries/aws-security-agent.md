---
title: "AWS Security Agent — Penetration Testing Service"
type: summary
tags: [security, penetration-testing, aws, managed-service, pentest]
sources: ["Create a penetration test - AWS Security Agent.md"]
created: 2026-05-21
updated: 2026-05-21
---

# AWS Security Agent — Penetration Testing Service

Managed AWS service for automated web application penetration testing. Operates against verified domains; no self-hosting required. Relevant as a reference for scope control patterns, not as a component to build.

## What It Is

AWS Security Agent is a console-configured pen testing service. You define scope, provide credentials, and it runs a test suite against your verified domains. Output: structured vulnerability findings. Optional: auto-remediation via PRs to your GitHub repos.

## Key Design Patterns Worth Borrowing

### Target vs. Accessible Domains Split

Critical distinction — two domain categories:

- **Target domains**: actively tested for vulnerabilities (must be verified)
- **Accessible domains**: third-party services the agent can *navigate through* but NOT attack (e.g., Okta, Auth0, Stripe for login flows)

Directly applicable to our agent: Neon, Namecheap, any OAuth provider must be listed as accessible — not targeted.

### Out-of-Scope URL Paths

Hierarchical exclusion: exclude `/admin/delete` → also excludes `/admin/delete/confirm`. Prefix-based, not exact-match. Prevents destructive test actions against known-dangerous paths.

### Credential Injection Patterns

Three methods:
1. Direct input (dev/test only)
2. AWS Secrets Manager reference (prod recommended)
3. Lambda function (custom auth flows)

Agent login prompt: freeform instructions for complex auth flows ("Navigate to /login, enter username in 'Email' field, click 'Sign In'"). Useful when the auth flow is non-standard.

### IAM Role Scope for Testing

Test runs under a scoped IAM role — not your default credentials. Role needs: VPC access, CloudWatch Logs write. Principle: minimum permissions for test execution.

### Scope Lock Before Execution Checklist

AWS Security Agent enforces a review gate before launch:
- All target domains verified and accessible
- IAM roles have correct permissions
- Destructive paths excluded from scope
- Authorization confirmed for all target domains

## What It Doesn't Do

- No CLI/programmatic control — console only
- No custom tool integration (wraps AWS's own test suite)
- No cross-account testing without explicit IAM trust
- VPC config required for private (non-public) applications

## Stack Requirements

- Domain verification via AWS console prerequisite
- IAM role with `securityagent` trust relationship
- CloudWatch log group (auto-created if not specified)

## Related Pages

- [[concepts/pentest-agent-design]] — our custom agent design, borrowing these patterns
- [[entities/pentagi]] — OSS autonomous pen testing system; compare architecture
- [[concepts/owasp-security-checklist]] — vuln categories the agent tests against
