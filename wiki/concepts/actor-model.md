---
title: "Actor Model"
type: concept
tags: [concurrency, distributed-systems, architecture, actor, erlang, orleans, akka]
sources:
  - "https://berb.github.io/diploma-thesis/original/054_actors.html"
  - "https://learn.microsoft.com/en-us/dotnet/orleans/overview"
created: 2026-05-10
updated: 2026-05-10
---

# Actor Model

A model of concurrent computation where the **actor** is the universal primitive. Each actor is a lightweight, isolated unit that encapsulates state and behavior, communicating exclusively through asynchronous message passing. Originating in work by Carl Hewitt in the early 1970s, it is now a foundational pattern for building distributed and highly-concurrent systems.

Related: [[patterns/concurrency]], [[systems/distributed-systems]], [[systems/architectural-patterns]]

---

## Core Model: Three Primitives

Upon receiving a message, an actor may do any combination of three things (source: Berb thesis):

1. **Send** — dispatch a finite number of messages to other actors (by address)
2. **Spawn** — create a finite number of new child actors
3. **Become** — change its own behavior, taking effect when the *next* message arrives

The `become` primitive is how actors manage mutable state without shared memory: the new behavior captures the updated state, and the transition is atomic with respect to the current message being processed.

---

## Mailbox Semantics

- Every actor has exactly one mailbox, addressable by a unique name.
- Messages are sent asynchronously; delivery time is unbounded.
- **The base model guarantees no global ordering** — message interleaving from multiple senders is non-deterministic.
- **Common implementation guarantee**: messages sent from actor A to actor B arrive in FIFO order relative to each other. This is a per-pair guarantee, not a global one.
- Mailbox enqueue/dequeue are atomic operations, preventing race conditions at the queue boundary.

---

## No Shared State

The model bans shared state entirely. Actors may not pass references, pointers, or mutable objects in messages. Only **immutable data** and **actor addresses** (names) are legal message payloads.

Passing a mutable reference re-introduces shared memory and breaks all isolation guarantees. Implementations (Akka, Erlang) enforce this via the type system or by deep-copying on send.

---

## Location Transparency

Actors are addressed by name, not by memory location. Because no actor holds a direct memory pointer to another, an actor's physical location — same process, same machine, or a remote node — is invisible to the caller.

This property makes distribution straightforward: routing a message to a remote actor requires only a network transport layer, not a programming model change. It is the primary reason actor systems are a natural fit for [[systems/distributed-systems]].

---

## Actor vs. Threads

| Dimension | Threads | Actors |
|---|---|---|
| State sharing | Shared memory; requires locks | No sharing; message only |
| Synchronization | Mutex, semaphore, RWLock | None required |
| Overhead | ~1–8 MB stack each | Very lightweight; millions possible |
| Deadlocks | Classic cyclic lock-wait | Still possible via cyclic message-wait |
| Race conditions | Common | Eliminated for local state; possible with bad protocol design |

Actors eliminate lock-based synchronization, but do not eliminate deadlocks entirely. A cycle of actors each waiting for a reply from the next creates the same logical deadlock as a lock cycle. The practical mitigation is timeouts on replies, not a structural guarantee.

Most actor runtimes use lock-free implementations internally; atomic behavior is only required for mailbox operations.

---

## Actor vs. CSP (Go Channels)

