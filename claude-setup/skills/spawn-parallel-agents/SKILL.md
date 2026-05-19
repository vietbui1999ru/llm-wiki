---
name: spawn-parallel-agents
description: Orchestrate parallel agents — in-process for short tasks (<30 min, ≤5), worktree pool for long/many tasks. Use when tasks are independent with no shared state. Invoke after to-issues or when user asks to run tasks in parallel.
allowed-tools: "Bash,Read,Agent"
---

# Spawn Parallel Agents

## Mode selection

```
Independent tasks?
  ├─ ≤5 tasks AND each <30 min AND no isolated filesystem needed
  │    → IN-PROCESS DISPATCH (Section 1 below)
  └─ >5 tasks OR any task >30 min OR need clean context per agent
       → WORKTREE POOL (Section 2 below)
```

---

## Section 1: In-Process Dispatch (short tasks)

Use for: independent debugging, test failures across different files, short parallel investigations.

**Don't use when:** tasks share files, have mid-task dependencies, or need >30 min each.

### Step 1: Identify independent domains

Group failures/tasks by what's broken. Each domain must be understandable without context from others.

### Step 2: Craft focused agent prompts

Each agent gets:
- **Specific scope** — one file, one subsystem
- **Clear goal** — exactly what to fix or produce
- **Constraints** — what NOT to touch
- **Expected output** — summary of findings and changes

```markdown
Fix the 3 failing tests in src/agents/agent-tool-abort.test.ts:

1. "should abort tool with partial output capture" — expects 'interrupted at' in message
2. ...

Do NOT change production code outside this file.
Return: summary of root cause and what you changed.
```

### Step 3: Dispatch in a single message

Send all Agent tool calls in one message so they run concurrently:

```
Agent 1 → fix agent-tool-abort.test.ts
Agent 2 → fix batch-completion-behavior.test.ts
Agent 3 → fix tool-approval-race-conditions.test.ts
```

### Step 4: Integrate

- Read each agent summary
- Check for conflicting edits to the same file
- Run full test suite
- Spot-check — agents can make systematic errors

**Common mistakes:**
- Too broad scope ("fix all tests") → agent gets lost
- No constraints → agent refactors everything
- Vague output request → you don't know what changed

---

## Section 2: Worktree Pool (long tasks)

## When to invoke

- User has a set of independent tasks and asks to parallelize
- `agent-orchestration` decision tree routes to WORKTREE POOL
- Tasks are too long for in-process agent teams (>30 min each)
- More than 5 parallel tasks needed

**Do not use for:** tasks that share files or have mid-task dependencies (sequence those instead).

---

## Step 1: Locate or build the inbox

Check if `.agents/inbox/` exists with tasks:

```bash
MAIN_REPO=$(git rev-parse --show-toplevel)
ls "${MAIN_REPO}/.agents/inbox/"*.md 2>/dev/null || echo "empty"
```

If empty, ask the user: "Should I populate the inbox from open issue files? Or describe the tasks you want parallelized."

If the user has issue files (from `/to-issues`), move them to the inbox:

```bash
mkdir -p "${MAIN_REPO}/.agents/inbox" "${MAIN_REPO}/.agents/claimed" "${MAIN_REPO}/.agents/done"
# Add .agents/ and .agent-task-id to .gitignore if not already there
grep -qxF '.agents/' "${MAIN_REPO}/.gitignore" 2>/dev/null \
  || echo '.agents/' >> "${MAIN_REPO}/.gitignore"
grep -qxF '.agent-task-id' "${MAIN_REPO}/.gitignore" 2>/dev/null \
  || echo '.agent-task-id' >> "${MAIN_REPO}/.gitignore"
```

If the user describes tasks verbally, create task files yourself before proceeding:

```markdown
<!-- .agents/inbox/TASK-001.md -->
---
id: TASK-001
scope: src/payments/
blocking: []
blocked-by: []
---

[task description, acceptance criteria, files to touch, files NOT to touch]
```

---

## Step 2: Verify scope safety

Read all inbox task files. For each pair, check that `scope:` fields do not overlap.

