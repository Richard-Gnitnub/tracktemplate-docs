<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted source excerpts and new explanation, 2026-10-24.
-->

# Following a transition edit through FreeCAD

Changing a transition length affects railway intent, its calculated result and
the displayed preview. This chapter follows one **Apply** operation through
those changes and explains how the implementation protects the selected entity.

**Source:** workbench revision
[`7965bfc4671668f889c1f43fb8336c5146c3f5cf`](https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf).
This chapter covers the bounded canonical Entry/Exit editor for Euler
(clothoid) transitions. It is a separate, explicitly activated development
route. The retained main workflow has its own dialogue and generation path.

## Purpose and design intent

The editor accepts a length, while the durable transition record describes
the radius, circle position, required tangent offset and total turn angle.
The application translates the requested length into that intent and solves it
before writing the document.

This follows the workbench's
[canonical-state design](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/ARCHITECTURE.md):
railway state supplies the meaning, and the preview represents it. A change to
the preview must not silently become a change to the railway definition.

## The visible controls and their context

`TrackTemplate.FCMacro` supplies `activate_transition_editing(document)`.
After activation, the returned lifecycle's `show_editor()` opens the modeless
**TrackTemplate transition editor**. Suitable canonical transition records
must already exist. This activation route does not establish normal installed
Addon startup.

| Control | Meaning in this workflow |
| --- | --- |
| **Selected transition** | Shows the stable identity of the selected railway transition |
| **Transition length (mm)** | Shows its current calculated length, formatted to three decimal places |
| **Apply** | Requests an edit to the selected canonical transition |
| **Close** | Closes the transient editor dialogue |
| Status text | Reports readiness, a result or a reason the edit did not apply |

When `show_editor()` opens or refreshes the dialogue, the selection must
resolve to exactly one editable transition with current analysis. Otherwise
the dialogue clears its fields and disables **Apply**. Subsequent selection
changes do not automatically reload the displayed state. **Apply** rechecks the
selection; a mismatch clears the fields and disables the button. Call
`show_editor()` again to load the current selection. Closing the dialogue is
separate from deactivating the editing lifecycle.

