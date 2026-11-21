<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted for the TrackTemplate developer handbook, 2026-10-24.
-->

# How C10 turnout placement and editing work

A turnout is **switches and crossings (S&C)**: it lets a route leave the host
track. TrackTemplate places a natural REA C10 reference layout on an existing
generated centreline. The host can be straight, circular or contain an Euler
(clothoid) transition. The difficult part is retaining the C10's relative
construction geometry while following the *actual host alignment*, then
changing that placement without losing the existing turnout identity or
production records.

The manager's stated design intent is to map the complete turnout through the
host centreline and to validate a replacement before committing an edit. **An
inference from the code:** storing one switch-toe chainage and one host identity
also makes placement reproducible after the FreeCAD document is reopened. The
workbench's stored configuration, rather than the current camera view or an
arbitrary picked XY position, defines the turnout. [Manager description][ui];
[placement builder][build]; [turnout identity][identity]

**Implementation examined:** TrackTemplate
[`7965bfc4671668f889c1f43fb8336c5146c3f5cf`][revision]. The manager,
C10 source dimensions, host mapping, FreeCAD objects and edit transactions
remain in the retained B15 macro. The effective B16 composition supplies
`turnout_valid_toe_range` and `turnout_host_station_interval` from
`tracktemplate.domain.turnout`; it supplies
`turnout_configuration_change_summary` through a compatibility adapter to
`tracktemplate.application.turnout_edit`. These are **internal calculations**,
not an independent FreeCAD API for creating a turnout. [Composition][bindings];
[domain][domain]; [edit summary][summary]

## Find the host and choose the placement

In the main generation dialogue, open **REA C10 turnout and crossover
manager...** after a generated template set exists. A FreeCAD document must be
open. In the manager, select the **Turnouts** tab. The adjacent **Crossovers**
tab is a different workflow. [Dialogue entry][entry]; [manager][ui]

The **Host track and placement** controls have these meanings:

| Visible control | Meaning in the code |
| --- | --- |
| **Generated host centreline** | A generated `Centreline`, `StraightTrackCentreline` or `TrackCentreline` source whose shape yields ordered station data. The list identifies its template set, route, track and measured host length. |
| **Refresh hosts** | Read the eligible centrelines in the current document again. |
| **Use selected centreline / picked point** | Match a selected FreeCAD centreline by object `Name`. If the selection includes a picked point, project it onto the nearest sampled host segment and use that segment's chainage, clamped to the valid toe range. |
| **Switch-toe chainage (mm)** | Distance from station 0 at the start of the *host's ordered centreline*, measured in its travel direction. Three decimal places are displayed; the placement is determined by this value. |
| **-100, -10, -1, +1, +10, +100** | Move the proposed toe by that many millimetres along the host. Each nudge is clamped to the spin box's current range. No document geometry changes until Create or Apply. |
| **Orientation** | **Facing in host travel direction** follows increasing host chainage; **Trailing against host travel direction** reverses turnout travel against the host's order. |
| **Handing** | **Left-hand** or **Right-hand**, measured relative to the turnout's chosen travel direction, not the screen or an absolute compass direction. |

The host is an object identity, not a free XY location. `turnout_host_alignment`
uses its shape: it prefers an ordered wire discretisation, then tries shape
discretisation and vertices. It constructs `points`, `headings` and an
accumulated station total. A picked point is projected onto those sampled
segments. The nearest projected chainage is an *input suggestion*, which the
range rule still constrains; picking is not a second railway geometry solver.
[Host discovery][hosts]; [picker][picker]

The **OO and production geometry** controls default to a **Track gauge (mm)**
of `16.5` and a **Design flangeway (mm)** of `1.0`. The former sets the model
rail separation; the latter enters the C10 common-crossing calculation. They
can change both the curved reference layout and its total occupied length.
The **template width and thickness** are derived from the host's recognised
template-set settings when available. `turnout_host_template_dimensions`
uses its width and thickness defaults if those settings are absent. The
dialogue has no independent width or thickness editors.
[Dimensions][dimensions]; [host section][host-width]

