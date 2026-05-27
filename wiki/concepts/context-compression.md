---
title: "Context Compression Strategies"
type: concept
tags: [agent-engineering, context-management, compaction, harness, long-horizon]
sources:
  - "Acon Optimizing Context Compression for Long-horizon LLM Agents.md"
  - "Evaluating Context Compression for AI Agents.md"
  - "pdfs/17241_Autoencoding_Free_Contex.pdf"
created: 2026-04-25
updated: 2026-05-27
---

# Context Compression Strategies

When agent sessions grow long, compression is mandatory. The wrong optimization target is *tokens per request* (minimize context size). The correct target is **tokens per task** — total tokens to complete a task, including re-fetch costs when compression loses critical information.

## Four Strategies

### 1. Anchored Iterative Summarization (recommended)
Maintain a structured persistent summary with named sections: session intent, files modified, decisions made, next steps. When compaction triggers, summarize only the newly-truncated span and **merge** it into the existing summary — don't regenerate.

**Why it works**: Structure forces preservation — each section is a dedicated slot that must be filled. Incremental merging prevents compounding loss across multiple compression cycles.

**When to use**: Long-running coding sessions, multi-step tasks, anything where the agent needs to track file modifications and decisions across context windows.

```
[SUMMARY]
Intent: Implement auth middleware for the API
Files modified: src/auth/middleware.ts (added), src/routes/api.ts (updated)
Key decisions: Using JWT with 1h expiry; refresh token in httpOnly cookie
Blocked on: CORS configuration for cross-origin refresh token flow
Next: Write tests for token refresh path
```

---

### 2. Opaque Compression
Produce a compressed representation optimized for reconstruction fidelity rather than human readability. Achieves highest compression ratios (99%+) but sacrifices interpretability.

**Why it works**: Optimizes for what the model needs to reconstruct context, not what a human would find readable.

**When to use**: High-volume automated pipelines where you don't need to inspect the compressed summary; when compression ratio matters more than debuggability.

**Caveat**: Cannot verify what was preserved. Harder to debug when compression loses critical information.

---

### 3. Regenerative Full Summary
Generate a fresh detailed summary from scratch on each compression trigger.

**Why it's worse**: Each regeneration can lose details that prior compressions handled correctly. Compounding across multiple cycles causes drift. Produces readable output but less reliable than anchored iterative across long sessions.

**When acceptable**: Short sessions with a single compression event; when simplicity matters more than accuracy.

### 4. Adaptive Guideline-Optimized Compression (research: Acon)
Use an LLM to compress context guided by a **learned prompt** — the compression guideline is optimized from task failure signals, not handcrafted. Applies separately to interaction history (when length > threshold) and raw observations (when observation > threshold).

**How it works**: Run agent with and without compression; find tasks where compression causes failure; feed contrastive pairs to an optimizer LLM to refine the guideline. Two alternating phases: utility maximization (fix failures) and compression maximization (shorten successes). Gradient-free — works with any API model.

**Why it can outperform fixed-prompt compression**: The guideline learns environment-specific signals — what types of information cause failure when dropped (e.g., API auth tokens, account balances, due dates). Generic prompts miss these domain constraints.

**When to use**: Multi-step agentic tasks with heterogeneous tool outputs; when generic summarization degrades task performance; when you have training trajectories to optimize from.

**Cost warning**: History compression breaks KV-cache prefix stability, forcing recomputation — this can make total API cost *higher* than no compression. Observation compression avoids this: compress before the observation enters history. Prefer observation compression in cost-sensitive settings.

**Distillation**: Once the large-model guideline is optimized, distill the compressor into a small model (e.g., Qwen3-14B via LoRA) to eliminate the overhead of calling a large LLM per step. Distilled compressors retain >95% of teacher accuracy across all benchmarks.

**Benchmark results** (AppWorld / OfficeBench / 8-obj QA): 26–54% peak token reduction; maintained or improved task performance. Small agent improvement (Qwen3-14B): +32% AppWorld, +20% OfficeBench, +46% QA.

