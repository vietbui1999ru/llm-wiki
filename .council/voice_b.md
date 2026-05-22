# openai/gpt-5.4

Short version:

A `skill` stays inside same agent. A `subagent` is another agent.

| Thing | Skill | Subagent |
|---|---|---|
| Form | Reusable prompt/workflow package | Named worker with own prompt/config |
| Context | Same context window as caller | Separate context window |
| Purpose | Load domain knowledge, checklists, repeatable instructions | Delegate bounded task, isolate noise, enforce role/tools |
| Execution | Does not do work by itself; caller uses enriched context to act | Runs independently, then returns summary |
| Isolation | None | Tools, model, permissions, memory, even worktree isolation possible |
| Parallelism | No | Yes, especially background subagents |

Practical rule, per [[syntheses/agent-primitive-selection]]:

- Use `skill` when knowledge or workflow is reusable across sessions and fits as prompt guidance.
- Use `subagent` when task is self-contained, noisy, or benefits from separate tools/permissions/context.
- Use `subagent` if only final result matters and main thread should stay clean.
- Skills can be preloaded into subagents, but subagents do not inherit parent skills automatically. Per [[concepts/agent-skills]] and [[concepts/agent-subagents]].

In harness terms, both are context-management primitives:
- `skill` = progressive disclosure inside one agent.
- `subagent` = delegation with context isolation.

Good mental model:
- `skill` = teach current worker.
- `subagent` = hire another worker. <task-complete>