CSP (Communicating Sequential Processes, as in Go's goroutines + channels) is the closest alternative model.

| Dimension | Actor Model | CSP |
|---|---|---|
| Identity | Actors have persistent identity (address) | Channels are anonymous |
| Coupling | Sender knows receiver's address | Sender and receiver coupled only by channel reference |
| Default | Asynchronous send | Synchronous rendezvous (buffered channels approximate async) |
| State | Encapsulated in actor | External to channel; programmer manages |
| Failure | Supervision trees (Erlang OTP) | Goroutine panics propagate; no built-in supervision |

Key tradeoff: actor identity enables fine-grained supervision and fault recovery; CSP channels are simpler to compose but harder to fault-isolate because there is no natural supervisor boundary.

---

## Supervision and "Let It Crash"

Erlang's contribution: treat failure as a **first-class protocol** rather than an error to prevent.

**Let it crash** — when an actor encounters an unexpected state, crash immediately rather than attempting partial recovery. The supervisor, not the crashing actor, is responsible for deciding what happens next.

### Supervision Trees

Actors are organized into a hierarchy. A **supervisor** monitors its children; when a child crashes, the supervisor receives a notification and applies a restart strategy:

| Strategy | Behavior |
|---|---|
| `one_for_one` | Restart only the crashed child |
| `one_for_all` | Restart all children when any one crashes |
| `rest_for_one` | Restart the crashed child and all children started after it |

Supervisors can themselves be supervised, forming a tree. Top-level supervisors escalate to the application if they exhaust restart budgets.

The isolation of actors (no shared state) is what makes this viable: one actor crashing cannot corrupt another actor's state, so selective restart is safe.

### OTP (Open Telecom Platform)

OTP is Erlang's standard library of supervision and behavior abstractions (`GenServer`, `GenStateMachine`, `Supervisor`). It formalizes the patterns above and handles the boilerplate of message loops, state threading, and restart policies.

---

## Virtual Actor Model (Orleans)

Microsoft Orleans (source: Microsoft Learn docs) introduced the **Virtual Actor** abstraction as an innovation over classical actors:

> Actors are purely logical entities that *always* exist, virtually. An actor cannot be explicitly created nor destroyed, and its virtual existence is unaffected by the failure of a server that executes it.

### Key properties

- **Perpetual logical existence** — the programmer never calls "create actor" or "destroy actor". An actor is simply addressed; the runtime activates it on demand and deactivates it under memory pressure.
- **Transparent activation/deactivation** — the runtime decides which silo (server) hosts an activation. If a silo fails, the grain re-activates on another silo automatically; callers are unaffected.
- **Always addressable** — because actors always exist logically, no "actor not found" error class exists.

### Grain and Silo concepts

**Grain** — the virtual actor unit in Orleans. Composed of:
- User-defined stable identity (GUID, integer, or string key)
- Behavior (grain class implementing an interface)
- Optional persistent or volatile state

**Silo** — a host process that runs one or more grains. Silos form a cluster; the cluster coordinates grain placement, failure detection, and load balancing.

```
Cluster
  └─ Silo A          (server/process)
       ├─ Grain X    (activated)
       └─ Grain Y    (activated)
  └─ Silo B
       └─ Grain Z    (activated)
```

### Placement and rebalancing

Orleans supports configurable grain placement strategies: random, prefer-local, and resource-optimized (CPU/memory utilization, default since Orleans 9.2). As of Orleans 9.x, activation rebalancing automatically redistributes grains across silos for improved load distribution.

### Differences from classical actors

| | Classical Actors (Erlang/Akka) | Virtual Actors (Orleans) |
|---|---|---|
| Lifecycle | Explicit spawn/kill | Always exists; runtime manages activation |
| Failure recovery | Supervisor restarts | Re-activation on another silo; transparent |
| Location | Programmer-aware (PID/address) | Runtime-managed; caller unaware of silo |
| State persistence | Manual | Built-in grain persistence API |
| Transactions | Manual coordination | Distributed ACID transactions built-in |

---

## Implementations

| Implementation | Language/Platform | Distinguishing trait |
|---|---|---|
| **Erlang/OTP** | Erlang | Origin implementation; supervision trees, let-it-crash as language philosophy; BEAM VM with preemptive scheduling and per-actor GC |
| **Elixir** | Elixir (BEAM) | Erlang semantics with modern syntax; `GenServer` and OTP supervision; `Phoenix` framework uses actors for WebSocket channels |
| **Akka** | Scala/Java (JVM) | Industry standard for JVM actor systems; typed actors, clustering, Akka Streams for backpressure |
| **Akka.NET** | C#/.NET | Port of Akka to .NET; classical actor model, no virtual actor abstraction |
| **Microsoft Orleans** | C#/.NET | Virtual Actor Model (grains + silos); transparent activation, built-in persistence and transactions; used in Azure, Xbox, Halo, Skype (per Microsoft docs) |
| **ProtoActor** | Go, C#, Kotlin | Cross-language; combines classical actors with virtual actor concepts; gRPC-based remote messaging |

---

## When to Use vs. Avoid

**Use when:**
- State has natural identity (user session, game entity, device, shopping cart) — each identity maps to one actor/grain
- High concurrency with per-entity isolation required — actors serialize access to their own state without global locks
- Distribution is a requirement — location transparency eliminates network-aware application code
- Failure isolation matters — supervision trees contain failures without global shutdown
- Long-lived stateful sessions — actor survives connection drops, unlike stateless request handlers

**Avoid when:**
- Tight synchronous pipelines — actor async-only communication adds latency and complexity where a direct call is simpler
- Compute-bound workloads without coordination — pure CPU parallelism (map-reduce, matrix ops) is better served by thread pools or data-parallel frameworks
- Simple CRUD with low concurrency — the actor model's overhead and mental model are not justified
- Strong ordering guarantees across multiple actors are required — the model provides per-pair FIFO at best; global ordering requires coordination (transactors) which re-introduces complexity

---

## Common Pitfalls

- **Reference passing** — passing mutable object references in messages silently breaks isolation; enforce immutability at message boundaries.
- **Blocking inside an actor** — a blocking call inside an actor stalls its mailbox processing; use async patterns or delegate to a separate worker actor.
- **God actor** — one actor doing too much; supervision is only effective when actors have single responsibilities.
- **Cyclic reply chains** — A waits for B waits for A; use timeouts or restructure to a request-response with explicit timeout handling.
