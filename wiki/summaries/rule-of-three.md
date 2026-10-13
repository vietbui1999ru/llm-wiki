---
title: "Rule of Three (Three Strikes and You Refactor)"
type: summary
tags: [rule-of-three, refactoring, duplication, dry, abstraction, principles]
sources: ["The Rule of Three in Computer Programming.md", "Rule of three (computer programming).md"]
created: 2026-10-11
updated: 2026-10-11
---

# Rule of Three (Three Strikes and You Refactor)

Two short sources on one refactoring heuristic: a blog post titled "The Rule of Three in Computer Programming" (the capture has no byline or URL) and the Wikipedia entry "Rule of three (computer programming)". Captured 2026-10-10 and 2026-10-11, ingested 2026-10-11. The two agree and overlap almost completely, so this is one summary, not two.

## The rule

Two instances of similar code do not need refactoring. When similar code appears a third time, extract it into a procedure or function. Wikipedia: popularised by Martin Fowler in *Refactoring* (Fowler, Beck, Brant, Opdyke, Roberts; Addison-Wesley, 1999) and attributed to Don Roberts. The blog calls it "three strikes and you refactor".

## Why have a rule at all (cost of duplication)

- **Maintenance:** when the rule a copy encodes changes, every copy must change, and a missed one is a bug.
- **Consistency:** business-logic changes must be applied the same way everywhere.
- **Bloat:** more code to navigate; one function centralises the logic.

## Why wait for the third (the actual content of the rule)

Two examples are too few to see the real pattern. Extracting at the second copy risks picking the **wrong abstraction**, which Sandi Metz argues makes code worse as new requirements arrive and will need refactoring again (Metz, "The Wrong Abstraction", 2016: sandimetz.com/blog/2016/1/20/the-wrong-abstraction). A third example supplies enough context to see what the copies share and where they differ.

Wikipedia states the economics: with three copies, the cost of maintaining them outweighs the cost of refactoring plus the risk of a bad design; with two copies it may or may not. The blog's illustration: the same logging snippet pasted a first, second and third time; the third is the signal to extract one logging function.

## Limits and caveats

- It is a **rule of thumb**, not a measured result. Neither source gives evidence for "three" over "two" or "four"; the number is a convention.
- It says when to *consider* extracting, not that the copies are the same knowledge. Look-alike code that encodes different business rules should stay separate (the DRY qualifier in [[patterns/principles]]).
- Both sources treat it as a balance between duplication and over-engineering; neither covers how to detect the third copy in a large codebase.

## Wiki connections

- [[patterns/principles]] — new "Rule of Three" subsection after DRY and YAGNI: the timing rule that reconciles them
- [[summaries/yagni-fowler-and-laws]] — the sibling principle: defer capability and abstraction until needed
- [[patterns/code-quality]] — duplicate-code smell (extract) and speculative generality (defer)
- AI relevance (inference, not from the sources): the code-quality page notes LLMs reimplement existing utilities; the Rule of Three also argues against letting an agent abstract after the first or second occurrence.
