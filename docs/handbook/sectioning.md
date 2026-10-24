<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted for the TrackTemplate developer handbook, 2026-10-24.
-->

# How shared section boundaries divide tracks, platforms and boards

The **Universal sectioning** controls divide a route into pieces while keeping
the selected track, platform and formation layers aligned at their joins.
The displayed design intent is explicit: measure the boundaries along the
main alignment and place each boundary perpendicular to its local direction
of travel. Balancing distributes the reference length evenly to avoid a very
short final piece. [Displayed controls and explanation][controls]

This chapter follows the plan into native cutting geometry, checks on the
resulting pieces and generated document objects. Read
[straight routes](straight-routes.md), [physical platforms](platforms.md) and
[formation boards](formation-board.md) for the source geometry. Here,
*section length* first means an interval along the reference alignment.
It is not a rectangular printer-bed dimension or a sheet-nesting result.

**Source:** workbench revision
[`7965bfc4671668f889c1f43fb8336c5146c3f5cf`][revision].
The controls, section planner, native masks and partition checks remain in
the retained B15 host. B16 binds selected Core station calculations through
adapters into that host. This is a retained workflow using modular helpers,
rather than a complete migrated sectioning API. [Station adapters][adapters];
[adapter construction][bindings]; [final installation][installation]

## Choose the layers and reference-length limits

The group contains nine controls. These are factory defaults; remembered or
saved values can replace them when the dialogue opens.

| Exact visible label | Configuration key | Meaning and default |
| --- | --- | --- |
| **Enable sectioning:** | `enabled` | Request sectioning. Defaults to off. |
| **Maximum section length:** | `maximum_section_length` | Upper reference-interval length. Default 0 mm keeps a complete object. |
| **Balance section lengths:** | `balance_lengths` | Divide the reference length evenly. Defaults to on. |
| **Minimum permitted length:** | `minimum_section_length` | Reject a calculated arrangement with an undersized interval. Default 100 mm. |
| **Section track templates:** | `section_track_templates` | Divide printable strip solids using the shared masks. Defaults to on. |
| **Section platform body:** | `section_platform` | Divide available 2D platform faces or 3D bodies, with their plan faces. Defaults to on. |
| **Section formation board:** | `section_formation` | Divide the board face before deriving its section outlines and solids. Defaults to on. |
| **Preserve unsplit objects:** | `preserve_unsplit` | Also retain complete output for a layer being divided. Defaults to on. |
| **Number in travel order:** | `number_in_travel_order` | Request separate number-engraving geometry. Defaults to on; section labels and metadata still have ordinal numbers when it is off. |

Both length editors accept **0–100,000 mm**, in 10 mm steps, with three decimal
places and the ` mm` suffix. These are the displayed widget limits.
Configuration import has its own specification; `clone_section_config`
normalises the two lengths to at least zero. Do not infer every configuration
constraint from the editor alone. [Controls][controls]; [length editor][length-editor];
[defaults and cloning][defaults]; [import specification][import-spec]

The enabling checkbox and maximum field remain available. The other seven
controls are enabled when **Enable sectioning:** is on and the maximum is
greater than zero. The platform and formation selections are not automatically
cleared when their source output is absent. Registration controls additionally
depend on formation sectioning; track assembly controls depend on track
sectioning. Those dependencies enable editors; the later plan and geometry
checks decide whether sectioning can proceed. [Control enablement][control-state]

Confirming the main dialogue with its standard **OK** button collects these
values through `_section_values()` and `values()`. Changing a field alone does
not cut existing document objects. The
[generation chapter](generate-template-set.md) explains the shared operation.
[Button box][dialogue]; [field reader][field-values]; [accepted dialogue][accepted]

### Check the selected source layers

