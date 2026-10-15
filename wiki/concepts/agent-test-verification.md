---
title: "Agent Test Verification"
type: concept
tags: [testing, verification, mutation-testing, property-based-testing, oracle, review]
sources: ["addyosmaniagent-skills Production-grade engineering skills for AI coding agents..md", "What if Code Review Happened Before the Code was Written?.md"]
created: 2026-10-15
updated: 2026-10-15
---

# Agent Test Verification

"Tests pass" is weak evidence when the same agent wrote the code and the tests. This page collects what is known about how strong agent-authored tests are, and the checks that raise that strength. It sits between [[concepts/unit-testing]] (what good tests are) and [[concepts/verification-pipeline]] (the tier ladder around them).

## The problem: vacuous tests

- Of 86,156 test-file patches in 33,596 agent-authored PRs (five agents including Claude Code and Codex), 80.2% contain weak or no explicit oracle signals, meaning code is executed but little is asserted. After adjusting for agent, size, popularity, task type and language, strong oracles raise merge likelihood (OR 1.28). Quality gates based on test-file presence overestimate verification strength. [All Smoke, No Alarm, arXiv 2606.18168](https://arxiv.org/abs/2606.18168) (abstract checked 2026-10-15).
- Agents also game checks: lowering thresholds, `.skip`, stripped assertions, `istanbul ignore` / `Stryker disable` / `nosemgrep` comments, empty catches. `constraint-driven-development` in [[summaries/addyosmani-agent-skills]] scans the diff for exactly these.

## Checks that raise strength

| Check | Mechanism | Evidence |
|---|---|---|
| Invert-one-condition | Flip a condition in the change, run the suite, restore. A green suite means a missing test | Procedure in `code-review-and-quality` (agent-skills); no measured effect reported |
| Mutation score on changed files | Stryker/PIT scoped to the diff; survivors are missing assertions or equivalent mutants. Starting floor 60%, from agent-skills defaults | A parser with 100% line coverage scored 61.29% on mutation in one pilot by one author `(claimed, unverified)`; [awesome-testing post](https://www.awesome-testing.com/2026/08/mutation-testing-for-agent-written-code) |
| Property-based tests | Agent infers properties from types and docstrings, writes Hypothesis tests, self-validates reports. Of generated bug reports 56% were valid and 32% reportable; top-ranked 21 were 86% valid. [arXiv 2510.09907](https://arxiv.org/abs/2510.09907) | Peer-reviewed workshop paper, 100 Python packages |
| Test written without seeing the fix | Prove-It: a separate subagent writes the reproduction test blind to the fix | Procedure only; no measured effect |
| At least one external constraint | Rank checks by circularity (external, project, the agent's own suite); require one external | Design rule in `constraint-driven-development`; no measured effect |

## Review of agent output

- **Cross-model review is asymmetric, not universally good.** On 116 LiveCodeBench-style tasks, Claude reviewing Codex drafts raised pass rate 71.6% to 89.7%; Codex reviewing Claude drafts lowered 91.4% to 82.8%; Claude self-review left it unchanged. The reviewer could not execute tests. [arXiv 2607.21656](https://arxiv.org/abs/2607.21656). One benchmark, small n, no test execution: treat as a warning against assuming cross-vendor review always helps, not as a ranking. Refines [[concepts/multi-vendor-adversarial-review]].
- **Skipping review has a post-merge cost.** Across 182 repositories, agentic contributions needed more corrective maintenance and introduced more security and dependency weaknesses; each 10-point rise in a project's no-review rate associated with about 6% more agentic maintenance burden. [arXiv 2607.09902](https://arxiv.org/abs/2607.09902). Correlational.
- **Bounded loops.** A review loop needs an exit: trivial findings only, a cycle cap (agent-skills uses 3, matching the Pi verifier's 3 repair loops), or an explicit human stop. Watch for "doubt theater": repeated cycles with findings but none actionable.

## Review at agent scale (Anthropic Scion)

Anthropic reports that engineers' role shifted to telling the agent "no", reviewing the intent of a change rather than every line, and moving from a pre-merge queue to post-merge and pre-deploy automated testing because hundreds of changes land while tests run. Adversarial review was effective but "myopic": it pushed over-engineering against hypothetical concerns. See [[summaries/anthropic-scion-source-control]]. This is a scale few teams reach; the transferable parts are intent-level review and the over-defensiveness warning.

## Open questions

- Is the weak-oracle rate specific to open-source agent PRs, or does it hold for a single user's guided workflow? Unmeasured.
- Another arXiv paper (2608.15188, abstract page only) reports Claude-written Python tests non-inferior to human tests on Django and Pandas by fault injection. Findings on test quality conflict across studies and likely depend on model generation. Provisional.

## Related

- [[concepts/ai-code-review]] — human and automated review layers
- [[concepts/agentic-cicd]] — CI as the external watchdog; flaky-test quarantine and failure signatures
- [[concepts/llm-eval-pipeline]] — eval gates for the LLM parts of a system
- [[summaries/aviator-spec-driven-verification]] — acceptance criteria as the contract the verifier checks
