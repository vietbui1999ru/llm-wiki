---
title: "Builder.io Patterns for Commandr + DiffViewer"
type: synthesis
tags: [builderio, agent-native, commandr, diffviewer, control-plane, visual-plan, visual-recap, action-registry]
sources:
  - "raw/BuilderIOagent-native A framework for building agent-native applications. 1.md"
  - "raw/BuilderIOskills Skills for coding agents 1.md"
  - "Commandr/protocol/SPEC.md v0.3"
  - "Commandr/docs/plans/PLAN-control-plane-runner-packages.md"
  - "DiffViewer/docs/V0.7-CONTROL-PLANE-COCKPIT-PLAN.md"
created: 2026-06-19
updated: 2026-06-19
---

# Builder.io Patterns for Commandr + DiffViewer

Builder.io's Agent-Native and Skills repos help our workflow in two concrete ways:

1. **Shared action vocabulary** — humans and agents should invoke the same validated actions, whether the trigger is a UI click, tool call, CLI command, MCP call, or runner adapter.
2. **Inspectable visual artifacts** — plans and recaps should become durable review packages, not chat walls.

They do **not** replace [[entities/commandr]] or its `.agents/` bus. Commandr remains L3 source of truth. DiffViewer remains L5 projection and action UI. Builder.io patterns shape the seams between them.

---

## Layer Mapping

| Builder.io idea | Our layer | Concrete use |
|---|---|---|
| Agent-Native `defineAction` | L5 action registry + L3 command wrappers | Define one action schema for UI clicks and agent proposals. Route lifecycle actions to Commandr commands. |
| Shared SQL-backed state | DiffViewer/Tauri local cache only | Use SQLite for fast UI state and audit projection, but rebuild from `.agents/` and artifacts. |
| `/visual-plan` | L4/L5 planning artifact | Generate a pre-code plan package with file map, diagrams, open questions, approval checklist. |
| `/visual-recap` | L5 review package | Generate end-of-task recap with diffs, screenshots, tests, council verdict, risks. |
| `/agent-watchdog` | Review workflow | Audit another runner/session from bus events, sidecars, artifacts, and git diff. |
| `/plan-arbiter` | Multi-agent planning gate | Compare competing plans, choose one, write the decision into the task packet or plan artifact. |
| `/efficient-frontier` | Model routing | Keep expensive models on judgment; use cheaper runners for scans, edits, logs, and artifact generation. |
| `/read-the-damn-docs` | L4 retrieval discipline | Require qmd/context7/raw-source pass before implementing external integrations. |

---

## Commandr Contract

Commandr should expose action-like verbs, but every bus mutation must still map to SPEC v0.3 or a future conformance-backed SPEC change.

| Action | Current Commandr side effect | Status |
|---|---|---|
| `task.claim` | `bin/claim`; move `inbox/` → `claimed/`; append `task_claimed` | Live SPEC |
| `task.progress` | `bin/progress`; append neutral `task_progress` | Live SPEC |
| `task.complete` | `bin/complete`; move `claimed/` → `done/`; append `task_complete` | Live SPEC |
| `task.fail` | Supervisor appends `task_failed`; normal completion with unmet criteria uses `bin/complete <claimed-path> fail` | Live SPEC |
| `annotation.create` | `bin/annotate-write`; write `.agents/annotations/...`; append `task_annotation` | Live SPEC |
| `approval.approve` | Write `.agents/approvals/<task>.approved` | Live SPEC |
| `approval.deny` | Write nothing; optional neutral `task_progress` note | Live SPEC behavior |
| `council.run` | `bin/council`; write `.agents/council/<task>.json`; append `council_verdict` | Live SPEC |
| `approval.request` | DiffViewer/local runner artifact only; no `.pending` file | Non-SPEC local projection |
| `artifact.create` | `.diffviewer/artifacts/<task>/...` or runner workspace artifact | Non-SPEC local projection |
| `review.generate` | DiffViewer creates review package from bus + sidecars + git diff | Non-SPEC local projection |
| `runner.start` | Runner adapter creates session/worktree and then uses bus commands | Non-SPEC adapter action |

Rule: `approval_requested`, `artifact_created`, `.agents/approvals/*.pending`, `.denied`, and runner workspace paths stay outside SPEC until DiffViewer has a real consumer and Commandr adds conformance checks.

---

## DiffViewer Contract

DiffViewer should implement the Builder.io pattern as a local action dispatcher:

```ts
type CockpitAction = {
  name: string;
  schema: unknown;
  actor: "human" | "agent" | "system";
  risk: "low" | "medium" | "high";
  requiresApproval: boolean;
  handler: "commandr" | "diffviewer" | "runner";
  auditEvent: "local" | "commandr" | "none";
};
```

Human clicks and agent proposals enter the same dispatcher. The dispatcher validates input, classifies risk, checks approval policy, then calls the right handler. Agent text never jumps directly to side effects.

DiffViewer-owned artifacts should live outside `.agents/`, for example:

```text
.diffviewer/artifacts/<task-id>/
  plan.md
  review-package.json
  review-package.md
  screenshots/
  lsp-summary.json
  command-log-summary.json
```

These artifacts are regenerated projections. Losing them should not corrupt task lifecycle.

---

## Visual Plan Package

Builder.io `/visual-plan` maps to a pre-implementation package rendered by DiffViewer.

Inputs:

| Source | Data |
|---|---|
| Commandr packet | Goal, acceptance criteria, files to touch, non-goals |
| qmd / llm-wiki | Relevant patterns, prior decisions, docs |
| CGC / CodeBoarding | file map, architecture graph, blast radius |
| Human annotations | constraints, approvals, steer notes |

Output: `.diffviewer/artifacts/<task>/plan.md`.

