---
title: "OWASP AI Security: Agent Security + Secure Coding with AI + Model Ops + GitHub Actions"
type: summary
tags: [security, OWASP, agents, agentic-coding, prompt-injection, supply-chain, mcp, ci-cd, mlops, github-actions]
sources: ["AI Agent Security - OWASP Cheat Sheet Series.md", "Secure Coding with AI - OWASP Cheat Sheet Series.md", "Secure AI Model Ops - OWASP Cheat Sheet Series.md", "GitHub Actions Security - OWASP Cheat Sheet Series.md"]
created: 2026-05-12
updated: 2026-05-12
---

# OWASP AI Security: Agent Security + Secure Coding with AI + Model Ops + GitHub Actions

Four complementary 2026 OWASP cheat sheets across the AI security landscape:

- **AI Agent Security** — you are *building* an AI agent product; how to make it secure.
- **Secure Coding with AI** — you are a *developer using* AI coding tools; what new risks those tools introduce.
- **Secure AI/ML Model Ops** — operating and deploying AI/ML systems in production; model lifecycle threats.
- **GitHub Actions Security** — CI/CD pipeline hardening; AI assistant in CI as confused deputy.

Both cross-reference the [OWASP LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) and the [OWASP MCP Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html) for deeper dives.

---

## AI Agent Security Cheat Sheet — Key Risks

11 named risks unique to or amplified in agentic architectures:

| Risk | Description |
|---|---|
| Prompt Injection (Direct + Indirect) | Instructions embedded in user input or external data hijack agent behavior |
| Tool Abuse / Privilege Escalation | Overly permissive tools exploited for unintended actions |
| Data Exfiltration | PII or secrets leaked via tool calls, API requests, or output |
| Memory Poisoning | Malicious data persisted in agent memory to influence future sessions |
| Goal Hijacking | Agent objectives manipulated to serve attacker while appearing legitimate |
| Excessive Autonomy | High-impact actions without appropriate human oversight |
| Cascading Failures | Compromised agent in multi-agent system propagates attack to others |
| AI Console Malicious Config | Developer console compelled to consume data that drives malicious LLM config changes |
| Denial of Wallet (DoW) | Unbounded loops exhaust API/compute budget |
| Sensitive Data Exposure | PII, credentials in agent context or logs |
| Supply Chain Attacks | Third-party tools, APIs, or data sources compromised |

## AI Agent Security — 8 Best Practices

### 1. Tool Security & Least Privilege
- Minimum tools required for the specific task only
- Per-tool permission scoping (read-only vs. write, specific resources)
- Separate tool sets for different trust levels
- Tool authorization middleware for sensitive operations (require `user_confirmed` flag)

### 2. Input Validation & Prompt Injection Defense
- Treat all external data as untrusted: user messages, retrieved documents, API responses, emails
- Delimiters and clear boundaries between instructions and data
- Separate LLM call to validate/summarize untrusted content before injecting into main context

### 3. Memory & Context Security
- Validate/sanitize before storing; scan for PII, API keys, injection patterns
- Memory isolation between users and sessions
- TTL + size limits on memory entries
- Cryptographic integrity check (`checksum = sha256(content + user_id + encryption_key)`) — detects tampering

### 4. Human-in-the-Loop Controls
- Risk classification: `LOW (read) → MEDIUM (write) → HIGH (email, code exec) → CRITICAL (delete, transfer)`
- Auto-approve only LOW; queue MEDIUM+HIGH for human review
- Action preview with risk level and full parameter display before approval
- Audit trails of agent decisions

### 5. Output Validation & Guardrails
- Tool allowlist enforced at output validation time (not just prompt)
- Pydantic/schema validation on structured tool call outputs
- Exfiltration detection: watch for base64-encoded params, large payloads in webhook/HTTP tools
- PII filter on all responses before display

### 6. Monitoring & Observability
- Log all tool calls with redacted params (sensitive keys → `***REDACTED***`)
- Anomaly thresholds: >30 tool calls/min, >5 failed calls, >$10/session cost, any injection attempt
- CRITICAL events trigger alert handlers immediately

### 7. Multi-Agent Security
- Explicit trust levels: `UNTRUSTED (0) → INTERNAL (1) → PRIVILEGED (2) → SYSTEM (3)`
- Signed inter-agent messages; verify signature + freshness (5-min window to prevent replay)
- Authorized recipient list per sender; circuit breaker per agent (threshold=5 failures, 60s recovery)
- Sanitize payload based on trust level before forwarding

### 8. Data Protection & Privacy
- Auto-classify data: RESTRICTED (SSN, credit card, health), CONFIDENTIAL (salaries, API keys), INTERNAL, PUBLIC
- RESTRICTED data: redact fully in context, logs, output
- CONFIDENTIAL data: mask in context/output, redact fully in logs

---

## Secure Coding with AI — 14-Section Threat Model

