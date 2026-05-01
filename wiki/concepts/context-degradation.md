---
title: "Context Degradation Patterns"
type: concept
tags: [agent-engineering, context-management, context-rot, harness, long-horizon]
sources: []
created: 2026-04-25
updated: 2026-04-25
---

# Context Degradation Patterns

Context degradation is not binary — it's a continuum of predictable failure modes as context length grows. Knowing the five patterns by name lets you diagnose failures correctly and pick the right mitigation.

## Smart Zone / Dumb Zone (Practitioner Model)

A practitioner mental model from Dex Hyp (Human Layer) and popularized by Matt Pocock: LLM performance has a **smart zone** (low token count, attention relationships least strained) and a **dumb zone** (high token count, attention degraded).

**Empirical threshold: ~100k tokens.** Pocock claims this holds regardless of advertised context window size (200k or 1M). The larger windows add more dumb zone, not more smart zone — the attention scaling is quadratic regardless of limit.

Implication for task sizing: keep tasks scoped so the agent completes them within ~100k tokens. This maps to the same principle as the degradation thresholds below, but gives a concrete absolute number practitioners can target.

---

## The Five Patterns

### 1. Lost-in-Middle
**What**: Information in the center of the context window receives less attention than content at the start or end. Attention distribution follows a U-curve — high at edges, degraded in the middle.

**Symptoms**: Agent ignores instructions or facts mentioned mid-conversation; references only the most recent or earliest information.

**Mitigation**: Move critical information to attention-favored positions (beginning or end). Use explicit markers to highlight critical content. Split long contexts to reduce middle span.

---

### 2. Context Poisoning
**What**: An early error gets referenced and built upon in subsequent turns, compounding incorrect reasoning across the conversation.

**Symptoms**: Agent confidently makes claims that contradict established facts; incorrect assumptions spread across turns even after the original error was corrected.

**Mitigation**: Verify critical claims before they propagate. Use [[concepts/context-compression]] to discard turns containing errors rather than summarizing them forward.

---

### 3. Context Distraction
**What**: Irrelevant information overwhelms relevant content, causing the agent to respond to the wrong parts of context.

**Symptoms**: Agent drifts off-task; incorporates tangential details from earlier turns into responses where they don't belong.

**Mitigation**: Selective masking — explicitly remove or summarize turns that have served their purpose. Keep the active task and recent turns; offload everything else to filesystem.

---

### 4. Context Confusion
**What**: The agent cannot determine which context applies when multiple conflicting or ambiguous contexts are present.

**Symptoms**: Agent hedges between two interpretations; produces inconsistent output across similar requests in the same session; asks clarifying questions that were already answered.

**Mitigation**: Partition contexts clearly with section markers or roles. Avoid injecting multiple system-level instructions with different scopes. Use explicit context scope tags ("for this task only", "global rule").

---

### 5. Context Clash
**What**: Accumulated information directly contradicts itself, creating unresolvable conflicts the model cannot navigate.

**Symptoms**: Agent output is inconsistent across the session; requests confirmation for things already decided; produces two different answers to the same question in the same response.

**Mitigation**: Compaction — summarize and reconcile contradictions before they accumulate. When requirements change, explicitly note the change and override rather than appending.

## Degradation Thresholds

Compaction should trigger before degradation becomes severe:

| Threshold | Action |
|---|---|
| 70% context window | Warning — start planning compaction |
| 80% context window | Trigger compaction |
| 90% context window | Aggressive compaction — preserve only active task state and critical decisions |

The exact thresholds depend on model behavior. Some models degrade gracefully; others show sharp performance cliffs.

## Detection Heuristic

Ask: *Is the agent ignoring something I told it earlier?* That's lost-in-middle or distraction. *Is it doubling down on a mistake?* That's poisoning. *Is it giving inconsistent answers?* That's confusion or clash.

## Related Pages

- [[concepts/context-compression]] — the three strategies for active compaction
- [[concepts/agent-harness]] — harness-level context management (compaction, masking, offloading)
- [[concepts/ralph-loop]] — loop pattern that manages context across multiple windows using filesystem state
- [[summaries/mattpocockworkflow]] — source of the smart zone / dumb zone model and 100k threshold
