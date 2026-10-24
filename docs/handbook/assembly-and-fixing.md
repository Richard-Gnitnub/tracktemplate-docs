<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted for the TrackTemplate developer handbook, 2026-10-24.
-->

# How board registration, strip joints and fixing holes work

Two adjacent groups in the generation dialogue solve different assembly
problems. **Formation-board registration features** locate neighbouring
formation-board sections with board joints or alignment holes. **Track-template
assembly and fixing** modifies each sectioned track strip with its own joint
and optional centreline fixing holes. Those fixing holes can also be cut through
the formation board, using the *same XY positions*. Board registration remains
an independent feature-placement operation.

The design intent displayed in the dialogue is to make sectioned pieces easier
to assemble while keeping their original railway alignment. In particular,
strip fixing holes lie on the track centreline; board registration searches for
available material beyond protected track and platform footprints. **Inference
from the code:** those different placement rules prevent a board joint from
depending on the strip's own joint position. They do not establish physical fit
for a particular material or cutting process. [Dialogue text][ui];
[board placement][registration]; [strip assembly][strip-joints]

**Implementation examined:** TrackTemplate
[`7965bfc4671668f889c1f43fb8336c5146c3f5cf`][revision]. The controls,
Boolean operations and generated objects are in the retained B15 host. The B16
workflow binds modular centreline station calculations into these callers; it
has not replaced the registration and joint builders with separate Core
algorithms. [B16 caller bindings][composition];
[sectioning context](sectioning.md)

## Choose the correct feature group

Both groups sit below **Universal sectioning** in the main generation dialogue.
Their controls become available when the relevant layer can be sectioned.
Selecting a group of fields alone does not regenerate the document: the main
dialogue's **OK** action supplies the configuration to Generate.
[Control enablement][control-state];
[generation and replacement](generate-template-set.md)

| Feature group | Editors become available when | What it changes |
| --- | --- | --- |
| **Formation-board registration features** | **Formation board** is enabled; **Enable sectioning:** is on with **Maximum section length:** above zero; **Section formation board:** is selected. | Adjacent board-section faces, then their derived perimeter and downward solid. |
| **Track-template assembly and fixing** | **Enable sectioning:** is on with a positive maximum; **Section track templates:** is selected. The subordinate editors need **Enable template assembly features:** as well. | Every generated track strip's native section solids, plus optional profile objects. |

The calculation must also produce an *active* multi-section plan. An enabled
checkbox with a maximum at or above the reference route's length produces an
inactive plan and no internal joints. [Section planner][plan];
[straight-route preparation][straight-route];
[curve preparation][curve-route]

### Formation-board registration controls

**Joint type:** offers four exact labels:

| Mode | Result at each shared internal board boundary | Relevant editors |
| --- | --- | --- |
| **Plain joints** (default) | No added registration geometry. | Only **Joint type:**. |
| **Alignment holes** | Paired before/after circular holes placed in safe board material. | **Alignment-hole diameter:** 4 mm, **Hole offset from joint:** 15 mm by default. |
| **Pins and sockets** | Up to two male and mating socket profiles, at different safe offsets across the board. | **Joint depth:** 12 mm, **Joint width:** 16 mm, **Fit clearance:** 0.20 mm by default. |
| **Tongue-and-groove joints** | One male and mating groove profile, when a safe location is found. | The same depth, width and fit-clearance editors. |

The default lengths above are loaded through `clone_registration_config`;
remembered or saved settings may replace them. The mode selector is the way to
disable board registration: it has no separate registration-enable checkbox.
The unused editors are disabled for each mode. “Up to two” is deliberate:
`_find_joint_rectangles` returns the safe candidates found, even if its
requested count of two cannot be reached. At least one is needed to proceed.
[Board defaults][defaults]; [controls][ui];
[candidate search][board-candidates]

### Track-template assembly controls

The strip mode names differ from the board modes: **Template joint type:**
offers **Plain joints**, **Pins and sockets**, and **Tongue-and-socket joints**.
The default is **Tongue-and-socket joints**; strip assembly itself is initially
off. These are **strip** joints, even when a board is also selected.

