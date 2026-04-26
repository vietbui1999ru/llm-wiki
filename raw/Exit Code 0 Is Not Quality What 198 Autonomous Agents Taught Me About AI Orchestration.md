I'm a solo developer building a spatial world-building platform codenamed Project Realms — 668,000 lines of TypeScript, 14 domains, a Canvas2D game engine, a video production studio, procedural generation, tactical combat. I come from IT administration and D&D worldbuilding, not systems research. But the architecture I built to coordinate AI agents across this codebase independently converges with what Google DeepMind published in their December 2025 scaling study — and in some dimensions, goes further than anything in the current literature.

This is the story of how I broke multi-agent orchestration, what I built to fix it, and what the numbers look like after 30 autonomous campaigns and 198 agents.

## The Failure That Started Everything

**My autonomous agent completed a full build and reported success.** It was running on Claude Code with a multi-phase campaign system, building a "Show Bible" feature — entity cards for 38 characters, locations, factions. It passed typecheck. Zero warnings. Architecture validation clean. The agent exited confidently.

**When I opened it, 37 of 38 entities were invisible.** One manually-created test entity rendered. Everything the agent built was structurally correct and completely non-functional. The feature was shipped empty, and the agent had no idea.

This is the foundational failure of autonomous AI code generation. The gap between "compiles" and "works" is where real users live. Typecheck proves structure, not appearance. Exit code 0 means "no errors," not "it's good."

Every engineer who has given an AI agent real autonomy has felt some version of this moment.

I built a system so it would never happen again.

## The Quality Ladder

**The Show Bible failure drove the creation of a four-tier verification pipeline.** Each tier catches failures invisible to the tiers below:

**Tier 1: Typecheck.** Does it compile? This is where every AI coding tool stops. It catches syntax errors, type mismatches, missing imports. It does not catch invisible features, broken layouts, or empty screens.

**Tier 2: Visual Verification.** Does it render? A Playwright-based tool navigates real routes in a real browser, counts DOM elements by data-testid, and captures screenshots. If a view that should have 38 entity cards has zero, this tier catches it. 13 routes are configured for automated verification across the platform.

**Tier 3: Screenshot Gate.** Is there proof? If an agent modified .tsx files during a campaign, it cannot complete without screenshot artifacts. No screenshots, no completion. This is a hard gate, not a suggestion.

