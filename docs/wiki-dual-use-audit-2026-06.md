# llm-wiki Dual-Use Audit & Optimization Plan

*Produced 2026-06-12 by a read-only 4-lens agent council (agent-consumer, human-learner, maintainer/cost, adversarial verifier). 21 findings raised, 4 refuted, 2 net-new added. No wiki pages were modified — this is a decision artifact pending Viet's approval.*

## Verdict — Is the Wiki Useful for AI Agents Today?

The wiki is moderately useful for agents and genuinely useful for humans, but the two-layer architecture described in the target model is only partially implemented. The pull layer (qmd retrieval) works well: four of five agent-realistic queries returned the correct page at rank 1 with confidence scores above 0.93. The concepts/ and entities/ layers are well-written, cross-linked, and substantive. For a human learning agent-engineering, this is a solid resource with 140 pages covering real ground.

The agent-consumption layer is the weak point. The real Tier 0 distillation is applied-ai.md (31 lines, always-loaded) — and that pairing with concepts/ is healthy in principle. But two concrete failures undermine it: global-prevention-rules.md has grown 80% past its stated 30-line cap with no enforcement gate, and it carries a live drift bug (the instinct-clustering documented-not-adopted label) that every session loads incorrectly. The patterns/ directory (13 pages, 253–557 lines each) has no agent-facing trigger clauses, causing agents that retrieve these files to parse hundreds of lines for rules that could be surfaced in a 10-line header block. Tier 1 (hook-enforced gates) is almost entirely absent: one PostToolUse hook exists, no PreToolUse gates.

**Scorecard** (averaged across lenses, adjusted for verifier):

| Dimension | Agent-Usefulness | Human-Usefulness |
|---|---|---|
| Agent-Consumer | 5 | 8 |
| Human-Learner | 7 | 6 |
| Maintainer/Cost | 6 | 7 |
| **Average** | **6.0** | **7.0** |

The wiki earns a 6/10 for agents and 7/10 for humans. Both scores are achievable at 8+ with the P0 and P1 fixes below.

## The Two-Layer / Tiered Target

The target model separates a human-readable source-of-truth layer (concepts/ prose pages, fully cited, cross-linked) from a derived agent-consumption layer delivered in three tiers: Tier 0 (tiny always-loaded push — CLAUDE.md + global-prevention-rules.md + applied-ai.md), Tier 1 (hook-fired rules that activate on specific triggers at zero cost when idle), and Tier 2 (the large pull body fetched JIT via qmd / wiki-context skill). The hard constraint baked into this model is that pull stays the default: nothing large goes into every session's context, because a prior decision already reclaimed 8,400 tokens by removing the wiki index from startup. Every action below is evaluated against that constraint — if a recommendation would push large content into all sessions, it is disqualified or reworked.

## Prioritized Action List

### P0 — Do First (Blocks Dual-Use or Correctness)

**P0-A: Add a lint step for Tier-0 distillation staleness**

The wiki lint procedure (CLAUDE.md "lint the wiki" operation) checks orphans, stale cross-refs in wiki/, and missing concept pages — but has no step verifying that applied-ai.md and global-prevention-rules.md still match their cited Tier-2 sources. This is the structural root cause of the instinct-clustering drift (P1-A) and the applied-ai.md compression omission (P1-E). Without this step, every lint pass gives a false clean bill of health on the most user-facing files.

- **What**: Add a step to CLAUDE.md's lint operation: "For each wikilink cited in applied-ai.md and global-prevention-rules.md, verify the linked page's current recommendation matches the Tier-0 claim. Flag any mismatch."
- **Why**: Closes the silent-drift window that is the single biggest maintenance risk of the two-layer split.
- **Tier touched**: Tier 0 (the distillation files), enforced at lint time (manual Tier 1 equivalent).
- **Effort**: S — one paragraph added to CLAUDE.md's lint section; five-minute manual checklist per lint run.
- **Files**: `CLAUDE.md` (lint operation section).

### P1 — High Value

**P1-A: Fix the live drift bug in global-prevention-rules.md (instinct-clustering)**

Every session loads an instruction to label `[[concepts/instinct-clustering]]` as `*(documented-not-adopted)*`. Log.md records that this status was removed months ago when ECC v2 was added as a reference implementation. The page no longer carries that status. This is a Tier-0 correctness failure, not a hygiene issue.

- **What**: Remove the instinct-clustering example from global-prevention-rules.md line 31 and replace with a generic pattern statement. Update agent-self-correction.md (lines 33 and 96) to drop the stale label. Run synthesize-mistakes to re-distill the file to ≤30 lines.
- **Why**: Agents consuming Tier 0 today receive an incorrect labeling instruction for a promoted concept.
- **Tier touched**: Tier 0 (global-prevention-rules.md), Tier 2 (agent-self-correction.md).
- **Effort**: S — three targeted line edits plus one synthesize-mistakes invocation.
- **Files**: `mistakes/global-prevention-rules.md`, `wiki/wiki/concepts/agent-self-correction.md`.

