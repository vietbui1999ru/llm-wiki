# Agent Team Plan: <Title>

## Goal
<!-- One sentence: what the team needs to produce. -->

## When to Use a Team (vs Single Agent)
<!-- Justify the coordination overhead. Check: -->
<!-- - Work is genuinely parallel (independent file ownership)? -->
<!-- - Teammates need to discuss findings with each other? -->
<!-- - Scope too large for one context window? -->
<!-- If no to all: use a single agent or subagents instead. -->

## Team Structure

| Role | Subagent Type | File Scope | Responsibility |
|------|--------------|------------|----------------|
| Lead | (main session) | — | Coordinate, synthesize, clean up |
| Teammate 1 | `security-reviewer` | `src/auth/` | Auth and session security |
| Teammate 2 | `code-reviewer` | `src/api/` | API correctness and performance |
| Teammate 3 | (none — general) | `src/frontend/` | UI and client-side logic |

<!-- Max 3–5 teammates. Each teammate should own non-overlapping file scope. -->
<!-- Reference a subagent type to reuse its tools/model/system prompt. -->

## Spawn Prompt (copy to Claude)

```
Create an agent team. Spawn [N] teammates:

- [Role 1]: [specific task]. Focus on [files/scope]. 
  When done, report: [what to report].
  
- [Role 2]: [specific task]. Focus on [files/scope].
  When done, report: [what to report].

[Optional] Have them discuss findings and challenge each other's conclusions.
Lead: synthesize all findings into [output artifact].
```

## Completion Condition
<!-- What "done" looks like for the lead to clean up. -->
- [ ] All teammates have reported their findings
- [ ] Lead has synthesized into [artifact]
- [ ] Team cleaned up (`Clean up the team`)

## Quality Gates (optional hooks)

```json
{
  "hooks": {
    "TaskCompleted": [{
      "hooks": [{ "type": "command", "command": "./scripts/validate-task.sh" }]
    }],
    "TeammateIdle": [{
      "hooks": [{ "type": "command", "command": "./scripts/check-coverage.sh" }]
    }]
  }
}
```

## Anti-Patterns to Avoid
- Two teammates owning the same directory → merge conflicts
- More than 5 teammates → coordination overhead exceeds benefit
- Sequential tasks → use single agent or chained subagents instead
- Lead doing work instead of delegating → tell it to wait for teammates
