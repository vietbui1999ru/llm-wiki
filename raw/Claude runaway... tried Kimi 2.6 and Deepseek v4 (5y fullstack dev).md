Hey guys, everyone is hunting for Claude alternatives right now right? I got tired of the situation too so I threw 20 bucks at Kimi 2.6 and Deepseek v4 to test them properly.

I'm a fullstack dev with around 5 years experience. My test was pretty real world: I made Claude Opus write a solid implementation plan like for a mid-level dev, then gave it to Kimi/Deepseek to actually code it. After that I had Opus do a proper code review.

Kimi 2.6 was clearly better. In most tasks it got pretty close to Sonnet level, but it kept missing stuff. Like it would do 85-90% of the job and forget some edge cases or smaller details. Also it thinks for ages and eats tokens like crazy. Yeah it's way cheaper but feels like a solid junior dev - can do the work but you gotta watch it and fix things after.

Deepseek v4 was straight up painful. Super slow, gave me wrong results multiple times, I just stopped testing it halfway. And even tho their website shows crazy cheap prices, after using it I have no idea how that works because it felt expensive for what I got lol.

Conclusion: I won't touch Deepseek again. Kimi is decent if you're on a tight budget and okay with reviewing everything, but I'm still looking for something closer to Claude without paying 100-200$ monthly.

Anyone found something better lately? Especially for fullstack/coding work. Help a brother out 😃 

**Update:** Guess I really underestimated DeepSeek v4 on "max" reasoning

A lot of dudes told me to give it another shot and I'm glad I did. Just tried it on a tricky bug I couldn't fix myself in one of my projects. It took quite a while thinking but it was actually fun watching it work. Also, Opencode shows the pricing(for ds) all wrong!! checked my balance after and it barely spent 20 cents for a full 1-hour debugging session!

Did it fix the bug directly? Nope. Did it give me solid insights? Yes. So overall it was helpful. Price/performance is actually impressive. But if I’m in a hurry, I’d still go with Sonnet. Sonnet would probably fix it faster even if it costs me like 8-10$

---

## Comments

> **flurrylol** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojodyw4/) · 61 points
> 
> You seem to be relying far too much on the LLM. You need a good harness and that’s what OpenCode is built for.
> 
> If you want to avoid expensive frontier models for coding, you must provide a good ecosystem for your LLM to perform well.
> 
> For starters, make sure DeepSeek is set to ‘max’ reasoning.
> 
> Then use specialized agents, skill, hooks, anything that will help you have the outcome you desire.
> 
> [My settings are open](https://github.com/fmflurry/settings-opencode) if you want inspiration, not that they’re good for you but I’m using a lot of deepseek v4 lately with great results for my needs.
> 
> > **thatguyinline** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojp6e8e/) · 18 points
> > 
> > Try GLM 5.1, in my experience it trounces Kimi by a lot. Opus comparable.
> > 
> > > **flurrylol** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojqadlw/) · 4 points
> > > 
> > > No indeed, OpenCode is model agnostic ! I use ‘max’ reasoningEffort, [I think they had an issue but 1.14.24 fixes it.](https://github.com/anomalyco/opencode/releases/tag/v1.14.24)
> > > 
> > > Edit: I replied to the wrong comment…
> 
> > **merth\_dev** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojofisg/) · 6 points
> > 
> > Thanks for sharing your settings, appreciate it!
> > 
> > > **Murdathon3000** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojpix8l/) · 4 points
> > > 
> > > I for one would be interested in a follow up or edit to this post re-running the same test again, maybe throwing in GLM 5.1 into the mix as well.
> 
> > **toadi** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojso1ic/) · 3 points
> > 
> > Sorry for being off topic but I see you use instincts. Does it work well? I seem to be bouncing around memory systems. For the moment I integrated Honcho [https://github.com/plastic-labs/honcho](https://github.com/plastic-labs/honcho). It captures well. But for example my problem is that I can not make the models use the memories well.
> > 
> > Use opencode and Pi agent. The latter more and more and just like you I write most of my own workflow.
> > 
> > WIll try Deepseek. Currently using GLM5.1 a lot.
> > 
> > **ivanimus** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/oju0foi/) · 1 points
> > 
> > Why you have the same skills in .claude, what difference?  
> > summary-routing-spec-error-resolution  
> > summary-routing-spec-error-resolution-2  
> > summary-routing-spec-error-resolution-3
> > 
> > > **flurrylol** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojurrbq/) · 1 points
> > > 
> > > These are skills 'auto-learned' at the end of the session. I will triage, but because I'm not using ClaudeCode as my main harness, it gets kind of messy over time. I will update today.
> 
> > **skpro19** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojufc6c/) · 1 points
> > 
> > You have defined subagents in your command file. But I don't see any subagent folder in the git repo?

