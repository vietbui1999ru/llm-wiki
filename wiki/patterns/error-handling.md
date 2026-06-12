---
title: "Error Handling Patterns"
type: pattern
tags: [patterns, software-engineering, error-handling, reliability]
sources:
  - "Best practices for exceptions.md"
  - "Error handling patterns.md"
  - "General error handling rules    Technical Writing.md"
created: 2026-05-06
updated: 2026-05-06
---

# Error Handling Patterns

Reference for both developers writing code and agents implementing features. Covers the full lifecycle: classification → representation → propagation → retry → observability.

## Agent Trigger

**Apply when:** Writing try/catch blocks, defining error types, retry logic, or reviewing error paths.
**Rule of thumb:** Fail fast, type your errors, never silently swallow; use Result types or exceptions consistently; backoff with jitter on retries.

---

## Error Taxonomy

Understanding what kind of error you have determines how you handle it.

### Expected vs. Unexpected

| Type | Definition | Example |
|---|---|---|
| **Expected** | Normal failure modes the domain anticipates | User not found, validation failure, rate limit hit |
| **Unexpected** | Bugs, invariant violations, infrastructure failures | NullPointerException, DB connection lost, OOM |

Expected errors belong in the return type (Result/Either or checked value). Unexpected errors surface as exceptions or panics and propagate to a global handler.

### Recoverable vs. Fatal

- **Recoverable**: caller can retry, fallback, or inform the user and continue
- **Fatal**: system cannot safely continue; crash or escalate immediately

A crashed app is more diagnosable than an app with undefined behavior from a swallowed error.

### Business Errors vs. Technical Errors

- **Business errors**: domain rule violations — surface to users with actionable messages ("Insufficient balance")
- **Technical errors**: infrastructure or code failures — log internally, surface generic message to users

Never leak stack traces, internal paths, or system details to end users.

---

## Fail-Fast Principle

Validate at the earliest possible point. Every validation deferred is a debugging cost multiplied.

**Rules:**
- Validate arguments before entering async or side-effecting logic
- Raise errors immediately upon detection — not after partially completing work
- In task-returning methods (async), throw argument exceptions synchronously before the async portion begins

```typescript
// Bad: validation buried inside async body
async function processOrder(orderId: string) {
  const result = await db.query(orderId); // orderId could be null
  if (!orderId) throw new Error("...");   // too late, query already ran
}

// Good: validate synchronously first
async function processOrder(orderId: string) {
  if (!orderId) throw new ArgumentError("orderId is required");
  return db.query(orderId);
}
```

---

## Exception Best Practices

### When to Use Exceptions

Use exceptions for **truly exceptional** conditions — events that are rare, unexpected, or represent violations of invariants. For conditions that occur routinely as part of normal flow, use conditional checks or Result types instead.

```csharp
// Prefer: check state before calling
if (conn.State != ConnectionState.Closed) conn.Close();

// Over: catch predictable failures
try { conn.Close(); }
catch (InvalidOperationException) { ... }
```

### Exception Hierarchy Design

- Derive custom exceptions from the appropriate base class, not always from the root `Exception`
- Name exception classes with the `Exception` suffix
- Include three constructors: `()`, `(message)`, `(message, innerException)`
- Add structured properties only when callers need them programmatically (not just for messages)
- Prefer predefined exception types over custom ones where they fit precisely

### What to Include in Exception Messages

- Root cause, not a generic label ("Server error" is insufficient)
- What went wrong, where, and ideally what the caller can do
- Proper grammar and ending punctuation
- No PII, no internal paths, no stack trace content in the message string itself

```python
# Bad
raise Exception("Error")

# Good
raise ValueError(f"User ID '{user_id}' not found in database 'users'.")
```

### Never Swallow Silently

```python
# Anti-pattern: silence all errors
try:
    process()
except Exception:
    pass  # no log, no rethrow — problem disappears

# Correct: at minimum log, then decide
try:
    process()
except Exception as e:
    logger.error("process() failed", exc_info=e)
    raise  # or handle intentionally
```

---

## Railway-Oriented Programming / Result Types

The `Result<Ok, Err>` pattern (Rust, Haskell Either, Kotlin Arrow, TypeScript fp-ts) makes error handling explicit and type-safe. The compiler enforces handling — unlike exceptions, which are invisible in signatures.

```rust
fn parse_user_id(s: &str) -> Result<UserId, ParseError> {
    s.parse::<u64>()
        .map(UserId)
        .map_err(|e| ParseError::InvalidFormat(e.to_string()))
}

// Propagate with ?
fn load_user(s: &str) -> Result<User, AppError> {
    let id = parse_user_id(s)?;   // returns Err early if parse fails
    let user = db.find(id)?;
    Ok(user)
}
```

**Chaining / composition:**
```typescript
// TypeScript with fp-ts or similar
const result = pipe(
  parseUserId(raw),
  flatMap(id => findUser(id)),
  map(user => user.profile),
);
```

### When to Use Result vs. Exceptions

| Situation | Use |
|---|---|
| Expected failure in a domain operation | Result / Either |
| Programming error / invariant violation | Exception / panic |
| Language forces exceptions (Java, Python) | Exceptions + careful hierarchy |
| Cross-boundary serialization needed | Result (serialize to structured error) |
| Hot path, allocation-sensitive | Result (no stack unwind overhead) |