Source: Acon paper (KAIST + Microsoft, 2025; AppWorld/OfficeBench/8-obj QA benchmarks)

---

## Key Results from Compression Evaluation (Factory.ai, 2025)

Factory.ai evaluated three production compression approaches on 36,611 messages from real software engineering agent sessions. Grading via GPT-5.2 LLM judge, six dimensions (accuracy, context awareness, artifact trail, completeness, continuity, instruction following).

| Method | Overall | Accuracy | Context | Artifact | Continuity |
|---|---|---|---|---|---|
| Factory (anchored iterative) | **3.70** | **4.04** | **4.01** | **2.45** | 3.80 |
| Anthropic (regenerative structured) | 3.44 | 3.74 | 3.56 | 2.33 | 3.67 |
| OpenAI (opaque /compact) | 3.35 | 3.43 | 3.64 | 2.19 | **3.77** |

Compression ratios: Factory 98.6%, Anthropic 98.7%, OpenAI 99.3%.

Key finding: **artifact trail is unsolved** — all methods scored 2.19–2.45 / 5.0 on tracking file modifications. Summarization alone cannot reliably track file state across long sessions; dedicated artifact indexing in the harness is likely needed.

Accuracy gap: Factory 4.04 vs OpenAI 3.43 (0.61 difference) — reflects file paths and error codes surviving compression. OpenAI's opaque endpoint treats file paths as "low-entropy content" and discards them, which is catastrophically wrong for coding agents.

---

## Token Budget Allocation

Understanding where tokens go helps decide what to protect vs. compress:

| Component | Typical Range | Compress? |
|---|---|---|
| System prompt | 500–2000 tokens | Never |
| Tool definitions | 100–500 per tool | No |
| Active task state | Variable | Never |
| Critical decisions | Variable | No — move to summary |
| Recent turns (last 3–5) | Variable | No |
| Tool outputs (current) | Variable | Partial — keep head+tail |
| Old message history | Grows unbounded | Yes — primary compression target |
| Retrieved documents | Often largest | Selective — mask served-purpose docs |

## KV-Cache Optimization

KV-cache hit rate determines recomputation cost. Cache hits require prefix stability — the beginning of the prompt must be identical across requests.

**Design rules:**
1. Place system prompts and tool definitions at the very start — they're stable across turns
2. Never put timestamps, session IDs, or request-specific data in the system prompt
3. Keep dynamic content (current task, user query) at the end
4. Consistent formatting across requests — even whitespace changes invalidate cache

```python
# Cache-unfriendly: timestamp in system prompt
system = f"Current time: {datetime.now().isoformat()}\nYou are..."

# Cache-friendly: stable system prompt, dynamic data appended
system = "You are a code assistant. Current time is provided per-request."
```

## Practical Decision Rule

- **Single session, no explicit complexity**: default to anchored iterative summarization
- **High-volume pipeline, compression ratio critical**: opaque compression
- **Quick prototype, one compression expected**: regenerative is fine
- **Never**: aggressive deletion without a summary — you will lose file modification history

## Clear Over Compact — Now Community Consensus

Matt Pocock argues against compacting and prefers hard context clears:

> "I much prefer my AI to behave like the guy from Memento because this state is always the same. Every time you do it, you clear and you go back to the beginning."

His argument: compaction introduces "sediment" — each compressed summary is imperfect, and multiple cycles compound drift. Clearing gives a deterministic, reproducible starting state.

**Updated (2026-05-04)**: Among experienced practitioners running harness-based AFK coding workflows (r/ClaudeCode + r/opencodeCLI, 2026-05, n≈30), clear-over-compact is **majority practice** — not a contrarian position. Every active framework in that community (GSD, Dangeresque, SandCastle, vanilla loops) enforces fresh context per task.

**This evidence is scoped**: the sample is ~30 experienced developers self-selected into harness-heavy workflows on two subreddits. It does not generalize to interactive/exploratory sessions, non-engineer users, or workflows without durable filesystem state.

**When clear-over-compact is valid**: filesystem stores all state (issue files, commits, PRDs); harness re-injects state at session start. The key design principle: **make clearing safe, then prefer clearing**.

