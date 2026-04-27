---
title: "Verification Pipeline"
type: concept
tags: [agent-engineering, verification, quality, testing, visual-verification, harness]
sources:
  - "Exit Code 0 Is Not Quality What 198 Autonomous Agents Taught Me About AI Orchestration.md"
created: 2026-04-26
updated: 2026-04-26
---

# Verification Pipeline

**"Exit code 0 means no errors — not it's good."**

The verification pipeline is a layered quality system for autonomous agents that catches failures invisible to the layers below. Built from production failures (30+ campaigns, 198 agents), it exists because structural correctness and functional correctness are orthogonal.

## The Four-Tier Quality Ladder

| Tier | What It Checks | What It Misses |
|---|---|---|
| **1. Typecheck** | Syntax, types, imports | Invisible features, broken layouts, empty screens |
| **2. Visual Verification** | Does it render? DOM elements by data-testid, screenshots | Interaction behavior (long-press, drag, timing) |
| **3. Screenshot Gate** | Hard gate: no screenshots = no completion | Correctness of what's rendered |
| **4. Design Critique** | Three-perspective evaluation: Spec / User / Art Director | Project-specific taste |

Most AI coding tools stop at Tier 1. The industry is still debating whether agents should run tests at all.

## Origin: The Show Bible Failure

An autonomous agent completed a multi-phase campaign, passed typecheck, exited confidently. 37 of 38 entity cards were invisible. One manually-created test entity rendered; everything the agent built was structurally correct and completely non-functional.

This is the foundational failure of autonomous AI code generation. **The gap between "compiles" and "works" is where real users live.**

## Tier 2: Visual Verification Implementation

Playwright navigates real routes in a real browser:
- Counts DOM elements by `data-testid`
- Captures screenshots as artifacts
- Configured per route (13 routes in the reference implementation)

If a view that should have 38 entity cards has zero, this tier catches it.

## Tier 3: Screenshot Gate

Hard enforcement, not a suggestion. If an agent modified `.tsx` files during a campaign, it **cannot complete** without screenshot artifacts. No screenshots = no completion signal.

This converts visual verification from optional to mandatory for UI-touching work.

## Tier 4: Design Critique

Three evaluator perspectives:
- **Spec Auditor** — does the output match requirements?
- **User Advocate** — would a human enjoy this?
- **Art Director** — does it match the project's visual identity?

Maximum two refinement rounds before escalating to human review. The cap prevents infinite loops on subjective quality.

**Limitation**: Tier 4 requires project-specific taste definition. "Does this feel inhabited?" only works if you've defined what "inhabited" means for your project. Non-transferable.

## Interaction Testing Gap (known ceiling)

Bugs that pass all four tiers are still possible:
- Long-press behavior
- Spawn mechanics
- FPS degradation over time

These require manual interaction. Automated interaction testing is the identified next frontier.

## Protocol Rules From Failures

**"Layer, don't replace"**: add new components beside working ones, verify visually, then remove the old version. Origin: 841 lines of working components replaced with 144 lines of broken output by agents that never rendered their work.

**"Design target, not delta"**: define the end state before starting; converge toward a reference, not away from a baseline. Origin: agent in infinite improvement loop because "done" wasn't defined.

**Plan validation gate**: check the agent's decomposed plan against the original request before execution begins. Origin: agent truncated its own scope in self-authored plan, declared done after 2 of 6 waves.

**Merge-before-cleanup**: worktree branches must be merged before cleanup runs. Origin: three agents' completed work vanished silently when branches were cleaned without merging.

**Claim-before-resume ordering invariant**: prevents two agent instances from picking up the same active campaign (TOCTOU race condition). Origin: two Archon instances editing the same files simultaneously.

## Anti-Pattern Accumulation

When AI agents generate code one file at a time, anti-patterns that are individually reasonable accumulate silently across the codebase. A cross-file DOM audit found 193 `repeat:Infinity` animations and 362 `backdrop-blur` instances — no single file was the bottleneck, but collectively devastating to performance.

Background cleanup agents running on a daily cadence prevent this debt from compounding. See [[concepts/agent-harness]] (Entropy / garbage collection principle).

## Relationship to Harness Engineering

The verification pipeline is an instantiation of the harness principle "Application legibility" — wire the app's own observability into the agent runtime so it can self-validate without human QA involvement.

It extends [[concepts/ralph-loop]] with completion conditions tied to verification passing rather than code existing.

## Related Pages

- [[concepts/agent-harness]] — harness design principles including application legibility and entropy/GC
- [[concepts/ralph-loop]] — completion conditions; verification as the exit signal
- [[concepts/agentic-sandbox-controls]] — sandbox security; visual verification runs in a real browser (security boundary)
- [[summaries/exit-code-0-quality]] — full case study with numbers and architecture
- [[concepts/cicd-testing]] — broader CI/CD testing strategy; verification-pipeline is one quality gate within it
- [[concepts/unit-testing]] — unit testing as the foundation layer beneath agent-specific verification
