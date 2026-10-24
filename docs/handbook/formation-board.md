<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted for the TrackTemplate developer handbook, 2026-10-24.
-->

# How the formation board follows tracks and platforms

The **Formation board** controls create a continuous support beneath selected
track-template strips and physical platforms. The board must cover their
occupied width, leave the requested margin, and remain wide enough between
larger features. Its outline therefore need not follow each platform taper
exactly. The source records the intended construction: sample the route, find
the occupied limits, broaden abrupt changes, close the ends and extrude one
face. [Displayed explanation][controls]; [sweep rationale][broadening-call]

This chapter follows that calculation from the controls to the cutting outline,
solid and separate engraving objects. Read [curves and spacing](curves-and-spacing.md)
and [physical platforms](platforms.md) for the geometry supplied to it.

**Source:** workbench revision
[`7965bfc4671668f889c1f43fb8336c5146c3f5cf`][revision]. The formation controls,
sweep and native shape builders remain in the retained B15 host. B16 supplies
selected Core station calculations through adapters; it does not replace the
formation operation with a complete Core API. The main curve family and each
straight route prepare their boards separately. [Effective station bindings][bindings];
[curve caller][curve-caller]; [straight caller][straight-caller]

## Read the controls as a set of decisions

The main dialogue stores formation settings until **Generate** reads them and
prepares the geometry. Editing a field does not itself replace a board in the
FreeCAD document. With **Enable formation board:** off, the associated fields
are disabled. Turning a control off or disabling its editor retains its value.
[Control state][control-state]; [reading the fields][field-values];
[generation lifecycle](generate-template-set.md)

| Visible control | Meaning and default |
| --- | --- |
| **Enable formation board:** | Request the board calculation and its selected outputs. Defaults to off. |
| **Include track-template strips:** | Include tracks whose printable **Strip** output is enabled. Defaults to on. A centreline alone does not select that track's width for the board. |
| **Include platform footprint:** | Include the calculated edge geometry of enabled physical platforms. Defaults to on. A platform can contribute with edge-only output; it does not need a visible solid. |
| **Outer margin:** | Add material beyond the occupied limits and, normally, beyond exposed route ends. Default 10 mm; editor range 0–10,000 mm. |
| **Minimum board width:** | Expand a narrower transverse section to this width. Default **20 mm**; editor range 0.1–10,000 mm. The worked example deliberately uses 120 mm. |
| **Formation output type:** | Choose **2D cutting outline**, **3D solid board**, or **2D outline and 3D solid**. Defaults to both. This selects document representations; the internal builder still prepares a solid. |
| **Board material thickness:** | Extrusion depth below the base plane. Default 12 mm; editor range 0.1–1,000 mm. Editable when the output type includes a solid. |
| **Show formation outline:** / **Show formation solid:** | Initial visibility of the corresponding unsplit object, when created. Both default to on. Each editor is enabled only when its representation is selected. |
| **Track-centreline engraving:** | Create separate engraving geometry from supplied track centrelines. Defaults to on. Its input selection differs from footprint inclusion. |
| **Platform-edge engraving:** | Create separate engraving geometry from enabled platforms' two longitudinal edges. Defaults to on. |

Length widgets display millimetres to three decimal places. These ranges and
defaults describe the software; they do not establish suitable sheet thickness
or support dimensions for a particular layout. The configuration reader
normalises margin to at least zero and minimum width and thickness to at least
0.1 mm. It replaces an unknown output type with the default.
[Defaults and normalisation][defaults]; [widgets][controls]; [length editor][length-editor]

The saved dictionary calls minimum width `minimum_neck_width`. It also contains
`fill_enclosed_gaps`, `smooth_outline` and `smoothing_tolerance`. The dialogue
constructs compatibility widgets for those three fields but does not put them
in the displayed formation layout. The current swept builder does not use
them. The older `create_formation_geometry` function used filling and smoothing
after combining faces; it is not the builder called by this workflow.
[Displayed field list][controls]; [older builder][old-builder]; [current builder][multi-builder]

