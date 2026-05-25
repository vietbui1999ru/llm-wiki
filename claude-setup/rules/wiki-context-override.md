# Wiki Context — Always Invoke (project override)

**Project-level override:** In this repo, wiki-context is always-invoke — overrides the
domain-triggered pattern in `~/.claude/rules/skill-invocation.md`.

Before any technical task, design discussion, architecture question, or agent work:
invoke `wiki-context` skill to load relevant patterns from ~/repos/llm-wiki.

Not conditional. Not "if relevant." The wiki index is already loaded — the skill
does the search. Invoke it, then proceed.

Skip only for: trivial one-line answers, pure shell commands, git operations.