Required sections:

| Section | Purpose |
|---|---|
| Scope | One sentence on what will change |
| File map | Files likely touched and why |
| Action plan | Ordered implementation steps |
| Risk table | risky files/actions and mitigation |
| Verification gates | typecheck, tests, visual, screenshot, council, approval |
| Open questions | only blockers, not routine ambiguity |
| Approval checklist | what human approves before code starts |

Commandr relationship: the plan is **not** the task packet. The packet remains the work contract; the plan is a rendered aid and can be referenced from `task_progress` as a neutral note.

---

## Visual Recap / Review Package

Builder.io `/visual-recap` maps directly to DiffViewer's end-of-task review package.

Inputs:

| Source | Data |
|---|---|
| Git diff | changed files, hunks, stats |
| `.agents/events.jsonl` | lifecycle, progress, annotations, council verdict |
| `.agents/council/<task>.json` | vote reasons and final verdict |
| `.agents/approvals/<task>.approved` | approval state |
| `.diffviewer/turns/` | per-turn file edits and sidecars |
| Runner workspace | logs, screenshots, diagnostics, command summaries |
| LSP/CodeBoarding | diagnostics, symbols, architecture impact |

Output: `.diffviewer/artifacts/<task>/review-package.json` plus a rendered Markdown/MDX view.

Minimal JSON shape:

```json
{
  "task": "TASK-001",
  "status": "review",
  "summary": "One sentence outcome.",
  "changedFiles": [{ "path": "src/auth.ts", "kind": "edit", "risk": "medium" }],
  "verification": [{ "name": "tests", "status": "pass", "evidence": "npm test" }],
  "approvals": { "approved": false, "tokenPath": ".agents/approvals/TASK-001.approved" },
  "council": { "verdict": "PASS", "abstentions": 0 },
  "artifacts": [{ "type": "screenshot", "path": "screenshots/login.png" }],
  "residualRisks": ["Manual staging deploy not run"]
}
```

DiffViewer can render this as cards: overview, file map, risk, verification, screenshots, logs, approvals, council, residual risks.

---

## Workflow

```text
1. Human or agent creates Commandr packet
2. DiffViewer action `review.generatePlan` creates visual plan artifact
3. Human approves direction via annotation or task approval workflow
4. Runner claims task through Commandr
5. Runner emits neutral progress and local artifacts
6. DiffViewer watches `.agents/`, sidecars, and artifact dirs
7. Runner completes/fails task through Commandr
8. DiffViewer action `review.generateRecap` builds visual recap
9. Council runs as advisory quality gate
10. Human approves commit through existing `.approved` token gate
```

This preserves the thin waist: Commandr records lifecycle; DiffViewer records UI/action/audit projections; runners own private execution state.

---

## Implementation Slices

### Slice 1: No-SPEC-Change Review Package

Build in DiffViewer only.

Acceptance criteria:

| Requirement | Check |
|---|---|
| Reads Commandr bus and git diff | No writes to `.agents/` except existing approval/annotation paths |
| Writes `.diffviewer/artifacts/<task>/review-package.json` | Regenerable and ignored from git |
| Renders a review package card | Includes diff stats, tests, council, approval state |
| Emits optional `task_progress` | One-line neutral note only |

### Slice 2: Action Registry

Add a local dispatcher in DiffViewer.

Acceptance criteria:

| Requirement | Check |
|---|---|
| Every action has schema/risk/handler | No ad-hoc side-effect endpoints |
| Agent proposals use same path as UI clicks | Invalid schema returns structured error |
| Commandr mutations shell to `bin/` tools | No raw bus file manipulation from UI |

### Slice 3: Builder-Style Skills

Package workflows as reusable skills consumed by OpenCode/Claude/Pi/omp.

Candidate skills:

| Skill | Output |
|---|---|
| `commandr-task` | claim/progress/complete discipline |
| `visual-plan` | plan artifact for DiffViewer |
| `visual-recap` | review package artifact |
| `agent-watchdog` | audit of another runner/session |
| `bus-debugger` | SPEC conformance and stale-state diagnosis |

Skill rule: a skill may call Commandr commands or write DiffViewer-local artifacts. It must not invent bus files or parse runner-private state as authority.

### Slice 4: Future SPEC Artifact References

Only after Slice 1 proves real UI value, consider a Commandr SPEC v0.4 artifact event.

Candidate event shape:

```json
{"ts":"<ISO8601>","event":"artifact_ref","task":"TASK-001","kind":"review-package","path":".diffviewer/artifacts/TASK-001/review-package.json","summary":"Review package generated"}
```

This needs SPEC text, conformance checks, and a migration decision. Until then, artifact references stay local or as human-readable `task_progress` notes.

---

## Non-Goals

- Do not replace `.agents/` with Agent-Native SQL state.
- Do not add `.agents/approvals/*.pending` or denial files.
- Do not emit non-SPEC events from Commandr.
- Do not store runner transcripts or LSP caches on the bus.
- Do not make DiffViewer authoritative for lifecycle.
- Do not adopt Builder.io templates wholesale before the local action/artifact seam works.

---

## Related Pages

- [[summaries/builderio-agent-native]] — source summary for shared actions and app surfaces.
- [[summaries/builderio-skills]] — source summary for visual-plan, visual-recap, watchdog, arbiter, efficient-frontier.
- [[entities/commandr]] — L3 bus and SPEC boundary.
- [[entities/diffviewer]] — L5 UI and Tauri cockpit direction.
- [[syntheses/desktop-control-plane]] — big-picture 5-layer control plane.
- [[concepts/agent-skills]] — portable `SKILL.md` packaging pattern.
- [[concepts/tool-design-for-agents]] — schemas and recovery-friendly tool contracts.
