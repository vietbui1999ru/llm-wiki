# Start small

A coding-agent setup should start lean and grow only when something fails. This guide is that
starting point. Each step is small, and each links to the wiki pages that explain why. Nothing here
asks you to copy anyone's dotfiles: the [How I Work](/guides/workflows) pages show one owner's
setup as an example, not a template.

The rule behind every step: **add a piece of setup in response to a failure you have seen, not one
you expect.** Setup you add up front is context the agent reads on every turn, and most of it never
earns its place ([context engineering](/concepts/context-engineering)).

## 1. Know what you are configuring

A coding agent is a model, a loop and a set of tools. The harness is everything around the model:
instructions, tools, permissions, checks. You will mostly be tuning the harness.

Read: [minimal coding agent](/syntheses/minimal-coding-agent),
[agent harness](/concepts/agent-harness), [AI coding agents](/entities/ai-coding-agents).

## 2. Write one short context file

One `AGENTS.md` (or `CLAUDE.md`) at the repo root. Put in only what the agent cannot work out from
the code: how to build and test, conventions that are not obvious, and the project's vocabulary.
Keep it short; long context files make agents worse, not better. Treat it as a map, not a manual.

Read: [agent context instructions](/concepts/agent-context-instructions),
[AGENTS.md format](/entities/agents-md-format), [domain glossary](/concepts/domain-glossary).

## 3. A few rules, and when a rule becomes a hook

Start with a handful of rules. When the agent breaks the same rule twice, the rule belongs in
something that runs, not in prose: a hook, a permission setting, a linter. Security rules
especially: a "do not" sentence in a context file is not enforced by anything.

Read: [rules vs hooks](/concepts/rules-vs-hooks),
[self-improving agent setup](/concepts/self-improving-agent-setup) (its minimal recipe),
[design principles](/patterns/principles) (YAGNI applies to setup too).

## 4. Plan before code, keep diffs small

Ask for a plan first on anything bigger than a one-file change, and keep each change small enough to
review. Agent mistakes hide in large diffs.

Read: [spec-driven frameworks vs native](/comparisons/spec-driven-frameworks-vs-native),
[AI-specific pitfalls](/concepts/ai-specific-pitfalls), [deep modules](/concepts/deep-modules).

## 5. One verification step and one review step

Run the tests and the type-checker before calling anything done, and read the diff yourself. Passing
tests are weak evidence on their own: agents can write tests that pass for the wrong reason.

Read: [verification pipeline](/concepts/verification-pipeline),
[agent test verification](/concepts/agent-test-verification),
[AI code review](/concepts/ai-code-review), [unit testing](/concepts/unit-testing).

## 6. A safety baseline

Run the agent with the narrowest permissions that still let it work, inside a sandbox when it runs
commands unattended. Treat anything it reads from the web or from files as possible instructions
from someone else.

Read: [sandbox controls](/concepts/agentic-sandbox-controls),
[indirect prompt injection](/concepts/indirect-prompt-injection),
[OWASP AI agent risks](/concepts/owasp-ai-agent-risks).

## 7. Keep long sessions healthy

Long sessions degrade. Clear or compact at natural break points, and write the state you need into
files so a fresh session can pick it up.

Read: [context window](/concepts/context-window),
[context degradation](/concepts/context-degradation),
[context compression](/concepts/context-compression), [prompt caching](/concepts/prompt-caching).

## 8. Add skills, subagents and hooks only when a failure repeats

Skills, subagents, plugins and model routing are each an answer to a specific problem. Reach for one
when you have that problem twice. A single loop with good tools beats a team of agents more often
than it seems.

Read: [agent skills](/concepts/agent-skills), [subagents](/concepts/agent-subagents),
[choosing an agent primitive](/syntheses/agent-primitive-selection),
[subagent cost model](/concepts/subagent-cost-model),
[model tier routing](/concepts/model-tier-routing).

## 9. Learn from mistakes, and prune

Keep a short lessons file. When a lesson keeps coming back, promote it into enforcement (step 3).
Cap the file and prune it: rules that no longer fire are noise.

Read: [self-improving agent setup](/concepts/self-improving-agent-setup),
[compound engineering](/concepts/compound-engineering),
[agent self-correction](/concepts/agent-self-correction).

## 10. Scale out later

Parallel agents, worktrees, multi-model review and long autonomous loops pay off once the basics
above hold. Add them one at a time.

Read: [worktree isolation](/concepts/worktree-isolation),
[branch strategy for agents](/concepts/branch-strategy-for-agents),
[agent teams](/concepts/agent-teams), [council pattern](/concepts/council-pattern),
[Ralph loop](/concepts/ralph-loop), [agentic CI/CD](/concepts/agentic-cicd).

## See one setup grown this way

The [How I Work](/guides/workflows) section shows where one owner's setup ended up after many rounds
of this: [architecture](/guides/architecture), [workflows](/guides/workflows) and
[send-it](/guides/send-it). Borrow what solves a failure you have; skip the rest.
