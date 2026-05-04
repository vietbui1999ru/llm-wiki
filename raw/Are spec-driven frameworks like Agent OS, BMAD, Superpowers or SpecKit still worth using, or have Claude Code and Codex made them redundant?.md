I've been trying to figure out where the community has landed on this, because I genuinely can't tell.

A year ago, the answer seemed obvious: if you're building anything non-trivial with LLMs, you need structured scaffolding — PRDs, memory layers, agent roles, task breakdowns. Frameworks like **BMAD-METHOD, Agent OS, Superpowers, and SpecKit** (and their cousins) exist precisely because raw LLMs drift, forget context, and produce spaghetti if you don't constrain them with specs upfront.

But now I look at **Claude Code** and **Codex**, for example, since they are the ones i'm using, and they feel... different? Claude Code does its own task decomposition, maintains context across files, and can self-correct mid-session without you babysitting a spec document. Codex feels similar — it reasons about the codebase, not just the prompt.

So I'm genuinely asking:

Do you still scaffold everything with a spec framework before touching Claude Code / Codex?

Or do you drop straight into vanilla agentic mode and only reach for a framework when things break down?

Or is the real answer that spec frameworks matter more now — because you're giving these powerful agents more autonomy, so the upfront spec is the only guardrail you have?

I built a mid-complexity product (a new vertical on top of an existing platform) using Claude Code and Codex with AgentOS as a seat belt. That was a year ago. I have a few projects upcoming to build and trying to decide whether investing in proper spec scaffolding is a force multiplier or just overhead that the model handles natively now.

Would love to hear from people who've shipped something real with either approach — not theory, actual experience.

***Worth mentioning... I'm originally a Product Leader who vibe codes now and not a software engineer.***

---

## Comments

> **hulkklogan** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojov0so/) · 28 points
> 
> I got rid of superpowers recently because they're just overly verbose and slow for my taste. I really like Matt Pocock's framework and skills, they strike a really nice balance of plan/prepare and execute without being so verbose as superpowers.
> 
> I DO really like the Superpowers brainstorming skill for UI work though, since it spins up an http server and serves examples. Easy enough to tell your agent to do though.
> 
> > **3abwahab** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpapoy/) · 2 points
> > 
> > I keep reading that Superpowers is tokens heavy as well.
> > 
> > So you now mainly use this Matt Pocock's skill? Can you share your workflow/stack, please. I think would be useful. Thank you so much!
> > 
> > > **hulkklogan** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpednu/) · 17 points
> > > 
> > > Here's his video that goes over the idea and the skills
> > > 
> > > [https://youtu.be/EJyuu6zlQCg?si=9HKdidbhjQljmR5N](https://youtu.be/EJyuu6zlQCg?si=9HKdidbhjQljmR5N)
> > > 
> > > Essentially:
> > > 
> > > 1. You describe what you want to do and run a grilling session for the agent to grill you and develop a shared comprehension of the work
> > > 2. Agent generates a detailed PRD
> > > 3. Agent breaks up the work into vertical slices (tracer bullets, for those familiar with the Pragmatic Programmer book) and creates a markdown kanban with tickets/issues. It also identified what can be AFKs and what needs HITL
> > > 4. review the issues to make sure it's actually doing vertical slices (AI loves working horizontally)
> > > 5. run agents
> > > 6. review work
> > > 
> > > > **3abwahab** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpffiq/) · 2 points
> > > > 
> > > > Thank you for sharing!
> 
> > **PinkySwearNotABot** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojrcogn/) · 1 points
> > 
> > he has more than 1 useful one besides the grill-me? i didn't think the other ones were worth salt
> > 
> > > **hulkklogan** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojrej8e/) · 3 points
> > > 
> > > Probably just comes down to personal preferences after grill-me, honestly. I like the one that works on code architecture too, to try to adhere to simple interfaces and deep modules.
> > > 
> > > > **PinkySwearNotABot** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojri8et/) · 0 points
> > > > 
> > > > How is grill me so popular?? It’s literally got like 3 lines of instructions -\_-
> > > > 
> > > > > **hulkklogan** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojrihyg/) · 2 points
> > > > > 
> > > > > Why's the size of instruction matter? It's incredibly useful. Sure, you can just copy/paste it.
> > > > > 
> > > > > > **PinkySwearNotABot** · [2026-05-04](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojtraro/) · 1 points
> > > > > > 
> > > > > > not a critique. more a state of awe.

