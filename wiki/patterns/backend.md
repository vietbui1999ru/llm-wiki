---
title: "Backend Patterns"
type: pattern
tags: [backend, patterns, middleware, authentication, service-layer, repository, dependency-injection, queue, api-gateway]
sources: ["Design Patterns for Modern Backend Development – with Example Use Cases.md", "Design Patterns for Modern Backend Development.md"]
created: 2026-05-06
updated: 2026-05-06
---

# Backend Patterns

Structural and behavioral patterns for server-side systems. Covers how HTTP requests flow through a server, how business logic is organized, and how external dependencies are managed. Focus is on decision criteria and anti-patterns — not just definitions.

## Agent Trigger

**Apply when:** Writing or reviewing server-side middleware, auth, service/repository layers, queues/workers, or API gateways.
**Rule of thumb:** Enforce auth at the right layer, keep service logic out of controllers, design queues for at-least-once + DLQ.

---

## Middleware Chains

Middleware is a function that sits in the request/response pipeline and either handles a concern or passes control to the next middleware.

```
Request → [Logger] → [Auth] → [RateLimit] → [Validator] → [Handler] → Response
```

**Composition order matters**:
- **Logger first**: captures all requests before any early exit
- **Auth before business logic**: reject unauthenticated requests early — saves computation
- **Rate limiter before auth**: prevents auth endpoint abuse without touching the identity system
- **Validator just before the handler**: auth is confirmed, now check the request shape
- **Error middleware last** (Express/Node convention): catches errors bubbled from all prior middleware

**Short-circuit pattern**: middleware should return early on failure — never call `next()` after sending a response. Calling `next()` after a response causes double-response bugs.

**Error middleware signature** (Express): takes `(err, req, res, next)` — four arguments. The framework uses the arity to distinguish it from normal middleware. Place it after all routes.

**Anti-patterns**:
- Business logic inside middleware — middleware handles cross-cutting concerns only (auth, logging, rate-limiting, parsing)
- Deeply nested middleware sharing mutable state via the request object — use typed context instead
- Auth middleware that silently passes on failure instead of returning 401/403

---

## Authentication and Authorization

Two distinct concerns often conflated:
- **Authentication (authn)**: who are you? (verify identity)
- **Authorization (authz)**: are you allowed? (verify permission)

### JWT vs Session Tokens

| | JWT | Session token |
|---|---|---|
| State | Stateless — claims embedded in token | Stateful — server holds session store |
| Revocation | Hard — must wait for expiry or maintain a denylist | Easy — delete session from store |
| Scalability | Better for horizontally scaled services | Requires shared session store (Redis) across instances |
| Token size | Larger (base64 payload) | Small opaque string |
| Best for | Service-to-service, mobile clients, multi-service auth | Traditional web sessions, high-security contexts needing instant revocation |

**JWT placement**: `Authorization: Bearer <token>` header, not a cookie (avoids CSRF). Access tokens short-lived (15m–1h), refresh tokens long-lived (days–weeks) stored securely server-side or in `HttpOnly` cookie.

### OAuth2 Flows

- **Authorization Code + PKCE**: web apps and mobile apps authenticating on behalf of a user. Redirect-based; PKCE required for public clients.
- **Client Credentials**: service-to-service (no user involved). Backend calls another backend with `client_id` + `client_secret`.
- **Device Code**: TV/CLI flows where user opens a browser separately.
- Never use the **Implicit flow** — deprecated; leaks tokens in URL fragments.

### RBAC vs ABAC

**RBAC (Role-Based Access Control)**:
- User has roles; roles have permissions
- Simple to implement, easy to audit
- Fails when permissions need context: `user can edit their own posts but not others'`

**ABAC (Attribute-Based Access Control)**:
- Decision based on attributes: subject attrs + resource attrs + environment attrs
- Expressive: `user.department == resource.department AND time < 18:00`
- Complex to implement and audit
- Use when RBAC requires an explosion of roles to represent contextual rules