**Tier 4: Design Critique.** Is it good? Three perspectives evaluate the output — Spec Auditor (does it match requirements?), User Advocate (would a human enjoy this?), Art Director (does it match the project's visual identity?). Maximum two refinement rounds before escalating to human review, which prevents infinite loops on subjective quality.

**No other agent framework or AI coding tool has this pipeline.** Not LangGraph, not CrewAI, not AutoGen, not Devin, not Cursor. The industry is still debating whether agents should run tests at all. This system requires agents to prove they can see.

This wasn't built from theory. Every tier was added after a specific failure:

**Observatory redesign:** A Fleet session replaced 6 working components in parallel. Agents wrote new versions of CampaignTimeline, SystemMap, and VitalsStrip without ever rendering them. Every component showed "Running NaN," no timeline, no vitals. 841 lines replaced with 144 lines of broken output. This created the "layer, don't replace" rule: add new components beside working ones, verify visually, then remove the old version.

**Infinite improvement loops:** An agent kept improving the UI from the current state without defining what "done" looks like. Each iteration was incrementally better, but the process never terminated. This created the "design target, not delta" rule: define the end state before starting, converge toward a reference, not away from a baseline.

> **If you're not building agent systems, here's the short version:** the architecture is a chain of command where each level handles bigger, longer problems, and no agent ever talks to another agent at its own level. The rest of this section is the technical detail — skip to "The Numbers" if you want the results.

## The Architecture

**The system is a four-tier hierarchy.** Each tier exists because the tier below it couldn't handle the scope or duration of the work. No tier was designed speculatively — each was built when I hit a concrete ceiling.

![Image](https://pbs.twimg.com/media/HDqosREbwAEYy8a?format=jpg&name=large)

The Systems Heirarchy Visualized

**Data flow is strictly top-down.** Fleet spawns Archon-level agents. Archon delegates to Marshals. Marshals invoke Skills. No tier communicates laterally. There is no agent-to-agent messaging at the same level. This is a star topology — adding agent 5 does not increase coordination complexity for agents 1 through 4.

**This matters because of** [what DeepMind found](https://arxiv.org/abs/2512.08296)**:** unstructured multi-agent networks — "bags of agents" — amplify errors up to 17.2x. Coordination breakdowns account for 36.9% of failures. Benefits plateau at 4 concurrent agents. [Cognition and Anthropic both advise against multi-agent systems in most cases, and for most systems, they're right.](https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them)

**My system agrees.** Single agents are correct for most tasks. Multi-agent coordination exists in this system for exactly two reasons: scope partitioning (the codebase is too large for one agent's context window) and persistent state across context windows (campaigns span days, context windows don't).

How Parallel Execution Actually Works

**Each agent gets a strict directory scope and a separate git worktree.** The agents literally cannot touch each other's files. They work in isolated copies of the repository. The merge happens after completion, with a circuit breaker: one conflict pauses the wave, two conflicts stop the session.

**Between waves, a discovery relay compresses findings from Wave N and injects them into Wave N+1's context.** If Agent A in Wave 1 discovers that GenreConfig is the theme source, Agent D in Wave 2 knows that before it starts. Agents don't reinvent each other's decisions.

**Scope overlap detection prevents collisions:** two scopes overlap if any directory in one is a prefix of any directory in the other. src/domains/sandbox/ overlaps with src/domains/sandbox/dialogue/ but not with src/domains/studio/. Claims are logged, dead instances are recovered after 2 hours, and contention is tracked in a bottleneck log.

How Persistence Works

**Archon is amnesiac by design.** Its personality comes from a profile file. Its knowledge comes from capability manifests. Its current work comes from a campaign file. Everything is externalized to the filesystem.

**When context fills, Archon writes state to the campaign file and exits.** The next invocation reads the file and resumes. The campaign file is the agent's brain — feature ledgers, decision logs, phase tracking, architectural constraints. This is what allows multi-day campaigns that survive context window boundaries.

No other surveyed framework — LangGraph, CrewAI, AutoGen, Devin, Cursor, MCO — implements persistent campaign state across sessions.

## The Taste Layer

**This is the part that isn't "ahead by N months."** It's on a different axis entirely.

**Generic frameworks route by capability:** can this agent write TypeScript? Can it call this API? This system routes by quality judgment: does this output feel inhabited?

**Archon's profile encodes my aesthetic judgment** as ranked decision heuristics and a Three Words test — Inhabited, Responsive, Intentional — applied at every visual and experiential decision point. There are explicit anti-patterns: no "centered heading + subheading + CTA" hero sections, no card grids with hover scale, no generic SaaS aesthetics.

**This cannot be abstracted into a framework.** It requires deep project knowledge. The Three Words test only works because I defined what "inhabited" means for this specific platform. That's the fundamental tension: generalizability vs. effectiveness. This system chose effectiveness.

The industry will eventually build persistent campaign state. They'll build visual verification. They might build parallel coordination with scope isolation. They will not build "does this feel inhabited?" because that requires someone to define what inhabited means, and that definition is mine.

## The Numbers

**Two timelines matter here, and they tell different stories.**

**The codebase** — Tailored Realms — has been in development for 113 days. 668,310 lines of TypeScript across 3,026 files. 1,091 React components. 141 Zustand stores. 163 test files with 45,716 lines of test code. 14 domains. 26 kernel subsystems. 1,241 commits. For scale context: VS Code's core is roughly 600,000 lines of TypeScript.

**The orchestration system** — Archon, Fleet, campaigns, the coordination protocol, the visual verification ladder, the design critique pipeline, the discovery relay — has been operational for 4 days. The early building blocks (first skills in January, first hooks in February) laid groundwork. But the full system landed March 14-15, 2026. Everything that follows happened since then:

**Agents spawned:** 198 **Fleet sessions:** 32 **Waves executed:** 109 **Campaigns completed:** 30 **Features delivered:** 296 **Decisions logged:** 127 **Session completion rate:** 90.6% (29/32) **Merge conflict rate:** 3.1% (1 real conflict / 32 sessions) **Circuit breaker activations:** 0 **Parallel execution rate:** 63.3% of waves used 2+ agents **Type error trajectory:** 84 → 0 (single root-cause fix) **Work queue completion:** ~93.3% (210/225 items) **Discovery relay instances:** 15+ documented

**What those agents built in 4 days:** a tactical combat engine (118 tests), a procedural animation library (6 modules), a map generation pipeline (177 tests), a video production studio, a full TV show exploration experience, a harness observability dashboard, a surface manager layout system, and a layout kernel. Plus the research documents you're reading right now.

**The planning and documentation corpus** — campaign files, session records, capability manifests, knowledge base articles, memory files, architectural specs — totals 278,881 lines across 911 markdown files. That's nearly half the codebase. The documentation is the multiplier. It is what allows AI agents to make informed decisions without human supervision. Without it, the agents are guessing. With it, they're operating from institutional knowledge.

## The Scars

**Every protocol rule in this system traces to a real failure.** Here are the five that matter most:

**1\. Show Bible renders empty** — the origin story. An autonomous agent completed a multi-phase campaign, passed every structural check, and shipped an invisible feature. This built the entire visual verification system.

> Any autonomous system that verifies only structure will confidently ship broken work.

**2\. Agent declares done after completing 2 of 6 waves** — the agent wrote its own work plan, then executed it. The plan truncated scope. The agent genuinely believed it was done because its plan said so. The plan is the agent's brain. This created the mandatory decomposition validation step — check the plan against the original request before execution begins.

> Self-planning agents have a decomposition fidelity problem. Plan validation is the highest-leverage quality gate.

**3\. Fleet loses an entire wave of work** — worktree branches were cleaned up without being merged. Three agents' completed work vanished silently. Token cost doubled. This created the mandatory merge-before-cleanup protocol.

> Agent isolation solves the conflict problem but creates an integration problem. The merge step is delivery, not cleanup.

**4\. Two Archon instances edit the same files** — both found the same active campaign and started working. Classic TOCTOU race condition, except the actors are AI agents instead of threads. This created the claim-before-resume ordering invariant.

> Multi-agent orchestration IS distributed systems engineering. Same problems, same solutions.

**5\. 193 repeat:Infinity animations + 362 backdrop-blur instances** — no single file was the bottleneck. Each instance was individually cheap but collectively devastating to performance. The only diagnostic was a cross-file DOM audit with killswitch-based measurement.

> When AI agents generate code one file at a time, anti-patterns that are individually reasonable accumulate silently across the codebase.

The code that implements claim-before-resume is trivial. The knowledge that it is necessary is not.

These 27 postmortems are the most valuable artifacts in the system. Not the architecture. Not the code. The scars.

## What the System Cannot Do

**Three honest ceilings:**

**The scope decomposability constraint.** The 3.1% merge conflict rate is low because work was carefully scoped into non-overlapping directories. When five agents all need to modify src/kernel/types/, Fleet can't help. The real ceiling isn't agent count — it's how decomposable the work is.

**The interaction testing gap.** An overnight fleet session shipped 4 bugs that passed both typecheck and visual verification. They were only discoverable through manual interaction: long-press behavior, spawn pack mechanics, FPS degradation over time. The quality ladder reaches level 2 (appearance) and hits the wall at level 3 (behavior). Automated interaction testing is the identified next frontier.

**The taste layer is non-transferable.** "Does this feel inhabited?" works because I defined what inhabited means for this project. The taste layer is the system's strongest differentiator and its hardest limitation simultaneously. It does not generalize into a framework. That's the point — and the cost.

## The System Documented Itself

**I want to end with something that happened while preparing this material.**

I needed benchmark data, postmortem collections, a system inventory, an architecture document, and a competitive landscape analysis. Five different research tasks, each requiring different data sources — campaign files, fleet session records, coordination metadata, capability manifests, external research.

**So I used the system.** One Fleet session. Five parallel agents. Each agent mined a different slice of the project's own data. Discovery relay between waves fed the benchmark numbers and postmortem highlights into the case study outline agent in Wave 2.

**The documents you've been reading — the numbers, the failure stories, the architecture explanation — were generated by the system they describe.** Five parallel agents, worktree-isolated, producing ~15,000 words of structured analysis in a single session.

This is not a footnote. This is the proof of concept. The system that orchestrates autonomous development on a 668K-line codebase also orchestrated the research that explains itself.

> If you want to see how it works: it just showed you.