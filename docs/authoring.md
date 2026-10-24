# Authoring the developer handbook

The handbook explains how TrackTemplate works and why its design serves a
railway task. A reader should understand a GUI operation from its inputs to
its result, then find the code needed to change it.

Use [GUI coverage](gui-coverage.md) to select a workflow. The wiki remains the
development journal. Keep dates, personal recollections and development
episodes there. Organise handbook chapters by concepts and working code paths.

This authoring profile adapts the workbench skills at revision
[`7965bfc`](https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf).
It governs this derived handbook. The workbench's
[TT-DOC-001 profile](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/ENGINEERING_POLICY.md#tt-doc-001-tracktemplate-technical-documentation-profile)
and technical-documentation management plan keep their existing authority.

## Start with the reader's problem

Choose one coherent workflow or calculation. State the railway or development
problem, the intended result, and the current implementation boundary. Explain
the necessary concepts before introducing their identifiers.

A chapter must teach the subject on the page. Source links let readers verify
and explore the explanation. They do not replace it.

For example, an easement chapter should explain curvature, station and tangent
before it follows the displacement calculation. A parameter-edit chapter
should explain the selected railway identity, replacement intent and document
transaction before it describes the callback sequence.

## Trace the whole GUI operation

For each workflow, establish these facts from the reviewed source:

1. **Entry point and purpose.** Name the visible control, its availability
   conditions and the task it serves. Check the final callback binding,
   including later method replacements in the retained host.
2. **Inputs and meaning.** Explain fields, defaults, units, signs, coordinate
   frames, identifiers and relationships. Distinguish typed input from values
   loaded from a document or calculated elsewhere.
3. **Code path.** Follow the UI handler through the application operation,
   railway calculation and adapters. Identify package and retained macro code.
4. **Algorithm and design intent.** Explain the equations, decisions and
   constraints that matter. Attribute recorded rationale to its source. Label
   any inference from the implementation.
5. **Result and state.** Show the returned data and the visible result. Name
   mutations, derived geometry, cache changes and saved properties. Explain
   Undo, persistence and export only where the operation actually uses them.
6. **Failure and recovery.** Cover meaningful invalid inputs, stale selections,
   unavailable actions and rollback. Preserve exact diagnostic text when quoted.
7. **Evidence and limits.** Link the relevant tests or retained runtime proof.
   State the representation and scope that each check covers.

Use one linked explanation for shared machinery such as transactions or
stationing. Each workflow page must still explain how that machinery affects
its own operation. Update the coverage row when the page is usable.

## Narrate the code

Keep a block short enough to discuss immediately. Introduce its purpose, show
the code, then explain the data or state change. Add intermediate values when
they make the calculation easier to follow.

Classify each block:

- **Runnable example:** include imports, inputs, environment requirements and
  the command or context needed to execute it. Use actual current symbols.
- **Source excerpt:** identify the file, revision and containing function.
  State which surrounding definitions it needs. Mark omissions.
- **Pseudocode:** label it explicitly. Do not present conceptual architecture
  names as callable API functions.

Do not rewrite executable code or exact identifiers to satisfy prose rules.
Keep the explanation around them clear. Avoid dumping a whole source file or
listing functions without explaining their relationships.

Explain relevant numerical distinctions. Nominal geometry, sampled coordinates,
viewport display and native exact geometry can have different contracts. State
which one the example produces. Keep prototype dimensions, model scale and
manufacturing adjustments distinct when the implementation distinguishes them.

Report how an example was checked. If it was only inspected against source,
say so. If a test or GUI session supplied the output, identify that evidence
and its revision. Run workbench examples under the workbench's own execution
guidance; a documentation build does not run them.

## Use sources according to their responsibility

| Question | Source to consult |
| --- | --- |
| What is the intended product? | [Product vision](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/PRODUCT_VISION.md) |
| Which state and dependency boundaries apply? | [Architecture](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/ARCHITECTURE.md) and [modularisation plan](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/MODULARISATION_PLAN.md) |
| What does this revision do? | Its implementation, final composition, configuration and tests |
| What was demonstrated? | The relevant retained validation result and its stated scope |
| What has the owner accepted now? | The separately labelled [live project plan](https://github.com/Richard-Gnitnub/tracktemplate/blob/main/reference/PROJECT_PLAN.md) and linked decisions |
| Which terminology and source restrictions apply? | [Terminology](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md), [provenance](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/PROVENANCE.md) and [licensing boundaries](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/LICENSING_BOUNDARIES.md) |

Pin implementation links to a complete commit SHA. A dated contract or
capability inventory describes its recorded scope. Compare it with current
code before using it for a present-tense claim. If sources disagree, record
the difference and keep the affected claim qualified until it is resolved.

The handbook can explain accepted requirements in reader-friendly terms. It
must link to their owner and preserve their meaning. A documentation edit does
not grant product acceptance, output clearance or authority to change a rule.

## Controlled English and STE100

Use UK English, active verbs, explicit actors and consistent terminology. Give
each paragraph one subject. Put a condition before the instruction it governs.
Explain technical terms when the reader first needs them. Preserve necessary
qualifications and numerical conditions when shortening prose.

Use the workbench's technical-term register. Keep code, UI labels, commands,
property names, diagnostics, equations, hashes and external quotations exact.
A new term that needs canonical approval remains a question for its owner;
the handbook must not silently approve it.

ASD-STE100 Issue 9 is the external controlled-writing reference used by the
upstream profile. Consult the official source when applying its vocabulary or
rules. Follow the upstream
[source and lookup instructions](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/external/asd-ste100/README.md).
Use a verified local official copy when available, or the
[official ASD/STEMG source](https://www.asd-ste100.org/). The
[Issue 9 PDF](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf)
is an external reference. Keep local reference material in ignored storage.

Use targeted lookup to find the source passages needed for the work. It does
not reduce the applicable rule set. For a formal Issue 9 assessment, the
reviewer must examine the complete named logical units against all applicable
requirements and record the official source, result, terms and limitations.

Keep these outcomes separate:

- **Handbook review completed:** the named candidate received the source,
  explanation, terminology and presentation review described here.
- **ASD-STE100 Issue 9 conformance not verified:** no sufficient formal review
  against the official standard exists for the named scope.
- **Formal conformance result:** report only the result supported by the named
  official-source review. A style checklist, lookup result or passing build
  cannot supply this result.

This adapted workflow does not establish TT-DOC-001 conformance or external
certification. If formal review is outside the task or the source is
unavailable, continue useful handbook work and state that conformance is not
verified. If the task specifically requires formal conformance, report the
remaining source or review gap. Keep upstream canonical-document changes on
the upstream route.

Do not publish the standard, its dictionary, extracted source text or lookup
caches as handbook content. Link to the official source. The repository needs
no paid writing service or additional publishing platform.

## One authoring and review cycle

1. Establish the reader need, page scope, source revision and technical owner.
   Read the relevant existing page before deciding to add another one.
2. Prepare the complete candidate. Check its claims, terminology, examples,
   links and assembled diff before handoff.
3. Identify the exact candidate with a Git commit, or a baseline, diff and file
   hashes. Include complete changed sections; review new pages in full.
4. Give that candidate to one independent reviewer. The reviewer returns one
   complete result and all necessary exact corrections. The reviewer does not
   edit the candidate or supply missing technical facts.
5. Apply the complete correction set once. Retain the original result and any
   unresolved findings. Run structural checks, the strict build and the
   relevant example checks. Inspect the rendered pages.
6. Report the final candidate, review, validation, example execution status,
   STE100 assessment status and limitations in the pull request.

For an objective validation defect, repair the defect and repeat the affected
check. Keep the original review result; do not start another stylistic review.
Do not hide a material unresolved fact to obtain a clean result. A new owner
requirement is new scope and must be identified as such.

Use Git and the pull request for the review record. No separate phase register,
documentation database or copied workbench receipt system is necessary here.
A small non-material correction needs its targeted check and diff review.

## Repository skills

The repository supplies these adaptations under `.agents/skills/`:

| Skill | Use |
| --- | --- |
| `$tracktemplate-docs-author` | Plan and write a narrated developer explanation, then coordinate its review and checks |
| `$tracktemplate-docs-ste100` | Consult the official standard within authoring or review and report the assessment boundary |
| `$tracktemplate-docs-review` | Review the fixed candidate independently and provide one complete correction set |
| `$tracktemplate-docs-align` | Find and correct documentation drift after a source or interface change |

The author skill includes a workflow template. Use the skills from the docs
checkout; its root `AGENTS.md` gives their paths and routing. For example:

```text
Use $tracktemplate-docs-author to explain the crossover Preview operation,
from its visible inputs through the solver and complete-radius preflight.
Use the source revision recorded in the GUI coverage map.
```

The adaptations draw on the upstream
[Technical Author Lead](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/.agents/skills/tracktemplate-technical-author-lead/SKILL.md),
[Documentation Review](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/.agents/skills/tracktemplate-documentation-review/SKILL.md),
[Documentation Alignment](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/.agents/skills/tracktemplate-documentation-alignment/SKILL.md)
and [Explain Change](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/.agents/skills/tracktemplate-explain-change/SKILL.md)
skills. They retain source ownership, controlled meaning, precise evidence and
a finite review cycle. They replace workbench-specific phase and tool paths
with this handbook's source tracing and Sphinx checks.

## Checks

From the pinned documentation environment, run:

```bash
python tools/validate_agent_skills.py
python -m sphinx -b html -n -W --keep-going docs _build/html
```

The first command checks skill discovery metadata and local guidance links.
The second builds the site. See [Testing and validation](testing.md) for their
limits. Review a changed page at desktop and narrow widths before publication.
