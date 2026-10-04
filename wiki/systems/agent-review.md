---
title: "agent-review: Per-Run Neovim Review Gate for Pi"
type: concept
tags: [agent-review, neovim, pi, human-in-the-loop, code-review, diffview, gitsigns, dotfiles]
sources: ["dotfiles docs/workflows/agent-review.md", "dotfiles docs/workflows/ai-workflow-consolidation.md", "dotfiles docs/workflows/agent-review-handoff.md", "dotfiles scripts/agent-review, scripts/trial-usage.sh", "dotfiles pi/.pi/agent/extensions/agent-review/index.ts", "dotfiles nvim/.config/nvim/lua/custom/agent_review.lua"]
created: 2026-10-04
updated: 2026-10-04
---

# agent-review: Per-Run Neovim Review Gate for Pi

A human-in-the-loop review of the changes a Pi agent made, done **once per Pi run** (not per edit) inside Neovim, using `diffview.nvim` for the diff, `gitsigns.nvim` for hunk navigation and reset, and real buffers for edits. It lives in the `~/dotfiles` repo. Facts below are from the dotfiles docs and source as of 2026-10-04 (dotfiles `main` at `37939d3`); items I could not verify are marked *(inferred)*.

**Scope: Pi only.** Claude Code keeps its built-in edit approval. No Claude, Codex or OpenCode hook calls this gate (searched `claude/`, `codex/`, `opencode/` in dotfiles; only prose mentions exist, e.g. in the `delegate-pi` skill: pane mode does not bypass agent-review).

## Why it exists

It is the **trial replacement** for the older per-edit gate, [[entities/diffviewer]]'s `pi-diff-review`, which reviews each edit in its own tmux pane and cannot open Neovim. The consolidation work measured that gate at 249 human decisions (146 dotfiles, 103 resume-gen) between 2026-07-28 and 2026-09-15, and decided to keep it as the gate until a Neovim per-run alternative could be compared. The even older `pi-review-gate.ts` (sandbox/batch gate with auto-apply, 4 batches ever used) is slated for deletion; agent-review reuses nothing from it. The rule is that **two review gates are never active at once**: `pi-diff-review` is currently disabled (symlinked into `extensions-available/`, disabled since 2026-09-18) and agent-review is enabled.

## Components

| Piece | Location (in dotfiles) | Role |
|---|---|---|
| Mode CLI | `scripts/agent-review` (python3, not on PATH) | `mode on\|off\|status`; writes `.pi/agent-review/mode.json` atomically. No mode file means **on** (fail closed). |
| Pi extension | `pi/.pi/agent/extensions/agent-review/index.ts` | Blocks human input while a review is pending, snapshots before/after each run, writes pending records, applies decisions. Command `/review [skip <id>]`. Listens to `post-run-verifier:settled`. |
| Neovim module | `nvim/.config/nvim/lua/custom/agent_review.lua` | `:AgentReview`, `:AgentReviewNote`, `:AgentReviewReject[!]`, `:AgentReviewDone`, plus debug/status/clear/verbose commands. Keymaps `<leader>ar` open, `an` note, `aD` done, `aR` reject file. |
| Test harness | `scripts/agent-review-nvim-test.lua`, `*.test.ts` beside the extension | Per the docs: 32 bun tests + 43 nvim checks, 0 failed (as of 2026-09). |
| Trial tooling | `scripts/trial-usage.sh`, `claude/.claude/hooks/trial-expiry.sh` | Counts usage; the SessionStart hook reports expiry and never deletes. |

State lives per repo root under `.pi/agent-review/` (gitignored via the `agent-workflow` template): `mode.json`, `pending/<uuid>.json`, `decisions/<uuid>.json`, plus git refs `refs/agent-review/<id>/{base,end}`.

## Flow

1. **Trigger.** A human `input` with mode on and no active run takes a *base snapshot*. Any further input while a review is pending is refused with a hint to `/review skip <id>`.
2. **Run ends.** After the post-run verifier settles (or a 30 s fallback timer), an *end snapshot* is taken. Snapshots are git **trees** built from a temporary index (`git add -A`, exclude `.pi`, `write-tree`). If end tree equals base tree, nothing to review. Otherwise a pending record is written and Pi shows "review pending, `:AgentReview` in nvim". If `mode.json` changed during the run, the record is marked `tamper` and mode is forced on. Snapshot errors also produce a pending record (fail closed). In print mode (`pi -p`) it sets exit code 1 and never auto-accepts.
3. **Review in Neovim.** `:AgentReview` opens the oldest valid pending record in diffview scoped to the run's files and sets the gitsigns base. Accept = leave the hunk; reject hunk = `:Gitsigns reset_hunk` (tracked files only); reject file = `:AgentReviewReject` (restores the base version or deletes a file the run created; refuses if the file changed since the end snapshot unless `!`); edit = edit the buffer; `:AgentReviewNote` attaches `{file, line, note}`.
4. **`:AgentReviewDone`.** Takes a final snapshot, builds `patch = git diff endTree finalTree` over the run's files, marks each file `accepted` or `changed`, and writes `decisions/<id>.json` atomically. Neovim never deletes the pending record.
5. **Pi applies the decision.** It watches `decisions/`, claims by renaming pending to `.processing`, validates shape, run id, end tree and that `finalTree` matches a fresh snapshot, then deletes the record and refs. Only if there is a patch, notes, a skip or changed files does it send **one** follow-up message pointing at the decision file ("do not reintroduce rejected changes"). That follow-up is itself a new reviewed run. An all-accepted review with no notes sends nothing.

## Trial status (2026-10-04)

The spec defines a trial of agent-review against `pi-diff-review`: expiry 30 days after the first decided review, usage compared by counting `decisions/*.json` against `pi-diff-review`'s `decisions.jsonl`, survivor chosen with `scripts/trial-usage.sh`. **The trial entry has not been registered:** `~/.claude/trial/manifest.json` is `[]`, so no expiry date exists and the expiry hook has nothing to report *(inferred consequence)*. On disk there is one decision (a skip, empty), so the earlier decision files were evidently cleared *(inferred)*. No survivor decision has been recorded.

## Known limits and gaps

- **Post-hoc review:** the verifier and tests run on unreviewed code before the human sees it; shared working tree; no sandbox. The tamper check is not a security boundary, and an agent running in herdr can type `/review skip` into its own pane. The spec says to document these, not solve them.
- **Deferred to v2 (not implemented):** override shortcut, 7-day ref pruning, multi-session guarantees beyond claim-by-rename.
- **Manual verification still open per the spec:** diffview render and `reset_hunk` correctness, a live round trip, subdirectory repo root, `pi-diff-review` non-activation, tamper flag live.
- **agent-flow integration** (a `review` state in the status pill, escalation, per-phase `Review: on|off`) is specified but no implementation was found in the sketchybar bridge *(not examined in detail)*.
- The `which-key` label for `<leader>aR` is missing from `init.lua` (the keymap carries its own description).

## Related

- [[entities/diffviewer]]: the per-edit gate this trials against (now disabled for Pi).
- [[entities/pi-agent]]: the agent harness being reviewed.
- [[syntheses/pi-orchestration-architecture]]: the earlier design that named `pi-diff-review` as the gate.
- [[syntheses/desktop-control-plane]]: the 5-layer toolchain DiffViewer sits in.
- [[systems/dotfiles-agent-harness-layout]]: where these pieces live and how they are provisioned.
