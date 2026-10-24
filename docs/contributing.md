# Contributing

A useful contribution starts with one clear problem and the source that owns
its requirements.

Read the workbench's [project guidance](https://github.com/Richard-Gnitnub/tracktemplate/blob/54c5903b41e89d1fdfb430c812495e36b91d690b/AGENTS.md) and
[contribution guide](https://github.com/Richard-Gnitnub/tracktemplate/blob/54c5903b41e89d1fdfb430c812495e36b91d690b/CONTRIBUTING.md) before changing its code.
They own the change, authorship, source-attribution and review requirements.
The contribution guide includes the Developer Certificate of Origin sign-off
and the declarations needed for railway data and other evidence.

When changing the workbench, follow these files at the revision you are
actually changing. The links here provide the documented reading baseline.

## Report a documentation issue

Search the [documentation issues](https://github.com/Richard-Gnitnub/tracktemplate-docs/issues)
for an existing report, then [open an issue](https://github.com/Richard-Gnitnub/tracktemplate-docs/issues/new/choose)
with the relevant form:

- **Documentation bug report** covers incorrect or unclear content, broken
  links or examples, and problems with the site or documentation build. Include
  the affected page or source, the problem and the expected result.
- **Documentation feature proposal** covers new developer guides, examples,
  reference material, navigation and documentation tooling. Describe the reader
  need, the proposed improvement and where it belongs.

Use the [workbench issue tracker](https://github.com/Richard-Gnitnub/tracktemplate/issues)
for workbench behaviour or product features.

## Changes to this documentation

Use a page for one reader task. Give the reader a short explanation and a
direct link to the relevant source. Keep technical names, paths and commands
exact.

For new developer chapters, follow [Authoring the handbook](authoring.md).
Use [GUI coverage](gui-coverage.md) to select a workflow, then explain its
purpose, inputs, real code path, results and failure behaviour. The repository
skills provide authoring, STE100 assistance, independent review and documentation
alignment. Follow [Using TrackTemplate terminology](terminology.md) and record
the upstream entries you checked in the pull request's terminology field.
The [transition-edit chapter](handbook/transition-edit.md) shows this approach.

If a proposed edit changes a technical requirement, first identify its owner
in [Reference](reference.md). The
[Technical Documentation Profile](https://github.com/Richard-Gnitnub/tracktemplate/blob/54c5903b41e89d1fdfb430c812495e36b91d690b/reference/ENGINEERING_POLICY.md#tt-doc-001-tracktemplate-technical-documentation-profile)
and its documentation-management provisions own the applicable authoring and
review route. A page on this site does not replace that authority.

Keep the source revision visible when a page explains a particular snapshot.
Use the separately labelled live status link for current progress. This helps
a reader distinguish a historical explanation from the current project state.

After a site edit, run the strict HTML build in
[Development environment](development.md) and inspect the changed page.
The [testing page](testing.md) explains what that check establishes.

## Scope of the handbook

The handbook helps developers understand GUI operations, railway calculations,
state changes and design intent. It also links the existing engineering
sources. Later modeller guidance is tracked in
[issue #179](https://github.com/Richard-Gnitnub/tracktemplate/issues/179).
The broader consolidation of decisions and evidence is tracked separately in
[issue #180](https://github.com/Richard-Gnitnub/tracktemplate/issues/180).
