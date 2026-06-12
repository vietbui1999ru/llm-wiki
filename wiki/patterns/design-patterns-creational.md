---
title: "Creational Design Patterns"
type: pattern
tags: [patterns, software-engineering, oop, typescript, go]
sources:
  - "Factory Method.md"
  - "Abstract Factory.md"
  - "Abstract Factory in Go.md"
  - "Builder.md"
  - "Prototype.md"
  - "Singleton.md"
  - "Design Patterns in TypeScript.md"
created: 2026-05-06
updated: 2026-05-06
---

# Creational Design Patterns

The five GoF creational patterns: when to reach for each, how they're structured, and what to avoid.

All five answer the same question — "how do I create an object?" — but at different levels of complexity and constraint. See the [[patterns/principles]] page for OCP and DIP, which these patterns repeatedly apply.

## Agent Trigger

**Apply when:** Deciding how objects get constructed — Factory Method, Abstract Factory, Builder, Prototype, or Singleton.
**Rule of thumb:** Introduce a creational pattern only when construction varies or must be controlled — avoid Singleton unless truly required.

---

## Factory Method

**Intent**: Define a factory method in a superclass; subclasses override it to change what product gets created.

**When to use**:
- You need to extend a library/framework by substituting a component (e.g., swap button type without rewriting UI logic).
- The exact type of object to create isn't known until runtime.
- You want to return cached/pooled objects rather than always constructing fresh ones.

**When NOT to use**:
- You have a simple flat set of product types with no inheritance hierarchy — a plain function or map is cleaner.
- Product families need to stay consistent across multiple dimensions (reach for Abstract Factory instead).

**Structure**:

```typescript
interface Transport {
  deliver(): void;
}

class Truck implements Transport {
  deliver() { /* by road */ }
}

class Ship implements Transport {
  deliver() { /* by sea */ }
}

abstract class Logistics {
  // factory method — subclasses override this
  abstract createTransport(): Transport;

  planDelivery() {
    const t = this.createTransport();
    t.deliver();
  }
}

class RoadLogistics extends Logistics {
  createTransport(): Transport { return new Truck(); }
}

class SeaLogistics extends Logistics {
  createTransport(): Transport { return new Ship(); }
}
```

**Anti-patterns**:
- Putting a `switch` on type inside the factory method — that's a parametric factory, not Factory Method. Extract to subclasses or use a registry.
- Conflating the creator's primary responsibility with product creation. The creator has business logic; the factory method is a hook.

---

## Abstract Factory

**Intent**: Produce families of related objects through a single interface, guaranteeing cross-family compatibility.

**When to use**:
- You have a matrix of (product types) × (variants) and need to ensure variant consistency — e.g., all UI elements must be Windows-style or all Mac-style, never mixed.
- You want to swap an entire product family at the injection point without touching client code.
- You're writing a platform-neutral library that delegates platform specifics to the host.

**When NOT to use**:
- You only have one product type to create — use Factory Method.
- Adding a new product type requires touching every concrete factory — the cost grows with every new product dimension.

**Structure**:

```typescript
interface Button { paint(): void; }
interface Checkbox { paint(): void; }

interface GUIFactory {
  createButton(): Button;
  createCheckbox(): Checkbox;
}

class WinFactory implements GUIFactory {
  createButton(): Button { return new WinButton(); }
  createCheckbox(): Checkbox { return new WinCheckbox(); }
}

class MacFactory implements GUIFactory {
  createButton(): Button { return new MacButton(); }
  createCheckbox(): Checkbox { return new MacCheckbox(); }
}

// Client only sees GUIFactory — never WinFactory or MacFactory directly
class Application {
  constructor(private factory: GUIFactory) {}
  buildUI() {
    const btn = this.factory.createButton();
    btn.paint();
  }
}
```

**Anti-patterns**:
- Making the factory a Singleton when you need multiple configurations in the same process (e.g., testing).
- Growing the factory interface for every minor product variation — prefer composition or a parameterized product instead.

---

## Builder

**Intent**: Construct a complex object step by step; the same construction process can produce different representations.

**When to use**:
- Object construction requires many optional parameters, producing the "telescoping constructor" smell.
- You need to produce multiple representations from the same step sequence (e.g., a car and its manual).
- Construction steps must run in a controlled order or can be deferred/recursed (e.g., Composite trees).

**When NOT to use**:
- The object is simple with 2–3 required fields — just use a constructor or a plain object literal.
- All fields are required; the step-by-step API provides no value over a single constructor call.

**Structure**:

