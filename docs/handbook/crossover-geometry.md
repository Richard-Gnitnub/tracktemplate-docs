<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted for the TrackTemplate developer handbook, 2026-10-24.
-->

# How crossover geometry and preflight work

A crossover connects two railway tracks through two turnouts and a connecting
road. TrackTemplate must place each turnout on its own host centreline and
join their branch roads. A visually plausible connector does not establish
that the **complete** arrangement satisfies the requested minimum resulting
radius. The two mapped turnout roads can be tighter than the connector.

This chapter follows the **Crossovers** tab from inputs and
**Preview geometry diagnostics** to the solver, analytical radius decision,
current-preview signature, native FreeCAD construction and edit recovery.
It explains current B16 behaviour rather than repeating the wiki's sequence
of experiments. Read [C10 turnout placement and editing](turnout-placement-and-editing.md)
for the natural turnout geometry, its host station and its separate object roles.

**Source revision:** [TrackTemplate `7965bfc4671668f889c1f43fb8336c5146c3f5cf`][revision].
The large inherited B15 host still owns the GUI, connector search, C10
construction and document object creation. B16 binds a
[`CrossoverPreflightAdapter`][preflight] around its solver, builder, editor
and diagnostics, and makes the [pure complete-radius decision][radius]
in `tracktemplate.domain.crossover`. The normal GUI is a composed host
workflow, not a standalone public crossover-construction API.

## Two hosts mean two separate station systems

Open **REA C10 turnout and crossover manager...** and select the
**Crossovers** tab. Its Host Track A and Host Track B selectors refer to
generated centrelines, not to arbitrary screen coordinates. The chosen Host A
chainage is the primary placement input. The solver derives a separate toe
chainage on Host B. Both chainages are in **millimetres from the start of
their own host's ordered centreline, increasing in that host's travel direction**.
A Host B station of 1,590 mm cannot be interpreted as a position along
Host A or as a lateral spacing.

The main input families are:

| Input or action | What it controls |
| --- | --- |
| Host A and Host B | The two identified, generated centrelines and their live sampled position/heading data. |
| Host A reference chainage | Where the first C10 is placed on Host A. Host B placement is solved from the required connection. |
| Arrangement | Facing or trailing crossover orientation and the associated directions along the hosts. |
| Handing | Selected or automatic turnout hand; local left/right relates to each turnout's direction of travel. |
| Track gauge and design flangeway | Parameters for the natural C10 turnout geometry. |
| Minimum resulting radius | Lower bound to check against *both mapped turnout roads* and the connecting road. |
| **Preview geometry diagnostics** | Run the current analytical solver and show geometry and feasibility findings without committing a crossover. |
| Create, edit, apply, cancel, remove | Managed crossover lifecycle actions. They need a current result and have different document/transaction effects. |

The host and arrangement selectors are explained here by function; do not
confuse the source's button labels or its current editor enablement with a
released FreeCAD Addon interface. The manager also supports an extension
journey from an existing turnout. The full forward/reverse conversion of
stored identities has its own [documentation issue][conversion-issue].
[Retained manager and actions][gui]; [current preview binding][composition]

### Follow the coordinates into the two C10s

The first turnout starts with the natural C10's local coordinates, where
`local_x = 0` is its switch toe and `local_y` is its lateral branch offset.
The retained mapping uses the Host A position, tangent and chosen facing/
trailing orientation to place those local points in FreeCAD XY coordinates.
The solver then places the second C10 on Host B using **Host B's** ordered
centreline, local heading and orientation. A curve or Euler (clothoid)
transition in either host changes the transformed turnout road.

