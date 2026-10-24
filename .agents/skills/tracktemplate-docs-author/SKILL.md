---
name: tracktemplate-docs-author
description: Write or materially revise TrackTemplate developer documentation that explains a GUI workflow, railway calculation, architecture or code path. Use for new handbook chapters, narrated code examples and design-intent explanations in tracktemplate-docs.
---

<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted for tracktemplate-docs on 2026-10-24. See ../../../NOTICE.md.
-->

# TrackTemplate docs author

## Establish the document need

Read [AGENTS.md](../../../AGENTS.md), the
[authoring guide](../../../docs/authoring.md), the existing affected page, and
the relevant [GUI coverage](../../../docs/gui-coverage.md) row.
Choose a new page, a material revision, a small correction, or no change.
Keep the change tied to the user's reader need.

Identify the source revision, reader question, visible workflow, technical
owner, implementation files and evidence needed. Keep current implementation,
recorded design intent and future direction distinct. Keep the wiki's journal
material outside the chapter.

Own the document work, not the technical requirement, terminology approval,
review verdict or product acceptance. Follow existing session authority for
repository changes. This skill does not add publication or merge authority.

## Build the explanation

Use [the workflow template](references/workflow-template.md) as a planning aid.
Adapt its headings to the subject; remove sections that do not apply.

1. Trace the actual control and final callback binding. Include availability,
   selection conditions, later method replacements and retained host code.
2. Explain each material input, its railway meaning, unit, frame, sign and
   relationship to other inputs. Distinguish supplied and derived values.
3. Follow the operation through UI, application, domain and adapters. Explain
   each responsibility before introducing its source identifier.
4. Show short real code blocks in dependency order. Label runnable examples,
   excerpts and pseudocode. Supply the context each block needs.
5. Narrate the algorithm, returned data and state changes immediately after
   the block. Use intermediate values where they clarify the calculation.
6. Explain design rationale from its owning source. Label reasoning inferred
   from code; do not invent rejected alternatives or historical intent.
7. Cover the result, invalid input, stale state and recovery. Explain selection,
   cache invalidation, transactions, Undo, persistence or export where relevant.
8. Link bounded tests or runtime evidence. Keep nominal geometry, sampled
   geometry, display and native output distinct. Report example execution
   accurately and preserve current capability limits.

Make the chapter useful without opening every source link. Keep shared
explanations in one handbook page and link to them. Keep normative requirements
and live acceptance with their workbench owners.

## Apply controlled writing

Use UK English and the upstream terminology register. Preserve exact code,
UI labels, diagnostics, properties, constants and units. Use **plain line** in
new prose. Avoid arbitrary shortening that removes controlled meaning.

Use [$tracktemplate-docs-ste100](../tracktemplate-docs-ste100/SKILL.md) within
authoring when consulting the standard. For formal conformance, require the
official Issue 9 source and full applicable review. Otherwise record that
Issue 9 conformance is not verified. Do not copy standard text or caches into
the repository.

## Deliver one candidate

Review the complete assembled diff, source claims, examples and links before
handoff. Check work from all contributing agents together. Preserve unrelated
accepted prose and frozen source evidence.

Identify the candidate by a Git commit or by its baseline, diff and file
hashes. Include complete changed logical units and all new pages. Route this
candidate to one independent
[$tracktemplate-docs-review](../tracktemplate-docs-review/SKILL.md).
Apply its complete exact correction set once. Keep its original verdict and
unresolved findings. Do not start a recurring language-review cycle.

Run the guidance validator, strict Sphinx build and relevant example checks
from the authoring guide. Inspect the rendered result. Repair an objective
validation defect and repeat its check. Do not rewrite technical meaning to
make a check pass.

Update the affected coverage row only to the depth actually delivered.
Report the exact candidate, source revision, review, checks, example execution
status, STE100 assessment status and remaining limitations. Keep the review
record in the pull request. Do not create workbench phase registers here.