---

## Error Propagation

### Let It Propagate

Default stance: if you cannot handle the error meaningfully at the current layer, let it propagate. Do not catch just to re-throw the same exception without adding context.

### Catch-and-Rethrow: Add Context

When catching, wrap with additional context about what operation failed. Preserve the original as `cause` / `innerException`.

```python
# Bad: swallows original cause
except Exception:
    raise RuntimeError("Something failed")

# Good: wraps with context, chains original
except Exception as e:
    raise ServiceError(f"Failed to load user {user_id}") from e
```

### Preserve Stack Traces

In C#, use bare `throw` (not `throw e`) inside a catch block to preserve the original stack trace. When rethrowing outside the catch block, use `ExceptionDispatchInfo.Capture` / `.Throw()`.

### Rollback on Partial Mutation

If a method performs multiple side effects and one fails, undo completed steps. Callers must be able to assume no side effects when an exception escapes.

```csharp
var txId = account.Withdraw(amount);
try {
    destination.Deposit(amount);
} catch {
    account.RollbackTransaction(txId);
    throw;  // preserve stack trace
}
```

---

## Retry and Backoff

### What Errors Warrant Retry

Retry only **transient** errors: network timeouts, rate limits, temporary unavailability. Do not retry:
- Validation errors (will always fail)
- Authentication failures (credentials wrong, not transient)
- Business rule violations

### Exponential Backoff with Jitter

```python
import random, time

def retry_with_backoff(fn, max_attempts=5, base_delay=0.5):
    for attempt in range(max_attempts):
        try:
            return fn()
        except TransientError as e:
            if attempt == max_attempts - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.1)
            time.sleep(delay)
```

**Jitter** prevents thundering herd when many callers retry simultaneously.

### Retry Budget

Cap total attempts and total elapsed time. See [[concepts/error-budget]] for the agentic adaptation of this pattern (retry/token/runtime/session budgets).

For self-healing loops: [[concepts/self-healing-loop]] covers the failure→retry→rollback→escalation sequence.

---

## Error Response Design (APIs)

See [[patterns/api-design]] for full REST conventions. Summary for error responses:

### Structured Error Body

```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "No user with ID 'abc123' exists.",
    "details": { "userId": "abc123" },
    "requestId": "req_xyz"
  }
}
```

### HTTP Status + Error Code

HTTP status gives coarse classification. A machine-readable `code` string provides specific identity.

| Category | HTTP Status Range |
|---|---|
| Client input errors | 4xx |
| Server / infra errors | 5xx |
| Auth failures | 401 / 403 |
| Not found | 404 |
| Rate limit | 429 |

Never return 200 with an error body — clients cannot distinguish success from failure without reading the body.

### User-Facing vs. Developer Messages

- `message`: safe to display to end users — no internals, no paths
- `details` / `debug`: developer context, strip in production or gate behind auth
- Never expose stack traces, SQL, or internal service names in API responses

---

## Logging Discipline

### What to Log

- Log at **ERROR**: unhandled exceptions, data loss scenarios, external service failures
- Log at **WARN**: degraded operation, retries, approaching limits, unexpected-but-handled states
- Log at **INFO**: significant lifecycle events (server start, job complete, user auth)
- Log at **DEBUG**: request details, intermediate state — only in development

### Avoid Logging PII

Never log passwords, tokens, email addresses, SSNs, payment data. Mask or omit before logging.

### Log Error Codes

Assign numeric or string codes to known error categories. Document them. Codes allow support teams to grep logs and correlate errors without reading prose.

### Log Once at the Boundary

Log at the point where the error is handled or escalated — not at every layer it passes through. Multiple log entries for the same error create noise and inflate storage.

---

## Anti-Patterns

| Anti-pattern | Problem | Fix |
|---|---|---|
| **Swallowing exceptions** | Error disappears, undefined behavior persists | Log + rethrow, or handle explicitly |
| **Returning null on error** | Callers must check everywhere; NPE far from origin | Return Result/Option or throw with context |
| **Magic error numbers** | `if (code == -7)` is unreadable and unmaintainable | Named constants or typed error codes |
| **Logging and rethrowing** | Creates duplicate log entries for one error | Log once, at the boundary where you handle |
| **Generic messages** | "Server error" — useless for diagnosis | Name the operation, the input, the constraint violated |
| **Raising in `finally`** | Replaces original exception, destroys root cause | Never throw from `finally`; only cleanup |
| **Throw from unexpected places** | Equals, GetHashCode, static constructors | Reserve exceptions for fallible operations |
| **Catching base Exception broadly** | Masks bugs, catches cancellation, prevents escalation | Catch specific types; let unexpected bubble |

---

## Cross-References

- [[patterns/api-design]] — error response shape, HTTP status conventions
- [[patterns/principles]] — fail-fast and single-responsibility apply to error handling design
- [[concepts/self-healing-loop]] — failure→retry→rollback→escalation harness pattern
- [[concepts/error-budget]] — retry/token/runtime/session budgets for agentic loops
