<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted source excerpts and new explanation, 2026-10-24.
-->

# How physical platforms follow tracks and form bodies

The **Platforms** manager places a railway platform beside one track or
between two tracks. It starts with the track centrelines, locates a length
along one reference track, calculates the two platform edges, and builds the
requested wires, face or solid. Its clearance fields measure from a track
centreline to a platform edge. They do not measure from a rail face.
[Controls and their recorded purpose][controls]

This feature uses the alignments already calculated by the main dialogue.
The separate **Platform widening** alignment mode changes a track's transition
geometry and spacing. It does not create a physical platform. Read
[curves and spacing](curves-and-spacing.md) for that calculation. The distinction
also applies to code: `build_platform_core` builds a track transition, whereas
`calculate_platform_boundaries` builds the physical platform's plan geometry.
[Track-transition contract][widening-contract]; [physical boundary calculation][boundaries]

**Source:** workbench revision
[`7965bfc4671668f889c1f43fb8336c5146c3f5cf`][revision]. This chapter follows
the B16 composition of the retained B15 dialogue and generation workflow.
The controls, projection, plan taper and native shape builders remain in that
host. B16 substitutes selected Core calculations for station mapping, heading
coverage, input validation, longitudinal bounds and top heights. It has not
moved the complete physical-platform operation into Core.
[Selected functions and caller dependencies][selection]; [runtime binding][binding]

## Edit a platform definition

Selecting a manager row loads **Selected platform settings**. Changing a
widget updates that row's in-memory configuration and table summary.
**Generate** later reads the definitions and builds geometry. These editor
changes do not themselves replace objects in the FreeCAD document.
[Editor read, save and load][editor]; [selection callbacks][manager]

| Manager action | What changes |
| --- | --- |
| **Add platform** | Save the current editor, append enabled defaults with a unique name, and select the new row. |
| **Duplicate selected** | Copy the selected definition and its enabled state, allocate a new `manager_id`, derive a proposed name from the original plus ` Copy`, and insert it after the original. The helper may add a numbered suffix. Truncation to 80 characters can still leave a duplicate name; rename it before generating both enabled definitions. |
| **Remove selected** | Remove the row and load the next valid selection. Removing the only row replaces it with a fresh, disabled default row. |
| **Move up** / **Move down** | Save the editor and swap complete definitions. The moved row keeps its manager identity. |

At least one row remains, and at most twenty rows are allowed. The initial
and reset definition is disabled; Add explicitly enables its new definition.
Unticking **Enable platform output:** retains an editable definition for
later use. [Defaults][defaults]; [manager operations and limits][manager]

### Interpret the fields in the selected arrangement

All length fields use millimetres and display three decimal places. Internal
headings use radians. The code calls the first host **Track A** and the second
**Track B**. In **Between two tracks**, the current GUI labels them **Up-side
track:** and **Down-side track:**. Those are observed UI labels; the selection
does not infer a railway's Up or Down running direction. In **Outside one
track**, A becomes **Adjacent track:** and B becomes disabled **Second track
(not used):**. [Fields][controls]; [dynamic labels and enablement][control-state]

