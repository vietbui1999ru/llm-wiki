---
title: "Worker Coordination: Partial Result Passing Between Parallel Agents"
type: concept
tags: [agent-engineering, multi-agent, coordination, parallelism, blackboard, pipeline, actor-model]
sources: []
created: 2026-05-12
updated: 2026-05-12
---

# Worker Coordination: Partial Result Passing Between Parallel Agents

The standard parallel agent pattern (subagents or teams) assumes workers have **non-overlapping scope** and only need to report completion back to the coordinator. When workers need each other's *partial* outputs mid-task, this assumption breaks.

**First question before reaching for a coordination pattern: is the decomposition wrong?**

"Worker A needs a partial result from Worker B" is often a sign that the work was not truly parallel. Restructure first:
- Can the shared dependency be computed *before* workers are spawned? → **contract-first**
- Does B's output simply feed into A? → **pipeline** (sequential, not parallel)
- Is the dependency bidirectional and emergent? → **blackboard**

---

## Pattern 1: Contract-First (Pre-coordination)

Define all interfaces, schemas, and API contracts before spawning workers. Workers operate on the contract file, not on each other's live output.

```
Coordinator writes: workspace/contracts/api-schema.json
Worker A reads it, builds frontend against the contract
Worker B reads it, builds backend to implement the contract
```

**When to use:** the interface can be fully specified upfront (REST endpoints, data models, type definitions, event schemas).

**When it fails:** exploratory work where the interface can only emerge from doing the work.

---

## Pattern 2: Pipeline (Sequential Fan-Out)

If A needs B's output but B doesn't need A's — it's not parallel, it's sequential. Make it explicit.

```
Coordinator → spawn Worker B → B completes → spawn Worker A with B's output
```

Disguising a pipeline as parallel work adds coordination complexity with no benefit. The decision tree should ask "do results depend on each other?" before declaring work parallel.

---

## Pattern 3: Filesystem Blackboard

Shared directory that workers read and write intermediates to. Workers poll for dependencies before proceeding.

```
workspace/
  blackboard/
    worker-a/partial.json     ← A writes here as it progresses
    worker-b/partial.json     ← B writes here
    shared/contracts.json     ← coordinator seeded upfront
```

**Protocol:**
1. Coordinator seeds the blackboard with initial state before spawning workers
2. Each worker writes its partial outputs to its own path at defined checkpoints
3. Workers that need a sibling's output poll with a bounded retry (e.g. 3× with 5s delay)
4. If dependency doesn't arrive within budget → escalate to coordinator, don't hang

**Why filesystem:** fits Claude Code's filesystem-first harness model. No message-passing infrastructure. Natural audit trail. Compatible with worktree isolation (each worker sees the blackboard via the shared repo).

**Risk:** polling creates busy-wait. Bound the retry count. If A polls for B's output and B has failed silently, A should timeout and signal the coordinator rather than polling indefinitely.

---

## Pattern 4: Actor Mailbox

Workers send typed messages to each other's mailboxes. The receiver processes messages when it's ready, giving natural back-pressure.

```
Worker A → send("worker-b/inbox/request-001.json", {type: "need-schema", from: "worker-a"})
Worker B → reads inbox, processes, replies to worker-a/inbox/response-001.json
```

**When to use:** workers have ongoing, multi-round interaction (not just a one-time partial result handoff). More appropriate for long-running actor systems than typical AFK coding loops.

Per [[concepts/actor-model]]: this is the mailbox semantics model — Orleans grains and Akka actors implement it natively. In a Claude Code harness, the filesystem is the mailbox.

---

## Decision Table

| Situation | Pattern |
|---|---|
| Interface knowable upfront | Contract-first |
| A needs B's final output, B doesn't need A | Pipeline (sequential) |
| Mutual dependency, interface emerges from work | Filesystem blackboard |
| Ongoing multi-round interaction between workers | Actor mailbox |
| Any of the above but work is genuinely independent | Re-decompose — you have the wrong task split |

---

## Common Failure Modes

**Silent dependency failure:** Worker B crashes or stalls; Worker A polls forever. Fix: always bound retries, always escalate to coordinator.

**Partial write races:** Worker A reads Worker B's partial output mid-write. Fix: workers write to a temp path then atomically rename; readers only consume complete files (use `.json.tmp` → `.json` rename pattern).

**Scope bleed:** Workers modify each other's files instead of reading the blackboard path. Fix: strict file ownership — each worker only writes to its own path.

---

## Related Pages

- [[concepts/agent-teams]] — team architecture; the standard pattern this extends
- [[concepts/agent-subagents]] — subagent isolation; when partial results indicate wrong decomposition
- [[concepts/actor-model]] — mailbox semantics, message-passing primitives (Orleans/Akka/Erlang)
- [[concepts/ralph-loop]] — filesystem state between context windows; same durability principle
- [[concepts/worktree-isolation]] — how workers get filesystem isolation while sharing the blackboard
- [[syntheses/agent-primitive-selection]] — decision tree for which primitive to reach for
