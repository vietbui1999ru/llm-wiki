![](https://substackcdn.com/image/fetch/$s_!wbJS!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F0199d4e9-5c15-48b0-8e54-a47fcd83bbbe_1865x1526.png)

A new proposed standard for coding agent rules has been making the rounds: [AGENTS.md](https://agents.md/). There's not a lot to it—it's a single text file (mostly) to be included as context to your conversations with LLM coding agents.

Various [tool](https://docs.cursor.com/en/context/rules) [vendors](https://docs.roocode.com/features/custom-instructions) [have](https://docs.windsurf.com/windsurf/cascade/memories) [had](https://docs.augmentcode.com/setup-augment/guidelines) [competing](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions) [ideas](https://docs.cline.bot/features/cline-rules) about [how](https://developers.google.com/gemini-code-assist/docs/agent-mode#agent-mode-context) to [structure](https://docs.augmentcode.com/setup-augment/guidelines) [rules](https://agents.md/) —some have that same single text file, just with a different name, some let you reference/import other text files from the main file, others let the LLM pick which rules to use based on the content of the conversation.

I think this new "standard" gets several things wrong:

1. **A single text file (with directory-based overrides) is the wrong abstraction**
2. **Its suggestions on content are woefully inadequate**

## The Wrong Abstraction

The proposed standard is a single markdown text file named AGENTS.md, that can be overridden/supplemented by additional AGENTS.md in subdirectories.

### A single text file is not navigable

To be useful in anything but a tiny project, more context is needed at the global level than can be easily maintained in a single text file. Even the examples they give are realistically too big to fit easily in a single human-maintainable file:

> - Project overview
> - Build and test commands
> - Code style guidelines
> - Testing instructions
> - Security considerations

A much better approach taken by many tools is to let you break up the content into smaller, self-contained, single-purpose files. (Why shouldn't our documentation-writing structure should follow the same principles as our code-writing structure?) This makes the rules much easier to read and maintain.

Examples: [Claude Code's format](https://docs.anthropic.com/en/docs/claude-code/memory#claude-md-imports) lets you import other files by reference; Cursor lets you define any number of rules files with [suggestions on when they should be referenced](https://docs.cursor.com/en/context/rules#rule-anatomy).

### Nested AGENTS.md makes some big assumptions

For monorepos, AGENTS.md allows you to use nested AGENTS.md files in each package directory:

> Agents automatically read the nearest file in the directory tree, so the closest one takes precedence and every subproject can ship tailored instructions.
> 
> **What if instructions conflict?**
> 
> The closest AGENTS.md to the edited file wins; explicit user chat prompts override everything.

This makes a whole bunch of assumptions:

1. There’s only one file being edited
2. There’s a file being edited at all!
3. The scope of a single rules file corresponds to the directory it lives in (consider: `/frontend/users`, `/backend/users`)
4. There’s no ambiguity or impedance mismatch between the nested rules files (parent: "write only functional tests!" child: "write only unit tests!")

There’s also **one really big unstated** and almost certainly **false assumption—that the agent can be relied upon to absolutely follow such guidelines** about which rules to follow or tool calls to make. This is especially true in the case of this FAQ:

> **Will the agent run testing commands found in AGENTS.md automatically?**
> 
> Yes—if you list them. The agent will attempt to execute relevant programmatic checks and fix failures before finishing the task.

**No agent will reliably follow any such instructions** —even assuming there is no ambiguity—nor is such behavior enforceable by the orchestrator managing the agent.

### A better approach: imports and hooks

Claude and Cursor make some good attempts at more adaptable rule inclusion, via references, file globs, and tool-like rule descriptions, but if we take a very small step upward in the abstraction tree, aren't these rule systems just a startup hook about what context to inject into a system message?

Claude Code has a [comprehensive hooks system](https://docs.anthropic.com/en/docs/claude-code/hooks-guide), that while encompassing more than the rules use case, can certainly be leveraged to do more complex, project-specific calculus about what rules to include.

I, however use Cursor, which lacks hooks functionality, so I have to take matters into my own hands to force it to run.

I have a [system of memory and rules](https://github.com/joshwand/coding-agent-rules) that I use, which has many individual files for various purposes, and a global rules repo that I [symlink](https://github.com/joshwand/coding-agent-rules/tree/main?tab=readme-ov-file#installation) into Cursor’s rules directory.

One of the first entries in my global rules is as follows:

```markup
YOUR FIRST TWO TURNS:
Your first response must always be a tool call to read the memory (\`.mr\` command). Your second response must always be a tool call to read the output ("repomix-output.md").
```

I use the excellent [repomix](https://repomix.com/guide/) tool to compile the essential portion of my memory structure and read it into context. (That `.mr` command is defined elsewhere, as `npx repomix --quiet --include _memory/ --ignore _memory/knowledgeBase --style markdown`.)

(Note to self: I need make this load the rest of the rules, too, since Cursor [requires hacks](https://github.com/joshwand/coding-agent-rules/blob/9b39ee71eaba84628a9aef47aa2c78a63f4ae848/rules_manager.py#L14) to ensure "always" rules are actually "always" imported.

### Further hooks possibilities

In the grand scheme of things this is pretty basic usage. There are lots more possibilities with running commands in hooks than I currently use.

One could:

- Maintain a better map structure of path to common rules (`{"/frontend/users": "users.md","/backend/users": "users.md"}`)
- As in my example above, when working on a cross-cutting concern like a domain object, load the business, architecture, and coding rules and context that apply to that concern, regardless of which component you invoked it from
- Use additional environment context to determine which context to load—recent git changes, PR contents, bug details from your issue tracker, relevant wiki pages, etc.
- Pass all these details to another LLM to have \*it\* decide what context to include
- Invoke the LLM-based context generation after the first user message to take into account your current intent

The context engineering possibilities are endless!

## What is the right context, though?

The examples given on the [AGENTS.md](https://agents.md/#examples) site, and most [examples](https://cursor.directory/rules) that I find around the web about the **content** of AGENTS.md and similar, mostly restrict themselves to coding style, conventions, build instructions, and micro-level architecture considerations ("use react hooks").

The slightly more advanced rulesets attempt to provide [sound programming principles](https://gist.github.com/ruvnet/7d4e1d5c9233ab0a1d2a66bf5ec3e58f), or define the [desired coding/testing workflow](https://forum.cursor.com/t/i-created-an-amazing-mode-called-riper-5-mode-fixes-claude-3-7-drastically/65516).

But there’s **so much more project-specific guidance** that’s helpful to include, depending on the type of task you’re working on, that few people think to include. More importantly, I'm referring to **context that the AI can't infer from reading the code**.

To give an example, perhaps you’ve experienced the phenomenon where the agent will code something that’s either:

1. Far too complicated and robust for your project
2. Hacky "simplest thing that could possibly work" duct-tape solution

What's missing here is a *view on where you are in your project's lifecycle* —MVP? Mature product? Just a POC that will only ever run on your own machine?

Or maybe you're implementing a new feature. Some things that AI can't determine from reading the code:

- Where are your users located?
- What are the different personas that have to be taken into account?
- What the heck is a *(your domain object here)* and how does it interact with outside data sources?
- What's the larger process or business context of the user flow you're implementing?
- What's more important for this particular feature set: latency or resiliency?

I always like to say:

> **The AI can't read your mind.**

or, alternately:

> **The AI can't read the room.**

Now, different kinds of real-world business context are going to be required for different types of tasks. If you're writing test cases, you don't need to know your competitive advantage, but you sure do need to know the nature of the data and where it comes from. If you're planning a new feature or making a UI, you might not need to know your SQL standards, but you probably need to know who your users are.

Here's another way of thinking about it:

> ## Yes, the AI is a junior engineer.

If you've worked on a team building software, you've surely experienced one or more of the following:

- As a junior, you plowed ahead with some incorrect assumptions that your senior or PM had to correct
- As a lead or PM, you've inadvertently underspecified a request, and the dev has come back with questions (or worse, they didn't).

This is why in a team of any size, there are onboarding docs, reference materials, decision logs, design docs, process standards, and a process for how a new dev comes up to speed on all the different aspects of the project. Inevitably, there are gaps, or things get out of date, and you end up feeling the consequences of it when things don't work as expected.

**If you want good output, you need to onboard the LLM "junior dev" in each and every conversation.**

I have a separate post coming soon about how I think this knowledge/context base should be structured, but you can also take a peek at [the memory section of my coding-agent-rules github repo](https://github.com/joshwand/coding-agent-rules/blob/main/memory.md).

## Coda: open questions

Two quick notes/questions:

1. Despite my pontificating, and endless threads on HN and Reddit, I've yet to find actual research or benchmarks on whether these kinds of rules and context engineering are actually effective/useful for coding agent tasks?
2. Is anybody trying project-specific fine-tuning or LORAs, instead of rules in the system/user messages?