**When compact wins over clear:**
- No durable filesystem layer — clearing loses state that can't be reconstructed
- Interactive debugging sessions where the chain of reasoning *is* the artifact
- Exploratory sessions where you don't yet know what to externalize to files
- Conversational research where history continuity is the product
- Long sessions with a non-engineer who can't reconstruct context from files

**When anchored iterative summarization is still better**: any of the "when compact wins" cases above.

**OpenCode hook extension**: OpenCode exposes `experimental.session.compacting` — a hook that lets plugins inject domain state into compaction summaries or replace the compaction prompt entirely. This enables custom anchored iterative summarization at the harness level, more reliable than system-prompt instructions. See [[comparisons/claude-code-vs-opencode-plugins]].

## Strategic Compaction Checkpoints

From ECC's `strategic-compact` skill — explicit heuristics for *when* to compact:

**Compact at logical seams:**
- After research/exploration, before implementation begins
- After completing a milestone, before starting the next task
- After debugging session ends, before resuming feature work
- After a failed approach, before trying a different strategy

**Do not compact:**
- Mid-implementation — you'll lose variable names, file paths, partial state
- Mid-debugging — you'll lose the chain of reasoning that is the artifact

**Token optimization settings** that complement compaction (from [[entities/everything-claude-code]]):
- `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50` — compact at 50% of context (vs default 95%) — prevents quality degradation from near-full context
- `MAX_THINKING_TOKENS=10000` — caps hidden thinking cost per request (claimed ~70% reduction)
- `CLAUDE_CODE_SUBAGENT_MODEL=haiku` — subagents use a cheaper model tier

All claimed impact numbers from ECC README; not independently verified. The pattern itself aligns with community consensus on token efficiency.

---

## Serialization Format (orthogonal layer)

Compression (selection) and serialization (encoding) are independent axes:
- Compress first: select what context to keep
- Then serialize efficiently: encode it with minimal token overhead

Schema-first formats (ONTO, TOON) achieve 40-60% reduction on structured data vs JSON.
Most valuable for: large homogeneous datasets injected into prompts. See [[concepts/llm-serialization-formats]].

---

## Research: Learned Soft Compression (SAC)

Distinct from the operational strategies above — SAC is a model architecture that produces compressed KV representations for serving. Not a drop-in tactic for Claude Code sessions.

**Semantic-Anchor Compression (SAC)** — Northeastern University / NiuTrans Research, 2025. Code: https://github.com/lx-Meteors/SAC

Core argument: autoencoding-based training objectives (ICAE, 500xCompressor, EPL) conflict with downstream task requirements — AE gradient and LM gradient are nearly orthogonal in parameter space, so optimizing one impairs the other.

**SAC method**: select anchor tokens directly from context (uniform chunking at compression ratio `r`), augment each with a learnable anchor embedding, apply bidirectional attention in the encoder (anchors see full context). Decoder remains causally masked. No autoencoding objective — trains on downstream task loss only.

**Results at 15× compression (vs EPL, second-best baseline), Llama-3.2-1B backbone:**
- In-domain MRQA: +6.7% F1 / +8.2% EM
- Out-of-domain MRQA: +6.9% F1 / +9.2% EM
- vs ICAE: +23.5% F1 / +26.8% EM
- Long-context summarization (32K input): SAC 18.49 avg ROUGE-1 F1 vs EPL 17.61
- Scales to 3B and 8B without diminishing returns

Limitations: requires LoRA fine-tuning; benchmarks limited to MRQA/QMSum/GovReport; frontier-scale generalizability unverified.

---

## Related Pages

- [[concepts/context-degradation]] — the failure modes compression prevents
- [[concepts/agent-harness]] — where compaction fits in the harness component model
- [[concepts/ralph-loop]] — filesystem as durable state across clean context windows (the complement to compression)
- [[concepts/dynamic-context-pruning]] — mid-session context reduction via Compress tool + deduplication + purge-errors; complements compaction
- [[entities/everything-claude-code]] — ECC's `strategic-compact` skill and token optimization settings
