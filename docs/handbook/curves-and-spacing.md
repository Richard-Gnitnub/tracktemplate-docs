<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted source excerpts and new explanation, 2026-10-24.
-->

# How curves and independent track spacing are calculated

A pair of tracks can have one spacing on the entry straight, another through
the curve and a third on the exit straight. The calculation must connect those
parts with continuous position and direction while keeping the circular
sections concentric. This chapter explains how the **Main curve** and
**Independent parallel-track controls** define that problem and how the three
alignment modes solve it. These alignments represent plain line track: curves
and transitions do not change that railway classification.

**Source:** workbench revision
[`7965bfc4671668f889c1f43fb8336c5146c3f5cf`][revision]. The B16 development
launcher retains the B15 dialogue and generation workflow. Its final
calculation bindings use `tracktemplate.domain.alignment` through
`tracktemplate.api`; compatibility adapters turn the returned XY pairs into
FreeCAD vectors. The [generation chapter](generate-template-set.md) follows
the surrounding document operation. The [transition-edit chapter](transition-edit.md)
covers a separate canonical Entry/Exit editor. The selected bindings for this
chapter are visible in the [B16 adapter construction][b16-adapters] and
[composition check][b16-binding].

## The controls decide which quantities are fixed

The main track has one **Main transition length (each):** value for both Euler
easements. **Main constant radius:** specifies its centreline radius, and
**Total turn angle:** includes both easements and the circular section.
Lengths use model millimetres. The angle control uses degrees: positive turns
left and negative turns right. **Main template width:** specifies the strip
width about the centreline; it is not the distance between tracks.

Each added row has its own **Name**, **Side**, geometry and output choices.
**Entry spacing** and **Exit spacing** mean perpendicular centre-to-centre
distances from the main track's straight tangent lines. **Curve spacing** is
the radial distance between concentric centrelines. Every row measures from
the main track, not from the preceding row. **Strip** and **Centreline** select
the corresponding outputs; they do not choose a different alignment equation.
The main alignment enables both outputs. [Control definitions][controls]

| Alignment mode | Supplied by the user | Calculated during generation |
| --- | --- | --- |
| **Euler - match spacings** | Entry, curve and exit spacings | Independent entry and exit Euler lengths |
| **Euler - use lengths** | Curve spacing; entry and exit Euler lengths | Entry and exit straight spacings |
| **Platform widening** | All three spacings and both transition lengths | A separate curvature-shape parameter for each end |

The mode-change signal calls `CurveInputDialog._update_row_mode`. This exact
excerpt needs the method's row widgets and the two mode tests above it:

```python
start_box.setEnabled(match_spacings or platform_mode)
finish_box.setEnabled(match_spacings or platform_mode)
entry_box.setEnabled(not match_spacings)
exit_box.setEnabled(not match_spacings)
```