**Where to enforce**:
- **Authentication**: middleware layer (verify token, attach identity to request context)
- **Coarse-grained authorization** (role check): middleware or route-level guard
- **Fine-grained authorization** (resource ownership, ABAC): service layer, not the handler. The handler doesn't know enough about the domain to make the call correctly.

---

## Service Layer Pattern

Separates HTTP concerns (parsing, serialization, status codes) from business logic.

```
HTTP Handler → Service → Repository
    ↑ thin           ↑ owns logic    ↑ owns data access
```

**Handler responsibility**: parse request, call service, map result to HTTP response. Nothing more.

**Service responsibility**: orchestrate business operations, enforce invariants, call repositories, emit domain events. Does not know about HTTP.

**Why thin controllers matter**:
- Business logic in handlers cannot be tested without standing up an HTTP stack
- Logic duplicated across multiple routes (REST + GraphQL + CLI) if it lives in handlers
- Mixed concerns make it impossible to change HTTP framework without rewriting logic

**Dependency injection into services**: services receive their dependencies (repositories, other services, event emitters) via constructor. Never construct dependencies inside the service.

```typescript
class OrderService {
  constructor(
    private readonly orders: OrderRepository,
    private readonly inventory: InventoryService,
    private readonly events: EventEmitter,
  ) {}

  async placeOrder(userId: string, items: LineItem[]): Promise<Order> {
    await this.inventory.reserve(items);        // domain logic
    const order = await this.orders.create(userId, items);
    this.events.emit('order.placed', order);
    return order;
  }
}
```

---

## Repository Pattern

Abstracts data access behind an interface. The rest of the application talks to the repository interface, not to the database driver.

```typescript
interface OrderRepository {
  findById(id: string): Promise<Order | null>;
  create(userId: string, items: LineItem[]): Promise<Order>;
  update(id: string, patch: Partial<Order>): Promise<Order>;
}

// Concrete implementation injected at runtime
class PostgresOrderRepository implements OrderRepository { ... }
// Test double injected in tests
class InMemoryOrderRepository implements OrderRepository { ... }
```

**Testability benefit**: swap the real database with an in-memory fake in unit tests — no test database required, tests run at millisecond speed.

**When not to use it**:
- Simple CRUD with no domain logic — the abstraction adds ceremony for no gain
- When you need database-specific features (complex CTEs, COPY, full-text search) that don't map cleanly to a generic interface — wrap those queries in a specialized query object instead, or expose them explicitly

**Anti-pattern**: repositories that return raw database rows instead of domain objects. The repository's job is to return domain types, not DB result sets.

---

## Queue / Worker Patterns

Offload work that doesn't need to complete within the HTTP request cycle.

```
HTTP Handler → enqueue(job) → Queue → Worker → side effects
      ↑ returns 202 Accepted immediately
```

### At-Least-Once Delivery

Most queues (SQS, RabbitMQ, Kafka) guarantee at-least-once delivery — the same message may be delivered more than once (due to network errors, retries, or crashes before acknowledgment).

**Idempotent consumers**: design workers so that processing the same message twice produces the same result as processing it once. Common techniques:
- Deduplicate using a message ID stored in the database (insert-if-not-exists before processing)
- Use idempotency keys for external API calls
- Make operations naturally idempotent: `SET status = 'shipped'` rather than `increment shipment_count`

### Dead-Letter Queues (DLQ)

Messages that fail repeatedly (after N retries) move to a DLQ instead of being dropped. A DLQ is the operational safety net — inspect failed messages, fix the bug, then replay.

Always configure a DLQ. Without one, poison messages (malformed or unprocessable) block the queue or silently disappear.

### Task Queue vs Event Stream

| | Task queue (SQS, Celery, BullMQ) | Event stream (Kafka, Kinesis) |
|---|---|---|
| Delivery | One consumer per message | Multiple consumer groups, each gets all messages |
| Ordering | Best-effort | Ordered within partition |
| Replay | DLQ only | Replay from offset |
| Use for | Job execution, background work | Event sourcing, fan-out, audit trails |

