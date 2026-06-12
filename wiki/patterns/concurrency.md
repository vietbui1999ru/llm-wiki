---
title: "Concurrency and Parallelism Patterns"
type: pattern
tags: [patterns, concurrency, systems, software-engineering]
sources:
  - "Mastering Concurrency A Guide for Software Engineers.md"
  - "Mastering Concurrency A Senior Engineer's Survival Guide.md"
created: 2026-05-06
updated: 2026-05-06
---

# Concurrency and Parallelism Patterns

Reference and agent guide for thread safety, synchronization primitives, async patterns, parallel algorithms, and concurrency failure modes.

## Agent Trigger

**Apply when:** Writing or reviewing multithreaded/async code, shared state, locks, or parallel algorithms.
**Rule of thumb:** Prefer immutability/message-passing over shared locks; guard every shared mutable access; watch for deadlock ordering and async pitfalls.

---

## Core Concepts

**Concurrency** — multiple tasks making progress in overlapping time intervals (may share a single CPU via scheduling).

**Parallelism** — tasks executing simultaneously on multiple CPU cores. True parallelism requires multiple hardware execution units.

**Multithreading** — one technique for concurrency: divide a process into threads that share memory and run independently.

The key insight: concurrency is a program structure property; parallelism is a runtime execution property. A concurrent program may or may not run in parallel depending on hardware.

---

## Thread Safety Fundamentals

A piece of code is **thread-safe** if it behaves correctly when called concurrently from multiple threads, without external synchronization by the caller.

**What makes code unsafe:**
- Multiple threads read and write shared mutable state without coordination
- Operations that appear atomic (e.g., `counter++`) are not — they compile to read/modify/write, which is three separate steps that can interleave

**Primary defense:** minimize shared mutable state. State that isn't shared can't race.

**Immutable data is always thread-safe.** Design data structures to be immutable where possible; share read-only references freely.

---

## Synchronization Primitives

### Mutex (Mutual Exclusion Lock)

Allows only one thread at a time into a critical section.

**When to use:** Protecting a shared data structure from concurrent reads and writes; when the critical section is short and won't block long.

**When NOT to use:** High-contention hot paths (mutex becomes a bottleneck); when reads vastly outnumber writes (use read-write lock instead).

**Anti-patterns:**
- Holding a mutex across I/O or long operations (thread starvation)
- Locking at too coarse a granularity (serializes too much work)
- Locking at too fine a granularity (complex, deadlock-prone)

### Semaphore

A counter that controls how many threads can access a resource simultaneously. Mutex is a special case (semaphore with max count = 1).

**When to use:** Rate-limiting access to a bounded resource pool (e.g., max 10 concurrent DB connections); producer-consumer coordination.

**When NOT to use:** Simple mutual exclusion — a mutex is clearer.

### Read-Write Lock (RWLock)

Multiple readers OR one writer at a time.

**When to use:** Read-heavy workloads (caches, config objects, in-memory indexes) where reads dominate and writes are rare.

**When NOT to use:** Write-heavy or evenly mixed workloads (writer starvation risk; overhead exceeds benefit).

### Atomic Operations

Hardware-guaranteed indivisible read-modify-write. No lock required.

**When to use:** Simple counters, flags, reference counts, lock-free data structure building blocks.

**When NOT to use:** Complex multi-field updates that must be consistent together — atomics can't protect multiple variables as a unit.

```cpp
// C++ example — fetch_add is atomic; no mutex needed
std::atomic<int> counter{0};
counter.fetch_add(1, std::memory_order_relaxed);
```

**`volatile` is not an atomic.** `volatile` prevents compiler optimization on memory-mapped I/O; it does not synchronize threads. A common beginner mistake.

### Condition Variables

Used with a mutex to block threads until a condition is true.

**When to use:** Producer-consumer; blocking until a queue is non-empty or a resource becomes available.

**Pattern:** Always check the condition in a loop (not `if`) to guard against spurious wakeups.

---

## Memory Models

Modern CPUs reorder instructions for performance. Compilers do the same. Without explicit synchronization, there is no guarantee that a write in one thread is visible in another.

**Memory ordering (C++/Rust/Java terminology):**

| Ordering | Guarantee | Cost |
|---|---|---|
| Relaxed | No synchronization; only atomicity | Lowest |
| Acquire / Release | Acquire sees all writes before a Release on the same atomic | Medium |
| Sequential Consistency | Global total order of all operations | Highest |

**False sharing:** Two unrelated variables on the same CPU cache line cause cache invalidation traffic between cores even though there's no logical sharing. Fix: pad structs to align variables to separate cache lines (`alignas(64)` in C++).

---

## Race Conditions

A race condition occurs when program behavior depends on the ordering or timing of thread execution.

**Detection:**
- Thread sanitizers (TSan, Helgrind, Java ThreadSanitizer) instrument code to detect data races at runtime
- Code review: any `if (condition) { use(condition) }` pattern on shared data without a lock is suspect
- Stress testing with many threads and intentional delays

**Prevention:**
1. No shared mutable state — prefer message passing or immutability
2. If shared state is necessary, always access it under the same lock
3. Use atomic operations for single-variable shared counters/flags
4. Design with ownership: one thread owns a piece of data at a time

---

## Deadlock

Deadlock: thread A holds lock X, waits for lock Y; thread B holds lock Y, waits for lock X. Neither can proceed.

