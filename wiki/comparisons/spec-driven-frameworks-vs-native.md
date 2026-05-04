---
title: "Spec-Driven Frameworks vs Native Claude Code"
type: comparison
tags: [frameworks, agent-workflow, planning, orchestration, spec-driven]
sources: ["Are spec-driven frameworks like Agent OS, BMAD, Superpdoms or SpecKit still worth using, or have Claude Code and Codex made them redundant?.md"]
created: 2026-05-04
updated: 2026-05-04
---

# Spec-Driven Frameworks vs Native Claude Code

Side-by-side analysis across four workflow approaches. Based on community evidence from practitioners who have shipped real projects (r/ClaudeCode, 2026-05-03).

---

## Frameworks Compared

| Framework | Style | Token cost | Enforcement | Portability |
|---|---|---|---|---|
| Superpowers | Iron-law discipline | High (4–5x lean) | Mandatory milestones + reviews | Claude Code only |
| GSD | Wave-based slash commands | High (similar to Superpowers) | Slash-command structure | Claude Code + Codex |
| BMAD / Agent OS | Spec-first, enterprise | High | Full spec ceremony | Vendor-portable |
| Matt Pocock skills | Composable, minimal | Low (on-demand load) | Developer discipline only | Vendor-portable |
| Vanilla plan mode | No framework | Baseline | None | N/A |
| Custom harness (ralph-loop, dangeresque, sandcastle) | Bespoke | Configurable | Whatever you build | Vendor-portable |

---

## Pros/Cons by Approach

### Heavy Frameworks (Superpowers, GSD, BMAD)

**Pros**
- Iron-law process discipline — agent can't skip steps
- Opinionated end-to-end: one decision to make, then follow the rails
- Built-in verification milestones: each gate is a catch opportunity
- Good for non-engineers who need process scaffolding to substitute for experience

**Cons**
- Token-heavy: framework overhead on every session (4–5x lean approach)
- Framework owns the process — hard to deviate for one-off tasks
- Ceremony bleeds in even for small bugs
- Superpowers: Claude-only; BMAD/GSD: slower to evolve with model capability changes
- Model improvements (Opus 4.7+) have absorbed some of what the framework did

**When to use**: Long multi-session projects, non-engineer users, team settings where shared process matters, any project where you're willing to trade tokens for enforcement.

---

### Lean Skills (Matt Pocock)

**Pros**
- Composable: invoke only what you need per session
- Low token cost: skills load on demand, not front-loaded
- Hackable: add/remove skills without framework breakage
- Vendor-portable: CLAUDE.md + skill files work across Claude, Codex, Cursor
- Pairs directly with custom orchestrators (SandCastle, Dangeresque)

**Cons**
- No enforcement: discipline depends on the developer, not the tool
- No built-in parallelism: need SandCastle or Dangeresque to get AFK parallel runs
- Requires more upfront thinking about which skills to reach for

**When to use**: Experienced developers who want control; projects where the Pocock workflow (grill→PRD→kanban DAG→AFK) fits naturally.

---

### Vanilla Plan Mode

**Pros**
- Zero overhead
- Full LLM autonomy on decomposition

**Cons**
- No persistent state across sessions
- No verification gates
- Reinvents structure every session restart
- Strictly dominated by lean skills for any non-trivial project

**When to use**: Single-session, throwaway scripts. Nothing else.

---

### Custom Harness (ralph-loop, dangeresque, sandcastle)

**Pros**
- Maximum control: harness matches your feedback loops exactly
- AFK parallel runs: multiple agents, multiple worktrees, unattended
- Adversarial review built in (Dangeresque)
- Token telemetry per iteration (SandCastle)

**Cons**
- Build and maintenance cost
- Requires harness engineering knowledge (see [[concepts/agent-harness]])
- SandCastle: container dependency + complexity
- Dangeresque: host-native (no container) but less feature-rich

**When to use**: Teams or individuals with multi-task parallel workloads; AFK overnight runs; when no existing framework matches your workflow.

---

## Key Discrepancies with Prior Wiki Content

### Sandbox controls vs Anthropic ToS

[[concepts/agentic-sandbox-controls]] recommends OS-level sandboxing (containers, Bubblewrap, Seatbelt) as mandatory per NVIDIA AI Red Team guidance. **However**: Anthropic's ToS restricts Claude Code subscription keys inside Docker containers. This creates a conflict:

- NVIDIA: "sandbox at OS level"
- Anthropic ToS: "no CC in containers" (subscription keys)

Resolution paths:
1. Use the API (not subscription) — no ToS restriction
2. Host-native worktree isolation (Dangeresque approach) + fine-grained `allowedTools`/`disallowedTools`
3. SandCastle workaround: Claude runs on host, containers only for tool execution

This nuance is not captured in the sandbox controls concept page. See [[concepts/agentic-sandbox-controls]].

### Clear-over-compact is now consensus

[[concepts/context-compression]] treats anchored iterative summarization as the default and Pocock's clear preference as a "contrarian position." Community evidence (2026-05-03) shows clear-over-compact is now *majority practice* for coding workflows. Every active framework (GSD, Dangeresque, SandCastle, vanilla loops) enforces fresh context per task. The "contrarian" label should be revised.

---

## What the Community Has Converged On

Across all approaches, the following practices appear in every high-upvote workflow:

1. **Worktree isolation** — each task in its own checkout, regardless of tool
2. **Clear over compact** — fresh 200K context per task, not compaction
3. **Filesystem as state** — PRDs, issues, decisions stored in files, not agent memory
4. **Verification before merge** — automated checks + human gate
5. **Skills over frameworks** — composable skills preferred to monolithic frameworks
6. **Adversarial review** — at minimum, different model tier for review (Sonnet→Opus); ideally cross-vendor

---

## Recommended Workflow (Synthesis)

For an experienced developer building non-trivial software:

```
1. grill-me → PRD → kanban DAG (Pocock workflow, lean skills)
2. AFK parallel run via Dangeresque or SandCastle
3. Adversarial review (cross-vendor or Sonnet→Opus)
4. Human merge gate
5. Clear context between sessions; filesystem as state
```

For a non-engineer building mid-complexity product:

```
1. Use Superpowers for discipline enforcement (Iron Laws catch what you'd miss)
2. Or: grill-me → explicit review checkpoints → human QA
3. Skip AFK parallel runs until process is stable
```

---

## Related Pages

- [[summaries/spec-driven-frameworks-reddit]] — community thread this analysis is based on
- [[summaries/mattpocockworkflow]] — lean skills workflow in detail
- [[summaries/superpowers-plugin]] — Superpowers detail
- [[entities/dangeresque]] — host-native orchestrator
- [[entities/sandcastle]] — parallel orchestrator with container isolation
- [[concepts/multi-vendor-adversarial-review]] — cross-vendor judge pattern
- [[concepts/branch-strategy-for-agents]] — merge strategy taxonomy
- [[concepts/agentic-sandbox-controls]] — OS-level sandbox recommendation (needs update re: ToS)
- [[concepts/context-compression]] — clear-over-compact debate
