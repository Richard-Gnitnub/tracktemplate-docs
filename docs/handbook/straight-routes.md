<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted source excerpts and new explanation, 2026-10-24.
-->

# How straight routes use datums and curve tangents

The **Straight Track Manager** creates straight alignments in two ways. An
independent route uses an entered position and direction. A connected route
continues every track in the curve family along its entrance or exit tangent.
The distinction determines which controls are editable, where additional
tracks appear and which end of each straight meets the curve. The manager
groups one or more alignments as a route, with one configuration and identity.
These examples represent plain line track; *straight* describes its shape.

**Source:** workbench revision
[`7965bfc4671668f889c1f43fb8336c5146c3f5cf`][revision]. The B16 development
launcher uses the retained B15 dialogue and generation host. It binds
`build_straight_route` to a package calculation through a compatibility
adapter. This chapter follows that composed route, from table controls to
stored output. The [generation chapter](generate-template-set.md) explains
the surrounding document operation; [curves and spacing](curves-and-spacing.md)
supplies the curve family used below. [Current composition][composition]

## Change rows before generating geometry

The manager appears in the main `CurveInputDialog`. Its four buttons edit
dialogue state. **Generate** later reads the configurations and builds the
requested output. Changing or removing a row does not immediately remove
objects from the FreeCAD document. [Controls][controls]; [handlers][handlers]

| Control | State change and reason to use it |
| --- | --- |
| **Add independent straight** | Append and select a new independent route. It starts at `(0, 0)`, with rotation 0°, Forward travel, one track and length 600 mm. |
| **Duplicate selected straight** | Copy the selected configuration, including its connection mode. Append ` copy` to the name, allocate a fresh manager identity and select the new row. |
| **Remove selected straight** | Remove the selected configuration and select the next valid row, or leave no selection when the table is empty. |
| **Replace with curve entrance + exit pair** | Replace **all** rows with `Curve Entrance Straight` and `Curve Exit Straight`. Both are enabled, 600 mm long and have fresh identities. |

The manager permits at most twenty routes. Add returns without a change at
that limit. Duplicate also returns if there is no usable selection; Remove
returns if there is no selected row. [Limits and defaults][defaults];
[row handlers][handlers]

The pair button deliberately replaces existing rows. The recorded source
comment explains that an earlier append action left independent routes
enabled, which could obscure the intended connection test. In this exact
excerpt from `_add_curve_connection_pair`, the two configurations have
already been created from fresh defaults:

```python
self._straight_configs = clone_straight_configs(
    [entrance_config, exit_config]
)
```

The handler then clears the table and repopulates exactly two rows. This
makes the accepted straight configurations unambiguous for that connection
test. It does not preserve any replaced row's identity. [Pair handler and
recorded rationale][pair-handler]

## Understand which inputs own the geometry

**Connection** has three choices: **Independent datum**, **Curve entrance**
and **Curve exit**. Lengths and coordinates use model millimetres. **Rotation**
uses degrees; the calculation converts it to radians. **Tracks** is a total
count, including Track 1, and permits one to twenty-one independent tracks.
The Length widget permits 0.001 to 1,000,000 mm. [Widget definitions][widgets]

| Fields | Independent datum | Curve entrance or Curve exit |
| --- | --- | --- |
| **Enabled**, **Route name**, **Connection**, **Length** | Entered for this route | Entered for this route |
| **Start X**, **Start Y**, **Rotation**, **Travel direction** | Track 1 datum and heading; Forward or Reverse | Disabled; use each curve track's endpoint and travel direction |
| **Tracks**, **Track spacing**, **Parallel side** | Total count, perpendicular centre-to-centre spacing and Left/Right of travel | Disabled; inherit the complete generated curve family |
| **Template width**, **Template thickness** | Entered strip dimensions | Disabled; inherit each curve track's width and the host's curve-template thickness |
| **Create strip**, **Show centreline** | Select either output or both | Remain editable; each output also requires the corresponding source curve flag |

New independent rows use spacing 50 mm, **Left of travel**, width 32 mm and
thickness 1 mm. Both output flags are selected. The width is the template
strip's width about the centreline. It is not track gauge or a clearance
allowance. [Defaults][defaults]; [control meanings][controls]

