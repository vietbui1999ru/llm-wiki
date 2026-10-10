---
title: "dev.to: Vibe Coding Interview Guide — Frameworks and Checklists"
type: summary
tags: [ai-coding-agents, interviews, evaluation, prompt-engineering, ai-code-review]
sources: ["raw/dev.to - Vibe Coding Interview Guide.md"]
created: 2026-09-16
updated: 2026-09-16
---

# dev.to: Vibe Coding Interview Guide — Frameworks and Checklists

Source: [truongpx396, dev.to — Vibe Coding Interview Guide](https://dev.to/truongpx396/vibe-coding-interview-guide-ace-ai-assisted-coding-assessments-1gbh)

Independent blog post (May 2026), more tactical than narrative — built around reusable checklists rather than anecdote. `(single-author blog, unverified against real interview outcomes — treat frameworks as prep scaffolding, not confirmed grading rubric)`.

## The CRATE prompt framework

Adapted from Dave Birss's CREATE framework, renamed for the interview context:

| Letter | Element | Example |
|---|---|---|
| C | Context | "In a Go REST API using chi router and sqlx..." |
| R | Role/Task | "Generate a repository method that..." |
| A | Constraints | "Use parameterized queries, return errors don't panic, follow the existing pattern in user_repo.go" |
| T | Target output | "Return the struct and method only, no main function" |
| E | Examples | "Similar to how GetUserByID works in the codebase" |

Not all five are needed every time, but context + constraints + task almost always are. Key claim: **prompt transcripts are saved and reviewed** — a tight CRATE prompt reads better on playback than a vague one that took three re-prompts to converge. The grader reportedly sees both the code and the prompt history.

## Prompt anti-patterns

| Anti-pattern | Why it hurts |
|---|---|
| One-shot mega-prompt | Output too large to review; signals no decomposition skill |
| Vague prompt ("make it better") | Signals you don't know what "better" means |
| Re-prompting the same broken prompt | Signals no debugging skill |
| Accepting first output without reading | Fatal — you'll be asked to explain it |
| Prompting for tests first | Don't — build the thing first in a live interview |

This directly matches the "one-shotting the whole spec" red flag from the Reddit thread ([[summaries/ai-agent-interview-evaluation]]) — independent corroboration of the same failure mode.

## The 30-second review checklist

Meant to run after every generated block, not just at the end:

- **Security**: raw string interpolation in SQL/shell? Auth check before touching user-owned resources? Hardcoded secrets? Input validation on external inputs?
- **Correctness**: null/empty/zero case handled? Errors from external calls handled? Types as expected? Signature matches call sites?
- **Performance**: loop inside a DB call (N+1)? Missing index on filter column? Loading a full object for one field?
- **Idioms**: matches existing repo style? Imports organized? Errors wrapped with context?
- **Agent-specific** (Claude Code / Cursor agent mode / Devin, etc.): did it actually run tests, or just claim they passed? Did it edit files outside the intended scope ("helpfully" refactoring an unrelated module)? Half-completed migrations/fixtures/feature-flags left behind? Hallucinated a function/package/import that doesn't exist? Destructive edits (deleted files, dropped tables, force-push) without authorization? If it used MCP tools, right server and right scope?

The agent-specific block is the most actionable addition beyond generic code review — it targets failure modes specific to *agentic* tools rather than AI output in general, complementary to [[concepts/ai-specific-pitfalls]].

## Interview format taxonomy (7 variants named)

Live AI-paired coding (60-90 min), take-home project (2-8 hrs), hybrid DS&A + AI round, system design with AI assistance, code review of AI output, repository-scale codebase extension, and an "agentic/autonomous-runner round" reserved for senior+ or AI-company-specific interviews. `(claimed taxonomy, single source — treat as one practitioner's categorization, not an industry standard)`.

## Named failure modes

Five archetypes given as anti-personas: **Passive Passenger** (never redirects), **Traditionalist** (refuses to use the tool at all, defeating the point of the round), **Prompt Looper** (re-prompts the same failing request without diagnosing), **Security Blind Spot** (ships the checklist's security gaps), **Silent Coder** (the communication failure from Hello Interview's axis 4, named independently here).

## Connections

- [[summaries/ai-agent-interview-evaluation]] — the CRATE prompt discipline and one-shot-mega-prompt anti-pattern both restate red flags this Reddit thread surfaced independently
- [[summaries/hellointerview-ai-coding-interviews]] — Silent Coder / Passive Passenger map onto Hello Interview's "communication" and "control over the AI" axes; three independent sources now agree on the same handful of failure shapes
- [[concepts/ai-specific-pitfalls]] — the agent-specific review checklist items (claimed-but-unrun tests, hallucinated imports, scope creep) are this concept applied to a live-review cadence
- [[concepts/ai-code-review]] — the 30-second checklist is a compressed, interview-scale version of this discipline
