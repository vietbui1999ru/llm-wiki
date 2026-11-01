---
title: "When \"Do Not\" Is Not deny: Security Rules in CLAUDE.md vs Built-In Controls"
type: summary
tags: [claude-md, agent-security, permissions, sandbox, usable-security, context-files, research]
sources: ["pdfs/When _Do Not_ Is Not Deny_ Security Rules in CLAUDE.md vs Built-In Controls - 2608.23550v1.pdf"]
created: 2026-11-01
updated: 2026-11-01
---

# When "Do Not" Is Not deny (Yan, arXiv 2608.23550, Aug 2026)

Ting Yan, "When 'Do Not' Is Not deny: Security Rules in CLAUDE.md vs. Built-In Controls", arXiv 2608.23550v1. Parsed with Docling 2.107.0 (OCR off; born-digital PDF).

## Abstract

A security rule written in `CLAUDE.md` ("never run npm publish", "never log secrets") is prose the model interprets. A Claude Code `deny` permission rule is a control the platform applies before the action runs. Both look like the same intent. The paper measures how many security rules developers actually write in public `CLAUDE.md` files have a matching built-in Claude Code control. Answer: about 4-16% depending on how strictly "matching" is defined; 4.4% (95% CI 2.6-6.7%) under the strict, adjudicated standard the author treats as primary.

## Problem

`CLAUDE.md` is a **write-only security channel**. Code gives feedback (compile errors, failing tests, logs); a prose security rule gives none. Nothing in the file or the agent tells the developer whether a rule is enforced by a permission rule, mode or sandbox, or left to model judgment. Prior work catalogued what instruction files contain (Agent READMEs: security content in 14.8% of 2,303 files; a Cursorrules study: ~4.4% of coded instructions concern security) or built prose-to-policy converters (ContextCov, Prose2Policy, AutoCedar), but none counted how often an existing control already covers a written rule.

**RQ:** among the security rules the extractor retrieves from public `CLAUDE.md` files, what percentage have a matching built-in Claude Code control that applies the same rule without added code?

## Methods

- **Corpus (Frame A):** GitHub code search for filename `CLAUDE.md`, retrieved 2026-08-14. Capped (1,000 results/query), relevance-ranked, so a convenience sample, not random. 647 repositories examined, 481 included (root or `.claude/CLAUDE.md`, ≥500 chars, English-dominant, no forks/mirrors, pinned to a commit SHA). Seed 20260813.
- **Extraction:** split each file into Markdown lines/sentences; keep segments containing rule words ("must", "never", "only", "do not", "ask before"...). 4,661 candidate segments.
- **Control reference:** Claude Code's documented controls frozen on 2026-08-13: `allow`/`ask`/`deny` permission rules (tool, Bash command, Read/Edit path, WebFetch domain patterns), permission modes, `additionalDirectories`, filesystem and network sandbox, managed settings. **Hooks are excluded**: a `PreToolUse` hook needs written code, and prompt/agent hooks decide by model judgment.
- **Matching definition (strict):** a control matches only if it covers the whole rule: same action, same target, the condition that makes the action wrong, and who must approve. Over-blocking many safe actions does not count.
- **Classifier:** an LLM (named in the paper as "Claude Sonnet 5"), one frozen prompt, told to resolve uncertainty toward "match" and to name the control it matched.
- **Validation:** 180 candidates, 60 per classifier stratum (not security / security without match / security with match; population sizes 3,791 / 726 / 144), labelled blind by two security practitioners, disagreements adjudicated. Inverse-probability weights; repository-clustered bootstrap (10,000 replicates) for every interval.
- **Extraction-recall audit:** one annotator read 50 random files in full, blind to the extractor.
- **Replication (Frame B):** the `CLAUDE.md` subset of the Agent READMEs dataset (701 repositories, at most 3 shared with Frame A). Classifier only, no human labels.

## Key results

**Table I: coverage among retrieved security rules (870 classifier-positive segments).**

| Matching standard | Has a match | No match (gap) |
|---|---|---|
| Classifier, full corpus | 16.6% [12.5, 21.4] | 83.4% [78.6, 87.5] |
| Human, loose (one annotator) | 14.3% [7.6, 23.4] | 85.7% [76.6, 92.4] |
| Adjudicated, strict (primary) | **4.4% [2.6, 6.7]** | **95.6% [93.3, 97.4]** |

The matching standard, not sampling error, drives the spread. "Loose" credits a control that can target the rule's command, path or domain even when it cannot express the full condition.

