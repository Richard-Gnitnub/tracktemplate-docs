# TrackTemplate developer documentation

A Sphinx documentation site for TrackTemplate contributors.

The handbook explains GUI workflows, code and design intent, with developer
orientation, architecture, validation and source links. The workbench repository
keeps its existing technical authority. User guidance remains later work under
[issue #179](https://github.com/Richard-Gnitnub/tracktemplate/issues/179).

[Read the developer documentation](https://tracktemplate-docs.readthedocs.io/en/latest/).

Read the Docs publishes the developer site from this repository.
GitHub Actions also validates the HTML and retains a build artifact.

## Build locally

Use Python 3.13. Run these commands from this directory:

```bash
python3.13 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-lock.txt
python tools/validate_agent_skills.py
python -m sphinx -b html -n -W --keep-going docs _build/html
```

Serve the result locally:

```bash
python -m http.server 8000 --bind 127.0.0.1 --directory _build/html
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Stop the server with
Ctrl+C. With the environment active, `make html` runs the same strict build.

## Source and authority

The original orientation pages are introductory guidance. Their references point to
TrackTemplate revision
[`54c5903b41e89d1fdfb430c812495e36b91d690b`](https://github.com/Richard-Gnitnub/tracktemplate/tree/54c5903b41e89d1fdfb430c812495e36b91d690b),
examined on 24 October 2026. The separately labelled
[live project plan](https://github.com/Richard-Gnitnub/tracktemplate/blob/main/reference/PROJECT_PLAN.md)
owns current project status.

The [authoring guide](docs/authoring.md), [terminology guide](docs/terminology.md),
[GUI coverage map](docs/gui-coverage.md),
[generation walkthrough](docs/handbook/generate-template-set.md),
[curves and spacing chapter](docs/handbook/curves-and-spacing.md),
[straight-route chapter](docs/handbook/straight-routes.md),
[physical-platform chapter](docs/handbook/platforms.md),
[formation-board chapter](docs/handbook/formation-board.md),
[sectioning chapter](docs/handbook/sectioning.md), and
[transition-edit walkthrough](docs/handbook/transition-edit.md) use workbench
revision
[`7965bfc4671668f889c1f43fb8336c5146c3f5cf`](https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf).
The coverage map records
which developer explanations still need writing. The terminology guide requires
authors and reviewers to read the relevant workbench register entries and record
their source revision, meaning and scope in the PR.

[AGENTS.md](AGENTS.md) routes repository agents to six skills for authoring,
STE100 assistance, independent review, documentation alignment, context-packet
preparation and context recovery. [Agent context and recovery](docs/agent-context.md)
explains their triggers, lead and worker responsibilities, and the distinction
between a temporary packet and platform-managed compaction.
The workflow uses the existing free Sphinx/Read the Docs setup. It does not
require a paid language service or claim formal STE100 conformance from a build.

Keep one source for each technical requirement. Link to its existing owner.
Update source references deliberately when reviewing a later revision. Do not
copy phase counts into these pages.

`requirements.txt` records the three direct dependencies. The lock file records
the complete Python 3.13 dependency set used for the checked build. Refresh it
deliberately when updating dependencies, then rebuild before proposing the change.

`docs/` is the single Sphinx source directory. Generated HTML belongs in
`_build/`. The build uses Sphinx, MyST Markdown and the PyData theme; it does
not import TrackTemplate or require FreeCAD.

The curve, straight, platform, formation and sectioning chapters' explanatory
SVG figures and numerical JSON are committed assets.
[Optional figure-regeneration instructions](docs/development.md#regenerate-the-alignment-figures)
use a separate Python environment with Matplotlib 3.10.8. Sphinx consumes the
assets directly and needs no additional dependency. The figure tools perform
independent mathematical calculations; they do not import or execute workbench
code.

## Scaffold origins

The Makefile adapts the earlier Companion/Railworks Sphinx scaffold.
[NOTICE.md](NOTICE.md) records the source revisions and scope.
[LICENSE](LICENSE) preserves the original MIT notice.
Adapted TrackTemplate skills, the terminology and agent-context guides,
the source-based handbook chapters and the explanatory figure tools and assets
retain GPL-3.0-or-later.
[NOTICE.md](NOTICE.md) identifies the covered paths and sources.
