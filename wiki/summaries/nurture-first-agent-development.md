---
title: "Nurture-First Agent Development (Zhang 2026)"
type: summary
tags: [agent-engineering, agent-development-methodology, knowledge-crystallization, tacit-knowledge, memory-augmented-agents, paper]
sources: ["pdfs/2603.10808v1.pdf"]
created: 2026-07-20
updated: 2026-07-20
---

# Nurture-First Agent Development (Zhang 2026)

**Paper:** *Nurture-First Agent Development: Building Domain-Expert AI Agents Through Conversational Knowledge Crystallization.* Linghao Zhang (NJUPT). arXiv 2603.10808v1, cs.AI/cs.HC/cs.SE. **Position/conceptual paper** — proposes a framework and illustrates it with one single-user case study; not an empirical evaluation (the author says so explicitly). Treat all claims as *proposed*, not validated.

## Problem

LLM agent frameworks (AutoGPT, MetaGPT, AutoGen, Claude Code, "OpenClaw") shifted the bottleneck from raw capability to **knowledge encoding** — the "configuration gap" between a foundation model's general ability and the domain expertise needed for outputs a practitioner would trust. Two existing paradigms both assume development is a **discrete phase before deployment**:

- **Code-first** — expertise as deterministic pipelines/rules. Reliable but can't capture judgment; updates need engineering cycles; captures the developer's understanding frozen at write-time.
- **Prompt-first** — expertise as system prompts / few-shot. Accessible but scales poorly (prompt outgrows context window), and prompts are static snapshots with no learning-from-use mechanism (DSPy tunes params but the artifact stays fixed).

Zhang argues this "build then deploy" assumption mismatches the nature of expertise, which is **tacit** (Polanyi; Nonaka–Takeuchi), **personal**, and **continuously evolving** — a static encoding decays from the moment it's written.

## Proposed method: Nurture-First Development (NFD)

The agent is "born with minimal scaffolding and raised through sustained interaction." Development and deployment are **concurrent, interleaved**. Three propositions: (1) development–deployment fusion; (2) conversational knowledge acquisition (dialogue, not upfront spec); (3) crystallization *as* development (the core dev act is consolidating conversational fragments into reusable assets, not writing code/prompts). Explicitly inspired by workspace-first infra with persistent memory + on-demand skills (cites "OpenClaw" and Claude Code as enabling architectures).

**Three-Layer Cognitive Architecture** — knowledge partitioned by *volatility* × *personalization*:
- **Constitutional** — identity/principles (`SOUL.md`, `AGENTS.md`, `USER.md`, `MEMORY.md`); loaded every session; low volatility; should hold *indices and principles, not detail*; budget ~10–15% of context.
- **Skill** — modular task capabilities (`SKILL.md` + `references/` + `scripts/`); loaded on demand; medium volatility; the primary container for crystallized knowledge; one responsibility per skill; coordinate via shared memory, not direct calls.
- **Experiential** — dated logs, case memories, patterns, errors (`memory/YYYY-MM-DD.md`); semantic search; high volatility; append-only; the raw material crystallization draws from.

Flow: **downward = grounding** (principles/skills interpret new experience), **upward = crystallization** (experience consolidated into skills/constitution).

**Knowledge Crystallization Cycle (KCC)** — the core developmental engine; operationalizes Nonaka–Takeuchi *externalization* (tacit→explicit). Four phases forming an ascending spiral: (1) **Conversational Immersion** (knowledge transfers implicitly through operational dialogue — the agent gets the *reasoning*, not just conclusions); (2) **Experiential Accumulation** (six tagged categories: operational records, reasoning traces, pattern observations, error records, contextual annotations, insight fragments — via tags like `[DECISION]`/`[INSIGHT]`/`[ERROR]`); (3) **Deliberate Crystallization** (5 sub-ops: pattern extraction → structuring → de-contextualization → validation → integration; needs the surgical workspace); (4) **Grounded Application** (crystallized patterns are *hypotheses* re-tested against new experience; contradictions trigger re-crystallization).

