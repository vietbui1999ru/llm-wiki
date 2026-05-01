---
title: "Matt Pocock — Full Walkthrough Workflow for AI Coding"
type: summary
tags: [agent-workflow, tdd, planning, kanban, parallelization, deep-modules, context-management]
sources: ["Full Walkthrough Workflow for AI Coding — Matt Pocock.md"]
created: 2026-04-30
updated: 2026-04-30
---

# Matt Pocock — Full Walkthrough Workflow for AI Coding

Source: workshop transcript (~90 min), YouTube companion to the skills repo.

Thesis: software engineering fundamentals — the same ones from Fowler, Ousterhout, the Pragmatic Programmer — apply directly to AI-assisted development. The failure mode is treating AI as a new paradigm and abandoning the fundamentals.

---

## LLM Constraints That Drive the Workflow

### Smart Zone / Dumb Zone
LLM attention is quadratic. Every token added strains attention relationships across all prior tokens. Performance degrades as context fills — Pocock calls this the "smart zone" (good) vs. "dumb zone" (degraded).

**Empirical threshold: ~100k tokens**, regardless of stated model context window size (1M or 200k). The smart zone is about attention mechanics, not advertised limits. Larger context windows ship more dumb zone, not more smart zone.

This is the same mechanism as [[concepts/context-degradation]] (lost-in-middle, U-curve attention), stated in practitioner terms with a concrete threshold.

### Clear Context Over Compacting
Pocock prefers hard context clears over compaction ("I hate compacting"). His argument:
- Clearing gives a **reproducible, deterministic starting state** — same system prompt every time
- Compaction leaves "sediment" — summarized history that is never quite right, and each compaction compounds drift
- Analogy: treat the LLM like the amnesiac from *Memento* — design the system so each session starts fresh and complete, not so you can preserve history across one long session

**Contrarian position** relative to anchored iterative summarization in [[concepts/context-compression]], which recommends structured compaction as the default. The debate is context-dependent: Pocock's workflow stores state in filesystem/git (PRDs, issue files, commits), making session-level memory unnecessary. If your harness doesn't have durable filesystem state, clearing is riskier.

---

## The Workflow

### Phase 0: Grill (Human-in-loop, mandatory)
Use `/grill-me` before writing any code. Goal: reach a **shared design concept** — not a plan, not a spec, but genuine mutual alignment.

- AI asks one question at a time, with a recommended answer for each
- Session can run 40–100+ questions
- The conversation history itself is the asset, not the resulting document
- Can ingest meeting transcripts, Slack threads, etc. as grill input

Anti-pattern: *specs to code* — writing a spec document and asking AI to implement it without a shared understanding. The AI will implement what the spec says, not what you meant.

### Phase 1: PRD — Destination Document
Use `/to-prd` to synthesize the grill session into a Product Requirements Document.

- Contains: problem statement, solution, user stories, implementation decisions, out-of-scope items
- The out-of-scope section is the **definition of done** — essential for preventing scope creep
- Pocock does not re-read the PRD after writing it; he trusts his grill session established alignment, and LLMs are good at summarization
- Keep proposed modules in mind throughout — this is not specs-to-code, the code shape matters from the start

### Phase 2: Kanban Board — Journey Document
Use `/to-issues` to break the PRD into independently-grabbable issues as a **directed acyclic graph (DAG)**, not a sequential list.

**Key technique: vertical tracer bullets**
- Tracer bullet = a thin vertical slice through all system layers (DB → service → API → UI)
- Goal: get feedback on the full integration path as early as possible
- Anti-pattern: horizontal slices (all DB work in phase 1, all API work in phase 2) — you don't test layer integration until phase 3
- First issue should always show something on the frontend, not just create a service

**Why DAG > sequential list:**
- Sequential plan forces one agent, one task at a time
- DAG with blocking relationships enables parallel agents: tasks with no pending blockers can be grabbed simultaneously
- Enables "phase 1 → phase 2A + 2B → phase 3" style parallelization

