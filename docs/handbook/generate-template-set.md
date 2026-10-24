<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted source excerpts and new explanation, 2026-10-24.
-->

# Generating and replacing a template set

The main dialogue collects a complete track arrangement, prepares its geometry,
then creates a set of FreeCAD objects. Its **Output behaviour:** control decides
whether that set replaces recognised generated objects or joins the existing
sets. This chapter follows that operation through its input, preparation,
document and failure boundaries.

**Source:** workbench revision
[`7965bfc4671668f889c1f43fb8336c5146c3f5cf`][revision].
The explanation covers the retained `CurveInputDialog` and `run_macro()` after
B16 composition. The separate [transition editor](transition-edit.md) has a
different state store and recovery implementation. Its guarantees do not apply
automatically to this path.

## Which implementation runs?

`TrackTemplate.FCMacro.run_macro(launch_workflow=True)` checks that the FreeCAD
runtime matches a qualified profile, composes the package operations and
launches the inherited workflow.
The default `run_macro()` prepares the foundation without opening this dialogue.
The loader verifies the retained B15 source fingerprint and evaluates its
definitions without the final automatic launch. This includes definitions
that appear after the original `run_macro()`. B16 then binds and checks the
selected package functions before calling that retained function.
[Launcher][launcher]; [host loader][host-loader]; [final launch][launch-binding].

The numerical alignment operations use `tracktemplate.domain.alignment`
through `tracktemplate.api`. Compatibility adapters supply FreeCAD vectors to
the retained caller. The dialogue, document objects and generation transaction
remain in the retained host. The final Core export policy also replaces the
dialogue's export-control and export-value methods; it does not replace
`CurveInputDialog.values()` or the main acceptance button.
[Calculation bindings][calculation-binding]; [export-policy bindings][export-policy].

The [architecture][architecture] records the intended separation between
railway intent, derived display and explicit materialisation. This current
generation route creates retained `Part` shapes and settings properties. It
does not establish that the whole main workflow uses the compact canonical
state or Coin presentation of the bounded transition editor.

## Accepting the main dialogue

The host uses `App.ActiveDocument`, or creates `ModelRailwayCurve` when no
document is active. It then opens the modal **Model Railway Curve Template**
dialogue, whose title includes the retained version text. No selected object
is required. Selection can help choose a source of defaults; it does not limit
which generated sets replacement removes.
[Workflow entry][workflow-entry]; [settings selection][settings-selection].

Source comments call acceptance the **Generate** action. The actual button is
Qt's standard **OK** button, with **Cancel** beside it; the source does not set
an explicit `Generate` caption. This excerpt from `CurveInputDialog.__init__`
uses the Qt-version-compatible `ok_button` and `cancel_button` enums resolved
immediately above it:

```python
buttons = QtWidgets.QDialogButtonBox(ok_button | cancel_button)
buttons.accepted.connect(self.accept)
buttons.rejected.connect(self.reject)
```

Acceptance closes the dialogue. The waiting `run_macro()` then reads its
values and begins generation. Cancellation returns before that read, although
a document created before the dialogue remains open. Button text can follow
the Qt locale. These are source-inspected bindings, not a new screenshot or
GUI observation. [Button source][accept-button]; [acceptance check][acceptance].

The **Main curve** fields are:

| Exact label | Meaning and supplied value |
| --- | --- |
| **Main transition length (each):** | Length of each main-track Euler easement, in mm; the same input supplies entry and exit |
| **Main constant radius:** | Main centreline radius through the circular section, in mm |
| **Total turn angle:** | Complete direction change, including both easements, in degrees; positive turns left and negative turns right |
| **Main template width:** | Printable strip width in mm, centred on the alignment; this is not the track gauge |
| **Number of additional tracks:** | Number of independently configured rows in **Independent parallel-track controls** |
| **Output behaviour:** | **Replace all existing generated templates** or **Create a new template set** |
| **Existing generated sets:** | Count recognised in the current document when the dialogue opens |

The length controls display three decimal places and an `mm` suffix. Fresh
main defaults are 600 mm for each easement, 600 mm radius, +90° and 32 mm width;
remembered or document values can override them. The companion
[curves and spacing chapter](curves-and-spacing.md) explains the local frame,
handedness, spacing modes and sampled geometry.
[Controls][main-controls]; [defaults][defaults]; [numeric controls][accept-button].

## What `values()` collects, and what is remembered

`CurveInputDialog.values()` returns an ordered 18-item tuple. Its first four
items are the main numerical inputs. The remainder carries added-track
configurations, straight-route definitions and selected row, platform
definitions and selected identity/index, formation, sectioning, registration,
template assembly, assembly labels, production export, material-report
settings and output behaviour. The caller unpacks that exact order.
[Value collection][values]; [caller unpacking][acceptance].

