---
title: "Code Quality Heuristics"
type: concept
tags: [patterns, software-engineering, clean-code, naming, refactoring]
sources:
  - "What Is Clean Code? A Guide to Principles and Best Practices.md"
  - "The SOLID Principles of Object-Oriented Programming Explained in Plain English.md"
created: 2026-05-06
updated: 2026-05-06
---

# Code Quality Heuristics

Tactical rules for writing readable, maintainable code: naming, function discipline, cognitive complexity, comment discipline, magic number elimination, and code smell identification.

Agent guidance: apply these when generating or reviewing code. When a heuristic is violated, flag it in review and fix it before marking work complete. These rules apply to AI-generated code with equal force — LLMs are known to violate DRY, produce long functions, and generate inconsistent naming.

---

## Naming Conventions

**Core rule:** A name should tell you why it exists, what it does, and how it is used. If a name requires a comment to explain it, the name is wrong.

### Variables

| Anti-pattern | Fix | Reason |
|---|---|---|
| `d`, `x`, `tmp` | `elapsed_days`, `user_index`, `cached_result` | Single letters give no context |
| `price` | `product_price` | Ambiguous scope; what product? |
| `data`, `info`, `stuff` | name the actual content | Noise words that communicate nothing |
| `flag`, `check`, `flag2` | `is_authenticated`, `has_pending_orders` | Boolean names should be yes/no questions |

### Functions

- Name with verb + noun: `calculate_total`, `fetch_user`, `validate_email`
- Boolean-returning functions: `is_`, `has_`, `can_`, `should_` prefixes
- Avoid `process_data`, `handle_stuff`, `do_work` — too generic to be searchable or testable

### Classes

- Noun or noun phrase: `InvoicePrinter`, `UserRepository`, `PaymentGateway`
- Avoid `Manager`, `Helper`, `Util`, `Handler` as primary names — these are SRP violations waiting to happen
- Name should match the single responsibility: `InvoicePersistence` not `InvoiceStuff`

### Language-specific conventions (follow the project's existing style)

| Language | Variables/Functions | Classes |
|---|---|---|
| Python | `snake_case` | `PascalCase` |
| JavaScript/TypeScript | `camelCase` | `PascalCase` |
| Java | `camelCase` | `PascalCase` |
| Go | `camelCase` (exported: `PascalCase`) | `PascalCase` |

---

## Function Discipline

### Size

There is no universal line count limit, but the heuristic is: a function should fit on one screen without scrolling. When it does not, look for extraction opportunities.

**Trigger for extraction:** sections of a function that can be named with a verb phrase. If you're writing a comment like `# validate inputs` before a block, that block is a candidate to become `validate_inputs()`.

### Single Responsibility

A function should do one thing. Signal that it does multiple things:
- The name contains "and": `validate_and_save`, `fetch_and_format`
- The function has multiple levels of abstraction mixed together (high-level orchestration + low-level string manipulation in the same body)
- Testing requires setting up multiple unrelated concerns

**Fix pattern — extract nested conditionals:**
```python
# Before: logic buried inside a larger function
def calculate_product_discount(product_price):
    if product_price > 100:
        discount_rate = 0.1
    elif product_price > 50:
        discount_rate = 0.05
    else:
        discount_rate = 0
    return product_price - (product_price * discount_rate)

# After: discount rate logic is named, isolated, and reusable
def calculate_product_discount(product_price):
    discount_rate = get_discount_rate(product_price)
    return product_price - (product_price * discount_rate)

def get_discount_rate(product_price):
    if product_price > 100: return 0.1
    if product_price > 50: return 0.05
    return 0
```

### Parameter Count

- 0–2 parameters: ideal
- 3 parameters: acceptable, review whether they cluster into a concept
- 4+ parameters: strong signal to introduce a parameter object or restructure

**Anti-pattern:** `create_user(name, email, age, role, department, is_active)` — introduce `UserSpec` or `CreateUserRequest`.

### Levels of Abstraction

A function should operate at one level of abstraction. Mixing high-level orchestration with low-level mechanics forces readers to context-switch constantly.

```python
# Bad: mixes high-level flow with string manipulation detail
def process_order(order):
    user = db.query(f"SELECT * FROM users WHERE id = {order.user_id}")
    items = [i for i in order.items if i.stock > 0]
    send_email(user.email, "\n".join([f"{i.name}: {i.price}" for i in items]))

# Better: each call is at the same abstraction level
def process_order(order):
    user = fetch_user(order.user_id)
    available_items = filter_in_stock(order.items)
    notify_user(user, available_items)
```

---

## Cognitive Complexity

Cognitive complexity measures how hard code is to understand — not just how many branches it has (cyclomatic complexity), but how nested and non-linear the control flow is.

**Key contributors to cognitive complexity:**

| Construct | Impact |
|---|---|
| Each `if`/`else` | +1 per branch |
| Nesting depth | multiplied cost — 3-deep `if` inside `for` is much harder than sequential |
| `break`, `continue`, `goto` | disrupts linear reading |
| Recursive calls | requires holding a mental stack |
| Boolean expressions with 3+ conditions | compound logic is hard to test exhaustively |

