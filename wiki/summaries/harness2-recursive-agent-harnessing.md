---
title: "Harness²: Recursive Agent Harnessing for an Open World (google-research/harness2)"
type: summary
tags: [harness-optimization, self-improving, agent-harness, recursion, benchmarks]
sources: ["google-researchharness2.md"]
created: 2026-10-22
updated: 2026-10-22
---

# Harness² (Google Research, 2026)

GitHub README for `google-research/harness2` (Apache-2.0). Paper: Xu et al., "Harness²: Recursive Agent Harnessing for an Open World", arXiv:2610.14224. Only the README was ingested; benchmark numbers are from the README *(claimed, unverified)*. Not an officially supported Google product.

## Core idea

A **harness** is everything around the model that makes it an agent. **Harnessing** is optimizing that system. Harness² improves the harness automatically, **with model weights fixed**, on tasks not seen when the harness was designed.

Two levels of recursion:

- **Task-level recursion: Propose → Probe → Compose.** A harness editor proposes edits (invariant and domain-specific), candidate harnesses are run on the *same* task, and a composer builds the refined harness from **behavioural contrasts between executions**. No ground-truth feedback is needed: the signal is the difference between runs.
- **Harnessing-level recursion.** An experience reflector writes adopted harnesses and "evidence-supported lessons" into a persistent **improvement harness**, which guides refinement on the next task.

Scaling modes: **parallel** (probe k general + k domain candidates, compose k results: explores wider) and **sequential** (k successive Propose-Probe-Compose steps: refines deeper). `--k` is the task-level recursion budget.

## Eight editable harness components

System prompt, guardrails, memory, skills (construct context); tool guidance, scripts (tool interface); subagents (delegation); plugins (middleware). This is a useful checklist of what a harness consists of; it matches the component model in [[concepts/agent-harness]].

## Reported results (claimed, unverified)

One Harness² step improves GLM-5 and Gemini 3.5 Flash over their base harnesses: up to +11.5 points on WorkBuddy-Bench, +4.5 on JobBench, +11.8 pp partial pass rate on LAB (legal). A larger recursion budget gives further gains. Executors: OpenCode (default) and Codex.

## Operational notes

- Executor network access is unrestricted and Codex runs with its sandbox disabled by default. The README warns that public rubrics may be reachable online: restrict network before evaluating or results can be contaminated.
- Results, adopted harnesses and reflection notes are written under `runs/`; re-running the same command resumes.

## Why it matters here

Harness² is a research-grade version of what practitioners do by hand when they tune CLAUDE.md, skills and hooks (see [[summaries/reddit-self-improving-claude-code-setup]]). Two ideas transfer:

1. **Contrastive evidence instead of self-assessment.** Compare runs of different harness variants on the same task rather than asking the agent whether it did well.
2. **Lessons must be evidence-supported** before they enter the persistent improvement harness, the same gate the Reddit practitioners arrive at ("only add a rule I had to correct twice").

## Wiki connections

- [[concepts/self-improving-agent-setup]]: Harness² is the automated end of that spectrum.
- [[concepts/agent-harness]]: component model.
- [[concepts/preference-feedback-loop]]: our judge-driven rule extraction is a manual, single-level analogue of harnessing-level recursion.
