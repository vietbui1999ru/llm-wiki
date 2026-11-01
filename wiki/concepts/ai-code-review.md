---
title: "AI Code Review"
type: concept
tags: [ai-agents, code-review, automation, security, testing]
sources: [Review AI-generated code.md, Build an optimized review process with Copilot.md, General Best Practices for vetting AI Code.md, Automated Security Reviews in Claude Code.md, How the Claude Code team does code review.md]
created: 2026-04-22
updated: 2026-11-01
---

# AI Code Review

> **Contradiction (2026-11-01):** The pages below assume every change gets a human pass that validates intent ("Human review must explicitly validate intent", 8-point checklist). [[summaries/claude-code-team-code-review]] reports the Claude Code team merging *low-risk* changes (docs, copy, internal-only, additive behind a flag) with **zero** human approvals once automated review and security are green, with intent-level human review reserved by a risk classifier for medium/high tiers and sensitive paths. Both can hold: the checklist describes what a human checks *when* one reviews; the newer source argues the question is which check (human or automated) fits each change's risk. That source is a vendor self-report *(claimed, unverified)*.

The practice of reviewing AI-generated code — and using AI agents to assist in that review. Requires a different lens than reviewing human code: mechanical correctness is often high, but intent alignment and AI-specific failure modes require explicit attention.

## Review pipeline

**Automated layer (agent or CI):**
- Static analysis, linters, security scanners (CodeQL equivalent)
- Automated agent review against context/standards document
- Dependency checks (license, maintenance, existence)
- Test execution

**Human layer:**
- Intent verification: does this solve the right problem?
- Architecture fit: does this match existing patterns?
- AI-specific pitfall scan: see [[concepts/ai-specific-pitfalls]]
- Domain logic correctness

## 8-point human checklist

1. Tests pass, static analysis clean
2. Code solves the stated problem (not just compiles)
3. Fits project architecture and conventions
4. Readable, maintainable, clear naming
5. Dependencies exist, are maintained, licenses compatible
6. No AI-specific pitfalls (hallucinated APIs, deleted tests, missed edge cases)
7. Security: data flows traced, injection/auth reviewed
8. Complex/sensitive changes get a second human reviewer

## Automated review with context instructions

Agent-based automated review quality is gated by [[concepts/agent-context-instructions]] quality. With good context: agent catches style violations, missing error handling, security patterns, performance issues — freeing human review for design and correctness.

Example: SHA-256 flagged as insecure for password hashing (too fast → brute-force vulnerable); agent suggests argon2 (slow, built-in salt). Human reviews and applies.

## Static analysis thresholds

Before human review: Code Health >9.5 (SonarQube or equivalent). Demand unit test coverage ≥99% for new code; reject if tests are deleted or mocked to hide issues. Label AI-generated code explicitly in PR metadata.

## Self-reviewing agent

Build a pre-human-review agent: runs automatically on PR open, checks against team standards (accuracy, tone, business logic), surfaces issues before human review begins. Frees human reviewers from surface-level catches.

## Claude Code `/security-review`

Built-in command — runs in-project, no custom agent needed. Analyzes for SQL injection, XSS, auth/authorization flaws, insecure data handling, dependency vulnerabilities. Can implement fixes inline after finding issues.

GitHub Actions integration: `anthropics/claude-code-security-review` automatically reviews every PR on open. Posts inline PR comments with findings and recommended fixes. Configurable filtering rules to reduce false positives and per-vulnerability-type sensitivity.

Recommendation: wire `/security-review` into project hook template (pre-commit on significant changes). For pre-deploy audits, or when a review escalates, run a read-only security-review pass on an Opus-tier model (define a custom subagent only if the job repeats; none is installed here, see [[concepts/model-tier-routing]]).

## Review at agent volume: the Claude Code team's practice (2026)

From [[summaries/claude-code-team-code-review]] (vendor article; all numbers *(claimed, unverified)*). What it adds to the pipeline above:

- **Optimize for human time, guard with reverts.** Track human approvals per PR (median, p95), human comments and wait-on-person time; revert and incident rates are the guardrail. Cutting review time that reappears as fix time is not a saving.
- **Review before the PR exists.** The authoring agent must show test/build/lint output, then a subagent reviews the diff in a fresh context. Review becomes continuous rather than an end gate.
- **Parallel finders plus verifier voting.** Several agents hunt bugs; a separate group votes on each finding; only agreed findings post. Style/cleanup-only findings are dropped. Tags: Important, Nit, Pre-existing. Every finding must be fixed or resolved with a reason; open bug or security findings block merge.
- **`REVIEW.md` per code owner:** short, states what failure looks like in that area, caps nits, lists paths to skip, demands file-and-line evidence, and asks for a count-first summary that says plainly when there is nothing to fix. Recurring findings get fixed at the source (skill, lint rule, `CLAUDE.md`, `REVIEW.md`), not re-flagged forever.
- **Risk tiers set by the change, not the author:** a classifier assigns 0 / 1 / 2 human approvals; a second classifier can override upward; sensitive paths and CI workflow files always need a person; lighter paths only for trusted authors; a bot approval never fills a human slot; approvals are pinned to a commit; the person who prompted an agent-written PR counts as a required reviewer.
- **Convergence rules for agent-vs-agent loops:** one PR ran 50+ overnight rounds; about 59% of repeated flags were on code present since round one. Fixes: cap at three rounds then ask the author to rethink the approach, diff-only re-review after the first passes, flag the bug *class*, never repeat a posted finding. Reported mean reviews to pass fell from 2.08 to 1.32.
- **Measure noise by human response** (fixed / wrong / intentional / did not matter) and by false reports on known-clean PRs. Noise costs more with agent authors, which fix every nit and trigger another round.
- **Incidents become a daily eval** for the reviewer; any prompt, tool or model change is kept only if the score rises.
- **Downstream layers carry the rest:** merge queue, feature flags, internal dogfooding, staged channels, fast rollback. Admitted gap: no circuit breaker yet that tightens approval when revert rates rise.

## Continuous improvement

Document successful prompts and effective context patterns. Update onboarding guides. Feed recurring review findings into the slop register (see [[concepts/ai-specific-pitfalls]]).

## The core risk

AI code can be syntactically correct, pass tests, and match style — while being *wrong* because it made incorrect assumptions about business logic or user intent. Human review must explicitly validate intent, not just correctness.

## Related

- [[summaries/claude-code-team-code-review]] — layered review, risk-tiered approval and convergence rules at agent volume
- [[systems/agent-review]] — the user's per-run human gate for Pi, compared with that practice
- [[concepts/ai-specific-pitfalls]] — failure modes unique to AI-generated code
- [[concepts/agent-context-instructions]] — how context documents improve automated review quality
- [[entities/ai-coding-agents]] — the agents producing and reviewing code
- [[concepts/owasp-security-checklist]] — full OWASP Top 10 + AI-specific security checklist for deep audits
- [[entities/codegraphcontext]] — relationship-aware review: use CGC to find callers and blast radius before flagging cross-module changes