The solver connects the resulting branch-road endpoints. Its retained
search for the second toe examines candidate positions and connector
families against endpoint positions, directed tangents, occupancy and
local-route restrictions. A connecting road must be feasible as a
continuous route; the solver is not simply drawing a straight segment
between two selected screen points. The resulting structure includes
Host A/B station data, resolved toe chainages, turnout orientations and
hands, C10 dimensions and a connector calculation.
[Retained solver][solver]; [turnout mapping](turnout-placement-and-editing.md#from-a-natural-c10-to-a-curved-host)

That separation has an important consequence: **the same numerical chainage
on the two hosts does not mean the same location or heading**. The
correspondence comes from solving the railway geometry. The solver also
checks the occupied host intervals of the two full C10 modules, not just
the toe points, and checks conflicts with existing managed trackwork.
[Retained solver and occupancy][solver]

## Test the whole railway route before constructing shapes

The original B14 preview could accept a connector whose radius met the
request even if one mapped turnout road was too tight. The
[bounded historical witness][contract] records that difference.
B16 instead asks a single analytical question:

\[
R_{\mathrm{complete}} =
\min(R_{\mathrm{turnout\,A}}, R_{\mathrm{turnout\,B}},
R_{\mathrm{connector}})
\]

Every value here is a *sampled resulting radius in millimetres*; a `None`
component means straight, not zero radius. The complete decision accepts
the request when no component is curved, or when the smallest finite
component radius is **at least** the requested minimum.

The following is an exact excerpt from
[`complete_radius_decision`][radius], after input validation:

```python
values = (
    turnout_a_radius_mm,
    turnout_b_radius_mm,
    connector_radius_mm,
)
result = {}
limiting = None
complete = None
for (label, key), value in zip(_COMPONENTS, values):
    if value is None:
        result[key] = None
        continue
    radius = float(value)
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("{} has no valid sampled radius.".format(label))
    result[key] = radius
    if complete is None or radius < complete:
        complete = radius
        limiting = label
```

The ordered component labels are **Host Track A turnout road**,
**Host Track B turnout road**, and **Connecting road**. This loop records
the smallest radius and the component responsible. The function then
compares that radius directly with the entered limit and returns
`accepted`, `limiting_component` and a component-specific diagnostic.
The strict decision itself does **not** use an acceptance tolerance.
The 0.000001 mm value in the historical fixture is a comparison tolerance
for its test measurements, not permission to accept a smaller radius.
[Complete decision][radius]; [fixed witness contract][contract]

### B16 adds the mapped turnout roads to the solver result

The retained connector solver provides the two resolved toe positions,
both sampled host geometries and the connector's minimum radius. The B16
adapter calculates the other two quantities *before* exact Part-shape
construction. This is an exact excerpt from its
[`solve` method][preflight]:

```python
metrics_a = module.turnout_mapping_metrics(
    solved["host_a_data"], solved["toe_chainage_a"],
    solved["orientation_a"], solved["handing"],
    solved["dimensions"],
)
metrics_b = module.turnout_mapping_metrics(
    solved["host_b_data"], solved["toe_chainage_b"],
    solved["orientation_b"], solved["handing"],
    solved["dimensions"],
)
decision = complete_radius_decision(
    metrics_a["turnout_minimum_radius"],
    metrics_b["turnout_minimum_radius"],
    solved["connector"].get("minimum_radius"),
    request["minimum_radius"],
)
```

Each calculation uses the **correct host's** data and its *own* solved toe
position. The adapter records host identities, geometry signatures,
request values and a signature of the current inputs in
`solved["complete_radius_preflight"]`. If `accepted` is false, it raises
the same component-specific error at this analytical boundary. It does
not first create a new crossover document object.
[Analytical adapter][preflight]

## Work through the two curved-host witnesses

The [frozen feasibility contract][contract] contains two measurements
from a controlled curved-host fixture. Host A is `SET-001` Main Track;
Host B is `SET-001` Track 2. The request uses **Facing crossover**,
**Automatic handing**, 16.5 mm gauge, 1.0 mm flangeway and a **600 mm**
minimum resulting radius.

| Measurement, mm | Host A toe 500.000 | Host A toe 746.298 |
| --- | ---: | ---: |
| Solved Host B toe | 1,341.223827 | 1,590.068084 |
| Mapped Host A turnout road | 606.584743 | 696.907920 |
| Mapped Host B turnout road | **540.848375** | 887.199391 |
| Connecting road | 621.083336 | **676.178669** |
| Complete minimum | **540.848375** | **676.178669** |
| Complete rule (600 mm limit) | **Reject** | **Accept** |

The left-hand example explains why a *connector-only* preview gave the
wrong answer: 621.083336 mm passes, but Host B's mapped turnout road is
only 540.848375 mm. The B16 decision rejects it with **Host Track B
turnout road** identified as the limiting component. The right-hand
example passes because **all three** components exceed 600 mm; this
time the connector is limiting. Changing Host A chainage changes the
solved Host B toe and the geometry, not merely the position of one
otherwise unchanged circle.

```{figure} ../_static/figures/crossover-complete-radius.svg
:alt: Two three-component bar comparisons at a 600 millimetre minimum radius. The first has an undersized Host B turnout road, while all three components in the second exceed the limit.
:width: 100%

The 600 mm dashed line is the requested minimum. Bars are sampled radii
from the fixed contract; they are not a plan drawing of the crossover.
```

These numerical values are **retained witness evidence**, not a new
FreeCAD run for this chapter. The historical B14 contract still describes
its earlier mismatch; the current B16 adapter and [regression tests][runtime-test]
supply the successor behaviour. The distinction matters when reading old
engineering reports.

## Why the preview has an input signature

A successful analytical result depends on more than the visible text fields.
Either host may have changed shape, an object may have been replaced, or
another turnout/crossover may now occupy an interval. Reusing the old
preview after one of those changes could construct geometry for a request
that is no longer valid.

`CrossoverPreflightAdapter.input_signature` hashes a versioned payload
containing the document identity, both host identities and *complete sampled
station, heading and point data*, the request values and current turnout/
crossover occupancy. Floats are encoded with `float(value).hex()` before
SHA-256 hashing rather than rounded to three GUI decimal places.
[Signature payload and encoding][preflight]

The adapter checks a previously supplied result before native construction.
This exact code excerpt is from [`_checked_result`][preflight]:

```python
expected = self._request_signature(request)
if decision.get("input_signature") != expected:
    raise ValueError(
        "The cached crossover preflight is stale; preview again."
    )
self.module._crossover_validate_pre_solved_result(
    pre_solved,
    request["host_a"], request["host_b"],
    request["reference_chainage"], request["arrangement"],
    request["handing"], request["track_gauge"],
    request["flangeway"], request["minimum_radius"],
)
```

The first check rejects a different current request; the inherited
validator then checks the solved data against the request. It is not
sufficient that the panel still displays `746.298` or that the planned
output filename is unchanged.

A change to Host A/B identity, a sampled point or heading, chainage,
arrangement, hand, gauge, flangeway, minimum radius, ignored entity IDs,
or occupied trackwork changes the relevant signature. A display-only
FreeCAD `Label` change is not a railway input here and need not change it.
The [FreeCAD preflight test][runtime-test] checks both cases.

### Preview and construction use the same decision

The final B16 workflow binds the adapter around
`solve_rea_c10_crossover_geometry`,
`_build_rea_c10_crossover_geometry` and
`edit_rea_c10_crossover`, and changes the panel's preview signature.
It also adds the complete-radius diagnostic above the retained
**Connector solver status** text. Connector acceptance is therefore
visible as a *subordinate* result, not the overall pass.
[Effective composition][composition]; [preflight diagnostics][preflight]

For an accepted, current preview, the build wrapper checks the signature
again before calling the inherited exact builder:

```python
checked = self._checked_result(
    request, arguments["pre_solved"],
)
arguments["pre_solved"] = checked
return self.original_builder(**arguments)
```

This is an exact excerpt from the adapter's [`build` method][preflight].
If no cached result is supplied, `_checked_result` performs a new
analytical solve. A supplied but stale result is **rejected**, not
silently treated as current. The inherited builder then creates both
C10 rail/strip constructions and the connecting road's native geometry.
The source records and resulting managed objects live in the FreeCAD
document only after the associated creation operation commits.
[Inherited build and lifecycle][build]; [preflight source][preflight]

## Editing, removal and recovery

A created crossover receives its own `XO-001`-style managed identity,
host identities, solved placement and generated objects/production
records. The panel can select it for an edit, load its saved input values,
preview a replacement and apply the change. Detailed timber resolution,
chair analysis and host integration are *downstream* decisions, not
guarantees established by crossover geometry.

The current B16 edit adapter first checks that the crossover still exists,
then checks the preview against the requested edit while ignoring the
crossover's *own* occupancy. Only after that does it call the inherited
edit operation. To protect display state on a rejected preflight, the
adapter suppresses the inherited **early** chair-display clear once and
allows normal cleanup later during the actual edit transaction.
[Edit wrapper][preflight]; [FreeCAD rejection evidence][runtime-test]

| Operation or event | Result and boundary |
| --- | --- |
| **Preview geometry diagnostics** | Analytical check and a displayed result. It does not itself commit a crossover. An invalid result cannot be used for Create. |
| Create with current accepted preview | Revalidates the result before native construction, then creates managed crossover objects inside the inherited document operation. |
| Change a host's geometry or trackwork occupancy after preview | The old signature is stale. The construction path refuses it and instructs the operator to preview again. |
| Edit with invalid complete radius | Rejected *before* exact shape construction or the edit transaction. Current derived display should not be cleared merely to reject that preflight. |
| Edit with accepted replacement | Inherited editing replaces the managed geometry/records within its document transaction and invalidates dependent analysis. The crossover identity remains the selected entity. |
| Cancel an edit | Discards the proposed GUI edit rather than applying it. It is not a FreeCAD document Undo operation. |
| Remove a managed crossover | Requires the normal selection and state checks. Host integration, if present, needs its separate removal/restoration route; do not equate deleting a preview with deleting integrated production geometry. |

The [qualified FreeCAD validator][runtime-test] includes a negative 500 mm
path, a positive 746.298 mm create path, edit rejection and signature
invalidation. The [GUI probe source][gui-proof] also checks that the
negative preview and attempted creation leave the copied fixture's
objects, persistence and Undo/Redo state unchanged, while positive creation
makes one documented transaction. Those are **retained test definitions
and evidence**, not tests newly executed in this documentation change.
They do not prove every possible host, placement, export or fit condition.

When a preview is rejected, first inspect the limiting component and the
configured radius, then recheck both hosts and the selected chainage.
After a geometry, selection or occupancy change, select
**Preview geometry diagnostics** again before Create/Apply. If a native
build or document operation fails later, inspect the transaction and
persistent objects before retrying; a successful analytical result
is not a guarantee that every FreeCAD Boolean or downstream operation
will succeed.

## What the result does not establish

- **Radius feasibility is not complete railway acceptance.** It checks
  sampled mapped turnout roads and the connector against the configured
  rule. It does not qualify timbers, special chairs, gauges after fabrication,
  physical clearances, or production output.
- **Preview is not a saved document object.** A successful preview
  describes an analytical candidate. A committed crossover has managed
  identity, geometry and records; a separate reference copy or host
  integration has different state.
- **Historical B14 evidence is not current B16 behaviour.** The
  [Phase 1 comparison][history] records the old preview/commit mismatch.
  Current B16 uses the shared preflight and its signature-bound callers.
- **Evidence is bounded.** The calculations in the table reproduce
  identified contract data. The cited FreeCAD/GUI tests are retained
  historical sources, not newly run here. No new native Part or real-GUI
  validation was performed for this chapter.

[Turnout–crossover conversion][conversion-issue], [timber analysis][timber-issue],
[host integration][integration-issue] and [production preflight][production-issue]
have separate handbook tasks. The upstream [terminology register][terms]
accepts S&C and contextual station/chainage while retaining
`switch/points/turnout`, `crossing/vee/frog` and `sleeper/timber` distinctions
as review-required. This page uses inherited labels for the observed
components; it does not approve new nomenclature or claim formal
ASD-STE100 Issue 9 conformance.

[revision]: https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf
[gui]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L37746-L39678
[solver]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L28302-L28488
[build]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L29665-L30166
[preflight]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/crossover_preflight.py
[radius]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/crossover.py
[composition]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L1257-L1318
[contract]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/contracts/phase1-crossover-feasibility.json
[history]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-07-21-b14-crossover-feasibility-characterisation.md
[runtime-test]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/freecad_validate_phase8_crossover_preflight.py
[gui-proof]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tools/freecad_bridge/run_phase8_crossover_preflight_gui.py
[terms]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md#current-contextual-register
[conversion-issue]: https://github.com/Richard-Gnitnub/tracktemplate-docs/issues/19
[timber-issue]: https://github.com/Richard-Gnitnub/tracktemplate-docs/issues/20
[integration-issue]: https://github.com/Richard-Gnitnub/tracktemplate-docs/issues/24
[production-issue]: https://github.com/Richard-Gnitnub/tracktemplate-docs/issues/32