The following options select **separate generated reference objects**:

| Checkbox (exact label) | Initial value | Output or calculation |
| --- | --- | --- |
| **Create full REA timber outlines** | On | Outlines for the source-driven timber positions and stepped lengths. |
| **Create timber centre lines** | Off | Separate transverse centre-line marks. |
| **Engrave timber identities** | On | Labels such as `J1`, `S1`, `T1` and crossing positions. |
| **Engrave rounded timber lengths** | Off | Model-length labels on the separate label object. |
| **Create TOE, HEEL, FP, BN, A and VJ datums** | On | Construction marks for the toe, heel, fine point, blunt nose, A timber and vee joint. |

These options control drawing or engraving geometry. They do not turn a label
into a rail or change the track-gauge and flangeway calculations. The manager
also reports sampled minimum radii and counts timber outlines outside the
combined template envelope or crossing an internal strip void; the report is
**diagnostic**, not a promise that every timber has physical support. Its
timber spans are derived from C-switch individual centres, an equally spaced
closure region, fixed crossing positions and exit sleepers. The source
converts a six-inch **prototype** increment into model millimetres. It then
applies `_turnout_stepped_timber_length`, which calculates
`max(step, floor(raw / step + 0.67) * step)`. This source convention can
round a small remainder down. [Timber layout][timbers];
[timber shapes][timber-shapes]; [host summary][summary-ui]

The **Guided turnout workflow** shows the main sequence and **Run next safe
step**. Select **Show specialist and maintenance controls** to expose the
individual Create, Edit, Apply, Cancel, Remove and integration buttons. The
final guided-step method is a later B15 replacement (`_turnout_run_next_guided_step_v13`);
it calls the same creation and edit handlers, then proceeds to chair analysis,
model support, 2D validation and possible host integration. Those later stages
have separate coverage. [Guided final binding][guided];
[GUI coverage](../gui-coverage.md)

## From a natural C10 to a curved host

The reference turnout starts in a **local C10 coordinate system**. Its
longitudinal coordinate `x` is measured in model millimetres from the switch
toe; `x = 0` is `TOE`. The turnout road moves sideways by a local offset `y`.
The code derives this natural straight-reference geometry using an REA C
semi-curved switch and a regular 1:10 crossing, with source notes recording
comparisons to Templot5. The nominal switch and turnout radii belong to that
straight-reference calculation. The *mapped* host and branch radii are
sampled after bending the geometry around the selected alignment.
[Dimensions][dimensions]; [rail references][rails]; [mapping metrics][metrics]

For the default model scale `76.2`, one prototype inch becomes exactly one
third of a model millimetre. The model begins **65 prototype inches before
the toe**, to include the switch-front reference, and continues beyond the
vee joint. This short excerpt from `rea_c10_dimensions` defines the complete
module, after the preceding code has calculated `blunt_nose_x`:

```python
vee_joint_length = (4.0 + 12.5 + (6.0 - 1.0) * 30.0) * inch
vee_joint_x = blunt_nose_x + vee_joint_length
exit_extension = 60.0 * inch
module_start_x = -switch_front
module_end_x = vee_joint_x + exit_extension
```

The *module start* is negative because it lies behind the toe; the *module
end* is positive. At the default gauge, flangeway and scale, these produce
approximately `module_start_x = −21.667 mm` and
`module_end_x = +361.400 mm`, for a complete **383.066 mm** module. The 60
prototype inch exit extension contributes **20.000 model mm**. These values
are calculated from the source equations; they are not lengths of an actual
host curve. [Module extent][module]

The retained B15 `map_turnout_local_point` maps each sampled local point onto
the selected centreline. Its relevant lines are:

