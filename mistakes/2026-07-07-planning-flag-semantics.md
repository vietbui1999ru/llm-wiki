---
date: 2026-07-07
type: bad-assumption
domain: planning
severity: low
---

# Plan misstated DISABLE_RATE_LIMIT scope and failure behavior

## What happened
Plan claimed `DISABLE_RATE_LIMIT` "hard-fails outside dev" and gates all rate limiting. Actually it is only read inside `checkRateLimitAsync` (the Upstash-aware auth limiter), only throws when `NODE_ENV === 'production'` (test env silently disables), and has zero effect on the sync `checkRateLimit` / `checkRateLimitBucket` limiters used by the settings/logs/chat/generate routes.

## What the fix was
Read `lib/rate-limit.ts` end to end; plan corrected to treat the three limiter families separately.

## Prevention rule
Before claiming an env flag's scope, grep every read-site of the flag — a flag checked in one function does not gate sibling functions in the same module.

## Context
ResumeLoop demo abuse-threshold design, 2026-07.
