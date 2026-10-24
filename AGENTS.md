# TrackTemplate documentation agent guidance

## Purpose and scope

Build a developer handbook that explains every current GUI workflow and the
code behind it. Explain the railway problem, design intent, inputs, calculations,
state changes, results and failure behaviour. Use short, narrated code blocks.
The wiki owns the development journal. Keep chronology and personal accounts
there.

Read [DOCUMENTATION_INTENT.md](DOCUMENTATION_INTENT.md),
[the authoring guide](docs/authoring.md), and the relevant row in
[GUI coverage](docs/gui-coverage.md) before substantial documentation work.
This repository owns the handbook and its authoring workflow. The workbench
repository keeps technical requirements, terminology, decisions and acceptance.

## Skills

| Task | Repository skill |
| --- | --- |
| Write or materially revise a developer explanation | [tracktemplate-docs-author](.agents/skills/tracktemplate-docs-author/SKILL.md) |
| Consult STE100 during authoring or the one review | [tracktemplate-docs-ste100](.agents/skills/tracktemplate-docs-ste100/SKILL.md) |
| Review a fixed candidate independently | [tracktemplate-docs-review](.agents/skills/tracktemplate-docs-review/SKILL.md) |
| Check claims after source changes | [tracktemplate-docs-align](.agents/skills/tracktemplate-docs-align/SKILL.md) |

Use the author skill automatically for new or materially changed handbook
prose. Use the STE100 skill within authoring or review when its source checks
apply. It does not create another review stage. A small factual or link
correction needs the relevant check and diff review.

## Source discipline

- Name the workbench revision that each implementation explanation covers.
  Verify GUI labels, callbacks and final runtime bindings at that revision.
- Link technical claims to the owning requirement, implementation or test.
  Explain the code in the page; a link alone does not teach the reader.
- Keep recorded design rationale separate from a reason inferred from code.
  Label an inference and do not invent rejected alternatives.
- Distinguish package code, retained macro code, session-only experiments and
  future interfaces. Do not describe a session method as a GUI action without
  an observed binding.
- Preserve exact code, UI labels, property names, diagnostics, commands,
  identifiers, units, signs, frames, tolerances and licence notices.
- Use UK English and the workbench terminology register. Use **plain line** in
  new prose. Keep established identifiers exact.
- Link live project status to its owner. Do not copy phase counts or acceptance
  registers into the handbook. Report a conflict between sources before fixing
  the affected explanation; do not change an upstream requirement to match code.

## Authoring and review

Follow the authoring guide's finite workflow: prepare the complete candidate,
identify its exact files and content, obtain one independent review, apply its
complete correction set once, and run the relevant checks. Keep unresolved
technical facts visible. Correct an objective validation defect and repeat its
check; do not start recurring stylistic reviews.

The handbook profile is an adaptation of TrackTemplate's technical-authoring
workflow. It does not change TT-DOC-001 or establish formal STE100 conformance.
Claim Issue 9 conformance only for a named scope with sufficient review against
the official source. Otherwise record that conformance is not verified.

Keep official STE PDFs, extracted standard text, dictionaries and lookup caches
out of Git and the published site. Local reference files can use ignored
`.local/`. Follow upstream guidance before running upstream tools.

## Validation and delivery

Use the pinned Python 3.13 documentation environment:

```bash
python tools/validate_agent_skills.py
python -m sphinx -b html -n -W --keep-going docs _build/html
```

Inspect changed HTML, navigation, code blocks and tables. Report code examples
as source-inspected, executed, or supported by named retained evidence; never
invent output. Sphinx and skill checks do not establish railway correctness,
GUI behaviour or linguistic conformance.

Keep edits within the requested task. Preserve unrelated work and the existing
scaffold notices. Do not add paid services or new runtime dependencies for this
workflow. Keep generated output in `_build/`. Publish a reviewable branch/PR
when the user authorises repository changes; merge only with user authority.