| Field | Meaning and interaction |
| --- | --- |
| **Platform name:** | Identifies the definition and contributes to generated labels and export filenames. The editor trims whitespace, limits it to 80 characters, and supplies a name when empty. Generate requires unique names among enabled definitions. |
| **Up-side edge clearance:** / **Track edge clearance:** | Perpendicular distance from A's centreline to the adjacent platform edge. Default 25 mm. |
| **Down-side edge clearance:** | Corresponding distance from B's centreline. Default 25 mm; used only between tracks. |
| **Outside side:** | **Left of travel** or **Right of travel**, relative to A's direction. This is independent of whether the track is the inside or outside track of a curve. |
| **Outside platform width:** | Full width measured away from the adjacent edge. Default 100 mm; disabled between tracks because the two host clearances determine that width. |
| **Platform coverage:** | Selects the available part of the hosts: constant curve, either transition with the curve, or both transitions with the curve. It bounds where the requested length can fit. |
| **Platform length:** / **Centre offset:** | Length on A and displacement from the middle of its selected coverage. Defaults 500 mm and 0 mm. Positive offset moves towards increasing A station. |
| **Match entry and exit ends:** | Copies the entry style and length to the exit and disables independent exit editing. Defaults to matched, tapered ends of 100 mm each. |
| **Entry end style:** / **Exit end style:** | **Square** preserves full width. **Tapered ramp to trackbed** narrows the plan and, for a solid, also lowers its top towards the end. End lengths govern both effects. |
| **Required track clearance:** / **Check clearance envelope:** | Default 20 mm and checked. Applies the selected-host clearance rule and the additional plan-envelope checks described below. |
| **Create edge objects:** / **Show edge objects:** | Separates whether edge objects exist from their initial visibility. Show is editable only when Create is checked. Both default to checked. |
| **Platform body output:** | **Edges only (2D)**, **2D platform face**, or **3D platform solid**. A new definition defaults to a solid. |
| **Platform height:** / **Show platform body:** | Default height 15 mm and visible body. Height is editable only for a solid; Show is editable for a face or solid. |

The values in this table are software defaults, not recommended dimensions
for a particular model railway. Widget limits also do not establish a valid
platform: for example, the editor accepts an end length of zero, but a
tapered end requires a positive length at validation. [Widget ranges][controls];
[input validation][input-validation]

The required-clearance field remains editable when its check is off. The
checkbox controls use of the value, rather than erasing it or locking the
field. [Control state][control-state]

Changing **Arrangement:** to **Outside one track** reapplies an outside
preset: width 100 mm, both transitions and constant curve, matched tapered
100 mm ends, solid output and visible body. It does not reset every field.
`_platform_loading` prevents that preset from replacing values when an
existing definition is loaded into the editor. Set the arrangement before
entering different end or coverage values. [Arrangement-change handler][outside-preset]

### Host names are choices backed by list positions

The selector contains **Main Track** followed by the added-track rows. It
does not include **Straight Track Manager** routes. The stored fields
`track_a_index` and `track_b_index` are zero-based positions in that curve
family, not persistent track IDs. [Host choices][host-choices]

This exact excerpt from `CurveInputDialog._set_platform_track_choices` runs
after the current labels have been collected. `combo` is one host selector:

```python
combo.blockSignals(True)
combo.clear()
combo.addItems(labels)
combo.setCurrentIndex(min(max(0, int(selected)), len(labels) - 1))
combo.blockSignals(False)
```

The clamp chooses the last available item when a stored index is too large.
Refreshing or loading the selected row can then save that new index. An
untouched row can still display **Missing track** and fail validation. Thus
removing a track can change a platform's effective host, or leave an invalid
reference; it is not a stable-identity remapping operation. Two clamped choices
can also become the same track, which is invalid between tracks.
[Refresh and clamping][host-choices]; [editor and table][editor]

## Map coverage to Track A's stations

A station is a distance along a particular centreline in its travel direction.
`alignment_station_data` puts station zero at the first supplied point and
adds each successive XY chord length. Common straight extensions therefore
affect absolute stations. The `core_start` and `core_end` bounds identify the
curve core within that supplied alignment. These sampled distances can differ
slightly from a nominal circular arc length. [Station contract][station-contract]

Coverage is first expressed as a shared **heading interval**, not a shared
chainage interval. For each selected host, the code reads its entry-transition
angle, exit-transition angle and total turn progress. Multiplying heading by
`turn_sign` makes progress nonnegative for either turn direction. The latest
entry-transition end and earliest exit-transition start bound the constant
curve that the hosts share. [Coverage implementation][coverage]

| **Platform coverage:** | Heading interval returned |
| --- | --- |
| **Constant curve only** | Latest entry end to earliest exit start. |
| **Entry transition and constant curve** | Zero progress to earliest exit start. |
| **Constant curve and exit transition** | Latest entry end to the smallest host total progress. |
| **Both transitions and constant curve** | Zero progress to the smallest host total progress. |

