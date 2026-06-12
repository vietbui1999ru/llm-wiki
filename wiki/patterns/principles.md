---
title: "Software Design Principles"
type: pattern
tags: [patterns, software-engineering, solid, dry, yagni, kiss]
sources:
  - "The SOLID Principles of Object-Oriented Programming Explained in Plain English.md"
  - "What Is Clean Code? A Guide to Principles and Best Practices.md"
created: 2026-05-06
updated: 2026-05-06
---

# Software Design Principles

Reference for SOLID, DRY, YAGNI, KISS, Law of Demeter, separation of concerns, and composition over inheritance. Each principle is stated, justified, and illustrated with a canonical violation and its fix.

Agent guidance: apply these when writing new classes/functions, and check against them during code review. Violation of multiple principles in one place is a refactor signal.

## Agent Trigger

**Apply when:** Making a design/structure decision or reviewing for design smells (SOLID, DRY, YAGNI, KISS, Law of Demeter).
**Rule of thumb:** Apply the principle that names the smell you actually see; don't over-abstract ahead of need (YAGNI beats speculative DIP).

---

## SOLID

### S — Single Responsibility Principle (SRP)

**Definition:** A class should have exactly one reason to change.

**Rationale:** Multiple responsibilities in one class mean multiple teams/features can modify it for unrelated reasons. Merge conflicts increase; the class becomes a catch-all that is hard to test and replace.

**Violation:**
```java
// Invoice calculates totals, prints to console, AND writes to disk — three reasons to change
public class Invoice {
    public double calculateTotal() { ... }
    public void printInvoice() { System.out.println(...); }
    public void saveToFile(String filename) { ... }
}
```

**Fix:** Extract `InvoicePrinter` and `InvoicePersistence` as separate classes. `Invoice` changes only when business rules change.

**Anti-patterns to catch:**
- A class named `UserManager` or `DataHelper` — "Manager"/"Helper" suffix often means mixed responsibilities
- A class with both `save*` and `render*` methods
- A function that validates, transforms, AND persists in sequence

**Cross-link:** [[concepts/deep-modules]] — deep modules implement SRP by hiding a wide implementation behind a narrow interface.

---

### O — Open-Closed Principle (OCP)

**Definition:** Classes should be open for extension, closed for modification.

**Rationale:** Modifying tested production code risks introducing bugs. Extension via interfaces/abstract classes allows adding behavior without touching existing logic.

**Violation:**
```java
// Every new persistence target requires modifying this class
public class InvoicePersistence {
    public void saveToFile(String filename) { ... }
    public void saveToDatabase() { ... }  // added by modifying the class
}
```

**Fix:** Define an interface, implement per-target:
```java
interface InvoicePersistence { void save(Invoice invoice); }
class FilePersistence implements InvoicePersistence { ... }
class DatabasePersistence implements InvoicePersistence { ... }
```

**Anti-patterns to catch:**
- `if (type == "A") ... else if (type == "B")` in a class that was working — add a new implementor instead
- Adding a method to a class when a new feature is introduced rather than creating a new implementation

**Cross-link:** [[patterns/design-patterns-behavioral]] — Strategy pattern is the canonical OCP implementation.

---

### L — Liskov Substitution Principle (LSP)

**Definition:** A subclass must be substitutable for its base class without altering program correctness.

**Rationale:** Inheritance is a promise: the child extends, never narrows. Violating LSP breaks caller assumptions and produces hard-to-detect runtime bugs.

**Violation:**
```java
// Square overrides Rectangle setters to enforce equal sides,
// breaking callers that set width/height independently
class Square extends Rectangle {
    @Override public void setWidth(int w) { super.setWidth(w); super.setHeight(w); }
    @Override public void setHeight(int h) { super.setHeight(h); super.setWidth(h); }
}
// Caller: r.setHeight(10); expects area = width * 10 — fails for Square
```

**Fix:** Do not inherit. Model `Square` and `Rectangle` as separate implementations of a `Shape` interface with `getArea()`.

**Anti-patterns to catch:**
- Overriding a method to throw `UnsupportedOperationException` or `NotImplementedException`
- A child class that ignores or no-ops a parent method
- Checking `instanceof` before calling a method — signals the type hierarchy is wrong

---

### I — Interface Segregation Principle (ISP)

**Definition:** Many small, client-specific interfaces are better than one large general-purpose interface.

**Rationale:** Forcing implementors to stub out methods they don't need pollutes the codebase and misleads readers. A `FreeParking` that implements `doPayment()` with `throw new Exception` is a lie.

**Violation:**
```java
interface ParkingLot {
    void parkCar(); void unparkCar(); void getCapacity();
    double calculateFee(Car car); void doPayment(Car car);  // payment shouldn't be mandatory
}
class FreeParking implements ParkingLot {
    public void doPayment(Car car) { throw new Exception("Parking lot is free"); }  // forced stub
}
```

**Fix:** Split into `ParkingLot` (park/unpark/capacity) and `PaidParkingLot extends ParkingLot` (fee/payment).

**Anti-patterns to catch:**
- An interface with 10+ methods
- Implementations that stub methods with empty bodies or exceptions
- A single interface imported by many unrelated consumers

**Cross-link:** [[concepts/deep-modules]] — ISP is the interface-side expression of deep modules; keep public surface narrow.

---

### D — Dependency Inversion Principle (DIP)

**Definition:** Depend on abstractions (interfaces/abstract classes), not concrete implementations.

**Rationale:** High-level modules should not be coupled to low-level details. When both depend on an abstraction, either can change independently.

