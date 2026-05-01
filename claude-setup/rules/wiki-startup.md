# Wiki and Agent Orchestration — Always Active

## Automatic invocation rules

These apply by default at every session. No user prompt needed.

### wiki-context (proactive)
Before any technical task, design discussion, architecture question, or agent work:
invoke `wiki-context` skill to load relevant patterns from ~/repos/llm-wiki.

Not conditional. Not "if relevant." The wiki index is already loaded — the skill
does the search. Invoke it, then proceed.

Skip only for: trivial one-line answers, pure shell commands, git operations.

### agent-orchestration (default for multi-step work)
For any task involving: multi-agent systems, subagent design, team coordination,
complex feature development, or agent harness work:
invoke `agent-orchestration` skill before designing the approach.

### skill check discipline (from superpowers)
When superpowers is enabled, the `using-superpowers` skill loads this at startup.
When it's not enabled, treat this rule as the equivalent:
- Before ANY substantive response, check: does a skill apply?
- If even 1% chance a skill applies → invoke it
- Process skills (debugging, design) before implementation skills

## Priority

User's explicit instructions > these rules > defaults.
If user says "just answer quickly" or "skip the skill" → skip it.
