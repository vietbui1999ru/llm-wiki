---
title: "API Design Patterns"
type: concept
tags: [patterns, software-engineering, api, rest, http]
sources:
  - "API design guide    Cloud API Design Guide.md"
  - "Google API Design Guide.md"
  - "General AIPs.md"
  - "RESTful web API Design best practices.md"
created: 2026-05-06
updated: 2026-05-06
---

# API Design Patterns

Reference for REST API design decisions. Covers resource naming, HTTP semantics, request/response conventions, errors, versioning, pagination, and long-running work. Drawn primarily from Google's API Design Guide (AIP series) and Google Cloud's RESTful best practices.

---

## Resource Naming

**Intent**: URLs identify nouns (resources), not verbs or actions. The URL is a stable address; behavior comes from the HTTP method.

**Rules:**
- Use plural nouns for collections: `/users`, `/orders`, `/books`
- Hierarchy via path segments: `/users/{userId}/orders/{orderId}`
- Collection IDs: plural, lowerCamelCase — `users`, `bookReviews`
- Resource IDs: server-assigned unless the client explicitly provides one at creation
- Avoid encoding verbs in the URL (`/getUser`, `/createOrder`)

**Hierarchy example:**
```
/projects/{project}/locations/{location}/instances/{instance}
```

**Custom actions** (when standard CRUD doesn't fit): use a colon suffix on the resource — `POST /orders/{id}:cancel`, `POST /documents/{id}:publish`. This is the AIP-136 pattern; it keeps the verb out of the base URL while signaling non-standard behavior.

**Anti-patterns:**
- Verb in URL: `POST /createUser` → use `POST /users`
- Flat namespace when hierarchy exists: `/userOrders` → `/users/{id}/orders`
- Inconsistent plurality: mixing `/user` and `/orders`

---

## HTTP Method Semantics

| Method | Intent | Idempotent | Safe |
|--------|--------|-----------|------|
| GET | Read resource or collection | Yes | Yes |
| POST | Create resource; non-idempotent actions | No | No |
| PUT | Full replacement of resource | Yes | No |
| PATCH | Partial update (field mask) | Yes* | No |
| DELETE | Remove resource | Yes | No |

*PATCH is idempotent only when you use field masks (same mask + same values = same result).

**GET**: must have no side effects. Never use GET to trigger state changes.

**POST**: use for creation (`POST /users`) and for custom actions that don't fit standard methods (`POST /jobs/{id}:cancel`).

**PUT vs PATCH**: prefer PATCH with a field mask for updates. Reserve PUT for full replacement (rare — clients must send the complete resource or risk losing fields they didn't include).

**DELETE**: should be idempotent — deleting an already-deleted resource should return 404 (or 200 with a tombstone for soft delete), not error. If deletion is async, return a long-running operation, not 200.

---

## Request/Response Design

### Field naming

- **JSON APIs**: `snake_case` is common (Python ecosystem, many REST APIs); Google's guide uses `lowerCamelCase` for JSON field names (Protobuf JSON mapping). Pick one and be consistent across all endpoints.
- Standard field names to reuse (AIP-148):
  - `name` — resource's full resource name
  - `display_name` — human-readable label
  - `create_time`, `update_time` — RFC 3339 timestamps
  - `labels` — user-defined key/value metadata map
  - `etag` — for optimistic concurrency
  - `page_token`, `next_page_token` — for pagination

### Partial responses (field masks)

When clients only need a subset of fields, accept a `fields` query param or a `read_mask` body field:

```
GET /users/123?fields=name,email,createdAt
```

Server returns only those fields. Reduces payload; avoids over-fetching. AIP-157.

For updates, use `update_mask` to specify which fields to change — everything else is untouched:

```json
PATCH /users/123
{
  "display_name": "Alice",
  "update_mask": "display_name"
}
```

Field masks are dot-notation paths: `"address.city"` updates only the nested city field.

### Output vs input fields

Mark server-computed fields clearly in docs (AIP-203): `create_time`, `uid`, `etag` are output-only. Clients must not send them on create/update; servers must ignore them if present.

---

## Error Response Shape

**Intent**: errors must be machine-parseable and human-readable without leaking internals.

**HTTP status code selection:**

| Code | When |
|------|------|
| 400 | Bad request — invalid input, missing required field |
| 401 | Unauthenticated — no valid credentials |
| 403 | Unauthorized — authenticated but not permitted |
| 404 | Resource not found |
| 409 | Conflict — concurrent write clash, duplicate create |
| 422 | Unprocessable — input parseable but semantically invalid |
| 429 | Rate limited |
| 500 | Internal server error |
| 503 | Service unavailable / overloaded |

**Never return 200 with an error body.** A 200 means the operation succeeded. Clients parse status first.

**Structured error body (AIP-193):**
```json
{
  "error": {
    "code": 404,
    "status": "NOT_FOUND",
    "message": "User 'users/456' not found.",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.BadRequest",
        "field_violations": [
          { "field": "email", "description": "Must be a valid email address." }
        ]
      }
    ]
  }
}
```

Fields:
- `code` — HTTP status integer
- `status` — canonical error name (string enum: `NOT_FOUND`, `INVALID_ARGUMENT`, `ALREADY_EXISTS`, etc.)
- `message` — human-readable, actionable, no stack traces or internal IDs
- `details` — typed error extensions (field violations, retry info, quota info)

**Anti-patterns:**
- Returning stack traces in `message`
- Using `error: "something went wrong"` with no detail
- Returning 500 for all errors, including client errors
- Inconsistent shapes across endpoints

See [[patterns/error-handling]] for language-level error handling patterns.

---

## Versioning Strategies

**Two main approaches:**

### URL versioning
```
/v1/users
/v2/users
```
Pros: explicit, easy to route, cacheable, visible in logs.
Cons: duplication when only some resources change; clients must update all base URLs.

**Google's recommendation**: major version in URL path (`/v1/`). Minor changes are additive and non-breaking — no version bump needed.

### Header versioning
```
Accept: application/vnd.api+json;version=2
API-Version: 2024-01-01
```
Pros: URL stays clean; date-based versioning avoids ambiguous "what's in v2".
Cons: harder to test (can't paste URL into browser), not cache-friendly, harder to route at the proxy layer.

**Tradeoff summary:**
- Greenfield public API, wide audience → URL versioning (simpler for consumers)
- Internal API or tight client control → header versioning viable
- Date-based header versioning (Stripe pattern) works well when you want a continuous changelog rather than discrete versions

**Breaking vs non-breaking changes (AIP-180):**

Non-breaking (no version bump needed):
- Adding a new field to a response
- Adding a new optional request parameter
- Adding a new enum value (with caution — clients must handle unknown values)
- Adding a new resource or method

Breaking (require version bump):
- Renaming or removing a field
- Changing a field's type
- Changing URL structure
- Changing error codes or error shape
- Removing an endpoint

---

## Pagination

### Cursor-based (preferred)

```json
GET /users?page_token=<opaque_cursor>&page_size=50

{
  "users": [...],
  "next_page_token": "abc123",
  "total_size": 1200
}
```

- `next_page_token` is opaque to the client (server encodes position internally)
- Absent or empty `next_page_token` means last page
- Stable across concurrent writes — cursor points to a position, not an offset
- Required for real-time or high-churn datasets

### Offset-based

```
GET /users?offset=100&limit=50
```

- Simple to implement and reason about
- Breaks on concurrent inserts/deletes (items can appear twice or be skipped)
- Acceptable for static or low-churn data; avoid for feeds or event streams

**Response envelope shape** (AIP-158):
- Collection field named after the resource: `"users": [...]` not `"data": [...]`
- `next_page_token` for continuation
- Optional `total_size` (integer) when cheap to compute — omit if it requires a COUNT(*) that kills performance

**Anti-patterns:**
- Returning all results with no pagination on unbounded collections
- Using page numbers (`page=3`) — fragile under insertion
- `data` as the collection key — not self-documenting

---

## Idempotency Keys

**Intent**: allow clients to safely retry POST (create) requests without creating duplicate resources.

**Pattern:**
```
POST /orders
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000

{ "item": "book", "quantity": 1 }
```

Server behavior:
1. Check if key was seen before.
2. If yes: return the original response (same status + body), do not re-execute.
3. If no: execute and store result keyed by idempotency key.
4. Key expiry: typically 24h–7d.

**Design rules:**
- Key is client-generated (UUID recommended)
- Scope key to the authenticated user to prevent cross-user replay
- Return `409 Conflict` if the same key is used with a different request body
- Store results durably (DB, not in-memory cache)

**When required**: any POST that creates a resource or triggers a side effect (payment, email send, job dispatch). See [[systems/distributed-systems]] for idempotency in distributed contexts.

---

## Long-Running Operations

When an operation cannot complete within a single HTTP round-trip (~30s), choose a strategy:

### Polling (LRO pattern — AIP-151)

```
POST /exports → 202 Accepted
{
  "name": "operations/export-abc123",
  "done": false
}

GET /operations/export-abc123 → 200
{
  "name": "operations/export-abc123",
  "done": true,
  "response": { ... }
}
```

- Initial POST returns an operation resource immediately
- Client polls `GET /operations/{id}` until `done: true`
- On failure: `done: true` + `error` field instead of `response`
- Include `metadata` for progress info (percent complete, ETA)
- Support `DELETE /operations/{id}` to cancel (`:cancel` custom method preferred per AIP-136)

### Webhooks / callbacks

- Client registers a callback URL at subscription time
- Server POSTs result to the URL when done
- Requires the client to have a publicly reachable endpoint
- Better for fire-and-forget; worse for request/response flow

### Server-sent events / streaming

- Client holds an HTTP connection open; server pushes events as they arrive
- Best for real-time feeds (logs, metrics, chat)
- Not suitable for one-off async operations

**Guidance**: default to polling LRO for async operations. Add webhooks only when clients have a documented need for push notifications.

---

## API Design Anti-Patterns

| Anti-pattern | Problem | Fix |
|---|---|---|
| Chatty API | Multiple round-trips for one logical operation; battery/latency drain on mobile | Offer composite "experience" endpoints for common workflows; or batch endpoints |
| Verb in URL | `/getUser`, `/deleteOrder` | Use noun URL + correct HTTP method |
| 200 on error | Clients must parse body to detect failure; breaks standard tooling | Return the correct 4xx/5xx status |
| Breaking changes without version bump | Existing clients silently break | Treat field removal/rename as breaking; bump major version or add new field alongside old one |
| Flat response with cryptic keys | `{"id-a": {"data": [...]}}` — human-unreadable | Named fields that match the resource: `{"orders": [...]}` |
| Unbounded collections | `GET /events` returns 10M records | Always paginate; enforce `max_page_size` server-side |
| Inconsistent naming | Mix of `snake_case`/`camelCase`/`PascalCase` across endpoints | Enforce one convention via linter or schema |
| Inside-out design | API shape mirrors internal DB schema, not consumer workflows | Design from consumer use cases outward |

---

## Cross-References

- [[patterns/error-handling]] — language-level error propagation and wrapping
- [[patterns/principles]] — SRP (single endpoint responsibility), ISP (client-specific interfaces)
- [[systems/distributed-systems]] — idempotency, consistency guarantees, retry semantics
- [[systems/system-design-process]] — where API design fits in the overall system design flow