The curve workflow prepares track, platform and formation geometry, then calls
`calculate_section_plan(main_alignment["total_length"], section_config)`.
Only when that calculated plan is active does it require at least one selected
layer. A selected platform layer needs an enabled 2D face or 3D body; edge-only
platform output is insufficient. A selected formation layer needs formation
output. These are generation-time checks, even though the corresponding
checkboxes can be enabled in the dialogue. [Plan and prerequisites][prerequisites]

This matters with the defaults: all three layer boxes begin selected.
Enabling a short maximum with no platform or formation output can therefore
produce a missing-layer error. Select the layers whose geometry is intended
to be divided. If the reference is already short enough for one complete
piece, the planner returns inactive and these active-plan prerequisites are
not applied. [Prerequisites][prerequisites]

## Calculate the reference intervals

For the curve family, the reference is the main alignment. Its length is the
sum of XY distances between sampled points after the alignment is prepared
and mirrored. Station zero is its first supplied point, with stations
increasing in travel order. It is not automatically the start of the curved
core, and sampled chord length is not ideal circular arc length.
[Main-length preparation][main-length]; [station calculation][station-core]

`calculate_section_plan` receives that total length and the section settings.
It first rejects a total at or below `GEOMETRY_TOLERANCE = 1.0e-8` mm.
This exact source excerpt then decides whether an actual split is necessary:

```python
maximum = float(config["maximum_section_length"])
enabled = bool(config["enabled"] and maximum > GEOMETRY_TOLERANCE)
if not enabled or maximum >= total_length - GEOMETRY_TOLERANCE:
    return {"enabled": False, "boundaries": [0.0, total_length], "ranges": [(0.0, total_length)]}
```

Here `total_length` and `config` are inputs to the enclosing function.
The returned `enabled` describes the **calculated plan**, not just the
checkbox. A disabled checkbox, effectively zero maximum, or maximum at least
the total within the stated tolerance produces one range. The function returns
before reading or checking minimum length in that branch. [Planner][plan];
[geometry tolerance][geometry-tolerance]

For an active split, the function rejects a minimum greater than the maximum
by more than `1.0e-8` mm. It calculates
`count = ceil(total_length / maximum)` and rejects a count above **999**.
The count supplies the balanced division and is an early limit for either
mode. [Planner][plan]; [section constants][section-constants]

### Balance every interval, or adjust only the last pair

This exact excerpt implements the balanced branch after `count` and `minimum`
have been read:

```python
if config["balance_lengths"]:
    length = total_length / float(count)
    if count > 1 and length + GEOMETRY_TOLERANCE < minimum:
        raise ValueError(
            "Balanced section length {:.3f} mm is below the minimum permitted "
            "length of {:.3f} mm.".format(length, minimum)
        )
    boundaries = [total_length * index / float(count) for index in range(count + 1)]
```

The endpoints are proportional positions along the full reference. With
1,200 mm total and a 500 mm maximum, `ceil(1200 / 500) = 3`, so each interval
is 400 mm. A minimum of 250 mm is satisfied. The boundaries are
`[0, 400, 800, 1200]` mm. [Balanced calculation][plan]

With balancing off, the planner first appends maximum-length intervals and
then the remaining endpoint. The same inputs initially give
`[500, 500, 200]` mm. The final 200 mm interval is below 250 mm, so the
following exact excerpt considers the last two intervals together:

```python
if len(boundaries) > 2:
    final_length = boundaries[-1] - boundaries[-2]
    if final_length + GEOMETRY_TOLERANCE < minimum:
        combined = boundaries[-1] - boundaries[-3]
        replacement = 0.5 * combined
        if replacement + GEOMETRY_TOLERANCE < minimum or replacement > maximum + GEOMETRY_TOLERANCE:
            raise ValueError(
                "The final unbalanced section would be {:.3f} mm and cannot "
                "be redistributed within the entered limits.".format(final_length)
            )
        boundaries[-2] = boundaries[-3] + replacement
```

