# Editing and code policy

- No large edits without being asked. Prefer minimal diffs.
- Ask before any destructive operation (delete, overwrite, rename).
- Shell scripts: zsh on macOS, bash-compatible on Linux.
- Prefer explicit over clever. For configs: show the diff, don't rewrite the whole file.

## Definition of Done

Before claiming complete: run type-checker and test suite, show output. `superpowers:verification-before-completion` not optional. "Type-checks clean" ≠ "works."

## Bug Fixing

Identify root cause before fixing. State it explicitly. Never patch symptoms.

## LOC Gate — Brain-Fatigue Cap

AI agents MUST cap code generation at **~50 lines of code (LOC) per turn**.

- **Write tool**: if the new file exceeds 50 logical source lines, split into multiple turns.
- **Edit tool**: if the added/modified lines exceed 50, break into smaller sequential edits.
- **Refactors**: plan the work across turns. Each turn delivers one coherent ~50-LOC chunk.
- **Exceptions**: mechanical changes (rename symbol, update imports, batch find-replace) and generated data (JSON fixtures, test vectors).
- **Why**: >50 LOC per turn increases defect density, review fatigue, and merge complexity. Small turns catch logic errors earlier and keep each diff reviewable.

Count logical source lines — exclude blank lines and single-line comments. If a turn needs more than 50 LOC of new code, ask the user before proceeding.