Changing mode enables the relevant inputs; it does not run the solver or
refresh calculated cells. `values()` later reads the rows for generation.
`prepare_track_alignment` replaces calculated values in each successful row's
configuration so generation can store the prepared values. Reopening also
uses remembered inputs, which can take precedence over document settings; the
[generation chapter](generate-template-set.md#what-values-collects-and-what-is-remembered)
explains that distinction. The existing B16 export-policy wrapper changes export controls and
export configuration; these maths controls retain their B15 handlers.
[Mode handling][row-modes]; [configuration update][prepare-result];
[B16 export wrapper][export-wrapper]

**Number of additional tracks:** permits zero to twenty rows. **Add track**
increments that count; **Remove last track** removes the final row, regardless
of selection. **Duplicate selected track** copies the selected row, appends
` copy` to its name and selects the new row. Without a valid selected row,
or at the twenty-row limit, duplication returns without changing the table.
These actions edit dialogue state. [Row handlers][row-handlers]

## Establish the centreline and its frame

An alignment is a centreline with a travel direction. Its **tangent** points
along that direction. Its **curvature** describes the rate at which the
tangent angle changes with distance: a straight has zero curvature, and a
circle of radius `R` has curvature magnitude `1/R`.

For the equations below, station `s` is distance along the particular
transition, from its start in its travel direction. The main core begins
nominally at `(0, 0)`, travelling along positive X. The added tracks have
their own core starts, which can have different X coordinates. A downstream
station index instead starts at the first point of each complete alignment,
including any common straight extension; its distances follow sampled chords.
These origins must not be interchanged. [Core construction][euler-core];
[station indexing][stationing]

The calculation first constructs a left turn. At tangent angle `theta`, the
unit tangent is `(cos(theta), sin(theta))` and its left normal is
`(-sin(theta), cos(theta))`. A positive normal displacement is to the left
of travel. In this construction, **Inside** has side factor `+1` and
**Outside** has `-1`. For curve spacing `d`, the secondary radius is
`R_secondary = R_main - side_factor * d`.

The host converts the magnitude of the entered turn to radians. After
construction and common straight extensions, a negative entered angle
reflects Y coordinates and tangent angles; X and point order remain unchanged.
Thus **Inside** continues to mean the smaller radius for either turn direction.
[Side and radius functions][sides]; [host calculation order][host-preparation];
[handedness contract][handedness]

## Integrate the Euler easement and locate the circle

An Euler, or clothoid, entry of length `L` approaches a circle of radius `R`
with curvature increasing linearly. With `u = s/L` and `alpha = L/(2R)`:

```{math}
\begin{aligned}
\kappa_{\mathrm{entry}}(s)&=\frac{s}{RL},
&\theta_{\mathrm{entry}}(u)&=\alpha u^2,\\
\Delta x&=L\int_0^1\cos\theta(u)\,du,
&\Delta y&=L\int_0^1\sin\theta(u)\,du.
\end{aligned}
```

The local exit starts tangent to the circle and reduces curvature to zero.
Its relative heading is `2 * alpha * u - alpha * u * u`. Each easement
therefore consumes `L/(2R)` radians, even though its curvature varies.
`clothoid_entry_displacement` and `clothoid_exit_displacement` integrate the
cosine and sine with Simpson's rule. The default is 240 intervals, with an
even count and a minimum of 40. Their return value is `(dx, dy, alpha)`.
For a length at or below `GEOMETRY_TOLERANCE` (`1.0e-8` mm), both
functions return zero displacement and turn. Larger lengths use numerical
integration of the stated Euler curve. [Displacement functions][euler-displacement]

The circle centre lies one radius along the left normal from the main entry's
end. In `main_circle_centre`, the preceding call has supplied `x_end`,
`y_end` and `entry_angle`:

```python
normal_x, normal_y = _left_normal(entry_angle)
return (
    x_end + (main_radius * normal_x),
    y_end + (main_radius * normal_y),
)
```

This construction makes the circle tangent to the easement at their joint.
Every added track receives the same circle centre. Its radius and the angles
at which it joins and leaves that circle can differ. [Centre calculation][centre]

The remaining circular angle is the total turn minus the two easement angles.
This exact excerpt from `build_concentric_core` uses its millimetre and radian
inputs:

```python
entry_angle = entry_transition / (2.0 * radius)
exit_angle = exit_transition / (2.0 * radius)
circular_angle = total_angle - entry_angle - exit_angle
```

The builder rejects a circular angle below `-1.0e-9` rad and clamps a smaller
negative residual to zero. Consequently, solving each end separately is not
enough: their combined lengths must also fit the complete turn. The nominal
core length is the two transition lengths plus `radius * circular_angle`.
[Euler core builder][euler-core]

## Solve straight spacing or calculate it from length

For circle-centre ordinate `C_y`, the entry's signed tangent offset is:

```{math}
b(L)=C_y-\Delta y(L,R)-R\cos\left(\frac{L}{2R}\right).
```

The circle joint has ordinate `C_y - R*cos(alpha)`. Subtracting
the easement's lateral displacement gives the ordinate of its starting
tangent. This exact excerpt from `transition_start_signed_offset` implements
that subtraction; the caller supplies all three arguments:

```python
_x_end, y_end, angle = clothoid_entry_displacement(
    transition_length,
    radius,
)
return circle_centre_y - y_end - (radius * math.cos(angle))
```

For the symmetric main alignment, the same scalar relation gives the exit's
signed separation from the main exit tangent. That exit separation is measured
along the final left normal, not along global Y. The host independently checks
both actual straight spacings after construction. [Offset and solver][solver];
[spacing verification][spacing-check]

In **Euler - use lengths**, preparation evaluates `b` for each supplied
length. It requires `b * side_factor > 1.0e-8` at each end; otherwise that
straight would be on the wrong side or effectively coincident. The returned
straight spacings are `abs(b)`. Curve spacing continues to fix the radius.
[Preparation branches][prepare]

In **Euler - match spacings**, preparation asks the solver for
`b(L) = side_factor * requested_spacing`. The implementation brackets length
between zero and `max(0, 2 * radius * total_angle - 1.0e-6)`. This upper
limit comes from the angle consumed by one Euler easement; it is not a promise
that both solved ends fit together. The solver checks the offsets at these
two limits and rejects a requested offset outside their range, allowing a
`1.0e-6` mm comparison margin.

An endpoint match within `1.0e-8` mm returns that endpoint length. Otherwise,
the residuals must bracket a root. Up to 72 bisection iterations halve the
length interval, stopping at an offset residual of `1.0e-10` mm or an interval
of `1.0e-7` mm. The core builder then checks the combined angle. These are
the implemented numerical limits; they do not establish manufactured accuracy.
[Solver implementation][solver]

## A two-track comparison

The retained preparation fixture uses a main radius of 600 mm, two 600 mm
Euler easements and a 90-degree left turn. Its **Outside** track has a
55 mm curve spacing, giving a 655 mm constant radius, and a 32 mm strip width.
For **Euler - match spacings**, its entry and exit spacings are both 50 mm.
The retained Euler oracle gives `559.4102547270278` mm for each solved
transition. The preparation fixture supplies those same solved lengths to
**Euler - use lengths**, demonstrating the inverse input choice.
[Preparation fixture][preparation-fixture]; [retained Euler values][euler-fixture]

The table applies the equations above to that example and to one further
comparison: fixing the outside easements at 600 mm. Values are rounded to
three decimal places; calculations retain the unrounded fixture length.
The main track's 32 mm strip width is also used, but width does not enter
these centreline equations. It is neither track gauge nor a clearance check.

| Quantity | Main track | Outside: match 50 mm | Outside: use 600 mm lengths |
| --- | ---: | ---: | ---: |
| Constant radius, mm | 600.000 | 655.000 | 655.000 |
| Each Euler easement, mm | 600.000 | 559.410 | 600.000 |
| Each straight spacing from main, mm | — | 50.000 | 52.952 |
| Each easement's turn, degrees | 28.648 | 24.467 | 26.242 |
| Circular-section length, mm | 342.478 | 469.461 | 428.872 |
| Core length before straight extensions, mm | 1542.478 | 1588.282 | 1628.872 |

At the larger radius, copying the main easement length gives a different
lateral displacement and turn. The resulting straight spacing is 52.952 mm.
To obtain 50 mm, the matching solver shortens the outside easements. Each
then consumes less of the 90-degree turn, leaving a longer circular section.
This is why the three spacings and both lengths cannot all be independent
inputs to this Euler construction.

Both curves share circle centre `(297.517, 624.778)` mm. Their core starts
do not share an X coordinate: the main starts at `(0, 0)`, and the matched
outside core starts at approximately `(19.504, -50.000)` mm. Spacing is the
perpendicular distance between the tangent lines, not the distance between
those two start points.

```{figure} ../_static/figures/euler-two-track-example.svg
:name: euler-two-track-plan
:alt: Main and outside left-turn centrelines share a circle centre. Perpendicular entry and exit spacings are 50 mm, while radial spacing on the circles is 55 mm.

The matched-spacing case in the main track's local XY frame. Dots mark the
two core starts. Dashed lines extend the tangents for measurement; they are
not generated straight-route objects. Axis scales are equal.
```

```{figure} ../_static/figures/euler-curvature-example.svg
:name: euler-two-track-curvature
:alt: Curvature rises linearly, stays constant on the circle, then falls linearly. The outside track reaches a lower peak at a shorter entry length and has a longer circular section.

Curvature against distance from each track's own core start. The joins have
continuous curvature, although its gradient changes there. Matching the
horizontal-axis values does not identify corresponding positions across
the two tracks.
```

The [calculation data](../_static/figures/alignment-example-values.json) and
figures come from an independent documentation script that integrates these
equations and checks the retained circle centre and matched offset. It does
not run the workbench or reproduce its sampled native geometry. The 600 mm
manual comparison is a teaching calculation, not a new GUI result. See
[regenerating the figures](../development.md#regenerate-the-alignment-figures)
for its source and optional environment.

## Platform widening solves a different curve

The dialogue's recorded purpose for **Platform widening** is to permit a wider
concentric curve, for example beside an island platform, while keeping both
straight spacings and transition lengths as inputs. It uses a continuous
compound-curvature profile in the selected turn direction. This alignment
mode does not itself create a platform body. [UI design explanation][controls]

For normalised station `u`, radius `R` and solved shape parameter `a`, the
entry and exit curvatures are:

```{math}
\begin{aligned}
\kappa_{\mathrm{entry}}(u)&=\frac{3u^2-2u^3+16au^2(1-u)^2}{R},\\
\kappa_{\mathrm{exit}}(u)&=\frac{1-3u^2+2u^3+16au^2(1-u)^2}{R}.
\end{aligned}
```

The polynomial connects zero curvature at the straight to `1/R` at the
circle, with zero curvature gradient at both ends. The additional polynomial
term permits a curvature peak between them. Even `a = 0` is this polynomial
transition, not an Euler easement. Integrating curvature gives the transition
angle `(L/R) * (0.5 + (8/15) * a)`; integrating its tangent gives displacement.
[Platform displacement and intent][platform-displacement]

Preparation measures the main entry and exit tangent-line offsets, adds the
signed requested spacings and solves each end. The shape search starts at
`-0.187499`; its upper bound reserves part of the total turn. It samples the
permitted parameter range, bisects sign-changing intervals and also refines
the smallest sampled residual. The source comment explains the latter step:
a valid solution can touch the boundary of the achievable range without
crossing it. A sign-change search alone would miss that case.
[Shape solver][platform-solver]

When several candidates exist, the solver prefers the largest minimum radius,
then the smallest transition angle, then the smallest absolute shape parameter.
The complete builder checks that both transition angles fit within the turn.
It derives peak curvature and minimum radius as follows; this excerpt needs
the two solved parameters and the constant radius:

```python
entry_peak = platform_peak_curvature_factor(entry_shape_parameter)
exit_peak = platform_peak_curvature_factor(exit_shape_parameter)
minimum_radius = radius / max(1.0, entry_peak, exit_peak)
```

Thus a track with a larger constant radius can still have a tighter transition
than the main track. Preparation rejects a peak minimum radius at or below
half the strip width. The host also asks **Confirm platform minimum radius**
when a platform-mode track's minimum radius is more than 0.01 mm below the
main constant radius. Declining stops generation before replacement.
[Platform builder][platform-core]; [width check][prepare];
[minimum-radius confirmation][radius-confirmation]

The shared fixture's platform case keeps 600 mm transitions and specifies
40/55/40 mm entry/curve/exit spacing. It therefore changes both the curve
family and the quantities being held fixed; it is not the Euler result with
a different display setting. [Preparation fixture][preparation-fixture]

## From calculated alignment to visible geometry

Both builders return ordered `points` and `headings`, core endpoints,
transition lengths and angles, circular length and nominal core length.
Preparation adds the track's name, mode, spacings, width and output flags.
Only after its calculations succeed does it write the two transition lengths
and two straight spacings back into the input configuration. This is temporary
calculation state; the generation workflow owns document storage and Undo.
[Preparation contract][preparation-contract]

The core sampler divides each segment into `ceil(length / 3.0)` intervals.
It evaluates curvature at each interval's midpoint and advances by an arc
with that constant curvature. The builders then replace circular-junction
coordinates and the final endpoint with independently calculated values.
This preserves the intended connections while retaining sampled intermediate
points. A 3 mm station interval is not a 3 mm geometric-error allowance, and
it supplies no uniform chord-error bound. [Sampler and Euler corrections][euler-core];
[platform corrections][platform-core]

Common straight extensions bring all entry ends to the smallest starting X
and all exit ends to the largest projection along the final tangent. They
preserve perpendicular spacing. After handedness is applied, the host sets
`total_length` to the sum of point-to-point chord lengths. Downstream
`alignment_station_data` uses those same chord distances from each alignment's
first point. This differs from the nominal sum of analytical segment lengths.
[Extensions][extensions]; [host order][host-preparation]; [stationing][stationing]

In this generation route, `create_centreline_wire` calls `Part.makePolygon`.
The strip builder offsets sampled points by half the width along their
normals, closes a polygonal boundary and extrudes its face. A smooth-looking
viewport therefore does not establish an analytical clothoid or a fitted
spline in the native output. The separate canonical transition exact-validation
route also declares its representation explicitly: a polyline with a bounded
chord approximation. Its contract must not be transferred to this fixed-step
core sampler. [Native strip and centreline construction][native-output];
[separate exact-transition contract][exact-transition]

## Failures and the evidence to inspect

The following examples identify the boundary that rejects an input. They are
source-inspected cases, not new GUI results from this documentation task.

| Input or condition | What rejects it and how to respond |
| --- | --- |
| Main total turn angle is zero | The host reports `The total turn angle cannot be zero.` Enter a non-zero main turn; independent straight routes have separate controls. |
| Main radius 600 mm; **Inside** curve spacing 599 mm; width 4 mm | The added radius is 1 mm, below half the width. Preparation rejects the constant radius. Reduce spacing or width, or increase the main radius. |
| Outside radius 655 mm; two 1100 mm Euler easements; total turn 90 degrees | The two easements together consume more angle than the complete curve. The builder reports the maximum combined length. Shorten the transitions or increase the turn. |
| A requested Euler offset lies outside the solver's endpoint range | The diagnostic states the requested signed offset and achievable signed range. Change the spacing, radius or turn inputs. |
| **Platform widening** has a zero entry transition | Preparation reports that the track needs a positive Entry transition length before solving either shape. |

The [preparation tests][preparation-tests] cover all three modes and both
sides, result contents, configuration updates and failure behaviour against
the B14/B15 references. Their invalid-input cases include the radius and
combined-angle examples above. The [platform tests][platform-tests] exercise
the shape search and its callers. The [retained preparation evidence][preparation-evidence]
reports the bounded host and GUI comparisons, including rejection, Undo/Redo
and save/reopen; its historical results are not a new test run at this chapter's
publication time.

All code blocks above are excerpts inspected against the pinned source. They
need their containing functions and are not standalone runnable examples.
The documentation build checks page structure and references. It establishes
neither FreeCAD execution nor railway or output acceptance. Code excerpts retain
the upstream [GPL-3.0-or-later notice][notice].

[revision]: https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf
[controls]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L3651-L3825
[row-modes]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4949-L5017
[row-handlers]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4797-L4862
[export-wrapper]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/core_export_policy.py#L18-L67
[b16-adapters]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L1127-L1150
[b16-binding]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L1458-L1499
[euler-displacement]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L55-L117
[centre]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L124-L138
[solver]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L322-L403
[euler-core]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L829-L1004
[sides]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L1202-L1211
[prepare]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L1214-L1400
[prepare-result]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L1402-L1423
[preparation-contract]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/contracts/phase7-track-preparation.md
[preparation-fixture]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_phase7_track_alignment_preparation.py#L126-L181
[euler-fixture]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_phase1_alignment.py#L83-L120
[extensions]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L1426-L1473
[stationing]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L1992-L2023
[handedness]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/contracts/phase7-alignment-handedness.md
[host-preparation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40962-L41102
[spacing-check]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41023-L41058
[platform-displacement]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L406-L469
[platform-solver]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L584-L817
[platform-core]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L1007-L1199
[radius-confirmation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41060-L41096
[native-output]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L9642-L9682
[exact-transition]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/application/transition_exact.py#L143-L160
[preparation-tests]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_phase7_track_alignment_preparation.py
[platform-tests]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_phase7_platform_transitions.py
[preparation-evidence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-09-20-phase7-track-preparation-regression.md
[notice]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/NOTICE.md
