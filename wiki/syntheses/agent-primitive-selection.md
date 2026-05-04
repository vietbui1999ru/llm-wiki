---
title: "Agent Primitive Selection"
type: synthesis
tags: [agent-engineering, orchestration, skills, subagents, teams, model-routing]
sources: ["Claude runaway... tried Kimi 2.6 and Deepseek v4 (5y fullstack dev).md"]
created: 2026-04-26
updated: 2026-05-04
---

# Agent Primitive Selection

Distilled from [[concepts/agent-skills]], [[concepts/agent-subagents]], [[concepts/agent-teams]], and the `agent-orchestration` skill. Answers the question: given a task, which primitive do you reach for?

## Decision Tree

```
Is the domain knowledge reusable across sessions and fits in prompts?
  → SKILL

Is it a reusable workflow but too complex for a single prompt?
  → SUBAGENT

Does the task pollute main context but results are all that matter?
  → SUBAGENT (foreground)

Can it run concurrently without blocking the main session?
  → SUBAGENT (background)

Do workers need to talk to each other?
  → No:  SUBAGENTS (each reports only to parent)
  → Yes: AGENT TEAM (shared task list + mailbox)

Is work genuinely parallel with non-overlapping file scope (3–5 pieces)?
  → AGENT TEAM
  → Otherwise: single session or sequential subagents
```

## Model Tier Routing

### Claude Code (wshobson tier routing)

| Model | When to use | Example agents |
|---|---|---|
| **Opus** | Judgment, design, architecture, security audits | design-explorer, architecture-reviewer, security-auditor |
| **Sonnet** | Implementation, review, debugging, deployment | code-writer, code-reviewer, backend-debug-tester |
| **Haiku** | Fast, repetitive, low-judgment | cmd-executor, code-writer-fast, session-report-generator |

**Rule**: Security and architectural decisions go to Opus. Per wshobson benchmarks, Opus achieves 65% fewer tokens on complex tasks — the higher rate is often offset by not needing correction loops.

### OpenCode / multi-provider (community consensus, r/opencodeCLI 2026-05)

| Role | Model | Notes |
|---|---|---|
| Planning / council / architecture | Opus 4.7, GLM-5.1 | Opus for judgment; GLM-5.1 for planning via Go plan |
| Implementation (AFK loop) | DeepSeek V4 Flash (max reasoning) | Direct API only — resellers strip reasoning effort |
| Implementation (Go plan) | GLM-5.1 | Community: lower hallucination than Kimi K2.6 |
| Fast targeted changes | DeepSeek V4 Flash, Qwen 3.6 Plus | Speed + cost |
| Adversarial review | DeepSeek V4 Pro, Qwen 3.6 Plus | Different training = different blind spots |
| UI / frontend | Kimi K2.6, Gemini | Visual reasoning strength |
| Spec writing | Mimo 2.5 Pro | Community: Opus-comparable for spec tasks |

**Key insight**: DeepSeek V4 Flash on max reasoning = dramatically better than default. Must use direct DeepSeek API — not OpenRouter or resellers. Toggle in OpenCode via `ctrl+t`.

**Opus-as-orchestrator pattern** (vietphi, r/opencodeCLI): use Opus to generate a bash script that dynamically dispatches the right model per task, capping expensive models by quota (e.g. GLM at 15%). Moves routing from static env config to agent judgment.

## Skill vs Subagent vs Team — At a Glance

| Dimension | Skill | Subagent | Agent Team |
|---|---|---|---|
| Own context window | No (injected into caller) | Yes | Yes (each teammate) |
| Persists state | No | No (unless writes files) | Via shared task list |
| Parallel execution | No | With `background: true` | Yes (inherent) |
| Inter-worker comms | N/A | None (parent only) | Mailbox |
| Isolation | No | Optional (`isolation: worktree`) | Per-teammate scope |
| Use for | Domain knowledge, checklists | Delegated tasks | Parallel cross-domain work |

## When NOT to Use a Team

- File scope overlaps between teammates → conflicts, merge pain
- Fewer than 3 independent pieces → subagents or sequential is simpler
- Workers need to coordinate mid-task → star topology breaks down; redesign
- Tight iteration loop with human → team coordination latency kills UX

Unstructured "bags of agents" amplify errors 17.2x. Coordination failures account for 36.9% of all multi-agent failures. See [[concepts/agent-teams]].

## Common Workflow Patterns

**Sequential** (steps depend on each other):
```
design-explorer → architecture-reviewer → code-writer → code-reviewer → project-health-monitor
```

**Parallel review**:
```
Lead spawns: security-auditor + code-reviewer + visual-verifier
Each owns distinct scope → lead synthesizes findings
```

**Debug with competing hypotheses**:
```
Spawn 3–5 subagents, each with a different theory
Each tries to disprove the others' theory
Surviving theory = actual root cause
```

**Security review loop**:
```
security-auditor (threat report) → code-writer (fix Critical/High) → security-auditor (re-audit)
```

**Multi-vendor adversarial review**:
```
Sonnet implements → Opus reviews (same vendor, different tier — minimum)
Claude implements → Codex reviews (cross-vendor — catches model-family blind spots)
/council: all vendors analyze simultaneously → surface disagreements explicitly
```
See [[concepts/multi-vendor-adversarial-review]] for when each level is appropriate.

## Related Pages

- [[concepts/agent-skills]] — skill architecture, loading levels, SKILL.md structure
- [[concepts/agent-subagents]] — full frontmatter reference, invocation patterns
- [[concepts/agent-teams]] — team architecture, quality gate hooks, known limitations
- [[concepts/agent-harness]] — harness components; primitives as building blocks
- [[concepts/verification-pipeline]] — verification requirements for each tier of work
