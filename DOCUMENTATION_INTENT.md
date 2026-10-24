## Summary

Establish TrackTemplate's developer documentation from the existing Sphinx Companion project. Start with a small, working site for contributors. User documentation follows later, when the product can support it.

This records the owner's documentation intent from 24 October 2026. The initial implementation uses the stack below, with Read the Docs hosting to follow review of the draft pull request.

## Problem or opportunity

TrackTemplate already has substantial engineering material, but a new contributor needs a clear route through it. A dedicated documentation site can explain the code, development environment and validation routes while linking to the existing authoritative documents.

The reusable source is [Railworks-Documentation at 0129517](https://github.com/Richard-Gnitnub/Railworks-Documentation/tree/01295177743201cb24bc4fe2fc859a1b5cb749d6), already a fork of [Templot5 Companion](https://github.com/ValleysEnduro/templot5companion). That source revision pins Sphinx 7.4.7 and sphinx-rtd-theme 2.0.0 and contains a GitHub Pages deployment workflow.

## Desired outcome

Create a separate `tracktemplate-docs` repository derived from that source, preserving its history and attribution. Use it for site configuration, navigation and contributor explanations. Keep technical requirements, project status, decisions and evidence in their existing owners in `tracktemplate`.

Starting stack: Sphinx 9.2.0, PyData Sphinx Theme 0.23.0 and MyST-Parser 5.1.0, with a separate Python 3.13 documentation environment. Use Read the Docs for hosting and pull-request previews once the service connection exists. Keep reStructuredText support alongside Markdown.

Begin with six areas:

- Start here: purpose, audience, repository map and authoritative status link.
- Development environment: documentation build and routes to the qualified FreeCAD environment.
- Architecture: module responsibilities and implementation boundaries.
- Contributing: the existing contribution and review route.
- Testing and validation: the purpose and limits of the different checks.
- Reference: curated source, API and terminology links.

## Acceptance criteria

1. A clean checkout builds the documentation with warnings treated as errors, using pinned dependencies.
2. The documentation build does not require a FreeCAD GUI session or change product runtime dependencies.
3. Internal navigation works; technical claims link to their source, with the documented source revision identified.
4. Current status comes from its canonical owner rather than a second manually maintained phase dashboard.
5. The site clearly identifies development material, current implementation and future intent.
6. A reviewer can inspect the generated site before publication.
7. Original notices remain with reused scaffold material; imported build output and caches do not become maintained source.

## Scope and related work

The initial work establishes the developer publication structure and a small set of useful pages. Apply TrackTemplate's existing documentation controls where canonical prose changes.

User guidance remains the later work in [tracktemplate#179](https://github.com/Richard-Gnitnub/tracktemplate/issues/179), scheduled after Phase 11. The consolidation in [tracktemplate#180](https://github.com/Richard-Gnitnub/tracktemplate/issues/180) remains separate. This initiative adds no new phase exit, decision register or evidence store and does not establish product or output acceptance.

The public [tracktemplate-docs repository](https://github.com/Richard-Gnitnub/tracktemplate-docs) has been created through GitHub's importer to preserve the Companion/Railworks Git history. The developer starter is proposed in a draft pull request. Read the Docs hosting and previews remain pending.

## References

- [Current project plan](https://github.com/Richard-Gnitnub/tracktemplate/blob/main/reference/PROJECT_PLAN.md)
- [Documentation policy](https://github.com/Richard-Gnitnub/tracktemplate/blob/main/reference/ENGINEERING_POLICY.md#tt-doc-001-tracktemplate-technical-documentation-profile)
- [Sphinx release notes](https://www.sphinx-doc.org/en/master/changes/index.html)
- [PyData theme](https://pydata-sphinx-theme.readthedocs.io/en/stable/)
- [Read the Docs pull-request previews](https://docs.readthedocs.com/platform/stable/pull-requests.html)