**Four necessary conditions (Coffman):** mutual exclusion, hold-and-wait, no preemption, circular wait. Break any one to prevent deadlock.

**Prevention strategies:**

1. **Lock ordering** — always acquire locks in the same global order. If every thread takes lock A before lock B, circular wait cannot form.
2. **Lock timeout** — try-lock with a timeout; back off and retry if acquisition fails.
3. **Single lock** — redesign so only one lock is needed for the operation.
4. **Lock-free / wait-free algorithms** — eliminate locks entirely using atomics (complex; use a battle-tested library).

**Anti-patterns:**
- Acquiring locks in different orders in different call paths
- Calling external code (callbacks, user code) while holding a lock — that code may try to re-acquire the same lock

---

## Async / Await Patterns and Pitfalls

Async/await models concurrency on a single thread (or small thread pool) using cooperative scheduling. No shared memory races — but different failure modes.

**When to use:** I/O-bound workloads (HTTP, DB queries, file reads); high-concurrency servers where threads would be wasteful.

**When NOT to use:** CPU-bound work — blocking the event loop starves all other coroutines. Offload to a thread pool.

**Common pitfalls:**

| Pitfall | Description | Fix |
|---|---|---|
| Blocking the event loop | Calling sync I/O or CPU-heavy code in an async context | Use `asyncio.to_thread` / `tokio::spawn_blocking` |
| Forgetting to await | Fire-and-forget silently; errors are swallowed | Always await or explicitly spawn with error handling |
| Async in a sync context | Calling async functions from non-async code incorrectly | Use runtime `.block_on()` or restructure to be async top-down |
| Unbounded concurrency | `asyncio.gather` on 10k tasks overwhelms downstream | Add a semaphore to limit concurrent tasks |

---

## Actor Model

Each actor is an isolated unit of state and behavior. Actors communicate only by sending messages; they never share memory directly.

**When to use:** Systems where independent agents manage their own state (game entities, distributed nodes, user sessions). Eliminates shared-memory races by design.

**When NOT to use:** Low-latency scenarios where message-passing overhead matters; simple in-process data pipelines.

**Implementations:** Erlang/Elixir (built-in), Akka (JVM), Actix (Rust), Swift concurrency (actor keyword).

---

## CSP (Communicating Sequential Processes)

Concurrent goroutines/processes communicate via typed channels. Goroutines block on send/receive until the other side is ready (or the channel is buffered).

**When to use:** Go pipelines; producer-consumer; fan-out / fan-in patterns; cleaner than explicit locks for many coordination tasks.

**When NOT to use:** Sharing large data structures (copying is expensive); when you need random access to shared state.

**Anti-patterns:**
- Unbuffered channels causing deadlock (sender blocks forever waiting for receiver)
- Leaking goroutines (goroutine blocks on channel receive, no one ever sends)

---

## Parallel Algorithm Patterns

### Map-Reduce

Split input into independent chunks (map), process each in parallel, aggregate results (reduce).

**When to use:** Data parallelism over large independent collections (log processing, image batch transforms, ML feature computation).

**Anti-pattern:** Map-reduce where the reduce step has global shared state that requires heavy locking — kills parallelism.

### Fork-Join

Fork N parallel tasks; join (wait) until all complete; combine results.

**When to use:** Recursive divide-and-conquer algorithms (parallel merge sort, parallel tree traversal); bounded parallel subtasks.

**Anti-pattern:** Forking too-fine-grained tasks — thread creation / scheduling overhead dominates for tiny work units.

### Thread Pool

Maintain a fixed set of worker threads. Dispatch tasks to the pool rather than spawning a new thread per task.

**When to use:** Almost always — raw thread-per-task creation is expensive. Most language runtimes provide one (Java `ExecutorService`, Python `ThreadPoolExecutor`, Go goroutine scheduler).

**When NOT to use:** CPU-bound work that needs dedicated OS threads with custom affinity (use system threads directly).

### Producer-Consumer

Producer threads enqueue work; consumer threads dequeue and process. Decouples production rate from consumption rate via a bounded buffer.

**When to use:** Pipeline stages with different throughput; rate smoothing; background processing queues.

**Backpressure:** When the consumer is slower than the producer, the buffer fills. Handle by: blocking the producer (simple, can starve), dropping items (loss-tolerant), or signaling upstream to slow down (preferred for reliability).

---

## Backpressure

Backpressure is explicit signaling from a slow consumer to a fast producer to slow down or stop. Without it, the producer overwhelms memory or drops data silently.

**Mechanisms:**
- Blocking bounded queues (producer blocks on `put` when queue full)
- Reactive Streams / async streams with `demand` signals
- TCP flow control (the network stack does this automatically)

**Anti-pattern:** Unbounded queues that accept all input — work accumulates in memory until OOM.

---

## Deadlock vs. Livelock vs. Starvation

| Problem | Description |
|---|---|
| Deadlock | Threads are all blocked; no progress ever |
| Livelock | Threads are active but keep stepping back and forth; no forward progress |
| Starvation | One thread never gets scheduled despite being ready (e.g., writer starvation in RWLock under constant readers) |

---

## Cross-references

- [[systems/distributed-systems]] — distributed concurrency: consistency models, CAP, distributed locks
- [[systems/scalability-reliability]] — connection pools, async servers, backpressure at system level
- [[patterns/principles]] — minimize shared mutable state is a core principle, not just a concurrency tip