> **flying-saucer-3222** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojpcw8n/) · 12 points
> 
> Our experiences are significantly different. Compared to Opus almost every model has given me better results at considering edge cases or fine details in real world tasks. If you try to vibe code, then Opus is the best but for any complex task where you want to guide it through development, it is terrible because it does not follow the instructions.
> 
> For example I once tried to migrate a 15,000 line C++ codebase to Rust and Opus implemented half of the features and just completely ignored any requests to implement the rest. Kimi, Deepseek or GPT produced slightly worse code but atleast they tried to implement everything. Even if the implementation was not perfect, I had to make a lot fewer changes for these results than for what I got from Opus.
> 
> And there was the time I asked Opus to find the route cause of a bug and it spent 10 minutes reasoning only to give me a list of generic possibilities because it didn't read the file I asked it to read. While GPT and Deepseek V4 Pro both found the cause of the bug in less than a minute because unlike Opus they actually read the file.
> 
> > **toadi** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojsonps/) · 2 points
> > 
> > Don't think Opus is made for that kind of work. Every model has it's task. I will stay in Anthropic world.
> > 
> > Opus is more the chat exchange ideas model. How would I implement abc, what options do I have. Could you spawn off a subagent to look into the code (with Haiku) how things are implemented and provide me some options.
> > 
> > Sonnet I would use for bit more open ended implementations. Or even for the bug hunt.
> > 
> > Haiku when I'm quite specific. Like in the code in this place implement a method that does xyz.
> > 
> > In essence different model for different types of jobs. Some overlap a bit and also depends on your workflow and type of project.
> > 
> > > **merth\_dev** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojtgh0a/) · 1 points
> > > 
> > > this is very similar to my usage
> > > 
> > > **Few-Philosopher-2677** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojvcbke/) · 1 points
> > > 
> > > That's how anybody should be using them. Honestly all I see everyone talk about is Opus lol. Less people talk about how to optimise their AI usage.

> **Grouchy-Stranger-306** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojod6xq/) · 11 points
> 
> deepseek found a few bugs for me that kimi introduced (c++), it doesn't always get the best results on first attempt but overall pretty happy with it, I moved from github copilot
> 
> > **merth\_dev** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojodn8b/) · 3 points
> > 
> > Yea, I heard a lot about Deepseek being strong on logic, maybe it's way more useful for heavy backend tasks. But for example this morning Gemini 3 Flash fixed a bug that GPT was struggling with

