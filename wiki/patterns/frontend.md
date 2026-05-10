---
title: "Frontend Patterns"
type: concept
tags: [patterns, frontend, react, software-engineering]
sources:
  - "Design Patterns for React Interviews.md"
  - "Persson Dennis - 21 Fantastic React Design Patterns and When to Use Them.md"
created: 2026-05-06
updated: 2026-05-06
---

# Frontend Patterns

Reference and agent guide for React component patterns, state strategy, rendering modes, performance techniques, and CSS architecture.

---

## Component Composition Patterns

### Custom Hooks

**Intent:** Extract stateful logic from components into reusable functions.

**When to use:** Any time a component has non-trivial `useEffect` / `useState` logic; when the same logic appears in multiple components.

**When NOT to use:** Simple, one-off UI state (a toggle open/closed) that won't be reused — inline it.

**Anti-patterns:** Keeping all `useState` / `useEffect` inside the component body; making hooks that do too many unrelated things (violates SRP).

```js
// prefer this
const { posts, loading, error } = usePosts()
// over inlining all fetch logic in the component
```

Hooks are the default modern replacement for HOC and render props. Reach for them first.

---

### Container / Presentational

**Intent:** Separate data-fetching / business logic (container) from rendering (presentational).

**When to use:** When a UI component needs to be reusable across different data sources; when you want to test UI independently of network behavior.

**When NOT to use:** Tiny, one-use components where the extra file adds no value.

**Pattern:**
- Container: calls hooks, handles navigation, passes data as props
- Presentational: receives props, renders, no network calls, minimal state

**Anti-patterns:** Fetching data inside a presentational component; putting JSX in a container beyond a single wrapper element.

---

### Compound Components

**Intent:** Allow a group of components to share implicit state and work as a single logical unit, without prop drilling.

**When to use:** Complex UI widgets (modals, tabs, accordions, dropdowns) where consumers need to customize sub-parts without knowing internal state.

**When NOT to use:** Simple components; situations where a plain props interface is sufficient.

```jsx
// consumer controls layout; parent manages shared state
<Modal isOpen={isOpen}>
  <Modal.Header>Title</Modal.Header>
  <Modal.Body>Content</Modal.Body>
  <Modal.Footer>...</Modal.Footer>
</Modal>
```

**Anti-patterns:** Using compound components for simple buttons or inputs; over-nesting when a flat prop API would be clearer.

---

### Headless Components

**Intent:** Provide behavior and accessibility logic with zero styling opinion. Consumer owns all markup and CSS.

**When to use:** Building a component library or design system; when you need complex keyboard/ARIA behavior but full style control (e.g., Radix UI, Ark UI pattern).

**When NOT to use:** Simple utility components; one-off UI where you're not reusing the logic elsewhere.

**Anti-patterns:** Using headless pattern for a button; adding opinionated classNames inside a headless hook.

---

### Higher-Order Components (HOC)

**Intent:** Wrap a component to inject props or add behavior (auth guard, logging, feature flags).

**When to use:** Legacy class-component codebases; cross-cutting concerns that can't use hooks (e.g., third-party lib that doesn't accept hooks).

**When NOT to use:** Modern functional components — use a custom hook instead.

**Anti-patterns:** Wrapper hell (HOC stacking); prop name collisions; using HOC when a hook would be simpler.

---

### Render Props

**Intent:** Pass a function-as-prop so the parent controls what gets rendered with data the child provides.

**When to use:** When a consumer needs full rendering control over what a logic-provider renders; headless pattern without hooks.

**When NOT to use:** Modern code — prefer custom hooks; compound components handle the common "share state across children" case better.

---

### Provider / Context Pattern

**Intent:** Share data across a component subtree without prop drilling. Implemented via React Context.

**When to use:** App-wide configuration that rarely changes: theme, i18n, auth session, feature flags.

**When NOT to use:** High-frequency state updates (causes unnecessary re-renders across all consumers); general-purpose dependency injection.

**Anti-patterns:** Using Context as a state manager; wrapping the entire app in 10 nested providers.

> For global mutable state, use Zustand, Jotai, or Redux — not Context.

---

### Control Props (Controlled vs. Uncontrolled)

**Intent:** Let the parent own a component's state (controlled) or let the component manage itself (uncontrolled).

**When to use (controlled):** Forms where you need to read or reset field values programmatically; when parent needs to gate submission or trigger field changes.

**When to use (uncontrolled):** Simple, self-contained inputs where parent doesn't need to inspect or mutate the value.

**Anti-patterns:** Mixing controlled and uncontrolled in the same component without clear handling; forgetting to pass `onChange` to a controlled input (read-only field bug).

---

### Error Boundaries

**Intent:** Catch render-phase errors in a component subtree and display a fallback instead of crashing the whole app.

