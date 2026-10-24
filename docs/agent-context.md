<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted for tracktemplate-docs on 2026-10-24. See ../NOTICE.md.
-->

# Agent context and recovery

A long documentation task can outlast the conversation context that an agent
has available. The agent needs enough retained state to continue the right
task, preserve edits and distinguish completed work from the next action.

This repository supplies two skills:

- **`tracktemplate-docs-context-compaction`** prepares a concise context packet
  while the task evidence is available.
- **`tracktemplate-docs-context-recovery`** checks that packet against current
  instructions, files and external records, then resumes the authorised work.

The first skill prepares for a context change. The host application controls
the actual compaction of conversation history. The packet does not change a
context limit, start a new chat or guarantee that an agent remembers every fact.

## What the packet preserves

Suppose an agent has written a chapter and received an independent review.
Two corrections remain. A Sphinx build passed for the earlier candidate, and a
PR creation request was interrupted before its response arrived. A useful
packet preserves those distinctions. The recovering agent must inspect the
current files, finish the remaining corrections, check the resulting candidate
and establish whether the PR already exists before submitting another request.

The shared template records:

- The user objective, latest steering, established permissions and limits.
- The repository, branch, commit, dirty paths and ownership of unfinished work.
- The workbench source revision, relevant terminology entries and evidence.
- The exact authoring stage, candidate, original review result and corrections.
- Validation commands and results, including which candidate each check covers.
- External actions, worker assignments, unresolved facts and the next action.

Keep exact identifiers, failures and qualifications. Summarise background and
link its source. Load unrelated history only when the task requires it. A
packet should let the next agent find evidence without repeating the entire
investigation.

This follows the workbench's
[context-recovery skill](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/.agents/skills/tracktemplate-context-recovery/SKILL.md)
and [context-packet format](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/.agents/skills/tracktemplate-context-recovery/references/context-packet.md)
at `7965bfc`. The documentation adaptation retains the
[finite authoring and review cycle](authoring.md#one-authoring-and-review-cycle)
and uses separate lead and worker packets. It does not import the workbench's
phase registers or create another project journal.

## When the skills run

The root `AGENTS.md` routes agents to the skills. Their descriptions support
task matching, and their `agents/openai.yaml` files allow implicit invocation.
These are instructions and discovery metadata; they do not install a timed
job or a platform event hook.

| Situation | Agent action |
| --- | --- |
| The user asks to save context, prepare for compaction or hand work over | Prepare or update the context packet |
| A long task reaches a substantial source, review, validation or publication result | Update the packet when the material state has changed |
| The host supplies a context warning or a known transition is approaching | Prepare a packet while the evidence is available |
| Work resumes after compaction, interruption or a long pause | Verify current state and resume through the recovery skill |
| No packet survives | Reconstruct from the current request, repository and accessible evidence; mark unknown facts |

There is no need to wait for a claimed token percentage. Preparing packets at
useful milestones reduces dependence on receiving a warning just before the
host compacts context. It also avoids filling the conversation with repeated
summaries after every tool call.

### ChatGPT, Codex and the API

OpenAI's [skill documentation](https://learn.chatgpt.com/docs/build-skills)
describes explicit selection and implicit matching against a skill's
description. The host initially loads metadata and reads the full instructions
when it selects the skill. Codex discovers repository skills in `.agents/skills`
from the working directory through the repository root.

Committing these files makes them available in this checkout. It does not
install them into every ChatGPT Pro conversation. A ChatGPT session needs an
available installed skill, or access to the repository instructions and files
so the agent can read and follow them. Where a skill is available in ChatGPT's
selector, use `@`; Codex CLI and IDE users can select `/skills` or mention its
`$name`. These discovery details were checked on 24 October 2026.

| Environment | Compaction control and this repository's boundary |
| --- | --- |
| ChatGPT Pro conversation | This repository sets no host compaction threshold. The cited documentation does not establish a Pro-specific threshold or a guaranteed pre-compaction callback for these skills. Use packets and recovery without promising either. |
| Codex CLI | The documented [`/compact` command](https://learn.chatgpt.com/docs/developer-commands) summarises the visible chat. Save the packet before deliberately using it. Do not assume that this CLI command exists in the ChatGPT composer. |
| An application built with the Responses API | The [API compaction guide](https://developers.openai.com/api/docs/guides/compaction) describes `context_management` with `compact_threshold`, and a separate `/responses/compact` endpoint. These are application controls. This documentation workflow does not call the API or configure them. |

The skills add no service, runtime dependency or paid publishing tool. They use
the existing repository workflow and the agent environment already in use.

### Requests you can use

When an agent can access this repository, a plain-language request is enough
to direct it to the files:

```text
Read AGENTS.md and use the context-compaction skill to save the current
TrackTemplate docs task. Preserve the review result and unfinished edits.
Continue the authorised work after saving the packet.
```

In a Codex checkout where local skills are discovered:

```text
Use $tracktemplate-docs-context-recovery to resume this documentation task.
Verify the packet against the working tree and current PR before continuing.
```

Neither request needs to ask the host to compact the conversation. The recovery
skill can also run without a saved packet when sufficient evidence survives.

## Lead and worker agents

OpenAI's [subagent guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents)
describes delegated agent threads and returning summaries to the main agent.
For this repository, the lead must provide each worker with its task, source
pins, permitted paths, relevant instructions and expected result. Do not assume
that a worker can see every message or skill already loaded by the lead.

| Actor | Packet responsibility |
| --- | --- |
| Lead agent | Preserve the whole user objective, shared candidate, worker assignments, received findings and remaining integration work |
| Worker agent | Preserve its assigned subtask, permitted changes, sources, results, unresolved questions and next subtask action |

Use one writer per packet. A worker returns its result and packet location to
the lead; it does not overwrite the lead's record or declare the whole task
complete. After an interruption, check actual agent and process status where
the host permits it. A recorded identifier does not prove that a worker is
still running or can be resumed.

## Storage and recovery limits

A short packet can stay in the conversation. For a continuing task that
benefits from a file, use the existing ignored `.local/` area:

```text
.local/context/<task-id>/lead.md
.local/context/<task-id>/workers/<worker-id>.md
```

These are temporary local files. They may not survive a fresh workspace. A
packet must say where the actual changed files and evidence are preserved;
describing uncommitted work does not preserve its contents. Cross-session
continuity requires access to those files and an already authorised durable
destination for any necessary packet. Do not automatically commit or publish
operational notes.

The workbench [terminology register](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md)
defines a **checkpoint** as named Git state and a **context packet** as the
route to that state. The packet is not a backup or a Git recovery checkpoint.
Keep credentials, unnecessary personal data, full transcripts, private raw
logs and official STE source extracts out of it.

During recovery, current instructions and owning sources take precedence over
the packet. Preserve established permissions, but verify live file and PR
state. Do not discard dirty work, retry an uncertain publication blindly or
repeat a completed stylistic review just because the conversation was
compacted. If an essential fact cannot be recovered, identify that specific
gap and continue the unaffected work.

## What validation can establish

The repository's skill validator checks metadata and local links. The strict
Sphinx build checks the guide's structure and references. A fresh agent can
exercise the skills against a bounded task to check whether it preserves and
recovers the required state.

Those checks do not force ChatGPT to compact, establish its internal trigger,
guarantee a platform callback or prove that a packet survives a workspace
reset. Keep any reported test result within the behaviour actually exercised.
