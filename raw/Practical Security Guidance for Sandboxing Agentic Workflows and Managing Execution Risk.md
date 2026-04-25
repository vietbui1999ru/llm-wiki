AI coding agents enable developers to work faster by streamlining tasks and driving automated, test-driven development. However, they also introduce a significant, often overlooked, attack surface by running tools from the command line with the same permissions and entitlements as the user, making them [computer use agents, with all the risks those entail](https://developer.nvidia.com/blog/from-assistant-to-adversary-exploiting-agentic-ai-developer-tools/).

The primary threat to these tools is that of indirect prompt injection, where a portion of the content ingested by the LLM driving the model is provided by an adversary through vectors such as malicious repositories or pull requests, git histories with prompt injections, `.cursorrules`, CLAUDE/AGENT.md files that contain prompt injections or malicious MCP responses. Such malicious instructions to the LLM can result in it taking attacker-influenced actions with adverse consequences.

Manual approval of actions performed by the agent is the most common way to manage this risk, but it also introduces ongoing developer friction, requiring developers to repeatedly return to the application to review and approve actions. This creates a risk of user habituation where they simply approve potentially risky actions without reviewing them. A key requirement for agentic system security is finding the balance between hands-on user input and automation. The following controls are what the NVIDIA AI Red Team considers either required or highly recommended, but ‌should be implemented to reflect your specific use case and your organization’s risk tolerance.

Based on the [NVIDIA AI Red Team](https://developer.nvidia.com/blog/nvidia-ai-red-team-an-introduction/) ’s experience, the following *mandatory* controls mitigate the most serious attacks that can be achieved with indirect prompt injection:

- Network egress controls: Blocking network access to arbitrary sites prevents exfiltration of data or establishing a remote shell without additional exploits.
- Block file writes outside of the workspace: Blocking write operations to files outside of the workspace prevents a number of persistence mechanisms, sandbox escapes, and remote code execution (RCE) techniques.
- Block writes to configuration files, no matter where they are located: Blocking writes to config files prevents exploitation of hooks, skills, and local model context protocol (MCP) configurations that often run outside of a sandbox context.

These *recommended* controls further reduce the attack surface, making host enumeration and exploration more difficult, limiting risks posed by hooks, local MCP configurations, and kernel exploits, and closing other exploitation and disclosure risks.

- Prevent reads from files outside of the workspace.
- Sandbox the entire integrated development environment (IDE) and all spawned functions (e.g., hooks, MCP startup scripts, skills, and tool calls), and, where possible, are run as their own user.
- Use virtualization to isolate the sandbox kernel from the host kernel (e.g., microVM, Kata container, full VM)
- Require user approval for every instance of specific actions (e.g., a network connection) that otherwise violate isolation controls. Allow-once / run-many is not an adequate control.
- Use a secret injection approach to prevent secrets (e.g., in environment variables) from being shared with the agent.
- Establish lifecycle management controls for the sandbox to prevent the accumulation of code, intellectual property, or secrets.

Note: This post doesn’t address risks arising from inaccurate or adversarially manipulated output from AI-powered tools, which are treated as user-level responsibilities.

## Why enforce sandbox controls at an OS level?

Agentic tools, particularly for coding, perform arbitrary code execution by design. Automating test- or specification-driven development requires that the agent create and execute code to observe the results. In addition, tool-using agents are moving toward [writing and executing throwaway scripts to perform tasks](https://www.anthropic.com/engineering/code-execution-with-mcp).

This makes application-level controls insufficient. They can intercept tool calls and arguments before execution, but once control passes to a subprocess, the application has no visibility into or control over the subprocess. Attackers often use indirection—calling a more restricted tool through a safer, approved one—as a common way to bypass application-level controls such as allowlists. OS-level controls, like macOS Seatbelt, work beneath the application layer to cover every process in the sandbox. No matter how these processes start, they’re kept from reaching risky system capabilities, even through indirect paths.

## Mandatory sandbox security controls

This section briefly outlines controls that the Red Team considers mandatory for agentic applications and the classes of attacks they help mitigate. When implemented together, they block simple exploitation techniques observed in practice. The section concludes with guidance on layering controls in real-world deployments.

### Network egress except to known-good locations

The most obvious and direct threat of network access is remote access (a network implant, malware, or a simple reverse shell), enabling an attacker access to the victim machine, where they can directly probe and enumerate controls and attempt to pivot or escape.

Another significant threat is data exfiltration. Developer machines often contain a wide range of secrets and intellectual property of value to an attacker, often even in a current workspace (e.g., `.env` files with API tokens). Exfiltrating the contents of directories such as ` ~/.ssh` to gain access to other systems is a major target, as is exfiltrating sensitive source code.

Network connections created by sandbox processes should not be permitted without manual approval. Tightly scoped allowlists enforced through HTTP proxy, IP, or port-based controls reduce user interaction and approval fatigue. Limiting DNS resolution to designated trusted resolvers to avoid DNS-based exfiltration is also recommended. A default-ask posture combined with enterprise-level denylists that cannot be overridden by local users provides a good balance between functionality and security.

### Block file writes outside of the active workspace

Writing files outside of an active workspace is a significant risk. Files such as `~/.zshrc` are executed automatically and can result in both RCE and sandbox escape. URLs in various key files, such as `~/.gitconfig` or `~/.curlrc`, can be overwritten to redirect sensitive data to attacker-controlled locations. Malicious files, such as a backdoored python or node binary, could be placed in `~/.local/bin` to establish persistence or escape the sandbox.

Write operations must be blocked outside of the active workspace at an OS level. Similarly to network controls, use an enterprise-level policy that blocks any such operation on known-sensitive paths, regardless of whether or not the user manually approves the action. These protected files should include dotfiles, configuration directories, and any additional paths enumerated by enterprise policy. Any other out-of-workspace file write operations may be permitted with manual user approval.

### Block all writes to any agent configuration file or extension

Many agentic systems, including agentic IDEs, permit the creation of extensions that enhance functionality and often include executable code. “Hooks” may define shell code to be executed on specific events (such as on prompt submission). MCP servers using an stdio transport define shell commands required to start the server. Claude Skills can include scripts, code, or helper functions that run as soon as the skill is called. Files such as `.cursorrules`, `CLAUDE.md`, `copilot-instructions.md`, can provide adversaries with a durable way to shape the agent’s behavior, and in some cases, gain full control or even arbitrary code execution.

In addition, agentic IDEs often contain global and local settings, including command allow and denylists, with local configuration settings in the active workspace. This can give attackers the ability to pivot or extend their reach if these local settings are modified. For example, adding a poisoned hooks configuration to a Git repository in a workspace can affect every user who clones it. Additionally, hooks and MCP initialization functions often run outside of a sandbox environment, offering an opportunity to escape sandbox controls.

Application-specific configuration files, including those located within the current workspace, must be protected from any modification by the agent, with no user approval of such actions by the IDE possible. Direct, manual modification by the user is the only acceptable modification mechanism for these sensitive files.

### Tiered implementation of controls

Defining universally applicable allow/denylists is difficult, given the wide range of use cases that agentic tools may be applied. The goal should be to block exploitable behavior while preserving manual user interventions as an infrequently-used fallback for unanticipated cases using a tiered approach such as the following:

1. Establish clear enterprise-level denylists for access to critical files outside the current workspace that can’t be overridden by user-level allowlists or manual approval decisions.
2. Allow read-write access within the agent’s workspace (with the exception of configuration files) without user approval.
3. Permit specific allowlisted operations (e.g., read from `~/.ssh/gitlab-key`) that may be required for the proper functionality of specific functions.
4. Assume default-deny for all other actions, permitting case-by-case user approval.

This post doesn’t specifically address command allow/denylisting, as OS-level restrictions should make command-level blocks redundant, though they may be useful as a defense-in-depth mitigation against potential sandbox misconfigurations.

The required controls discussed provide strong protection against indirect prompt injection and help reduce approval fatigue. However, there are remaining potential vulnerabilities, including:

1. Ingestion of malicious hooks or local MCP initialization commands.
2. Kernel-level vulnerabilities that lead to sandbox escape and full host control.
3. Agent access to secrets.
4. Failure modes in product-specific caching of manual approvals.
5. The accumulation of secrets, IP, or exploitable code in the sandbox.

The additional controls and considerations help close some of these remaining potential vulnerabilities.

### Sandbox IDE and all spawned functions

Many agentic systems only apply sandboxing at the time of tool invocation (commonly only for the use of shell/command-line tools). While this does prevent a wide range of abuse mechanisms, there remain many agentic functionalities that often default to running outside of the sandbox. These include hooks, MCP configurations that spawn local processes, scripts used by ‘skills’, or other tools managed at the application layer. This is often required when sandboxes are associated only with command-line tools, while file-editing tools or search tools execute outside of a sandbox and are controlled at the application level. These unsandboxed execution paths can make it easier for attackers to bypass sandbox controls or obtain remote code execution.

The sandbox restrictions discussed should be enforced for all agentic operations, not just command-line tool invocations. Restrictions on write operations for files outside of the current workspace and configuration files are the most critical, while network egress from the sandbox should only be permitted for properly configured remote MCP server calls.

### Use virtualization to isolate the sandbox kernel from the host kernel

Many sandbox solutions (macOS Seatbelt, Windows AppContainer, Linux Bubblewrap, Dockerized dev containers) share the host kernel, leaving it exposed to any code executed within the sandbox. Because agentic tools often execute arbitrary code by design, kernel vulnerabilities can be directly targeted as a path to full system compromise.

To prevent these attacks at an architectural level, run agentic tools within a fully virtualized environment isolated from the host kernel at all times, including VMs, unikernels, or Kata containers. Intermediate mitigations like gVisor, which mediate system calls via a separate user-space kernel, are preferable to fully shared solutions, but offer different and potentially weaker security guarantees than full virtualization.

While virtualization typically introduces some amount of overhead, it’s frequently modest compared to that induced by LLM calls. The lifecycle management of the virtualized environment should be tuned against the associated overhead required to minimize developer friction while preventing the accumulation of information.

### Prevent reads from files outside of the workspace

Sandbox solutions often require access to certain files outside of the workspace, such as `~/.zshrc`, to reproduce the developer’s environment. Unrestricted read access exposes information of value to an attacker, enabling enumeration and exploration of the user’s device, secrets, and intellectual property.

This follows a tiered approach consistent with the principle of least access:

1. Use enterprise-level denylists to block reads from highly sensitive paths or patterns not required for sandbox operation.
2. Limit allowlist external reads access to what is strictly necessary, ideally permitting reads only during sandbox initialization and blocking reads thereafter.
3. Block all other reads outside the workspace unless manually approved by the user.

### Require manual user approval every time an action would violate default-deny isolation controls

As described in the tiered implementation approach, default-deny actions that aren’t allowlisted or explicitly blocked should require manual user approval before execution. Enterprise-level denylists should never be overridden by user approval.

Critically, approvals should never be cached or persisted, as a single legitimate approval immediately opens the door to future adversarial abuse. For instance, permitting modification of `~/.zshrc` once to perform a legitimate function may allow later adversarial activity to implant code on a subsequent execution without requiring re-approval. Each potentially dangerous action should require fresh user confirmation.

### Use a secret injection approach to prevent secrets from being exposed to the agent

Developer environments commonly contain a wide range of secrets, such as API keys in environment variables, credentials in `~/.aws`, tokens in.`env` files, and SSH keys. These secrets are often inherited by sandboxed processes or accessible within the filesystem, even when they aren’t required for the task at hand. This creates unnecessary exposure.

Even with network controls in place, exposed secrets remain a risk.

Sandbox environments should rely on explicit secret injection to scope credentials to the minimum required for a given task, rather than inheriting the full set of host environment credentials. In practice:

- Start the sandbox with a simple or empty credential set.
- Remove any secrets that aren’t required for the current task.
- Inject required secrets based only on the specific task or project, ideally via a mechanism that is not directly accessible to the agent (e.g., a credential broker that provides short-lived tokens on demand rather than long-lived credentials in environment variables).
- Continue enforcing standard security practices such as least privilege for all secrets.

The goal is to limit the blast radius of any compromise so that a hypothetical attacker who gains control of agent behavior can only use secrets that have been explicitly provisioned for the current task and not the full set of credentials available in the host system.

### Establish lifecycle management controls for the sandbox

Long-running sandbox environments can accumulate artifacts over time from downloaded dependencies, generated scripts, cached credentials, intellectual property from previous projects, and temporary files that persist longer than intended. This expands the potential attack surface and increases the value of a compromise. When an attacker gains access to an agent operating in a stale sandbox, they may find secrets, proprietary code, or tools required for earlier work that can be repurposed.

The details of lifecycle management vary based on sandbox architecture, initialization overhead, and project complexity. The key principle is ensuring that the sandbox state doesn’t persist indefinitely, whether through:

1. Ephemeral sandboxes: Using sandbox architectures where the environment exists only for the duration of a specific task or command (e.g., Kata containers created and destroyed per execution), preventing accumulation.
2. Explicit lifecycle management: Periodically destroying and recreating the sandbox environment in a known-good state (e.g., weekly for VM-based sandboxes), ensuring accumulated state is cleared on a known schedule.

While the provider of the agentic tool is responsible for ensuring lifecycle management, organizations should evaluate their sandbox architecture and establish lifecycle policies that balance initialization overhead and developer friction against accumulation risk.

## Learn more

Agentic tools represent a significant shift in how developers work. They offer productivity gains through automated code generation, testing, and execution. However, these benefits come with a corresponding expansion of the attack surface. As agentic tools continue to evolve, gaining new capabilities, integrations, and autonomy, the attack surface evolves with them. The principles outlined in this post should be revisited as new features come out. Organizations should regularly validate that their sandbox implementations provide the isolation and security controls they expect.

Learn more about agentic security from the NVIDIA AI Red Team, including:

- The [risks of unsandboxed code](https://developer.nvidia.com/blog/how-code-execution-drives-key-risks-in-agentic-ai-systems/).
- Research on [agentic developer tools](https://developer.nvidia.com/blog/from-assistant-to-adversary-exploiting-agentic-ai-developer-tools/).
- How the AI Red Team does [threat modeling](https://developer.nvidia.com/blog/modeling-attacks-on-ai-powered-apps-with-the-ai-kill-chain-framework/) for agentic applications.