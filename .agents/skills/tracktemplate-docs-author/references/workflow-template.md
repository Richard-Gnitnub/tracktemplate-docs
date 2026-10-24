<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted for tracktemplate-docs on 2026-10-24. See ../../../../NOTICE.md.
-->

# Workflow chapter template

Use this outline to plan one coherent explanation. Replace the prompts with
verified content. Do not publish a page of empty sections or claim that a
control is documented because its label appears in the coverage map.

## Purpose and design intent

Explain the railway or developer problem, the intended result and the owning
requirement. Attribute recorded rationale. Label any implementation inference.

Record the complete workbench source revision and the reviewed implementation
boundary. State whether the route uses package code, retained host code or
both. Put a material experimental limitation beside the relevant capability.

Before drafting, apply [Using TrackTemplate terminology](../../../../docs/terminology.md).
Read the relevant upstream entries and check their meaning, assurance state and
scope. Record the source revision, checked terms and unresolved findings in the
PR. Explain terms on the page where the reader needs them.

## GUI entry point

Name the exact visible control, where it appears and when it is available.
Identify its final handler. Include selection, document and prerequisite
conditions. If the operation is session-only, say so and do not call it a GUI
workflow.

## Inputs and relationships

| Input or state | Railway meaning | Unit or identity | Constraint or relationship |
| --- | --- | --- | --- |
| Replace with a real field | Explain its purpose | Use the actual unit or ID | Explain how it affects the operation |

State which values the user supplies, which the document owns and which the
algorithm derives. Explain any mutation of an input record.

## Walk through the implementation

Follow the call path in concept order. For each short block:

1. Explain the step's purpose.
2. Identify it as a runnable example, source excerpt or pseudocode.
3. Give a pinned source link and any required context.
4. Explain the calculation or state change.
5. Show the relevant intermediate or returned value and how it was checked.

Use actual entrypoints. Keep equations connected to source variables. Explain
units, frames, signs, sampling and numerical limits where they matter.

## Visible result and document state

Explain the returned data, viewport result and stored changes. Identify
canonical intent and derived representations. Cover transactions, Undo/Redo,
save/reopen and export only where the operation uses them. Link shared
machinery and explain its effect on this workflow.

## Invalid input and recovery

Explain useful failure examples: impossible geometry, stale selection,
unavailable action, partial output or rollback. Quote diagnostic strings
exactly. Identify which boundary performs each check.

## Evidence and implementation limits

Link tests and retained evidence for the claims made. Distinguish source
inspection, execution in this task and earlier retained results. Record the
scope of GUI or native-output evidence. State any unverified result.

## Source map

Give the few owning functions, classes and contracts a contributor needs next.
Update the workflow's coverage row and incoming navigation when the chapter is
ready. Keep review details in the PR rather than adding a phase-status panel.