`_update_all_straight_row_modes` disables the fields whose values the curve
owns. It sets the displayed connected track count to one main track plus the
added curve rows. Other disabled widgets retain their values: they are not
a live display of every inherited result. The connected calculation reads
the actual curve records and uses `TEMPLATE_THICKNESS`, currently 1 mm,
supplied by the host adapter. [Mode update][mode-update]; [adapter][adapter]

For a connected track, the strip flag is the route's `create_template` flag
**and** the source track's flag. The centreline uses the same rule with
`show_centreline`. Thus selecting **Create strip** on the straight row cannot
restore a strip disabled on its source curve track. A missing source flag
defaults to true in the calculation. [Connected output selection][connected]

## Calculate an independent route in its travel frame

Track 1 starts at the entered datum `O = (Start X, Start Y)`. Let `theta` be
the effective travel heading, `L` the length and `d` the track spacing. The
unit tangent `t` points along travel; the unit normal `n` points left of
travel. For **Left of travel**, the side factor `sigma` is +1; for **Right of
travel**, it is −1.

The following exact excerpt from `build_straight_route` takes a normalised
configuration. It is part of the function, not a standalone script:

```python
heading = math.radians(config["rotation_degrees"])
if config["direction"] == _STRAIGHT_DIRECTION_REVERSE:
    heading += math.pi
tangent_x = math.cos(heading)
tangent_y = math.sin(heading)
normal_x, normal_y = _left_normal(heading)
```

Reverse adds half a turn **before** the tangent and normal are calculated.
It therefore changes both the direction of travel and the physical side
described as left. The datum remains fixed. [Independent calculation][independent]

```{math}
\begin{aligned}
\mathbf{t}&=(\cos\theta,\sin\theta),
&\mathbf{n}&=(-\sin\theta,\cos\theta),\\
\mathbf{P}_i&=\mathbf{O}+\sigma i d\,\mathbf{n},
&\mathbf{Q}_i&=\mathbf{P}_i+L\,\mathbf{t}.
\end{aligned}
```

Here `i` is zero for Track 1, one for Track 2, and so on. `P_i` is the
track's travel start and `Q_i` its finish. All tracks have the same heading
and length. Each track offset is measured from Track 1. The corresponding
source excerpt sits inside the loop over `range(config["track_count"])`:

```python
offset = side_factor * track_index * config["track_spacing"]
start_x = config["start_x"] + (offset * normal_x)
start_y = config["start_y"] + (offset * normal_y)
finish_x = start_x + (config["length"] * tangent_x)
finish_y = start_y + (config["length"] * tangent_y)
```

The calculation returns just these two endpoints for each alignment, with
the same heading at both. It has no curve sampling loop. Independent
rotation is also independent of the main curve's turn direction; changing
that curve's handedness does not mirror the independent datum.
[Alignment record][record]; [host preparation order][host-order]

## Work through Forward and Reverse

For this example, leave optional formation, sectioning and assembly features
off. Keep **Production export** off: the current composed Core export
explicitly rejects enabled straight routes during its dependency inventory.
This is a limit of that export route, even though the retained host contains
straight production records. Document generation and export admission are
separate steps. [Current export restriction][export-scope]

1. Select **Add independent straight**.
2. Set **Route name** to `Datum example`.
3. Set **Start X** to 100 mm and **Start Y** to 200 mm.
4. Set **Length** to 600 mm and **Rotation** to 0°.
5. Set **Tracks** to 2 and **Track spacing** to 50 mm.
6. Select **Left of travel** and **Forward**.
7. Keep width 32 mm, thickness 1 mm and both output flags selected.
8. Select **Generate** to request the route alongside the main dialogue's curve
   family in the generated set.

The formula gives tangent `(1, 0)` and left normal `(0, 1)`. For the comparison,
reopen the manager and change only **Travel direction** to **Reverse** before
generating again. The effective heading is then pi radians:
the tangent becomes `(-1, 0)` and the left normal becomes `(0, -1)`.

| Direction | Track | Start `(X, Y)`, mm | Finish `(X, Y)`, mm |
| --- | --- | --- | --- |
| Forward | 1 | `(100, 200)` | `(700, 200)` |
| Forward | 2 | `(100, 250)` | `(700, 250)` |
| Reverse | 1 | `(100, 200)` | `(-500, 200)` |
| Reverse | 2 | `(100, 150)` | `(-500, 150)` |

