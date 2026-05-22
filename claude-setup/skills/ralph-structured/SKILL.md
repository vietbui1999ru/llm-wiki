---
name: ralph-structured
description: Structured ralph loop — decomposes a goal into tasks.json, enforces one-task-per-iteration, stuckness protection (3 attempts), and iteration logging. Use when a task has 3+ steps, multiple files, explicit testing requirements, or sequential dependencies ("first X then Y").
allowed-tools: "Bash,Read,Write,Edit"
---

# Ralph Structured Loop

Two phases: decompose a goal into a task file, then launch `/ralph-loop` with a
task-driver protocol. The protocol enforces one-task-per-iteration — the agent picks
the first pending task each fresh context, completes it, marks it done or blocked,
and logs the outcome. The plugin is untouched; all logic lives in the protocol file.

## Phase 1 — Task Decomposition

### Step 0: Check for existing tasks

```bash
cat .claude/tasks.json 2>/dev/null
```

If `tasks.json` exists with tasks where `status` is `"pending"`: show the remaining
tasks and ask:

> "`.claude/tasks.json` has [N] pending tasks. Resume the existing loop, or start
> fresh with a new task list?"

- **Resume** → skip to Phase 2
- **Fresh** → continue with Step 1 (will overwrite tasks.json)

### Step 1: Parse the goal

The user's goal is the argument passed to this skill invocation. If no argument was
provided, ask: "What's the goal for this loop?" If the response is empty or too
vague, ask clarifying questions until you can write a one-sentence goal statement.

### Step 2: Generate task list

Think through the goal. Decompose into tasks using these rules:

- One task = one unit of work completable in a single agent context window
- Each task needs a clear pass/fail signal: a `test_cmd` OR a specific
  `acceptance_criteria` (not both required, but at least one must be unambiguous)
- Order by dependency — blockers first
- Max 15 tasks. If scope requires more, tell the user:
  > "This scope is too large for one loop. Suggest breaking into [N] phases."
  Then list the proposed phases and ask which to tackle first. Do not generate >15 tasks.

Write `.claude/tasks.json`:

```json
[
  {
    "id": "TASK-001",
    "title": "Short imperative title (≤10 words)",
    "acceptance_criteria": "Specific, testable condition — observable without running the code",
    "test_cmd": "npm test -- --testPathPattern=feature",
    "status": "pending",
    "attempts": 0
  }
]
```

`test_cmd` is optional — omit the field (don't write `null`) if no automated test
applies. `acceptance_criteria` is always required.

### Step 3: Show for approval

Display the task list:

```
Task list for: [goal]
──────────────────────────────────────
TASK-001: [title]
  Criteria: [acceptance_criteria]
  Test:     [test_cmd or "manual verification"]

TASK-002: [title]
  ...
──────────────────────────────────────
[N] tasks. Proceed, or edit the list?
```

Wait for user approval. If the user requests edits: update `tasks.json` and re-display
the list. Only continue to Phase 2 when the user explicitly approves.

---

## Phase 2 — Launch

### Step 4: Write the protocol file

Write `.claude/ralph-protocol.md` with this exact content, substituting `{GOAL}` with
the user's original goal:

```markdown
# Ralph Structured Loop Protocol

**Goal:** {GOAL}
**Task file:** .claude/tasks.json
**Log file:** .claude/ralph-log.md

This file is read-only during the loop. If accidentally modified, run `git checkout .claude/ralph-protocol.md` to restore it, then re-read it at the start of the next iteration.

## Each iteration — follow these steps exactly

1. Read `.claude/ralph-log.md` if it exists — understand what prior iterations did
   and what was left incomplete.

2. Read `.claude/tasks.json`. Find the first task where `"status": "pending"`.

3. If no pending tasks exist:
   - Print a summary: "Loop complete. [N done, M blocked]"
   - For each blocked task, print: "BLOCKED: [id] — [title] — [acceptance_criteria]"
   - Then output exactly: <promise>ALL_TASKS_DONE</promise>
   Do not proceed to step 4. The loop will terminate automatically after this output.

4. Increment the task's `"attempts"` counter **before starting work**:
   Read `.claude/tasks.json`, increment `attempts` for this task, then write the entire file back using the Write tool. Do not use Edit — partial JSON edits create inconsistent state.

5. Work **only** on this task. Do not touch any other task.

6. When the work feels complete:
   - If a `test_cmd` is present: run it via Bash
     - Tests pass → set `"status": "done"` in tasks.json
     - Tests fail AND attempts < 3 → leave `"status": "pending"` (retry next iteration)
     - attempts >= 3 → set `"status": "blocked"` regardless of test result
   - If no `test_cmd`: evaluate against `acceptance_criteria`
     - Criteria met → set `"status": "done"`
     - Criteria not met AND attempts < 3 → leave `"status": "pending"`
     - attempts >= 3 → set `"status": "blocked"`

7. Append exactly one line to `.claude/ralph-log.md`:
   `[ITER N] TASK-XXX: one sentence — what happened and the outcome (done/pending/blocked)`
```

### Step 5: Handle --kanban flag (skip if not passed)

If `--kanban` was passed by the user:

```bash
if ! command -v jq >/dev/null 2>&1; then
  echo "jq not found — skipping kanban sync. Install with: brew install jq (macOS) or apt install jq (Linux)"
else
  REPO=$(git rev-parse --show-toplevel 2>/dev/null) || REPO="."
  mkdir -p "${REPO}/.agents/inbox" "${REPO}/.agents/claimed" "${REPO}/.agents/done"

  # Mirror all pending tasks to inbox
  jq -r '.[] | select(.status == "pending") | "\(.id)\t\(.title)"' .claude/tasks.json | \
    while IFS=$'\t' read -r task_id title; do
      echo "# ${task_id}: ${title}" > "${REPO}/.agents/inbox/${task_id}.md"
    done
fi
```

### Step 6: Add .gitignore entries

```bash
REPO=$(git rev-parse --show-toplevel 2>/dev/null) || REPO="."
GITIGNORE="${REPO}/.gitignore"
for entry in ".claude/tasks.json" ".claude/ralph-log.md" ".claude/ralph-protocol.md"; do
  grep -qxF "$entry" "$GITIGNORE" 2>/dev/null || echo "$entry" >> "$GITIGNORE"
done
```

### Step 7: Launch ralph-loop

Run this Bash command to start the loop:

```bash
echo "Starting structured ralph loop..."
```

Then instruct the user:

> "Task file written. Run this to start the loop:"
> ```
> /ralph-loop Read .claude/ralph-protocol.md and follow its instructions. Do not modify that file. --completion-promise "ALL_TASKS_DONE"
> ```

Do not run `/ralph-loop` yourself — the user must type it to activate the stop hook
in their current session.
