Best practices for humans vetting agentic/AI-generated code from a session focus on skepticism, automation, and strategic review. Prioritize readability, security, and tests before accepting.codescene+1

## Preparation

Run static analysis (SonarQube, linters) first for complexity/security. Check Code Health >9.5; refactor if low.[exceeds](https://blog.exceeds.ai/assess-pr-code-ai-tools/)

## Readability Check

Verify descriptive names, short functions (<50 lines), no deep nesting. Ensure self-documenting; minimal comments.github+1

## Logic/Security

Trace data flows manually; hunt injections, auth bypasses. Confirm architecture fit, no isolated solutions.[thevirtualforge](https://www.thevirtualforge.com/company/blog/ai-generated-code-needs-human-oversight-how-to-validate-and-secure-ai-powered-development)

## Tests/Coverage

Demand unit tests (99%+ coverage), E2E verification. Run them; reject deletions or mocks hiding issues.

## Accept Criteria

Small changes only; label AI-generated. Approve if maintainable, compliant; iterate with agent on fixes.augmentcode+1