## Select footprints before choosing a boundary

`create_formation_geometry_multi` returns `None` when formation output is
disabled. Otherwise it selects track strips and platform geometries. This exact
excerpt selects tracks; `all_alignments` contains the current curve family or
one straight route's alignments:

```python
selected_alignments = (
    [
        alignment
        for alignment in all_alignments
        if alignment.get("create_template", False)
    ]
    if config["include_track_templates"]
    else []
)
```

Thus both the formation inclusion checkbox and the track's printable Strip
choice matter. The neighbouring platform selection uses `include_platform`
and non-null entries in `platform_geometries`. Generate has already produced
those entries from enabled platform definitions, including edge-only
definitions. Body visibility does not remove their plan geometry. If neither
selection supplies anything, the operation rejects the request before building
a board. [Selection and rejection][multi-builder]; [platform preparation][platform-preparation]

Do not use one selection rule for every formation-related result:

| Result | Geometry supplied to it |
| --- | --- |
| Board footprint | Selected printable strips and selected enabled platform edges. |
| Track engraving | All curve-family alignments and the alignments of prepared straight routes, when track engraving is enabled. Strip, centreline-display and footprint-inclusion switches do not filter this collection. |
| Platform engraving | The enabled platforms' edge geometry, when platform engraving is enabled, independently of footprint inclusion and platform edge-object visibility. |
| Protected geometry for later registration | All non-null supplied track-protection and platform plan faces, independently of the footprint-inclusion switches. |

The generation caller and native builders own these different collections.
For example, a track whose strip is off can still supply an engraving line and
a protection face. Neither contribution automatically widens the footprint.
[Track protection][track-protection]; [engraving caller][engraving-caller];
[returned protection collection][multi-builder]

## Map the occupied edges to one reference track

### Use the reference's stations and normal

The sweep selects `all_alignments[0]` as its reference. For the curve board,
this is the main alignment, even when its own strip is not included. For a
straight board, it is that route's first alignment. The reference need not be
the physical platform's **Track A**. This distinction matters when comparing
platform length with the board's widening distance. [Reference selection][sweep-start]

Station zero belongs to the first supplied reference point. The station helper
accumulates XY chord lengths along successive points in the direction of
travel. Straight extensions can therefore change absolute stations. These are
sampled distances, not ideal circular arc lengths. At each station the left
normal is `(-sin(heading), cos(heading))`; positive offsets lie left of travel,
and negative offsets lie right. [Station calculation][station-core]; [normal][left-normal]

Each selected strip supplies two edge paths at half its width on either side
of its own centreline, using that track's local heading. Each selected platform
supplies its already tapered `edge_a` and `edge_b` paths. The formation routine
then maps every path into the reference track's station and offset coordinates.
[Source edge construction][source-edges]

### Project paths and collect their limits

`_project_formation_point_to_reference` follows an ordered reference cursor to
a nearby vertex, examines nearby segments, and projects the supplied point
onto those segments. It clamps the segment fraction and prevents the mapped
station from moving backwards. After choosing a station, it interpolates the
reference point and heading. This exact excerpt converts the remaining
displacement into a signed lateral offset:

```python
normal_x, normal_y = left_normal(reference_heading)
signed_offset = dot_xy(
    float(point.x) - float(reference_point.x),
    float(point.y) - float(reference_point.y),
    normal_x,
    normal_y,
)
```

The dot product measures displacement along the reference normal. The method
uses local sampled segments; it does not establish a globally unique nearest
point on an arbitrary looping route. If it finds no usable candidate segment,
it falls back to the preceding minimum station. Consecutive path samples mapped
within `1.0e-8` mm of the preceding station replace that sample with the latest
offset. This avoids a zero-length interpolation span but is not a comparison
that explicitly retains the most outward duplicate offset.
[Projection and fallback][projection]; [path samples][edge-samples]

