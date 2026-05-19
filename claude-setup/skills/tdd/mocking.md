# When to Mock

Mock at **system boundaries** only:
- External APIs (payment, email, etc.)
- Databases (sometimes — prefer test DB)
- Time/randomness
- File system (sometimes)

Don't mock:
- Your own classes/modules
- Internal collaborators
- Anything you control

## Designing for Mockability

**1. Use dependency injection**

Pass external dependencies in rather than creating them internally:

```typescript
// Easy to mock
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// Hard to mock
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

**2. Prefer SDK-style interfaces over generic fetchers**

```typescript
// GOOD: Each function is independently mockable
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// BAD: Mocking requires conditional logic inside the mock
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

## Anti-Patterns

### 1. Testing Mock Behavior

```typescript
// ❌ BAD: Testing that the mock exists
expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();

// ✅ GOOD: Test real behavior
expect(screen.getByRole('navigation')).toBeInTheDocument();
```

Gate: "Am I testing real component behavior or mock existence?" If mock existence → delete the assertion.

### 2. Test-Only Methods in Production

Never add methods to production classes that are only called from tests. Move cleanup/setup to test utilities.

Gate: "Is this method only called in test files?" If yes → don't add it to the production class.

### 3. Mocking Without Understanding

Don't mock a method before understanding its side effects. If the test depends on a side effect (e.g., config written to disk), mocking that method silently breaks the test.

Gate: Before mocking — list the real method's side effects. Check if the test depends on any of them. If yes, mock at a lower level.

### 4. Incomplete Mocks

Mock the **complete** data structure as it exists in reality, not just fields your immediate test uses. Partial mocks hide structural assumptions and produce false confidence.

Gate: Check the real API response shape. Include all fields the system might consume downstream.

### 5. Tests as Afterthought

Testing is part of implementation, not optional follow-up. You cannot claim a feature is complete without tests. TDD prevents this structurally — write the test first.

## Red Flags

- Assertion checks for `*-mock` test IDs
- Methods only called in test files
- Mock setup is >50% of test
- "I'll mock this to be safe" (mock without understanding)
- Partial mock object missing documented fields
