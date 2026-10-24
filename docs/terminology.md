<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted terminology guidance for the developer handbook, 2026-10-24.
-->

# Using TrackTemplate terminology

The handbook uses TrackTemplate's
[canonical terminology register][register]. Read its relevant entries before
writing or reviewing a technical explanation. The workbench register owns
the definitions and accepted wording; this page explains how to apply them
in the handbook.

**Reading baseline:** workbench revision
[`7965bfc4671668f889c1f43fb8336c5146c3f5cf`][revision], examined on
24 October 2026. The linked
[terminology-assurance contract][contract] records the railway term states,
review ownership and compatibility boundaries.

## Read the source before choosing a term

1. Identify the railway and project technical terms needed for the explanation.
   Record the workbench revision used for the terminology check. Normally use
   the chapter's implementation revision. If a later terminology decision
   applies to older code, identify both revisions.
2. Read each relevant entry in the actual register. Check its meaning, preferred
   form, context and exclusions. Consult the assurance contract when a railway
   term has a recorded review state.
3. Check the [technical nouns and verbs][technical-terms] as well as the
   [canonical track terms][track-terms]. A familiar word can have a specific
   project meaning. An approved noun does not automatically supply an approved
   verb.
4. Compare the explanation with the actual code and GUI labels. Preserve exact
   identifiers, quoted labels, commands, diagnostics and historical evidence.
   Explain a legacy label beside the quotation when readers need the distinction.
5. Record the source revision, relevant entries and any unresolved meaning in
   the pull request. The repository's PR template provides that field. A reviewer
   must check the meanings in context; a list of links alone is insufficient.

A local workbench checkout can supply the source if its revision is verified.
Otherwise read the pinned source links. If the source cannot be read, report
that gap and keep the affected terminology claim unverified. Do not reconstruct
an entry from memory or silently assign a new meaning.

## Preserve the terminology-assurance state

The [assurance control][assurance] distinguishes four states. Apply each state
to the precise context recorded upstream.

| State | Consequence for handbook prose |
| --- | --- |
| `accepted` | Use the preferred form within its accepted meaning and context. Acceptance does not establish usage for every railway, region or era. |
| `provisional` | Identify it as a working description. Preserve the evidence gap; do not present it as an established public fact or production designation. |
| `review-required` | Preserve and attribute observed wording where necessary. Explain the unresolved meaning and refer it to its workbench owner. Do not select a synonym to settle the question. |
| `frozen-legacy` | Retain exact wording in source excerpts, compatibility identifiers and reproducibility evidence. Use the accepted current form in new explanation only where the meanings match. |

Use an existing upstream review identifier when it applies. A new terminology
decision belongs with the workbench owner. Record unresolved findings in the
PR and keep the affected public explanation qualified. The handbook cannot
change a term's state by defining it locally.

The register also contains [candidate-bound admissions][candidate-terms]. Those
apply only to their named candidate and occurrences. Their presence does not
grant general permission to reuse a meaning in a new chapter. Read the stated
context and exclusions before relying on an entry.

## Distinctions that matter in this handbook

These examples apply the linked register; they are a reading aid, not a
complete term register.

| Term or context | How to use it |
| --- | --- |
| **Plain line track** | Track without switches and crossings. It can be straight or curved. Use **plain line** after introducing the term and **plain-line** when it modifies another noun. [Track terms][track-terms] |
| **Straight** and **curve** | Describe alignment shape independently of whether the track is plain line or contains S&C. [Track terms][track-terms] |
| **Easement** or **transition** | Name the mathematical subtype where the behaviour depends on it. For the [transition-edit walkthrough](handbook/transition-edit.md), that subtype is Euler (clothoid). [Contextual register][contextual-register] |
| **Station** or **chainage** | State the owning centreline, origin and travel direction. Explain that the value locates a position along that centreline. [Contextual register][contextual-register] |
| **Alignment** and **documentation alignment** | An alignment is a track centreline with a specified travel direction. Use **documentation alignment** for reconciling a page with its sources. [Track data][track-data]; [assurance operations][assurance-operations] |
| **Sleeper**, **timber** and source chair labels | Preserve the specific component or source meaning. The register keeps support taxonomy and some chair designations under review; they are not interchangeable labels. [Contextual register][contextual-register] |
| **S1** and **L1** in Phase 9 research packages | These are source designations in that stated context. The labels alone do not establish independent prototype identification or production acceptance. [Chair-definition package][chair-package] |

The [writing and naming rules][naming] reserve `ordinary_track` and related
legacy evidence names for their existing compatibility or historical use.
Keep an actual identifier exact in a code walkthrough. Use **plain line** in
new railway-category prose when that is the intended meaning. Do not apply
that replacement to source chair or timber classifications without their own
review.

## Apply the register throughout the authoring workflow

The author skill reads the applicable entries before drafting. The STE100
helper preserves their technical meanings while checking the surrounding
language. The independent reviewer checks the recorded terms against the
actual prose, excerpts and source context. The documentation-alignment skill
compares the register's old and new entries when a source update affects a page.

When a terminology decision changes, update the affected explanation, source
revision and qualifications together. Preserve historical quotations and
compatibility identifiers. The [authoring guide](authoring.md) supplies the
review and validation steps.

The structural validator checks local guidance links; Sphinx checks the site
build. Neither establishes correct railway meaning or formal ASD-STE100
conformance. The project register supplies technical terminology within its
stated scope. A formal STE100 assessment also needs the official standard and
the applicable review described in the authoring guide.

[register]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md
[revision]: https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf
[contract]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/contracts/phase1-terminology-assurance.json
[assurance]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md#assurance-control
[technical-terms]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md#asd-ste100-project-terminology
[track-terms]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md#canonical-track-terms
[contextual-register]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md#current-contextual-register
[candidate-terms]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md#candidate-bound-inventory-terminology
[track-data]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md#L205-L207
[assurance-operations]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md#L133
[chair-package]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md#L201-L214
[naming]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md#project-writing-and-naming
