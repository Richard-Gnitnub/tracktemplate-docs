# Sources and notices

## Existing Sphinx scaffold

The Makefile adapts the Sphinx build arrangement in:

- [Richard-Gnitnub/Railworks-Documentation](https://github.com/Richard-Gnitnub/Railworks-Documentation/tree/01295177743201cb24bc4fe2fc859a1b5cb749d6),
  revision `01295177743201cb24bc4fe2fc859a1b5cb749d6`.
- [ValleysEnduro/templot5companion](https://github.com/ValleysEnduro/templot5companion/tree/17f9fc4770379e9add7fb8bcaf3b2b0161e61d9a),
  revision `17f9fc4770379e9add7fb8bcaf3b2b0161e61d9a`.

The two source Makefiles contain the same build scaffold. This draft changes
the source directory to `docs/`, the output directory to `_build/` and the
default build options.

The original MIT licence, including
`Copyright (c) 2024 Rich Bunting`, is preserved verbatim in [LICENSE](LICENSE).

## New documentation

The TrackTemplate-facing pages, theme configuration and validation workflow
form the initial developer documentation for TrackTemplate contributors. They
do not speak on behalf of Martin Wynne or the Templot project.

The original orientation pages link to TrackTemplate's source documents at revision
`54c5903b41e89d1fdfb430c812495e36b91d690b`. Those linked documents retain
their own licences, notices and authority. A link does not change those terms.

## Adapted TrackTemplate skills, chapters and explanatory figures

The following material retains the upstream `GPL-3.0-or-later` licence:

- Adapted skills under `.agents/skills/` and `docs/terminology.md`.
- `docs/handbook/transition-edit.md`,
  `docs/handbook/generate-template-set.md` and
  `docs/handbook/curves-and-spacing.md`.
- `tools/render_alignment_figures.py` and its committed outputs:
  `docs/_static/figures/euler-two-track-example.svg`,
  `docs/_static/figures/euler-curvature-example.svg` and
  `docs/_static/figures/alignment-example-values.json`.

The complete GPL version 3 text is preserved in
[.agents/LICENSE](.agents/LICENSE). The original scaffold's MIT notice remains
in [LICENSE](LICENSE); it does not relicense these adapted materials.

Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.

Adapted for TrackTemplate's developer handbook on 24 October 2026 from
[Richard-Gnitnub/tracktemplate at 7965bfc4671668f889c1f43fb8336c5146c3f5cf](https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf).
The adaptations add GUI-to-code narration, handbook-specific source tracing,
Sphinx validation and an explicitly scoped language-review profile. They omit
workbench phase registers and repository-specific receipt tooling.

| Adaptation | Principal upstream sources |
| --- | --- |
| `tracktemplate-docs-author` and its workflow template | `tracktemplate-technical-author-lead` and `tracktemplate-explain-change` skills |
| `tracktemplate-docs-review` | `tracktemplate-documentation-review`, its writing checklist and ownership map, and `tracktemplate-technical-author-lead` |
| `tracktemplate-docs-ste100` | TT-DOC-001 and the technical-documentation management plan in `reference/ENGINEERING_POLICY.md`; `reference/external/asd-ste100/README.md`; `reference/TERMINOLOGY.md`; the documentation-review checklist |
| `tracktemplate-docs-align` | `tracktemplate-documentation-alignment` skill |
| Transition-edit chapter | `tracktemplate/ui/transition_parameter_editor.py`, `tracktemplate/application/transition_edit.py` and the linked state, adapter and validation sources |
| Generation and replacement chapter | `TrackTemplate.FCMacro`, the retained B15 `CurveInputDialog` and `run_macro`, `tracktemplate/compatibility/transition_workflow.py`, `core_export_policy.py` and the linked persistence and evidence sources |
| Curves and spacing chapter | `tracktemplate/domain/alignment.py`, retained B15 controls and geometry construction, the compatibility adapters and linked alignment contracts and fixtures |
| Explanatory figure tool and generated assets | Euler equations in `tracktemplate/domain/alignment.py` and numerical expectations in `tests/validate_phase1_alignment.py` at the pinned revision; independent documentation calculations and plotting |
| Terminology-use guide | `reference/TERMINOLOGY.md` and `reference/contracts/phase1-terminology-assurance.json` |

All upstream skill paths are under `.agents/skills/` at the named revision.
The upstream [NOTICE.md](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/NOTICE.md)
records the project copyright, GPL-3.0-or-later terms and Templot source basis.
Source-linked railway calculations and validation evidence retain that
provenance and their recorded limits.

The explanatory figures show smooth mathematical centrelines and curvature.
They do not reproduce the retained host's sampled geometry or constitute a
FreeCAD, GUI or workbench validation result. Their source revision and numerical
scope are recorded in the generator and the accompanying JSON. Matplotlib is
used only by the optional regeneration tool; it is not a Sphinx build dependency.

ASD-STE100 remains an external copyrighted reference. This adaptation includes
no official PDF, controlled dictionary, extracted standard text or lookup
cache, and makes no ASD endorsement or certification claim.

## Third-party build tools

Sphinx, MyST Parser, PyData Sphinx Theme and the GitHub Actions used by this
scaffold retain their respective upstream licences. The requirements file
identifies the direct Python dependencies. Action revisions are pinned in the
validation workflow.
Matplotlib, used for optional figure regeneration, retains its upstream licence.
