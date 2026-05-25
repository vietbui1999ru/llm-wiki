---
title: "9 Things People Get Wrong With grill-* Skills"
type: summary
tags: [agent-skills, grill-me, planning, context-management, matt-pocock]
sources:
  - "9 Things People Get Wrong With My grill-* skills.md"
created: 2026-05-25
updated: 2026-05-25
---

# 9 Things People Get Wrong With grill-* Skills

Source: Matt Pocock video transcript (YouTube, ~2025). Follow-up to his original skills release, targeting failure modes in `/grill-me` and `/grill-with-docs` usage. See [[summaries/mattpocockskills]] for the base skills reference.

## What Grilling Is (and Isn't)

The grill-* skills relentlessly question you one-at-a-time until you reach shared understanding. They **aid you as an engineer, not replace you**. The skill's quality depends on the quality of the person answering. Grilling is a conversation, not an interview — you must actively direct it.

## The 9 Failure Modes

### 1. Answering High-Fidelity Questions in a Grilling Session

**The distinction (from Ryan Singer's Shape Up):**
- **Low-fidelity questions**: answerable by Q&A alone — e.g., "what URL should this live on?"
- **High-fidelity questions**: need a prototype or working thing to answer — e.g., "how will this form feel with 12 fields?"

High-fidelity questions are **ungrillable**. Trying to answer them in a grilling session wastes time and produces fake consensus.

**Fix**: When you hit an ungrillable question, use `/handoff` to a prototyping session. Learn what you need. Hand off results back to the original grilling session, then continue with grillable questions.

### 2. Grilling on Too Large a Scope

Two problems with oversized scope:
1. High-fidelity questions hide inside large scopes — you can't detect them until you're deep in
2. Context window runs out (~120K tokens is where Pocock estimates the "dumb zone" begins for frontier models)

**Fix**: Before grilling, ask the agent to break the scope into smaller grillable scopes. Grill each independently. Build on solid foundations before pushing scope further out.

### 3. Being Too Passive

If you're passive, the agent runs wild: asks 540 questions, explodes scope, pursues ungradable questions. You lose the session to noise.

**Fix**: Lead the conversation. Actively redirect the scope. Correct the agent when it asks questions that are too granular or off-scope.

### 4. Being Too Active (Grilling Endlessly on Low-Fidelity Questions)

Opposite failure: you keep grilling on things that just need to be built. Over-planning low-fidelity details when you need to get to code.

**Fix**: Know when to stop grilling and implement. If the remaining questions are low-fidelity and you have context budget left, switch to implementation in-session.

### 5. Not Preserving Grilling Session Value

The grilling session context is extremely valuable — it contains design decisions built up over many turns. Two bad behaviors:
- Clearing context before creating a handoff document (throws away the whole session)
- Not converting decisions into code or a handoff artifact

**Fix**: Create a handoff artifact from the grilling session before clearing. Use `/to-prd` or `/handoff` from within the grilling session (not from a fresh context). Never clear context first.

### 6. Using Too Small a Model for Grilling

Grilling depends heavily on **parametric knowledge** (the model's trained understanding of systems, patterns, and edge cases you haven't considered). Small models have weak parametric knowledge.

Contrast: implementation tasks depend mostly on **contextual knowledge** (the files and plans passed in). A smaller model can handle implementation once you have a detailed plan. But grilling needs a frontier model.

**Fix**: Use the best available model for grilling. Downgrade to smaller models only at implementation time.

### 7. Not Valuing the Design Decisions Produced

Related to #5 but distinct: people don't recognize that the Q&A answers in a session are deliverables — not just scaffolding to throw away. Every answered question is a captured design decision.

**Fix**: Treat grilling session context as a primary artifact. Record decisions in CONTEXT.md, ADRs, or a PRD before the session ends.

### 8. Trying to Run Just One Grilling Session

Throughput is limited by model latency between your answers. You can dramatically increase planning throughput by running two sessions in parallel — answer one session's question while the other processes, then switch.

**Fix**: Run 2 grilling sessions simultaneously. Pocock's limit is 2 (3 if one session is doing long-running research). "It's just managing two Slack threads at once."

### 9. Not Improving at Grilling Itself

Grilling is a skill that improves with practice. Better grillees:
- Recognize low vs. high fidelity faster
- Know when to stop and prototype
- Keep scope appropriately tight
- Answer concisely, reducing unnecessary context growth

## Summary Decision Model

```
Is the question answerable in Q&A? → Low-fidelity → Answer it
                                    → High-fidelity → Handoff to prototype session

Is scope too big? → Break it down first, then grill each piece

Am I running out of context? → Stop grilling. Create handoff artifact. Don't clear context first.

Is the model too small? → Switch to frontier model for grilling; save small models for implementation

Am I stuck alone? → Open a second parallel grilling session
```

## Related Pages

- [[summaries/mattpocockskills]] — full skills reference: grill-me, grill-with-docs, tdd, diagnose, handoff
- [[concepts/agent-skills]] — skill architecture reference
- [[concepts/context-degradation]] — why "dumb zone" at ~120K matters
- [[concepts/context-compression]] — how to handle handoffs and context management
