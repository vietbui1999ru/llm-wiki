# Domain Docs

Single-context repo. One shared domain context for all agents.

## CONTEXT.md
Location: repo root (`CONTEXT.md`).
Purpose: shared vocabulary, wiki taxonomy, naming conventions, page structure rules.
Built lazily via `/grill-with-docs` — does not exist until the first domain term crystallizes.
Agents: read and apply if it exists; do not fail or skip if absent.

## ADRs
Location: `docs/adr/`.
Format: `NNNN-short-title.md` per decision.
Agents must not contradict an existing ADR without flagging it first.
ADR threshold: only warranted when a decision is hard to reverse, surprising without context, AND resulted from genuine trade-offs. Otherwise capture in CONTEXT.md.
