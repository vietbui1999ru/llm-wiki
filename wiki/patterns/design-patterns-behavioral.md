---
title: "Behavioral Design Patterns"
type: pattern
tags: [patterns, software-engineering, gof, design-patterns]
sources:
  - "Chain of Responsibility.md"
  - "Command.md"
  - "Iterator.md"
  - "Mediator.md"
  - "Memento.md"
  - "Observer.md"
  - "State.md"
  - "Strategy.md"
  - "Template Method.md"
  - "Visitor.md"
  - "Domain Event.md"
  - "Design Patterns in TypeScript.md"
created: 2026-05-06
updated: 2026-05-06
---

# Behavioral Design Patterns

Behavioral patterns define how objects communicate and distribute responsibility. They govern algorithms, control flow, and the assignment of duties between objects — without coupling concrete implementations together.

Related: [[patterns/design-patterns-creational]], [[patterns/design-patterns-structural]], [[patterns/principles]]

## Agent Trigger

**Apply when:** Choosing how objects communicate or coordinate — Observer, Strategy, State, Command, Mediator, Chain of Responsibility, etc.
**Rule of thumb:** Name the collaboration problem first; don't reach for a pattern unless the variation it absorbs is real.

---

## Chain of Responsibility

**Intent:** Pass a request along a chain of handlers; each handler decides to process it or forward it.

**When to use:**
- Multiple handlers may process a request and the set isn't known upfront (middleware pipelines, auth checks)
- Handlers must be composable and orderable at runtime
- You want to avoid coupling the sender to a specific receiver

**When NOT to use:**
- Every request must be guaranteed to be handled (CoR may silently drop unhandled requests)
- Chain is static and rarely changes — a simple `if/else` or strategy is cleaner

**Structure:**

```typescript
interface Handler {
  setNext(handler: Handler): Handler;
  handle(request: string): string | null;
}

abstract class BaseHandler implements Handler {
  private nextHandler: Handler | null = null;

  setNext(handler: Handler): Handler {
    this.nextHandler = handler;
    return handler;
  }

  handle(request: string): string | null {
    return this.nextHandler ? this.nextHandler.handle(request) : null;
  }
}

class AuthHandler extends BaseHandler {
  handle(request: string): string | null {
    if (request === 'authenticated') return super.handle(request);
    return 'AuthHandler: rejected';
  }
}
```

**Anti-patterns:**
- Building a chain so long that debugging which handler acted becomes hard — prefer logging at each node
- Using CoR when all requests need a response; prefer Strategy or explicit dispatch instead

---

## Command

**Intent:** Encapsulate a request as a standalone object, enabling queuing, undo/redo, and deferred execution.

**When to use:**
- You need undo/redo (text editors, drawing tools)
- Operations must be queued, logged, or scheduled (job queues, audit trails)
- Multiple UI elements (button, shortcut, menu) trigger the same action

**When NOT to use:**
- Simple one-shot operations with no need for history or deferral — adds unnecessary indirection
- The operation has no meaningful inverse (undo is impossible anyway)

**Structure:**

```typescript
interface Command {
  execute(): void;
  undo(): void;
}

class CutCommand implements Command {
  private backup = '';
  constructor(private editor: Editor) {}

  execute(): void {
    this.backup = this.editor.getSelection();
    this.editor.deleteSelection();
  }

  undo(): void {
    this.editor.insert(this.backup);
  }
}

class CommandHistory {
  private stack: Command[] = [];
  push(cmd: Command) { cmd.execute(); this.stack.push(cmd); }
  undo() { this.stack.pop()?.undo(); }
}
```

**Anti-patterns:**
- Putting business logic inside the Command itself — Command should delegate to a Receiver
- Conflating Command with Strategy: Command is about *what happened* (history, undo); Strategy is about *how to do something now*

---

## Iterator

**Intent:** Provide a uniform interface to traverse a collection without exposing its internal structure.

**When to use:**
- Collection has a complex internal structure (tree, graph) clients shouldn't care about
- Multiple simultaneous traversals of the same collection are needed
- You want to swap traversal algorithms without changing client code

**When NOT to use:**
- Simple arrays/lists where the language's built-in `for...of` suffices — unnecessary abstraction
- Performance-critical traversal of specialized structures where direct access is faster

**Structure:**

