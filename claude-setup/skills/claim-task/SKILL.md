---
name: claim-task
description: Claim the next available task from the shared inbox at session start. Invoke at the beginning of any agent session running inside a git worktree, before doing any other work.
allowed-tools: "Bash,Read"
---

# Claim Task from Shared Inbox

Invoke this at the start of any session running inside a worktree. It atomically claims one task from the shared inbox in the main checkout, which is accessible from any worktree.

## Step 1: Locate the inbox

```bash
MAIN_REPO=$(dirname "$(git rev-parse --git-common-dir)")
INBOX="${MAIN_REPO}/.agents/inbox"
CLAIMED="${MAIN_REPO}/.agents/claimed"
```

`git rev-parse --git-common-dir` always resolves to the main `.git` regardless of which worktree you are in. `dirname` gives the main checkout root.

## Step 2: Claim atomically

```bash
for task_file in "${INBOX}"/*.md; do
  [ -f "$task_file" ] || { echo "No tasks available in inbox."; exit 0; }
  task_name=$(basename "$task_file")
  if mv "${task_file}" "${CLAIMED}/${task_name}" 2>/dev/null; then
    echo "Claimed: ${CLAIMED}/${task_name}"
    break
  fi
  # mv failed = another agent claimed it first; try next
done
```

`mv` is atomic on POSIX (same filesystem). If two agents race to the same file, exactly one wins — no lock files needed.

## Step 3: Read your task

Read the claimed file. It contains your full work specification: scope, acceptance criteria, files to touch, files NOT to touch.

```bash
cat "${CLAIMED}/${task_name}"
```

Do not start any work until you have read and understood the task file.

## Step 4: Work and complete

When your task is done:

1. Commit all changes with a descriptive message
2. Move your claimed file to done:

```bash
mv "${CLAIMED}/${task_name}" "${MAIN_REPO}/.agents/done/${task_name}"
```

3. If the orchestrator expects a status signal:

```bash
echo "DONE" > "${CLAIMED}/${task_name%.md}.status"
```

## If inbox is empty

Output: "Inbox is empty — no tasks to claim. Check with the coordinator before proceeding."

Do not invent work. Wait for tasks to be added or ask the user what to do.
