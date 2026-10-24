---
name: "tracktemplate-docs-review"
description: "Review a frozen TrackTemplate handbook change for technical fidelity, source authority, code explanations and clear language. Use after the author supplies the complete candidate; return one review with all necessary exact corrections."
---
<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted for tracktemplate-docs on 2026-10-24. See ../../../NOTICE.md.
-->

# TrackTemplate handbook review

## Responsibility

Read the [shared authoring profile](../../../docs/authoring.md) first.
Review the complete frozen scope supplied by the author. Remain read-only.
Do not author the candidate, apply corrections, approve upstream engineering
decisions, or give merge, release, phase or output-use acceptance.

Use the handbook profile unless the task specifies a formal STE100 scope.
A handbook review result does not establish ASD-STE100 or TT-DOC-001
conformance. Use `$tracktemplate-docs-ste100` to assist this same review when
language or formal-standard checks need it; do not add another review stage.

## Establish the review scope

1. Record the candidate commit, or its baseline, diff and file hashes.
   Record the paths and complete logical units under review.
2. Read the relevant pinned workbench sources and the source map supplied by
   the author. Include actual implementation and evidence for behaviour claims.
3. Identify each unit as explanation, procedure, reference, historical evidence
   or proposed design. Apply the checks appropriate to that purpose.
4. Keep unrelated accepted wording outside the scope. Expand only where a
   changed statement requires surrounding context to preserve its meaning.

## Check technical fidelity

- Follow each GUI walkthrough from the actual label and command handler to
  the application, domain, adapter and output paths that it uses. Do not infer
  a complete GUI route from an isolated function or a module name.
- Check code excerpts against the cited revision. Preserve identifiers, UI
  text, diagnostics, commands, units, numerical limits and required context.
  Label omissions and distinguish executable examples from illustrative code.
- Check that narration explains inputs, relevant state changes, derived
  results, failure behaviour and the reason for the design.
- Distinguish implemented behaviour, intended design, historical evidence and
  unresolved questions. Keep headless evidence separate from GUI acceptance.
- Check source authority and revision dates. A handbook explanation can teach
  the design; it must not replace upstream requirements, terminology or status.
- Preserve qualifications, provenance, licence boundaries and output-use
  limits. Do not resolve a technical or rights question by changing its words.
- Check that a claimed common GUI, Python or AI route has implementation
  evidence. Identify future interfaces as intent when no route is implemented.

## Check readability and navigation

Use precise UK English, explicit actors and consistent railway terminology.
Put conditions before procedural actions and use one operation per step.
Keep explanations connected: state what the code does and why it matters.

Keep source-grounded explanations and useful code narration even when they
repeat a concept from an upstream owner. Link the owner for authority.
Do not replace an explanation with links alone or remove necessary detail to
meet a sentence limit. Request wording changes only for a concrete defect.

Check headings, cross-references, code captions and neighbouring qualifications.
Treat a successful Sphinx build as build evidence only; it does not establish
technical correctness, runtime acceptance or linguistic conformance.

## Return one complete review

Return `ACCEPT`, `APPROVED_WITH_EXACT_CORRECTIONS` or `BLOCKED` for the
frozen handbook candidate. State the reviewed identity, scope, evidence and
limitations. Report formal STE100 verification separately when it applies.

For every correction, provide the exact path, preimage and replacement.
Add a location and surrounding context when the preimage is not unique.
Explain the concrete defect and cite its source or applicable profile rule.
Give the complete correction set in this review, including when blocked.

For unresolved technical facts, identify the claim, missing evidence and
upstream subject owner. Preserve uncertainty; do not invent a replacement
fact. A blocker can remain unresolved after every wording correction is applied.

The author applies the complete authorised correction set once and verifies
the exact changes and deterministic build checks. Do not reopen wording for
another preference pass. Repair an objective validation defect against its
specific evidence without starting a new stylistic cycle.

Do not create phase registers, acceptance records, STE caches or replacement
policy owners in this repository. Use the existing Git and pull-request record.
