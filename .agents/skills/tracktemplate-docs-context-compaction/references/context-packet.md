<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted for tracktemplate-docs on 2026-10-24. See ../../../../NOTICE.md.
-->

# Documentation context packet

Use this temporary navigation record while the evidence is available. Replace
placeholders with verified facts, `unknown`, or `not applicable`. Keep the active
facts concise and link retained evidence. Include only task-relevant material;
retain an exact correction set by reference when it is too large for the packet.

```text
Task identifier and packet role (lead or assigned worker):
Prepared / verified at (UTC):
Compressed navigation; not authority, a backup, or a Git recovery checkpoint.

Objective and requested deliverable:
Latest user steering and accepted corrections (exact where material):
Established authority and limits (source; publication and merge separately):

Repository identity and workspace path:
Branch / baseline / HEAD / existing named Git state:
Dirty and untracked paths — known owner or unknown — purpose:
Where actual changed files and evidence are preserved; persistence limits:
Task-relevant recovery warnings, including any known retained stash:

Must-retain requirements, identifiers, units, diagnostics and qualifications:
Workbench source revision and inspected paths:
Terminology source revision and entries read:

Active work:
- Completed and verified actions:
- Unfinished action and current failure, if any:
- Exact failing command, environment, result and evidence path:

Authoring and review:
- Stage reached:
- Candidate commit, or baseline plus diff and file hashes:
- Original review scope, verdict and complete correction-set reference:
- Corrections applied / pending; unresolved findings:
- Validation command, environment, result, candidate and evidence:
- Example status (source-inspected / executed / named retained evidence):
- STE100 assessment scope and status:

External actions:
- Action — planned / submitted / confirmed / unknown — actual reference:
- Unknown outcome — read-only verification required before any retry:

Delegation:
- Agent/task identifier — assignment — permitted files/actions:
- Own packet/evidence path — observed status and time — reported result:
- Pending dependency; lead verification or integration still required:

Sources retained by reference — pinned path/URL and reason needed:
Cold or excluded material — reason excluded and retrieval trigger:
Contradictions, unavailable evidence and unverified claims:
Next authorised action and nearest proof:
```

## Loss check

Check the packet against the actual request, files and evidence. Preserve dirty
paths and ownership uncertainty, exact failures, source revisions and the
original review result. Do not change `planned` to `confirmed`, `source-inspected`
to `executed`, or an unresolved finding to acceptance while shortening text.

A source path is useful only if the receiving agent can access it. Identify
local-only evidence and expired or uncertain process handles. Do not assume
that a fresh workspace contains uncommitted files. When a known retained stash
matters, identify it precisely; a packet does not authorise its removal.

Keep credentials, unnecessary personal data, hidden reasoning, full transcripts,
private raw logs and official STE source extracts out of the packet. Do not
publish it automatically. Follow the storage and single-writer rules in the
[compaction skill](../SKILL.md).
