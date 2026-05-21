---
title: "GitHub Issue as Handoff Artifact"
type: concept
tags: [agent-workflow, handoff, github, issue-tracker, orchestration, task-queue, multi-agent]
sources: ["handoff is my new favourite skill.md"]
created: 2026-05-21
updated: 2026-05-21
status: stub
---

# GitHub Issue as Handoff Artifact

A variation of the `/handoff` skill where the handoff document is published as a GitHub issue instead of a temp-dir markdown file. Bridges `/handoff` (context forking), `/to-issues` (work decomposition), and [[concepts/shared-task-queue]] (agent dispatch).

**Recommendation: use temp file by default. Upgrade to issue only when persistence, team visibility, or autonomous dispatch is needed.** The operational cost of CI setup is real; the temp-file form is zero-infra. See [When to Use Each Form](#when-to-use-each-form).

---

## Core Idea

The original `/handoff` skill saves to `$TMPDIR` — ephemeral by design. Replacing the file write with:

```bash
gh issue create \
  --title "Handoff: <purpose>" \
  --body "<handoff doc>" \
  --label "agent-handoff"
```

turns the handoff doc into a persistent, shareable, trackable artifact. The returned issue URL is passed to the next agent session as its kickoff.

## Handoff Issue Body Format

The issue body must follow the same structure as the original `/handoff` skill output — not a freeform "context dump." Required sections:

```markdown
## Purpose
<one sentence: what the next session must accomplish>

## Context
<minimum context needed; use file paths / issue links as pointers, not copied content>

## Suggested skills
- /grill-with-docs | /tdd | /diagnose | etc.

## Acceptance signal
<what "done" looks like for the receiving agent>

## Sensitive data
[REDACTED — strip all API keys, passwords, PII before publishing]
```

Pointers over copy-paste: if the relevant context lives in a PR, file, or existing issue — link it. The issue body should be a navigation map, not a transcript.

---

## Return Handoff (Multi-Hop)

The original `/handoff` skill supports a `grilling → prototype → return handoff → grilling` pattern. With GitHub issues, the return handoff is a **comment on the original issue**, not a new issue:

```bash
gh issue comment <issue-number> \
  --body "<return handoff doc: learnings from prototype session>"
```

This makes the issue a thread — each agent hop appends a comment, preserving the full reasoning chain without creating N separate issues. The originating session resumes by reading the issue's comment history:

```bash
gh issue view <issue-number> --comments
```

---

## Tradeoffs vs. Temp File

| Property | `$TMPDIR/handoff.md` | GitHub Issue |
|---|---|---|
| Lifetime | OS-controlled (ephemeral) | Persistent until closed |
| Team visibility | Local machine only | Shared with team |
| Traceability | None | Links to PRs, comments, labels |
| Multi-hop handoff | File gets overwritten | Agent comments per hop |
| Agent dispatch | Manual paste | Webhook → CI (requires setup) |
| blocked-by references | Not possible | Issue ID usable in other issues |
| Operational cost | Zero | CI runner + CLI auth required |

---

## Lean-Session Interaction

[[syntheses/lean-agentic-workflow]] uses `lean-session` to write `.agents/checkpoint.md` on every idle/compaction event. When `/handoff` fires mid-session, the checkpoint already contains current task state (git state, task list, changed files).

The handoff issue body should reference the checkpoint path as a pointer:

```markdown
## Context
Checkpoint at: .agents/checkpoint.md (read at session start for full task state)
Active task: <task summary>
...
```

The receiving agent loads the checkpoint at startup before reading the issue body. This avoids re-serializing state that lean-session already captured.

**Open question**: if the original session continues after handoff (the whole point), the checkpoint will be overwritten by subsequent idle events. The receiving agent should read the checkpoint *immediately at session start*, not lazily. This is unverified — needs real implementation experience.

---

## Synthesis with /to-issues

`/to-issues` decomposes a PRD into vertical-slice GitHub issues for parallel agent execution. A handoff issue sits one level above this:

1. Grilling session surfaces out-of-scope task → `/handoff` → creates issue #X (`agent-handoff` label)
2. Receiving agent reads issue #X → if task is multi-session, runs `/to-issues` → child issues created with `## Parent: #X`
3. Child issues land in `.agents/inbox/` as task files (see materialization below)
4. Parallel agents claim from inbox; close child issues on completion; comment resolution on #X

The handoff issue becomes the parent in the `/to-issues` template's `## Parent` field.

---

## Synthesis with Shared Task Queue

A handoff issue can be materialized into `.agents/inbox/` using the task file format required by [[concepts/shared-task-queue]]:

```bash
# Materialize issue into .agents/inbox/ with correct task file format
ISSUE_NUMBER=<n>
TITLE=$(gh issue view $ISSUE_NUMBER --json title -q .title)
BODY=$(gh issue view $ISSUE_NUMBER --json body -q .body)
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/-$//')

cat > ".agents/inbox/TASK-${ISSUE_NUMBER}.md" <<EOF
---
id: TASK-${ISSUE_NUMBER}
type: implementation
blocking: []
blocked-by: []
scope: (set by receiving agent)
---

# ${TITLE}

## Context
GitHub issue: #${ISSUE_NUMBER}
$(gh issue view $ISSUE_NUMBER --comments | tail -20)

## Acceptance criteria
(derived from issue body — receiving agent must parse)

## Do not touch
(receiving agent sets based on active worktrees)
EOF
```

Note: `scope` and `do-not-touch` fields must be filled by the receiving agent at claim time — they can't be known at materialization. The task file is a skeleton; the agent completes it before starting work.

---

## Auto-Dispatch via GitHub Actions

**Operational requirement: not zero-infra.** The dispatch job needs:
- A self-hosted runner with Claude Code CLI installed and authenticated (`ANTHROPIC_API_KEY` secret)
- `gh` CLI available on the runner
- The runner must have repo write access to push commits back

```yaml
on:
  issues:
    types: [labeled]

jobs:
  dispatch:
    if: github.event.label.name == 'agent-handoff'
    runs-on: self-hosted  # NOT ubuntu-latest — CC CLI not available on GitHub-hosted runners
    steps:
      - uses: actions/checkout@v4
      - name: Materialize task file
        run: |
          ISSUE=${{ github.event.issue.number }}
          BODY=$(gh issue view $ISSUE --json body -q .body)
          # Write to inbox using the format above
          # Then claim + run agent
          claude --print "$(cat .agents/inbox/TASK-${ISSUE}.md)"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      - name: Comment result on issue
        if: always()
        run: |
          gh issue comment ${{ github.event.issue.number }} \
            --body "Agent session complete. See commit: $(git rev-parse HEAD)"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Simpler alternative**: skip Actions entirely. Receiving agent is started manually with `gh issue view <n>` as the initial prompt. Auto-dispatch is useful only when the pipeline is fully trusted and the runner is already maintained.

---

## When to Use Each Form

| Scenario | Use |
|---|---|
| Short focused task, one session, solo | `$TMPDIR/handoff.md` (original skill, zero infra) |
| Task needs team review before starting | GitHub issue (human can comment/approve first) |
| Multi-hop: prototype returns learnings | GitHub issue with comment-back |
| Task may expand to multi-session work | GitHub issue → `/to-issues` decomposition |
| Fully autonomous dispatch | GitHub issue + Actions (only if self-hosted runner exists) |
| Cross-agent adversarial review | GitHub issue (agent-agnostic; readable by Codex/Copilot) |

---

## Open Questions (Needs Implementation Experience)

- Does lean-session checkpoint survive long enough for the receiving agent to read it? Depends on how fast the original session continues after handoff.
- What's the right granularity for `agent-handoff` vs. `needs-triage` labels? Can an issue carry both?
- Return-handoff via comment: does the original session need to poll for comments, or is the URL enough for a human to close the loop?

---

## Related Pages

- [[summaries/mattpoccock-handoff-skill]] — /handoff skill design; temp-file form; grilling→prototype→back pattern
- [[summaries/mattpocockskills]] — /to-issues: PRD → vertical-slice issues; /to-prd: session → issue
- [[concepts/shared-task-queue]] — atomic `.agents/inbox/` claim protocol; task file format spec
- [[syntheses/lean-agentic-workflow]] — lean-session checkpoint; full grill→PRD→AFK loop
- [[concepts/agent-harness]] — broader orchestration harness context

*Stub — expand when a dedicated source is ingested.*
