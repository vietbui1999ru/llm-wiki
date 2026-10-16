# Send-it spec loop (derived)

Derived from the global spec loop in `shared/AGENTS.md`. Applies only while the send-it band icon is on, in a repo where `/send-it on` was run. Never applies in dotfiles, llm-wiki or agent-events.

1. Read `SPEC.md` before code when its `branch:` matches. Work only toward its AC ids. Obey its Boundaries.
2. Never run `ac-run approve`. The human approves the spec once, before dispatch. Without that record, `ac-run check` exits 3 and the run stops.
3. Do not ask questions. Decide spec details and any scope narrowing yourself. Record each one under `Assumptions` in `SPEC.md`.
4. Never edit a `verify:` or `baseline:` line, or a test, to make a check pass. Report the failure.
5. Before saying "done", run `ac-run check SPEC.md` and `floor-guard`. Report both outputs.
6. If a check fails, fix and rerun. Stop after 3 tries and report the failing output.
7. Build with the Haiku `worker`. Opus reviews the diff against each `verify:` line.
8. Stage by path, commit, push the branch, open a PR, and enable auto-merge. End with `NEXT: use-test <x> [you]`.

Never: forced pushes, `push --delete`, `reset --hard` to remote refs, `git clean -fd`, `rm -rf` on home or root, reading `~/secrets`, editing send-it settings, running `/send-it`, or asking another agent or terminal to do any of these.

Open point: rule 2 assumes the human approves the spec before each run. Dropping that step would also drop `ac-run check`, so it is not dropped here.