The final two initial intervals total 700 mm. Replacing them with 350 mm each
moves the penultimate boundary from 1,000 to 850 mm. The earlier 500 mm piece
stays unchanged. The final boundaries are `[0, 500, 850, 1200]` mm.
[Unbalanced redistribution][plan]

This is a local adjustment of the last pair. It does not search for every
feasible arrangement. With the same total and maximum but a **400 mm minimum**,
balanced `[400, 400, 400]` satisfies the limits; the unbalanced branch rejects
its proposed `[500, 350, 350]` result. Choosing another mode can therefore
matter even when the nominal section count is unchanged.

`ranges` pairs consecutive boundaries. The final check compares the minimum
with the `1.0e-8` mm geometry tolerance and the maximum with **`1.0e-6` mm**.
The unbalanced stepping loop also uses a tolerance, so its final interval count
need not equal the raw ceiling at a floating-point boundary. These numerical
details belong to the implementation; they are not cutting or manufacturing
tolerances. [Final range checks][plan]

```{figure} ../_static/figures/section-lengths-example.svg
:alt: Three rows compare 400 millimetre balanced pieces, the initial 500, 500 and 200 millimetre unbalanced arrangement, and the final 500, 350 and 350 millimetre result.

Independent arithmetic for a 1,200 mm reference, 500 mm maximum and 250 mm minimum. The unbalanced correction redistributes only the last pair.
```

The optional documentation tool checks these values and the nominal example
below without importing the workbench.
[Independent numerical record](../_static/figures/section-example-values.json)

## Turn reference boundaries into shared cutting geometry

A boundary station gives a point and a heading on the reference. The heading
defines travel; the perpendicular line through that point defines the join
across the layers. B16's station adapter returns a native `App.Vector` and
heading to the retained mask builder. The selected calculation interpolates
between sampled XY points and headings; it does not replace the heading with
the direction of the straight chord. [Station calculation][station-core];
[adapter result][adapters]

The active `create_section_masks` routine uses spatial clipping regions.
An earlier helper named `create_section_mask_face` constructs a sampled swept
strip, but the active routine does not call it. Following the similarly named
helper would therefore explain the wrong cutting path. [Active masks][masks];
[earlier helper][earlier-mask]

### Build perpendicular limits, then a face and prism

The builder obtains bounding boxes from the supplied source shapes. With no
usable source it rejects the operation. It makes an overall XY face around
those boxes, padded by **100 mm** on every side. A separate reach is
`max(100, 4 × hypot(span_x, span_y) + 100)` mm. That reach sizes the finite
rectangles used as halfspaces. [Bounds and masks][bounds-and-masks]

Here a *halfspace* means the large rectangular region kept on one side of a
cross-section line. The actual representation is finite. This exact helper
positions its near edge in local tangent coordinates:

```python
def _section_halfspace_face(point, heading, extent, forward):
    if forward:
        x_start, x_finish = -1.0e-5, extent
    else:
        x_start, x_finish = -extent, 1.0e-5
    return _oriented_rectangle(point, heading, x_start, x_finish, 2.0 * extent)
```

`point` and `heading` locate the cross-section; `extent` is the calculated
reach. `_oriented_rectangle` converts those local tangent and normal
coordinates into XY vertices. Each rectangle is `2 × extent` wide across
the track. Forward means towards increasing reference station.
[Halfspace and rectangle construction][halfspace]; [oriented rectangle][rectangle]

The near edges extend `1.0e-5` mm past the nominal cut in both directions.
Adjacent regions therefore include a nominal **`2.0e-5` mm common band**
before clipping. They are not mathematically disjoint regions. The later
area or volume overlap check governs what the partition accepts. The source
does not state a rationale for that small offset. [Halfspace implementation][halfspace];
[partition check][partition]

For each planned interval, this exact excerpt from `create_section_masks`
starts from the overall face and applies its internal limits:

