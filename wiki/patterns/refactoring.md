---
title: "Refactoring Techniques"
type: pattern
tags: [patterns, software-engineering, refactoring, code-quality]
sources: ["Refactoring and Design Patterns.md"]
created: 2026-05-06
updated: 2026-05-06
---

# Refactoring Techniques

Systematic code improvement without changing behavior. Each technique has a specific trigger — apply when the smell appears, not speculatively. Source: Fowler's refactoring catalog (refactoring.guru).

See also: [[patterns/principles]], [[patterns/code-quality]], [[patterns/design-patterns-behavioral]]

## Agent Trigger

**Apply when:** Improving existing code structure without changing behavior, or reviewing a large/complex function.
**Rule of thumb:** Pick the named technique (Extract Method, Replace Conditional with Polymorphism, etc.) that targets the specific smell; refactor in small behavior-preserving steps.

---

## Extract Method / Function

**What:** Pull a code block into a named function.

**Trigger:** Block needs a comment to explain it; function exceeds one screen; duplicated logic across two sites.

```python
# Before
def print_order(order):
    print(f"Order #{order.id}")
    total = sum(item.price for item in order.items)
    print(f"Total: {total}")

# After
def print_order(order):
    print_header(order)
    print_total(order)

def print_header(order):
    print(f"Order #{order.id}")

def print_total(order):
    print(f"Total: {sum(item.price for item in order.items)}")
```

**Anti-pattern:** Extracting fragments too small to name meaningfully. If you can't name it, it's not a unit.

---

## Extract Variable

**What:** Name a complex expression by assigning it to a local variable.

**Trigger:** Expression appears more than once; expression is hard to read inline.

```python
# Before
if user.age >= 18 and user.country in ALLOWED_COUNTRIES and not user.banned:

# After
is_eligible = user.age >= 18 and user.country in ALLOWED_COUNTRIES and not user.banned
if is_eligible:
```

---

## Inline Function

**What:** Replace a trivial function call with its body.

**Trigger:** Function body is as clear as its name; function is called in only one place and adds no abstraction value.

```python
# Before
def is_senior(driver):
    return driver.age > 65

if is_senior(driver): ...

# After
if driver.age > 65: ...
```

**Anti-pattern:** Inlining functions that are called from multiple sites — creates duplication.

---

## Move Function

**What:** Relocate a function to the class/module that uses it most.

**Trigger:** Function references data from another class more than its own; function is used exclusively by one other module.

**Agent note:** Run this when a function's imports are dominated by another module's types. Move it there.

---

## Replace Temp with Query

**What:** Replace a temporary variable with a method call.

**Trigger:** Temp variable is computed once and only read; same computation needed in subclasses.

```python
# Before
base = quantity * price
if base > 1000:
    return base * 0.95

# After
def base_price(self):
    return self.quantity * self.price

if self.base_price() > 1000:
    return self.base_price() * 0.95
```

**Trade-off:** Adds a function call overhead. Only applies when clarity outweighs micro-performance concerns.

---

## Introduce Parameter Object

**What:** Bundle related parameters into a single object or dataclass.

**Trigger:** Multiple functions share the same parameter group (3+ params that always travel together).

```python
# Before
def book_room(start_date, end_date, guest_count, room_type): ...

# After
@dataclass
class BookingRequest:
    start_date: date
    end_date: date
    guest_count: int
    room_type: str

def book_room(request: BookingRequest): ...
```

---

## Replace Conditional with Polymorphism

**What:** Replace a type-switch or if/elif chain with subclass dispatch.

**Trigger:** Conditional branches on a type tag; same conditional pattern repeats across multiple methods.

```python
# Before
def get_speed(bird):
    if bird.type == "European":
        return base_speed()
    elif bird.type == "African":
        return base_speed() - bird.load_factor * 2
    elif bird.type == "Norwegian Blue":
        return 0 if bird.nailed else base_speed()

# After
class EuropeanSwallow(Bird):
    def speed(self): return base_speed()

class AfricanSwallow(Bird):
    def speed(self): return base_speed() - self.load_factor * 2

class NorwegianBlueParrot(Bird):
    def speed(self): return 0 if self.nailed else base_speed()
```

**Agent note:** This requires a class hierarchy. If you only have one conditional site and no future extension planned, the complexity cost may not be worth it.

---

## Decompose Conditional

**What:** Extract condition and branches into well-named functions.

**Trigger:** Condition or branch body is complex enough to need comments.

```python
# Before
if date < SUMMER_START or date > SUMMER_END:
    charge = quantity * winter_rate + winter_service_charge
else:
    charge = quantity * summer_rate

# After
if is_winter(date):
    charge = winter_charge(quantity)
else:
    charge = summer_charge(quantity)
```

---

## Replace Magic Number with Constant

**What:** Assign a named constant to any literal that carries meaning.

**Trigger:** Numeric or string literal appears in logic; its meaning is not obvious from context.

```python
# Before
if order.items > 10:
    discount = 0.05

# After
BULK_ORDER_THRESHOLD = 10
BULK_DISCOUNT_RATE = 0.05

if order.items > BULK_ORDER_THRESHOLD:
    discount = BULK_DISCOUNT_RATE
```

---

## Replace Error Code with Exception

**What:** Throw an exception instead of returning a sentinel error value.

**Trigger:** Callers must check a return value for error status before using it; error handling is frequently skipped.

```python
# Before
def find_user(id):
    user = db.get(id)
    if user is None:
        return -1
    return user

# After
def find_user(id):
    user = db.get(id)
    if user is None:
        raise UserNotFoundError(f"No user with id={id}")
    return user
```

**Anti-pattern:** Using exceptions for normal control flow (e.g., checking if a value exists before inserting).

---

## Pull Up Method

**What:** Move a method from subclasses to their shared parent.

**Trigger:** Two or more subclasses have identical or near-identical method implementations.

**Process:**
1. Verify both implementations are truly identical (or differ only in variable names).
2. Move to parent.
3. Remove from subclasses.

---

## Push Down Method

**What:** Move a method from a parent to only the subclasses that use it.

**Trigger:** Method in parent is only relevant to one subclass; other subclasses inherit dead weight.

---

## Extract Class

**What:** Split one class into two, each with a single responsibility.

**Trigger:** Class has fields and methods that naturally cluster into two groups; class is growing toward 200+ lines.

```
Before: class Person { name, phone, areaCode, officePhone, ... }
After:  class Person { name, ... }
        class TelephoneNumber { phone, areaCode, officePhone }
```

---

## Inline Class

**What:** Merge a class back into its only user.

**Trigger:** Class has so little responsibility remaining that it no longer justifies its existence (often after prior refactoring).

**Anti-pattern:** Inlining a class that is used by more than one caller — creates coupling.

---

## Refactoring Order of Operations

When tackling a messy file, apply in this sequence:

1. **Extract Variable** — name confusing expressions
2. **Extract Method** — isolate logical units
3. **Move Function** — place code near its data
4. **Introduce Parameter Object** — reduce parameter sprawl
5. **Replace Conditional with Polymorphism** — only if the type-switch pattern is pervasive

Do not apply all techniques at once. One refactoring at a time, with tests passing after each step.