The first three modes reject an unusable shared constant-curve interval.
The full-core mode can proceed without that interval. The heading-to-station
search uses A's core bounds and the retained monotone turn progression; it
is not a general station locator for arbitrary looping or straight routes.
The physical-platform caller also rejects a selected length with no positive
turn progression. [Coverage and 64-step heading search][coverage];
[boundary preparation][coverage-caller]

In this exact excerpt from `calculate_platform_boundaries`, the shared
heading bounds and A's station data have already been calculated:

```python
base_start_a = station_for_progress_heading(data_a, start_progress, turn_sign)
base_finish_a = station_for_progress_heading(data_a, finish_progress, turn_sign)
longitudinal = resolve_platform_longitudinal_bounds(
    config,
    base_start_a,
    base_finish_a,
)
```

Only A supplies these station bounds. B need not have the same station at
either end. The separate Core calculation then locates the requested centre.
This exact excerpt from `resolve_platform_longitudinal_bounds` follows checks
that the available and requested lengths are positive:

```python
midpoint = 0.5 * (base_start + base_finish)
centre_offset = float(config["centre_offset"])
centre_station = midpoint + centre_offset
```

For available length `A`, requested length `L` and offset `o`, the intended
start and finish insets are `(A - L) / 2 + o` and `(A - L) / 2 - o`.
Both must remain nonnegative. Equivalently, the maximum length at this centre
is twice the shorter distance from the centre to a coverage end. The code
rejects a request that does not fit; it does not silently shorten it. Its
`1.0e-8` mm geometry tolerance permits only tiny boundary residuals.
[Longitudinal calculation and diagnostics][longitudinal]

The returned dictionary records start, finish and centre stations, actual
centre offset and length, available length, and both insets. Generate stores
the resolved length, offset and insets back into the normalised configuration.
The inset fields also remain in stored JSON for older-file compatibility.
[Result][longitudinal]; [generation caller][platform-generation]; [stored defaults][defaults]

## Calculate the full-width cross-sections

The host divides the requested A length into steps no larger than 3 mm. It
also inserts taper breakpoints, so a change between tapered and full-width
geometry is represented explicitly. Interpolation supplies A's point and
heading at each station. The left normal is perpendicular to that heading;
an offset along it is perpendicular to the centreline's travel direction.
[Sampling and important stations][coverage-caller]; [station contract][station-contract]

### Beside one track

For A point `P`, left unit normal `N`, clearance `c`, width `w`, and side
sign `q` (`+1` for left, `-1` for right), the untapered edges are:

```text
edge A = P + q × c × N
edge B = P + q × (c + w) × N
```

These are explanatory equations, not callable Python. Both edges use A's
own normal. There is no second host or independently entered B clearance in
this arrangement. The retained calculation records the configured width as
`minimum_width` before applying end tapers. [Outside calculation][outside-edges]

### Between two independently eased tracks

Equal chainage on two tracks does not generally identify one cross-section.
Even for concentric circles, 150 mm along a 600 mm radius spans 0.25 radians;
the corresponding arc on a 655 mm radius is 163.75 mm. Different transition
lengths add another difference. This is why the implementation searches for
B at each normal cross-section of A. [Projection implementation][projection]

First, `_project_centreline_to_reference_normal` finds B's centreline on
A's normal. The sign of its normal separation tells the code which side of
A contains B. The code places A's edge towards B, using A's clearance.
It then searches again for **B's offset edge** on that same cross-section.
The B edge uses B's own heading and clearance towards the reference point.
Its station can differ from both A's station and the earlier B-centreline
projection station. [Centreline and offset-edge projection][projection]

The common root search evaluates this exact nested function in
`_find_normal_projection_station`. `point_at_station` supplies either a B
centreline point or a B offset-edge point, and the tangent belongs to A:

```python
def projection_value(station):
    point = point_at_station(station)
    return dot_xy(
        point.x - reference_point.x,
        point.y - reference_point.y,
        tangent_x,
        tangent_y,
    )
```

A zero tangent dot product puts the point on the normal through the reference.
The search prefers a solution near the previous station to maintain continuity,
then searches more widely when necessary. It does not prove that an arbitrary
looping alignment has one unique intersection. [Projection root search][projection]

