---
date: 2026-05-06
type: reasoning
domain: wiki-authoring
severity: high
pages-affected: summaries/wshobson-agent-orchestration, summaries/opencode-model-switching-reddit, concepts/council-pattern, syntheses/agent-primitive-selection
---

# Unverified stats elevated to architectural guidance

## What happened

Multiple times in this wiki, a number or performance claim from a non-empirical source was written into a wiki page as fact, then propagated into downstream routing recommendations without flagging its origin:

1. **"Opus achieves 65% fewer tokens on complex tasks"** — from wshobson's repo README (self-reported marketing). No methodology, no baseline. Written into `wshobson-agent-orchestration.md` as a benchmark justifying model routing. Repeated in `agent-primitive-selection.md` as a routing rule.

2. **"per AA bench"** in opencode-model-switching-reddit — "AA bench" is never defined. Likely a casual Reddit reference to an informal evaluation. Written as if citing a named benchmark.

3. **Council cost "10-15x single query"** — derived from one constructed arithmetic example (3 models × 1K tokens). Applied as a general rule without caveating: (a) only applies to full 3-stage council, (b) output tokens not modeled, (c) Stage 1+3 only is ~6-7x.

## Pattern

Source is promotional / self-reported / single Reddit comment → written into wiki as fact → cited downstream as a rule → shapes recommendations.

"Multiple wiki pages agree" is not corroboration if all pages derived from the same single raw source.

## Prevention rule

Before writing any performance number or benchmark name into a wiki page:
1. Can I name the methodology (what was measured, against what baseline)?
2. Is the source independent of the thing being measured (not a self-report)?
3. If no to either: write `(claimed, unverified)` inline — never drop the qualifier.

For downstream pages: only inherit numbers that have explicit sources. If the upstream page says "unverified", the downstream page must too.
