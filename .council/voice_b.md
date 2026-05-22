# openai/gpt-5.4

Core split:

- `Skill` = reusable instructions inside same agent context.
- `Subagent` = separate agent instance with own context.

Practical difference, per [[concepts/agent-skills]] and [[concepts/agent-subagents]]:

- Context:
  `Skill` injects prompt/workflow into current conversation.
  `Subagent` gets fresh context window. Parent sees summary only.

- What it is:
  `Skill` acts like capability pack or playbook.
  `Subagent` acts like delegated worker.

- Isolation:
  `Skill` no isolation. Shares same history, same context pressure.
  `Subagent` isolates noisy work: tests, logs, docs, large scans.

- Execution:
  `Skill` does not do work by itself. It changes how main agent works.
  `Subagent` actually runs task independently, then reports back.

- Tools / permissions / model:
  `Skill` can shape tool usage and model choice for current agent.
  `Subagent` has its own explicit tool/model/permission config.

- Parallelism:
  `Skill` no.
  `Subagent` yes, especially background workers.

- Best use:
  `Skill` for reusable domain knowledge, checklists, workflows.
  `Subagent` for self-contained tasks where result matters more than full trace.

Rule of thumb from [[syntheses/agent-primitive-selection]]:

- Reusable knowledge that fits in prompt -> `Skill`
- Task that pollutes context or should run separately -> `Subagent`

Short version:
`Skill` makes one agent smarter.
`Subagent` gives one agent a helper. <task-complete>