Sources: [activation and save observer](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/TrackTemplate.FCMacro#L198-L345),
[dialogue and controller](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/ui/transition_parameter_editor.py),
[lifecycle](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/ui/transition_editing_lifecycle.py).

## 1. Read the requested length without losing precision

The **Apply** signal calls `_on_apply()`. This source excerpt shows how the
dialogue converts its text into a number; the surrounding method provides
`self.length_edit` and the loaded state:

```python
raw_value = self.length_edit.text().strip()
if raw_value == self._loaded_length_text:
    value = self._loaded_length_mm
else:
    value = float(raw_value)
```

The displayed text has three decimal places. If the user leaves it unchanged,
the method uses the original numerical value. This preserves precision and
allows an unchanged input to remain a no-op. Parsing the rounded display text
on every click could otherwise introduce a small unintended edit.

The method passes the requested value and the state it originally displayed to
`controller.edit_selected()`. Parsing and application errors appear in the
status text as `Edit not applied: ...`.

Source: [`TransitionParameterEditorDialog._on_apply`](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/ui/transition_parameter_editor.py#L171-L210).

## 2. Recheck the selected state

The controller reads the current selection again. It compares the complete
selected state with the state that the dialogue displayed:

```python
selected = self.selected()
if selected.state != expected_state:
    raise TransitionParameterSelectionError(
        "The selected transition changed; no edit was applied."
    )
```

This excerpt comes from `edit_selected()`. The comparison protects an edit
prepared for an earlier selection or state. If it succeeds, the controller
calls `edit_transition_length_mm()` with the current state, requested length
and selected edit port.

The edit port supplies the document operation. The controller does not write
a FreeCAD property itself.

Source: [`TransitionParameterEditorController.edit_selected`](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/ui/transition_parameter_editor.py#L66-L80).

## 3. Translate length into replacement intent

The application command requires a finite, non-negative length. It rejects
booleans and values outside the accepted numeric types. If the requested value
matches the current calculated length within the geometry tolerance, it takes
the unchanged-intent route.

For a changed length, the command calculates the corresponding signed tangent
offset. This source excerpt uses the already validated `length_mm`:

```python
intent = state.intent
replacement = replace(
    intent,
    target_signed_offset_mm=transition_start_signed_offset(
        intent.circle_centre_y_mm,
        intent.radius_mm,
        length_mm,
    ),
)
```

`replace()` creates a new immutable intent record. The stable identity, radius,
circle coordinate, total angle and diagnostic labels remain in that record.
The target offset changes to represent the requested length.

The offset calculation evaluates the transition endpoint and its tangent in
canonical local left-turn space. Lengths and offsets use millimetres; angles
use radians. The subsequent analysis solves for the length that satisfies the
replacement intent and the available turn-angle constraint.

Sources: [length-edit command](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/application/transition_edit.py#L73-L113),
[intent fields](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/transition.py#L22-L51),
[offset and solver](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L322-L403).

## 4. Analyse before applying the document edit

`edit_transition_intent()` checks the replacement and routes it through the
state and analysis functions. Its central sequence is:

```python
replacement = analyse_transition_state(
    replace_transition_intent(state, intent)
)
apply_edit(state, replacement)
```

This is an excerpt from the command, not a standalone script. `apply_edit`
is the port's `apply_transition_edit` method, checked earlier in the function.

`replace_transition_intent()` refuses a change to the existing transition's
identity. It retains numerical analysis only when its signed inputs still
match. Changing a label can preserve that result; changing a numerical input
invalidates it. `analyse_transition_state()` then supplies current analysis
before the port can write the document.

If the replacement is identical to the existing intent, the command returns
`changed=False` without calling the edit port. These are internal application
commands. Their use here does not make them stable released API functions.

Sources: [application command](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/application/transition_edit.py#L43-L70),
[signatures and replacement](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/application/transition_state.py#L165-L266).

## 5. Commit the state and refresh the preview

`FreeCADTransitionEditPort` reads the document state and compares it with the
command's previous state. A mismatch produces `stale-edit-base`. This checks
the document at the write boundary, after the controller's selection check.

The store then performs these operations within one FreeCAD transaction:

1. Write the replacement state as a compact JSON payload.
2. Read it back and verify that the stored payload matches.
3. Refresh the preview through the supplied `before_commit` callback.
4. Commit the transaction.

The port defers ordinary document-driven preview updates around this operation.
If the write or callback fails while the transaction is open, the store
attempts to abort it. The
[rollback helper](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/adapters/freecad/transition_state.py#L361-L382)
raises `transaction-rollback-failed` if FreeCAD cannot complete that abort.

The port then reads the actual document state, attempts to rebuild the preview
from it and checks that the state equals the command's previous state. A
preview recovery failure reports `edit-view-recovery-failed`; a different
document state reports `edit-state-recovery-mismatch`. The code does not
promise that every failure restores the canonical state or leaves the view
usable.

The store also compares the serialised payload before opening a transaction.
An identical payload creates no document history entry.

Source: [store update and edit port](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/adapters/freecad/transition_state.py#L510-L646).

## Results, Undo and save/reopen

After a successful edit, the dialogue keeps the replacement state and displays
its calculated length. It reports either `Edited transition ...` or
`No transition change was required.`

The transaction makes the state change available to FreeCAD Undo/Redo. In the
retained lifecycle proof, an Exit transition changes from 420 mm to 360 mm;
Undo, Redo and another Undo restore 420 mm before saving. The save observer
deactivates the transient editing setup. The canonical records survive
save/reopen, and explicit reactivation builds fresh previews from them.

The retained proof also records a lifecycle limit: cleanup can leave one empty
display-mode switch child per object. It removes the active geometry and
selection state. The
[residual guard](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/presentation/transition_coin_viewprovider.py#L66-L91)
rejects another activation while that child remains, so the demonstrated
restart route closes and reopens the document before creating a fresh
lifecycle. Before directly closing a document with an active lifecycle, call
that lifecycle's `deactivate()`: this route has no automatic document-close
cleanup. This bounded result does not establish full-workbench cleanup or
performance behaviour.

Sources: [GUI lifecycle fixture](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/freecad_gui_validate_phase5_transition_editing_lifecycle.py),
[retained lifecycle evidence and limitations](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/history/phase-closeouts/PHASE5_CLOSEOUT.md#owner-operated-b16-lifecycle-validation).

## Checks a contributor should follow

| Claim | Focused source or evidence |
| --- | --- |
| Selection changes prevent an unintended edit | [Parameter-editor checks](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_phase5_transition_parameter_editor.py) |
| Replacement analysis precedes the edit port; no-op behaviour | [Application-command checks](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_phase5_transition_edit_command.py) |
| Numerical changes invalidate analysis; label changes preserve it | [State and signature checks](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_phase4_transition_state.py) |
| Native edit, Undo/Redo and failure handling | [FreeCAD edit fixture](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/freecad_validate_phase5_transition_edit.py) |
| Visible editor, selection, save and reactivation | [GUI lifecycle fixture](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/freecad_gui_validate_phase5_transition_editing_lifecycle.py) |

This chapter's excerpts were inspected against the pinned source. No new
FreeCAD session or executable-example run supplied the results described here;
the runtime account refers to the linked retained evidence. The documentation
build checks page structure and references.

Code excerpts retain the upstream
[GPL-3.0-or-later notice](https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/NOTICE.md).