Each added-track dictionary contains a name, side, alignment mode, entry,
curve and exit spacings, two transition lengths, width, and separate template
and centreline flags. An incomplete table row raises
`Track row {} is incomplete. Close and reopen the macro.` Assembly-label and
material-report configuration validation also occurs during collection.
`values()` runs before the caller's main geometry-error handler, so these
collection failures do not use that handler's normal error-dialogue path.
[Row conversion][row-config]; [value collection][values]; [validation boundary][validation].

Defaults have two distinct sources. The host first finds settings associated
with selected generated objects, or the last recognised settings object, with
a template fallback. It then gives `read_last_dialog_inputs(doc)` precedence
for most main and manager controls. That reader checks a preference entry
keyed by the saved document's absolute filename, or the unsaved document's
name, and then tries the global last-used payload. Assembly-label and
material-report settings are loaded separately from the settings source.
[Entry and precedence][workflow-entry]; [preference reader][remembering].

After successful collection, the host attempts to remember the accepted
inputs **before replacement confirmation and geometry validation**. The
record includes manager selections and output behaviour; material-report
preferences use a separate helper. Consequently, declining replacement or
rejecting invalid geometry can still leave the next dialogue populated with
the accepted inputs. These writes use `App.ParamGet`, outside the document
transaction. They are best effort: storage failures can return `False`, and
the caller does not check that result.
[Remembering call][remember-call]; [preference implementation][remembering].

This is different from saving generated-set properties. Preparation can update
the working track dictionaries with solved transition lengths and spacings.
The early preference snapshot precedes those updates; the generated settings
later contain the prepared values. It is therefore incorrect to treat both
records as the same successful-build snapshot.
[Preparation contract][preparation-contract]; [stored parameters][stored-parameters].

## Prepare before removing existing output

When replacement is selected and the initial count is non-zero, a
**Replace generated templates** question describes its document-wide scope.
Its default answer is **No**. A positive answer permits preparation to
continue; it does not immediately delete anything.
[Replacement question][replacement-question].

The main checks require a positive radius and width, a non-negative transition
length, a radius greater than half the width, and a non-zero turn angle. For
example, a zero angle raises `The total turn angle cannot be zero.` The host
then validates platform configuration and the export request, converts the
magnitude of the angle to radians, and records its sign separately.
[Initial validation][validation].

The host builds the main alignment, then prepares each added track. This
source excerpt is inside `run_macro()`; `track_configs`, the circle centre,
main radius, radian angle and `main_alignment` already exist:

```python
track_alignments = []
for config in track_configs:
    track_alignments.append(
        prepare_track_alignment(
            config,
            circle_centre,
            radius,
            total_angle,
            main_alignment,
        )
    )
```

The final binding is `_PrepareTrackAlignmentAdapter`, which calls the package
calculation and converts only the new XY point sequence to `App.Vector`
values with Z equal to zero. Successful preparation updates four fields in
the same configuration dictionary: entry length, exit length, start spacing
and finish spacing. It leaves the main alignment unchanged. The returned
alignment supplies points, headings, calculated lengths and track metadata.
[Caller excerpt][prepare-call]; [adapter][preparation-adapter];
[preparation contract][preparation-contract].

The caller adds common straight extensions, checks added-track entry and exit
spacing against 0.01 mm and checks the side of each straight. A platform
widening profile tighter than the main radius can require another confirmation.
It then mirrors the completed alignments for a right turn and records their
sampled polyline lengths. Independent or curve-connected straight routes are
prepared afterwards. [Alignment checks and straight routes][alignment-checks].

Further preparation creates requested platform shapes, track strips, formation
geometry, sections, joints, holes and production records. In the simple curve
case, each strip is a polygonal boundary offset from the sampled centreline,
formed into a face and extruded through the fixed 1 mm thickness. This is
materialised sampled geometry, not an analytic clothoid solid. Optional export
planning and preflight also precede the transaction.
[Shape preparation][shape-preparation]; [strip construction][strip-shape];
[remaining preparation][remaining-preparation].

**Inference from this ordering:** preparing the requested geometry before
replacement reduces the operations that can fail after old output is removed.
It does not eliminate them. Curve centreline wires and several document-bound
derived objects are still created inside the transaction. The confirmation's
validation wording must not be read as a guarantee that every subsequent
shape or document operation has already succeeded.
[Document creation][document-creation].

## Set identity and replacement ownership

`planned_template_set_id()` returns `SET-001` for replacement. Creating another
set chooses the lowest unused `SET-nnn` value found across document objects.
`unique_internal_name()` separately avoids FreeCAD object-name collisions.
Labels, internal object names and set identifiers therefore serve different
purposes. A replacement can reuse `SET-001`; it does not preserve the old
object identities merely because their labels or names resemble the new ones.
[Identity helpers][identity].