> **genunix64** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpcien/) · 7 points
> 
> Frameworks are not redundant, but I would not treat them as one big mandatory ceremony either.
> 
> What has worked for me is splitting scaffolding into three layers:
> 
> 1. repo-local hard context: CLAUDE.md/AGENTS.md as a router, ADRs/specs/non-goals as source of truth
> 2. task orchestration: small investigate -> implement -> review units, ideally isolated in worktrees
> 3. cross-session memory: decisions, constraints, open questions, and project state that survive compaction or switching between Claude Code/Codex
> 
> The trap is putting all of that into one giant framework prompt. It feels safer, but it often just burns tokens and gives the agent more soft instructions to ignore. For small bugs, vanilla agent + tight repo docs is usually enough. For new features/services, I still want a spec/milestone/review loop because it catches ambiguity before implementation.
> 
> I built Mnemory for the third piece: a self-hosted memory backend for agents via MCP/REST: [https://github.com/fpytloun/mnemory](https://github.com/fpytloun/mnemory)
> 
> The useful part is not "more context"; it is lifecycle management: deduping decisions, handling contradictions when a fact changes, expiring short-term context, and keeping longer details as artifacts instead of stuffing everything back into the prompt. So my answer would be: use specs/frameworks where they reduce ambiguity, keep repo docs as the authority, and use memory only for durable cross-session state. If memory becomes a second messy knowledge base, it eventually hurts more than it helps.

> **\-PM\_ME\_UR\_SECRETS-** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojotdd5/) · 11 points
> 
> I think the biggest appeal of any sort of framework is that it can be used across models, you can change models as they ebb and flow in popularity and still maintain context/structure.
> 
> > **GolfEmbarrassed2904** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojovgg7/) · 5 points
> > 
> > Yes. I use GSD and Superpowers with Codex and Claude Code concurrently on the same repo
> > 
> > > **\-PM\_ME\_UR\_SECRETS-** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojp0c74/) · 3 points
> > > 
> > > Same with Superpowers. What is GSD?
> > > 
> > > > **GolfEmbarrassed2904** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojp4sk9/) · 4 points
> > > > 
> > > > Get shit done. [https://github.com/gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done). I do brainstorming with superpowers then review plan with codex then hand plan to gsd. I prefer the ‘granularity’ of gsd
> > > > 
> > > > > **3abwahab** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpblg5/) · 3 points
> > > > > 
> > > > > Shouldn't Superpowers and GSD be doing the same job?
> > > > > 
> > > > > > **GolfEmbarrassed2904** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpoeja/) · 1 points
> > > > > > 
> > > > > > GSD works from an end-to-end plan and defines individual phases and then allows you to further detail and iterate on each phases details (discuss, plan, execute)
> > > 
> > > > **mossiv** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpfmnx/) · 0 points
> > > > 
> > > > Get shit done. But it’s a dead framework now. GSD2 is out which is against the TOCs unless you use the API. GSD(1) is insanely token heavy and just not worth using anymore. Regardless of how good it is. I think it’s no somewhere in the 4-5x range of super powers.
> > > > 
> > > > You’d be better off with speckit, open spec, or spec kitty ad an alternative tbh.
> > > > 
> > > > > **HarbaughHeros** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojqgo5m/) · 3 points
> > > > > 
> > > > > “dead framework” > new version pushed less than 24 hours ago. Lmao
> > > > > 
> > > > > [https://x.com/gsd\_foundation/status/2042940718092525956?s=46](https://x.com/gsd_foundation/status/2042940718092525956?s=46)
> > > > > 
> > > > > GSD directly recommends using GSD 1 over GSD 2.
> > > > > 
> > > > > > **mossiv** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojqq7wu/) · 0 points
> > > > > > 
> > > > > > At some point, the focus was going to be GSD2. I take back my comment - but what I stated was truthful for an apparent small time in space.
> > > > 
> > > > > **GolfEmbarrassed2904** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpnw0b/) · 1 points
> > > > > 
> > > > > Yup. Unfortunately. However until I find something that works better for my workflow I’m continuing to use GSD. SpecKit is way over the top for me to use for home side projects. But eventually I’ll have to experiment with the others. GSD was built for the individual vs team developer - if you have a recommendation I’m all ears.
> > > > > 
> > > > > **vgwicker1** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojqfdql/) · 1 points
> > > > > 
> > > > > GSD new release 15 years ago. Totally agree on the api heavy one

