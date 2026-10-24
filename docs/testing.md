# Testing and validation

## Documentation checks

Check the repository's agent-skill metadata and local guidance links:

```bash
python tools/validate_agent_skills.py
```

This catches missing skill descriptions, inconsistent invocation metadata and
broken local guidance paths. It does not assess prose or formal STE100
conformance. The [authoring guide](authoring.md) defines those review boundaries.

Build the site with warnings treated as errors:

```bash
python -m sphinx -b html -n -W --keep-going docs _build/html
```

This checks whether Sphinx can read the sources, resolve its internal
references and produce HTML without warnings. It does not establish the
technical correctness of every statement or confirm that every external
website is available.

Inspect the changed pages in the browser. Check navigation, headings, code
blocks and tables at desktop and narrow-screen widths. Confirm that each
source link points to the intended file and revision.

GitHub Actions runs the skill checks and strict HTML build, then retains an
artifact for review. Read the Docs builds the hosted site.

For a pull request, open the Read the Docs check's Details link and inspect
the generated preview before merging.

## Workbench evidence

Use the workbench's [validation strategy](https://github.com/Richard-Gnitnub/tracktemplate/blob/54c5903b41e89d1fdfb430c812495e36b91d690b/reference/VALIDATION.md)
and [testing policy](https://github.com/Richard-Gnitnub/tracktemplate/blob/54c5903b41e89d1fdfb430c812495e36b91d690b/reference/TESTING_POLICY.md) to select checks for
a code change.

Those sources distinguish standalone checks from FreeCAD host checks and
real-GUI evidence. A documentation build cannot establish geometry,
persistence, display or production-output correctness. Similarly, a passing
standalone code test does not establish every host behaviour.

Read the evidence for the capability you intend to change, including its
limitations. The [live project plan](https://github.com/Richard-Gnitnub/tracktemplate/blob/main/reference/PROJECT_PLAN.md)
is the entry point for current phase and acceptance status.