**Mitigations:**

1. **Early return / guard clauses** — eliminate the `else` branch by returning early when a condition fails
   ```python
   # Instead of nested if/else:
   def process(user):
       if user is None: return None
       if not user.is_active: return None
       return compute(user)
   ```

2. **Extract condition into a named boolean function**: `if is_eligible_for_discount(user)` reads better than `if user.age > 65 and user.account_type == "premium" and not user.has_discount`

3. **Flatten loops** — if you have a loop inside a loop inside an if, consider whether the inner loop belongs in its own function

---

## Comment Discipline

### When to comment

Comments should explain **why**, not **what**. If the code clearly states what it does, a comment restating it is noise.

**Comment when:**
- The code does something non-obvious for a non-obvious reason (performance hack, workaround for external system behavior, regulatory requirement)
- There is a known edge case or gotcha a future reader should know before modifying
- The function has a non-trivial contract (preconditions, postconditions, exceptions)

**Do not comment when:**
- The function name already says it: `# This function groups users by id` before `group_users_by_id()` is redundant
- You're explaining what a standard algorithm does — if the reader doesn't know merge sort, that's a prerequisite problem, not a documentation problem
- You're tracking changes (`# Added by Alice, 2024-03-01`) — that's version control's job

### Docstrings / doc comments

Use for public APIs. Include: what the function does, parameters, return type, exceptions raised, non-obvious behavior warnings.

```python
def group_users_by_id(user_id: str) -> int:
    """Assign user to a processing category (1–9) based on their ID.

    Warning: IDs containing non-ASCII characters may not map correctly.
    See docs/user-categorization.md for supported formats.

    Args:
        user_id: The user's string identifier.

    Returns:
        Category number 1–9.

    Raises:
        ValueError: If user_id is empty or unsupported format.
    """
```

### Stale comment anti-pattern

A comment that describes what the code used to do (before a refactor) is worse than no comment — it actively misleads. When modifying code, always update or delete adjacent comments.

---

## Magic Numbers and Constants

**Definition:** A magic number is a numeric (or string) literal in code whose meaning is not self-evident.

**Rule:** Replace any literal whose purpose is not immediately obvious at the call site with a named constant.

```python
# Bad — reader must infer what 0.1 means
discount = price * 0.1

# Good — intent is explicit, single change point if rate changes
TEN_PERCENT_DISCOUNT = 0.1
discount = price * TEN_PERCENT_DISCOUNT
```

**Applies to:**
- Numeric literals (`0.1`, `86400`, `404`, `3`)
- String sentinels (`"admin"`, `"pending"`, `"USD"`)
- Array indices used as semantic positions (`data[2]` meaning "the third column")

**Where to define constants:**
- Module/file level for shared constants
- Class-level for class-specific constants
- Avoid defining them as function-local unless they are truly local to one function

---

## Code Smell Taxonomy

Code smells are patterns that indicate deeper problems. They are not bugs — the code may work — but they signal that a refactor is warranted.

### Structural smells

| Smell | Description | Fix |
|---|---|---|
| Long method | Function does too much; scrolls past one screen | Extract methods |
| Large class | Class has too many fields and methods | Split by responsibility (SRP) |
| Long parameter list | 4+ parameters to a function | Introduce parameter object |
| Duplicate code | Same logic in 2+ places | Extract to shared function (DRY) |
| Dead code | Unreachable code, unused variables/functions | Delete it |
| Feature envy | Method uses another class's data more than its own | Move method to that class |

### Complexity smells

| Smell | Description | Fix |
|---|---|---|
| Nested conditionals | 3+ levels of if/for nesting | Guard clauses, extract methods |
| Inconsistent abstraction | High and low-level logic mixed in one function | Separate abstraction levels |
| Boolean trap | `update(true, false, true)` — positional booleans | Named parameters or enum |
| Speculative generality | Abstractions with no current users | YAGNI — delete or defer |

### AI-specific smells (common in LLM-generated code)

- **Overly long methods:** LLMs optimize for function, not conciseness. Review generated functions > 20 lines.
- **Duplicated logic:** LLMs don't know the full codebase. Generated code often reimplements existing utilities.
- **Inconsistent naming:** LLM-generated code in an existing file may use different naming conventions than the file.
- **Redundant conditions:** `if x == True:`, `if len(list) > 0:` — LLMs produce defensive conditions that add noise.
- **Hardcoded secrets:** LLMs may include example API keys or credentials. Always scan generated code before committing.
- **Insecure dependencies:** LLMs may suggest packages with known CVEs. Verify all suggested libraries.

---

## Related pages

- [[patterns/principles]] — SOLID, DRY, YAGNI, KISS — the design principles behind these heuristics
- [[patterns/refactoring]] — Mechanics for moving from smell to clean code
- [[concepts/unit-testing]] — Function discipline and SRP make code testable; testability is a quality signal
- [[concepts/deep-modules]] — Ousterhout's framing: complexity hides behind narrow interfaces; function discipline is complementary