```python
direction = _turnout_orientation_sign(orientation)
hand = _turnout_hand_sign(handing)
station = float(toe_chainage) + direction * float(local_x)
if station < -1.0e-7 or station > host_data["total"] + 1.0e-7:
    raise ValueError(
        "The turnout requires host chainage {:.3f} mm, outside the available 0.000 to {:.3f} mm range.".format(
            station, host_data["total"]
        )
    )
point, host_heading = interpolate_alignment_station(host_data, station)
travel_heading = host_heading if direction > 0.0 else host_heading + math.pi
normal_x, normal_y = left_normal(travel_heading)
signed_y = hand * float(local_y)
return vector_xy(point.x + signed_y * normal_x, point.y + signed_y * normal_y)
```

In this excerpt, `toe_chainage` is on the **host**, `local_x` and `local_y`
belong to the **natural C10**, and `host_heading` is the tangent of the
sampled centreline at that host station. Facing uses `direction = +1`;
trailing uses `−1` and turns the travel heading by π radians. Left-hand uses
`hand = +1`; right-hand uses `−1`. The resulting FreeCAD plan point is on
the left or right normal of the turnout's travel heading. The function also
rejects a station outside the host length *before* interpolation.
[Point mapping][mapping]

The mapping is used for the main-road and turnout-road strips, the complete
stock, switch, closure, wing, vee and check-rail reference polylines, and
timber/label/datum geometry. It samples straight, circular and transitioned
segments through the actual ordered host shape. It does **not** assert that
an originally straight-reference C10 retains its nominal radius after the
mapping. The UI therefore names **sampled** host and turnout-road minimum
radii, separately from nominal switch and reference turnout radii.
[Rail components][rails]; [builder][build]; [metrics][metrics]

## The toe fits only when the entire module fits

Let `L` be the host length in millimetres, `s` the selected switch-toe host
chainage, and `a = module_start_x` and `b = module_end_x` with `a < 0 < b`.
The whole module occupies the stations between `s + d·a` and `s + d·b`,
where `d = +1` for facing and `d = −1` for trailing. Both endpoints must
lie in `[0, L]`.

The effective B16 function `turnout_valid_toe_range` implements that
constraint. This is an exact excerpt from `tracktemplate.domain.turnout`;
`_turnout_orientation_sign` supplies `+1` or `−1`:

```python
total = max(0.0, float(host_length))
start_x = float(dimensions["module_start_x"])
finish_x = float(dimensions["module_end_x"])
if _turnout_orientation_sign(orientation) > 0.0:
    minimum = max(0.0, -start_x)
    maximum = min(total, total - finish_x)
else:
    minimum = max(0.0, finish_x)
    maximum = min(total, total + start_x)
return minimum, maximum
```

For facing travel the toe must leave room for the switch front *before* it
and the crossing/exit *after* it. Trailing reverses which end needs the long
clearance. When `maximum < minimum`, the host is too short to hold the whole
turnout. The UI shows **no complete C10 fits** and disables Create/Apply.
Otherwise the toe spin box is clamped to the computed range. The builder
checks the range again so that direct calls cannot evade the UI limit.
[Domain toe range][domain]; [range UI][summary-ui]; [builder validation][build]

The second B16 calculation records the **occupied interval**, independently
of which station is the switch toe. Its source excerpt is:

```python
direction = _turnout_orientation_sign(orientation)
station_a = float(toe_chainage) + direction * float(
    dimensions["module_start_x"]
)
station_b = float(toe_chainage) + direction * float(
    dimensions["module_end_x"]
)
return min(station_a, station_b), max(station_a, station_b)
```

The interval is stored as `host_station_interval` on the turnout configuration.
`_turnout_find_overlap` compares it with existing turnouts **on the same host
object**, ignoring the current turnout when editing. An overlap greater than
`TURNOUT_OVERLAP_TOLERANCE = 0.10 mm` is rejected. This is a station-interval
conflict check, not a full 3D interference analysis. The same B16 interval
function also serves host integration and crossover solving, which have
their own more involved rules. [Occupied interval][domain];
[overlap check][overlap]; [composition][bindings]

### Worked example: a curved host and one C10

The [curved-host FreeCAD validation script][curved-evidence] uses a generated
centreline of **1,542.475839 mm** and a source recipe with switch-toe chainage
**746.298 mm**, 16.5 mm gauge, 1.0 mm flangeway and a left-hand facing
turnout. These figures provide a concrete input; the arithmetic below was
checked independently from the dimensions formula without running FreeCAD.
[Recipe][recipe]; [curved test][curved-evidence]