> **return\_of\_valensky** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojouz1o/) · 4 points
> 
> I've been honing my setup over time and it's been steadily moving towards the main core of this below. I tried bmad and speckit for a while. The problem is that you want 1,000 small sessions that do exactly 1 thing with the only context being the rules, the code, and the task.
> 
> \- [CLAUDE.md](http://claude.md/) filled with philosophical programming best practices
> 
> \- skills with not a lot of words but deep technical meaning (mostly Matt Pocock's skills, but 3-4 of my own)
> 
> those 2 alone will get you to a good set of product requirement docs and individual issues.
> 
> from there I then use a headless agent with multi individualized passes INVESTIGATE->IMPLEMENT->REVIEW in git worktrees to tackle one piece at a time.
> 
> > **3abwahab** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpbyj3/) · 1 points
> > 
> > Insightful! Can you share the link for this Matt Pocock's skills?
> > 
> > > **return\_of\_valensky** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpjxuk/) · 5 points
> > > 
> > > [https://github.com/mattpocock/skills](https://github.com/mattpocock/skills)
> > > 
> > > here's the orchestrator I'm using as well:
> > > 
> > > [https://github.com/slikk66/dangeresque](https://github.com/slikk66/dangeresque)
> > > 
> > > matt has a much more advanced one, but it has some tradeoffs with complexity, the dangeresque is lighter weight and works for me, here's matt's:
> > > 
> > > [https://github.com/mattpocock/sandcastle](https://github.com/mattpocock/sandcastle)
> > > 
> > > Here's a video of him explaining how it works: [https://www.youtube.com/watch?v=E5-QK3CDVQM](https://www.youtube.com/watch?v=E5-QK3CDVQM)
> > > 
> > > I have been on my own journey to really figure this stuff out (professional reasons mostly) and I keep find myself aligning very closely with what this guy Matt keeps doing. Like literally I have an epiphany and then next day he puts out a video basically saying same thing, same epiphany, but his solution is like 20x more insightful and well thought out 😂 so I keep coming back to his stuff

> **BidWestern1056** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojp1nsp/) · 4 points
> 
> for a time they appear redundant but with the continuous regressions lately they are more important than ever.
> 
> check out npcpy too
> 
> [https://github.com/npc-worldwide/npcpy](https://github.com/npc-worldwide/npcpy)

> **yopla** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojqqnit/) · 4 points
> 
> Honestly I'm mostly done with framework. Last weak I just told Claude to "break it into phases and make a task plan that is trackable and include a prompt to restart from where the work stops, if everything is done say `That's all folks` and nothing else".
> 
> Then I ran it from the shell with a loop.
> 
> I think, my next "framework" will be just some variation of that in Claude.md

> **Sharchimedes** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojp4c0a/) · 3 points
> 
> Agentic decisionmaking is expensive and currently still error prone, so the more you can reduce ambiguity and keep context focused, the more efficiently you’re going to be able to get reliable results.
> 
> Projects grow into requirements, requirements are refined into specs, specs become implementation phases with breakdowns of tasks. Tasks result in functional code and tests.
> 
> Agents can be effectively directed to help at all these levels with various models and tools, and I expect the specific tools to change over time, but without some massive breakthroughs, the fundamentals are really the same as they always were.

> **Affectionate\_Unit155** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpj60h/) · 3 points
> 
> as a non engineer the spec frameworks prbably give u more value not less, they force the upfront thinking that engineers do naturally from experience. the model handling decomposition doesnt mean ur vision is clear enough to decompose correctly without structure

> **bart007345** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojq5n8w/) · 3 points
> 
> Everyone is talking about implementation details, i need a spec to describe the requirements.
> 
> Implementation is largely solved but how to make sure you built what the client wants?
> 
> > **lovenewyork** · [2026-05-04](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/oju047k/) · 1 points
> > 
> > Do you have an understanding of the functionality On a technical and non technical ($10 programming words) level?
> > 
> > If you do, most important thing is to break everything down into small tasks, setup a team of agents with skills that apply to your needs, most important part of this is an application - not just a website - you need a agents that handle review, testing and verification.
> > 
> > You chop stuff up into small blocks - you avoid context rot, dead code ‘/clear’ if everything passes and you can identify code runs - clean - commit, push - archive the work tree -
> > 
> > Clear saves you a ton of context and tokens.
> > 
> > Get started on next task. If you have a firm handle on the workflow, deploy more agents and start running them in Parallel sessions - (there’s a plugin where you don’t have to utilize teams - it will allow your agents to work in isolated work trees but communicate - someone help me. Forgot the name.

> **goship-tech** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojosnzw/) · 7 points
> 
> For single focused sessions, a lean [CLAUDE.md](http://claude.md/) is enough - Claude Code handles the decomposition natively now. The frameworks still earn their keep on multi-session projects where you need persistent task state that survives context resets; without that structure you are re-explaining the whole codebase every time.
> 
> > **3abwahab** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpazdv/) · 0 points
> > 
> > Great point. What framework are you using mostly?

> **Business\_Average1303** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojouzb9/) · 2 points
> 
> Depends, big effort I prefer these orchestration workflows, a spec is very useful if you’re working on a new artifact or service because you can actually lay out the solution before building it to prevent having (too many) modifications in the implementation phase. It’s easier to change a requirement, a big implementation detail that might affect how it’s built, you can generate diagrams to help you understand the solution too
> 
> If it’s just a bug fix or a small feature I think it’s overkill and just using Claude Code is enough 

> **rover\_G** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojovbz8/) · 2 points
> 
> For me claude seems to be making more nuanced decisions about when a task is underspecified as to require additional design and implementation planning
> 
> > **3abwahab** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpc84f/) · 1 points
> > 
> > So that means you're not using frameworks to harness and guide it?
> > 
> > > **rover\_G** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpg9ou/) · 1 points
> > > 
> > > I only use official anthropic and my own custom plugins. Claude’s behavior changes with every reading and also during A/B tests. Those changes are sometimes minor and sometimes more pronounced. Over time the changes stack up into meaningful transformations in the meta working strategy and I adapt my workflows to align with what anthropic says works best.

> **fangisland** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojowym5/) · 2 points
> 
> The most important thing is to push context into the repo via markdown in a structured way. Things like ADRs, guides, architecture docs, product goals and non goals, etc. and use CLAUDE.md as a compass to these docs (same with skills). If you do that, native plan mode works just fine; I'd only use the frameworks you mentioned if you struggle with knowing how to prompt effectively.
> 
> > **3abwahab** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpd0rs/) · 1 points
> > 
> > Well, that is enlightening. So it's like you're using a minified version of the frameworks through adding the Markdown files to the Repo and just use [Claude.MD](http://claude.md/) as the guide to read these docs?
> > 
> > > **fangisland** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojprfp3/) · 0 points
> > > 
> > > Yes, I loosely follow [the concepts in this article](https://openai.com/index/harness-engineering/), but I don't do frontend for the most part (I do platform engineering/infra) so not everything translates. For example, we do a ton of complex Ansible work for our IaC deploys and have a curated style guide with our opinionated expectations, so in my AGENTS/CLAUDE or any skills, I point the agent at that doc rather than rephrasing or summarizing the contents. This way you can have canonical locations for domain-specific knowledge and have a generalized compass or atlas to point the agents where they need to look.
> 
> > **Stradigos** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojphi5o/) · 1 points
> > 
> > Along those lines, is graphify worth it? Ever use that?
> > 
> > > **fangisland** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpqhsq/) · 1 points
> > > 
> > > No, I've never run into an issue where I was unable to create human-readable and bot-readable documentation that agents are able to glean context from in order to accomplish the tasks at hand. But I've also managed mid-sized software teams for years before code assistance/agents came out, so it's a skill I've always had.

> **iVtechboyinpa** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpkys6/) · 2 points
> 
> Is one necessary? I think you can arguably achieve a greater outcome if you know everything you want out of the solution, but in my case, I can think of maybe 80-90% of the way there, and I rely on the LLM to take me the extra mile.
> 
> When I initially started a few months ago I didn’t use anything, just plan mode and go. Then I learned about subagents and started using those heavily for domain work. Then I had a prompt I’d past every time so it would review my plan with subagents. Then I had it execute my plan with subagents.
> 
> This was all nice because it saved context and I felt like my output was better since each domain was scoped and owned.
> 
> I never looked into any of GSD, BMAD, etc. because I was content doing what I was doing. But then my mentor at work introduced me to an SDLC he was working on, which I started using and then adopted to my process, and now it’s what I use everyday.

> **PinkySwearNotABot** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojrdq3y/) · 2 points
> 
> that's what I've been wondering, too. still figuring it out.
> 
> but now I have the problem of having too many frameworks all at one time, and having difficulties toggling them on/off as not to clash with one another, as they sometimes do.
> 
> Compound Engineering, Grill-me, GSD1 + 2, SpecKit, OpenSpec, TinyPec (jk - got ya), impeccable, superpowers...
> 
> Anyone know of a good way to isolate them besides just uninstalling all of them but the one you want to play with? It doesn't make it any easier that there isn't a single folder for them that you can easily just go and modify
> 
> > **Vivid\_Activity\_7845** · [2026-05-04](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojt8iet/) · 2 points
> > 
> > Tldr: yes use tools below, (not mine, free local, im just a user)
> > 
> > It's still not entirely simple, depending on your set up, but there are some tools that help. They can help you keep track of your Claude code addons and CCTM lets you create profiles = a virtual (rather than soley based on folder) Claude code config.
> > 
> > It gives a gui where you can essentially check box which are active. You can have multiple profiles.
> > 
> > There are a lot of other features.
> > 
> > For just "viewing" your config of skills agents plug-ins settings hooks etc, I use CCM. I call it view as it's not for changing settings directly.
> > 
> > There is a lot of overlap = only CCTM does the profiles which give what you want = turn off overlapping skills, plug-ins, hooks etc..
> > 
> > Makes it easy to clone a base profile and add extras for TESTING
> > 
> > CCTM
> > 
> > [https://github.com/tylergraydev/claude-code-tool-manager](https://github.com/tylergraydev/claude-code-tool-manager)
> > 
> > CCM
> > 
> > [https://github.com/MarkShawn2020/claude-code-manager](https://github.com/MarkShawn2020/claude-code-manager)
> > 
> > In getting your links I notice the author recommends their new successor project
> > 
> > [https://github.com/lovstudio/lovcode](https://github.com/lovstudio/lovcode) It Looks on target but haven't used it. It's for skills management, more detailed analysis..
> > 
> > > **PinkySwearNotABot** · [2026-05-04](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojtqg4w/) · 1 points
> > > 
> > > The one agent I don't use, lol

> **vacationcelebration** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojp6z2h/) · 3 points
> 
> I use superpowers for pretty much everything. I don't have enough confidence in Claude or codex to perfectly implement a new feature just straight up or with plan mode.
> 
> Superpowers is worth it for me because of the milestones and reviews, each allowing another opportunity to catch edge cases, gaps and misinterpretations.
> 
> For really small stuff, I have a custom skill that forces a sub agent code review, linting/formatting check and commit.
> 
> Yes that takes more time and tokens, but I feel it saves me time and nerves in the long run, especially since I usually pingpong between at least two different agent sessions, so it's not like I'm watching the agent code and review.
> 
> > **Appropriate\_Pain4089** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojp7opk/) · 3 points
> > 
> > Loved Superpowers, but I think it got slow and too bloated? Everything ate thousands of tokens and took a lot of time
> > 
> > > **vacationcelebration** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojp8yrv/) · 2 points
> > > 
> > > I gladly trade in time and tokens for bad surprises during final PR review.
> > > 
> > > In codex, I actually request the agent to always use sub agents for reviews instead of doing self-reviews as I feel they catch more, even though they take more time, tokens and maybe iterations.
> 
> > **lovenewyork** · [2026-05-04](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/oju0ank/) · 1 points
> > 
> > Yea superpowers is amazing. Agreed.

> **lgbarn** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpdpsn/) · 1 points
> 
> I’ve used them all and grill-me is better for my workflow. Way more detailed spec. Using a crafted Claude.md is pure snake oil.

> **KickLassChewGum** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojpy9lc/) · 1 points
> 
> Claude Code has made nothing redundant. If anything, *it* has become redundant, and the way Anthropic is trying to fix this isn't by making it *non*\-redundant, it's building a walled garden around their thing.

> **Conscious\_Concern113** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojq68vo/) · 1 points
> 
> I used BMAD heavily until Opus 4.7 then I switched back to regular plan mode. The secret to making that work is have Codex 5.5 high review the plan and give feedback that is feed back into Opus 4.7. You will go through several iterations until they full agree the plan is ready. Then have Claude implement the plan on a separate session. Once complete Codex does a code review.
> 
> So far it has worked great on larger features.

> **\_Bo\_Knows** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojr11s7/) · 1 points
> 
> I think fundamentally everything in the harness will be absorbed into the models. I think it helps, but fundamentally the moat is the understanding and context you/your team/company compounds. My plugin helps me create that moat now so it starts compounding and is plugin proof. Check it out [https://github.com/boshu2/agentops](https://github.com/boshu2/agentops)

> **TheTentacleOpera** · [2026-05-03](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojrd9x0/) · 1 points
> 
> I have an agent write out plans, have them in linear, pull when I want to work on them.
> 
> How am I meant to keep an entire project in my head if I only use native CLI tools?
> 
> Also if you need to go back to a feature, it really helps to have the plans available with the implementation details added in the code review stage.

> **Birchyman** · [2026-05-04](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojs44cj/) · 1 points
> 
> Not sure if they are required but I use them because everything I’m doing is for my own learning and, working in the tech space but no software background, it’s given me really good insights into spec driven development, importance of PRD and UX design etc.

> **silveroff** · [2026-05-04](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojsosy8/) · 1 points
> 
> No offense intended, but if I were you (not software engineer) I’d drop the idea of spending my time and money on any AI. It will simply not work. You’ll think it is or „almost” or you’ll think that someone will take over and „fix it”..but that’s not true. It will be pile of useless code eventually. Sorry to say that.

> **lovenewyork** · [2026-05-04](https://reddit.com/r/ClaudeCode/comments/1t2mym5/comment/ojtz6tl/) · 2 points
> 
> Hey bud, avoid the overly negative butt hurt people - truth is it all depends on the type of project, its scope - and your own config.  
> My advice - if you have the time, study everything you can about best practices straight from anthropic’s site and Codex to start. Once you have a grasp on the functionality, principles, try stuff out.  
> I spent a long time messing around with different methodologies - currently and honestly - vanilla Claude CLI with superpowers and a few other agents,skills, plugins, hooks etc have been working fantastic for me.  
> There are some really cool harnesses and setups out there but more often than not, there’s always a trade off. I think if Anthropic allowed usage with subscription and we all weren’t terrified of being banned - there might be more out there but try and learn the principles first. Coded is pretty damn decent - very straight forward.  
> I would avoid Gemini - CLI like the plague, it routinely lies about writing code, creates fake commits etc - save your money - but don’t stop exploring. Every single day there are new things popping up! Make something dope!
> 
> Forgot to mention impeccable for design, UI-UX Pro Max for design, superpowers via Claude marketplace, compound engineering, caveman, graphiphy, claude-mem, look for something to replace the grep tool that comes built in (if it still does) - if you don’t have any db setup or some type of persistence across each of your projects, each of these platforms will eat through your tokens searching and scanning through your directories - night.