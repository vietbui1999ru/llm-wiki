---
title: "Deep Modules"
type: concept
tags: [software-design, agent-engineering, testability, modularity, codebase-design]
sources: ["Full Walkthrough Workflow for AI Coding — Matt Pocock.md"]
created: 2026-04-30
updated: 2026-04-30
---

# Deep Modules

Concept from John Ousterhout, *A Philosophy of Software Design* (2018). A deep module has a **narrow public interface** and **substantial internal implementation**. A shallow module has a wide interface and thin implementation.

---

## Deep vs Shallow

```
Shallow (bad)                Deep (good)
┌──────────────────┐        ┌──┐
│ helper1()        │        │  │  narrow interface
│ helper2()        │        │  │
│ format()         │        │  │  wide implementation
│ parse()          │        │  │
│ validate()       │        │  │
└──────────────────┘        └──┘
   wide interface              thin interface,
   thin implementation          rich behavior
```

Many small files with many exports = shallow codebase. A few well-defined services/modules with narrow APIs = deep codebase.

---

## Why It Matters for AI Agents

### 1. Dependency graph traversal
In a shallow codebase, understanding one behavior requires tracing through many files and many inter-module relationships. The agent burns context tokens mapping this graph before it can act. In a deep codebase, the module is the scope — the agent works within one boundary.

### 2. Test boundaries
Shallow modules create an ambiguous testing problem: do you test each function individually (unit)? Do you group related files (integration)? Where does the boundary go? Individual function tests produce fragile, over-specified tests that resist refactoring.

Deep modules have a natural test boundary: **the module interface**. Wrap the public API in a test harness, exercise it with realistic inputs, assert on observable outputs. The internals can change without breaking tests.

```typescript
// Shallow: tests mirror internal structure (fragile)
test('formatPoints correctly', () => { ... })
test('validateLevel correctly', () => { ... })
test('updateStreak correctly', () => { ... })

// Deep: tests exercise observable behavior through the interface (stable)
test('GamificationService: lesson completion awards correct points', () => { ... })
test('GamificationService: streak resets after 24h gap', () => { ... })
```

### 3. AI produces shallow codebases by default
Without intervention, AI agents tend toward shallow architectures — many small helper functions, many small files, many exports. This is partly because each implementation step is scoped to the immediate need and partly because AI doesn't maintain a global module map between sessions.

Running `/improve-codebase-architecture` surfaces deepening opportunities. More importantly, include proposed module structure in the PRD before implementation begins.

---

## The Gray Box Principle

Pocock's corollary: deep modules enable the developer to maintain a **gray box** view of the codebase.

- You need to understand the interface and observable behavior of each module
- You do not need to understand every internal line
- This lets you move fast (delegate implementation to agents) while retaining genuine ownership of the system

The alternative — delegating module structure to agents — produces a codebase you don't understand, where agent output quality degrades further because the codebase itself is poorly structured.

---

## Practical Signals

A codebase is too shallow if:
- Your PRD requires touching 10+ files for a single feature
- Tests mock 5+ dependencies per test
- You can't describe what a "module" is without listing 15 files
- AI implementation consistently touches wrong files or introduces duplicate logic

---

## Related Pages

- [[summaries/mattpocockworkflow]] — deep modules in the context of the full AI coding workflow
- [[concepts/unit-testing]] — test boundaries, AAA pattern, behavior-not-implementation testing
- [[concepts/agent-harness]] — agent operating within bounded scope (module) vs. full graph
- [[concepts/agent-context-instructions]] — CONTEXT.md as a way to communicate module structure to agents