```{figure} ../_static/figures/turnout-host-intervals.svg
:alt: Two bars on a host-chainage scale. The facing C10 occupies 724.631 to 1107.698 mm; the trailing C10 occupies 384.898 to 767.965 mm. Both use toe 746.298 mm.
:width: 100%

Host station occupancy for the same toe in two orientations. The orange
markers identify the toe. The bars include the module's switch-front and
crossing-end extents.
```

| Input or derived value | Facing with host travel | Trailing against host travel |
| --- | ---: | ---: |
| `module_start_x`, `module_end_x` (local, mm) | `−21.667`, `+361.400` | Same natural C10 |
| Valid toe range on this host (mm) | `21.667–1181.076` | `361.400–1520.809` |
| Toe for this example (mm) | `746.298` | `746.298` |
| Occupied host interval (mm) | `724.631–1107.698` | `384.898–767.965` |
| After a **+10 mm** toe nudge | `734.631–1117.698` | `394.898–777.965` |

Each orientation occupies **383.066 mm** of host chainage, despite the
different start and end stations. For example, facing begins at
`746.298 − 21.666667 = 724.631333 mm` and ends at
`746.298 + 361.399567 = 1107.697567 mm`. Trailing uses the reversed sign.
The diagram shows station occupancy, **not** a scale drawing of the curved
rails, turnout hand or source timber lengths.

With facing orientation, a requested toe of **1182.000 mm** would require the
far end at approximately **1543.400 mm**, beyond this host's end at
**1542.476 mm**. The builder rejects it as out of range. The UI normally
prevents that input by clamping the toe field; a picked point or nudge is
also clamped. A second turnout that overlaps this module on the same host
can reject an otherwise legal chainage. [Validation][build]; [picker][picker]

## Create the managed turnout

The **Create curve-inheriting C10 turnout** action calls
`TurnoutManagerDialog.create_turnout`, which passes the chosen host,
chainage, orientation, handing, gauge, flangeway and output options to
`create_curve_inheriting_c10_turnout`. Before opening a FreeCAD transaction,
the builder confirms the source is a recognised centreline, validates the
complete module range and overlaps, resolves the host's template-set identity,
calculates the C10 and maps/validates all rail and timber polylines. It makes
the combined strip solid and cutting footprint in memory.
[Create handler][create-ui]; [build][build]

The create operation then opens a document transaction and creates a stable
`TO-001`-style identifier and a turnout group. Its children have separate
roles so that later operations can find them by identity:

| Generated role | Representation and purpose |
| --- | --- |
| `TurnoutSettings` | Persistent configuration, identity and source metadata, without a rail shape. |
| `TurnoutTemplate` | Combined main and branch template-strip solid (3D export source). |
| `TurnoutPlanOutline` | Combined plan cutting footprint (2D cutting source). |
| `TurnoutRailGeometry` | Complete rail and centreline references (engraving). |
| `TurnoutTimberGeometry`, `TurnoutTimberCentres` | Optional outline and centre-line engraving objects. |
| `TurnoutTimberLabels`, `TurnoutConstructionMarks` | Optional identity/length labels and construction-datum engraving objects. |

It saves a `TurnoutConfigurationJSON` value on identified objects, updates
`TurnoutConfigurationsJSON` on the template-set settings object, and writes
turnout export sources into `ProductionRecordIndexJSON`. Optional blank
shapes do not add production records. The existing host centreline, original
track template, sections, platforms and other railway geometry are not
replaced by *standalone turnout creation*. That later change is the distinct
**Integrate selected turnout** workflow. [Create transaction][create];
[catalogue][catalogue]; [host integration][integration]

## Edit an existing turnout without losing its identity