```typescript
interface Iterator<T> {
  hasNext(): boolean;
  next(): T;
}

class TreeIterator implements Iterator<Node> {
  private stack: Node[];
  constructor(root: Node) { this.stack = [root]; }

  hasNext(): boolean { return this.stack.length > 0; }

  next(): Node {
    const node = this.stack.pop()!;
    if (node.right) this.stack.push(node.right);
    if (node.left)  this.stack.push(node.left);
    return node;
  }
}
```

**Anti-patterns:**
- Modifying the collection during iteration (undefined behavior in most implementations)
- Making the iterator stateful in the collection class itself — kills parallel traversal

---

## Mediator

**Intent:** Centralize communication between objects through a single mediator, eliminating direct dependencies between components.

**When to use:**
- Many components interact in complex ways (chat rooms, form validation, UI control coordination)
- Reusing a component requires dragging in too many dependencies
- You want to change how components collaborate without touching them

**When NOT to use:**
- Only two or three objects need to coordinate — a mediator is overkill, direct reference is fine
- The "mediator" ends up being a God Object that knows everything and does everything

**Structure:**

```typescript
interface Mediator {
  notify(sender: Component, event: string): void;
}

class FormDialog implements Mediator {
  constructor(private checkbox: Checkbox, private input: TextInput) {}

  notify(sender: Component, event: string): void {
    if (sender === this.checkbox && event === 'change') {
      this.input.setVisible(this.checkbox.checked);
    }
  }
}

class Component {
  constructor(protected mediator: Mediator) {}
}
```

**Anti-patterns:**
- Letting the mediator grow into a God Object — split mediators by bounded context
- Using Mediator when Observer would do (see comparison table below)

---

## Memento

**Intent:** Capture an object's internal state as an opaque snapshot, enabling rollback without breaking encapsulation.

**When to use:**
- Undo/redo requires full state restoration (editors, transactions)
- Direct state access would violate encapsulation (private fields must be saved)
- Rollback on error in multi-step operations

**When NOT to use:**
- State is large and snapshots are frequent — RAM consumption becomes prohibitive
- The object's state is easily reconstructible from a command inverse (use Command undo instead)

**Structure:**

```typescript
class Editor {
  private text = '';

  setText(text: string) { this.text = text; }
  save(): Snapshot { return new Snapshot(this.text); }
  restore(s: Snapshot) { this.text = s.getState(); }
}

class Snapshot {
  constructor(private readonly state: string) {}
  getState(): string { return this.state; }
}

class History {
  private snapshots: Snapshot[] = [];
  push(s: Snapshot) { this.snapshots.push(s); }
  pop(): Snapshot | undefined { return this.snapshots.pop(); }
}
```

**Anti-patterns:**
- Exposing Snapshot fields publicly — caretakers should only see opaque snapshots (metadata only)
- Saving snapshots too frequently without a cap strategy (LRU limit, max history depth)

---

## Observer

**Intent:** Define a one-to-many dependency so that when one object changes state, all dependents are notified automatically.

**When to use:**
- State changes in one object need to trigger updates in unknown/dynamic sets of others
- You want loose coupling between publisher and subscriber (different modules, plugins)
- Subscribers should be addable/removable at runtime

**When NOT to use:**
- Notification order matters and must be guaranteed — Observer fires in registration order by default, which is fragile
- Notification chains are deep (A notifies B which notifies C…) — debugging becomes hard, use Mediator instead

**Structure:**

```typescript
interface Subscriber {
  update(event: string, data: unknown): void;
}

class EventEmitter {
  private listeners = new Map<string, Subscriber[]>();

  subscribe(event: string, listener: Subscriber) {
    const existing = this.listeners.get(event) ?? [];
    this.listeners.set(event, [...existing, listener]);
  }

  notify(event: string, data: unknown) {
    this.listeners.get(event)?.forEach(l => l.update(event, data));
  }
}
```

**Anti-patterns:**
- Forgetting to unsubscribe — classic memory leak in long-lived UIs
- Publishing too many fine-grained events — subscribers become overwhelmed; batch or coarsen events

---

## State

**Intent:** Allow an object to change its behavior when its internal state changes, by delegating to a state object rather than branching on a state field.

**When to use:**
- Object behavior changes dramatically with state and the state-specific code grows complex
- State transitions are frequent and involve multiple methods
- You have a finite-state machine with many states and the `if/switch` sprawl is growing

**When NOT to use:**
- Only a few states with simple, rarely-changing transitions — a plain enum + switch is easier to follow
- States don't actually change behavior, just data — State pattern adds class overhead for no gain

