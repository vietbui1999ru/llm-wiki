---
title: "Structural Design Patterns"
type: pattern
tags: [patterns, software-engineering, gof, structural, typescript]
sources:
  - "Adapter.md"
  - "Bridge.md"
  - "Composite.md"
  - "Decorator.md"
  - "Facade.md"
  - "Flyweight.md"
  - "Proxy.md"
  - "Design Patterns in TypeScript.md"
created: 2026-05-06
updated: 2026-05-06
---

# Structural Design Patterns

The seven GoF structural patterns describe how to compose classes and objects into larger structures. Each controls what the caller sees (the interface) and what actually executes behind it. They enforce [[patterns/principles]] — SRP, OCP — through composition rather than inheritance.

See also: [[patterns/design-patterns-creational]], [[patterns/design-patterns-behavioral]], [[concepts/deep-modules]]

## Agent Trigger

**Apply when:** Composing or adapting objects/interfaces — Adapter, Decorator, Facade, Proxy, Composite, Bridge, or Flyweight.
**Rule of thumb:** Pick by intent — Adapter converts, Facade simplifies, Proxy controls access, Decorator adds behavior.

---

## Adapter

**Intent:** Convert an incompatible interface into one the client expects — without modifying either side.

**When to use:**
- Integrating a third-party or legacy class whose interface you cannot change.
- Reusing existing subclasses that share behavior but differ in interface.
- Translating between data formats (e.g., XML → JSON) at a boundary.

**When NOT to use:**
- You control both sides — just align the interfaces directly.
- The mismatch is so deep that the adapter becomes a full reimplementation (consider a new service instead).

**Structure:**

```typescript
interface Target {
  request(): string;
}

class LegacyService {
  specificRequest(): string { return "legacy result"; }
}

class Adapter implements Target {
  constructor(private adaptee: LegacyService) {}
  request(): string {
    return this.adaptee.specificRequest();
  }
}

// Client only sees Target — unaware of LegacyService
const client = (t: Target) => t.request();
client(new Adapter(new LegacyService()));
```

**Anti-patterns:**
- Wrapping every class "just in case" — Adapter is a boundary tool, not a default abstraction.
- Class adapter via multiple inheritance: TypeScript lacks it; prefer object composition.
- Bidirectional adapters: almost always a sign the design needs rethinking.

---

## Bridge

**Intent:** Decouple an abstraction from its implementation so both can vary independently.

**When to use:**
- A class hierarchy is growing across two orthogonal dimensions (e.g., shapes × renderers, remotes × devices).
- You want to switch implementations at runtime.
- Designed up-front when you know two axes of variation will coexist long-term.

**When NOT to use:**
- Only one dimension varies — Bridge adds unnecessary indirection.
- The class is already cohesive; splitting it creates more complexity than it removes.

**Structure:**

```typescript
interface Renderer {
  drawCircle(x: number, y: number, r: number): void;
}

class SVGRenderer implements Renderer {
  drawCircle(x, y, r) { /* SVG output */ }
}
class CanvasRenderer implements Renderer {
  drawCircle(x, y, r) { /* Canvas output */ }
}

// Abstraction holds a reference to the implementation
class Circle {
  constructor(
    private renderer: Renderer,
    private x: number, private y: number, private r: number
  ) {}
  draw() { this.renderer.drawCircle(this.x, this.y, this.r); }
}

// Mix freely: new Circle(new SVGRenderer(), 0, 0, 5).draw()
```

**Anti-patterns:**
- Confusing Bridge with Strategy — Bridge separates structural hierarchies at design time; Strategy swaps algorithms at runtime within one object.
- Applying Bridge reactively to an existing monolith without first identifying the two independent dimensions.

---

## Composite

**Intent:** Compose objects into tree structures and treat leaves and containers uniformly through a common interface.

**When to use:**
- The domain naturally forms a recursive hierarchy (filesystem, UI component tree, org chart, AST).
- Client code should not distinguish between single elements and collections of elements.
- Operations need to propagate recursively (render, calculate, validate).

**When NOT to use:**
- The data is not actually recursive — force-fitting a flat list into Composite adds noise.
- Leaf and container operations diverge so much that a shared interface becomes meaningless.

**Structure:**