---

## Dependency Injection

Pass dependencies in rather than constructing them inside a component. Decouples components from their concrete implementations.

**Three forms**:
- **Constructor injection** (preferred): dependencies declared in constructor signature. Mandatory, visible, testable.
- **Property injection**: set via public property after construction. Allows partial construction — harder to reason about.
- **Method injection**: pass dependency at call time. Use only when the dependency varies per-call.

**Container-based DI**: frameworks (NestJS, Spring, .NET DI) manage object graphs automatically. Useful at scale. For smaller services, manual constructor injection is often clearer.

**Service Locator anti-pattern**: a global registry from which any code can pull dependencies. Hides dependencies, makes call graphs opaque, and makes testing harder because you must configure the global registry before each test.

```typescript
// Anti-pattern — service locator
const db = ServiceLocator.get('database');

// Preferred — constructor injection
class UserService {
  constructor(private readonly db: DatabaseConnection) {}
}
```

---

## API Gateway Pattern

A single entry point in front of multiple backend services (common in microservices).

**Functions at the gateway**:
- **Request routing**: route `/orders/*` to order service, `/users/*` to user service
- **Auth at the edge**: verify JWTs once at the gateway; forward verified identity (e.g., `X-User-Id` header) to services — services trust the gateway, not raw clients
- **Rate limiting**: enforce per-client or per-IP limits globally without duplicating logic in every service
- **Aggregation**: compose multiple service calls into a single response (BFF variant)
- **Protocol translation**: REST → gRPC, WebSocket upgrade

**When to push auth into services**: when services are called by other services directly (service-to-service) or when the gateway trust model is insufficient for the security requirement.

**Single point of failure risk**: the gateway must be highly available. Deploy multiple instances behind a load balancer. Don't put business logic in the gateway — it should remain a routing/policy layer.

See also: [[systems/scalability-reliability]] for rate limiting algorithm selection (token bucket vs leaky bucket).

---

## Backend Anti-Patterns

### Fat Controllers

Controllers that contain business logic, data access, and HTTP handling all in one function. Symptoms: handlers over 50 lines, direct `db.query()` calls inside route handlers, duplicated logic across routes.

Fix: extract a service layer; move DB access to a repository.

### Direct DB Calls from Handlers

```typescript
// Anti-pattern
app.get('/users/:id', async (req, res) => {
  const row = await db.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
  res.json(row);
});
```

Bypasses the service layer (no domain logic, no authorization check), directly couples the route to the DB schema, and cannot be tested without a real database.

### Synchronous Chains That Should Be Async

Sending an email, resizing an image, or calling a slow third-party API inside the HTTP request cycle. Each adds latency and holds a connection open.

Rule of thumb: if the user doesn't need the result to continue, it belongs in a queue.

### Missing Input Validation

Never trust request data. Validate at the boundary — before it reaches the service layer. Unvalidated input causes type errors deep in domain code, is a primary injection vector, and produces confusing 500s instead of 400s.

Use a schema library (Zod, Joi, class-validator) at the handler layer. The service layer should receive clean, typed data — not raw request bodies.

### Anemic Service Layer

Services that are just pass-throughs to repositories with no logic. Usually a symptom of putting logic back in handlers or fat repositories. Domain invariants (business rules) belong in the service, not scattered across callers.

---

## Cross-references

- [[patterns/api-design]] — RESTful resource design, error response shape, versioning, idempotency keys
- [[patterns/principles]] — SOLID underpins DI (Dependency Inversion), SRP (thin controllers), OCP (repository interface)
- [[systems/distributed-systems]] — idempotency, saga, circuit breaker — required when workers call external services
- [[systems/architectural-patterns]] — hexagonal architecture is the generalization of the service layer / repository boundary
- [[patterns/database]] — repository implementations: N+1, connection pooling, query optimization
- [[patterns/error-handling]] — error taxonomy, retry/backoff for queue workers