Every tagged object receives these assignments in `tag_generated_object()`;
the preceding statements create the string properties:

```python
obj.GeneratedBy = GENERATOR_ID
obj.GeneratedRole = role
obj.TemplateSetID = set_id
obj.GeneratorVersion = MACRO_VERSION
```

`GeneratedBy` is the ownership marker
`ModelRailwayCurveTemplate.IndependentEasements`. `GeneratedRole` identifies
the object's role, such as `Group`, `Settings`, `Template` or `Centreline`.
`TemplateSetID` groups the outputs from this operation. These fields are then
marked read-only in the property editor. The version remains the retained
host's version. [Identity source][identity]; [ownership constant][output-modes].

Replacement opens the generation transaction before calling
`remove_all_generated_outputs(doc)`. That function selects every object with
the matching generator marker, regardless of its set or role. It also applies
legacy recognition: template input-property combinations, centreline names
and group-name prefixes. It removes recognised non-group objects first,
groups second, and recomputes if anything was removed. Thus a selected set can
provide defaults while **all** recognised generated sets are replaced.
[Transaction entry][transaction-entry]; [recognition and cleanup][cleanup].

Objects that these predicates do not recognise are left alone. This is the
actual boundary behind the prompt's promise to preserve unrelated objects;
legacy recognition includes names and properties, not an independent ownership
registry. **Create a new template set** skips cleanup and uses set-specific
name suffixes, preserving the existing generated sets.
[Recognition][cleanup]; [creation naming][transaction-entry].

## Commit, stored properties and visible results

The transaction adds a top-level group, a `Part::Feature` settings container,
the requested template compound and centreline objects, plus enabled layers.
The settings container can have a null shape. The host also materialises
production-source objects and builds the production-record index. Hidden
source objects can therefore exist in addition to the visible tracks.
[Object creation][document-creation]; [record materialisation][record-materialisation].

`store_parameters()` writes typed main inputs and calculated properties, plus
JSON configurations for the managers. Examples include `TransitionLength`,
`CurveRadius`, `TotalTurnAngle`, `TrackConfigurationJSON`,
`OutputBehaviour`, `CircularArcAngle`, `TotalCentrelineLength` and automatic
entry/exit-straight lengths. The settings object receives
`ProductionRecordIndexJSON`; an unsplit template also receives the parameter
properties. These document properties persist when the document is saved.
The generation function itself does not save an FCStd file.
[Stored parameters][stored-parameters]; [write calls][record-materialisation].

After those writes, the transaction ends with this source excerpt:

```python
_document_recompute(doc)
doc.commitTransaction()
transaction_open = False
```

The later `_document_recompute()` definition calls `doc.recompute()` and adds
timing information only when a guided measurement is active. It supplies no
additional rollback or state-equality check.
[Commit][commit-and-abort]; [final recompute helper][recompute].

Export, production-schedule creation and material-report creation follow the
generation commit. Schedule and report failures are caught separately and
reported as failures while generated geometry remains. The host recomputes
again, selects the top view, fits the view and shows **Railway production
outputs created**, with the set, removal count, geometry and report results.
Export is a separate boundary: enabling it adds earlier preflight and later
file operations, with the current B16 policy supplied by the export adapter.
File-publication details are outside this chapter.
[Post-commit operations][after-commit]; [result dialogue][result-dialogue];
[current export policy][export-policy].

## Failure and Undo limits

The transaction exception handler is short. This source excerpt follows the
creation and commit block inside `run_macro()`:

```python
except Exception:
    if transaction_open:
        try:
            doc.abortTransaction()
        except Exception:
            pass
    raise
```

It attempts to abort an open transaction and then raises the original error.
An abort failure is suppressed. There is no read-back comparison, manual
reconstruction or preview recovery here. The outer handler shows **Railway
template error** and writes `Railway template error: ...` to the console.
[Abort and commit][commit-and-abort]; [outer handler][result-dialogue];
[error dialogue][error-dialogue].

| Failure or cancellation point | State that can remain |
| --- | --- |
| Main dialogue cancelled | Existing generated objects remain; a newly opened empty document can remain |
| Replacement declined or preparation rejected | Old generated objects remain; accepted-input preferences may already have changed |
| Creation fails with the generation transaction open | The host attempts FreeCAD abort; restoration depends on that abort succeeding |
| Export, reports or final view update fail after commit | The generated set has already committed; these operations do not abort that transaction |

The transaction participates in FreeCAD history, but the whole operation is
not one atomic document-and-preference-and-file change. Post-commit utilities
have their own behaviour. Do not promise that one Undo reverses everything
above, or that document Undo restores remembered preferences. Historical GUI
evidence demonstrates complete Undo/Redo and a successful injected-abort case
for its named fixture; it does not establish recovery from every failure.
[Workflow history evidence][workflow-evidence].