This exact excerpt from `calculate_platform_boundaries` measures the
projected edge-to-edge separation. `side_sign`, the edge difference, and
A's normal have already been calculated:

```python
available_width = side_sign * dot_xy(
    edge_difference_x,
    edge_difference_y,
    normal_x,
    normal_y,
)
```

The next checks reject nonpositive width and more than 0.01 mm of separation
along A's tangent. The latter is a cross-section alignment check. The code
also rejects tracks that meet, cross or change sides, and a projected B edge
that reverses station order beyond its small permitted residual.
`minimum_width` records the smallest full width at the sampled sections.
It is not a continuous minimum certified between all samples.
[Width and ordering checks][between-edges]; [projection tolerance][projection-constant]

**Design inference:** using A as the longitudinal reference gives the user
one length and position to edit, while the projection accommodates a second
track with different easing. This explains the behaviour seen in the code;
it is not a separate recorded design decision.

## Apply plan tapers and solid ramp heights

The initial boundaries define the full-width platform. End treatment then
modifies that geometry. **Square** leaves an end full width. A tapered entry
increases its width fraction with distance from the start; a tapered exit
reduces it towards the finish. Their lengths must be positive, each must fit
the platform, and their sum must not exceed its length.
[End-length validation and taper factor][tapers]

The taper fraction has a small lower bound derived from
`PLATFORM_MIN_NOSE_WIDTH = 0.10` mm. This preserves a nonzero nose for an
otherwise wider platform. It does not widen a platform already narrower
than 0.10 mm: the effective lower width is the smaller of the existing width
and 0.10 mm. [Constants][constants]; [taper factor][tapers]

For a between-track platform, the taper moves both edges towards their
cross-section midpoint. For an outside platform, it keeps the track-facing
edge fixed and moves the far edge towards it. This exact excerpt is the
outside branch of `apply_platform_plan_tapers`; `vector_x`, `vector_y` are
the full edge-to-edge vector and `factor` is the calculated width fraction:

```python
new_a = vector_xy(point_a.x, point_a.y)
new_b = vector_xy(
    point_a.x + (vector_x * factor),
    point_a.y + (vector_y * factor),
)
```

The function returns the two modified edge lists and their minimum sampled
separation as `minimum_tapered_width`. That is separate from the earlier
full-width `minimum_width`. [Plan-taper implementation][tapers]

Matching ends copies the entry style and length to the exit in both the
editor and `clone_platform_config`. Normalisation derives the stored
`vertical_end_ramps`, `entry_ramp_length` and `exit_ramp_length` from those
styles when the body is solid. They are compatibility fields, not three
additional independent GUI controls. [Control state][control-state];
[normalisation and compatibility fields][normalisation]
Equal configured end styles and lengths do not guarantee mirror-image shapes
on hosts whose width or curvature changes between the two ends.

For a solid, `calculate_platform_top_heights` raises a tapered entry from
the 1.0 mm template surface to the configured full height. This exact
excerpt is inside its loop over relative A stations; `trackbed_height`,
`full_height`, and the applicable entry length are already set:

```python
if entry_length > GEOMETRY_TOLERANCE and station < entry_length:
    fraction = min(max(station / entry_length, 0.0), 1.0)
    height = min(
        height,
        trackbed_height + ((full_height - trackbed_height) * fraction),
    )
```

The exit uses distance remaining to the finish in the same way. Height means
top Z above the XY base plane; it is not an extra height above the trackbed.
The solid's bottom stays at Z = 0. A tapered solid must have full height
greater than the template surface plus the geometry tolerance. Face and
edge-only output retain the plan taper without creating a sloping solid.
[Height calculation][heights]; [input checks][input-validation]; [solid construction][native]

## Work through a 150 mm outside platform