> **look** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojofw4v/) · 13 points
> 
> Try Mimo 2.5 Pro to develop a spec, GLM-5.1 to make sequential plan files from that spec, then Kimi 2.6 to implement those plan files.
> 
> Use another model, such as Qwen 3.6 Plus and/or Deepseek V4 Pro, to do adversarial reviews of each step.
> 
> > **merth\_dev** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojog8hv/) · 3 points
> > 
> > appreciate it
> > 
> > > **look** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoj2vz/) · 8 points
> > > 
> > > No problem. I think the key insight for working with open models is that each one has significant strengths and weaknesses. Unlike working with Opus, you do not want to use just one model for everything.
> > > 
> > > The second thing is that there is a lot of personal preference and difference in workflows, and there are a bunch of models each with its own style and quirks, so what works well for one person might not work as well for you. Experiment with all of them a bit to find the pairings that work best for you.
> > > 
> > > In my opinion the single two best models right now are Mimo 2.5 Pro and GLM-5.1. Combined (Mimo for the high level then GLM for the implementation) they are very Opus-like in both the quality and the interaction.
> > > 
> > > > **debackerl** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojpt71v/) · 2 points
> > > > 
> > > > Exactly, sometimes I'm bored by people claiming X is the best, and the comment saying 'no Y is best'... Depends on the use case...
> > > > 
> > > > I see an analogy with our own company: 15yr ago, dev teams were composed of senior devs getting high-level specs from marketing, now, those specs are giving to a business analysts, which the gives each user journey and workflow to the IT architect (a senior dev), which hands over to a junior or medior dev. When I read people saying that they use a powerful model for specs and lighter one for dev, I feel like they fall in my 2nd case.
> > > > 
> > > > How do you do the split? To what level do you let the planner creates tasks? (E.g. UML diagrams of the target? Name of each method to change? Or higher level?)
> 
> > **gfxd** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojsxh9l/) · 1 points
> > 
> > Is there anything like Claude Octopus, but exclusively for open source models?
> > 
> > [https://github.com/nyldn/claude-octopus](https://github.com/nyldn/claude-octopus)
> > 
> > > **look** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojtylr8/) · 1 points
> > > 
> > > I don’t use anything like that, but you can make subagents for adversarial reviews by other models and maybe a slash command to launch a set of them.
> > > 
> > > For something a bit more structured, reading Octupus’ description reminded me a bit of [https://github.com/obra/superpowers](https://github.com/obra/superpowers)

> **MatKarYaarPlease** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoji2m/) · 6 points
> 
> you'll probably have a better time using deepseek v4 flash max reasoning instead of v4 pro
> 
> > **Classic\_Television33** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojqdsvh/) · 2 points
> > 
> > Why? Do you find its reasoning better or just faster with the same quality?

> **Several\_Pi\_58** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojobphf/) · 5 points
> 
> Tried on opencode glm 5.1 or minimax 2.7, its good.
> 
> Not só good like Claude opus or gpt 5.4, but glmm 5.1 or Kimi 2.6 isnt so worst.
> 
> And minimax 2.7. is cheaper and good.
> 
> > **merth\_dev** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojod8fm/) · 5 points
> > 
> > I guess i will go with GLM first
> > 
> > > **Several\_Pi\_58** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojqnoz7/) · 3 points
> > > 
> > > Its more expensive. But better.
> > > 
> > > > **worstvillan** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojqv3ys/) · 3 points
> > > > 
> > > > go with opencode go subscription and use ds v4 flash with high reasoning and some skills from awssome skills github, its much better than minimax 2.7 in my case . tps,reasoning - ds won
> > > > 
> > > > > **Several\_Pi\_58** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojrgoer/) · 2 points
> > > > > 
> > > > > Thanks for your tip.
> > > > > 
> > > > > **nealhamiltonjr** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojt5cfn/) · 1 points
> > > > > 
> > > > > The github I found for awesome skills seems to all be for claude code. Which one are you referring to?

> **bbramb** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoiv4z/) · 5 points
> 
> Interesting. We have a different experience then.
> 
> I fired claude cause deepseek-v4 is just as good. Tbh, sonnet was already a great model for my engineering workflow but deepseek-v4 is as good as opus 4.6 at a fraction of a cost.
> 
> > **Riseing** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojs0ffh/) · 3 points
> > 
> > Most of these models are good enough to do most of my work with human review. Full blown vibe coding you'll probably need opus 4.6 or gpt 5.5 but if you have enough experience to already know what you need done I find most of them to be interchangeable at this point.
> > 
> > Kimi 2.6 is my favorite right now since it has zero guardrails and will work on anything.
> > 
> > **torontobrdude** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoyzty/) · 2 points
> > 
> > Are u using pro or flash
> > 
> > > **bbramb** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojozv2p/) · 2 points
> > > 
> > > Pro.

