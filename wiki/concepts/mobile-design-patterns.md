---
title: "Mobile Design Patterns"
type: concept
tags: [mobile, ux, react-native, flutter, ios, android, touch, gestures, performance]
sources:
  - "Gesture Navigation in Mobile Apps Best Practices.md"
  - "mobile-design — sickn33antigravity-awesome-skills.md"
created: 2026-05-13
updated: 2026-05-13
---

# Mobile Design Patterns

Core doctrine for designing and building mobile UIs. The central law: **mobile is not a small desktop**. Constraints come first, aesthetics second. Touch-first, battery-conscious, platform-respectful, offline-capable.

## Mobile Feasibility & Risk Index (MFRI)

Before designing any mobile feature, assess feasibility across five dimensions (each scored 1–5):

| Dimension | Question |
|---|---|
| Platform Clarity | Is the target platform (iOS/Android/both) explicitly defined? |
| Interaction Complexity | How complex are gestures, flows, or navigation? |
| Performance Risk | Does this involve lists, animations, heavy state, or media? |
| Offline Dependence | Does the feature break without network? |
| Accessibility Risk | Does this impact motor, visual, or cognitive accessibility? |

**Formula:** `MFRI = (Platform Clarity + Accessibility Readiness) − (Interaction Complexity + Performance Risk + Offline Dependence)`

**Range:** −10 → +10

| MFRI | Status | Action |
|---|---|---|
| 6–10 | Safe | Proceed normally |
| 3–5 | Moderate | Add performance + UX validation |
| 0–2 | Risky | Simplify interactions or architecture |
| < 0 | Dangerous | Redesign before implementation |

## Touch Psychology

- **Finger ≠ cursor.** Accuracy is low. Reach matters more than precision.
- **Fitts' Law:** Primary CTAs live in the thumb zone. Destructive actions pushed away from thumb reach. No hover assumptions.
- **Minimum touch targets:** 44pt (iOS) / 48dp (Android). Non-negotiable.

## Gesture Design

### Design for natural mapping

Mirror real-world actions:

| Gesture | Real-World Analogy | Digital Use |
|---|---|---|
| Swipe left/right | Turning pages | Navigating between content |
| Pinch | Manipulating physical items | Zoom in/out |
| Pull down | Opening a drawer | Refresh or reveal |

### Consistency is the contract

If swiping left archives an email in one part of the app, it must do so everywhere. Breaking consistency breaks muscle memory and trust.

### Feedback is mandatory

Every gesture needs confirmation:
- Animation previews showing available gestures
- Progress indicators during multi-step gestures
- Haptic feedback confirming completion (not just visuals)

### Never gesture-only

Gestures must always have a backup:
- Button equivalents for every gestural action
- Voice command alternatives for hands-busy scenarios

Gesture-only navigation excludes users with motor impairments and fails discoverability.

### Prevent overload

Keep the gesture set minimal. Tinder uses exactly two gestures (swipe left, swipe right) for its core function. Complexity should live in the content, not the interaction model.

### Onboarding for non-obvious gestures

Hidden or unconventional gestures require:
- Interactive tutorials on first encounter
- Visual indicators (e.g., subtle animations showing swipe affordance)
- Gradual introduction, not a gesture glossary dump at launch

## Platform Divergence Matrix

Some things should be unified across platforms; others must diverge to respect platform conventions:

```
UNIFY                          DIVERGE
──────────────────────────     ─────────────────────────
Business logic                 Navigation behavior
Data models                    Gestures
API contracts                  Icons
Validation                     Typography
Error semantics                Pickers / dialogs
```

### Platform defaults

| Element | iOS | Android |
|---|---|---|
| Font | SF Pro | Roboto |
| Min touch target | 44pt | 48dp |
| Back navigation | Edge swipe from left | System back gesture |
| Modal sheets | Bottom sheet | Dialog or sheet |
| Icon system | SF Symbols | Material Icons |

## Performance Doctrine

### Hard bans

| Never | Why | Always |
|---|---|---|
| `ScrollView` for long lists | Memory explosion | `FlatList` / `FlashList` / `ListView.builder` |
| Inline `renderItem` | Re-renders all rows | `useCallback` + `memo` |
| Index as key | Reorder bugs | Stable ID from data |
| JS-thread animations | Jank | Native driver / GPU-accelerated |
| `console.log` in production | JS thread block | Strip logs at build |
| No memoization | Battery + perf drain | `React.memo` / `const` widgets |

### Required patterns

React Native:

```ts
const Row = React.memo(({ item }) => (
  <View><Text>{item.title}</Text></View>
));

const renderItem = useCallback(
  ({ item }) => <Row item={item} />,
  []
);

<FlatList
  data={items}
  renderItem={renderItem}
  keyExtractor={(i) => i.id}
  getItemLayout={(_, i) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * i,
    index: i,
  })}
/>
```

Flutter: `const` everywhere possible, targeted rebuilds only.

### Animation

Only animate `transform` and `opacity` (GPU-accelerated). Never animate layout properties (triggers expensive reflow on the JS thread).

## Touch & UX Anti-Patterns

| Never | Why | Fix |
|---|---|---|
| Touch target < 44–48px | Miss taps | Pad hitSlop |
| Gesture-only action | Excludes users | Button fallback |
| No loading state | Feels broken | Explicit feedback |
| No error recovery | Dead end | Retry + user-facing message |
| Ignore platform norms | Breaks muscle memory | Check iOS HIG / Material Design |

## Security Patterns

| Never | Why | Fix |
|---|---|---|
| Tokens in `AsyncStorage` | Easily stolen | `SecureStore` / Keychain |
| Hardcoded secrets | Reverse-engineered | Env vars + secure storage |
| No SSL pinning | MITM risk | Certificate pinning |
| Log sensitive data | PII leakage | Never log tokens/credentials |

## Framework Decision Tree

```
Need OTA updates + web team → React Native + Expo
High-performance UI required → Flutter
iOS only                     → SwiftUI
Android only                 → Jetpack Compose
```

No debate without explicit justification.

## Pre-Code Checkpoint

Before writing any mobile code, answer:

```
Platform:      iOS | Android | Both
Framework:     RN | Flutter | SwiftUI | Compose
MFRI Score:    ___

3 principles I will apply:
1.
2.
3.

Anti-patterns I will avoid:
1.
2.
```

## Release Readiness Checklist

- [ ] Touch targets ≥ 44–48px
- [ ] Offline states handled (degraded mode, not crash)
- [ ] Secure storage used (no tokens in AsyncStorage)
- [ ] Lists use FlatList/FlashList with memo + useCallback
- [ ] Production logs stripped
- [ ] Tested on low-end device
- [ ] Accessibility labels on all interactive elements
- [ ] MFRI ≥ 3 for all features

## Emerging Patterns

- **AI-driven gesture recognition:** Context-aware gesture interpretation, predictive gesture anticipation based on user behavior
- **Multimodal input:** Gesture + voice combinations for hands-busy scenarios; automatic input method switching based on context
- **AR gestures:** 3D gesture tracking for spatial interaction (AR furniture placement, etc.)

## Related Pages

- [[patterns/frontend]] — React component patterns, rendering strategies, CSS architecture
- [[concepts/owasp-security-checklist]] — mobile security intersects with token storage and input validation
- [[entities/spotme]] — mobile skill scaffold via React Native skills (Vercel)