```typescript
interface Component {
  render(): string;
}

class Leaf implements Component {
  constructor(private name: string) {}
  render() { return this.name; }
}

class Container implements Component {
  private children: Component[] = [];
  add(c: Component) { this.children.push(c); }
  render() { return this.children.map(c => c.render()).join(", "); }
}

// Client treats both identically
const root = new Container();
root.add(new Leaf("a"));
const sub = new Container();
sub.add(new Leaf("b"));
root.add(sub);
root.render(); // "a, b"
```

**Anti-patterns:**
- Putting `add`/`remove` on the `Component` interface — leaves must throw or no-op, violating ISP. Keep child management on `Container`.
- Composite with a single level of nesting — just use an array.

---

## Decorator

**Intent:** Attach additional responsibilities to an object at runtime by wrapping it in another object that shares the same interface.

**When to use:**
- You need combinatorial behavior without a subclass explosion (logging + caching + auth on a handler).
- Behavior should be stackable and independently removable at composition time.
- The class is `final` or you cannot modify it.

**When NOT to use:**
- Order of decorators matters in non-obvious ways — prefer an explicit pipeline.
- You only need one variation — a simple subclass is clearer.

**Structure:**

```typescript
interface Logger {
  log(msg: string): void;
}

class ConsoleLogger implements Logger {
  log(msg: string) { console.log(msg); }
}

class TimestampDecorator implements Logger {
  constructor(private inner: Logger) {}
  log(msg: string) { this.inner.log(`[${Date.now()}] ${msg}`); }
}

class LevelDecorator implements Logger {
  constructor(private inner: Logger, private level: string) {}
  log(msg: string) { this.inner.log(`${this.level}: ${msg}`); }
}

// Stack at composition time:
const logger = new LevelDecorator(new TimestampDecorator(new ConsoleLogger()), "INFO");
logger.log("ready"); // INFO: [1714000000000] ready
```

**Anti-patterns:**
- Stateful decorators that depend on their position in the stack — behavior becomes order-sensitive and fragile.
- Deep decorator chains for a single cross-cutting concern — collapse into one class.
- Confusing Decorator with Proxy: Decorator adds behavior the client explicitly composed; Proxy controls access that the client doesn't manage.

---

## Facade

**Intent:** Provide a simplified, opinionated interface to a complex subsystem.

**When to use:**
- Integrating a framework with many moving parts where clients need only a small slice.
- Isolating the rest of the codebase from a third-party dependency so a swap changes only the facade.
- Layering a subsystem — each layer gets a facade; layers communicate through facades only.

**When NOT to use:**
- Clients need the full subsystem power — a facade that re-exposes everything is just indirection.
- The subsystem has only 2-3 classes — the facade adds a maintenance layer for nothing.

**Structure:**

```typescript
// Complex subsystem internals (unchanged, 3rd-party or legacy)
class AuthService { verify(token: string): boolean { return true; } }
class RateLimiter { allow(userId: string): boolean { return true; } }
class AuditLog { record(event: string): void { /* ... */ } }

// Facade: one entry point for the common case
class ApiGateway {
  private auth = new AuthService();
  private limiter = new RateLimiter();
  private audit = new AuditLog();

  handleRequest(token: string, userId: string, action: string): boolean {
    if (!this.auth.verify(token)) return false;
    if (!this.limiter.allow(userId)) return false;
    this.audit.record(action);
    return true;
  }
}
```

**Anti-patterns:**
- God-object facade that owns all subsystem logic — it becomes the monolith you were hiding.
- Facade that leaks subsystem types through its return values — callers become coupled to internals anyway.
- Multiple facades for the same subsystem with overlapping responsibilities.

---

## Flyweight

**Intent:** Share the immutable (intrinsic) state among many fine-grained objects, passing mutable (extrinsic) state in per-operation calls, to reduce memory consumption.

**When to use:**
- The app creates enormous numbers of similar objects (particles, glyphs, map tiles) that exhaust available RAM.
- Objects can be cleanly split into intrinsic (shared, immutable) and extrinsic (per-instance, mutable) state.
- Profiling confirms the memory problem exists — apply this pattern deliberately, not speculatively.

**When NOT to use:**
- Object count is small — the factory and split state add complexity for no measurable gain.
- State cannot be cleanly separated — you end up passing most state as arguments anyway.

**Structure:**