> **NoBlame4You** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoq02l/) · 5 points
> 
> Personally i use opencode and use glm 5.1 mostly but for very clear instructions or just alot of easy work, i really enjoy working with deepseek flash max.

> **Friendly-Assistance3** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoa1y2/) · 27 points
> 
> Skill issue
> 
> > **Time-Category4939** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoauto/) · 4 points
> > 
> > For the people that might be interested, how would you proceed?
> > 
> > **shadow1609** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoakw2/) · 7 points
> > 
> > Agree
> > 
> > **merth\_dev** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoao1h/) · 4 points
> > 
> > a bit more details bro
> > 
> > > **orionblu3** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojobff9/) · 2 points
> > > 
> > > Not dude but just curious; was it on max reasoning effort?
> > > 
> > > > **Unlikely-Scratch8915** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojq7lwn/) · 1 points
> > > > 
> > > > I heard some harnesses are incompatible with DS reasoning. Is that true? Oh wait actually it's resellers like openai that are incompatible with DS reasoning. Not sure about opencode now.
> > > > 
> > > > > **orionblu3** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojqcxme/) · 2 points
> > > > > 
> > > > > Deepseek through deepseek directly works as expected in terms of being able to change reasoning effort with ctrl+t. Deepseek through ollama *requires* adding reasoningeffort setting directly in the config, so there's that but yeah haven't had any issues personally; maybe some weird caching bugs occasionally
> > > > > 
> > > > > > **Icy\_Passage4064** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojsq6cq/) · 1 points
> > > > > > 
> > > > > > Which values can it take ?

> **AutomaticAd6646** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojocnfx/) · 8 points
> 
> Opencode 5 dollar first month then 10 months next. 70 times the usage compared to claude.
> 
> I used claude and opencode in same project side by side. They both gave same answers to my prompts.
> 
> > **Unlikely-Scratch8915** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojq7v8s/) · 2 points
> > 
> > Can opencode handle DS4 Pro's reasoning?
> > 
> > > **AutomaticAd6646** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojst1pq/) · 1 points
> > > 
> > > What is ds4
> > > 
> > > > **Unlikely-Scratch8915** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojwgze5/) · 1 points
> > > > 
> > > > Deep Seek V4. I found out it can with DS direct API but it fails with opencode unless you get a special shim.
> 
> > **merth\_dev** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojod572/) · 2 points
> > 
> > and how did you test it? some real projects or leetcode challenges?
> > 
> > > **According\_Water\_5774** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoinl9/) · 3 points
> > > 
> > > To be honest it sounds like you are trying a leetcode challenge set up on a real world project. If you spend time getting the set up correct you can get excellent results even with something like Deepseek v4 Flash - which is cheap and fast (and you get a load of usage from it with OpenCode Go). It sounds like you are coming from Claude and expecting the same results without putting in any of the effort that would get you the same results.
> > > 
> > > **AutomaticAd6646** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojstl57/) · 1 points
> > > 
> > > What is leetcode? I use opencode and claude in React native and Mern based projects.

> **acecile** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojodx7q/) · 4 points
> 
> I really think Qwen 3.6 is doing great. It's probably less powerful but cost lors less and its doing good job when instructions are clear
> 
> > **merth\_dev** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoe7o6/) · 3 points
> > 
> > It might be cheaper but it eats way more tokens so in the end they kinda cancel each other out

> **narkeeso** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojodxtc/) · 4 points
> 
> I would give Kimi another try, you won’t find better performance to price ratio imo. Without knowing your prompts, I would suggest being ready to question the response. The more questions the better, even if it’s for your own understanding too. Sometimes the reasoning will catch mistakes through this process and you can learn something from it too. One shot fixes/features are rarely the optimal solution in my experience even when using Opus 4.6

