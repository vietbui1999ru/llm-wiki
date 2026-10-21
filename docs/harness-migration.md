# Agent Harness Migration (Planned)

> **Planned change, under development.** Nothing described below the "Where it stands" section has been built yet. The source of truth is `SPEC-HARNESS-MIGRATION.md` in this repo, and the executable spec (20 acceptance criteria, each with a `verify:` command) lives on the `worktree-feat+harness-orchestrator` branch of `~/repos/agent-harness`, status draft. This page is a simplified presentation; when the two disagree, the spec wins.

The agent workflow (configs, rules, skills, review gates, Pi delegation and UI bridges) grew inside `~/dotfiles`, with more pieces in `llm-wiki/claude-setup`, several sibling repos, and live config files that no repo tracks. The plan moves it into a dedicated **agent-harness** repo, then grows that repo into a **multi-machine orchestrator**: one hub on the homelab that dispatches agents to other machines over Tailscale.

Related guides: [Architecture](/guides/architecture) (how the harness fits together today) and [Standard workflow](/guides/workflows) (the spec loop the migration must not break).

---

## Why

- **Sprawl.** The workflow spans four agents (Claude Code, Codex, Pi, OpenCode), the spec loop and review gates, Pi delegation through pueue, and UI bridges in Neovim, sketchybar, herdr and claude-tui. Nobody can hold it in their head any more.
- **Coupling.** About 50 hardcoded `~/dotfiles/scripts/...` paths, many inside agent rule text, and a symlink loop between three repos.
- **No clean install.** A second machine cannot run the workflow, because part of it is untracked live state. That blocks the orchestrator, which needs remote nodes to install the harness on their own.

## Where it stands

**Step 1 is done (2026-10-22): a link-view repo.** `~/repos/agent-harness` exists locally with no remote. Nothing has moved; dotfiles is still the live source.

| Piece | Role |
|---|---|
| `links.tsv` | Manifest of 43 components: path, source, layer, status (`linked` or `owned`). Doubles as the migration checklist. |
| `scripts/sync-links` | Creates or repairs the symlinks from the manifest; `--check` reports broken ones. |
| `local-snapshots/` | Copies of 13 untracked live files (Pi and Codex config, judge scripts, herdr hooks). No credentials. |
| `docs/inventory.md` | Full inventory, data flow and coupling report. |

Every component is `linked` today. The migration flips rows to `owned`, one layer at a time.

---

## Chart 1 — Ownership before and after Phase A

Who owns each layer. Today ownership is split across three repos plus untracked files, with a loop between dotfiles and llm-wiki. After Phase A the harness owns everything a node needs; the UI bridges stay where they are for now.

```mermaid
flowchart LR
    subgraph BEFORE["Today"]
        direction TB
        DF["dotfiles<br>agent config, workflow CLIs,<br>session-band mod, bridges"]
        WK["llm-wiki/claude-setup<br>rules, skills, scripts"]
        LIVE["untracked live files<br>Pi settings + routing,<br>Codex config, herdr hooks"]
        SIB["sibling repos<br>claude-tui, agent-events,<br>pi-live-status"]
        DF -- "symlinks rules + skills" --> WK
        WK -- "docs-sync points back" --> DF
    end

    subgraph AFTER["After Phase A"]
        direction TB
        H["agent-harness<br>workflow CLIs behind PATH shim<br>single rules + skills source<br>tracked Pi + Codex config<br>harness install --profile node"]
        DF2["dotfiles<br>UI bridges, mods<br>old paths symlink into harness"]
        WK2["llm-wiki<br>knowledge only"]
        DF2 -- "links" --> H
    end

    BEFORE ==> AFTER
```

| Layer | Today | After Phase A |
|---|---|---|
| Agent config (Claude, Codex, Pi, OpenCode) | dotfiles, partly untracked | harness, tracked, no credentials |
| Rules and skills | llm-wiki `claude-setup`, linked from dotfiles | harness, one source |
| Workflow CLIs (`ac-run`, `floor-guard`, `commit-funnel`, `agent-review`) | `dotfiles/scripts`, called by hardcoded path | harness, found on `PATH` through a shim |
| Claude mods (session-band) | dotfiles | unchanged (later phase) |
| UI bridges (Neovim, sketchybar, herdr, claude-tui) | dotfiles and sibling repos | unchanged (later phase) |

## Chart 2 — Data flow today

How state moves between the agents and the UI surfaces. The migration changes where these pieces live, not how they talk; this flow must still work after every step.

```mermaid
flowchart LR
    subgraph AGENTS["Agents"]
        CC["Claude Code"]
        PI["Pi"]
        CX["Codex"]
    end

    CC -- "hooks" --> STATE["~/.claude/state"]
    CC -- "panes" --> HERDR["herdr socket"]
    PI -- "panes" --> HERDR
    PI -- "agent-review extension" --> REVIEW[".pi/agent-review"]
    PUEUE["pueue<br>Pi task queue"]

    HERDR --> BRIDGE["herdr to sketchybar bridge"]
    PUEUE --> BRIDGE
    BRIDGE --> SB["sketchybar agents item"]

    REVIEW --> CLI["agent-review CLI"]
    REVIEW --> NVIM["Neovim :AgentReview"]
    REVIEW --> BAND["session-band gates"]
    STATE --> BAND
    PUEUE --> BAND
    STATE --> EVENTS["agent-events"]

    DAEMON["claude-daemon"] --> TUI["claude-tui status"]
    TUI --> SB
    TUI --> PISTAT["Pi statusline"]
```

---

## Chart 3 — Migration order (Phase A)

Each step is gated by the same baseline. A0 records today's state as passing; every later step reruns it, and any regression blocks that step. Old `~/dotfiles/...` paths keep working through symlinks into the harness until every consumer is updated.

