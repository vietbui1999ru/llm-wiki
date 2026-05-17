---
title: "Avoiding AI Code Slop — Intent-Driven Verification"
type: summary
tags: [ai-agents, code-review, slop, intent, spec-first, verification, technical-debt]
sources: ["How to Avoid AI Code Slop.md"]
created: 2026-05-17
updated: 2026-05-17
---

# Avoiding AI Code Slop — Intent-Driven Verification

Source: "How to Avoid AI Code Slop" — Ankit Jain (CEO, Aviator), via Engineering Leadership newsletter. Practical methodology for preventing quality degradation when AI generates production code at scale.

---

## The Core Problem

Code review was designed for human-paced output. AI-generated PRs are different in kind:
- Volume: more PRs than humans can review carefully → rubber-stamping
- Intent loss: human authors carry implicit context (tradeoffs considered, alternatives rejected); AI prompts are rarely saved
- Failure mode: code that **compiles, passes tests, and looks plausible but is subtly wrong**

> "The most dangerous variety reads right and has correct syntax, but the logic is wrong."

---

## 6 Slop Failure Modes

| Mode | Description | Catch difficulty |
|---|---|---|
| **Plausible but incorrect logic** | Syntactically right, logically wrong; requires knowing what code *should* do | Very high |
| **Over-engineering** | 200-line abstraction for a 15-line problem; trained on enterprise patterns | Medium |
| **Convention blindness** | Correct generic code that ignores your repo's naming, error handling, module boundaries | Medium |
| **Hallucinated APIs** | Invokes methods that don't exist or were removed | Low (compile/runtime error) |
| **Defensive overreach** | Excessive try-catch, silent error swallowing; code "handles" failures by hiding them | High |
| **Cargo-cult patterns** | Copies patterns (retry logic, circuit breakers) without the reasoning behind them | High |

Common thread: **slop passes the eye test**. That's what makes it dangerous at scale.

See [[concepts/ai-specific-pitfalls]] for full failure mode catalogue.

---

## Intent-Driven Verification

The proposed shift: **move review upstream to before code is written**, not after.

> "When a design decision is caught in spec review, fixing it is a sentence change. When caught in code review, it may require significant rework."

### The Spec-First Workflow

```
1. Write spec (AI-assisted) — scope, acceptance criteria, explicit out-of-scope
2. Review + approve spec (human)
3. Generate code against spec
4. Automated agent verifies code against acceptance criteria
5. Human code review catches only convention-level issues
```

Spec format: 2–3 sentences on scope + list of acceptance criteria + what's explicitly out of scope. Can be AI-generated from a ticket or prompt conversation.

### Aviator Experiment

Full-stack feature (hierarchical config system), zero manually written app code:
- 65 acceptance criteria reviewed and approved before generation
- ~6k lines generated (40% app, 40% tests, 20% GraphQL auto-generated)
- Second agent verified all 65 criteria in **6 minutes**
- Result: 60 passed, 4 failed, 1 partial
- Human review: ~10 comments per PR, mostly convention-level (import placement, naming)

Key finding: spec review catches design-level issues; code review catches convention-level issues. **Both layers are necessary because they catch different things.**

---

## 5 Guardrails

1. **Scope tasks tightly** — large open-ended prompts produce the most slop; decompose into small, well-specified subtasks with checkpoints
2. **Intent as first-class artifact** — document the *what* before generating the *how*; even a few sentences + acceptance criteria counts
3. **Review intent before implementation** — require spec approval above a complexity threshold; front-load high-value decisions
4. **Automate mechanical checks** — tests, linting, type checks catch surface-level slop; stack imperfect filters until nothing comes through
5. **Build a slop register** — team-maintained list of patterns AI consistently gets wrong in your codebase; feed back into prompts + CI checks

---

## Slop Register

A per-codebase document of known AI failure patterns: naming conventions AI ignores, error-handling patterns it violates, deprecated libraries it recommends, module boundaries it crosses.

Two uses:
1. **Prompting**: inject register into prompts to prevent known patterns
2. **CI**: encode as lint rules or pre-commit checks to catch them when they slip through

Connects to [[concepts/domain-glossary]] (CONTEXT.md pattern) and [[concepts/agent-context-instructions]].

---

## Relation to Existing Wiki

- [[concepts/ai-specific-pitfalls]] — overlaps on hallucinated APIs and "looks right" code; this source adds over-engineering, defensive overreach, cargo-cult
- [[concepts/ai-code-review]] — this source argues spec review is the higher-value gate; code review becomes convention-only
- [[summaries/ai-code-vetting-practices]] — complements: vetting practices = what to check; this source = when and how to restructure the process
- [[concepts/verification-pipeline]] — spec-first + agent verification fits as a tier-0 gate (before typecheck/visual)
- [[concepts/agent-context-instructions]] — slop register is a form of context instruction injected into agent prompts
- [[summaries/reviewing-ai-generated-code]] — same domain; this source focuses on process restructuring vs. review checklist