Select the row in **Existing Stage 8A turnouts**, then choose **Edit selected
turnout** (or the guided **Edit selected turnout** action). The manager loads
the saved controls, remembers `editing_turnout_id` and the original
configuration, and locks **Generated host centreline** and the results table
while editing. The picked-point button can still move the toe **on the same
host**; it rejects a different selected centreline. The UI disables creation
and integration actions in edit mode. [Edit entry][edit-ui]; [edit mode][edit-mode]

The saved host is a fixed part of this edit. The code checks it again:

```python
if turnout_integration_by_id(doc, identifier) is not None:
    raise ValueError("Remove the host-template integration before editing {}. This preserves all affected production records and section boundaries safely.".format(identifier))
old_config = turnout_config_by_id(doc, identifier)
if old_config is None:
    raise ValueError("Turnout {} no longer exists in this document.".format(identifier))
if str(getattr(host_obj, "Name", "")) != str(old_config.get("host_object") or ""):
    raise ValueError("An existing turnout must remain on its original host centreline during Stage 8A editing.")
```

This is a source excerpt from `edit_curve_inheriting_c10_turnout`. The same
function also requires the existing group, settings, solid, outline and rail
objects. After building a proposed turnout, it verifies that the template-set
ID is unchanged. A missing source object, different host or set, or active
integration therefore blocks the replacement. [Edit builder][edit]

The B16 `turnout_configuration_change_summary` compares the proposed and
original values. It names changes in chainage, handing, orientation, gauge,
flangeway and each output checkbox; it also reports older rail/timber revision
upgrades when necessary. The UI uses the same summary to enable **Apply
turnout changes** and display a confirmation list. With no changes or
revision upgrade, Apply is disabled. Choosing **No** in the confirmation
leaves the editor open for further changes. [Summary algorithm][summary];
[Apply UI][apply-ui]

Once confirmed, the edit function builds the **entire replacement geometry in
memory** using the original turnout ID and ignoring that turnout in the
overlap check. If building fails, it has not yet opened the edit transaction.
For a successful build, the transaction updates the existing group, settings,
solid, outline and rail objects *in place*. The optional timber, label and
datum objects are reused when present, added when newly enabled or removed
when their resulting shapes are empty. The code refreshes the production
index by removing the old turnout source names before appending the current
records, then updates the saved turnout catalogue and commits.
[Edit transaction][edit]; [optional objects][optional];
[production records][production]

The important result is that `TO-001` and the established **required** FreeCAD
source-object names survive the edit. Optional objects retain their names only
if they survive the selected options. The curved-host retained validation
also checks unchanged names and production-record IDs for a **handing-only**
edit where the optional output selection remains the same. That test is
evidence for its controlled fixture, not proof for every possible new set of
checkboxes. [Curved-host evidence][curved-evidence]

### Cancellation, rejection and removal have different boundaries

| Situation | Document and editor result | Recovery |
| --- | --- | --- |
| **Cancel edit** | Discards the proposed controls and exits edit mode; no turnout builder or production-record update is called. | Select the turnout again to start another edit. |
| **No changes** | Apply stays disabled in the normal UI. A direct API call still clears derived chair displays, checks required objects and builds the proposed geometry. Only an unchanged, successfully validated build returns `old_config` without opening an edit transaction. | Change a setting or cancel. An older revision can still present a geometry-upgrade change. |
| **No** at the Apply confirmation | Does not call the edit builder; edit mode and proposed controls remain. | Amend settings or choose **Cancel edit**. |
| Out-of-range toe, overlapping module, wrong host or set, missing required object, or invalid geometry | Builder or guard raises an error. The edit transaction is not committed; if an error occurs after the transaction opens, the code calls FreeCAD `abortTransaction()`. The manager stays in edit mode and shows the error. | Choose a valid toe/host state, resolve the conflicting turnout, restore missing document objects, or cancel. Do not assume the error has repaired missing sources. |
| Already integrated | Edit and Remove are disabled in normal selection mode; the edit builder also rejects active integration. | Use **Remove host integration** to restore the original host and standalone production records, then edit. |
| **Remove selected turnout** | With confirmation and no active integration, removes the selected standalone group/objects and their production entries in one FreeCAD transaction; the host railway geometry is left in place. | Cancel the confirmation to keep it. FreeCAD Undo may be available for a committed transaction; verify the document state before further operations. |

