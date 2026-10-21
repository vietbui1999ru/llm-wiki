# Send-it spec loop (derived)

Derived from the global spec loop in `shared/AGENTS.md`. Applies only while the send-it band icon is on, in a repo where `/send-it on` was run. Never applies in dotfiles, llm-wiki or agent-events.

1. Read `SPEC.md` before code when its `branch:` matches. Work only toward its AC ids. Obey its Boundaries.
2. Never run `ac-run approve` or `ac-run check`. Send-it has no approval record and does not execute `verify:` lines. The human's use-test is the gate.
3. Do not ask questions. Decide spec details and any scope narrowing yourself. Record each one under `Assumptions` in `SPEC.md`.
4. Never edit a `verify:` or `baseline:` line, or a test, to make a check pass. Report the failure.
5. Before saying "done", run `floor-guard` and report its output. Check the diff against each `verify:` line by reading it, not by running it.
6. If a check fails, fix and rerun. Stop after 3 tries and report the failing output.
7. Build with the Haiku `worker`. Opus reviews the diff against each `verify:` line.
8. Stage by path, commit, push the branch and open a PR. After `floor-guard` passes, archive SPEC.md as the branch's last commit, per global spec-loop rule 7 (`git mv SPEC.md docs/specs/<YYYY-MM-DD>-<slug>.md`), push it, then enable auto-merge. End with `NEXT: use-test <x> [you]`.

Never: forced pushes, `push --delete`, `reset --hard` to remote refs, `git clean -fd`, `rm -rf` on home or root, reading `~/secrets`, editing send-it settings, running `/send-it`, or asking another agent or terminal to do any of these.

Trade-off: no `verify:` line runs in send-it, so a passing command is never proof. Correctness rests on Opus's diff review and the human's use-test.
