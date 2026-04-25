---
title: "Tool Design for Agents"
type: concept
tags: [agent-engineering, tool-design, harness, llm-interface]
sources: []
created: 2026-04-25
updated: 2026-04-25
---

# Tool Design for Agents

Tools designed for agents differ fundamentally from APIs designed for developers. A developer reads documentation and understands underlying systems. An agent **infers intent from descriptions and generates calls from natural language**. Every ambiguity is a failure mode.

## The Dual Audience Problem

Tool errors serve two audiences with opposite needs:
- **Developers**: detailed technical info, stack traces, internal state
- **Agents**: actionable guidance — what went wrong and exactly how to correct it

**Design for agent recovery first.** A developer can read logs. An agent can only recover if the error message tells it what to do next.

## Description Engineering

Every tool description must answer four questions:

1. **What does the tool do?** — exact action, not vague ("helps with", "can be used for")
2. **When should it be used?** — specific triggers and contexts, including indirect signals
3. **What inputs does it accept?** — types, constraints, defaults, what each parameter controls
4. **What does it return?** — output format, examples of success and error states

**Principle: concrete over generic.** Instead of "Use an ID like '123'" → "Use format: 'CUST-######' (e.g., 'CUST-000001')". Instead of "Provide a date" → "Format: 'YYYY-MM-DD' (e.g., '2024-01-15')".

## Error Message Structure

Error messages for agents should contain:
1. What specifically went wrong (not just an error code)
2. What the correct format or value should be
3. A concrete example of valid input
4. Whether a retry is appropriate

```json
{
  "error": {
    "code": "INVALID_CUSTOMER_ID",
    "message": "Customer ID 'CUST-123' does not match required format",
    "expected_format": "CUST-######  (e.g., 'CUST-000001')",
    "resolution": "Provide a 9-character customer ID matching CUST-######",
    "retryable": true
  }
}
```

The agent reads this and knows exactly what to change. Compare with `{"error": "400 Bad Request"}` — that gives the agent nothing to act on.

## Naming Conventions

**Parameters**: self-documenting full words, no abbreviations except standard ones (id, url). Consistent across all tools for similar concepts.

- Good: `customer_id`, `search_query`, `output_format`, `max_results`
- Bad: `x`, `val`, `param1`, `info`

**Enumerations**: consistent across the whole tool surface.
- Affirmative options: `include_` prefix (`include_history`, `include_metadata`)
- Negative options: `exclude_` prefix (`exclude_archived`, `exclude_inactive`)
- Don't mix: `"format": "short"` in one tool and `"format": "brief"` in another for the same concept

## Response Format

Provide format options that let agents request appropriate verbosity:

```python
def get_customer(customer_id: str, format: str = "concise") -> dict:
    """
    format: "concise" → id, name, status only
            "detailed" → all fields including history
    """
```

This prevents agents from being overwhelmed by large responses when they only need one field, while allowing full data when needed.

## Tool Discovery

Agents discover tools by scanning descriptions. A tool that matches many ambiguous situations gets called incorrectly. Design each tool to have a clear, non-overlapping trigger condition.

When two tools could plausibly be used for the same thing, one of them is named wrong, described wrong, or shouldn't exist.

## Application to This Codebase

When writing tools for Claude agents (MCP tools, harness tools, bash wrappers):
- Write the description as if the agent has never seen the codebase
- Put the correction instruction directly in the error message
- Choose parameter names that appear in the natural language query that would trigger the tool
- Test by asking: "If the agent calls this with wrong input, does the error tell it exactly what to change?"

## Related Pages

- [[concepts/agent-harness]] — harness architecture where tools live; bash as general-purpose tool
- [[summaries/agent-harness-engineering]] — OpenAI case study: tool legibility as agent performance lever