There is one narrower side effect to remember: `edit_curve_inheriting_c10_turnout`
calls `clear_chair_analysis_display` **before** checking required objects and
building the replacement. Its final binding also removes derived 2D chair
display objects. Consequently, a rejected edit can clear those visible
analysis/layout overlays even though the turnout's rails, template geometry
and production records were not replaced. Re-run or rebuild the affected
analysis display after a failed edit if needed. Do not describe this as a
complete no-change guarantee for *all* document objects. [Clear call][edit];
[final display cleanup][chair-clear]

The dialog's **Close** button asks whether to cancel an active edit; **Cancel
edit** itself just drops the proposed configuration. FreeCAD's document
transaction/Undo boundary is separate from those dialogue controls. Editing a
standalone turnout is also different from
[converting it into a crossover](turnout-crossover-conversion.md),
integrating it with host production or creating a non-production reference
copy. [Close behaviour][remove-ui]; [integration][integration]

## Evidence, terminology and current limits

- The B16 [toe-range][toe-test], [host-interval][interval-test] and
  [edit-summary][summary-test] validators check the package decisions against
  retained behaviour and verify the intended composition routes. The
  [curved-host FreeCAD comparison][curved-evidence] describes a controlled
  create, handing edit and production-record check across the retained
  implementations. These are **source-inspected test definitions**; this
  documentation change did not execute FreeCAD.
- The worked numerical example was evaluated separately from the source
  formulas in standalone Python. It demonstrates station arithmetic and
  acceptance bounds; it is **not** a FreeCAD geometry, strength, construction
  clearance or manufacturing test. Sampled radii depend on the selected host.
- The [upstream terminology register][terms] accepts S&C and the centreline
  station context, but marks *switch/points/turnout*, *crossing/vee/frog* and
  *sleeper/timber* distinctions as `review-required`. This chapter identifies
  source-labelled rail, timber and datum roles without approving disputed
  prototype nomenclature or a finished physical turnout design.
- The C10 geometry is fixed at this implementation stage. Host integration,
  [crossover geometry](crossover-geometry.md), chair fit and production
  readiness have additional checks and their own
  [GUI coverage](../gui-coverage.md). A successful Create or Apply
  does not constitute approval of production chairs or physical clearances.
  ASD-STE100 Issue 9 conformance has **not** been formally verified for this
  chapter.

[revision]: https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf
[entry]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4631-L4641
[manager]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L39686-L39947
[ui]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L39686-L39730
[hosts]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L22021-L22095
[picker]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40175-L40230
[dimensions]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L22098-L22366
[host-width]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L23359-L23382
[timbers]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L23063-L23165
[timber-shapes]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L23197-L23335
[summary-ui]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40235-L40328
[guided]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46811-L46963
[module]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L22261-L22268
[rails]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L22530-L22752
[mapping]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L22788-L22805
[metrics]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L22896-L22918
[domain]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/turnout.py
[bindings]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L249-L271
[summary]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/application/turnout_edit.py
[overlap]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L22920-L22946
[build]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L23603-L23817
[create-ui]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40517-L40560
[create]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L23959-L24163
[catalogue]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L23435-L23470
[identity]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L23387-L23432
[edit-mode]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40135-L40222
[edit-ui]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40344-L40455
[apply-ui]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40459-L40516
[edit]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L24166-L24405
[optional]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L23888-L23934
[production]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L23494-L23512
[integration]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40689-L40732
[remove-ui]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40752-L40794
[chair-clear]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46137-L46139
[recipe]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tools/freecad_bridge/turnout_recipe.py#L24-L43
[curved-evidence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/freecad_validate_phase8_curved_host_turnout.py#L97-L222
[toe-test]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_phase8_turnout_toe_range.py
[interval-test]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_phase8_turnout_host_interval.py
[summary-test]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_phase8_turnout_edit_summary.py
[terms]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md#current-contextual-register
