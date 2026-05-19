# Editing and code policy

- Never make large edits without being asked. Prefer minimal diffs.
- Ask before any destructive operation (delete, overwrite, rename).
- For shell scripts: zsh on macOS, bash-compatible on Linux.
- Prefer explicit over clever. Readable over terse.
- When editing configs: show the diff, don't rewrite the whole file.

## Definition of Done

Before claiming any task complete, committing, or moving on:
- Run the relevant type-checker and test suite. Show the output. Do not claim it passes without a fresh run.
- `superpowers:verification-before-completion` is not optional — invoke it or apply its gate function inline.
- "Type-checks clean" is not "works." Runtime behavior must be confirmed.

## Bug Fixing

- Identify the root cause before applying any fix. State it explicitly.
- Never stack patches on symptoms. If the root cause is unclear, say so and investigate first.