Use the previous chapter's left-turn example: main radius 600 mm, matched
Outside track radius 655 mm, and total turn 90°. The Outside track's retained
solved transition length is 559.4102547270278 mm at each end. Choose that
outer track as A and **Right of travel**. This puts the platform beyond the
outermost track. Choosing the main track with the same side would put the
platform in the gap towards the neighbouring track and can fail the later
envelope check. [Curve example](curves-and-spacing.md#a-two-track-comparison);
[relationship checks][relationships]

After selecting **Outside one track**, set these illustrative inputs:

| Input | Value |
| --- | --- |
| **Adjacent track:** / **Outside side:** | Outside track / **Right of travel** |
| **Platform coverage:** / **Centre offset:** | **Constant curve only** / 0 mm |
| **Platform length:** | 150 mm |
| **Track edge clearance:** / **Outside platform width:** | 20 mm / 30 mm |
| **Platform body output:** / **Platform height:** | **3D platform solid** / 12 mm |
| **Match entry and exit ends:** | Checked |
| **Entry end style:** / **Entry end length:** | **Tapered ramp to trackbed** / 30 mm |
| **Required track clearance:** / **Check clearance envelope:** | 20 mm / checked |

These values explain the algorithm. They are not physical-clearance or
manufacturing recommendations. The arithmetic and figures below are
independent documentation calculations; the platform has not been generated
in a new FreeCAD session for this chapter.

For the smooth nominal Outside circle, the constant-curve length is
`655 × (π/2 − 559.4102547270278/655) = 469.461339324` mm.
A centred nominal 150 mm interval leaves about 159.731 mm at each end.
The workbench instead maps the coverage headings to its sampled A stations
before centring the length. Do not copy the nominal inset into a claim about
the exact host result. [Curve numerical record](../_static/figures/alignment-example-values.json);
[platform numerical record](../_static/figures/platform-example-values.json)

```{figure} ../_static/figures/platform-plan-example.svg
:alt: Smooth plan illustration of the outer track, fixed adjacent platform edge, tapered far edge and neighbouring main track.

Independent smooth-circle illustration. The origin is A's midpoint;
positive X follows its tangent and positive Y points right of travel there.
The workbench uses sampled point and heading data instead.
```

At a full-width cross-section, the near and far offsets from A are 20 and
50 mm. In the ideal circular illustration, these correspond to radii 675
and 705 mm. At relative station 15 mm, the entry fraction is `15/30 = 0.5`:
the width becomes 15 mm, the far offset becomes 35 mm, and the top becomes
`1 + (12 − 1) × 0.5 = 6.5` mm. At station zero the plan nose is 0.10 mm
wide and its top is at 1.0 mm. [Taper equations][tapers]; [height equations][heights]

| Relative A station, mm | Near offset, mm | Tapered width, mm | Far offset, mm | Top Z, mm |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 20 | 0.10 | 20.10 | 1.0 |
| 3 | 20 | 3 | 23 | 2.1 |
| 15 | 20 | 15 | 35 | 6.5 |
| 30 | 20 | 30 | 50 | 12.0 |
| 75 | 20 | 30 | 50 | 12.0 |
| 120 | 20 | 30 | 50 | 12.0 |
| 135 | 20 | 15 | 35 | 6.5 |
| 147 | 20 | 3 | 23 | 2.1 |
| 150 | 20 | 0.10 | 20.10 | 1.0 |

Here relative station zero is the platform start on A, and 150 mm is its
finish. These width and height relations apply at those stations independently
of the absolute station of the platform. The two ends occupy 60 mm in total,
leaving 90 mm at full width and height. Plan width and top height are separate
quantities: the small nose-width floor does not raise the ramp endpoint.

```{figure} ../_static/figures/platform-profiles-example.svg
:alt: Two plots show platform width and top height against relative Track A station, with taper endpoints at 30 and 120 millimetres.

Independent end-profile arithmetic for the same 150 mm example. Both
profiles use A's relative station; the vertical plot shows top Z, not thickness
above the trackbed.
```

### Compare the space between the tracks

Now consider a separate between-track definition with main track A and
Outside track B. The ideal constant-curve centreline gap is 55 mm. Before
tapering, subtract the two edge clearances:

| Clearance at each track, mm | Combined clearance, mm | Nominal full width, mm |
| ---: | ---: | ---: |
| 20 | 40 | 15 |
| 26 | 52 | 3 |
| 27 | 54 | 1 |
| 28 | 56 | −1 — no positive width |

Increasing clearance consumes platform width. The last row has no valid
full-width platform to taper. For the first three rows, actual sampled
widths still come from the two projection searches, so the nominal subtraction
does not replace runtime validation. In transitions, independently eased
tracks can have varying gap and different local headings; one constant gap
calculation is then insufficient. [Boundary checks][between-edges]

## Build native wires, faces and solids

`calculate_platform_boundaries` returns edge lists, their ordered plan
boundary, relative stations and top heights. It also returns the resolved
length and insets, full and tapered minimum widths, heading bounds, maximum
tangent mismatch, and host names and indices. `create_platform_shapes` uses
that geometry to create native `Part` shapes before document objects exist.
[Geometry result][geometry-result]; [native construction][native]

| Requested output | Native construction |
| --- | --- |
| Separate edges | A `Part.makePolygon` wire for each edge. For a solid, its Z follows the top profile plus the 0.02 mm display lift. For 2D output, edge Z is 1.07 mm. |
| **2D platform face** | Clean the ordered plan boundary, close its wire, and call `Part.Face` at Z = 1.05 mm. |
| Solid with square ends | Make a face at Z = 0 and extrude it by the configured height. |
| Solid with a tapered end | Build closed vertical cross-section wires from Z = 0 to the sampled top heights, then make a solid ruled loft through selected sections. |

The face builder rejects an open, null or invalid face, including a boundary
that the kernel considers self-intersecting. The loft builder rejects a null
or invalid result; both builders call `isValid()` when the host provides it.
Its profiles are selected about 9 mm apart, with the first,
last and taper-breakpoint sections retained; plan edges use the finer samples.
These are native shapes built from sampled geometry, not analytic circular
offset surfaces. [Boundary cleaning and face checks][face]; [loft profiles and checks][loft];
[constants][constants]

One low-height corner needs qualification: a square-ended solid can accept
a configured height below 1 mm, but the height helper floors its edge-profile
values at 1 mm while the extrusion uses the entered height. Source inspection
therefore indicates that its separate edge wires can sit above the body top.
This case was not executed here. [Height calculation][heights]; [native construction][native]

Generate also creates a plan face for **every** enabled platform, even when
body output is **Edges only (2D)**. That footprint supports relationship
checks and later production geometry. Separate output choices do not remove
the need for a valid plan boundary. [Generation caller][platform-generation]

## Check clearances and reject unsuitable geometry

With **Check clearance envelope:** checked, the selected-host input check
requires each edge clearance to be at least the larger of the configured
required clearance and half the host's template width when its strip output
is enabled. The exact excerpt below is from `validate_platform_inputs`,
inside its loop over selected hosts:

```python
minimum = max(required, template_half_width)
if clearance + 1.0e-9 < minimum:
```

For an enabled 32 mm track strip and required clearance 20 mm, the minimum
is `max(16, 20) = 20` mm. Disabling strip output removes the half-width term
but retains the required clearance. These checks concern model geometry and
configured envelopes; they do not prove a vehicle's swept clearance.
[Input checks and exact diagnostics][input-validation]

`validate_platform_relationships` compares each plan face with envelopes of
the other curve-family tracks when the checkbox is enabled and required
clearance is positive. It rejects intersection area above `1e-5` square
millimetres. It also checks overlap between enabled platforms with the same
area threshold, regardless of that checkbox. Straight Track Manager routes
are outside the `all_alignments` list passed to this operation.
[Relationship checks][relationships]; [caller and alignment scope][platform-generation]

| Failure | Where and why it stops |
| --- | --- |
| Missing A or B, or identical hosts between tracks | Input validation cannot form the selected relationship. |
| Nonpositive length, clearance, outside width or solid height | Input validation rejects the required dimension; a tapered solid also needs height above the 1 mm template surface. |
| No shared constant interval, centre outside coverage, or length too long at that centre | Coverage or longitudinal validation cannot place the requested platform. |
| End lengths exceed the platform, individually or together | The end-profile check rejects the requested taper configuration. |
| Tracks meet, change sides, cannot be projected, or B's projected edge reverses | Cross-section construction cannot preserve the required between-track relationship. |
| Nonpositive full width or tangent mismatch above 0.01 mm | The two projected edges do not form an acceptable cross-section. |
| Invalid face or loft, clearance-envelope intrusion, or platform overlap | Native construction or relationship checks reject the resulting shape. |
| Edge creation off with **Edges only (2D)** | The definition would create no output. |

These checks occur before generated-set replacement. They are separate from
later kernel or document-operation errors. The
[generation chapter](generate-template-set.md) explains the transaction,
replacement and recovery boundary. [Preparation before transaction][preparation]

## Follow identity, visibility and saved state

Manager identity and generated numbering serve different purposes. The UUID
`manager_id` restores the selected row and survives reordering. Generate
instead numbers a platform by its one-based position in the complete list.
This exact excerpt is inside the retained `run_macro` generation loop:

```python
for platform_index, stored_config in enumerate(platform_configs):
    platform_config = clone_platform_config(stored_config)
    platform_configs[platform_index] = platform_config
    if not platform_config["enabled"]:
        continue
    platform_number = platform_index + 1
```

Disabled rows can leave gaps in platform numbers, and reordering can change
those numbers. Generated objects carry `PlatformNumber` and `PlatformName`
alongside set and role metadata; they do not use the manager UUID as their
platform output identity. [Selection identity][manager-identity];
[generation][platform-generation]; [platform metadata][metadata]

Edge objects have role `PlatformEdge`; an unsplit body has role `PlatformBody`;
section bodies have role `PlatformSection`. The creation blocks apply
`show_edges` to edge visibility and `show_body` to the unsplit body. The
section-body creation block does not apply `show_body`, so that checkbox
must not be described as a universal visibility rule for every section.
Shared sectioning and its preserve-unsplit setting also affect whether an
unsplit body is created. [Edges and unsplit bodies][objects]; [section bodies][section-objects]
[Unsplit-body selection][unsplit]

Accepted dialogue inputs are remembered before validation and replacement
confirmation, so a failed geometry attempt can still supply values when the
workflow reopens. The source records this as deliberate preservation of user
input. Remembered input takes precedence over generated-document settings.
Successful generation writes the ordered definitions to
`PlatformConfigurationsJSON`, mirrors the first in legacy
`PlatformConfigurationJSON`, and records counts and `PlatformSummary`.
[Remembered-input lifecycle](generate-template-set.md#what-values-collects-and-what-is-remembered);
[platform settings writer][settings]

Configuration import has a source-level caveat at this revision.
`apply_configuration_payload` installs the imported platform list, refreshes
host choices, then loads row zero. Refresh can save the previous editor
values into that new row before loading it. This is an inferred overwrite
risk from the call sequence, not a reproduced GUI defect; the chapter does
not claim that imported row-zero settings always arrive unchanged.
Configuration validation also checks duplicate names across all rows and
both host indices for enabled rows, whereas Generate checks duplicate names
among enabled rows and uses B only between tracks.
[Import sequence][import-sequence]; [refresh/save][host-choices];
[configuration checks][configuration-checks]; [Generate name checks][name-checks]

Platform preparation is followed by the shared document transaction. A
document-stage exception attempts to abort it. Production export follows
the document commit and has a separate failure outcome; an export failure
does not imply that the generated document was rolled back.
[Generation and replacement](generate-template-set.md); [commit and export ordering][commit-export]

## Use platform footprints in later operations

The current `create_formation_geometry_multi` path passes the selected platform
edge geometry to `_simple_formation_swept_face`. That calculation projects
both edges into the main alignment's reference, combines their lateral extents
with the selected track strips, adds margin, and broadens the board near
changes in width. The source records the reason: the board must support the
platform without following every taper point. Platform plan faces are also
retained as protected shapes. The older `create_platform_envelope_face`
helper is not the base footprint path used by this multi-platform caller.
[Current formation consumer][formation]; [swept edges and recorded rationale][formation-sweep]

Shared section masks use the main alignment, rather than each platform's
chosen A track. If platform sectioning is enabled and a body exists, the
caller intersects the body and its plan face with those masks. This applies
to a face or a solid; an edges-only definition has no body to section. The
partition check permits a platform to occupy only some of the shared sections.
The long edge wires are created separately and remain unsplit by this body
partition loop. [Shared masks][section-masks]; [section preparation][section-preparation]

This connects the platform definition to the board and its physical parts.
The [formation-board chapter](formation-board.md) follows the board-margin,
width and footprint calculation. The [sectioning chapter](sectioning.md)
explains shared cuts, partial platform coverage and the partition checks.
This chapter establishes the platform geometry that those operations consume.

## Evidence and reproduction limits

The chapter's code blocks are source excerpts, not standalone examples.
They require the containing functions and host or package context identified
beside them. The source trace covers the controls, final B16 substitutions,
retained projection and native builders, and the generation caller.

The workbench retains bounded regression evidence for station mapping,
heading coverage, platform input validation, longitudinal bounds and top
heights. Those comparisons concern the selected helpers and their caller
bindings. They do not prove every combination of platform projection,
native body generation, import, sectioning or export.
[Station evidence][station-evidence]; [coverage evidence][coverage-evidence];
[input evidence][input-evidence]; [bounds evidence][bounds-evidence]; [height evidence][height-evidence]

For example, the retained top-height GUI procedure uses outside-one-track,
constant-only solid output with 50 mm tapered ends and 15 mm height. It
records paired Create/Edit, Undo/Redo, rejection and Save/reopen comparisons.
Those are named historical results for that fixture, not a runtime result
for the 30 mm ends and 12 mm height taught here. [Retained procedure][height-evidence]

The optional figure generator and its numerical record preserve the
independent arithmetic used here. Regeneration instructions are in
[Development environment](../development.md#regenerate-the-alignment-figures).
It checks the table values and nominal relationships without importing or
executing the workbench. The figures are illustrations, not screenshots or
measurements from a qualified FreeCAD run. The exact host UI behaviour,
native shapes and noted import risk were not executed for this chapter.

[revision]: https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf
[controls]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L3958-L4207
[widening-contract]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/contracts/phase7-platform-core.md
[boundaries]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L9205-L9460
[selection]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L62-L137
[binding]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L1458-L1499
[editor]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L5310-L5492
[manager]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L5494-L5612
[defaults]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L878-L919
[control-state]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L5939-L6002
[input-validation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L1791-L1863
[outside-preset]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L5896-L5937
[host-choices]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L5280-L5308
[station-contract]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/contracts/phase7-station-mapping.md
[coverage]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L2058-L2137
[coverage-caller]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L9210-L9277
[longitudinal]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L1908-L1972
[platform-generation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41098-L41151
[outside-edges]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L9401-L9418
[projection]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L8776-L8983
[between-edges]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L9283-L9396
[projection-constant]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L596-L597
[tapers]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L9001-L9098
[constants]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L514-L531
[normalisation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L1293-L1403
[heights]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L1866-L1905
[native]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L9536-L9632
[relationships]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L8705-L8769
[geometry-result]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L9423-L9460
[face]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L9463-L9502
[loft]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L9515-L9575
[preparation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41642-L41663
[manager-identity]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L781-L800
[metadata]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11873-L11905
[objects]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L42181-L42258
[section-objects]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L42387-L42432
[unsplit]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41505-L41518
[settings]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L21706-L21907
[import-sequence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L5770-L5815
[configuration-checks]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L2854-L2888
[name-checks]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L8686-L8702
[commit-export]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L42666-L42715
[formation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10461-L10521
[formation-sweep]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10365-L10415
[section-masks]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41318-L41350
[section-preparation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41405-L41439
[station-evidence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-09-12-phase7-station-mapping-regression.md
[coverage-evidence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-09-26-phase7-platform-heading-coverage-regression.md
[input-evidence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-09-26-phase7-platform-input-validation-regression.md
[bounds-evidence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-09-26-phase7-platform-longitudinal-bounds-regression.md
[height-evidence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-09-27-phase7-platform-top-heights-regression.md
