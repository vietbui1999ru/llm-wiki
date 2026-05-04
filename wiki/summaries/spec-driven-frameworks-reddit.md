---
title: "Spec-Driven Frameworks vs Native Claude Code/Codex — Community Synthesis"
type: summary
tags: [agent-workflow, frameworks, orchestration, planning, community, spec-driven]
sources: ["Are spec-driven frameworks like Agent OS, BMAD, Superpdoms or SpecKit still worth using, or have Claude Code and Codex made them redundant?.md", "Plugins for Opencode.md"]
created: 2026-05-04
updated: 2026-05-04
---

# Spec-Driven Frameworks vs Native Claude Code/Codex — Community Synthesis

Source: r/ClaudeCode Reddit thread (2026-05-03), 30+ comments from practitioners who have shipped real projects.

---

## The Question

Do frameworks like BMAD, Agent OS, Superpowers, and SpecKit still earn their keep now that Claude Code and Codex do their own task decomposition and context management? Or have they been absorbed?

---

## Community Consensus

No single answer — position correlates with project size and user background.

**For single-session small tasks**: vanilla Claude Code + lean CLAUDE.md is sufficient. Frameworks are overhead here.

**For multi-session projects**: frameworks pay off as the *cross-session persistent state layer*, not as decomposition engines. Without structure, you re-explain the whole codebase every session restart.

**For non-engineers**: spec frameworks have more value, not less — they force the upfront thinking engineers do from experience. The LLM can decompose, but it can't clarify what you actually want if you haven't thought it through.

---

## Framework-Specific Notes

### Superpowers
- Still widely used. Iron Law discipline (TDD, debugging loops) adds structure that native Claude Code lacks.
- Token-heavy: flagged by multiple users as 4–5x the cost of lighter alternatives.
- Praised for milestone-gated reviews — each milestone is a catch opportunity.
- Community split: worth it for those who value the review gates; abandoned by those who want speed.

### Matt Pocock skills
- Dominant alternative to Superpowers in the thread. Lightweight, composable, principled.
- grill → PRD → kanban DAG → AFK loop: already in [[summaries/mattpocockworkflow]].
- `improve-codebase-architecture` skill surfaced as underrated by multiple commenters.
- Paired with [[entities/sandcastle]] or [[entities/dangeresque]] for AFK parallelism.

### GSD (Get Shit Done)
- Wave-based DAG execution with explicit slash commands (`/gsd-execute-phase`).
- GSD1 is token-heavy (4–5x Superpowers). GSD2 restricts to API-only (violates subscription ToS).
- Still maintained as of thread date; not dead despite rumors.
- Overlaps Pocock workflow substantially; preferred by those who want slash-command enforcement.

### BMAD
- One user switched from BMAD to native plan mode when Opus 4.7 launched — model got capable enough to not need it.
- Workflow: Opus 4.7 plans → Codex 5.5 reviews the plan (adversarial) → iterations until agreement → Claude implements → Codex code-reviews.

### Agent OS / SpecKit
- Less discussed in the thread; treated as the "enterprise" end.
- SpecKit: "way over the top for home side projects" (direct quote).

---

## Emerging Patterns

### Thin CLAUDE.md + skills as the new default
Multiple high-karma commenters converge on this: maintain a lean CLAUDE.md pointing to ADRs/architecture docs, use skills for task-specific guidance. Not a framework — a structured filesystem.

> "Lean CLAUDE.md is enough for single-session work. Frameworks earn their keep on multi-session projects for persistent task state."

### Adversarial multi-model review
Multiple workflows combine Claude (implement) + Codex (review plan) or vice versa. Catches single-model blind spots. See [[concepts/multi-vendor-adversarial-review]].

### Clear-over-compact enforced
Every active workflow in the thread — GSD, Pocock, Dangeresque, vanilla loops — ends sessions with clear (not compact). Pocock's empirical position against compaction is community consensus now.

### Orchestration without frameworks
`yopla` comment: "told Claude to break into phases, make a trackable task plan, include a restart prompt. Ran it from shell in a loop." This is a sketch of [[concepts/ralph-loop]] discovered organically.

### gitignored durable corpus (AgentOps pattern)
`.agents/` directory: not committed, not deleted — durable per-project context that survives session resets. Resolves the commit-everything vs. delete-after-ship tension. See [[entities/agentops]].

---

## New Tools Mentioned

| Tool | What | Status |
|---|---|---|
| [[entities/sandcastle]] | TS lib for parallel agents in worktrees + containers | Active, Matt Pocock |
| [[entities/dangeresque]] | Host-native CLI, adversarial reviewer, human-merge gate | Active |
| [[entities/mnemory]] | Self-hosted MCP cross-session memory | Active |
| [[entities/agentops]] | `.agents/` corpus + `/council` multi-vendor consensus | Active |
| CCTM | Desktop GUI for CC config/profiles | Utility tool |
| Lovcode | CC chat-history browser + skill marketplace | Utility tool |

---

## OpenCode Plugin System

Separate source (`Plugins for Opencode.md`): OpenCode is a Claude Code competitor with a substantially different plugin architecture. Key differentiator: plugins can **inject context into and replace compaction prompts**, exposing a hook Claude Code doesn't. See [[comparisons/claude-code-vs-opencode-plugins]].

---

## Related Pages

- [[summaries/mattpocockworkflow]] — Pocock's full workflow (the lightweight winner)
- [[summaries/superpowers-plugin]] — Superpowers detail
- [[summaries/agent-harness-engineering]] — harness anatomy underpinning all frameworks
- [[concepts/ralph-loop]] — the harness pattern practitioners are rediscovering
- [[comparisons/spec-driven-frameworks-vs-native]] — side-by-side analysis
- [[concepts/multi-vendor-adversarial-review]] — the BMAD→Codex adversarial pattern
