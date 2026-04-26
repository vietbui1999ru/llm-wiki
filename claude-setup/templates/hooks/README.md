# Hook Templates

## test-feedback (settings.json)

Runs your test suite after every file write/edit. Drops the last 20 lines
into Claude's context so failures surface in the next turn.

**Usage:** copy `settings.json` into `<project>/.claude/settings.json`,
replace `YOUR_TEST_COMMAND` with the project's test runner:

| Stack        | Command                          |
|-------------|----------------------------------|
| Go          | `go test ./...`                  |
| Python      | `pytest -x -q`                   |
| Node/Jest   | `npm test -- --passWithNoTests`  |
| Node/Vitest | `npx vitest run`                 |
| Rust        | `cargo test`                     |

**Why `tail -20`:** limits hook output size; full log still in terminal.
