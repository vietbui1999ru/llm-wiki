---
title: "Dangeresque"
type: entity
tags: [orchestration, agent-harness, host-native, adversarial-review, worktrees]
sources: ["Are spec-driven frameworks like Agent OS, BMAD, Superpdoms or SpecKit still worth using, or have Claude Code and Codex made them redundant?.md"]
created: 2026-05-04
updated: 2026-05-04
---

# Dangeresque

Host-native CLI orchestrator for Claude Code / Codex. Dispatches headless agents in git worktrees, runs an adversarial AI reviewer, and enforces a human-merge gate before anything lands. Lighter than [[entities/sandcastle]] — no container dependency.

GitHub: https://github.com/slikk66/dangeresque

---

## Design Rationale: Host-Native

Dangeresque is explicitly host-native. Anthropic's Terms of Service restrict using Claude Code subscription keys inside Docker containers. SandCastle works around this via provider abstraction (run Claude on host, sandbox tool execution). Dangeresque avoids the problem entirely: Claude Code runs on the host, worktrees provide task isolation, fine-grained `allowedTools`/`disallowedTools` enforce safety.

This is a direct **policy-driven design decision**, not a technical limitation. See [[concepts/agentic-sandbox-controls]] for the tension between OS-level sandboxing (NVIDIA AI Red Team recommendation) and Anthropic ToS.

---

## Four-Phase Pipeline

```
1. Worker phase
   → headless Claude/Codex in isolated git worktree
   → inherits MCP servers and tools from parent session
   → implements the task, runs tests

2. Verify phase
   → automated checks: tests, types, linting
   → failure here triggers retry or human escalation

3. Review phase
   → adversarial AI reviewer (different model from implementer)
   → reviews diff against coding standards (pushed, not pulled)
   → can block merge with structured feedback

4. Human-merge gate
   → mandatory — no auto-merge regardless of reviewer pass
   → human sees diff + reviewer notes before merge decision
```

The adversarial reviewer is the key differentiator from most orchestrators. Using a different model (e.g., Codex reviews Claude's work) catches single-model blind spots. See [[concepts/multi-vendor-adversarial-review]].

---

## Artifacts

`.dangeresque/runs/` — gitignored directory storing per-run artifacts:
- Worker output logs
- Reviewer notes
- Worktree references

Not committed, not deleted after session — durable enough to reference but not polluting git history. Similar pattern to [[entities/agentops]]'s `.agents/` corpus.

---

## Compared to SandCastle

| Dimension | Dangeresque | SandCastle |
|---|---|---|
| Container dependency | None (host-native) | Docker/Podman/Vercel |
| Adversarial reviewer | Built-in (mandatory) | Optional (reviewer agent) |
| Human merge gate | Mandatory | Configurable |
| Language | CLI (shell-based) | TypeScript library |
| Branch strategy | Single worktree-per-task | head/merge-to-head/branch |
| Complexity | Lower | Higher |

Dangeresque is the lighter-weight choice for individuals; SandCastle for teams or CI/CD integration.

---

## Related Pages

- [[entities/sandcastle]] — heavier alternative with container isolation and branch strategy abstraction
- [[concepts/multi-vendor-adversarial-review]] — the adversarial reviewer pattern
- [[concepts/agentic-sandbox-controls]] — OS-level sandbox recommendation; host-native as ToS-compliant alternative
- [[concepts/agent-harness]] — harness architecture
- [[concepts/ralph-loop]] — minimal harness pattern; Dangeresque adds adversarial review on top
- [[summaries/mattpocockworkflow]] — workflow that Dangeresque implements
