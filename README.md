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

The [authoring guide](docs/authoring.md), [GUI coverage map](docs/gui-coverage.md)
and [transition-edit walkthrough](docs/handbook/transition-edit.md) use workbench
revision `7965bfc4671668f889c1f43fb8336c5146c3f5cf`. The coverage map records
which developer explanations still need writing.

[AGENTS.md](AGENTS.md) routes repository agents to four adapted skills for
authoring, STE100 assistance, independent review and documentation alignment.
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

## Scaffold origins

The Makefile adapts the earlier Companion/Railworks Sphinx scaffold.
[NOTICE.md](NOTICE.md) records the source revisions and scope.
[LICENSE](LICENSE) preserves the original MIT notice.
Adapted TrackTemplate skills and the source-based transition-edit chapter retain
GPL-3.0-or-later. [NOTICE.md](NOTICE.md) identifies the covered paths and sources.