## A two-track walkthrough

Use main radius 600 mm, both main Euler easements 600 mm, +90° total turn and
32 mm strip width. Add one **Outside** track in **Euler - match spacings** mode
with entry/curve/exit spacings of 50/55/50 mm, width 32 mm, and both output flags
on. Disable straight routes, physical platforms, formation, sectioning and
production export. These numerical inputs follow the retained
[preparation fixture][preparation-test].

The secondary circular radius is 655 mm. Its equal entry and exit spacing
requests lead to equal solved Euler lengths of approximately **559.410 mm**;
the retained alignment validator records the unrounded value. Those solved
lengths replace the secondary configuration's length fields during preparation.
The [geometry chapter](curves-and-spacing.md) explains why equal spacing
requests do not require copying the main easement length.
[Recorded numerical expectation][numeric-test].

In a document without set identifiers, creating this arrangement plans
`SET-001`. The expected geometry is one compound containing two strip solids,
plus two separate curve centreline objects. Settings and production metadata
accompany these outputs. Creating it again plans the next unused identifier; choosing
replacement instead plans `SET-001` and removes all recognised generated
sets inside the transaction. This is a source-derived walkthrough, not an
executed GUI result or an assertion of the total document-object count.
[Set allocation][identity]; [object creation][document-creation].

## Evidence and source map

The retained [July 2026 routed-workflow comparison][workflow-evidence] covers
handed replacement, full Undo/Redo, save/reopen, zero-angle rejection and a
failure injected at the first tagging call after removal. It used an earlier
B16 transition composition and a copied fixed fixture. Its
[driver][workflow-driver] deliberately bypasses the remembered-input reader,
so that result does not validate preference precedence.

The [later preparation evidence][preparation-evidence] records package/host
equivalence, configuration mutation and a bounded platform-widening GUI
lifecycle. Its API checks and [native fixture][native-test] cover preparation
and preservation of document state by that calculation, not the complete
generation transaction. These retained accounts identify their own source
and runtime limits; neither is a new run at this chapter's revision.

| Contributor question | Owning source |
| --- | --- |
| What does acceptance return? | [`CurveInputDialog.values()`][values] and [`run_macro()` entry][workflow-entry] |
| Which calculation actually runs? | [B16 adapters and bindings][calculation-binding], then [curves and spacing](curves-and-spacing.md) |
| What can replacement remove? | [Recognition predicates and cleanup][cleanup] |
| What is stored and when does it commit? | [`store_parameters()`][stored-parameters] and [generation commit/abort][commit-and-abort] |

All excerpts were inspected against the pinned source. No FreeCAD session,
workbench tool or executable example was run for this chapter. A documentation
build checks the page, not geometry or rollback. Code excerpts retain the
upstream [GPL-3.0-or-later notice][notice].

[revision]: https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf
[launcher]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/TrackTemplate.FCMacro#L101-L177
[host-loader]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/b15_workflow_host.py#L97-L209
[launch-binding]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L2984-L3048
[calculation-binding]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L1127-L1202
[export-policy]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/core_export_policy.py
[architecture]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/ARCHITECTURE.md#accepted-direction
[workflow-entry]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40796-L40882
[settings-selection]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L6818-L6849
[accept-button]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4760-L4789
[acceptance]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40883-L40911
[main-controls]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L3593-L3740
[defaults]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L332-L352
[values]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L6318-L6367
[row-config]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4827-L4850
[remembering]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L1424-L1639
[remember-call]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40910-L40932
[replacement-question]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40934-L40959
[validation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40961-L41003
[prepare-call]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41005-L41018
[preparation-adapter]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L427-L453
[preparation-contract]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/contracts/phase7-track-preparation.md
[alignment-checks]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41020-L41128
[shape-preparation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41130-L41255
[strip-shape]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L9634-L9682
[remaining-preparation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41256-L41640
[identity]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L6852-L6917
[output-modes]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L324-L326
[cleanup]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L6737-L6965
[transaction-entry]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41642-L41667
[document-creation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41665-L41755
[record-materialisation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L42589-L42664
[stored-parameters]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L21706-L21845
[commit-and-abort]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L42666-L42675
[recompute]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L47495-L47504
[after-commit]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L42677-L42796
[result-dialogue]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L42911-L42975
[error-dialogue]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L6663-L6669
[workflow-evidence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-07-22-b16-transition-routed-workflow-parity.md
[workflow-driver]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tools/freecad_bridge/probes/b14_ordinary_edit_driver.py#L374-L392
[preparation-test]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_phase7_track_alignment_preparation.py#L122-L155
[numeric-test]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_phase1_alignment.py#L92-L120
[preparation-evidence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-09-20-phase7-track-preparation-regression.md
[native-test]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/freecad_validate_phase7_track_alignment_preparation.py
[notice]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/NOTICE.md