**Violation:**
```java
class PersistenceManager {
    FilePersistence filePersistence;  // depends on concrete class
}
```

**Fix:**
```java
class PersistenceManager {
    InvoicePersistence invoicePersistence;  // depends on interface
    BookPersistence bookPersistence;
}
```

**Anti-patterns to catch:**
- `new ConcreteService()` inside a business-logic class instead of injecting it
- Unit tests that are hard to write because real dependencies (DB, HTTP) are constructed inline

**Note:** DIP is the mechanism that makes OCP work. If OCP is the goal, DIP is how you get there.

---

## DRY — Don't Repeat Yourself

**Definition:** Every piece of knowledge must have a single, unambiguous representation in the system.

**Rationale:** Duplicated logic means changes must be made in multiple places. One missed location creates divergence and bugs.

**Violation:**
```python
def calculate_book_price(quantity, price): return quantity * price
def calculate_laptop_price(quantity, price): return quantity * price
```

**Fix:** `def calculate_product_price(quantity, price): return quantity * price`

**Anti-patterns to catch:**
- Copy-paste with minor variable name changes
- The same validation logic in the controller, service, and model layers
- Comments that describe what the code does — the code should express it; if it can't, extract a named function

**Qualifier:** DRY is about knowledge, not code. Two functions that look identical but represent different business rules should not be merged.

---

## YAGNI — You Aren't Gonna Need It

**Definition:** Do not add functionality until it is required.

**Rationale:** Speculative code adds complexity, needs maintenance, and is often wrong about what will actually be needed.

**Anti-patterns to catch:**
- A `strategy` parameter added "in case we need to swap algorithms later"
- Abstract base classes created before there is a second implementor
- Configuration flags for behavior that has no current user

**When to ignore:** When a known requirement is arriving in the next sprint and the upfront cost of extensibility is small.

---

## KISS — Keep It Simple, Stupid

**Definition:** Prefer the simplest solution that satisfies the requirement.

**Rationale:** Complexity is the primary source of bugs, onboarding cost, and maintenance burden. Clever code is a liability.

**Anti-patterns to catch:**
- Using a design pattern when a plain function works
- Premature abstraction: interfaces with one implementation, factories that construct one type
- Nested ternaries, one-liners that require 30 seconds to parse

**Agent guidance:** When two solutions both work, prefer the one with fewer moving parts, fewer files, and fewer concepts to hold in working memory.

---

## Law of Demeter (LoD) / Principle of Least Knowledge

**Definition:** A method should only call methods on: itself, its parameters, objects it creates, its direct component objects. Do not call methods on objects returned by other calls.

**Rationale:** Long chains like `a.getB().getC().doSomething()` create tight coupling between `A` and the internals of `B` and `C`. Changes to intermediate types ripple outward.

**Violation:**
```python
total = order.getCart().getItems().calculateTotal()
```

**Fix:** `total = order.getTotal()` — `Order` exposes total directly, hiding the cart/items structure.

**Anti-patterns to catch:**
- Method chains longer than two hops (`obj.getX().getY().doZ()`)
- Passing a large object just to extract one field — pass the field directly

---

## Separation of Concerns (SoC)

**Definition:** Different concerns (business logic, persistence, presentation, validation) belong in distinct modules.

**Rationale:** Mixed concerns make each part harder to test and replace. A component that validates, saves, and emails is coupled to three external systems.

**Anti-patterns to catch:**
- SQL queries in a React component
- HTTP response formatting in a database repository
- Auth logic scattered across route handlers

**Cross-link:** SoC is SRP applied at the architectural level. SRP applies within a class; SoC applies across modules and layers.

---

## Composition Over Inheritance

**Definition:** Favor building behavior by composing objects with the desired capability rather than inheriting from a base class.

**Rationale:** Inheritance creates tight coupling through the class hierarchy. Adding behavior via composition keeps classes independent and substitutable.

**Violation:** `class LoggingService extends EmailService` — `LoggingService` inherits all of `EmailService`'s interface and internals just to add logging before sends.

**Fix:** `class LoggingService { constructor(private inner: EmailService) {} }` — wraps and delegates.

**Anti-patterns to catch:**
- Deep inheritance hierarchies (3+ levels)
- Inheriting just to reuse a utility method — inject the utility instead
- `extends BaseController`, `extends BaseRepository` with large shared state

**Cross-link:** [[patterns/design-patterns-structural]] — Decorator pattern is composition over inheritance made explicit.

---

## Summary: When to Apply Which Principle

| Situation | Check |
|---|---|
| Adding a method to an existing class | SRP — does this belong here? |
| New feature requires modifying a working class | OCP — can you extend instead? |
| Using inheritance | LSP — is the subtype truly substitutable? |
| Designing an interface | ISP — is every method needed by every implementor? |
| Constructing dependencies inside a class | DIP — can you inject instead? |
| Tempted to copy-paste logic | DRY — extract a named abstraction |
| Adding "future-proof" flexibility | YAGNI — do you have a concrete requirement? |
| Solution is growing complex | KISS — what is the simplest path? |
| Calling a method on a return value | LoD — expose what callers need directly |

---

## Related pages

- [[concepts/deep-modules]] — Ousterhout's framing: narrow interface, wide implementation; intersects SRP, ISP
- [[patterns/code-quality]] — Naming, function discipline, complexity — the tactical application of these principles
- [[patterns/design-patterns-behavioral]] — Strategy (OCP), Observer, Command; behavioral patterns that implement SOLID
- [[patterns/design-patterns-structural]] — Decorator (composition over inheritance), Adapter, Proxy
- [[patterns/refactoring]] — Mechanics for moving from violation to compliance