> **amunozo1** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoga7w/) · 4 points
> 
> I really had great experiences with DeepSeek. I did not use Claude recently but, although it is not as good at GPT-5.5, it is really good and not slow at all.

> **SkilledHomosapien** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojomvo0/) · 4 points
> 
> Ds4f is very fast and cheap, but it could always provide different perspectives on a same topic so that’s very helpful.

> **NadaBrothers** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojp4bi6/) · 4 points
> 
> Well deepseekr4 is a reasoning model. In contrast,   Kimik2 is specifically for trained agentic coding which explains what you saw.

> **Zestyclose\_Report526** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojp67eg/) · 4 points
> 
> LLMs can only do what you tell them to. If they aren't giving you the results you are looking for then you need to be more verbose in your instructions. Try using the grill-me skill to help build this habit, think of it like prompting training wheels. Soon you'll just be giving it proper instructions without needing it.  It's quite a common issue to omit LLM instructions that you think are common sense, it's definitely a Shift in thinking.

> **Rustybot** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojqhtkz/) · 4 points
> 
> My top tier:
> 
> Gemini-3.1-pro-custom-tools,  
> Minimax m2.7  
> GLM 5.1  
> Gpt5.3-codex, 5.4-mini, 5.4/5.5  
> Gpt-oss-120b (high) for fast and simple.

> **vbitcoin** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojocrtx/) · 9 points
> 
> For me kimi suck and waste of time. Glm is better and will save your day
> 
> > **merth\_dev** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoczsc/) · 7 points
> > 
> > yea GLM I will give it a try
> > 
> > > **Much-Researcher6135** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojs49k3/) · 1 points
> > > 
> > > results?

> **Sid-Hartha** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoln5x/) · 3 points
> 
> DeepSeek v4 is excellent and fast in my experience. User error.
> 
> > **BlacksmithLittle7005** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoy317/) · 2 points
> > 
> > Pro or flash and what reasoning levels?

> **hackdev001** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojorphe/) · 3 points
> 
> I have found kimi k2.6 and mimo v2.5 pro to be pretty good for everyday use.  
> Not as good as GPT 5.5 obviously but does the job finally. You just have to be good with prompting

> **m1k3s0** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojq9xxr/) · 3 points
> 
> I can't speak to fullstack dev work but in my experience with a C++ app, DS V4 Flash is amazing with the right guidance. I also toggle between plan and build a lot. Before I make any big changes I work through all of the details with it, then I put it in build mode and let it loose. It's crazy how fast and cheap it is.

> **IvanVilchesB** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojqdqw7/) · 3 points
> 
> My setup is similar , try mimo 2.5 pro i think is better than kimi , deepseek

> **Classic\_Television33** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojqfuep/) · 3 points
> 
> Per my own testing (giving the same question to GLM-5.1, Kimi K2.6, DeepSeek v4 Pro max) I've found DeepSeek v4 Pro max to be the best issue analyst. It can deliver detailed analysis on an issue that ended up helping GPT-5.5 xhigh catch a bug it failed to fix on its own. As for implementation, GLM-5.1 has lower hallucination rate than Kimi K2.6 per AA bench and is much faster in opencode Go.

> **ennbou** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojr5zuw/) · 3 points
> 
> I recently tried Kimi, and I asked Moonshot AI to opt out of having my content used for model improvement and research purposes. I followed the exact process mentioned in their Terms of Service, but it seems they don't respect their own rules.
> 
> Their response was implicitly a 'no,' telling me that if I want to stop data collection, I have to "apply to delete my account." So, this will be my first and last time using them.

> **qq\_rawrr** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojraixb/) · 3 points
> 
> Idk which deepseek you used but even flash through open code go subscription and open code harness with agents md and a plan worked like codex/claude for me lmao it only failed some very nifty gritty networking details like client server reconciliation specifics. On any other task didn’t flinch and since the codebase is full oop without over engineering stuff review was very clear and easy to do it did everything perfectly maybe the name choices where a bit more specific than I would do but it didn’t better work than the mid devs in the 2 teams I lead

