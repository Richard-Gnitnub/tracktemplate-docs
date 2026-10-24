# TrackTemplate developer documentation

A developer handbook for TrackTemplate's code, GUI workflows and design intent.

TrackTemplate is an in-development project for parametric model railway
templates inside FreeCAD. Its [product vision](https://github.com/Richard-Gnitnub/tracktemplate/blob/54c5903b41e89d1fdfb430c812495e36b91d690b/reference/PRODUCT_VISION.md)
explains the intended Workbench and the current migration programme.

```{note}
The original orientation material uses source snapshot `54c5903b`. The authoring
guide, terminology guide, GUI coverage map and handbook chapters on generation,
curves and spacing, straight routes, and transition editing use `7965bfc`.
Both snapshots were examined on 24 October 2026; each explanation identifies
its source boundary.
The [live project plan](https://github.com/Richard-Gnitnub/tracktemplate/blob/main/reference/PROJECT_PLAN.md)
owns current project status.
```

## Find your starting point

| Your task | Start here |
| --- | --- |
| Build or edit this documentation | [Development environment](development.md) |
| Understand the code boundaries | [Architecture](architecture.md) |
| Follow the main generation and replacement workflow | [Generate a template set](handbook/generate-template-set.md) |
| Understand curves, easements and independent track spacing | [Curves and spacing](handbook/curves-and-spacing.md) |
| Follow straight datums, travel direction and curve connections | [Straight routes](handbook/straight-routes.md) |
| Follow the separate canonical transition editor | [A transition edit](handbook/transition-edit.md) |
| Find a workflow to document | [GUI coverage](gui-coverage.md) |
| Write a narrated technical explanation | [Authoring the handbook](authoring.md) |
| Use the project's railway and software terms | [Using TrackTemplate terminology](terminology.md) |
| Prepare a contribution | [Contributing](contributing.md) |
| Choose the right validation | [Testing and validation](testing.md) |
| Find an API, contract or canonical source | [Reference](reference.md) |

The handbook explains current implementation with narrated code and source
links. The coverage map identifies the chapters still needed. The linked
canonical documents continue to own their subjects. User
documentation is separate later work tracked in
[issue #179](https://github.com/Richard-Gnitnub/tracktemplate/issues/179).

```{toctree}
:hidden:
:maxdepth: 2

development
architecture
handbook/generate-template-set
handbook/curves-and-spacing
handbook/straight-routes
handbook/transition-edit
gui-coverage
authoring
terminology
contributing
testing
reference
```