**P1-B: Enforce the 30-line cap on global-prevention-rules.md**

The file is 54 lines against a stated cap, has grown by two rules in the last three days without pruning, and carries no enforcement gate. At the current growth rate it will double within two months. The cap comment is decorative without a mechanical check.

- **What**: After P1-A's synthesize-mistakes run, add a pre-commit hook (or a step in synthesize-mistakes itself) that fails if global-prevention-rules.md exceeds 35 non-blank lines: `awk 'NF' mistakes/global-prevention-rules.md | wc -l | awk '$1>35{exit 1}'`. Every future mistake append must include a corresponding prune.
- **Why**: Tier 0 payload must stay bounded. The cap is already documented — enforce it mechanically.
- **Tier touched**: Tier 0 (file size gate), Tier 1 (pre-commit hook).
- **Effort**: S — one pre-commit hook line; update to synthesize-mistakes SKILL.md.
- **Files**: `mistakes/global-prevention-rules.md`, synthesize-mistakes SKILL.md, `.claude/settings.json` or pre-commit config.

**P1-C: Separate wiki-authoring rules from cross-repo engineering rules**

global-prevention-rules.md currently mixes two audiences: wiki-authoring minutiae (benchmark citation, index drift, documented-not-adopted conventions — lines 11-31) and cross-repo engineering rules (model-tier routing, test-command heuristic, judge-eval gating — lines 33-54). A code-gen agent fetching this file gets wiki-maintenance noise on every request. Splitting also directly supports P1-B by freeing lines.

- **What**: Move wiki-authoring rules to a new `mistakes/wiki-authoring-rules.md`. Load it only inside this project's CLAUDE.md via @-import. global-prevention-rules.md retains only cross-repo engineering rules.
- **Why**: Reduces per-session Tier-0 noise for non-wiki coding sessions. Gives wiki-authoring rules a proper home in this project only.
- **Tier touched**: Tier 0 (split push payload by audience).
- **Effort**: M — split the file, update CLAUDE.md @-import, verify global CLAUDE.md no longer imports the wiki-authoring half.
- **Files**: `mistakes/global-prevention-rules.md` (new split), `CLAUDE.md` (add @-import for wiki-authoring-rules.md).

**P1-D: Create wiki/concepts/model-tier-routing.md as a dedicated pull page**

The model-tier routing rule (Haiku/Sonnet/Opus decision table with agent-spawn examples) exists only in push files: global-prevention-rules.md and `~/.claude/rules/model-routing.md`. A qmd query for "model tier routing" surfaces a synthesis page, not an authoritative rule. This means the rule can only reach agents via startup push — no targeted mid-session pull fallback exists.

- **What**: Create `wiki/concepts/model-tier-routing.md` with the decision table, escalation criteria, and agent-spawn examples. Cross-link from agent-self-correction.md's deviation trigger table (it already references this query). Reduce global-prevention-rules.md's model-tier section to a one-liner pointer.
- **Why**: Gives the rule a Tier-2 pull home, allows Tier-0 to shrink, and makes mid-session re-checks possible without startup cost.
- **Tier touched**: Tier 2 (new pull page), Tier 0 (shrinks the push rule to a pointer).
- **Effort**: M — write the page, update index.md, add cross-links, prune the push file.
- **Files**: `wiki/concepts/model-tier-routing.md` (new), `index.md`, `wiki/wiki/concepts/agent-self-correction.md`.

**P1-E: Add applied-ai.md sync procedure when cited pages change (+ clear-over-compact omission)**

applied-ai.md (Tier 0, always-loaded) cites five concept pages by wikilink with inline heuristic claims. No procedure fires when those pages update their core recommendation. The context-compression page has been updated (clear-over-compact for harness/AFK workflows) but applied-ai.md is silent on it. This is the structural maintenance risk of the two-layer split.

- **What**: (1) Add a line to the wiki ingest procedure in CLAUDE.md: "If the updated page is cited in applied-ai.md, review that Tier-0 rule for staleness before closing the ingest." (2) Add clear-over-compact as a one-line note in applied-ai.md's compression bullet: "For harness/AFK workflows: clear-over-compact is community consensus — see [[concepts/context-compression]] §Clear Over Compact."
- **Why**: Closes the omission gap immediately (net-new verifier finding). The ingest procedure addition makes future drift a conscious step rather than an accident.
- **Tier touched**: Tier 0 (applied-ai.md update), procedural (CLAUDE.md ingest step).
- **Effort**: S — two targeted edits (one line to applied-ai.md, one step to CLAUDE.md ingest).
- **Files**: `claude-setup/rules/applied-ai.md`, `CLAUDE.md`.