**Reliability (Table II, design-weighted against the 180 adjudicated labels).**

| | Security-relevant | Matching control |
|---|---|---|
| Classifier precision | 0.894 [0.816, 0.958] | 0.350 [0.219, 0.488] |
| Classifier recall | 0.672 [0.523, 0.867] | 1.000 |
| Annotator agreement | 90.0% | 96.5% (111/115) |
| Cohen's κ | 0.77 | 0.89 |

The classifier over-credits: it finds every true match but two thirds of its "matches" are rejected by humans. Its single repeated error is seeing a blockable command, path or domain and calling it a match. The four rejected kinds:

1. A **condition** the pattern cannot encode ("run `npm publish` only when cutting a release"; "never merge to main, only the user does that").
2. **Content** rather than location ("never commit secrets"; no permission pattern reads content).
3. **Authorization by meaning or system state** ("the backend reads but never writes `portfolio.locked_amount`").
4. **Data-flow** requirements ("only LLM API calls leave the network"; the domain allowlist does not express this).

**Extraction recall:** 63 of 95 in-scope reference rules = 66.3% [48.8, 82.0]. Misses are flat statements, rules split across headings, or other wording. All rates apply only to retrieved rules.

**By resource family (Table III, classifier only, exploratory; family agreement with the annotator only 57.1% weighted):** destructive commands 31.5% (n=248), egress 26.5% (34), secrets 20.0% (140), authorization/approval 6.9% (290), other 5.8% (104), PII 5.6% (54).

**Rule wording does not predict enforceability:** coverage by first rule word overlaps (never 23%, do not 19%, always 25%, only 11%, must 7%).

**Which controls the classifier cites (144 matches):** `deny` 99 (69%), `ask` 33 (23%), `allow` 4, network sandbox 3, permission modes 3, filesystem sandbox 2.

**Unvalidated secondary split of the 870 (Appendix C, classifier only):** 16.6% match; 51.3% "custom" (a deterministic check is writable but needs a hook, scanner or CI); 20.8% model-mediated (open-ended judgment); 11.4% missing-context (information not visible at enforcement). The author explicitly does not read the 51.3% as the share added code could close.

**Robustness:** re-weighting by template or repository and dropping the largest repositories keeps the classifier estimate at 16.6-21.3%. Frame B gives 25.1% [20.8, 30.0], still a minority.

**Control-reference audit (post hoc, 2026-08-16):** `additionalDirectories` was described backwards (it grants access, it does not restrict); `sandbox.credentials` was missing; and the network sandbox **only blocks non-allowlisted hosts when `strictAllowlist` or a managed lockdown is also set; `allowedDomains` alone blocks nothing**. None changed a label.

## Limitations

- Measures whether a documented control *exists*, not whether a repository configured it, whether it works at runtime, or whether the team enforces the rule elsewhere (CI, hooks, org tooling). A rule without a matching control is not necessarily unprotected.
- Convenience sample skewed to new, low-visibility projects: 93% of segments from repositories created 2025-2026; 58% of repositories have no stars.
- Single product (Claude Code) at a single freeze date; Frame B reuses the same instrument.
- Family breakdown and secondary reasons rest on one annotator or none.
- Extraction recall about two thirds; missed rules may differ.
- Single author; the paper discloses that an OpenAI Codex model assisted with analysis code and polishing *(model name as given in the paper, reported, unverified)*.

## Design response proposed

Close the loop: show beside each rule whether a built-in control backs it; mark unenforceable rules as advisory; log when a rule would have applied; help convert prose into a reviewable check.

## Wiki connections

- [[concepts/agent-context-instructions]]: adds the security-rule angle: prose security rules in context files are mostly unenforced; put enforceable ones in `permissions.deny`/`ask`, hooks or CI.
- [[summaries/claude-code-permissions-settings]]: the controls this paper measures against. The paper's audit says `allowedDomains` alone does not block other hosts; that page presents `allowedDomains` + `deniedDomains: ["*"]` as default-deny, which may need re-checking against current docs (not edited here).
- [[summaries/less-is-more-claude-md]]: same family of evidence that `CLAUDE.md` content is weaker than it looks (Gloaguen et al. is the paper's reference [16]).
- [[concepts/rules-vs-hooks]]: the paper's "custom" category is exactly what hooks exist for; it quantifies how much of the gap is hook-shaped.
- [[concepts/agentic-sandbox-controls]]: sandbox as one of the few built-in deterministic controls.
- [[summaries/steer-not-script-agent-instructions]]: "safety gates are better as hooks than prose" now has a measured basis.
