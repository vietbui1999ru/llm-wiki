---
title: "SWE-Bench Mobile: Can LLM Agents Develop Industry-Level Mobile Applications?"
type: summary
tags: [benchmark, coding-agents, swe-bench, mobile, ios, multimodal, harness, evaluation, research]
sources: ["pdfs/SWE-Bench Mobile_ Can Large Language Model Agents Develop Industry-Level Mobile Applications_.pdf", "pdfs/SWE-Bench Mobile_ Can Large Language Model Agents Develop Industry-Level Mobile Applications_page_11.pdf"]
created: 2026-11-01
updated: 2026-11-01
---

# SWE-Bench Mobile (Tian, Wang et al., KDD 2026)

Muxin Tian, Zhe Wang et al. (University of Toronto, Xiaohongshu Inc., UIUC, UC Berkeley, Coolwei AI Lab), *KDD 2026*, DOI 10.1145/3770855.3818488. Leaderboard: swebenchmobile.com.

**Parsing note:** the full PDF is a browser print of image-only pages (no text layer), so Docling without OCR returned only images and Docling's OCR engines were not usable on this machine. The 10 pages were read natively instead. The separate `_page_11.pdf` file is the paper's last page (end of Appendix C: agent differences and practitioner implications), which the 10-page file lacks; it is used below.

**Evidence status for every number below:** author-reported, from a benchmark the authors built and host on a **private** test set. Results cannot be independently reproduced. n = 50 tasks, so **one task = 2 percentage points**; most configurations ran once.

## Abstract

A benchmark for coding agents doing feature work in a large production iOS codebase, with multimodal inputs (PRDs and Figma designs). 22 agent-model configurations across four agents (Cursor, Codex, Claude Code, OpenCode). The best reach a 12% task success rate.

## Problem

HumanEval and MBPP are isolated algorithmic problems. SWE-Bench uses real GitHub issues but is bug fixing, text-only, mostly 1-2 file changes, and Python. Industrial development instead means reading a PRD, translating a Figma design, navigating hundreds of thousands of lines, and making coordinated multi-module changes. Mobile adds visual grounding, event-driven state (lifecycle callbacks, async events), and framework-heavy, less-represented languages (Swift/Objective-C).

## Methods

**Task format.** Each instance is a triple (input, expected output, evaluation config). Input: a PRD (avg 450 words, from real Xiaohongshu product requirements), a Figma design for 70% of tasks, reference images for 92%, and a snapshot of the Xiaohongshu iOS codebase (~500K lines Swift/Objective-C, ~5 GB). Output: a unified diff patch.

**Dataset (Table 1).** 50 tasks, 449 test cases (avg 9.1 per task), avg 4.2 files modified per task. Categories: UI components 18, data management 10, gesture and interaction 8, media and assets 7, networking 4, other 3. Difficulty: easy 15, medium 25, hard 10 (easy = 1-2 files and <50 lines; hard = 6+ files and >150 lines).

**Evaluation method (important for reading the numbers).** Tests are task-specific `pytest` suites that **inspect the diff text**: pattern matching and structural analysis for feature entry points, removal of blocking behaviour, cross-file cohesion, and semantics-aware matching of alternative names. **The app is never compiled or run**, so a patch can pass without building. Static checks first reject empty or whitespace-only diffs and malformed patches. A missing patch (timeout or error) counts as failing all its tests.

**Metrics.** Task Success Rate: percentage of the 50 tasks where all tests pass. Test Pass Rate: percentage of the 449 test cases passed.

**Setup.** macOS 14.x; Cursor v2.3 (agent mode), Codex CLI v0.77.0, Claude Code CLI v2.1.37, OpenCode v1.1.44. Models: Claude Opus 4.5, Sonnet 4.5, Haiku; GPT-5, 5.1, 5.2; Gemini 3 Pro; GLM-4.6, GLM-4.7. Figma reached through the official Figma MCP for vision models; GLM-4.6 got a GLM Vision MCP that turned designs into text.

## Key results

**Headline.** Best Task Success 12% (6 of 50 tasks): Cursor + Opus 4.5, Cursor + Sonnet 4.5, Codex + GLM-4.6. Best Test Pass 28.1% (Cursor + Opus 4.5; Codex + Sonnet 4.5).

**Table 5 (abridged): Task Success / Test Pass / cost per task / time.**