**P1-F: Fix index.md structural defects (duplicate Syntheses header, misclassified page)**

index.md has two separate `## Syntheses` sections. Line 5 contains only pi-orchestration-architecture, isolated before the Summaries section. The second Syntheses section at line 153 ends with systems/otel-council, which is a systems/ page.

- **What**: Merge the two Syntheses sections into one (at line 153). Move pi-orchestration-architecture into it. Move systems/otel-council to the ## Systems section.
- **Why**: A reader or agent scanning the index receives a structurally incorrect taxonomy. Navigation relies on index.md correctness.
- **Tier touched**: Tier 2 (pull artifact — index.md is fetched JIT, not pushed).
- **Effort**: S — three mechanical line moves.
- **Files**: `index.md`.

**P1-G: Document patterns/ and systems/ in CLAUDE.md and GUIDE.md taxonomy**

Both CLAUDE.md and GUIDE.md define the wiki directory taxonomy as five directories (summaries/entities/concepts/comparisons/syntheses). Neither mentions patterns/ (13 pages) or systems/ (7 pages). A human following onboarding docs has no indication these 20 pages exist.

- **What**: Add patterns/ and systems/ entries to the wiki structure block in both files, with brief descriptions clarifying that patterns/ is a parallel software-engineering reference track (not derived from concepts/) and systems/ contains system-level design and architecture pages.
- **Why**: 20 pages are invisible to onboarding users. Also corrects the model/reality mismatch — patterns/ is a peer human-learning track, not the terse agent layer the audit target model implied.
- **Tier touched**: Tier 2 (pull documentation).
- **Effort**: S — four lines added across two files.
- **Files**: `CLAUDE.md`, `GUIDE.md`.

**P1-H: Fix dangling wikilink in pi-orchestration-architecture.md**

pi-orchestration-architecture.md contains `[[concepts/agent-primitive-selection]]` but the file lives at `wiki/syntheses/agent-primitive-selection.md`. This is a confirmed dangling link.

- **What**: Change `[[concepts/agent-primitive-selection]]` to `[[syntheses/agent-primitive-selection]]` in pi-orchestration-architecture.md.
- **Why**: A human following the link gets nothing. One-character path correction.
- **Tier touched**: Tier 2 (pull artifact fix).
- **Effort**: S — single-line edit.
- **Files**: `wiki/syntheses/pi-orchestration-architecture.md`.

**P1-I: Add AGENT TRIGGER blocks to the top of each patterns/ file**

Pattern files are 253–557 lines of dense prose with no agent-facing trigger clause at the head. An agent retrieving error-handling.md (328 lines) must read the entire file to locate applicable rules. The target model calls for a terse derived layer; this is the near-term approximation that costs almost nothing to maintain.

- **What**: Add a 5-10 line `## Agent Trigger` block below the frontmatter of each patterns/ file. Contents: concrete "apply when" conditions in plain language, and a one-line decision or rule of thumb. Also fix the frontmatter `type: concept` on all 13 files to `type: pattern` to correctly distinguish them from concepts/ pages.
- **Why**: Makes pattern pages immediately parseable by a retrieve-and-bail agent without requiring the full terse wiki/rules/ layer to exist first.
- **Tier touched**: Tier 2 (pull artifacts — patterns/ pages).
- **Effort**: M — 13 files, ~10 lines each; frontmatter change on all 13.
- **Files**: All files under `wiki/patterns/`.

**P1-J: Clarify threshold duplication across applied-ai.md, agent-harness.md, context-degradation.md**

The compaction thresholds (70%/80%/90%) appear verbatim in three files. Three independent update targets for one fact.

- **What**: Designate context-degradation.md as the single authoritative source. In agent-harness.md and applied-ai.md, replace inline numbers with forward references: "see [[concepts/context-degradation]] for thresholds."
- **Why**: Collapses three update targets to one, consistent with the two-layer model's intent (Tier 2 is authoritative; Tier 0 points, not duplicates).
- **Tier touched**: Tier 0 (applied-ai.md reference update), Tier 2 (agent-harness.md reference update).
- **Effort**: S — two targeted edits replacing numbers with a forward reference.
- **Files**: `claude-setup/rules/applied-ai.md`, `wiki/wiki/concepts/agent-harness.md`.

### P2 — Nice to Have

**P2-A: Add status:stub + (training data — verify) markers to unsourced concept pages**

Nine concept pages have `sources: []` and make confident empirical or architectural claims without inline qualifiers. The highest-risk instance is context-degradation.md's "Empirical threshold: ~100k tokens. Pocock claims this holds..." with no source file and no marker.

