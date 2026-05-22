# Chairman: anthropic/claude-opus-4-6

## Question

what is the difference between a skill and a subagent in an AI coding harness

## Council

- Voice A: anthropic/claude-sonnet-4-6 → voice_a.md
- Voice B: openai/gpt-5.4 → voice_b.md

## Synthesis

## Points of Agreement

Both voices converge completely on the core architecture:

- **Skill = prompt injection into caller's context window.** No isolation, no separate inference call. Enriches the current agent.
- **Subagent = separate context window with independent execution.** Returns summary only. Main context stays clean.
- **Skills can preload into subagents** via frontmatter, but subagents don't inherit parent's active skills.
- **Parallelism**: subagents yes, skills no.
- **Tool/permission restriction**: subagents support it natively, skills only via `allowed-tools:` metadata.
- **Best-for heuristic**: skill when knowledge is reusable and fits as guidance; subagent when task is self-contained, noisy, or needs isolation.

## Points of Disagreement

Essentially none. Voice A provides more operational detail (token costs, worktree isolation, concrete examples). Voice B frames it more abstractly ("progressive disclosure vs delegation") and is slightly more concise. No substantive conflict.

One minor framing difference: Voice A says "no separate model call" for skills — Voice B says "does not do work by itself." Same truth, different emphasis. A skill changes *how* the current agent works; a subagent *does work separately*.

## Synthesized Answer

**Skill** — a reusable prompt package that injects domain knowledge, checklists, or workflow discipline into the current agent's context window. ~1.5k tokens on invoke. No isolation, no parallel execution. The agent gains expertise and acts on it within the same conversation. Mental model: *teaching the current worker*.

**Subagent** — a separate agent instance with its own context window, model tier, tools, and permissions. Runs independently (optionally in background/worktree). Returns a summary; verbose intermediate work never enters the parent's context. Mental model: *hiring another worker who reports back*.

**Decision heuristic** (from [[syntheses/agent-primitive-selection]]):

| Reach for... | When... |
|---|---|
| Skill | Knowledge/workflow is reusable, fits as prompt guidance, no need to isolate side effects |
| Subagent | Task is self-contained, output is verbose/noisy, needs tool restriction, benefits from parallel execution, or only the final result matters |

**Key interaction**: skills preload into subagents via `skills:` frontmatter — this is how you give a delegated worker domain expertise at turn 0.

Both voices are correct and complementary. Voice A is more useful operationally; Voice B's "progressive disclosure vs delegation" framing is the cleanest mental model.