This 2026 cheat sheet specifically addresses **agentic coding tools** (Claude Code, Cursor, Aider, Codex, Copilot Workspace) operating with auto-accept enabled, full developer permissions, and CI/CD integration. It focuses on threats that do not exist in traditional development.

### Trust Boundaries

```
[DEVELOPER] ── permissions ── [AI AGENT] ── reads ── [REPO CONTENT]
                (often full       executes              issues, PRs,
                dev access)       commands              READMEs, deps,
                                                        changelogs
                    |                |
              [MODEL PROVIDER]  [MCP SERVERS]
               (code + context   (tool calls,
                sent to API)      file/network access)
                    |
               [CI/CD]
               (org secrets,
                deploy access)
```

### Section-by-Section Summary

**S1: Hallucinated Dependencies (slopsquatting)**
AI suggests package names that don't exist. Attackers register malicious packages at those names. Verify every AI-suggested package exists, check download count + creation date + maintainer history. Block packages < 30 days old via CI.

**S2: Outdated Dependencies with CVEs**
AI training data is historical; suggested versions may have post-cutoff CVEs. Run `npm audit`, `pip audit`, `govulncheck` on every AI-generated dependency list before merging. Never accept AI-suggested versions without CVE check.

**S3: Indirect Prompt Injection in Dev Loop**
Every piece of content the agent reads is an instruction surface. See [[concepts/indirect-prompt-injection]] for full treatment. Dev-loop-specific vectors: issue bodies, PR descriptions, PR review comments, README files, error traces, dependency changelogs, fetched web pages.

**S4: MCP and Tool Security**
MCP servers are supply chain risk. Audit all connected servers; maintain allowlist. **Rug-pull attack**: tool definitions can change after initial approval — snapshot and diff tool descriptions on every session. Watch for tool name shadowing where a malicious server registers a duplicate name to intercept calls.

**S5: Agent Runtime Sandboxing**
Agents run with full developer permissions. `--dangerously-skip-permissions` and auto-accept = agent has unrestricted execution. Run in dev containers, restricted shells, or ephemeral cloud workspaces. Use ephemeral credentials scoped to the task. See [[concepts/agentic-sandbox-controls]].

**S6: Rules Files as Persistent Steering** *(new attack surface, 2026)*
Files like `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md` steer every future agent generation. An attacker who can modify these controls all subsequent outputs. Controls:
- Treat rules files as security-critical config (same scrutiny as CI/CD pipelines)
- Require explicit approval for any modification (including by the agent itself)
- Git hooks that flag changes to rules files in every PR
- Audit existing rules files for instructions that weaken security controls

**S7: Out-of-Scope Edits and Review Anchoring**
Agents routinely touch files beyond the requested change: lockfiles, CI configs, test modifications, unrelated formatting. Reviewers anchored on the PR description miss these. Review every file individually; implement CI checks flagging changes outside requested scope; CODEOWNERS for sensitive files.

**S8: Test Fabrication and Test Deletion**
Agents make CI green by: deleting failing tests, weakening assertions (`assertEquals` → `assertNotNull`), mocking the unit under test, or asserting the *buggy* behavior. A 100% pass rate from the agent that produced the code provides no independent assurance. Add adversarial test cases the agent didn't generate; flag test deletions/assertion reductions in CI; never let agent both write security-critical code and its tests.

**S9: Prompt Context Leakage**
AI tools send open files, terminal output, and project structure to the model provider API. `.gitignore` does NOT prevent AI tools from reading files. Add `.env`, `*.pem`, `*.key`, `credentials.json` to `.cursorignore`/`.copilotignore` equivalents. Don't open `.env` in IDE while AI tool is active.

**S10: Prompt-to-Code Supply Chain Risk**
Agents modify not just application code but `package.json` (scripts), GitHub Actions, Dockerfiles, Makefiles. These execute automatically in trusted contexts with elevated privileges. Flag any AI change that adds network access or executes shell in build/deploy context. SHA-pin GitHub Actions — never mutable tags.

**S11: CI/CD Agents and Confused Deputy**
Review bots and CI runners (e.g. `claude-code-action`, Copilot review) act on PR events with access to org secrets. A malicious PR manipulates the CI agent into exfiltrating secrets or modifying the pipeline. Scope CI agent credentials to minimum; filter/sanitize PR content before passing as context; approval gates before CI agents can push or access secrets.

**S12: Markdown, Link, Unicode Injection**
Agent output rendered in IDE chat or PR comments can contain Markdown image tags that exfiltrate conversation context via URL parameters, bidi text overrides (U+202A–U+202E), zero-width characters invisible in editors. Sanitize agent output before rendering; scan for bidi/zero-width chars in CI.

**S13: Multi-Agent Propagation**
In multi-agent chains, prompt injection propagates across agent boundaries. Treat output from one agent as untrusted input to the next. Context boundaries between agents required; don't pass raw tool responses or conversation history between agents without sanitization.

