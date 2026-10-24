---
name: tracktemplate-docs-context-compaction
description: Prepare a concise TrackTemplate documentation context packet before compaction, a handoff or a long pause, or at a substantial milestone in a long task. Preserve decisions, dirty work, source pins, review state and next actions. This skill does not invoke or configure platform compaction.
---

<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted for tracktemplate-docs on 2026-10-24. See ../../../NOTICE.md.
-->

# Prepare a documentation context packet

## Purpose and triggers

Save the operational state needed to continue the authorised task. Use this
skill when asked to preserve context, before a known context transition or
agent handoff, and after a substantial source audit, candidate freeze, review,
validation or publication result in a long task. Update an existing packet
when its material state changes; do not write a new log after every tool call.

Follow [AGENTS.md](../../../AGENTS.md) and
[Agent context and recovery](../../../docs/agent-context.md). The host owns
actual compaction. Do not invent a token percentage, claim that a packet
forces compaction, install a hook, or promise a callback before every automatic
compaction. If the host exposes a warning, use it as an additional cue.

## Prepare the packet

1. Recover the user's objective, latest steering, accepted corrections,
   permissions and limits from the available conversation. Record exact
   wording where it affects scope or authority, with its source. A summary
   cannot grant authority or override the current instructions.
2. Check the task's repository identity, branch, baseline, HEAD and relevant
   working-tree changes. Identify dirty and untracked paths, their owners and
   their purpose. Record unknown ownership rather than assigning it to yourself.
   Do not commit, stash, reset, switch branches or remove files to prepare a
   packet. Record existing named Git state and task-relevant recovery warnings.
3. Use the shared [context-packet template](references/context-packet.md).
   Preserve exact source revisions, identifiers, failures and qualifications.
   Keep the active task and next action explicit. Link bulky evidence instead
   of copying tool logs. Record material exclusions and when to retrieve them.
4. Preserve the finite authoring stage: candidate identity, original review
   verdict, complete correction set, applied corrections, unresolved findings
   and validation tied to that candidate. Keep source-inspected examples,
   executed examples and retained evidence distinct. A build pass is not
   technical acceptance or verified STE100 conformance.
5. Record external actions as planned, submitted, confirmed or unknown, with
   the actual commit, PR, issue or build reference when available. An interrupted
   response does not prove that publication failed. Record the verification
   needed before a retry.
6. For delegated work, record each relevant agent's assigned scope, permitted
   paths, reported result and outstanding dependency. Distinguish a worker's
   report from the lead's verified integrated result. Process and agent handles
   may expire; preserve the evidence needed if they cannot be resumed.

## Store and verify

Use conversation state for a short packet. When a file helps a continuing task,
use the existing ignored `.local/` area, with one writer per file:

```text
.local/context/<task-id>/lead.md
.local/context/<task-id>/workers/<worker-id>.md
```

Choose stable task and worker identifiers. The lead owns `lead.md`; a worker
writes only its assigned packet and returns its path and findings to the lead.
A read-only worker returns the packet in its response. Do not overwrite another
agent's packet. Check that a file is saved and ignored before reporting it.

The packet is temporary navigation, not a backup or Git recovery checkpoint.
A local file may disappear with the workspace. Record where actual changed
files and evidence are preserved. Use an already authorised durable destination
when cross-session persistence is required; otherwise state the limitation.
Do not automatically publish a packet or add it to a commit. Keep secrets,
credentials, unnecessary personal data, hidden reasoning, whole transcripts,
raw private logs and official STE source extracts out of it.

Before relying on the packet, compare it with its sources. Check the objective,
exact decisions, dirty paths, source pins, failures, review status, action status
and next step. Mark compressed background and unsupported claims explicitly.
Correct omissions while the evidence is still available.

Report the packet location or include the short packet, its verification time,
and the next action. Continue the authorised task unless the user requested a
pause. After a context change, use
[$tracktemplate-docs-context-recovery](../tracktemplate-docs-context-recovery/SKILL.md).
