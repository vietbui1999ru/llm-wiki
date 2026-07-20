---
title: "Nurture-First Development (NFD)"
type: concept
tags: [agent-engineering, agent-development-methodology, knowledge-crystallization, tacit-knowledge, memory, three-layer-architecture]
sources: ["pdfs/2603.10808v1.pdf"]
created: 2026-07-20
updated: 2026-07-20
---

# Nurture-First Development (NFD)

A proposed methodology for building **domain-expert** AI agents by *growing* them through sustained conversation, rather than *building* them upfront. Development and deployment run concurrently: the agent starts as minimal scaffolding and accumulates expertise from daily use, which is periodically consolidated into reusable knowledge assets. Framework-agnostic — instantiable on any harness with persistent memory + on-demand skills (the source paper cites Claude Code and "OpenClaw"; the pattern applies equally to Codex, Copilot, Pi, Gemini setups). Source: [[summaries/nurture-first-agent-development]] (Zhang 2026) — a **position paper**, so the framework is proposed, not empirically validated.

## Three paradigms of agent development

| | Encoding | Developer | Update mechanism | Ceiling |
|---|---|---|---|---|
| **Code-first** | deterministic pipelines/rules | software engineer | code change + redeploy | engineering capacity |
| **Prompt-first** | static system prompt / few-shot | prompt engineer | edit the prompt | context window |
| **Nurture-first** | evolving memory files | **domain practitioner** | conversation + crystallization | memory search quality |

Code-first and prompt-first both assume *build → then → deploy*. NFD's claim: expertise is **tacit, personal, and evolving**, so any static upfront encoding starts decaying immediately. NFD dissolves the build/deploy boundary. Its defining move is *who develops the agent* — the domain expert, through daily dialogue, not an engineer. (Contrast the pure code-first pole in [[syntheses/minimal-coding-agent]], where an agent is a fixed loop + tools you write once.)

## Three-Layer Cognitive Architecture

Organize the agent's knowledge by **volatility × personalization**:

- **Constitutional** — identity, principles, rules; loaded every session; low volatility; hold *indices and pointers, not detail*; keep it small (budget ~10–15% of context). (Cross-agent forms: `MEMORY.md`/`AGENTS.md`/`SOUL.md`/`USER.md`, `CLAUDE.md`.)
- **Skill** — modular, single-responsibility task capabilities loaded on demand; medium volatility; the **home for crystallized knowledge**; skills coordinate through shared memory files, not direct invocation. (Cross-agent: `SKILL.md` + `references/` + `scripts/`.) See [[concepts/agent-skills]].
- **Experiential** — dated logs, case memories, error patterns from *use*; semantic-searched; high volatility; append-only. (Cross-agent: `memory/YYYY-MM-DD.md`.) Overlaps [[concepts/memory-bank-pattern]] and [[concepts/agentic-memory-tool]].

Two flows: **grounding** (down — principles/skills interpret new experience) and **crystallization** (up — experience consolidated into skills/constitution).

## The Knowledge Crystallization Cycle (the engine)

The mechanism that turns fragmented conversational knowledge into structured assets — an operationalization of Nonaka–Takeuchi *externalization* (tacit→explicit). An ascending spiral of four phases:

1. **Conversational Immersion** — expertise transfers implicitly through operational dialogue; the agent captures the *reasoning*, not just conclusions.
2. **Experiential Accumulation** — every interaction is logged and tagged. Six categories: operational records, reasoning traces, pattern observations, error records, contextual annotations, insight fragments (tags like `[DECISION]`/`[INSIGHT]`/`[ERROR]` make later extraction cheap).
3. **Deliberate Crystallization** — a periodic, human-in-the-loop batch job: extract patterns → structure → **de-contextualize** (generalize) → **validate against the full corpus** → integrate with version tracking.
4. **Grounded Application** — crystallized patterns re-enter service as **hypotheses**, tested against new experience; contradictions trigger re-crystallization.

**Key safeguard:** value is monotonic across cycles *only because* a human validates which patterns get promoted. Automated, unreviewed crystallization loses that guarantee — and the source names full self-directed crystallization as the paradigm's main open problem (the "crystallization bottleneck"). This is the same human-approval discipline as [[concepts/preference-feedback-loop]] and the mistakes→rules distillation this wiki already runs.

## Operational patterns

- **Dual-Workspace** — a *surgical* workspace (full filesystem access; scaffolding, bulk migration, crystallization, refactoring — treats the knowledge base as a data structure) separate from a *nurturing* workspace (the runtime conversational channel where immersion/accumulation happen). Both share file state. Maps cleanly onto: agentic coding tool (surgical) + conversational assistant (nurturing).
- **Spiral Development** — Bootstrap (aim for bootability, not completeness) → Nurture → Crystallization Checkpoint → repeat, with each revolution raising the baseline. Triggers: scheduled, threshold, or event.

## Why it matters here

NFD is essentially the theory behind *this wiki*: a Constitutional layer (`CLAUDE.md`, `MEMORY.md`), a Skill layer (`wiki/` pages + skills), and an Experiential layer (`mistakes/`, `log.md`, dated captures), with `synthesize-mistakes` / ingest as crystallization operations promoting fragments into durable rules. It gives that practice a name and a formal shape. Closely related: [[concepts/compounding-knowledge-base]] (making each unit of work make later units easier) and [[concepts/context-compression]] (curating the experiential layer to preserve signal).

## Caveats

The backing paper is conceptual with a single-user, no-control case study — adopt the *structure* (layering, tagged experiential logs, human-validated crystallization checkpoints) as a design vocabulary, not as evidence of measured performance. Its own limitations apply: cold-start low value, bias absorption (the agent can crystallize a *bad* habit as readily as a good one), no objective quality metric for nurtured knowledge, and org-scale sharing unsolved.
