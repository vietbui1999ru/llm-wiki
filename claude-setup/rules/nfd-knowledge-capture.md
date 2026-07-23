# NFD Knowledge Capture

**Status: proposed, not adopted.** Not @-imported by any CLAUDE.md — has no effect until reviewed against the existing patterns/rules split ([[concepts/knowledge-crystallization-cycle]]) and explicitly wired in. Captured here so the proposal isn't lost, not as an active rule.

Applies across all sessions and all agent harnesses (Claude Code, OpenCode, Pi, Codex).

## Fragment Tagging Protocol

During any session, tag notable fragments inline when they arise naturally:

- `[INSIGHT]` — a generalizable principle or heuristic observed in context
- `[DECISION]` — a meaningful choice made with non-obvious rationale
- `[PATTERN]` — a recurring structure noticed across sessions or tasks
- `[ERROR]` — a mistake and corrective principle; also triggers `capture-mistake` skill in Claude Code

Use tags sparingly — only when the fragment would be worth recalling in a future session.

## Crystallization Suggestion Trigger

When 3+ `[INSIGHT]` or `[PATTERN]` tags accumulate in one session:
> "Crystallization candidate: [X]. Suggest wiki ingest or synthesize-mistakes to formalize?"

Do not suggest for `[ERROR]` — the `capture-mistake` hook handles those automatically.

## Why this matters

Errors are already captured via `mistakes/raw-log.md`. Insights and patterns are not — they evaporate at session end. This protocol closes the gap between our current error-only crystallization and full NFD-style Knowledge Crystallization Cycle.

See [[concepts/knowledge-crystallization-cycle]] and [[concepts/nurture-first-development]].
