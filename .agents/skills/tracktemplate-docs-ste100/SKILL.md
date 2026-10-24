---
name: "tracktemplate-docs-ste100"
description: "Assist the TrackTemplate handbook author or sole reviewer with precise UK English, project terminology and ASD-STE100 Issue 9 source checks. Use for language guidance or a named formal conformance scope; never treat a style check or Sphinx build as formal conformance."
---
<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted for tracktemplate-docs on 2026-10-24. See ../../../NOTICE.md.
-->

# TrackTemplate handbook STE100 helper

## Responsibility

Read the [shared authoring profile](../../../docs/authoring.md) first.
Assist the author before candidate freeze or the sole handbook reviewer during
the existing review. Return guidance or findings to that role. Do not create a
second linguistic verdict, correction cycle or approval stage.

Use the derived handbook profile by default. Its UK English and clarity rules
do not establish ASD-STE100 Issue 9 conformance or TT-DOC-001 conformance.
Do not claim certification, endorsement or conformity from this skill's use.

## Choose and record the scope

1. Identify the exact prose and its purpose: explanation, procedure or reference.
2. Identify the technical source, terminology owner and workbench revision.
3. State whether the task requires handbook language guidance or a named formal
   Issue 9 review. Do not silently convert one route into the other.
4. Keep code and other exact content separate from the surrounding prose.
   Record relevant exclusions without using them to exempt ordinary explanation.

For handbook guidance, use the project profile and
[Using TrackTemplate terminology](../../../docs/terminology.md). Read the
relevant upstream entries at the recorded revision. Check meaning, preferred
form, assurance state and context; candidate-bound admissions are not global.
Record the entries consulted and any source gap in the PR's terminology field.
Explain an unfamiliar technical term when the reader needs it. Do not create
a second canonical term register or approve a disputed meaning.

## Preserve technical meaning

- Preserve code, API and schema identifiers, keys, values, paths, hashes,
  commands, quoted UI labels, diagnostic text and other exact source content.
- Preserve units, tolerances, algorithms, conditions, ordering, exceptions,
  provenance, rights status and every qualification that limits a claim.
- Keep implementation, future intent, evidence, inference and unresolved
  questions distinguishable. Language editing cannot supply missing proof.
- Use the upstream railway meaning of a term. Do not turn plain line into
  straight track or remove a mathematical subtype from an easement explanation.
- Keep historical or external quotations accurate and attributed. Clarify
  difficult wording outside the quotation; do not silently rewrite the source.

## Apply the handbook language profile

Use UK English, explicit actors and concrete verbs. Remove an ambiguous pronoun
only when its intended referent is evidenced. Keep one coherent topic in each
paragraph and connect the explanation to the actual code.

For a procedure, state prerequisites and conditions before the affected action.
Give one operation per step and identify the observable result or failure.
For a design explanation, retain the rationale, constraints and trade-offs.
Do not force explanatory prose into a sequence of commands.

Keep necessary technical detail. Do not substitute a simpler word when it
changes the meaning, and do not impose an arbitrary word or sentence count.
Preserve the user's intended meaning when suggesting a more direct sentence.

## Handle a formal Issue 9 request

Use the official ASD/STEMG Issue 9 source, supplied with authorised access or
obtained from the [official source](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf).
Record the edition, source identity, reviewed unit and candidate identity.
Do not use model recollection, project summaries or a word list as the standard.

Review all applicable writing and vocabulary requirements for the named scope.
Targeted retrieval can locate relevant source material; it does not narrow the
applicable requirements. Check technical-term use against the governing rules
and the upstream project register where applicable.

If the official source or sufficient review evidence is unavailable, report
"Issue 9 conformance not verified". Continue useful source and handbook-profile
checks, and identify the formal review limitation without suggesting approval.

Do not copy the standard, dictionary, extracted text or derived caches into this
repository. Do not add the official PDF as a Sphinx or CI dependency.
A formal review must record its scope, result, terms, exclusions and limitations.
It does not establish the wider TT-DOC-001 governance controls by itself.

## Return bounded assistance

Before freeze, give the author concrete language guidance with its basis.
During the sole review, provide all findings together, with exact paths,
preimages and replacements for corrections that the evidence supports.
For a formal rule finding, identify the official rule and source used.

Leave unresolved engineering facts or term meanings with their subject owner.
Do not invent exact replacement facts or start another review to improve style.
Keep Sphinx, spelling and other mechanical results separate from formal
linguistic evidence. This helper grants no publication or acceptance authority.
