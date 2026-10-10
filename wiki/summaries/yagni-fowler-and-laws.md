---
title: "YAGNI: Fowler's Bliki and Laws of Software Engineering"
type: summary
tags: [yagni, simple-design, extreme-programming, over-engineering, principles]
sources: ["bliki Yagni.md", "YAGNI (You Aren't Gonna Need It).md"]
created: 2026-10-10
updated: 2026-10-10
---

# YAGNI: Fowler's Bliki and Laws of Software Engineering

Two short sources on the same principle. The first is Martin Fowler's bliki entry "Yagni" (the capture has no byline or URL; the canonical page is martinfowler.com/bliki/Yagni.html, inferred from its links). The second is the YAGNI entry of *Laws of Software Engineering* (lawsofsoftwareengineering.com, last updated 2026-07-20 in the capture). Captured 2026-10-04, ingested 2026-10-10.

## The principle

Do not add a capability, or the abstraction that supports it, until you need it. It comes from Extreme Programming's Simple Design practice. The phrase is credited to a conversation between Kent Beck and Chet Hendrickson on the C3 project; Ron Jeffries popularised it: "Always implement things when you actually need them, not when you just foresee that you need them." Fowler calls the unneeded code a **presumptive feature**: code that supports a feature not yet available for use.

## Why: four costs of building early (Fowler)

| Cost | Meaning |
|---|---|
| **Build** | Effort on analysis, code and tests for something that turns out unneeded. |
| **Delay** | The work you did not do instead; value from the needed feature arrives later. |
| **Carry** | The extra complexity slows every feature built until the presumptive one is used (or removed). |
| **Repair** | The right feature built wrong: what you learn later means rework. |

He cites Kohavi et al.: of features built after careful up-front analysis at Microsoft, only about a third improved the metric they targeted, so the odds that a presumptive feature is unneeded are at least two in three. The comparison "cheaper to build now than later" has to be made against the cost of delay and that probability.

## Limits (the part people drop)

- **YAGNI applies to capability built to support a presumptive feature. It does not apply to effort that makes software easier to change.** Refactoring, self-testing code and continuous delivery are what make YAGNI viable; without them it turns into a curse. "Yagni is not a justification for neglecting the health of your code base."
- It applies only when the extra work **adds complexity** now. If a future-minded choice adds none, there is nothing to invoke YAGNI against. Fowler's example: a lookup table for error messages instead of inline literals, which makes later translation easy and costs almost nothing.
- Abstractions and parameterisation count too: "any abstraction that makes it harder to understand the code for current requirements is presumed guilty". This does not mean forgoing all abstraction.
- **Test: imagine the refactoring** you would need to add the capability later. Often the thought experiment shows it is not much dearer, which settles it.
- YAGNI can fail: an expensive change that an earlier, cheaper one would have avoided. Those cases are hard to spot in advance and easier to remember than the times it saved effort; Fowler judges the failures rare and outweighed.
- Small decisions matter: an hour spent adding an abstraction you are sure you will need soon is the common case, and many small ones compound.

## Laws entry: examples

Add no configuration flag "in case someone wants to toggle this"; extend a one-purpose function only when a second use arrives; implement simple JSON export, not a serialisation library covering XML and YAML. Teams that adopt it rely on refactoring confidence: defer only if you trust you can add it later at low cost, backed by tests, refactoring tools and CI.

## Wiki connections

- [[patterns/principles]] — the YAGNI section, rewritten from this source
- [[patterns/code-quality]] — "speculative generality" smell: delete or defer
- [[entities/ponytail]] — an agent skill built on the same minimality idea
- [[concepts/subagent-cost-model]] — a related cost argument: cost of carry in context, not code