Formalized: knowledge state `K_t = (C_t, S_t, E_t)`; value `V(K) = α·Breadth(E) + β·Structure(S) + γ·Align(C,U)` with the dominant term shifting over the lifecycle (early: α; post-crystallization: β; mature: γ). **Non-decreasing Value proposition**: *if* crystallization only promotes human-validated patterns, value is monotonic across cycles — the human-in-the-loop review (Algorithm 1, line 3) is the safeguard.

**Operational framework:**
- **Dual-Workspace Pattern** — *Surgical* workspace (full filesystem access; scaffolding, bulk migration, crystallization, refactoring — "knowledge base as a data structure"; Claude Code fits) vs *Nurturing* workspace (runtime conversational channel; immersion + accumulation; "OpenClaw" fits). Shared file state bridges them.
- **Spiral Development Model** — Phase 0 Bootstrap (1–3 days, aim for bootability not completeness; optional historical-data migration) → Phase 1 Initial Nurturing (1–3 wks) → CC1 → Phase 2 Structured Nurturing (1–3 mo) → CC2 → Phase 3+ mature (crystallization as routine maintenance; agent may self-propose candidates). Triggers: scheduled / threshold / event.

## Key results (illustrative case study — read with care)

Single financial-research analyst (5+ yrs, ~400 historical notes over 18 mo). Bootstrap migrated notes and extracted 10 themes / 6 error types / 3 approaches. Table 2 progression (Wk1-3 → post-CC1 → Wk9-12 → post-CC2):

| Metric | Wk1-3 | post-CC1 | Wk9-12 | post-CC2 |
|---|---|---|---|---|
| Useful analyses (%) | 38 | 52 | 71 | 74 |
| Case recalls | 2 | 5 | 12 | 15 |
| Bias flags | 0 | 1 | 4 | 5 |
| Skill refs populated | 2 | 4 | 6 | 8 |
| Error patterns | 6 | 8 | 10 | 12 |

Three illustrative episodes: (A) a sector-specific correction (capex/FCF weighting) generalized into a design principle; (B) a tacit "asymmetric conviction / decay-rate-of-uncertainty" strategy externalized into `binary-event-strategy.md`; (C) an emergent `narrative-drift-analysis` skill arising from repeated ad-hoc requests. Reported qualitative wins: **forced externalization** exposed inconsistencies in the analyst's own framework; agent as **institutional memory**; crystallized methodology docs more accurate than self-reported theory (derived from observed practice).

## Limitations (author-stated)

Single-user, **no control group**, subjective "usefulness" metric — feasibility demo, not proof. Open challenges: cold-start (early agent has low value), org-scale knowledge sharing/ownership, quality assurance (agent may absorb user *biases*; no test-coverage analog), context-window economics, and the **crystallization bottleneck** (still semi-manual — full self-directed crystallization is unsolved).

## Applicability

Best when expertise is tacit + personal + evolving + conversational + pattern-recognition-heavy (legal/medical/financial advisory, research, creative, strategy). Fully formalizable/static domains (e.g. tax-form processing) are better served code-first. Distinguishing feature: the **domain practitioner is the developer** (democratizes agent-building); the scalability ceiling is *memory search quality*, not engineering capacity or context size.

## Connections

- Conceptual **opposite pole** to the build-then-run tutorials in [[syntheses/minimal-coding-agent]] — those are pure code-first; NFD dissolves the build/deploy boundary.
- Sits on top of [[concepts/agent-harness]] (Model + Harness): NFD is a *development methodology* for growing the harness's knowledge, not a harness itself.
- Experiential-layer curation + context budgeting relate to [[concepts/context-compression]].
- Distilled, generalized-across-agents concept page: [[concepts/nurture-first-development]].