| Exact visible label | Default after assembly is enabled | Meaning |
| --- | --- | --- |
| **Joint depth:** | 8 mm | Nominal projection beyond the internal strip boundary. |
| **Joint width / pin diameter:** | 10 mm | Centred tongue width, or diameter of each of two rounded pins. |
| **Fit clearance:** | 0.20 mm | Extra socket depth and sideways clearance. |
| **Centreline fixing holes:** | On | Cut through-holes on each individual strip's centreline. |
| **Holes per strip per section:** | 2 | Count on *each* track in *each* section, editor range 1–20. |
| **Fixing-hole diameter:** | 2 mm | Diameter of each finished strip hole. |
| **Minimum distance from section ends:** | 25 mm | Requested centre-to-end distance; the joint guard can increase it. |
| **Matching holes in formation board:** | Off | Cut the strip-hole pattern through the board if formation geometry exists. |
| **Show hole-cutting geometry:** | On | Show or hide separate selectable hole profiles; it does not switch the cuts off. |

The three joint dimension editors activate only for a shaped strip mode. Hole
count, diameter, clearance, matching holes and display activate only while
**Centreline fixing holes:** is selected. **Plain joints** can still produce
fixing holes. Values in the dialogue have widget limits; configuration cloning
also normalises numeric values, so a widget range must not be mistaken for a
complete physical or manufacturing limit. [Strip defaults][defaults];
[control state][control-state]; [configuration readers][value-readers]

## Locate board registration away from protected footprints

