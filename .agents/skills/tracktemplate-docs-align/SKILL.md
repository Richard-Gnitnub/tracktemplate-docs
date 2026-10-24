---
name: tracktemplate-docs-align
description: Audit and reconcile TrackTemplate handbook claims after changes to GUI controls, code, architecture, terminology or evidence. Use for stale examples, broken source mappings, incomplete GUI coverage or conflicts between the handbook and the reviewed workbench revision.
---

<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted for tracktemplate-docs on 2026-10-24. See ../../../NOTICE.md.
-->

# TrackTemplate docs alignment

## Bound the audit

Read [AGENTS.md](../../../AGENTS.md), the
[authoring guide](../../../docs/authoring.md), the affected pages and relevant
[GUI coverage](../../../docs/gui-coverage.md) rows. Identify the triggering
change, previous documented revision and proposed source revision.

Keep the audit targeted unless the user asks for a complete review or concrete
evidence shows wider drift. Preserve unrelated work and historical evidence.
Keep the workbench's technical requirements and acceptance with their owners.

## Verify each affected claim

1. Locate the visible GUI control, availability conditions and final callback
   binding. Check later method replacements and composition adapters.
2. Trace the current input schema, calculations, output and mutations. Compare
   the page's actual code blocks, values, units and diagnostics with the source.
3. Compare rationale with its recorded owner. Identify any inference that the
   page presents as an accepted design decision.
4. Compare validation claims with the named evidence and its revision. Keep
   standalone, native FreeCAD, GUI and export evidence distinct.
5. Check whether a former limit remains, a new route exists or a documented
   function moved. Read current code and current status owners; a historical
   extraction contract cannot establish today's whole capability inventory.
6. Check the recorded STE100 assessment scope. Do not carry a previous formal
   result onto materially changed prose without sufficient new review.

Classify a material finding as `VERIFIED`, `STALE`, `CONTRADICTORY`,
`DUPLICATED`, `ORPHANED` or `CANNOT_VERIFY`. Give its page location, source and
reader consequence. Report material findings before making the authorised
corrections; do not request confirmation for routine in-scope fixes.

## Reconcile the handbook

Correct the affected explanation and its pinned source links together. Preserve
meaning, exact identifiers and useful qualifications. Keep a conflict visible
until the correct source owner resolves it. Do not change an upstream rule or
silently erase a limitation to match current code.

Preserve the handbook's explanatory prose when replacing a stale source link.
Do not reduce a chapter to a list of references. Update coverage only to the
depth verified. Keep shared explanations in their existing handbook owner.

For material prose changes, use
[$tracktemplate-docs-author](../tracktemplate-docs-author/SKILL.md) and its one
independent review. Use
[$tracktemplate-docs-ste100](../tracktemplate-docs-ste100/SKILL.md) when the
standard is relevant. Keep formal conformance unverified without sufficient
official-source review. A small link or factual correction needs a targeted
check and diff review.

Run the guidance validator and strict Sphinx build. Recheck changed source
links, examples and navigation. Do not create a new phase dashboard, source
authority register or recurring stylistic review.

Report the audit scope, source revisions, findings, applied corrections,
review and validation results, and claims that remain unverified.