| Agent | Model | Task % | Test % | $/task | min |
|---|---|---|---|---|---|
| Cursor | Opus 4.5 | 12.0 | 28.1 | 3.50 | 15.0 |
| Cursor | Sonnet 4.5 | 12.0 | 26.7 | 2.00 | 14.2 |
| Cursor | GPT-5.1 | 2.0 | 19.6 | 1.10 | 14.2 |
| Codex | GLM-4.6 | 12.0 | 19.6 | 1.30 | 13.3 |
| Codex | Sonnet 4.5 | 10.0 | 28.1 | 2.50 | 12.5 |
| Codex | Opus 4.5 | 4.0 | 20.7 | 3.50 | 14.2 |
| Codex | GPT-5.1 | 0.0 | 7.1 | 1.00 | 13.3 |
| Claude Code | GLM-4.6 | 10.0 | 26.7 | 1.30 | 11.7 |
| Claude Code | Sonnet 4.5 | 10.0 | 24.7 | 2.00 | 13.3 |
| Claude Code | Opus 4.5 | 8.0 | 21.8 | 4.00 | 15.0 |
| Claude Code | Haiku | 8.0 | 18.3 | 0.50 | 8.3 |
| OpenCode | GLM-4.6 | 8.0 | 17.8 | 0.13 | 32.5 |
| OpenCode | GPT-5.1 | 6.0 | 7.1 | 0.02 | 2.0 |
| OpenCode | Opus 4.5 | 2.0 | 12.0 | 9.33 | 8.2 |

Costs: OpenCode via OpenRouter API billing; GLM via the GLM Coding Plan; prices at experiment time.

**Harness matters as much as the model.** Same model, different agent: Opus 4.5 scored 12% on Cursor vs 2% on OpenCode (6 tasks vs 1), the paper's "6x gap". Commercial agents beat OpenCode for every model tested; OpenCode's best (GLM-4.6, 8%) trails the best commercial result by 4 points (2 tasks). The paper attributes this to tool use, context management and iteration strategy, without an ablation that isolates which. The appendix observes OpenCode "often gets stuck in endless file reading loops" on the large codebase.

**Complexity (Figure 5).** Success falls from 18% for 1-2-file tasks (n=3) to 2% for 7+ files (n=11); 20% for patches under 50 lines vs 3% over 200 lines. Error bars are binomial 95% CIs and overlap heavily at these sample sizes. By difficulty label: easy 18.5% pass, hard 5.8%.

**Robustness (Figure 8).** Claude Code + Opus 4.5 over 3 runs: 6, 8, 6% (mean 6.7%, σ 1.15). Codex + Opus 4.5 over 2 runs: 4, 4%. Run-to-run noise of about one task is the same size as many of the between-configuration differences above.

**Prompt ablation (Table 4; one configuration only, Claude Code + GLM-4.6).**

| Prompt strategy | Task % | Test % |
|---|---|---|
| Defensive Programming | 10.0 | 26.7 |
| Quality Focused | 10.0 | 26.3 |
| Baseline | 10.0 | 19.3 |
| Test Driven | 6.0 | 22.0 |
| Detailed Role / Structured Checklist / Context Rich / Comprehensive | 4.0 | 20.7-22.7 |

Defensive prompting raised Test Pass by 7.4 points with no change in tasks solved. The four elaborate prompts each cost 3 tasks of success. The authors conclude simple prompts beat complex ones; this is one model, one agent, one run per prompt.

**Failure analysis (best agents; categories overlap).** Missing feature flags 54% (agents implement the feature but skip the feature toggle or experiment flag required for gradual rollout), missing data models 22%, missing files 11-15%, missing UI components 11-15%, missing required methods 9%, incomplete multi-file implementation 4-7%. Predictors of success: well-scoped 1-3 file changes, PRDs naming classes, method signatures or similar code, isolated modules, existing patterns to copy. Predictors of failure: logic spread across architectural layers, PRDs saying "all scenarios" or "everywhere" without file lists, UI-plus-logic coupling, novel patterns.

**Per-agent observations (appendix, qualitative).** Cursor: best exploratory search, finds the right files but may not edit them all. Claude Code: conservative, well-formed patches for the files it chooses. Codex: strong generation, weaker navigation, relies on initial context. OpenCode: file-reading loops.

## Limitations

- One proprietary codebase and one platform (iOS); Android/Kotlin is future work.
- Diff-text tests check structural intent, not runtime behaviour; a passing patch may not compile, and a correct but unusually shaped patch may fail.
- Private test set: protects against contamination but blocks independent verification of every number.
- 50 tasks and mostly single runs: differences of 1-2 tasks (2-4 points) are inside run-to-run noise.
- Prompt ablation covers one agent-model pair.
- The benchmark authors include employees of the company whose codebase is used.

## Wiki connections

No existing wiki page covers SWE-bench; this is the first SWE-bench-family page.

- [[concepts/agent-harness]]: direct, if noisy, evidence that the harness around a model changes outcomes (same Opus 4.5, 12% vs 2%).
- [[entities/opencode]]: the open-source agent tested; weakest harness here, with file-reading loops on a 5 GB repo.
- [[entities/ai-coding-agents]]: Cursor, Codex, Claude Code compared head to head.
- [[concepts/llm-eval-pipeline]]: design choices worth borrowing (private held-out set against contamination, task-level vs test-level metrics) and a cautionary one (diff-pattern tests instead of execution).
- [[concepts/agent-test-verification]]: diff-text pytest suites are a weak oracle; "tests pass" here means "the patch looks like it contains the right edits".
- [[summaries/less-is-more-claude-md]]: same direction as the prompt ablation: more elaborate instructions did not help and often hurt.
- [[concepts/agent-context-instructions]]: the 54% feature-flag miss is the kind of non-obvious, project-specific rule that belongs in a context file.
