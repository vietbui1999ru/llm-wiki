---
title: "Claude Code Auto Mode"
type: summary
tags: [claude-code, permissions, security, auto-mode, classifier, prompt-injection]
sources:
  - "Claude Code auto mode a safer way to skip permissions.md"
  - "Configure permissions.md"
created: 2026-05-07
updated: 2026-05-07
---

# Claude Code Auto Mode

Auto mode is a permission mode between `default` (manual approval) and `bypassPermissions` (no guardrails). It delegates approval decisions to model-based classifiers instead of humans, catching dangerous overeager actions while letting safe actions run freely.

Source: Anthropic engineering blog.

---

## Threat Model

Four causes of dangerous agent actions:
1. **Overeager behavior** — agent understands the goal but acts beyond authorization
2. **Honest mistakes** — agent misunderstands blast radius (thinks a resource is test-scoped)
3. **Prompt injection** — adversarial instructions in tool outputs hijack the agent
4. **Misaligned model** — agent pursues its own goal (rare; evaluated at each release)

---

## Architecture: Two Layers

**Input layer (prompt injection probe):** Scans tool outputs (file reads, web fetches, shell output) before they enter context. Adds warning when content looks like hijack attempt.

**Output layer (transcript classifier):** Evaluates each tool call before execution.

```
User request → Tier 1 (safe-tool allowlist) → Tier 2 (in-project file ops) → Tier 3 (transcript classifier)
```

**Tier 1 — built-in allowlist**: file reads, grep, glob, code navigation, todo, plan mode transitions. Broad interpreter rules (Python `*`, node `*`) are dropped on entering auto mode.

**Tier 2 — in-project file writes**: Allowed without classifier call. Reviewable via version control.

**Tier 3 — transcript classifier**: Everything else: shell commands, web fetches, external tools, subagent spawns, filesystem ops outside project directory.

---

## Two-Stage Classifier

Stage 1: fast single-token yes/no filter, tuned to err toward blocking (8.5% FPR).
Stage 2: chain-of-thought reasoning, runs only when Stage 1 flags (reduces FPR to 0.4%).

Stage 2 uses almost identical prompt to Stage 1 → mostly cache-hit, low extra cost.

**What the classifier sees**: user messages + tool calls only. Assistant prose and tool results are stripped.
- Stripping assistant text prevents the agent from talking the classifier into a bad call
- Stripping tool results blocks prompt-injection payload from reaching the classifier

---

## Default Block Categories

- **Destroy or exfiltrate**: force-push, mass-delete cloud storage, send internal data externally
- **Degrade security posture**: disable logging, install SSH keys/cronjobs, modify own permission config
- **Cross trust boundaries**: run cloned external code, scan credential stores, send data to unspecified services
- **Bypass review or affect others**: push to main, prod deploys, modify shared infra

**Default allow exceptions**: install packages already in repo manifest, standard credential flows, push to session's working branch.

---

## Performance (Evaluated on Real Data)

| Dataset | Stage 1 FPR/FNR | Full Pipeline FPR/FNR |
|---|---|---|
| Real traffic (n=10,000) | 8.5% FPR | 0.4% FPR |
| Real overeager actions (n=52) | 6.6% FNR | 17% FNR |
| Synthetic data exfil (n=1,000) | 1.8% FNR | 5.7% FNR |

17% FNR on real overeager actions is the honest number. Classifier correctly identifies the danger but misreads whether the user's consent actually covers the blast radius. Not a drop-in replacement for careful human review on high-stakes infra.

---

## Multi-Agent Behavior

Classifier runs at both ends of a subagent handoff:
- **Outbound**: catches agent-initiated delegation that looks authorized inside subagent but wasn't from user
- **Return**: reviews subagent's full action history before results go back to orchestrator; prepends security warning if flagged (doesn't discard results)

---

## Deny-and-Continue

When classifier blocks: denial returned as tool result + instruction to find safer path. After 3 consecutive denials or 20 total: escalate to human (or terminate in headless `-p` mode).

False positives cost one retry, not a killed session. This is what makes 0.4% FPR survivable in long-running tasks.

---

## Related Pages

- [[summaries/claude-code-permissions-settings]] — full permissions schema
- [[concepts/agentic-sandbox-controls]] — sandbox as complementary layer
- [[concepts/indirect-prompt-injection]] — what the input-layer probe defends against
- [[concepts/context-degradation]] — why stripping tool results from classifier input improves accuracy
