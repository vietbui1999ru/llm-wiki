---
title: "r/ExperiencedDevs: What Do 'Use an AI Agent Live' Coding Interviews Evaluate?"
type: summary
tags: [ai-coding-agents, interviews, evaluation, agent-skills, agent-subagents, hiring]
sources: ["raw/What are interviewers actually looking for in a \"use an AI agent live\" coding interview?.md"]
created: 2026-09-11
updated: 2026-09-11
---

# What Do "Use an AI Agent Live" Coding Interviews Evaluate?

Source: [r/ExperiencedDevs thread, 2026-08-08](https://reddit.com/r/ExperiencedDevs/comments/1vivvyh/)

OP asked what separates strong from weak signal in a live-coding interview where a candidate builds a React spec using an AI agent of their choice (Claude Code, Cursor, etc.) while two engineers observe. This is a mixed-signal community thread, not a study — treat every claim below as one practitioner's stated interview rubric, not a validated standard. `(anecdotal, unverified)` applies throughout.

---

## No industry consensus — the meta-finding

The strongest and most-upvoted thread of the discussion is that there is **no standard rubric**. dashingThroughSnow12 (163 pts) lists contradictory failure modes reported across companies: rejected for using AI too much, too little, too-detailed prompts, too-terse prompts, iterating too much, iterating too little. Several commenters (TheNinjaFennec, dpekkle) attribute this to the format being new industry-wide — the replacement for LeetCode-style rounds hasn't converged yet. A few (ADDSquirell69, rochakgupta) treat the format itself as a red flag about the company's engineering maturity.

## The one moment that actually carries signal

ItaySela's answer (126 pts, most-discussed subthread) argues two engineers in an hour will not read the diff carefully — the deliverable itself carries less signal than candidates assume. The high-information moment is when the agent hands back something **plausible and wrong**. Practical implications:
- Specs handed out in these interviews reliably contain an ambiguity. Name it out loud and state your resolution *before* prompting — this is the one thing an interviewer can't reconstruct from reading code afterward.
- The agent's "thinking" time is not dead air — it's the only unstructured stretch in the hour. State your acceptance/rejection criteria *before* the output lands, not after, so the interviewer can verify you had a bar rather than making peace with whatever appeared.

## Convergent themes across independent company reports

Several commenters describing their own company's actual rubric (Mundane-Charge-1900, 08148694, youngggggg, j1knra, Financial-Grass6753, Seylox, Cold_Aioli478) converge on the same handful of axes despite no shared standard:

1. **Requirement clarification before prompting** — ask questions, name ambiguities (esp. outlier/invalid-input handling), don't one-shot a mega-prompt without first scoping.
2. **Critical review, not blind acceptance** — the single most-cited red flag is "looks good enough" without inspecting the diff. Financial-Grass6753 flags ignored "slop signals" (absent types, needless casts, duplication) as disqualifying regardless of prompt quality.
3. **Scope discipline** — did the candidate let the agent over- or under-build relative to the actual ask.
4. **Willingness to redirect** — as the solution evolves, does the candidate re-steer the agent or tunnel-vision on the first output.
5. **Tests and validation** — expectation is usually "a couple of E2E happy-path tests," not full coverage; pre-installed Playwright/headless Chrome buys time.
6. **Narration** — verbal reasoning throughout is treated as equal-weight to the end result, not secondary to it.
7. **Post-hoc explainability** — 08148694's method: take the agent away after and make the candidate discuss the code, decisions, and trade-offs *without* assistance. This is presented as the actual gate; the live session is just the setup for it.

## DrCaret2's adoption-spectrum framing (8 pts, structurally distinct answer)

Instead of scoring the single session, DrCaret2 says the interview is used to locate the candidate on an adoption curve: never tried it → copy-paste from chat → "trusted partner" (reviews every PR, steady velocity, picks up previously-missed small tasks) → "auto mode for everything" (feels more productive but often has silently high rework — their org's audit found 60% of one week's tokens were pure waste) → "Claude army" zealot who ships without understanding the system. The interviewer's stated goal is fit with the team's current AI-usage norms and curiosity/non-dogmatism, not a single correct usage pattern.

## Contested points — no resolution in-thread

- **Plan mode**: 08148694 rewards "iterate on the plan mode plan"; tr14l calls plan mode "far too weak," arguing real planning needs a separate session with docs/diagrams/decision log. foonek claims plan mode silently uses a weaker model and prefers running the top model in analyze-only mode instead. `(unverified per-vendor implementation claim)`.
- **Subagents**: GND52/DomBrown2406 frame subagent-based review (including cross-model review, e.g. a second vendor's agent reviewing the first's output) as a strong signal; the_pwnererXx calls manual subagent invocation itself a red flag ("the agent should decide that"); several note interview-scale tasks rarely justify subagents at all, making this axis hard to demonstrate regardless of skill.
- **Bring your own CLAUDE.md/RULES.md/skills**: nullbyte420 and dsound advocate a pre-written rules file (line-length caps, composition over inheritance, TDD, linter config) as prep; dpekkle and WhenSummerIsGone counter that a generic file eats interview time and modern default agent behavior may not need "write nice code" instructions anymore. Consensus fragment: *if* you bring prior setup, you must be able to justify each rule yourself — "it's what the superpowers plugin does" is treated as a non-answer.
- **Whose subscription pays**: aj0413 and Reasonable_Glass2501 raise it as a real unresolved logistics question; The_Northern_Light says expecting to use the *interviewer's personal* subscription is an instant reject.

## Practical heuristics extracted from the thread

1. Surface the spec's ambiguity and your resolution out loud before your first prompt — this is the one artifact the diff can't provide afterward.
2. Treat agent "thinking" time as interview time: state acceptance criteria before output lands, not as a reaction to it.
3. Never present agent output as done without visibly inspecting it (types, duplication, edge cases) — silence here is the most commonly cited failure.
4. Be ready to explain your decisions and the agent's decisions with the agent taken away — several interviewers treat this as the real gate, not the live build.
5. If bringing a personal CLAUDE.md/skills setup, be ready to justify every rule in your own words, not by reference to the tool that generated it.
6. Don't assume subagents/plan-mode use will read as a positive signal by default — both are contested; using them without being able to explain *why* they fit this task can read as overhead-for-its-own-sake.

## Connections

- [[entities/ai-coding-agents]] — the class of tools (Claude Code, Cursor, etc.) candidates choose from
- [[concepts/ai-code-review]] — the reviewing discipline interviewers are testing for when they watch for "blind acceptance"
- [[concepts/ai-specific-pitfalls]] — the "looks right" failure mode is exactly the plausible-and-wrong moment ItaySela identifies as the real signal
- [[concepts/agent-skills]] — relevant to the bring-your-own-rules-file debate; grill-* antipattern (can't justify rules beyond "the plugin does it") maps directly onto this thread's post-hoc explainability test
- [[concepts/agent-subagents]] — relevant to the contested subagent-usage-as-signal debate
- [[concepts/verification-pipeline]] — the testing/validation axis (E2E happy path, review loop) mirrors this wiki's own quality-ladder framing
- [[concepts/multi-vendor-adversarial-review]] — GND52's cross-model subagent review suggestion is a live-interview application of this pattern