```mermaid
flowchart TD
    A0["A0 · Baseline gate<br>dotfiles tests: 77 Python + 23 Node<br>stow dry-run claude + pi<br>sync-links --check: 43 links<br>Claude settings parse, pi --version"]
    S1["1 · Workflow CLIs<br>harness-owned behind a PATH shim<br>removes ~50 hardcoded paths"]
    S2["2 · Rules and skills<br>single source in the harness<br>collapses the three-repo loop"]
    S3["3 · Untracked config<br>Pi + Codex config tracked, no credentials<br>fix codex + shared stow conflicts"]
    S4["4 · Node install<br>harness install --profile node<br>sets up a clean machine over SSH"]
    S5["5 · Phase B MVP-1<br>two-node ping-pong through the hub"]
    GATE{{"after every step:<br>rerun A0 checks<br>regression blocks the step"}}

    A0 --> S1 --> S2 --> S3 --> S4 --> S5
    S1 -.-> GATE
    S2 -.-> GATE
    S3 -.-> GATE
    S4 -.-> GATE
```

---

## Chart 4 — Phase B: the orchestrator

Once a node can install the harness by itself, the same Go binary, `harness`, runs in two roles. The **hub** on the homelab keeps a node registry (declared tags plus probed facts), a SQLite store of tickets and messages, an MCP server so one Claude Code session can see every agent's context, and a kanban WebUI. **Nodes** are machines reached over SSH on the tailnet; the hub places an agent on the node whose tags match the job, for example a monitoring agent on the machine with the monitoring stack.

```mermaid
flowchart TB
    YOU(["You<br>one Claude Code prompt session"])
    WEB(["Kanban WebUI<br>tailnet only"])

    subgraph TAILNET["Tailscale tailnet"]
        subgraph HUB["Hub · homelab · harness hub"]
            MCP["MCP server"]
            REG["Node registry<br>tags + probed facts"]
            DB[("SQLite<br>tickets + messages")]
            RELAY["Message relay<br>direct · group · broadcast"]
        end

        subgraph N1["Node · tag: monitoring"]
            A1["Pi agent"]
        end
        subgraph N2["Node · tag: gateway"]
            A2["Pi agent"]
        end
        GW["AI gateway"]
    end

    YOU -- "MCP" --> MCP
    WEB --> DB
    MCP --> DB
    REG -- "place by tags" --> N1
    REG -- "place by tags" --> N2
    A1 <-- "control messages" --> RELAY
    A2 <-- "control messages" --> RELAY
    RELAY --> DB
    A1 -- "per-node virtual key" --> GW
    A2 -- "per-node virtual key" --> GW
```

Design boundaries:

- **Control plane only.** The hub relays agent and orchestrator messages. Agents may *set up* data links, such as shipping gateway logs to the monitoring machine, but the harness never carries that traffic.
- **No provider keys on nodes.** Nodes call the AI gateway with per-node virtual keys the hub can revoke.
- **Tailnet only.** The WebUI is single-user and not exposed publicly.
- **No auto-rescheduling.** If a node fails mid-task, the ticket is parked and you are notified. Infrastructure work has side effects, so it is never silently re-run elsewhere.

## Chart 5 — MVP-1: two-node ping-pong

The first end-to-end proof. Two Pi agents on two different nodes exchange messages only through the hub, and the result lands on the ticket. MVP-2, the monitoring scenario, gets its own spec.

```mermaid
sequenceDiagram
    participant You
    participant Hub as Hub (homelab)
    participant A as Pi on node A
    participant B as Pi on node B

    You->>Hub: create ticket "ping-pong"
    Hub->>A: dispatch over SSH (tags match)
    Hub->>B: dispatch over SSH (tags match)
    A->>Hub: message to B: ping
    Hub->>B: relay ping
    B->>Hub: message to A: pong
    Hub->>A: relay pong
    A->>Hub: report done
    Hub->>You: ticket updated, visible in WebUI and MCP
    Note over Hub,B: on reconnect, missed messages are replayed<br>a node that misses heartbeats parks the ticket
```

---

## How "done" will be checked

The agent-harness spec has 20 acceptance criteria. Grouped:

| Criteria | Scope | How checked |
|---|---|---|
| AC-1 to AC-5 | Baseline: dotfiles tests, stow dry-run, harness links, Claude settings, Pi CLI | Commands, now and after every step |
| AC-6 to AC-10 | Phase A: no hardcoded script paths, CLIs behind the shim, rules and skills owned, config tracked without credentials, node install | Commands; node install checked by hand on a second machine |
| AC-11 to AC-18 | Phase B units: message relay, replay after reconnect, heartbeat timeout, tag placement, guarded `--dangerously-skip`, MCP tool list, in-process ping-pong | Go tests |
| AC-19 to AC-20 | Phase B on real hardware: ping-pong across two tailnet nodes, WebUI reachable only on the tailnet | By hand |

## Risks and open items

- **Hidden consumers of old paths.** Rule text and one test assert `~/dotfiles/scripts/ac-run`. The compatibility symlinks must stay until a search shows zero consumers.
- **Relative symlinks inside dotfiles** depend on directory depth and can break when a package moves.
- **Untracked state.** `pi-live-status` is not under git, and Pi, Codex, judge and herdr files exist only as snapshots.
- **Stale pieces** to delete during the move: `claude-setup/settings.json`, `install-claude-symlink.sh`, a dangling `~/.local/bin/ao`.
- **Likely bug found during the inventory:** `pi-status.lua` reads `~/.pi/status` while the writer uses `<cwd>/.pi/status`.
- **Open:** the spec is still a draft awaiting approval; the agent-harness repo has no remote yet; the UI-bridge move is unscheduled.
