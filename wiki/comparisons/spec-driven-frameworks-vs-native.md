---
title: "Spec-Driven Frameworks vs Native Claude Code"
type: comparison
tags: [frameworks, agent-workflow, planning, orchestration, spec-driven]
sources: ["Are spec-driven frameworks like Agent OS, BMAD, Superpdoms or SpecKit still worth using, or have Claude Code and Codex made them redundant?.md", "AGENTS md gets it wrong in 2 ways.md"]
created: 2026-05-04
updated: 2026-05-27
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
2. Host-native worktree isolation (Dangeresque approach) + `permissions.allow`/`permissions.deny` in `.claude/settings.json` (note: `allowedTools`/`disallowedTools` is the old CC schema — see [[summaries/claude-code-permissions-settings]])
3. SandCastle workaround: Claude runs on host, containers only for tool execution

This nuance is not captured in the sandbox controls concept page. See [[concepts/agentic-sandbox-controls]].

### Clear-over-compact is now majority practice (scoped)

[[concepts/context-compression]] no longer labels clear-over-compact as a "contrarian position" — this comparison page was written before that update. The current page reflects: clear-over-compact is majority practice among experienced practitioners in harness-based AFK workflows (r/ClaudeCode + r/opencodeCLI, 2026-05, n≈30). Every active framework in that community (GSD, Dangeresque, SandCastle, vanilla loops) enforces fresh context per task.

**Evidence scope**: ~30 experienced developers in harness-heavy communities. Compact remains better for interactive/exploratory sessions and workflows without durable filesystem state.

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

## AGENTS.md Format Critique (Wand, 2026-05-06)

The AGENTS.md standard (and equivalents: CLAUDE.md monoliths, Cursor single-rule-files) fails in two ways:

**Wrong abstraction — single file doesn't scale:**
- Cannot hold all project context without becoming unmaintainable
- Nested AGENTS.md assumes false constraints: single-file-edit scope, directory = domain scope, no ambiguity between parent/child rules
- Most importantly: **agents will not reliably follow rule-file-selection instructions** — compliance is not enforceable by the orchestrator
- Better: `@path/to/file.md` composition (Claude Code), multiple scoped rule files (Cursor), or hooks that load context programmatically

**Content guidance too narrow:**
Most examples restrict to coding style, build/test commands, micro-architecture. Missing — what AI can't infer from code:

| Missing context | Why it matters |
|---|---|
| Project lifecycle stage | MVP vs. mature product drives simplicity/robustness tradeoff |
| User locations and personas | Affects latency requirements, compliance, UI/UX |
| Domain objects and external relationships | What is a `Subscription` and where does it come from? |
| Business context of user flows | Why does checkout have this edge case? |
| Feature-specific tradeoffs | Latency vs. resiliency — which matters here? |

"The AI can't read the room." Every conversation starts with a junior dev needing re-onboarding. Build commands are not enough.

**Wand's alternative**: many single-purpose files + global rules repo via symlink + Memory Bank (`_memory/` hierarchy loaded via repomix at session start). See [[concepts/memory-bank-pattern]], [[entities/agents-md-format]] (critique section), and [[concepts/rules-vs-hooks]].

**Implication for this comparison**: the lean CLAUDE.md + skills approach partially addresses the content narrowness problem (skills pull domain-specific context), but still benefits from `@` composition to avoid the single-file scale problem.

---

## Related Pages

- [[entities/dangeresque]] — host-native orchestrator
- [[entities/sandcastle]] — parallel orchestrator with container isolation
- [[concepts/multi-vendor-adversarial-review]] — cross-vendor judge pattern
- [[concepts/branch-strategy-for-agents]] — merge strategy taxonomy
- [[concepts/agentic-sandbox-controls]] — OS-level sandbox recommendation (needs update re: ToS)
- [[concepts/context-compression]] — clear-over-compact debate
- [[concepts/memory-bank-pattern]] — cross-session memory alternative Wand uses
- [[concepts/rules-vs-hooks]] — hooks architecturally superior to static files for dynamic context