```python
for index, (start, finish) in enumerate(section_plan["ranges"]):
    face = overall.copy()
    if index > 0:
        start_point, start_heading = interpolate_alignment_station(data, start)
        face = face.common(_section_halfspace_face(start_point, start_heading, extent, True))
    if index < range_count - 1:
        finish_point, finish_heading = interpolate_alignment_station(data, finish)
        face = face.common(_section_halfspace_face(finish_point, finish_heading, extent, False))
```

`face.common(...)` keeps the native intersection. The first interval has no
start cut, and the last has no finish cut. **Inference from this construction:**
source material beyond the reference's endpoints, such as exposed formation
end margins, can remain in the first or last piece.

The builder refines each resulting face and rejects a null result or one with
no face components. It translates a copy to `z_min` and extrudes it through
`z_max - z_min` to produce a solid cutter. A null extrusion is rejected.
Each mask records `start`, `finish`, `face` and `solid`. [Mask construction][masks]

In the curve workflow, the bounds use the track compound, available platform
bodies and formation body, including available layers not selected for
sectioning. The caller supplies vertical bounds for their heights and board
depth. All selected layers then reuse the same mask list. [Caller and bounds][mask-caller]

The two cutting wrappers are deliberately small. These exact source functions
apply the corresponding face or solid cutter:

```python
def section_plan_face(face, masks):
    return [_common_or_none(face, mask["face"]) for mask in masks]


def section_solid_shape(shape, masks):
    return [_common_or_none(shape, mask["solid"]) for mask in masks]
```

`_common_or_none` uses the native intersection, returns `None` for a null or
wholly negligible result, and refines usable geometry. A missing piece is a
slot in the returned list; it does not renumber the remaining intervals.
[Clipping helpers][clipping]

## Follow the same cuts across a curved family

The next figure is a **new nominal circular teaching construction** using the
earlier chapters' dimensions. It does not reproduce their full Euler-easement
fixture or a new native FreeCAD partition.

Take a 300 mm main-reference arc of radius 600 mm, starting at XY `(0, 0)`
with heading along positive X and turning left about `(0, 600)`. The outer
track has radius 655 mm and both printable strips are 32 mm wide.
Here ideal main station `s` gives angle `theta = s / 600`. A 100 mm maximum
and 50 mm minimum produce three balanced reference intervals, with internal
cuts at `s = 100` and `s = 200` mm.

Because both circles meet a perpendicular reference line at the same angle,
each outer-centreline interval has ideal arc length
`100 × 655 / 600 = 109.166667` mm. The common cut positions align the pieces;
they do not impose a 100 mm maximum on the outside track's own arc length.

Place the same 150 mm outside platform used in the preceding explanation so
that its start meets main station **120 mm**. Retain 20 mm edge clearance from
the outer centreline, 30 mm full width, 30 mm end tapers and 12 mm height.
Its relative outer-host station `u` corresponds to `s = 120 + u × 600 / 655`. Its finish is therefore
at main station **257.404580 mm**.

| Shared reference interval | Main-centreline length, mm | Outer-centreline length, mm | Platform length along its outer host, mm |
| --- | ---: | ---: | ---: |
| Section 01: 0–100 | 100 | 109.166667 | No platform piece |
| Section 02: 100–200 | 100 | 109.166667 | 87.333333 |
| Section 03: 200–300 | 100 | 109.166667 | 62.666667 |

The platform lengths add to 150 mm. Section 02 begins before the platform,
and Section 03 finishes after it. Those two platform pieces keep their shared
section numbers; they do not become platform Sections 01 and 02.