Between mapped path samples, `_formation_offset_at_station` interpolates the
offset by station distance. It contributes only at existing reference stations
inside that path's mapped range. The following exact excerpt from
`_accumulate_formation_path_extents` updates the occupied limits at one such
reference index:

```python
left_extents[index] = (
    offset if previous_left is None else max(float(previous_left), offset)
)
right_extents[index] = (
    offset if previous_right is None else min(float(previous_right), offset)
)
```

The largest offset is the left limit and the smallest is the right limit.
Together they enclose the participating edge samples at that cross-section.
The operation does not preserve a hole between disconnected strips: the
eventual board spans from one outer limit to the other.
[Offset interpolation and accumulation][accumulation]

The first and last populated reference indices bound the active sweep. Missing
limits between known indices interpolate by **array index**, rather than by
station distance; the two kinds of interpolation must not be confused. Missing
values before or after a known sequence repeat its nearest value within the
active range. A very short path whose mapped range contains no reference sample
contributes no occupied sample. The builder rejects an entirely unusable
collection. [Missing-sample interpolation][fill-samples]; [active range][active-range]

## Add margin, broaden changes, then enforce width

The order matters. First, the sweep adds the margin to its left limits and
subtracts it from its right limits. This exact excerpt runs over the active
reference indices:

```python
for index in range(start_index, finish_index + 1):
    left_extents[index] = float(left_extents[index]) + margin
    right_extents[index] = float(right_extents[index]) - margin
```

The margin is transverse to the reference at each sampled section. The code
then broadens abrupt changes before applying minimum width.
[Margin and broadening order][broadening-call]

### Carry a wider section towards its neighbours

The source explains that the board should support a platform without copying
every taper point. `_broaden_formation_extent_transitions` makes one forward
pass and one backward pass. The caller fixes the maximum transverse slope at
`0.5`: an edge can move inwards by at most 0.5 mm for each millimetre of
reference-station distance. This is an implementation value, not a GUI field.
[Recorded rationale and value][broadening-call]

In this exact excerpt from the forward pass, `distance` is the difference
between successive reference stations. `upper_envelope` identifies the left
limit:

```python
allowance = maximum_slope * distance
if upper_envelope:
    broadened[index] = max(
        float(broadened[index]),
        float(broadened[index - 1]) - allowance,
    )
else:
    broadened[index] = min(
        float(broadened[index]),
        float(broadened[index - 1]) + allowance,
    )
```

For a left limit, `max` keeps the farther-left value. For a right limit, `min`
keeps the farther-right value. The backward pass applies the same relationship
from the other direction. Both passes can only move the envelope outwards.
A wide platform section can therefore require board material before the
platform starts and after it finishes. This operation broadens the sampled
limits; it does not fit a spline or invoke the hidden smoothing setting.
[Both passes][broadening-helper]

### Widen around the envelope's own midpoint

Next, `_simple_formation_swept_face` compares each broadened width with
`minimum_neck_width`. This exact excerpt follows the reads of `left_value`
and `right_value`:

```python
if left_value - right_value < minimum_width:
    midpoint = 0.5 * (left_value + right_value)
    left_value = midpoint + 0.5 * minimum_width
    right_value = midpoint - 0.5 * minimum_width
```

It adds equal amounts to the two sides of a narrow envelope. It does **not**
centre the board on the main track. An asymmetric arrangement remains offset
from that track. Width here means separation along the sampled reference
normal; this check alone is not a proof of the narrowest physical distance
anywhere in the final face. [Minimum-width calculation][minimum-width]

## Work through the two-track and platform example

