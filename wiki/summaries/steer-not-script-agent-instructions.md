---
title: "Stop Scripting Your Coding Agent. Start Steering It."
type: summary
tags: [agent-instructions, claude-md, prompting, principles, protocol]
sources: ["Stop Scripting Your Coding Agent. Start Steering It..md"]
created: 2026-10-22
updated: 2026-10-22
---

# Stop Scripting Your Coding Agent (Pattern Interruption, Substack, early 2026)

Opinion essay, no data. Linked in [[summaries/reddit-self-improving-claude-code-setup]] as still relevant.

## Thesis: script the protocol, principle-ize the judgment

Sort every instruction into one of two buckets:

| | Protocol | Judgment |
|---|---|---|
| Should be | Specific, exact, non-negotiable | Principle-based, adaptive |
| Because | Consistency matters more than creativity | Context matters more than consistency |
| Example | "Output must include a verification section with pass/fail per criterion" | "Verification must produce evidence, not assertions" |
| Failure when wrong | Agent reinvents your workflow each run | Agent follows a stale script against the codebase |

**Protocol** = output format, phase order, integration contracts (endpoints, payloads, deploy commands), safety gates ("always ask before deleting"). **Judgment** = which pattern, how to handle this error, refactor vs patch, test strategy, naming.

Most configurations get it backwards: they script judgment ("use library X") and leave protocol vague ("format nicely").

## Three layers for the judgment bucket

1. **Architectural principles:** stable beliefs ("side effects explicit and contained", "test behaviour, not implementation").
2. **Quality criteria as states, not actions:** "all code conforms to the lint config", not "run the linter". Binary, agent-checkable.
3. **Anti-patterns:** what must not happen ("never catch and ignore", "no circular deps"). Described as the most underused category.

## Migration steps

1. Extract the principle each specific instruction encodes.
2. Rewrite steps as end states.
3. Mine the last ~20 PR review comments for anti-patterns.
4. Sort remaining specifics into protocol (keep, make *more* specific) vs judgment (replace with principle).
5. Remove tool/library/path names from the judgment bucket; if the agent cannot discover them, fix codebase discoverability.

## Wiki connections

- [[concepts/agent-context-instructions]]: adds the protocol/judgment split.
- [[concepts/rules-vs-hooks]]: safety gates are protocol and are best enforced by hooks, not prose.
- [[summaries/less-is-more-claude-md]]: companion piece by the same publication.