**Structure:**

```typescript
interface PlayerState {
  clickPlay(player: AudioPlayer): void;
  clickStop(player: AudioPlayer): void;
}

class PlayingState implements PlayerState {
  clickPlay(player: AudioPlayer) {
    player.stopPlayback();
    player.setState(new ReadyState());
  }
  clickStop(player: AudioPlayer) { player.stopPlayback(); }
}

class AudioPlayer {
  private state: PlayerState = new ReadyState();
  setState(s: PlayerState) { this.state = s; }
  clickPlay() { this.state.clickPlay(this); }
}
```

**Anti-patterns:**
- Letting states depend on each other heavily — states should transition the context, not call sibling state methods directly
- Using State when Strategy would do (see comparison table below)

---

## Strategy

**Intent:** Define a family of interchangeable algorithms, encapsulate each one, and let clients select or swap them at runtime.

**When to use:**
- Multiple variants of an algorithm exist and the right one is chosen at runtime (sorting, routing, pricing)
- You want to eliminate `if/switch` blocks that select algorithm variants
- Algorithms should be testable in isolation without touching the context

**When NOT to use:**
- Only one or two variants exist and they're unlikely to grow — a simple function is cleaner
- Clients can't know which strategy to choose — Strategy requires the caller to understand the differences

**Structure:**

```typescript
interface SortStrategy {
  sort(data: number[]): number[];
}

class QuickSort implements SortStrategy {
  sort(data: number[]): number[] { /* ... */ return data; }
}

class MergeSort implements SortStrategy {
  sort(data: number[]): number[] { /* ... */ return data; }
}

class Sorter {
  constructor(private strategy: SortStrategy) {}
  setStrategy(s: SortStrategy) { this.strategy = s; }
  sort(data: number[]) { return this.strategy.sort(data); }
}
```

**Agent note:** Strategy is the conceptual basis for [[concepts/agent-skills]]. Each skill is a strategy: a named, swappable prompt-template that a context (agent harness) invokes by name. The harness doesn't know the skill's contents — it just calls `execute(skillName, context)`.

**Anti-patterns:**
- Making Strategy objects stateful — they should be pure transformers; state belongs in the context
- Exposing too many strategy variants to clients — use a factory or registry to hide selection logic

---

## Template Method

**Intent:** Define the skeleton of an algorithm in a base class, deferring specific steps to subclasses — without allowing subclasses to change the overall structure.

**When to use:**
- Multiple classes share the same algorithm structure but differ in specific steps (data parsers, report generators)
- You want to enforce a fixed processing order while allowing customization of individual steps
- Reducing duplication across nearly-identical subclasses

**When NOT to use:**
- Composition is preferred over inheritance — use Strategy instead (runtime swap, no subclassing required)
- The algorithm has many steps and subclasses need to skip or reorder them — Template Method is inflexible here

**Structure:**

```typescript
abstract class DataParser {
  // Template method — do not override
  parse(filePath: string): Report {
    const raw = this.readFile(filePath);     // abstract step
    const data = this.parseData(raw);        // abstract step
    this.validate(data);                     // hook (optional override)
    return this.buildReport(data);           // concrete step
  }

  abstract readFile(path: string): string;
  abstract parseData(raw: string): unknown[];
  protected validate(_data: unknown[]): void {} // hook
  private buildReport(data: unknown[]): Report { return { rows: data }; }
}

class CsvParser extends DataParser {
  readFile(path: string): string { return fs.readFileSync(path, 'utf8'); }
  parseData(raw: string): unknown[] { return raw.split('\n').map(r => r.split(',')); }
}
```

**Anti-patterns:**
- Making the template method overridable — subclasses must extend steps, not the skeleton itself
- Adding so many hooks that subclasses can override almost everything — at that point use Strategy

---

## Visitor

**Intent:** Separate an operation from the object structure it operates on, enabling new operations without modifying element classes.

**When to use:**
- You need to add many distinct, unrelated operations to a stable class hierarchy (AST traversal, export formats)
- The element hierarchy is closed for modification but open for new behaviors
- Operations must accumulate state across multiple elements (e.g., collecting metrics while traversing a tree)

**When NOT to use:**
- The element hierarchy changes frequently — every new element type requires updating all visitors
- Elements have complex private state that visitors can't access without breaking encapsulation

**Structure:**

