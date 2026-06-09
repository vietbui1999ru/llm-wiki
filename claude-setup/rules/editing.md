# Editing and code policy

- No large edits without being asked. Prefer minimal diffs.
- Ask before any destructive operation (delete, overwrite, rename).
- Shell scripts: zsh on macOS, bash-compatible on Linux.
- Prefer explicit over clever. For configs: show the diff, don't rewrite the whole file.

## Definition of Done

Before claiming complete: run type-checker and test suite, show output. `superpowers:verification-before-completion` not optional. "Type-checks clean" ≠ "works."

## Bug Fixing

Identify root cause before fixing. State it explicitly. Never patch symptoms.