```typescript
// Flyweight: immutable shared state
class GlyphType {
  constructor(readonly char: string, readonly font: string, readonly size: number) {}
  render(canvas: CanvasRenderingContext2D, x: number, y: number): void {
    // draw this.char at (x, y) using this.font/size
  }
}

// Factory: pool guarantees identity sharing
class GlyphFactory {
  private pool = new Map<string, GlyphType>();
  get(char: string, font: string, size: number): GlyphType {
    const key = `${char}|${font}|${size}`;
    if (!this.pool.has(key)) this.pool.set(key, new GlyphType(char, font, size));
    return this.pool.get(key)!;
  }
}

// Context: extrinsic state (position) lives here, not in GlyphType
class Glyph {
  constructor(readonly type: GlyphType, readonly x: number, readonly y: number) {}
  render(canvas: CanvasRenderingContext2D) { this.type.render(canvas, this.x, this.y); }
}
```

**Anti-patterns:**
- Making flyweights mutable — shared state becomes a data-race source; flyweights must be immutable after construction.
- Using Flyweight without a factory — callers manually manage the pool and create duplicate instances.
- Treating it as a general caching mechanism — Flyweight is specifically about object identity sharing for memory reduction.

---

## Proxy

**Intent:** Provide a drop-in substitute that controls access to the real object — adding lazy init, caching, access control, logging, or lifecycle management transparently.

**When to use:**
- Lazy initialization of a heavyweight resource you don't always need (virtual proxy).
- Access control — only authorized callers reach the real service (protection proxy).
- Caching repeated identical calls (caching proxy).
- Logging or auditing every call without touching the service class (logging proxy).
- Hiding network call complexity behind a local interface (remote proxy).

**When NOT to use:**
- You only need to intercept one method — a simple wrapper function is less indirection.
- The pre/post logic changes what the interface means for the caller — use Decorator instead (client-controlled composition, not infrastructure interception).

**Structure:**

```typescript
interface DataStore {
  fetch(id: string): Promise<Record<string, unknown>>;
}

class RealDataStore implements DataStore {
  async fetch(id: string) { /* expensive DB call */ return {}; }
}

class CachingProxy implements DataStore {
  private cache = new Map<string, Record<string, unknown>>();
  constructor(private real: DataStore) {}

  async fetch(id: string) {
    if (!this.cache.has(id)) {
      this.cache.set(id, await this.real.fetch(id));
    }
    return this.cache.get(id)!;
  }
}

// Client receives DataStore — unaware of caching layer
const store: DataStore = new CachingProxy(new RealDataStore());
```

**Anti-patterns:**
- Proxy that changes the observable behavior of the interface — that's Decorator.
- Combining caching + logging + auth into one proxy class — compose separate proxies or extract middleware.
- Proxy that swallows errors silently — control access, don't hide failures from callers.

---

## Confusion Table: Adapter vs Facade vs Proxy

These three all wrap something. The differences are precise:

| | **Adapter** | **Facade** | **Proxy** |
|---|---|---|---|
| **Interface change** | Yes — converts incompatible to compatible | Yes — defines a new simplified interface | No — same interface as the real object |
| **Scope** | One object | Entire subsystem (many objects) | One object |
| **When designed** | Reactive — fixes existing incompatibility | Reactive or proactive | Proactive or reactive |
| **Client aware?** | Uses the new compatible interface | Uses the simpler interface | Fully transparent — same interface |
| **Purpose** | Interface translation | Complexity hiding | Access control / interception |
| **Typical trigger** | Third-party library has wrong shape | Complex subsystem with many callers | Lazy init, caching, auth, logging |

Quick rule: need a **different interface** → Adapter. Need a **simpler interface** to a subsystem → Facade. Need the **same interface** with interception → Proxy.

---

## Pattern Selection Signals

| Signal in code | Pattern |
|---|---|
| `legacyService.weirdMethod()` needs to satisfy `interface Foo` | Adapter |
| Class hierarchy exploding across two independent dimensions | Bridge |
| Recursive `children: T[]` with uniform `operation()` | Composite |
| Stacking optional behaviors (logging, compression, encryption) on a base object | Decorator |
| `new SubsystemA(); new SubsystemB(); ...` repeated across many callers | Facade |
| Millions of near-identical objects with shared constant data draining RAM | Flyweight |
| Need caching/auth/lazy-init without modifying the real class | Proxy |
