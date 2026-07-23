---
title: "Knowledge Crystallization Cycle (KCC)"
type: concept
tags: [agent-engineering, knowledge-management, crystallization, tacit-knowledge, memory, compounding]
sources: ["pdfs/2603.10808v1.pdf"]
created: 2026-06-30
updated: 2026-07-23
---

# Knowledge Crystallization Cycle (KCC)

*(proposed, single-source — same position paper as [[concepts/nurture-first-development]]; not yet reviewed against this wiki's own patterns/rules split. Pending synthesis check before any of "Our Stack Implementation" below is treated as adopted.)*

The core developmental mechanism of [[concepts/nurture-first-development]]. Converts fragmented conversational knowledge into structured, reusable Skill Layer assets. Operationalizes Nonaka & Takeuchi's tacit-to-explicit knowledge conversion within an agent memory context.

---

## Four Phases

```
Phase 1: Conversational Immersion
    Operational dialogue; knowledge transferred implicitly.
    No explicit "teaching sessions" required.
    ↓
Phase 2: Experiential Accumulation
    Fragments tagged and logged in Experiential Layer.
    Six categories: [OPERATIONAL], [REASONING], [PATTERN],
                    [ERROR], [CONTEXT], [INSIGHT]
    ↓
Phase 3: Deliberate Crystallization (surgical workspace)
    Scope filter → pattern extraction → human review →
    de-contextualize → validate against full corpus → promote
    ↓
Phase 4: Grounded Application
    Crystallized knowledge in active service.
    Generates new experience at higher baseline.
    Contradictions trigger re-crystallization.
```

Each revolution of the cycle raises the knowledge baseline. The spiral doesn't close — it expands.

---

## Algorithm 1: Crystallization Process

```
Input: Knowledge state K = (C, S, E), scope θ
Output: Updated state K'

1. D ← ScopeFilter(E, θ)          # select relevant Experiential entries
2. P ← ExtractPatterns(D)          # automated pattern detection
3. P* ← HumanReview(P)             # user validates — the critical safeguard
4. for each validated pattern p ∈ P*:
5.     k ← Structure(p, S)         # format for Skill Layer
6.     k ← Decontextualize(k)      # generalize beyond original context
7.     if Validate(k, E):          # check against full corpus, not just scope
8.         S ← S ∪ {k}            # promote to Skill Layer
9.         E ← E \ {entries consolidated into k}
10. return K' = (C, S', E')
```

**Non-regression guarantee**: H(S') ≥ H(S) — Skill Layer information content never decreases after validated crystallization. Human review (line 3) + corpus validation (line 7) together prevent false patterns from being promoted.

---

## Six Experiential Fragment Categories

| Tag | Content | Crystallization path |
|---|---|---|
| `[OPERATIONAL]` | Decisions made, actions taken, outcomes | Contributes to aggregate statistics; rarely crystallized individually |
| `[REASONING]` | Decision logic, assumptions, alternatives considered | High crystallization value; reasoning traces improve efficiency |
| `[PATTERN]` | Regularities across experiences ("every time X, Y tends to follow") | Primary crystallization target; becomes Skill reference content |
| `[ERROR]` | Mistakes + corrective principles | High-priority crystallization target; becomes prevention rules |
| `[CONTEXT]` | Environmental metadata, domain-state annotations | Enriches retrievability of other fragments |
| `[INSIGHT]` | Standalone principles articulated during conversation | Often immediately promotable to Skill Layer; don't need accumulation |

Insight fragments may bypass accumulation entirely — promote directly if standalone. Error records need accumulation before patterns emerge. Operational records rarely justify individual crystallization.

---

## Crystallization Triggers

| Mode | When | Best for |
|---|---|---|
| **Scheduled** | Regular intervals (weekly, monthly) | Steady experiential accumulation; predictable domains |
| **Threshold** | Volume > N uncrystallized entries OR performance drift detected | Domains with bursty activity |
| **Event-driven** | After significant domain events (regime change, phase transition, major decision) | Strategic, advisory, research domains |

---

## Crystallization Efficiency

Three factors determine how much structured knowledge emerges from a given experiential corpus:

1. **Experience diversity** — varied situations crystallize better than repetitive data; a corpus of 50 distinct cases > 200 variations of the same case
2. **Annotation quality** — [REASONING] traces crystallize efficiently; bare [OPERATIONAL] records don't
3. **Pattern density** — domains with strong regularities (financial patterns, legal precedent) yield higher efficiency than idiosyncratic domains

---

## Our Stack Implementation

We run partial KCC. Mapping:

| KCC Phase | Our Implementation | Gap |
|---|---|---|
| Immersion | Daily Claude Code / OpenCode / Pi sessions | None — happens naturally |
| Accumulation | `mistakes/raw-log.md` (hook-captured) | Only [ERROR] captured; [INSIGHT]/[PATTERN] not tagged |
| Crystallization | `synthesize-mistakes` skill → `global-prevention-rules.md` | Scope limited to errors; no Skill Layer promotion path |
| Grounded Application | `wiki-context` skill (retrieves crystallized knowledge) | Incomplete — wiki-context retrieves wiki pages but not `global-prevention-rules.md` inline |

**Proposed fix**: Add `[INSIGHT]` and `[PATTERN]` tagging to AGENTS.md (all harnesses). When tagged fragments accumulate, route to wiki ingest rather than `synthesize-mistakes`. The wiki ingest pipeline IS the crystallization algorithm — it already implements Algorithm 1 via: `pdf-ingest` / `pre-digest` (scope+extract) → comprehension questions (human review) → wiki page (de-contextualize+promote).

---

## Related Pages

- [[concepts/nurture-first-development]] — parent paradigm; three-layer architecture; our-stack synthesis
- [[concepts/compounding-knowledge-base]] — KCC is the formal mechanism behind wiki compounding
- [[concepts/agent-self-correction]] — wiki-as-oracle = Grounded Application phase
- [[concepts/agent-skills]] — Skill Layer is the destination for crystallized patterns
- [[concepts/agentic-memory-tool]] — Experiential Layer implementation
