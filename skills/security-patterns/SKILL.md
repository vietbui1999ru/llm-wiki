---
name: "security-patterns"
description: "Run a structured OWASP and agent-security review. Use for auth, permissions, data handling, prompt injection, or API review."
---

# Security Patterns

Structured security checklist.

## Review buckets

- broken access control
- cryptographic failures
- injection
- insecure design
- security misconfiguration
- vulnerable dependencies
- authentication failures
- data integrity
- logging and monitoring
- SSRF

## Agent-specific checks

- indirect prompt injection
- excessive tool permissions
- destructive actions without confirmation
- secret leakage via prompts, config, or logs

## Output format

For each finding:

```text
[SEVERITY] Category — Brief description
Location: file:line
Issue: exploit path or failure mode
Fix: concrete remediation
```

## Severity

- Critical
- High
- Medium
- Low
- Info