```typescript
interface Visitor {
  visitDot(d: Dot): void;
  visitCircle(c: Circle): void;
}

interface Shape {
  accept(v: Visitor): void;
}

class Dot implements Shape {
  accept(v: Visitor) { v.visitDot(this); }
}

class Circle implements Shape {
  accept(v: Visitor) { v.visitCircle(this); }
}

class XmlExportVisitor implements Visitor {
  visitDot(d: Dot)       { /* emit dot XML */ }
  visitCircle(c: Circle) { /* emit circle XML */ }
}
```

**Anti-patterns:**
- Using Visitor when the element hierarchy is unstable — you'll be updating every visitor on every new class
- Skipping the `accept` method and doing `instanceof` dispatch instead — loses double-dispatch correctness

---

## Domain Event

**Intent:** Represent something meaningful that happened in the domain as an immutable, named, timestamped value object; distribute it to interested parties.

**When to use:**
- You need a full audit log of what triggered state changes
- Multiple downstream systems or services must react to the same business fact
- Building toward Event Sourcing (Domain Events are a prerequisite)
- Cross-aggregate coordination in DDD without tight coupling

**When NOT to use:**
- Simple CRUD with no downstream consumers — event infrastructure adds overhead for no benefit
- The "event" is purely technical (e.g., a cache miss) rather than a domain-meaningful fact

**Structure:**

```typescript
// Immutable source data — never mutated after creation
interface DomainEvent {
  readonly eventType: string;
  readonly occurredAt: Date;        // when it happened in the world
  readonly recordedAt: Date;        // when the system noticed it
}

class OrderPlaced implements DomainEvent {
  readonly eventType = 'OrderPlaced';
  readonly occurredAt: Date;
  readonly recordedAt: Date;

  constructor(
    readonly orderId: string,
    readonly customerId: string,
    occurredAt: Date
  ) {
    this.occurredAt = occurredAt;
    this.recordedAt = new Date();
  }
}

// Event bus (simple synchronous variant; replace with async for production)
class DomainEventBus {
  private handlers = new Map<string, ((e: DomainEvent) => void)[]>();

  subscribe(eventType: string, handler: (e: DomainEvent) => void) {
    const existing = this.handlers.get(eventType) ?? [];
    this.handlers.set(eventType, [...existing, handler]);
  }

  publish(event: DomainEvent) {
    this.handlers.get(event.eventType)?.forEach(h => h(event));
  }
}
```

**Anti-patterns:**
- Mutable event objects — source data must be immutable (retroactive corrections are separate events)
- Publishing events before the transaction commits — subscribers react to facts that may roll back
- Unnamed, generic events (`DataChanged`) — events should name *what happened* in domain language

---

## Confusion Table

Commonly confused pairs:

| Question | Observer | Mediator |
|---|---|---|
| Who knows about whom? | Publisher doesn't know subscribers | All components know only the mediator |
| Coupling direction | One publisher → many subscribers | Many components → one mediator |
| Coordination logic lives in | Each subscriber (distributed) | The mediator (centralized) |
| Use when | Decoupled event fan-out | Complex inter-component orchestration |

| Question | Strategy | State |
|---|---|---|
| Who swaps the behavior? | Client passes in a strategy | Context or the state itself transitions |
| Do behaviors know each other? | No — strategies are independent | Yes — states can trigger transitions to other states |
| Primary intent | Interchangeable algorithm selection | Behavior change driven by internal FSM |
| Use when | Caller chooses the algorithm | Object's own state drives behavior change |

| Question | Command | Chain of Responsibility |
|---|---|---|
| How many handlers? | One pre-configured receiver | Chain tries multiple until one handles |
| Supports undo? | Yes — Commands carry state for reversal | No — handlers are stateless filters |
| Primary intent | Encapsulate & defer a specific operation | Route a request through an ordered filter chain |
| Use when | Undo/redo, queuing, audit trail | Middleware, validation pipelines, event bubbling |

---

## Cross-references

- [[patterns/principles]] — Strategy, Observer, CoR all follow OCP; Iterator and Command follow SRP
- [[patterns/design-patterns-creational]] — Command + Prototype for cloneable command history; Iterator + Factory Method for typed iterators
- [[patterns/design-patterns-structural]] — CoR + Composite (bubble through parent tree); Visitor + Composite (traverse and operate)
- [[concepts/agent-skills]] — Strategy pattern is the direct conceptual basis for the skill architecture in agent harnesses