- **What**: For each of the nine pages: add `status: stub` to frontmatter and a stub footer per wiki convention, and prefix empirical claims with `(training data — verify)` inline.
- **Why**: The wiki's own epistemic discipline rule requires these markers.
- **Effort**: M — nine files. **Files**: `wiki/concepts/context-degradation.md`, `wiki/concepts/tool-design-for-agents.md`, +7 others (grep `sources: \[\]` in wiki/concepts/).

**P2-B: Implement at least two Tier-1 hook gates from agent-self-correction's table**

No PreToolUse hooks exist. The page's deviation trigger table is declarative, not enforced.

- **What**: Implement two PreToolUse hooks: (a) on Bash matching `git commit` — check whether a verification step ran; (b) on Edit — if lines changed exceeds a threshold, fire a qmd query reminder. Zero cost when not triggered.
- **Effort**: M. **Files**: `.claude/settings.json` or `.claude/settings.local.json`.

**P2-C: Add hub wikilinks for the highest-value orphan pages**

21 pages are reachable only via index.md or qmd. Agent consumers unaffected (qmd ranks by content); human link-following is broken.

- **What**: Add one outbound link from the most relevant hub for the four highest-value orphans (agent-diff-viewer, control-plane-expansion-plan, linux-setup-guide, slash-commands).
- **Effort**: S — four line additions.

**P2-D: Fix context-compression.md strategy numbering**

Strategies are numbered 1, 2, 3, 5, 4. The page has 28 inbound wikilinks — the most-referenced concept page.

- **What**: Renumber logically (1 Anchored, 2 Opaque, 3 Regenerative, 4 CCR, 5 Acon). Update index.md description.
- **Effort**: S. **Files**: `wiki/concepts/context-compression.md`, `index.md`.

**P2-E: Delete stray root-level junk files**

`/concepts/....md` (0 bytes, root-level shadow dir) and `/page-name.md` (template placeholder at repo root) pollute grep searches.

- **What**: Delete `/concepts/....md` and the empty `/concepts/` directory. Delete or move `/page-name.md` to `claude-setup/templates/`.
- **Effort**: S — two deletes.

**P2-F: Source or stub tool-design-for-agents.md**

`sources: []`, covers an important concept (dual-audience error messages, description engineering) without a cited source.

- **What**: Add `status: stub` + footer + `(training data — verify)` inline. File an ingest request for the Anthropic tool-use docs.
- **Effort**: S. **Files**: `wiki/wiki/concepts/tool-design-for-agents.md`.

## Biggest Risk of the Two-Layer Split

The central maintenance danger is silent Tier-0 drift: applied-ai.md and global-prevention-rules.md are always loaded and make specific claims derived from Tier-2 concept pages, but nothing mechanically ensures those claims stay synchronized when the source pages change. The instinct-clustering bug is a live production example — a concept was promoted months ago, the Tier-2 page was updated, log.md recorded the change, but the Tier-0 rule continued instructing incorrect labeling through every session since. The mitigation is not automation (a full derivation pipeline would be over-engineered for this wiki's scale) but procedural integration: the lint step added by P0-A makes Tier-0 staleness a visible checklist item rather than a silent assumption, and the ingest-procedure addition in P1-E makes every source update a trigger for a Tier-0 review. The risk cannot be eliminated without a sync pipeline, but it can be reduced to a narrow detection window (the time between a concepts/ update and the next lint run) with low overhead. The growth rate of global-prevention-rules.md without a mechanical cap is the secondary risk — P1-B addresses it with a pre-commit gate.

## Open Questions for Viet

1. **wiki/rules/ as a future tier**: Should we create a formal `wiki/rules/` directory as the terse derived agent layer (one decision-table file per pattern domain)? This is the target model's intended agent-consumption layer and would make the AGENT TRIGGER blocks in P1-I obsolete. Is that the roadmap, or are the TRIGGER blocks the permanent solution?

2. **patterns/ rename**: Rename `wiki/patterns/` to `wiki/engineering-ref/` to signal it is a parallel reference track, not a derived layer? The verifier considered this disruptive; P1-G opts for documentation over rename. Rename anyway, or is documentation sufficient?

3. **applied-ai.md ownership**: applied-ai.md lives in `claude-setup/rules/`, not `wiki/` — a Claude-config file that summarizes wiki content. Treat it as a wiki artifact (linted, cited, updated by ingest) or as a config file (updated by explicit operator decision only)? This decides whether P0-A's lint step applies to it automatically.

4. **context-degradation's ~100k threshold**: The page cites "Pocock claims" with no source file and no marker. Is there an original source to ingest, or should this stay a training-data assertion with explicit markers?

5. **Tier-1 hook scope**: Should the P2-B hooks be project-scoped (this repo's `.claude/settings.json`) or global (user settings.json)? And does the commit-verification hook need wiki-specific criteria or is a generic check sufficient?
