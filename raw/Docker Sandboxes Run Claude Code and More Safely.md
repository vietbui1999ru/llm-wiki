We introduced Docker Sandboxes in experimental preview a few months ago. Today, we’re launching the next evolution with microVM isolation, available now for macOS and Windows.

We started Docker Sandboxes to answer the question:

## How do I run Claude Code or Gemini CLI safely?

[Sandboxes](https://www.docker.com/products/docker-sandboxes/) provide disposable, isolated environments purpose-built for coding agents. Each agent runs in an isolated version of your development environment, so when it installs packages, modifies configurations, deletes files, or runs Docker containers, your host machine remains untouched.

This isolation lets you run agents like **Claude Code, Codex CLI,** **Copilot CLI, Gemini CLI, and Kiro** with autonomy. Since they can’t harm your computer, let them run free.

Since our first [preview](https://www.docker.com/blog/docker-sandboxes-a-new-approach-for-coding-agent-safety/), Docker Sandboxes have evolved. They’re now more secure, easier to use, and more powerful.

## Level 4 Coding Agent Autonomy

Claude Code and other coding agents fundamentally change how developers write and maintain code. But a practical question remains: how do you let an agent run unattended (without constant permission prompts), while still protecting your machine and data?

Most developers quickly run into the same set of problems trying to solve this:

- OS-level sandboxing interrupts workflows and isn’t consistent across platforms
- Containers seem like the obvious answer, until the agent needs to run Docker itself
- Full VMs work, but are slow, manual, and hard to reuse across projects

We started building Docker Sandboxes specifically to fill this gap.

## Docker Sandboxes: MicroVM-Based Isolation for Coding Agents

**Defense-in-depth, isolation by default**

- Each agent runs inside a dedicated microVM
- Only your project workspace is mounted into the sandbox
- Hypervisor-based isolation significantly reduces host risk

**A real development environment**

- Agents can install system packages, run services, and modify files
- Workflows run unattended, without constant permission approvals

**Safe Docker access for coding agents**

- Coding agents can build and run Docker containers inside the MicroVM
- They have no access to the host Docker daemon

**One sandbox, many coding agents**

- Use the same sandbox experience with Claude Code, Copilot CLI, Codex CLI, Gemini CLI, and Kiro
- More to come (and we’re taking requests!)

**Fast reset, no cleanup**

- If an agent goes off the rails, delete the sandbox and spin up a fresh one in seconds

## What’s New Since the Preview and What’s Next

The experimental preview validated the core idea: coding agents need an execution environment with clear isolation boundaries, not a stream of permission prompts. The early focus was developer experience, making it easy to spin up an environment that felt natural and productive for real workflows.

As [Matt Pocock](https://x.com/mattpocockuk) put it, *“Docker Sandboxes have the best DX of any local AI coding sandbox I’ve tried.”*

With this release, we’re making Sandboxes more powerful and secure with no compromise on developer experience.

## What’s New

- **MicroVM-based isolation** Sandboxes now run on dedicated microVMs, adding a hard security boundary.
- **Network isolation with allow and deny lists** Control over coding agent network access.
- **Secure Docker execution for agents** Docker Sandboxes are the only sandboxing solution we’re aware of that allows coding agents to build and run Docker containers while remaining isolated from the host system.

## What’s Next

We’re continuing to expand Docker Sandboxes based on developer feedback:

- **Linux support**
- **MCP Gateway support**
- **Ability to expose ports to the host device and access host-exposed services**
- **Support for additional coding agents**

Docker Sandboxes were made for developers who want to run coding agents unattended, experiment freely, and recover instantly when something goes wrong. They extend the usability of containers’ isolation principles but with hard boundaries.

If you’ve been holding back on using agents because of permission prompts, system risk, or Docker-in-Docker limitations, [Docker Sandboxes](https://docs.docker.com/ai/sandboxes/) are built to remove those constraints.

We’re iterating quickly, and feedback from real-world usage will directly shape what comes next.