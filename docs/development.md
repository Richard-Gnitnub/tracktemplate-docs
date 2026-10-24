# Development environment

## Build this documentation

The documentation build uses Python 3.13. Run these commands from the scaffold
root:

```bash
python3.13 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m sphinx -b html -n -W --keep-going docs _build/html
```

The build writes HTML to `_build/html/`. To inspect it in a browser:

```bash
python -m http.server 8000 --bind 127.0.0.1 --directory _build/html
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) and stop the server with
Ctrl+C when finished. FreeCAD is not needed for this documentation build.

The direct dependencies are listed in `requirements.txt`. The lock file records
the complete dependency set used for the checked Python 3.13 build.

Edit the Markdown pages in `docs/`. MyST supplies Sphinx directives within
Markdown, including the navigation tree on the home page. The theme settings
live in `docs/conf.py`; the small colour adjustments live in
`docs/_static/custom.css`.

## Regenerate the alignment figures

The [curves and spacing chapter](handbook/curves-and-spacing.md) uses committed
SVG figures and a numerical JSON record. The Sphinx build reads these assets
directly; Matplotlib is needed only to regenerate them. To run the optional
[figure tool](https://github.com/Richard-Gnitnub/tracktemplate-docs/blob/main/tools/render_alignment_figures.py)
in a separate environment, use these commands from the repository root:

```bash
python3.13 -m venv _build/figure-env
_build/figure-env/bin/python -m pip install matplotlib==3.10.8
_build/figure-env/bin/python tools/render_alignment_figures.py
```

The tool rewrites `euler-two-track-example.svg`, `euler-curvature-example.svg`
and `alignment-example-values.json` under `docs/_static/figures/`. It also
writes PNG inspection copies and its Matplotlib cache under
`_build/generation-review/`. Review the changed assets and rendered chapter
before including regenerated output in a contribution.

These are independent mathematical illustrations using equations and retained
fixture values from workbench revision
[`7965bfc4671668f889c1f43fb8336c5146c3f5cf`](https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf).
The script uses standard Python and Matplotlib; it does not import or run
workbench code or FreeCAD. Its arithmetic comparisons do not validate the
workbench's sampled geometry. The chapter explains that representation boundary.

## Work on the FreeCAD code

The documentation environment and the qualified FreeCAD host environment
serve different purposes. Use the workbench repository's
[validation strategy](https://github.com/Richard-Gnitnub/tracktemplate/blob/54c5903b41e89d1fdfb430c812495e36b91d690b/reference/VALIDATION.md) to identify the
applicable host profile and evidence requirements before running host checks.

Start with [project guidance](https://github.com/Richard-Gnitnub/tracktemplate/blob/54c5903b41e89d1fdfb430c812495e36b91d690b/AGENTS.md), then use the
[workflow catalogue](https://github.com/Richard-Gnitnub/tracktemplate/blob/54c5903b41e89d1fdfb430c812495e36b91d690b/reference/AGENT_WORKFLOWS.md) for the task you
intend to perform. The [contribution guide](https://github.com/Richard-Gnitnub/tracktemplate/blob/54c5903b41e89d1fdfb430c812495e36b91d690b/CONTRIBUTING.md) owns
the requirements for submitted code and evidence.

This site does not yet provide an installation procedure for a released
Workbench. The [live project plan](https://github.com/Richard-Gnitnub/tracktemplate/blob/main/reference/PROJECT_PLAN.md)
is the route to current packaging and release status.