**Doc rot warning:** After the feature ships, close or delete the PRD/issue files. Old PRDs left in the repo become context poison for future agent sessions — they describe stale state and the agent treats them as ground truth.

### Phase 3: AFK Implementation (Night Shift)
The planning phases are the *day shift* (human-in-loop). Implementation is the *night shift* (AFK).

The loop prompt:
1. Inject all open issue files at session start
2. Inject last N commits (provides recent context without full history)
3. Agent picks the next unblocked AFK task
4. Explores → implements via TDD → runs feedback loops → commits
5. On "no more tasks", exits
6. Loop restarts with fresh context (clear, not compact)

**Human-in-loop vs AFK taxonomy:**
- Planning, alignment, QA, code review = always human-in-loop
- Implementation = AFK-safe when: good tests exist, tracer bullets provide integration signals, issue scope is bounded

### Phase 4: QA and Code Review (Human-in-loop, mandatory)
QA is how the developer imposes taste back on the codebase. Automating QA entirely produces "slop." The human must verify that the tracer bullet actually works end-to-end.

- AI-written automated review in the smart zone (clear after implementation, review fresh) catches a large class of bugs cheaply
- Reviewer gets **pushed** coding standards (in system prompt); implementer can **pull** standards (via skills)
- Model tier suggestion: Sonnet for implementation, Opus for review

---

## Codebase Design for AI Agents

### Deep Modules
Concept from John Ousterhout, *A Philosophy of Software Design*. See [[concepts/deep-modules]].

- **Deep module**: narrow public interface, substantial internal implementation
- **Shallow module**: wide interface, thin implementation (many small files with many exports)
- AI agents perform worse in shallow codebases because they must traverse large dependency graphs to understand scope
- Deep modules create clear test boundaries: wrap the module interface, not individual internal functions
- "Gray box" principle: the developer needs to know the *interface behavior*, not every internal detail — this lets you retain codebase understanding while delegating implementation

Running `/improve-codebase-architecture` surfaces deepening opportunities automatically.

### Feedback Loops as the Ceiling
> "The quality of your feedback loops is the ceiling on AI output quality."

If AI produces bad output, fix the feedback loops first (tests, type checks, integration signals), not the prompts. An agent coding without fast, deterministic pass/fail signals is coding blind.

### Push vs Pull for Coding Standards
- **Push**: hardcode into CLAUDE.md — always present in context, appropriate for universal rules
- **Pull**: define as skills — agent fetches on demand, appropriate for task-specific guidance
- For automated review agents: push standards (reviewer must see them)
- For implementation agents: pull standards (they fetch what they need)

---

## SandCastle — Parallel AFK Pattern
Pocock's TypeScript library for production-grade parallel agent loops:

```
Planner agent
  → reads all open issues
  → selects batch of parallelizable tasks (respecting DAG blocking)

For each selected task:
  → create git worktree
  → sandbox in Docker container
  → run implementation agent with issue context

For each completed worktree:
  → run reviewer agent (Opus, pushed coding standards)

Merger agent
  → merges passing branches
  → resolves type/test conflicts
  → closes completed issues
```

Each implementer runs in isolation — separate context window, separate worktree. Fresh context per loop iteration (clear, not compact).

---

## Relation to Existing Wiki

- [[summaries/mattpocockskills]] — the skills behind each phase (grill-me, to-prd, to-issues, tdd, improve-architecture)
- [[concepts/context-degradation]] — smart zone / dumb zone at the concept level
- [[concepts/context-compression]] — clear-vs-compact debate
- [[concepts/deep-modules]] — Ousterhout's module design for AI-optimized codebases
- [[concepts/ralph-loop]] — the harness pattern underlying the AFK loop
- [[concepts/verification-pipeline]] — the QA / review gate after implementation
- [[concepts/agent-context-instructions]] — CLAUDE.md as push mechanism for coding standards