```{figure} ../_static/figures/straight-route-direction.svg
:alt: Two plan views with identical axes. Forward tracks run right from X 100 to 700, with Track 2 fifty millimetres above Track 1. Reverse tracks run left from X 100 to minus 500, with Track 2 fifty millimetres below Track 1. Track 1 starts at the same datum in both views.

The fixed datum and travel-relative offset produce different physical
centrelines. Both panels use the same axes and equal X/Y scale. The diagram
shows centreline arithmetic, not template edges or a FreeCAD result.
```

Reverse constructs a new route from the same datum. It does not merely swap
the endpoints of the previously generated Forward route. This explains both
the move to negative X and Track 2's move below Track 1.

The table and figure are independently calculated documentation examples.
Displayed coordinates are rounded; floating-point sine at pi can leave a tiny
residual. The [numerical record](../_static/figures/straight-route-example-values.json)
retains the unrounded values, source revision and evidence limits. These
calculations were checked for this chapter; this GUI sequence was not newly
executed in FreeCAD. See [figure regeneration](../development.md#regenerate-the-alignment-figures).

## Join the completed curve family

A connected route uses the curve's travel direction at its join. Let `J` be
that endpoint and `t` its unit tangent. The entrance straight starts behind
`J` and travels into it. The exit straight starts at `J` and travels away:

```{math}
\begin{aligned}
\text{Entrance points}&=[\mathbf{J}-L\mathbf{t},\ \mathbf{J}],\\
\text{Exit points}&=[\mathbf{J},\ \mathbf{J}+L\mathbf{t}].
\end{aligned}
```

For example, this exact entrance-branch excerpt follows selection of the
source track's `join_point` and `heading`:

```python
remote_point = _straight_point(
    join_point[0] - (config["length"] * math.cos(heading)),
    join_point[1] - (config["length"] * math.sin(heading)),
)
points = [
    remote_point, _straight_point(join_point[0], join_point[1]),
]
```

The point order preserves travel from the entrance straight, through the
curve, and onto the exit straight. Each connected route receives every curve
alignment in the source order. It inherits their individual positions and
widths, so the disabled independent spacing value does not reposition them.
[Connected branches][connected]

The join uses the **completed** curve endpoint. Before it builds straight
routes, the host adds common straight extensions to the curve family and
applies the selected turn direction. The extensions bring the entrance ends
to a shared X coordinate and the exit ends to a shared projection along the
exit tangent. Those extensions are derived automatically from the curve
family; they are not a 600 mm straight-manager setting.
[Common extension calculation][extensions]; [host extension call][host-extensions]

This exact excerpt from the host's main generation path shows the subsequent
order. `all_alignments` already contains those common extensions:

```python
for alignment in all_alignments:
    mirror_alignment_for_turn(alignment, turn_sign)
    alignment["total_length"] = polyline_length(alignment["points"])

straight_route_results = build_straight_routes(
    straight_configs,
    all_alignments,
)
validate_connected_straight_routes(
    straight_route_results,
    all_alignments,
)
```

The connected calculation therefore inherits any reflection used for a
right turn. Its join may be beyond the bare Euler or circular core endpoint.
Connection validation runs before native production preparation and before
the transaction that removes recognised old output. [Host order][host-order]

### Continue the two-track curve example

Use the [matched-spacing example](curves-and-spacing.md#a-two-track-comparison):
main radius 600 mm, main Euler length 600 mm at each end and total turn +90°.
The Outside track uses **Euler - match spacings**, with 50 mm entry spacing,
55 mm curve spacing and 50 mm exit spacing. Its radius is 655 mm and its
retained solved Euler length is approximately 559.410 mm at each end.
Keep both curve widths at 32 mm and both output flags selected.

Select **Replace with curve entrance + exit pair**. The manager now contains
two routes, each 600 mm long. Each route contains the two curve tracks, so
there are four straight alignments in total. Their disabled **Tracks** cells
show 2. Keep Production export and the optional features off as above.

The curve example's circle centre is approximately `(297.517, 624.778)` mm.
Its Outside core starts at `(19.504, -50.000)` mm, but the automatic entry
extension brings its first point to `(0, -50)` mm. At the other end, the
automatic extension brings the Outside track to the main track's exit
projection. The connected route joins those extended points:

| Connected route and track | Travel start `(X, Y)`, mm | Travel finish `(X, Y)`, mm |
| --- | --- | --- |
| Entrance — main | `(-600.000, 0.000)` | `(0.000, 0.000)` |
| Entrance — Outside | `(-600.000, -50.000)` | `(0.000, -50.000)` |
| Exit — main | `(922.295, 922.295)` | `(922.295, 1522.295)` |
| Exit — Outside | `(972.295, 922.295)` | `(972.295, 1522.295)` |

These are independent calculations rounded to 0.001 mm, using the previous
chapter's retained solved length and Euler equations, then the common-end
and straight-route equations above. They are not coordinates measured from
a new FreeCAD run. The entrance heading is 0 radians; the exit heading is
pi/2 radians. Thus each entrance travels along positive X and each exit
along positive Y. The resulting 50 mm separation follows the curve family's
end spacing, rather than the independent straight row's disabled fields.
[Curve numerical record](../_static/figures/alignment-example-values.json);
[extension equations][extensions]

## Follow the adapter, identity and document result

`_straight_values` collects all manager rows, including disabled routes.
`_straight_row_config` reads each row and preserves its existing manager ID
when available. The main dialogue returns those configurations for Generate.
The surrounding workflow remembers accepted values before geometry work;
reopening can therefore use remembered inputs ahead of stored document
settings. [Row readers][row-readers];
[generation input lifecycle](generate-template-set.md#what-values-collects-and-what-is-remembered)

The current `_StraightRouteAdapter` normalises each configuration through
the host's `clone_straight_config`. For connected routes, it projects curve
endpoints, headings, original point/heading counts, names, widths and output
flags into neutral Python values. Interior FreeCAD vectors do not cross this
calculation boundary. The package function returns XY pairs; the adapter
turns only the new straight points into `App.Vector(x, y, 0.0)`. It creates
no document objects and does not mutate the source curve vectors.
[Adapter implementation][adapter]

An enabled route returns `route_id`, `name`, `connection_mode`, `config`,
`alignments` and `length`. A disabled route returns `None` and is omitted
from the generated route list. Its configuration remains available in the
manager's collected settings. Each alignment records its two points,
constant headings, width, thickness, flags and source alignment name where
applicable. Its length is the Euclidean endpoint distance. The returned
`config` is the normalised dictionary supplied to the domain call.
[Result construction][record]; [route calculation][route]; [host collection][collection]

Station on each straight alignment starts at zero at its first point and
increases along travel to its length at the second point. For the connected
example, entrance station 600 mm is at the curve join; exit station zero is
at the curve join. Those origins are separate from station on the curve.
[Retained geometry and station assertions][station-tests]

Route identity is derived from the manager ID:

```python
route_id = "straight-{}".format(config["manager_id"])
```

The route's display name is separate. Duplicating a row allocates a new ID;
renaming a normal existing row preserves it. The host also repairs duplicate
IDs on its local cloned route configurations before calculation. That local
repair does not rewrite the caller's original configuration list.
[Row identity][row-readers]; [duplicate handling][collection]

For the unsectioned examples, `prepare_straight_routes_production` prepares
native geometry before document replacement. A strip boundary places edges
half the width to either side of the two centreline points, closes the
rectangle and extrudes it by the thickness. Each enabled strip becomes a
separate `Part::Feature`. Each enabled centreline becomes a separate wire,
lifted to `template_thickness + CENTRELINE_LIFT`; the lift is 0.02 mm.
[Shape construction][native-shapes]; [production preparation][production];
[document objects][objects]

The generated set has `Straight Tracks [SET-…]` and
`Straight Track Templates [SET-…]` groups. Objects carry set and generator
metadata, `RouteID`, `RouteName` and per-track roles. The settings object
stores `StraightTrackConfigurationsJSON`, `StraightRouteCount`,
`StraightTrackCount` and `StraightTrackSummary`.
These are generation settings and derived objects; the separate canonical
[transition editor](transition-edit.md) has its own state ownership.
[Groups][groups]; [route metadata][metadata]; [stored settings][settings]

Optional formation, sectioning and assembly calculations use the prepared
straight routes but need their own explanations. The
[coverage map](../gui-coverage.md#alignments-and-generated-template-sets)
tracks those chapters. The shared generation chapter covers
[replacement ownership](generate-template-set.md#set-identity-and-replacement-ownership)
and [commit and visible results](generate-template-set.md#commit-stored-properties-and-visible-results).

## Reject inconsistent connections before replacement

`build_straight_route` rejects an enabled route with neither output flag
selected. Its message says that the route must create a strip, a centreline,
or both. A connected route also needs curve alignments with at least two
points and matching point/heading counts. The tracks must share a common
tangent direction at the selected end. [Calculation checks][route]

The separate `validate_connected_straight_routes` checks the complete
calculated family. It requires the expected track count and two points for
each straight. It compares the joined endpoints and headings, then checks
which side of the join contains the remote point. Independent routes bypass
this connected-route check. [Validator][validation]

| Check | Source numerical limit | What it detects |
| --- | --- | --- |
| Straight length | Greater than `1.0e-8` mm | Degenerate alignment at the calculation boundary; the GUI minimum is higher |
| Joined endpoints | Error no greater than `1.0e-7` mm | A displaced join |
| Heading difference | Wrapped angular difference no greater than `1.0e-10` rad | Different tangent directions, with angles compared modulo a full turn |
| Remote-point projection | Below `-1.0e-8` mm at the entrance; above `1.0e-8` mm at the exit | A straight placed on the wrong side of its join |

For example, an entrance route could have the correct joined endpoint and
heading values but place its remote point ahead of that endpoint. The dot
product of `remote - join` with the curve tangent would be positive, so the
projection check rejects it. These are numerical consistency limits, not
physical manufacturing tolerances. The functions expect their documented
normalised records; they are not a general validator for arbitrary malformed
Python dictionaries. [Straight-route contract][route-contract];
[connection-validation contract][validation-contract]

The connected-validator diagnostics explicitly state:
`No existing generated objects have been removed.` That matches their
placement before production preparation and the generation transaction.
Later failures have different boundaries. Native shape construction can
reject an unclosed boundary, null face or null solid. Once the transaction
starts, the exception handler attempts an abort; it does not guarantee that
every possible host failure can be rolled back.
[Transaction boundary](generate-template-set.md#failure-and-undo-limits)

The current Core export restriction is later still: export runs after the
generation commit. An export refusal can therefore leave a successfully
generated document without exported files. Keep that distinction when
diagnosing a straight-route result. [Post-commit export path][post-commit]

## Evidence and implementation limits

The [retained straight-route regression record][route-evidence] reports 117
standalone comparison cases, 120 qualified native vector/caller cases and
real-GUI independent and connected create/edit journeys. Those journeys
checked metadata, object order, identities, station values, replacement,
Undo/Redo and copied-document save/reopen. They also recorded rejection
before removal and recovery after an injected later error. The inherited
Undo/Redo procedure used **three steps**; it does not establish one
transaction for every later utility.

The [retained connected-validation record][validation-evidence] reports 71
comparison/native cases and a connected create/edit/reject/save/reopen
journey. It checks the caller's validation position and preservation of the
document on rejection. The relevant validators are
[`validate_phase7_straight_route.py`][route-tests] and
[`validate_phase7_connected_straight_validation.py`][validation-tests], with
their separately recorded FreeCAD checks.

These are historical results at their recorded candidates. This chapter
adds source inspection at the named revision and independent numerical
examples. It does not add a new FreeCAD run, full B-rep or export-byte
equivalence, general performance acceptance, or acceptance of every optional
formation, sectioning and assembly combination. The upstream contracts and
evidence continue to own those limits.

[revision]: https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf
[composition]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L1152-L1170
[controls]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L3839-L3936
[handlers]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L5187-L5278
[defaults]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L537-L767
[pair-handler]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L5197-L5230
[widgets]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L5062-L5148
[mode-update]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L5152-L5185
[adapter]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L493-L551
[independent]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L1558-L1605
[connected]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L1606-L1684
[record]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L1488-L1528
[route]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L1531-L1700
[extensions]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L1426-L1473
[host-extensions]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41004-L41030
[host-order]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41098-L41118
[row-readers]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L5027-L5060
[collection]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L8393-L8404
[native-shapes]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L9634-L9683
[production]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L11799-L11814
[objects]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41747-L41816
[groups]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L41663-L41702
[metadata]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L6920-L6940
[settings]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L21734-L21861
[validation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py#L1703-L1789
[route-contract]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/contracts/phase7-straight-route.md
[validation-contract]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/contracts/phase7-connected-straight-validation.md
[export-scope]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/core_dependency_inventory.py#L164-L167
[post-commit]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L42667-L42715
[route-evidence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-09-09-phase7-straight-route-regression.md
[validation-evidence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-09-26-phase7-connected-straight-validation-regression.md
[route-tests]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_phase7_straight_route.py
[validation-tests]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_phase7_connected_straight_validation.py
[station-tests]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_phase7_straight_route.py#L509-L559