```bash
grep -h "^scope:" "${MAIN_REPO}/.agents/inbox/"*.md
```

If two tasks share a scope prefix (e.g., `src/` and `src/auth/`) — they overlap. Tell the user and suggest sequencing those two. Only parallelize non-overlapping tasks.

---

## Step 3: Determine worker count

Rule: min(task count, 5). Beyond 5, coordination overhead and token cost outweigh benefit. If >5 tasks exist, run the first 5; remaining stay in inbox for a second wave.

---

## Step 4: Spawn agents

For each claimable task (up to the worker count), spawn one background Agent with `isolation: "worktree"`. Each agent receives its task specification directly in the prompt — it does not need to discover the inbox.

Spawn all agents in a single message (parallel tool calls):

> Spawn [N] Agent tool calls simultaneously. For each:
> - `isolation: "worktree"` — gives the agent its own filesystem checkout
> - `run_in_background: true` — lets all run concurrently
> - Prompt includes the full task spec + these instructions:
>   1. Your task is defined above. Work only in the files listed under `scope:`.
>   2. Run existing tests before starting: confirm baseline is green.
>   3. Implement, run tests, fix until passing.
>   4. Commit your work with a clear message.
>   5. Do not touch files outside your scope — another agent owns them.
>   6. Signal completion by writing `DONE` to `.agents/claimed/<task-id>.status`

Mark the task file as claimed before spawning (atomic move):

```bash
mv "${MAIN_REPO}/.agents/inbox/TASK-001.md" \
   "${MAIN_REPO}/.agents/claimed/TASK-001.md"
```

After the atomic move, write the task ID sentinel to the worktree root so hooks can
identify which task this agent owns (env vars don't cross hook process boundaries):

```bash
# This runs inside the worktree after it's created — include in agent prompt instructions:
echo "TASK-001" > .agent-task-id
```

Include this line in every agent's prompt (substituting the real task ID):
```
First action: run `echo "TASK-001" > .agent-task-id` to register your task identity.
```

After claiming, write an agent registry entry to `.agents/registry.json`:

```bash
REGISTRY="${MAIN_REPO}/.agents/registry.json"
SESSION_ID="<agent-session-id-or-generated-uuid>"
ENTRY="{\"id\":\"${SESSION_ID}\",\"task\":\"TASK-001\",\"status\":\"running\",\"started_at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"machine\":\"$(hostname -s)\",\"model\":\"haiku\"}"

# Append to agents array (jq required) or initialize:
if [[ -f "$REGISTRY" ]]; then
  jq --argjson e "$ENTRY" '.agents += [$e]' "$REGISTRY" > /tmp/registry_tmp && mv /tmp/registry_tmp "$REGISTRY"
else
  echo "{\"agents\":[$ENTRY]}" > "$REGISTRY"
fi
```

Also append a `task_claimed` event to `.agents/events.jsonl`:

```bash
echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"event\":\"task_claimed\",\"task\":\"TASK-001\",\"agent\":\"${SESSION_ID}\"}" \
  >> "${MAIN_REPO}/.agents/events.jsonl"
```

---

## Step 5: Monitor and collect results

After all background agents complete, you will be notified. Then:

1. Read each agent's result summary
2. Run the full test suite from the main checkout to catch integration issues
3. For each completed worktree branch: merge to main (or open PR if `scope` touches shared interfaces)
4. Move completed task files to `.agents/done/`
5. Run `git worktree prune` to clean up
6. Update `.agents/registry.json` — set each completed agent's `status` to `"done"` or `"failed"`
7. Append `task_complete` or `task_failed` event to `.agents/events.jsonl`

If any agent failed: the worktree branch and task file remain. Inspect, fix manually, or re-queue the task to inbox for a second wave.

---

## Scope safety reminder

Worktrees isolate filesystems — agents literally cannot see each other's in-progress edits. But worktrees do NOT prevent:
- Port conflicts if agents start dev servers (assign ports via `DEV_PORT` env in each worktree)
- Logical duplication (two agents writing near-identical helpers in different modules)

Catch logical duplication in Step 5 during review before merging both branches.
