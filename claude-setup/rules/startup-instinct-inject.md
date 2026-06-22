# Startup: Instinct Injection

After session and drift checks, inject high-confidence learned instincts if present:

```bash
PROJECT_ID=$(git rev-parse --short HEAD 2>/dev/null || echo "global")
cat ~/.claude/homunculus/projects/$PROJECT_ID/instincts.json 2>/dev/null
```

| Result | Action |
|---|---|
| File missing or empty | Silent skip. |
| Entries with `confidence >= 0.7` | Inject as behavioral priming (see below). |
| All entries `confidence < 0.7` | Silent skip — not confident enough to inject. |

When injecting, surface as:
> **Active instincts** (learned from prior sessions, high confidence):
> - [pattern 1]
> - [pattern 2]
>
> Apply unless current task explicitly overrides them.

To build instincts for this project: run `/instinct-triage` after a few sessions of work.
Observations accumulate at `~/.claude/homunculus/projects/<id>/observations.jsonl`.

**Override:** "ignore instincts" or "fresh start" → skip injection for this session.
**Status:** instinct clustering is documented-not-adopted — see [[concepts/instinct-clustering]].
