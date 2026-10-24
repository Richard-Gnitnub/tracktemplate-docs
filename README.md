# TrackTemplate developer documentation

A Sphinx documentation site for TrackTemplate contributors.

The initial scope is developer orientation, documentation setup, architecture,
contribution routes, validation and reference links. The workbench repository
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
python -m sphinx -b html -n -W --keep-going docs _build/html
```

Serve the result locally:

```bash
python -m http.server 8000 --bind 127.0.0.1 --directory _build/html
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Stop the server with
Ctrl+C. With the environment active, `make html` runs the same strict build.

## Source and authority

The new pages are introductory guidance. Their technical references point to
TrackTemplate revision
[`54c5903b41e89d1fdfb430c812495e36b91d690b`](https://github.com/Richard-Gnitnub/tracktemplate/tree/54c5903b41e89d1fdfb430c812495e36b91d690b),
examined on 24 October 2026. The separately labelled
[live project plan](https://github.com/Richard-Gnitnub/tracktemplate/blob/main/reference/PROJECT_PLAN.md)
owns current project status.

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
