---
name: "council"
description: "Run the repo's multi-model council workflow. Use for architecture, security, or durable tradeoff decisions where more than one answer looks valid."
---

# Council

Multi-model deliberation via `claude` and `codex` CLIs. No API keys needed — each CLI uses its own stored auth.

**Voices**: Sonnet 4.6 (A) + GPT-5.4 (B)
**Chairman**: Opus 4.6

Outputs written to `.council/` and auto-committed to git.

## When to use

- architecture choice with multiple valid approaches
- security design decision
- major workflow or memory design
- tradeoff with lasting consequences

## Voices only

```bash
council "QUESTION"
```

Writes `.council/voice_a.md` (Sonnet) and `.council/voice_b.md` (GPT-5.4). Auto-commits.

## Full pass with Chairman

```bash
council --chairman "QUESTION"
```

Voices run first, then Opus reads both files and writes `.council/synthesis.md`. Auto-commits.

## Add Codex as third voice

```bash
council --chairman --add openai/gpt-5.3-codex "QUESTION"
```

## After output

Read `.council/synthesis.md` (or voice files if no chairman). Summarize:

1. agreements
2. disagreements
3. chosen direction and why

If `.agents/decisions.md` exists in target project, append decision there.
