---
name: instinct-triage
description: Triage accumulated learned instincts from ~/.claude/homunculus/. Review instincts.json for confidence scores, prune stale or low-confidence entries, and promote high-confidence recurring patterns to skill files. Run monthly or when instinct count exceeds 20. NOTE: instinct clustering pipeline is documented-not-adopted — this skill is the starter path. See [[concepts/instinct-clustering]].
allowed-tools: "Bash,Read,Edit"
model: sonnet
---

# instinct-triage — Learned Instinct Review

## When to invoke

- Monthly review prompt from the user
- Instinct count exceeds 20 (check: `wc -l ~/.claude/homunculus/instincts.json 2>/dev/null`)
- Agent behavior feels inconsistent with recent corrections
- User says "triage instincts" or "prune instincts"

## Step 0: Distill observations into instincts (if needed)

Check whether raw observations exist but no instincts.json yet:

```bash
PROJECT_ID=$(git rev-parse --short HEAD 2>/dev/null || echo "global")
STORE="$HOME/.claude/homunculus/projects/$PROJECT_ID"
echo "Observations: $(wc -l < $STORE/observations.jsonl 2>/dev/null || echo 0) entries"
echo "Instincts: $(cat $STORE/instincts.json 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print(len(d.get("instincts",[])))' 2>/dev/null || echo 0) entries"
```

If observations exist but instincts.json has < 3 entries (or doesn't exist), offer to distill:

> "Found N session-end observations. Run distillation to extract behavioral patterns? (yes/no)"

If yes: read observations.jsonl, then analyze the session history to extract recurring patterns:
- What tool sequences do you use most often in this project?
- What checks do you consistently run before claiming completion?
- What ordering conventions do you follow (e.g., read-before-edit, test-before-commit)?
- What qmd queries do you run when stuck?

Write discovered patterns to `$STORE/instincts.json`:
```json
{
  "project_id": "<id>",
  "updated": "<timestamp>",
  "instincts": [
    {
      "id": "<short-hash>",
      "pattern": "<behavioral pattern as a one-sentence instruction>",
      "confidence": 0.0,
      "source": "distilled",
      "created": "<timestamp>",
      "last_seen": "<timestamp>",
      "frequency": 1
    }
  ]
}
```

Assign initial confidence 0.5 for new distilled instincts. Only patterns you observe with high certainty from the observations log get confidence 0.7+.

If no observations exist: print "No observations recorded yet. Sessions are marked at shutdown via the Stop hook. Run a few work sessions then try again." Skip to Step 1.

## Step 1: Check if instinct store exists

```bash
ls ~/.claude/homunculus/ 2>/dev/null || echo "No instinct store found — instinct clustering not yet set up."
```

If no instinct store: print "Instinct clustering not yet active. See [[concepts/instinct-clustering]] to set up ECC v2. Stopping." and exit.

## Step 2: Read instincts

```bash
cat ~/.claude/homunculus/instincts.json 2>/dev/null
```

Parse each instinct entry. For each, note:
- `id` — unique identifier
- `pattern` — the behavioral pattern captured
- `confidence` — score 0.0–1.0
- `last_seen` — timestamp
- `frequency` — how many times triggered
- `source` — what tool/context generated it

## Step 3: Triage categories

Classify each instinct as one of:

| Category | Criteria | Action |
|---|---|---|
| **Promote** | confidence > 0.85, frequency > 5, last_seen < 14 days | Convert to a skill file entry |
| **Keep** | confidence 0.6–0.85, frequency 2–5, recent | No change |
| **Stale** | last_seen > 30 days | Flag for pruning |
| **Low-confidence** | confidence < 0.5 | Flag for pruning |
| **Conflicting** | contradicts a rule in applied-ai.md or CLAUDE.md | Remove immediately |

## Step 4: Prune stale and low-confidence entries

For entries flagged for pruning, remove them from `instincts.json` using the Edit tool.
Anchor each removal on the entry's unique `id` field.

Log pruned IDs:
```
Pruned: [id1, id2, id3] — stale/low-confidence
```

## Step 5: Promote high-confidence instincts

For each "Promote" entry, create or append to `~/.claude/homunculus/promoted-patterns.md`:

```markdown
## [pattern summary] — promoted YYYY-MM-DD
- Pattern: [behavioral pattern text]
- Confidence: [score] | Frequency: [n] | First seen: [date]
- Candidate skill: [suggested skill name or "none — add to applied-ai.md"]
```

Do not auto-create skills. Flag for human review and approval.

## Step 6: Report

```
instinct-triage complete:
  Total reviewed: N
  Pruned: M (X stale, Y low-confidence, Z conflicting)
  Promoted candidates: K (see ~/.claude/homunculus/promoted-patterns.md)
  Kept: J
```

Append to `~/repos/llm-wiki/log.md`:
```
## [YYYY-MM-DD] instinct-triage | N reviewed, M pruned, K promotion candidates
```