Use the previous chapters' nominal left-turn geometry: a main circle of radius
600 mm and a matched outside circle of radius 655 mm. Set both printable strips
to 32 mm. The [platform example](platforms.md#work-through-a-150-mm-outside-platform)
places a 150 mm platform outside the outer track, with 20 mm edge clearance,
30 mm full width, 12 mm height and matched 30 mm ends. Set the formation margin
to 10 mm, minimum width to 120 mm and board thickness to 12 mm.

These are illustrative inputs. The calculations and figures use ideal
concentric-circle cross-sections and independent arithmetic. They are not
measurements from a newly generated FreeCAD board.

### Compare the middle with and without the platform

Use the **main track's signed left-normal offset** for every value below.
The outside centreline is at −55 mm. Its 32 mm strip therefore occupies
−71 to −39 mm. The platform's near and far edges are at −75 and −105 mm:
the 55 mm centreline gap plus the 20 mm clearance and, for the far edge,
the additional 30 mm width.

| Calculation at the full-width middle | Platform excluded | Platform included |
| --- | ---: | ---: |
| Occupied left limit, mm | +16 | +16 |
| Occupied right limit, mm | −71 | −105 |
| Left limit after 10 mm margin, mm | +26 | +26 |
| Right limit after 10 mm margin, mm | −81 | −115 |
| Width after margin, mm | 107 | 141 |
| Final left limit after the 120 mm minimum, mm | **+32.5** | **+26** |
| Final right limit, mm | **−87.5** | **−115** |
| Final width, mm | **120** | **141** |

With tracks alone, the 107 mm envelope has midpoint −27.5 mm. The minimum
adds 6.5 mm on each side, producing a 120 mm board about that same midpoint.
With the platform included, the 141 mm envelope already exceeds the minimum.
At this full-width middle, narrower neighbouring sections do not broaden it
further. The board top is at Z = 0 and its bottom at Z = −12 mm; platform
height and board thickness are separate inputs.
[Independent numerical record](../_static/figures/formation-example-values.json)

```{figure} ../_static/figures/formation-cross-section-example.svg
:alt: Two nominal transverse sections compare a 120 millimetre board supporting two track strips with a 141 millimetre board that also includes the outside platform.

Independent nominal cross-sections at the platform's full-width middle. Both use the main track's signed left-normal offsets; the board extends below the base plane.
```

### Follow the board beyond a platform end

The platform uses station along its outer host, while the formation sweep uses
the main track. In this ideal circular example, a relative outer-track distance
`u` corresponds to main-track distance `x = u × 600 / 655` at the same angle.
The 30 mm entry taper therefore spans about **27.481 mm on the main reference**.
Set `x = 0` at the main cross-section through the platform start; this is an
example origin, not the workbench's absolute station zero.

Away from the platform, the raw right limit with margin is −81 mm. At full
platform width it reaches −115 mm. In a continuous illustration of the 0.5
slope rule, this 34 mm outward difference needs **68 mm of main-reference
distance** to return to −81 mm. The board starts broadening at
`27.480916 − 68 = −40.519084` mm, before the platform begins.

At `x = 0`, the broadened right limit is approximately −101.260 mm. With the
left limit at +26 mm, the width is about **127.260 mm**, so the 120 mm minimum
does not act there. Away from this wider region, minimum width expands both
sides towards the tracks-only values of +32.5 and −87.5 mm. The next figure
shows why applying the width minimum before broadening would teach the wrong
sequence. [Independent values](../_static/figures/formation-example-values.json)

```{figure} ../_static/figures/formation-width-example.svg
:alt: An unrolled nominal profile compares occupied margins, widening around the platform ends and the final two board edges after minimum width is applied.

Continuous illustration using relative main-track distance. The actual workbench projects sampled edges and performs two passes over its existing station array; this plot is not its generated cutting outline.
```

## Close the ends at the correct tangent boundary

For each reference point, the sweep places left and right boundary points at
their calculated normal offsets. At the first and last active indices, it
also shifts the reference point along its tangent. The default start shift is
`−outer_margin`, and the default finish shift is `+outer_margin`. Both points
at one end receive the same shift, so the closing cap remains perpendicular to
that endpoint's heading. [Shift defaults][sweep-start]; [boundary construction][end-construction]

This exact excerpt in `_simple_formation_swept_face` selects and applies the
terminal shift. The surrounding loop has already obtained `point` and `heading`:

```python
tangent_shift = 0.0
if index == start_index:
    tangent_shift = start_tangent_shift
elif index == finish_index:
    tangent_shift = finish_tangent_shift
base_x = float(point.x) + tangent_shift * math.cos(heading)
base_y = float(point.y) + tangent_shift * math.sin(heading)
```

The left boundary runs forwards and the right boundary returns in reverse
order. The final face builder closes that combined path. The end treatment
extends the terminal cap; it is not a rounded offset around every perimeter
corner. [Closed boundary][end-construction]

Connected straight routes override the tangent shifts so adjoining ends stop
at their shared tangent boundary. The entrance straight travels towards the
curve; the exit straight travels away. With a 10 mm margin:

| Board situation | Start shift, mm | Finish shift, mm |
| --- | ---: | ---: |
| Both ends exposed | −10 | +10 |
| Entrance straight connected to the curve | −10 | 0 |
| Exit straight connected to the curve | 0 | +10 |
| Curve with an entrance connection only | 0 | +10 |
| Curve with an exit connection only | −10 | 0 |
| Curve with both connections | 0 | 0 |

For a 600 mm straight measured from its start in its travel direction, the
corresponding cap coordinates are −10 and 610 mm when independent, −10 and
600 mm at an entrance connection, or 0 and 610 mm at an exit connection.
[Straight cap settings][straight-caller]; [curve cap settings][curve-caps];
[straight direction](straight-routes.md)

A straight board requires formation enabled, track-strip inclusion and at
least one printable strip. Its preparation forces platform inclusion off.
The curve helper suppresses a cap margin when it finds a connected route mode;
it does not check that the straight actually emitted a board. The rule also
does not fuse the boards or guarantee identical lateral widths at the seam.
It specifies their tangent end planes. [Straight conditions][straight-caller];
[connection-mode checks][curve-caps]

## Build native outputs and separate engraving geometry

`_create_plan_face` cleans consecutive XY duplicates within `1.0e-7` mm,
closes the boundary and creates a polygon wire and `Part.Face`. It rejects
insufficient, open, null or invalid geometry. The multi-platform builder checks
the resulting footprint where `isValid()` is available, then performs this
exact extrusion:

```python
body = footprint.extrude(
    App.Vector(0.0, 0.0, -config["board_thickness"])
)
if body.isNull():
    raise ValueError("FreeCAD could not extrude the formation-board solid.")
```

The negative Z vector places the board below track level. This block runs even
for **2D cutting outline**: the output choice controls which document objects
are emitted later. An outline-only request can therefore still fail during
internal extrusion. The code checks for a null body here; it does not perform
an additional body `isValid()` check in this block.
[Plan-face checks][plan-face]; [active builder][multi-builder]

The returned dictionary contains `face`, `outline`, `body`, `area` and
`protected_face`. The outline helper copies the footprint's outer wires and
lifts them to Z = 0.01 mm for display. The face remains at Z = 0. Despite its
singular name, `protected_face` is a list of supplied protection shapes, not a
union or the new board face. Registration and section-number placement use
that collection to avoid protected track and platform regions.
[Outline helper][outline]; [returned data][multi-builder]; [protection consumer][protection-use]

### Engraving objects do not cut the solid

Engraving prepares separate polygonal wires at `ENGRAVING_LIFT = 0.04` mm.
In this exact excerpt from `run_macro`, `straight_production_results` already
contains each prepared straight route:

```python
if formation_config["enabled"] and formation_config["create_track_engraving"]:
    engraving_alignments = list(all_alignments)
    for bundle in straight_production_results:
        engraving_alignments.extend(bundle["alignments"])
    track_engraving_shape = create_track_engraving_shape(
        engraving_alignments
    )
```

The track engraving builder lifts each supplied centreline. The platform
engraving builder lifts both longitudinal platform edges and combines them;
it does not add the closing caps. Neither builder clips these lines to the
formation outline or cuts grooves into the board. Their purpose is separate,
selectable engraving geometry, as the GUI tooltips state.
[Engraving caller][engraving-caller]; [wire builders][engraving-builders];
[display lifts][output-constants]

## Follow document identity, visibility and saved settings

The unsplit curve board and its engraving use the following base object names.
The generated-set naming helper can append a set suffix or choose a unique
name, so the full internal name is not invariant. Roles and export metadata
identify the derived representations. [Object creation][document-objects];
[set naming][set-naming]

| Base object name | Role | Meaning |
| --- | --- | --- |
| `RailwayFormationBoardPerimeter` | `FormationOutline` | Separate perimeter cutting profile. |
| `RailwayFormationBoard` | `FormationBody` | Downward-extruded board solid. |
| `RailwayTrackCentrelineEngraving` | `EngravingGeometry` | Combined track-centreline lines. |
| `RailwayPlatformEdgeEngraving` | `EngravingGeometry` | Combined platform-edge lines. |

The creation blocks apply `show_outline` and `show_solid` to unsplit curve and
straight boards. They do not apply those settings in the formation-section
creation blocks. Engraving has no corresponding Show control or explicit
visibility assignment in its creation block. Sectioning's `preserve_unsplit`
choice also determines whether an unsplit board exists. These controls must
therefore not be described as universal visibility switches for every board
section or engraving object. [Unsplit selection][unsplit]; [curve objects][document-objects];
[straight objects][straight-objects]; [section objects][section-objects]

When opening the dialogue, remembered inputs take precedence over generated
document settings. Otherwise `read_formation_config` reads
`FormationConfigurationJSON` and normalises it, falling back to defaults for
missing or malformed data. Accepted dialogue inputs are remembered before
geometry validation and replacement confirmation. A failed attempt or declined
replacement can therefore supply the values on the next opening.
[Configuration reader][config-reader]; [input precedence][load-state];
[remembered inputs](generate-template-set.md#what-values-collects-and-what-is-remembered)

Successful generation writes `FormationConfigurationJSON` and a
`FormationSummary` containing output type, margin, minimum width, thickness and
plan area when board geometry exists. Generated settings preserve the inputs;
editing a derived perimeter is not a parameter-edit route back into this
calculation. The shared generation chapter explains replacement identities,
transactions and Undo. [Settings writer][settings];
[generation and replacement](generate-template-set.md)

## Understand rejection and the later production boundary

The board is prepared before generated-set replacement begins. Useful failure
conditions include:

| Condition | Where it stops |
| --- | --- |
| Neither selected printable strips nor an enabled platform footprint | The multi-builder rejects the empty input selection. |
| Missing or incomplete reference points/headings | Station preparation or the sweep's reference checks reject the input. The first diagnostic depends on which check fails first. |
| An incomplete selected strip or platform edge | Edge construction or ordered path mapping cannot supply a usable path. |
| No usable occupied reference samples | Active-range or missing-limit checks reject the envelope. |
| Too few distinct boundary points, an open boundary or an invalid face | Plan-face construction rejects the cutting footprint. |
| A null extrusion or no perimeter wire | Native body or outline preparation fails, including for an outline-only request. |

These conditions come from the [selection checks][multi-builder],
[station calculation][station-core], [edge mapping][edge-samples],
[active range][active-range], [face builder][plan-face] and [outline helper][outline].
They are distinct from errors after the document transaction starts. A later
document-stage exception attempts to abort that transaction; export follows
the document commit and has its own result. Export failure does not imply
that the generated board was rolled back. [Transaction and export ordering][transaction]

Shared sectioning can partition the face and body, while registration,
numbering and matching holes consume or modify the prepared geometry. Those
algorithms remain separate work in [issue #15][section-issue] and
[issue #16][assembly-issue]. This chapter explains their formation inputs,
including the protection collection, without treating every later result as
the unmodified base sweep.

Generated objects carry export metadata, but the normal B16 Core export route
currently rejects a configuration with formation enabled. Its dependency
inventory also excludes other optional features. Board creation and metadata
therefore do not establish that a board is admitted to that export route.
The dedicated export explanation is tracked in [issue #33][export-issue].
[Current Core export scope][export-scope]

## Evidence and reproduction limits

All Python blocks above are source excerpts. They need the enclosing functions,
configuration and host context named beside them; they are not standalone
FreeCAD examples. The optional documentation tool checks the independent
cross-section and continuous-profile arithmetic and its saved numerical record.
[Development environment](../development.md#regenerate-the-alignment-figures)
gives the regeneration commands.

The station-mapping contract records formation callers of the migrated helpers.
However, its retained GUI procedure explicitly disables formation, assembly
and export. It cannot establish a board or engraving result. The capability
inventory records that no dedicated accepted formation-board migration fixture
was found in that inventory. [Station contract][station-contract];
[retained GUI scope][station-evidence]; [capability inventory][capability]

No new workbench, FreeCAD GUI, native-board, engraving or manufacturing check
was executed for this chapter. The figures explain nominal relationships;
they do not reproduce the local projection, index-based gap interpolation or
finite station array of a native run. Sampled limits and successful face
construction also do not prove continuous clearance, arbitrary route topology,
physical support or fabrication suitability. Keep each claim with its stated
source and representation.

[revision]: https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf
[controls]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4212-L4259
[broadening-call]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10391-L10416
[bindings]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L1168-L1178
[curve-caller]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41221-L41238
[straight-caller]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11454-L11533
[control-state]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L6004-L6021
[field-values]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L6216-L6232
[defaults]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L922-L962
[length-editor]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4771-L4779
[old-builder]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L9971-L10035
[multi-builder]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10461-L10521
[platform-preparation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41119-L41151
[track-protection]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41158-L41164
[engraving-caller]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41284-L41300
[sweep-start]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10297-L10327
[station-core]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L1992-L2055
[left-normal]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L6981-L6982
[source-edges]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10338-L10371
[projection]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10044-L10153
[edge-samples]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10156-L10184
[accumulation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10187-L10226
[fill-samples]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10229-L10253
[active-range]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10373-L10389
[broadening-helper]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10256-L10294
[minimum-width]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10417-L10428
[end-construction]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10430-L10459
[curve-caps]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11782-L11796
[plan-face]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L9705-L9732
[outline]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L9950-L9959
[protection-use]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41455-L41493
[engraving-builders]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11041-L11066
[output-constants]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L496-L508
[document-objects]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L42260-L42323
[set-naming]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41650-L41663
[unsplit]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41505-L41522
[straight-objects]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41826-L41873
[section-objects]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L42434-L42476
[config-reader]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L6490-L6499
[load-state]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40801-L40849
[settings]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L21731-L21961
[transaction]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L42666-L42715
[section-issue]: https://github.com/Richard-Gnitnub/tracktemplate-docs/issues/15
[assembly-issue]: https://github.com/Richard-Gnitnub/tracktemplate-docs/issues/16
[export-issue]: https://github.com/Richard-Gnitnub/tracktemplate-docs/issues/33
[export-scope]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/core_dependency_inventory.py#L164-L170
[station-contract]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/contracts/phase7-station-mapping.md
[station-evidence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-09-12-phase7-station-mapping-regression.md#L111-L122
[capability]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/CAPABILITY_MATRIX.md#L55