**When to use:** Wrap independent feature areas (dashboard, chat panel, data table) so a bug in one doesn't kill the whole page.

**When NOT to use:** Error boundaries do NOT catch errors in event handlers, async code (setTimeout, promises), or SSR — use try/catch there.

**Note:** Still requires a class component (as of React 18); use `react-error-boundary` library to get a hook-friendly wrapper.

---

### Portal Pattern

**Intent:** Render a child into a DOM node outside the parent's DOM hierarchy.

**When to use:** Modals, tooltips, dropdowns, context menus that need to escape `overflow: hidden` or z-index stacking contexts.

**When NOT to use:** Regular in-flow content; don't reach for portals just to avoid fixing CSS.

---

### Atomic Design

**Intent:** Organize components into a hierarchy: atoms → molecules → organisms → templates → pages.

**When to use:** Design systems with many teams; apps that need strict consistency across many views.

**When NOT to use:** Small apps; teams that don't have a shared design system to enforce.

---

## State Management Strategy

| State scope | Tool | When |
|---|---|---|
| Local UI state | `useState` | Toggle open/close, controlled input value |
| Derived state | Computed inline or `useMemo` | Value computable from existing state |
| Lifted state | Lift to nearest common ancestor | Two siblings need shared state |
| Server state | TanStack Query / SWR | Fetched data with caching, refetch, loading/error states |
| Global client state | Zustand / Jotai / Redux | Auth session, cart, user preferences shared across many components |
| Cross-subtree config | React Context | Theme, i18n, feature flags (low-update-frequency only) |

**Decision rule:** Use the narrowest scope that satisfies the requirement. Local → lifted → global. Do not reach for Redux for state used in one component.

---

## Rendering Strategies (Next.js / framework-level)

| Strategy | Acronym | When to use |
|---|---|---|
| Client-Side Rendering | CSR | Highly interactive dashboards; data personalized per user; behind auth |
| Server-Side Rendering | SSR | SEO-critical pages with frequently-changing data; personalized pages that need fresh data per request |
| Static Site Generation | SSG | Marketing pages, blogs, docs — content changes infrequently |
| Incremental Static Regeneration | ISR | SSG pages that need periodic refresh without full rebuild |

**Anti-patterns:** SSR for pages that don't need SEO or fresh-per-request data (unnecessary server cost); CSR for public landing pages (SEO miss).

---

## Performance Patterns

### Memoization

- `React.memo` — skip re-render if props haven't changed (shallow equal). Use on pure presentational components that render often.
- `useMemo` — memoize expensive computed values. Use only when computation is actually expensive; premature memoization adds overhead.
- `useCallback` — stable function reference for child props. Needed when passing callbacks to memoized children.

**Anti-pattern:** Wrapping every component in `memo` and every function in `useCallback` by default — measure first.

### Lazy Loading / Code Splitting

```js
const HeavyChart = React.lazy(() => import('./HeavyChart'))
// Wrap with <Suspense fallback={<Spinner />}>
```

Use for large components not needed on initial paint (charts, rich editors, admin panels).

### Virtualization

Render only visible rows in large lists. Use `react-window` or `TanStack Virtual`. Essential for lists > ~100 items; unnecessary for short lists.

### Image / Asset Optimization

Use framework primitives (`next/image`) for lazy loading, responsive sizing, and format optimization. Avoid raw `<img>` for large assets in SSR frameworks.

---

## CSS Architecture

| Approach | Best for | Trade-offs |
|---|---|---|
| BEM | Plain HTML/CSS projects; no build tooling | Verbose class names; naming discipline required |
| CSS Modules | React with build step; scoped styles per component | No global leakage; colocated with component |
| Utility-first (Tailwind) | Rapid prototyping; design-system-constrained teams | Large class strings in JSX; requires design token discipline |
| CSS-in-JS (styled-components, Emotion) | Dynamic styles based on props; theme integration | Runtime cost; bundle size; SSR complexity |

**Decision rule:** Prefer CSS Modules or Tailwind for new React projects. Use CSS-in-JS only if you need runtime-dynamic styles tied to JS values.

---

## SOLID in React

- **SRP:** One component, one responsibility. Container/hook for logic; presentational for rendering.
- **OCP:** Extend via props/composition; don't modify existing components for new use cases.
- **LSP:** Components in the same family (PrimaryButton / SecondaryButton) should accept the same base props.
- **ISP:** Small, focused prop interfaces. Don't force a component to accept props it ignores.
- **DIP:** Components depend on hook abstractions (`useUsers`), not concrete fetch implementations.

---

## Cross-references

- [[patterns/design-patterns-behavioral]] — Observer pattern underlies event systems and React's synthetic event model
- [[patterns/design-patterns-structural]] — Decorator pattern is the conceptual ancestor of HOC
- [[patterns/principles]] — DRY, KISS, SOLID applied to components