> **Mistic92** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojrf0fk/) · 3 points
> 
> Deepseek os great with Go, flutter and some frontend. It feels like sonnet

> **Messi\_is\_football** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojrixly/) · 3 points
> 
> Idk, i used deepseek flash (medium) after using gemini 3 flash. Deepseek much better. 200k LOC project, multi file edits.

> **CtrlAltDelve** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojrr6ye/) · 3 points
> 
> Honestly, it's not even a contest for me. The Codex Pro tier is everything I could have ever wanted from an LLM subscription, with limits that I can't hit even if I try.

> **lemon07r** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojskqa0/) · 3 points
> 
> Gpt 5.4 is the only good cheaper option and it's not that much cheaper. And 5.5 is obviously just as expensive pretty much. K2.6 was basically the best cheapish option but it's still nowhere near gpt or opus levels. You can try glm 5.1 maybe? I think it's around k2.6 level, maybe slightly worse. Sub wise I really like the codex plans and factory droid's new subs which are similar.

> **unkownuser436** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoi4wz/) · 5 points
> 
> This is probably skill issue. Five years of developer experience means nothing, if you dont know how to use these AI tools bro. Deepseek v4 actually good model.

> **Necessary\_Water3893** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojofmuh/) · 5 points
> 
> Totally agree that Claude can’t be beaten by the open-source models yet. I believe all the hype you see in this subreddit is probably based on small projects
> 
> For me, the closest thing to Claude is the ChatGPT model through the $20 subscription, using Codex or OpenCode
> 
> > **merth\_dev** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojog1i1/) · 5 points
> > 
> > The main reason I'm looking for an alternative is I have a feeling these cheap 20$ plans will disappear soon. That's why I wanted to test everything now before prices go up
> > 
> > > **PaulGrapeGrower** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojpbysh/) · 3 points
> > > 
> > > I have the same feeling. I'd bet these plans will be 10x more expensive a year from now.
> > > 
> > > BTW, I'm using MiniMax and GLM. MiniMax works well for 80% of the tasks and I give the harder tasks to GLM. I also use GLM to review MM work.
> > > 
> > > Edit: I also use BMAD skills for advanced tasks.

> **iamvandevo** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojpymbj/) · 2 points
> 
> Deepseek v4 is amazing. I found it better than Claude. You probably have skill issues

> **jfly2015** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojqa5ci/) · 2 points
> 
> I'm using Deepseek V4 PRO API with VSCode and Cline, works well for me, I guess it depends on the job. If fixed things claude was having a hard time fixing.

> **ofcoursedude** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojqb2lh/) · 2 points
> 
> Where did you try those? Deepseek with opencode using the deepseek provider (not openrouter or something like that) is very fast and extremely token efficient while delivering more readable code than other models
> 
> > **merth\_dev** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojtg72x/) · 1 points
> > 
> > i subscribed to deepseek and moonshot apis, used them in opencode by providing API key

> **FindingSerendipity\_1** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojql5b8/) · 2 points
> 
> Check out MiMi 2.5 Pro, it has not gotten as much hype but is a very capable model overall and scores very close to the top closed SOTA models. If you want to try a bunch of models (api) for cheap, check out NanoGPT - Here is a discount code invite [https://nano-gpt.com/r/xQyxyy83](https://nano-gpt.com/r/xQyxyy83) (ref)

> **HappySl4ppyXx** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojtb460/) · 2 points
> 
> Try GLM5 and 5.1

> **alp82** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojth32f/) · 2 points
> 
> You need to use a harness and framework/workflow, otherwise the models have to fill the gaps too heavily.
> 
> Or extremely detailed prompts, but that's not an efficient user of your time either.
> 
> I built a workflow for myself which I released as Claude code plugin, but I think i should also make it compatible with opencode and hermes.
> 
> It's basically treating prompts as starting point to gather requirements, implement it and review the results afterwards.
> 
> It will use more tokens but the quality will increase significantly.
> 
> If you want to check it out: [https://github.com/alp82/alp-river](https://github.com/alp82/alp-river)
> 
> > **merth\_dev** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojtzl3y/) · 2 points
> > 
> > thanks for sharing