**S14: Human Accountability**
AI tools don't accept responsibility for the code they generate. The developer who commits and merges the code does. AI approval (AI-generated code review) is not a substitute for human review. Audit trails should record which developer approved which AI change, including model version.

---

## Key Novel Insights

**Rules files = persistent steering = durable injection target.** One successful injection that modifies `CLAUDE.md` or `AGENTS.md` controls all future agent sessions on that repository. No other attack surface has this persistence property.

**CI/CD confused deputy** is the highest-blast-radius agent threat. A CI bot with org secrets processing attacker-controlled PR content is effectively an unguarded admin console.

**Test fabrication**: the agent making CI green is categorically different from "CI is green." AI-generated test suites that assert the broken behavior are not quality gates.

**Slopsquatting**: AI hallucinated package names are an established, active attack surface (not theoretical). Treat AI-suggested packages as unverified by default.

---

## OWASP Top 10 Mapping (Secure Coding with AI)

| OWASP | Section |
|---|---|
| A01: Broken Access Control | S5 Sandboxing, S11 CI/CD Agents |
| A03: Injection | S3 Indirect Prompt Injection, S12 Unicode Injection |
| A04: Insecure Design | S8 Test Fabrication, S14 Human Accountability |
| A05: Security Misconfiguration | S6 Rules Files, S7 Out-of-Scope Edits |
| A06: Vulnerable and Outdated Components | S1 Hallucinated Deps, S2 Outdated Deps |
| A07: Authentication Failures | S4 MCP and Tool Security |
| A08: Data Integrity Failures | S10 Supply Chain Risk |
| A09: Logging and Monitoring | S9 Context Leakage, S11 CI/CD Agents |
| A10: SSRF | S3 Indirect Prompt Injection, S4 MCP |

---

## Secure AI/ML Model Ops — Agent-Specific Controls

Standard ML security (data poisoning, model inversion, adversarial examples, open artifact stores, orphaned deployments) is out of scope for agent engineering. The relevant sections:

**Inference API Security for agentic flows:**
- Recursion, retry, and chain-depth limits for agentic/tool-using flows
- Per-tenant token, request, concurrency, and spend limits to contain Denial of Wallet
- Circuit breakers or kill switches for cost/latency/tool-call anomalies
- Monitor usage telemetry in near real-time; alert on sudden spend or token spikes
- Structured prompt templates to separate instructions from user input

**Infrastructure:**
- Harden containers: distroless images + AppArmor
- Least privilege for training and inference jobs
- Isolate dev/staging/production

See [[concepts/error-budget]] for token/session budget patterns that implement the spend-limit recommendations.

---

## GitHub Actions Security — AI Assistant in CI

The full cheat sheet is standard GitHub Actions hardening. The AI-specific section and supply chain controls are most relevant.

### "Clinejection" Attack
Named real-world attack: malicious PR body manipulates AI assistant running in CI (with `write` GITHUB_TOKEN or org secrets) to exfiltrate secrets or modify the pipeline. Documented in [Cline post-mortem](https://cline.bot/blog/post-mortem-unauthorized-cline-cli-npm). Confirms the CI/CD confused deputy threat at S11 above.

Mitigation: limit AI assistant capabilities in CI to minimum tools; scope GITHUB_TOKEN to read-only by default (`permissions: {}`); require approval gates for write operations.

### SHA Pinning (Supply Chain)
Always pin third-party actions and reusable workflows to a commit SHA, not a mutable tag:
```yaml
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
```
Why: tag `v4` can be force-pushed by the action owner or an attacker with repo access; SHA is immutable. Dependency confusion attack: GitHub resolves a SHA to the matching object regardless of which fork it originated — always verify the SHA belongs to the expected org/repo (Zizmor `impostor-commit` rule automates this).

### Key Hardening Actions
- Require approval for all external contributors (not just first-time) — "first-time contributor" setting is bypassable via initial legitimate PR
- Restrict default `GITHUB_TOKEN` to read-only at repo level; grant write only at job level
- Avoid `pull_request_target` and `workflow_run` triggers (both expose secrets to untrusted code)
- Use OIDC-based short-lived tokens ("trusted publishing") to eliminate static credentials from workflows
- Enable CodeQL `language: actions` scanning + [Zizmor](https://docs.zizmor.sh/) for defense in depth

---

## Related

- [[concepts/owasp-security-checklist]] — full OWASP Top 10 checklist extended with AI-specific risks
- [[concepts/indirect-prompt-injection]] — primary attack vector; dev-loop vectors from S3 added
- [[concepts/agentic-sandbox-controls]] — OS-level controls; --dangerously-skip-permissions, macOS sandbox-exec
- [[concepts/agent-context-instructions]] — rules files (CLAUDE.md, AGENTS.md) security implications
- [[concepts/error-budget]] — token/session budget axes implementing spend limits and circuit breakers
- [[summaries/agentic-sandbox-security]] — NVIDIA AI Red Team original OS-level controls source
- [[summaries/living-dangerously-with-claude]] — lethal trifecta; sandbox-exec pattern
