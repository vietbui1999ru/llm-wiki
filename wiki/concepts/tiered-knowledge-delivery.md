---
title: "Tiered Knowledge Delivery (Push / Hook / Pull)"
type: concept
tags: [agent-engineering, knowledge-management, context-engineering, wiki-architecture, token-cost]
sources: ["docs/wiki-dual-use-audit-2026-06.md"]
created: 2026-07-23
updated: 2026-07-23
---

# Tiered Knowledge Delivery (Push / Hook / Pull)

The mechanism behind this wiki's "agent-first" claim (see [ONBOARDING.md](../../ONBOARDING.md)): agents get pre-synthesized structure without paying a search cost for it, while the bulk of the wiki stays out of every session's context.

## Two failure modes this replaces

- **Pure preload**: push the whole index/wiki into every session. Correct but wasteful — a prior decision removed a 32KB wiki index from global startup, reclaiming ~8,400 tokens/session, precisely because most sessions never touch most pages.
- **Pure on-prompt search**: nothing is preloaded; every fact requires the agent to decide to invoke `wiki-context` / `qmd query` and pay a retrieval round-trip. Cheap when idle, but only as reliable as the agent's judgment to search — high-frequency, high-cost-of-violation knowledge (LOC gate, model-tier routing, epistemic discipline) shouldn't depend on that judgment firing every time.

## The three tiers

| Tier | Delivery | Cost when idle | Contents |
|---|---|---|---|
| **Tier 0 — push** | Always-loaded via CLAUDE.md `@`-imports | Paid every session | `mistakes/global-prevention-rules.md` (capped ≤45 non-blank lines, gated by `claude-setup/scripts/check-gpr-cap.sh`), `claude-setup/rules/applied-ai.md` |
| **Tier 1 — hook** | Fires only on a specific trigger (PreToolUse/PostToolUse) | Zero | e.g. `capture-mistake` firing on self-correction; sparse today — most of the model still runs on Tier 0 + Tier 2 |
| **Tier 2 — pull** | JIT via `wiki-context` skill / `qmd query`, on demand | Zero | Everything else — `wiki/concepts/`, `patterns/`, `entities/`, `syntheses/`, etc. The default; nothing large goes here-to-everywhere |

Promotion between tiers is decided by **frequency × cost-of-violation**, not by how interesting a page is. Content earns Tier 0 only if it's both hit often and expensive to get wrong.

## Provenance

Decided 2026-06-12 via a read-only 4-lens agent council (agent-consumer, human-learner, maintainer/cost, adversarial verifier) — see `docs/wiki-dual-use-audit-2026-06.md` for the full scorecard, prioritized fix list, and the hard constraint this model must satisfy: *pull stays the default; nothing large gets pushed into every session*.

Correctness of Tier 0 is checked by the wiki's own lint procedure's Tier-0 distillation sync step (CLAUDE.md "Lint" operation) — for each wikilink cited in `applied-ai.md` / `global-prevention-rules.md`, verify the linked page still says the same thing.

## Open question this doesn't answer

The model says *where* knowledge lives once it's structured. It says nothing about *how raw session experience becomes* Tier-0/Tier-2 material in the first place — right now that's manual (`synthesize-mistakes`, ad-hoc wiki ingest). [[concepts/knowledge-crystallization-cycle]] proposes a formal answer to that gap *(proposed, single-source, not yet reviewed)* — if adopted, it would be the authoring pipeline that feeds this delivery model, not a replacement for it.

## Related

- [[concepts/compounding-knowledge-base]] — why the pull layer (Tier 2) compiles rather than just indexes
- [[concepts/context-compression]] — the token-cost discipline this model is built to satisfy
- [[concepts/agent-self-correction]] — a Tier 2 pull pattern; [[concepts/instinct-clustering]] is its push-equivalent counterpart
- [[concepts/nurture-first-development]] / [[concepts/knowledge-crystallization-cycle]] — proposed theory for the authoring side, not yet adopted