```typescript
interface QueryBuilder {
  setTable(name: string): this;
  addWhere(clause: string): this;
  addLimit(n: number): this;
  build(): string;
}

class SelectQueryBuilder implements QueryBuilder {
  private parts: { table?: string; wheres: string[]; limit?: number } =
    { wheres: [] };

  setTable(name: string): this { this.parts.table = name; return this; }
  addWhere(clause: string): this { this.parts.wheres.push(clause); return this; }
  addLimit(n: number): this { this.parts.limit = n; return this; }

  build(): string {
    let q = `SELECT * FROM ${this.parts.table}`;
    if (this.parts.wheres.length) q += ` WHERE ${this.parts.wheres.join(' AND ')}`;
    if (this.parts.limit) q += ` LIMIT ${this.parts.limit}`;
    return q;
  }
}

// Usage — method chaining form (Director is optional)
const query = new SelectQueryBuilder()
  .setTable('users')
  .addWhere('active = true')
  .addLimit(10)
  .build();
```

**Anti-patterns**:
- Not calling `reset()` between builds — previous state leaks into the next product.
- Putting the `build()` result type on the builder interface when builders produce incompatible types (it breaks typing).
- Skipping the Director when the same step sequence is duplicated across callers — extract it.

---

## Prototype

**Intent**: Clone an existing configured object rather than constructing and configuring from scratch.

**When to use**:
- You receive an object through an interface and need a copy, but don't know (or can't depend on) its concrete class.
- Construction is expensive and the object differs only slightly from a known baseline — clone the baseline and mutate.
- You want to eliminate subclasses that exist only to encode configuration variants.

**When NOT to use**:
- The object has circular references or holds external resources (DB connections, file handles) — deep clone semantics become tricky.
- The class is simple enough to reconstruct cheaply from a factory.

**Structure**:

```typescript
interface Cloneable<T> {
  clone(): T;
}

class Shape implements Cloneable<Shape> {
  constructor(
    public x: number,
    public y: number,
    public color: string,
  ) {}

  clone(): Shape {
    return new Shape(this.x, this.y, this.color);
  }
}

class Circle extends Shape {
  constructor(x: number, y: number, color: string, public radius: number) {
    super(x, y, color);
  }

  clone(): Circle {
    return new Circle(this.x, this.y, this.color, this.radius);
  }
}

// Prototype registry pattern
const registry = new Map<string, Shape>([
  ['red-circle', new Circle(0, 0, 'red', 10)],
]);

const copy = registry.get('red-circle')!.clone();
```

**Anti-patterns**:
- Shallow clone when the object contains nested mutable references — child objects are aliased, not independent.
- Forgetting to override `clone()` in subclasses — the parent version returns the parent type, silently losing subclass fields.

---

## Singleton

**Intent**: Ensure exactly one instance of a class exists in the process, with a global access point.

**When to use**:
- A single shared resource must be coordinated globally — e.g., a connection pool, a logger, a config store.
- You need stricter control than a global variable provides (the instance can't be overwritten externally).

**When NOT to use**:
- The "global access" need can be satisfied by dependency injection — prefer DI; it keeps the code testable.
- You'd need multiple instances in tests or in different scopes (multi-tenant, per-request). Singleton collapses those.
- The class has meaningful mutable state that different callers should not share.

**Structure**:

```typescript
class Database {
  private static instance: Database | null = null;

  // Private constructor: prevents `new Database()` from outside
  private constructor(private readonly url: string) {}

  static getInstance(url: string): Database {
    if (!Database.instance) {
      Database.instance = new Database(url);
    }
    return Database.instance;
  }

  query(sql: string): void { /* ... */ }
}

const db = Database.getInstance('postgres://localhost/app');
```

For Node.js: module-level `export const db = new Database(url)` is often sufficient and more testable — reserve the class-based Singleton for cases where lazy initialization or explicit control matters.

**Anti-patterns**:
- Using Singleton as a substitute for proper dependency injection — hides coupling, kills testability.
- Not handling thread-safety in languages where it matters (Java, Go, Rust) — double-checked locking or `sync.Once` required.
- Treating factory classes (AbstractFactory, Builder) as Singletons without considering test isolation — valid but declare it explicitly.

---

## Comparison: when to reach for each

| Need | Pattern |
|---|---|
| Subclass decides which product type to create | **Factory Method** |
| Swap entire product family (variant consistency) | **Abstract Factory** |
| Construct complex object with many optional steps | **Builder** |
| Copy a configured object, class unknown at call site | **Prototype** |
| Exactly one instance, globally accessible | **Singleton** |
| Simple one-type construction, no variation | Plain constructor / object literal |

**Evolution path**: designs often start with Factory Method, then grow to Abstract Factory when a second product type is needed, then to Builder when construction becomes multi-step.

---

See also:
- [[patterns/principles]] — OCP and DIP, which these patterns enforce
- [[patterns/design-patterns-structural]] — Adapter, Bridge, Decorator, Facade, etc.
- [[patterns/design-patterns-behavioral]] — Strategy, Observer, Command, etc.