The [formation-board calculation](formation-board.md) supplies a continuous
plan face and a *protected* collection of track and platform plan geometry.
The protected collection is prepared independently of the footprint-inclusion
checkboxes. The section planner supplies shared internal boundary stations;
each has a point and heading on the main reference alignment.
[Formation protection][formation-source];
[shared boundaries](sectioning.md#turn-reference-boundaries-into-shared-cutting-geometry)

`apply_registration_features` examines one internal boundary at a time. A
candidate location is an offset to the left or right of the reference
centreline's local normal, rather than a fixed offset typed into the dialogue.
`_normal_offset_candidates` derives offsets from the board bounding box, uses
steps of `max(2, 0.75 × feature_width)` mm and considers larger absolute
offsets first. This makes the search depend on the available board face and
feature size. It does not guarantee symmetric or evenly spaced placements.
[Normal-offset search][board-candidates]

For shaped joints, the builder tries rectangles for a male and a larger
socket. This exact source excerpt is within `_find_joint_rectangles`:

```python
male = _oriented_rectangle(centre, heading, -0.25, depth, width)
socket = _oriented_rectangle(
    centre,
    heading,
    -0.25,
    depth + clearance,
    width + 2.0 * clearance,
)
guard = _oriented_rectangle(
    centre,
    heading,
    -2.0,
    depth + clearance + 2.0,
    width + 2.0 * clearance + 4.0,
)
```

The enclosing function has already moved `centre` along the boundary normal.
Local X follows the boundary heading; local Y crosses it. The guard extends
2 mm beyond the nominal feature range and 2 mm past each side of the expanded
socket. The search accepts a location only when the guard is almost wholly
inside the board (`common.Area >= 0.999 × guard.Area`) and intersects the
protected shapes by at most `1.0e-5` mm². A Boolean failure rejects that
candidate. Those numerical tests are placement rules, not fit tolerances.
[Inside/protection checks][board-candidates];
[rectangle construction][rectangles]

At each boundary, the preceding board face gains the male geometry; the next
face has its socket removed. **Alignment holes** instead locate one or two
normal offsets; for each offset, a hole lies before and after the joint at the
entered longitudinal distance. The candidate guards are larger than the
holes and must also fit the board and avoid protected geometry. The separate
alignment-hole object holds the resulting circular outlines. If no candidate
is safe, generation raises an error that suggests a greater formation margin,
smaller feature or **Plain joints**. [Board registration][registration];
[alignment-hole search][board-candidates]

These operations change board **section faces**. The host then creates their
perimeters and extrudes their bodies down by the configured board thickness.
The board's registration profiles are separate from its actual cut solids.
Neither operation adds a joint to a physical platform body.
[Board-section outputs][curve-route]; [object creation][objects]

## Make a joint on every individual track strip

Each shared cut is originally defined on the main alignment. An outside track
may travel a different distance between those cuts, so
`calculate_template_section_stations` intersects each shared cross-section
with each strip's own centreline. It checks increasing travel order, fixes the
first and last stations to that strip's endpoints, then supplies a list of
stations per track. [Station mapping][station-mapping];
[sectioning example](sectioning.md#follow-the-same-cuts-across-a-curved-family)

At an internal boundary, `apply_track_template_joints` takes the **position**
from the individual track but the **heading** from the main shared boundary.
This exact source excerpt occurs inside its per-track loop:

```python
track_station = template_section_stations[track_index][boundary_index + 1]
point, _track_heading = interpolate_alignment_station(track_data, track_station)
male_faces, socket_faces = _template_joint_faces(
    point,
    main_heading,
    float(source["alignment"]["width"]),
    config,
)
```

The leading underscore on `_track_heading` signals that the interpolated
track heading is not used for joint orientation. The common cut direction
stays consistent across tracks, while each joint occupies its own strip.
The source validates the 2D feature faces against the unsplit strip's plan
face before extruding cutters through that strip's thickness.
[Joint application][strip-joints]

For a centred tongue, the male rectangle starts 0.25 mm before the section
line and ends at the entered depth; the socket starts 0.50 mm before the line,
extends to `depth + clearance`, and is `width + 2 × clearance` wide. The
preceding native solid gains the tongue; the following solid has the socket
cut out. Separate outer-wire profiles record the joint geometry.
[Joint faces][strip-faces]; [native operations][strip-joints]

The first width check in `_template_joint_faces` is this exact excerpt:

```python
edge_margin = 1.0
usable_width = track_width - 2.0 * edge_margin
if width + 2.0 * clearance > usable_width + GEOMETRY_TOLERANCE:
    raise ValueError(
        "Template joint width {:.3f} mm plus clearance does not fit within a "
        "{:.3f} mm track strip while retaining 1 mm side margins.".format(
            width, track_width
        )
    )
```

It reserves 1 mm at each strip side for the expanded socket. **Pins and
sockets** has a second, distinct fit rule: two rounded pins must fit at
opposite normal offsets. The code calculates a maximum offset from the edge
and a minimum offset of `0.75 × (diameter + 2 × clearance)`. It refuses the
mode if those cannot both be met. Each rounded pin also needs
`depth > diameter / 2 + 0.25` mm. These checks are for the model geometry;
they do not qualify an actual pin fit. [Pin calculation][strip-faces]

## Distribute fixing holes along the track centreline

Hole placement uses each track's mapped section stations, its own centreline
and the requested count. It first chooses an **effective end clearance**.
When the strip has a shaped joint, the code automatically protects the joint
depth, socket fit adjustment, hole radius and a further 1 mm:

```python
joint_guard = 0.0
if config["joint_type"] != TEMPLATE_JOINT_PLAIN:
    joint_guard = (
        float(config["joint_depth"])
        + float(config["fit_clearance"])
        + radius
        + 1.0
    )
end_clearance = max(float(config["minimum_end_clearance"]), joint_guard)
```

This is an exact excerpt from `create_track_template_fixing_holes`; `radius`
is half the entered hole diameter. For **Plain joints**, the guard is zero
and only the requested minimum applies. With a shaped joint, a small entered
minimum can therefore yield a larger effective clearance. [Hole placement][holes]

For every section, the algorithm forms the usable station range:

```python
usable_start = start + end_clearance
usable_finish = finish - end_clearance
usable_length = usable_finish - usable_start
if usable_length <= GEOMETRY_TOLERANCE:
    raise ValueError(
        "Section {:02d} of '{}' is too short for {} fixing hole{} with "
        "the required {:.3f} mm end clearance.".format(
            section_index + 1,
            source["alignment"]["name"],
            hole_count,
            "" if hole_count == 1 else "s",
            end_clearance,
        )
    )
```

In that enclosing function, `start` and `finish` are the mapped stations on
one track centreline. The hole centres then use
`fraction = (hole_index + 0.5) / hole_count` within the usable range. Thus the
holes are evenly distributed **inside** the allowed interval; the first hole
need not lie exactly at the minimum clearance. The function cuts a circular
cutter through the corresponding native strip solid and returns the actual
hole faces plus elevated outline profiles, grouped by section. It also checks
that each hole fits inside the original strip plan face and that a diameter
plus 2 mm is no greater than strip width. [Hole stations and cutters][holes]

### Worked 400 mm strip: why 5 mm becomes 8.2 mm

This **nominal arithmetic example** isolates one ideal straight strip section.
Assume its own station range is `0–400 mm` and its width is **32 mm**. Enter
a **6 mm** tongue depth, **8 mm** tongue width, **0.2 mm** fit clearance,
**two** fixing holes of **2 mm** diameter and **5 mm** minimum end clearance.
These override the default depth, width and requested clearance.

| Calculation | Result |
| --- | ---: |
| Side-margin test: `8 + 2 × 0.2 ≤ 32 − 2 × 1` | `8.4 ≤ 30 mm`, passes |
| Hole radius: `2 / 2` | `1 mm` |
| Automatic joint guard: `6 + 0.2 + 1 + 1` | `8.2 mm` |
| Effective clearance: `max(5, 8.2)` | **8.2 mm** |
| Usable range | `8.2–391.8 mm` |
| Usable length: `400 − 2 × 8.2` | `383.6 mm` |
| Hole 1: `8.2 + (0.5 / 2) × 383.6` | **104.1 mm** |
| Hole 2: `8.2 + (1.5 / 2) × 383.6` | **295.9 mm** |

```{figure} ../_static/figures/assembly-fixing-example.svg
:alt: Schematic 400 millimetre long, 32 millimetre wide strip with fixing-hole centres at stations 104.1 and 295.9 millimetres; matching holes lie at the same planar coordinates in the board below.

The two 2 mm holes use the strip's centreline. When matching board holes are enabled, their centres follow the strip positions. The small drawn holes are enlarged for legibility; this is an arithmetic diagram, not a native FreeCAD result.
```

For another section starting at track station `s₀`, add `s₀` to both local
positions. On a curve, use the **mapped track-centreline stations** in place
of an assumed 400 mm main-reference interval. On a track using **Pins and
sockets**, the same input dimensions pass the separate two-pin width test:
the expanded socket diameter is `8.4 mm`, the calculated pin offsets are
`±8 mm`, and `6 > 8 / 2 + 0.25` mm passes the rounded-pin depth test. Passing
these equations is no substitute for a native shape check. [Pin logic][strip-faces]

The numbers above were independently recalculated from the source equations.
No FreeCAD join or hole cutting was executed for this example. The prior
retained [station-mapping regression][retained-evidence] explicitly disabled
assembly; it cannot be cited as native validation of these features.

## Cut matching holes through the board, then register its sections

When **Matching holes in formation board:** is enabled, the strip hole builder
returns each 2D hole face in model XY coordinates. The caller passes that
same list to `cut_formation_matching_holes`. The board does not recalculate
its own stations or spacing. This excerpt shows the board containment guard
and face cut inside that function:

```python
for hole_face in hole_faces:
    if not _candidate_inside_formation(hole_face, formation_geometry["face"]):
        raise ValueError(
            "A matching fixing hole lies outside the formation board. Include the "
            "track-template strips in the swept envelope or increase its margin."
        )
    face = _refine_shape(face.cut(hole_face))
```

Here `face` began as a copy of the board's plan face. The function also cuts
each hole through a copy of the board's downward body using a cutter extending
0.20 mm beyond both board faces. It returns updated board geometry and a
separate outline profile lifted slightly above the board. It refuses a missing
board, an outside hole or null resulting geometry. Matching holes require
actual formation-board output, but the **Section formation board:** checkbox
need not be selected merely to cut them into a complete board. [Matching
board cutter][matching]; [formation input](formation-board.md)

The order in the curve-generation route is consequential:

1. The main reference supplies section masks; each track strip is partitioned
   and its *base* pieces pass the section reconstruction checks.
2. Individual track stations are mapped. Strip joints are added and sockets
   removed; centreline fixing holes are optionally cut afterwards.
3. If requested, matching holes modify the continuous formation face and body.
4. Platform sections are cut separately. If formation sectioning is selected,
   the now-current formation face is partitioned and checked. Board
   registration changes the resulting board faces, followed by outline and
   solid construction.
5. Generate creates FreeCAD objects and metadata within its replacement
   transaction. An export, if requested, follows that document commit and has
   a separate failure boundary.

Both the main curved route and each straight-route production bundle follow
the strip → matching-board → board-registration dependency. The straight route
has its own reference alignment and rejects matching holes if no straight
formation extension exists. [Curved order][curve-route];
[straight order][straight-route];
[document transaction](generate-template-set.md)

The base strip partition check precedes its joint and hole alterations. The
board partition check uses its face **after matching holes**, but precedes
board registration. Therefore, passing a partition check cannot certify every
final jointed or drilled piece. [Partition checks](sectioning.md#keep-later-assembly-changes-outside-that-claim)

## Recognise the result and a failed placement

The generated set can contain section solids, one
**Track Template Joint** profile per shared internal boundary, **Track Template
Fixing Holes** profiles per section, **Formation Board Matching Fixing Holes**
profiles, and **Section Joint** registration or internal alignment-hole
profiles. These profiles are separately selectable `Part::Feature` objects,
with generated-role and export-category metadata. **Show hole-cutting
geometry:** changes visibility of the strip and matching-board hole profiles;
the through-cuts remain in the solids. [Generated objects][objects]

| Situation | Implementation response and next step |
| --- | --- |
| No active split or a **Plain joints** mode | No shaped joints from that mode. Strip holes can still be enabled independently. |
| Board placement guard overlaps protected geometry or falls outside available board material | Try another normal offset. If none fits, report the joint number; increase board margin, reduce feature size or select **Plain joints**. |
| Strip tongue or socket breaches its plan face, or 1 mm side margins fail | Reject the joint; reduce depth/width or change mode. The two-pin mode has an additional fit check. |
| A strip section is missing, its mapped boundaries reverse, or a hole does not fit | Reject the construction with a specific geometry or station diagnostic. Check section lengths and affected track geometry. |
| Two end guards leave no usable centreline range | Reject the hole pattern; increase section length, reduce feature depth/diameter or adjust the request. |
| Matching board is absent or too narrow | Reject matching-hole cutting; enable an adequate board footprint or turn matching off. |
| FreeCAD produces a null feature or cut | Raise a native-shape error; the normal Generate replacement transaction attempts to preserve the prior generated set. |

The generation path prepares native geometry before replacing the existing
generated document objects. The replacement transaction attempts to abort on
an exception; remembered dialogue values and later filesystem export are
separate state boundaries. See
[Generating and replacing a template set](generate-template-set.md) for the
full state and Undo account. The presence of export metadata does not mean
these assembly modes are supported by the current **B16 Core export** route:
its dependency inventory excludes sectioning, registration and template
joints. [Current Core-export exclusions][export-scope]

These pages describe inspected source and independent numerical arithmetic.
They do not prove a manufactured joint, clearance, retained B-rep after
save/reopen, or production readiness. For further inspection, start with the
specific source owners below.

## Source map

| Reader question | Owning implementation |
| --- | --- |
| Where are the labels, defaults and activation conditions? | [GUI fields][ui], [default/clone functions][defaults], [enablement][control-state] |
| How do board joints avoid railway footprints? | [Protected board geometry][formation-source], [candidate tests][board-candidates], [board registration][registration] |
| How do the two tracks get different boundary stations? | [Per-track station mapping][station-mapping], [B16 composition][composition] |
| What shapes do strip joint modes construct? | [Face builders][strip-faces], [native application][strip-joints] |
| How are hole positions and the effective guard calculated? | [Fixing-hole function][holes] |
| How are matching board holes carried into generated output? | [Matching-hole cut][matching], [curve call order][curve-route], [objects][objects] |

[revision]: https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf
[ui]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4302-L4391
[defaults]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L994-L1063
[value-readers]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L6247-L6273
[control-state]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L6023-L6056
[composition]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L145-L184
[plan]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10537-L10585
[formation-source]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10461-L10521
[board-candidates]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10841-L10962
[rectangles]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10826-L10839
[registration]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10965-L11038
[station-mapping]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11134-L11210
[strip-faces]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11222-L11305
[strip-joints]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11308-L11370
[holes]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11372-L11456
[matching]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11839-L11871
[straight-route]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11535-L11697
[curve-route]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41320-L41475
[objects]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L42325-L42550
[retained-evidence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-09-12-phase7-station-mapping-regression.md#L96-L139
[export-scope]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/core_dependency_inventory.py#L164-L170