Retain a 10 mm formation margin, 120 mm minimum width and 12 mm thickness.
In the continuous illustration from the
[formation chapter](formation-board.md#follow-the-board-beyond-a-platform-end),
the support envelope starts broadening about 40.519084 mm before the platform.
Moving its origin to main station 120 places that change at **79.480916 mm**,
inside Section 01. The final board still has its 120 mm minimum width until
**105.480916 mm**: both edges shift as the support envelope expands. Its outline
can therefore respond to the platform in Section 01, which contains no platform
piece. The width itself increases in Section 02. This distinction follows the
board's broadening and minimum-width calculations.

```{figure} ../_static/figures/section-shared-boundaries-example.svg
:alt: A nominal curved pair of track strips, an outside platform and a formation outline share perpendicular cuts at main stations 100 and 200 millimetres. The platform occupies only Sections 02 and 03.

Shared internal boundaries in an ideal circular example. The first and last masks retain the exposed formation end margins. The drawing is not a native cutting result or a statement of sheet or printer-bed fit.
```

The actual workbench locates these boundaries using sampled station data and
native intersections. For track-specific downstream operations,
`calculate_template_section_stations` maps each shared line to a station on
each track centreline. Its `alignment_station_at_cross_section` helper collects
candidates from sampled points and segments. If none is found, it accepts
the nearest sampled point when its perpendicular distance to the line is at
most **0.01 mm**; otherwise it raises an error. With several candidates,
it chooses the one nearest the corresponding fractional travel progress.
After mapping all boundaries, it sets the first and last stations to that
track's own endpoints and rejects any interval whose finish is no more than
`1.0e-8` mm beyond its start. It does not reapply the main plan's length limits
to those secondary-track intervals. [Track-specific station mapping][track-stations]

## Check what each partition preserves

A usable native cut is not sufficient on its own. The caller checks whether
the list of pieces preserves the source geometry and whether neighbouring
pieces overlap beyond its comparison threshold.

This exact excerpt from the curve caller checks each printable strip
**before** corresponding pieces are combined:

```python
if section_config["section_track_templates"]:
    for source in template_sources:
        pieces = section_solid_shape(source["solid"], section_masks)
        validate_section_partition(
            source["solid"],
            pieces,
            "'{}' track-template".format(source["alignment"]["name"]),
            require_every_section=True,
        )
```

The required slots differ by layer:

| Source being divided | Geometry checked | Must every interval contain a piece? |
| --- | --- | --- |
| Each printable track strip | Initial strip solid | Yes |
| Each platform with body output | Body and its separate plan face | No |
| Formation board | Plan face before section registration and extrusion | Yes |

The platform exception permits partial route coverage. It still requires at
least one usable piece and complete coverage of the original platform under
the same area or volume checks. It does not waive reconstruction. Track and
formation checks reject a missing slot. A slot can contain a compound;
“present in every section” does not promise exactly one connected solid.
[Layer calls][layer-calls]; [validator][partition]

### Measure missing geometry, overlap and reconstruction

`validate_section_partition` uses volume when the original shape's volume
exceeds `1.0e-8`; otherwise it uses area. It does not compare wire length.
The source defines its reference measure and tolerance exactly as follows:

```python
original_measure = max(dimensional_measure(original_shape), 1.0)
tolerance = max(1.0e-5, original_measure * 1.0e-7)
```

For a solid, these measures use mm³; for a face, mm². The reference measure
is floored at **1.0**, and that floor affects the reconstruction target as
well as tolerance. For example, the arithmetic would compare an original
measure of 0.5 against 1.0. That is a source-derived corner of this formula,
not a runtime test or an instruction to alter the tolerance.
[Measurement and tolerance][partition]

The validator removes absent or null entries from its usable list, checks
any required slots, and rejects a wholly empty result. It then measures
what remains of the source after subtracting all usable pieces. This exact
excerpt performs one cut against their compound:

```python
section_compound = usable[0] if len(usable) == 1 else Part.makeCompound(usable)
missing = original_shape.cut(section_compound)
missing_measure = dimensional_measure(missing)
```

The adjacent source comment records why it uses that arrangement: every
piece was already clipped with `source.common(shared_mask)`, and a single
cut avoids repeatedly fragmenting the remaining source through many Boolean
operations. This explains the implementation choice without claiming a new
performance result. [Recorded validation rationale][partition]

Next, the function adds the piece measures and examines every pair whose
bounding boxes may overlap. A native intersection measures each pair's
overlap. Any pair above the tolerance is rejected. It subtracts the sum of
pair overlaps before comparing the reconstructed measure with the reference:

```python
reconstructed_measure = section_measure - overlap_measure
measure_shortfall = max(0.0, original_measure - reconstructed_measure)
measure_excess = max(0.0, reconstructed_measure - original_measure)
```

This exact excerpt calculates the reconstructed measure and its differences.
The following condition rejects the partition if `missing_measure`,
`measure_shortfall` or `measure_excess` exceeds `tolerance`. Its error includes
the measured values and permitted tolerance. The checks serve different
purposes: direct subtraction finds uncovered source, pair comparisons detect
overlap, and the reconstructed measure checks the total. [Complete check][partition]

The check relies on pieces having been clipped to the source. It is not a
complete topology or B-rep equality test, and its pairwise arithmetic is not
an explicit fused-union comparison. Tight turns or returning routes can make
these spatial cuts unsuitable; **inference from the implementation:** the
overlap and coverage checks reject such a partition rather than choosing an
alternative cutting strategy. These thresholds do not establish fabrication
accuracy, structural support or physical fit.

### Keep later assembly changes outside that claim

The order of operations limits what the partition check covers:

- Track pieces are checked before track joints and fixing holes modify them.
- Matching fixing holes can already have changed the formation face when
  that face is partitioned and checked.
- Formation registration features modify the checked section faces; section
  outlines and downward solids are then derived from those modified faces.

Those are intentional later operations. The initial strip or formation
partition check does not certify every final jointed or drilled result.
[Curve operation order][layer-calls]; [straight operation order][straight-layers]
The [assembly and fixing chapter](assembly-and-fixing.md) follows the separate
board and strip placement rules through the final geometry.

## Preserve objects and give each route its own sequence

For the curve family, the preservation decision begins with this exact
source statement:

```python
preserve_unsplit = bool(section_config["preserve_unsplit"] or not section_active)
```

If the calculated plan is inactive, complete objects remain. With an active
plan, a selected layer emits section pieces; **Preserve unsplit objects:**
decides whether it also retains its complete output. An unselected layer
keeps its complete output regardless of that checkbox. [Curve preservation][preservation]

Retained output is not uniformly hidden. Complete track-template objects
are hidden when track sectioning is active. Complete platform bodies retain
their `show_body` choice, and formation outline/solid objects retain their
respective show choices. “Unsplit” also need not mean untouched by every
earlier assembly operation: matching holes may already be present.
[Track visibility][track-visibility]; [platform visibility][platform-visibility];
[formation visibility][formation-visibility]

### Straight routes prepare their own plans

Each straight production bundle uses its own `alignments[0]` as the reference,
calculates its own total and section plan, then creates its own masks.
It can section track strips and formation geometry; it does not section
physical platforms. Effective straight-layer flags require the selected
option and actual available source geometry. If neither layer is effective,
that route keeps its complete output. The curve's later missing-layer checks
still apply to the curve family. [Straight reference][straight-reference];
[straight plan and masks][straight-plan]; [straight preservation][straight-preservation]

Local numbering restarts at 01 for each straight route. The route's identity
distinguishes its Section 01 from the curve's Section 01 or another route's
Section 01. “Universal” here describes shared machinery and shared boundaries
within each route's selected layers. It does not create one continuous global
station plan or number sequence across all curve and straight geometry.
[Straight object loop][straight-objects]

### Separate object numbers from engraved numbers

The object loops assign section labels, `SectionNumber` and
`TravelOrderNumber` from `index + 1`. **Number in travel order:** controls
the additional number-engraving shapes. Clearing it omits those shapes but
does not remove the objects' section identities. A platform with no first
piece can consequently begin at Section 02. [Number request][numbering];
[curve section objects][curve-objects]; [straight section objects][straight-objects]

The engraving builder uses stroke digits and at least two-digit formatting.
It creates separate geometry at the engraving display lift. When formation
is available, placement tries positions across the interval midpoint, checking
a candidate rectangle against the board and protected regions. If none passes,
the helper returns the reference midpoint anyway. Do not infer guaranteed
clear placement from the presence of a number. [Number geometry and placement][number-geometry]

The principal visible objects have these base name patterns. Generated-set
suffixes and uniqueness handling can change the complete internal name.

| Example base name | Generated role | Meaning |
| --- | --- | --- |
| `RailwayTrackTemplateSection_01` | `TrackTemplateSection` | Combined curve-track pieces for one shared interval. |
| `RailwayPlatformSection_P01_S02` | `PlatformSection` | Platform 1's piece in shared Section 02. |
| `RailwayFormationSection_01_Profile` / `_Body` | `FormationSection` | Formation cutting profile or solid for one interval. |
| `RailwaySectionNumberEngraving_01` | `EngravingGeometry` | Separate section-number lines. |
| `RailwayStraightTrackTemplateSection_R01_S01` | `StraightTrackTemplateSection` | Route 1's combined strips in its local Section 01. |
| `RailwayStraightFormationSection_R01_S01_Profile` / `_Body` | `StraightFormationSection` | Route 1's formation profile or solid. |

These are derived `Part::Feature` objects. Tags identify the generated set,
role and export subtype. Straight features also carry `RouteID` and
`RouteName`. The visible section metadata's `SectionLength` is the reference
interval's `finish - start`, even where another track has a different distance
between the same cuts. Additional production-record objects can exist;
the table is not an exhaustive document inventory. [Curve objects][curve-objects];
[straight objects][straight-objects]; [identity tags][identity-tags];
[section metadata][metadata]

## Follow saved state and failure recovery

Accepted dialogue inputs are remembered before geometry validation and
replacement confirmation. On the next opening, those remembered values take
precedence over generated settings. Otherwise `read_section_config` reads
`SectionConfigurationJSON`, normalises it and falls back to defaults for
missing or unsuitable data. Successful generation writes that JSON and a
`SectionSummary` on the settings output.
[Input precedence][load-state]; [remembered inputs][remembered];
[configuration reader][config-reader]; [settings writer][settings];
[summary writer][summary]

The following failures occur during preparation, before old generated
objects are removed:

| Condition | Result |
| --- | --- |
| Unusable reference length, inconsistent limits or more than 999 nominal pieces | The planner rejects the request. |
| Balanced lengths below the minimum, or a final unbalanced pair that cannot satisfy the limits | No section plan is returned. |
| Active curve plan with no selected layer or unavailable platform/formation output | Layer prerequisites reject the selection. |
| No source bounds, an empty mask or a null cutting prism | Native mask preparation fails. |
| Missing required strip/formation pieces, no usable platform piece, or excessive missing/overlap/reconstruction measure | Partition checking rejects the pieces. |
| No crossing candidate is found and no sampled point is within 0.01 mm of a shared boundary, or a mapped interval's length is at or below `1.0e-8` mm | Track-specific station mapping rejects the arrangement. |

[Planner][plan]; [prerequisites][prerequisites]; [mask checks][masks];
[partition checks][partition]; [track mapping][track-stations]

A failed partition preserves the earlier generated objects at this stage,
but it does not mean that nothing changed anywhere: attempted dialogue values
may already have been remembered. The shared generation workflow opens its
document transaction later and removes old generated output inside it.
A document-stage exception attempts to abort the transaction.
[Replacement boundary][transaction];
[generation and replacement](generate-template-set.md)

Export follows the document commit and has its own failure reporting.
Furthermore, the normal B16 Core dependency inventory rejects a configuration
with sectioning enabled. Generated section objects and their export metadata
do not establish admission to that export route. The tooltip's “export-ready”
description must be read with this implementation boundary.
[Commit and export order][export-order]; [current Core export scope][export-scope]
The dedicated export explanation is tracked in [issue #33][export-issue].

## Evidence and reproduction limits

All Python blocks on this page are exact source excerpts after removal of
their common enclosing indentation. They require the containing functions,
variables and host context named beside them; they are not standalone
FreeCAD examples. The independent figure tool verifies the numerical
illustrations and saved values. The
[development guide](../development.md#regenerate-the-alignment-figures)
gives its commands.

The retained station-mapping regression records an actual B16
platform-sectioning comparison. Its two-track curve had a 600 mm main radius,
600 mm transitions and a 90° turn. The outside platform changed from 250 to
300 mm, with 600 mm maximum and 100 mm minimum section lengths, balanced
lengths, number geometry and preserved complete output. It compared records,
roles, section numbers, geometry metadata, history, two Undo/Redo cycles,
persistence and preference recovery. Its earlier Undo/Redo procedure used
three steps. [Retained GUI case][gui-evidence]

That case disabled **formation, assembly and export**. The report does not
claim complete B-rep or export-byte equality, a general performance result,
or proof of every sectioning combination. Its recorded empty-source fixture
failure also shows why a successful process exit alone was insufficient:
the required success marker was absent. [Evidence limits][gui-evidence];
[recorded fixture correction][fixture-evidence]

No new workbench, upstream validator, macro or FreeCAD process was executed
for this chapter. The straight length calculation and continuous circular
drawing explain the source relationships. They do not reproduce finite
sampled masks, the small common band at a cut, native Boolean operations,
or partition-validation results. Keep native evidence, nominal arithmetic
and output-use claims within those stated limits.

[revision]: https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf
[controls]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4262-L4299
[defaults]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L965-L992
[length-editor]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4771-L4779
[import-spec]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L2242-L2253
[control-state]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L6023-L6050
[dialogue]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4760-L4768
[field-values]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L6234-L6245
[accepted]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40883-L40932
[prerequisites]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41240-L41268
[main-length]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41098-L41100
[plan]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10537-L10585
[geometry-tolerance]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L596
[section-constants]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L509-L510
[station-core]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L1992-L2055
[adapters]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L659-L685
[bindings]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L1168-L1178
[installation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L1458-L1499
[masks]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10669-L10699
[earlier-mask]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10596-L10639
[bounds-and-masks]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10642-L10699
[halfspace]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10661-L10666
[rectangle]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10826-L10839
[mask-caller]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41318-L41350
[clipping]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10702-L10721
[track-stations]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11134-L11210
[partition]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10743-L10824
[layer-calls]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41352-L41475
[straight-layers]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11596-L11697
[preservation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41505-L41522
[track-visibility]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41709-L41725
[platform-visibility]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L42220-L42258
[formation-visibility]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L42260-L42293
[straight-reference]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11454-L11468
[straight-plan]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11535-L11594
[straight-preservation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11699-L11737
[straight-objects]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41904-L42083
[numbering]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41478-L41503
[curve-objects]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L42341-L42494
[number-geometry]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11069-L11132
[identity-tags]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L6881-L6939
[metadata]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11873-L11905
[load-state]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40801-L40849
[remembered]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40910-L40932
[config-reader]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L6502-L6511
[settings]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L21731-L21799
[summary]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L21922-L21931
[transaction]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41642-L41658
[export-order]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L42666-L42715
[export-scope]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/core_dependency_inventory.py#L164-L170
[gui-evidence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-09-12-phase7-station-mapping-regression.md#L96-L139
[fixture-evidence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-09-12-phase7-station-mapping-regression.md#L256-L264
[export-issue]: https://github.com/Richard-Gnitnub/tracktemplate-docs/issues/33