> **SwissTac0** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoz8vf/) · 5 points
> 
> I mean GPT 5.5 is best you gonna get.... Claude is junk. Gpt actually scales down well through the efforts and lower level VS Claude which if it's not opus Xhigh it's useless and Xhigh is useless because it'll run out in about 25 minutes for me.
> 
> You need to say what you are doing. DS 4 pro is legendary at many things. GPT is legendary for everything except UI design but that's fine go use Kimi, Qwen, Gemini or Opus for that.
> 
> Whats your goal? Are you a vibe code purist that wants to do nothing? Qwen. Better than Claude for 90% of what half the people on here do while being 20% the price and 10x faster for the same task.
> 
> Are you wanting to keep a grip on everything and just have a dn good implementation Ai that executes on your creativity? Gpt
> 
> You doing Math heavy work? V4 Pro or R1, hear Gemini is good now for this.
> 
> .
> 
> Claude is just the overly seductive party girl that you managed to claim as your GF.... It's fun at first but then you start to grow up and learn you want to actually move forward in life so you break up and find a real woman that ends up being your best friend while sto your surprise is objectively sexier.
> 
> > **merth\_dev** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojp308b/) · 3 points
> > 
> > #1 answer! Thanks

> **CommercialMove1486** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojoksct/) · 2 points
> 
> These days I have the GO plan, and I've been using GLM 5.1 a lot to plan/discuss and Qwen 3.6 plus to execute. It's been giving me good results in production projects. Of course, I've been using a lot of skills like superpowers and caveman + rtk, to better direct the models and reduce context and token consumption...

> **vietphi** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojolm7v/) · 2 points
> 
> Keep the **$100 Claude plan** and use it to **orchestrate models** in OpenCode to save money.
> 
> > **PaulGrapeGrower** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojpag81/) · 2 points
> > 
> > What do you use to do orchestration?
> > 
> > > **vietphi** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojrsv6u/) · 3 points
> > > 
> > > I'm using Opus. It generates a bash script to call the OpenCode models and decides which one fits each task. For example, it currently prioritizes DeepSeek v4 Flash because it’s powerful and cost-effective. More intensive reasoning models like GLM 5.1 are capped at around 15% to save quota. I honestly didn't expect Opus to be smart enough to handle this logic but it did very well. 
> > > 
> > > I've actually moved this into a separate GitHub repo and am currently testing it. Planning to share it with everyone soon!
> 
> > **debackerl** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojptgng/) · 2 points
> > 
> > Careful, if Anthropic catches you using OpenCode with a sub, they will ban you
> > 
> > > **vietphi** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojrr8us/) · 1 points
> > > 
> > > Why? I dont have any warning about this? 

> **VictorCTavernari** · [2026-05-03](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojpdj2q/) · 1 points
> 
> I launched my service for model inference and I am curious to know if you have these evaluation on some GitHub Repo, because I would like to test it on with service.

> **tuhdo** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojtzp91/) · 1 points
> 
> Try Codex $100 bro. Just for this month is sufficient. You can LOOP with that thing.

> **Nice-Permission-4339** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojuesma/) · 1 points
> 
> I have been cycling through the same models and the trade-off usually comes down to speed versus deep reasoning. If you have the time to let the model "think" then the newer reasoning versions are unmatched for debugging. I still keep Sonnet as my primary for quick logic but I have started using the Grok and Opus 4.6 APIs for the really messy architectural stuff. It is all about using the right tool for the specific task rather than trying to find one model to rule them all.

> **skpro19** · [2026-05-04](https://reddit.com/r/opencodeCLI/comments/1t2kl79/comment/ojufvrr/) · 1 points
> 
> Try minimax m2.7 to implement the plan.