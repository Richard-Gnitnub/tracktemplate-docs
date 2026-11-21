<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted for the TrackTemplate developer handbook, 2026-11-21.
-->

# Model timber support and the lightweight 2D chair layout

A chair can sit on a rail–timber support point while a corner of its rotated
base extends beyond the timber. TrackTemplate calculates bounded model-only
side extensions from that transformed envelope, then checks a lightweight
2D layout against the effective support. The workflow preserves the recorded
prototype timber reference. It does not solve a timber-end overhang by making
the timber wider. [Support calculation][support-calculation];
[effective timber transformation][support-transform]

Read [Chair-position analysis](chair-analysis.md) first for logical positions,
source assignments and the earlier analytical footprint. This chapter follows
**Prepare model timber support**, **Build 2D chair layout** and their display
controls. The subsequent construction of export chair bodies has a
[separate documentation issue][solids-issue].

**Source revision:** [TrackTemplate
`7965bfc4671668f889c1f43fb8336c5146c3f5cf`][revision]. The retained B15
macro supplies the final support/layout functions, panel and display. B16
replaces the logical analysis signature and an inner analysis-reuse operation;
it does not replace the support/layout reuse predicates described here.
The host version is **`10.2A8A7B15`**, the solid/support schema is **2**, and
the final 2D representation revision is **2**.
[Host loader][host-loader]; [B16 installation][b16-install];
[schema][schema]; [representation revision][representation-revision]

The source labels `S1`, `S1J`, `ordinary` and `joint` identify inherited
implementation cases. They do not resolve the register's support taxonomy,
provisional S1 designation or independent prototype identification. A passed
envelope check does not establish measured chair–rail physical fit or
production acceptance. [Terminology states][terms];
[chair evidence and physical-fit meanings][chair-terms]

## Follow the explicit support and layout controls

Open **REA C10 turnout and crossover manager...**, choose **Turnouts** or
**Crossovers**, and select a managed entity. Enable **Show specialist and
maintenance controls**. The group titled **Chair analysis, model support
and 2D layout** contains the controls below.
[Manager entry][manager-entry]; [crossover controls][crossover-controls];
[turnout controls][turnout-controls]; [panel construction][panel]

| Control | When the specialist panel enables it | Operation |
| --- | --- | --- |
| **Prepare model timber support** | Selected configuration; analysis is neither missing nor stale. | Calculate or reuse the bounded support state. |
| **Build 2D chair layout** | Effective support status is clear or applied. | Validate the compact plan and construct or reuse its display. |
| **Show 2D chair layout** | Matching 2D display objects exist. | Show or hide the group and its layers. |
| **Build 3D chairs for export** | Effective 2D layout status is validated. | Invoke the separate detailed-body operation. |

These are the final refresh conditions. Current analysis need not have every
assignment resolved: the specialist support button excludes only missing or
stale analysis. The final status line reports chair positions, model support,
2D layout and 3D export chairs, followed by **Production ready: No.**
[Final enablement and status line][panel-refresh]

For an explicit run, use this sequence:

1. If geometry or support settings changed, use the specialist **Analyse
   chair positions** control to store a current analysis.
2. Select **Prepare model timber support**. Read any blocking reason before
   trying the layout stage.
3. When support is clear or applied, select **Build 2D chair layout**.
4. Inspect the support outlines, failure outlines and unresolved positions.
   Use **Show 2D chair layout** to change their visibility.

The panel handlers pass the selected entity identity and pending settings to
`prepare_chair_model_support` or `build_and_validate_chair_2d_layout`, then
refresh the parent and panel. B15 wraps the handlers for action measurement.
The layout handler also makes the display visible after either a fresh build
or a reuse return. [Handlers and final bindings][handlers];
[measurement bindings][measurement-bindings]

### Keep the guided route distinct

The guided support step also excludes incomplete assignments, conflicts and
critical conflicts. Crossover support/layout steps require inactive host
integration; turnout steps require no active edit. **Run next safe step**
uses its own analysis → support → layout sequence and stops on blocked support
or failed 2D fit. It does not automatically construct optional export chairs.
[Guided crossover conditions][guided-crossover];
[guided turnout conditions][guided-turnout]; [safe-step callbacks][safe-step]

The separate guided row labelled **Analyse chair positions** retains an older
callback that can reach physical-chair generation once analysis is current.
The [analysis chapter's callback explanation](chair-analysis.md#the-guided-button-has-a-different-retained-callback)
traces that discrepancy. Therefore the explicit export button's 2D gate must
not be described as a universal gate on every inherited 3D route.

## Distinguish the three planar representations

| Representation | Construction | What it controls |
| --- | --- | --- |
| Analytical footprint | The analysis stage places its envelope along the timber axes. | Logical analysis findings and a read-only support recommendation. |
| Transformed support rectangle | The physical-plan stage transforms the source-dimensional base rectangle using the rail support point and gauge-side orientation. | Bounded side extensions, support containment and the later envelope checks. |
| Decorative 2D plan symbol | The final renderer places cached rounded bases and detail wires at the instance position and rotation. | The visible lightweight representation. It does not control widening or validation. |

The first representation belongs to [analytical footprint construction](chair-analysis.md#understand-the-analytical-footprint-and-findings).
The later two share placement data but have different geometry and purposes.
The final display property `Chair2DValidationEnvelope` says:

> Separate exact transformed source-dimensional support rectangle; decorative symbol never controls validation or timber widening

Here, “exact” describes the retained calculation's transformed rectangle.
It is not a claim about independently accepted prototype dimensions or
manufactured output. [Instance transformation][instance];
[final representation metadata][display-metadata]; [chair evidence][chair-terms]

This distinction matters at a rounded corner. A decorative base may appear
clear of a timber edge while the rectangular validation envelope still
overhangs it. The validation uses the envelope even when its complete outline
is not drawn as an ordinary display layer; critical findings add red envelope
outlines. [Final display construction][display]

## Build the compact plan from current inputs

Both public operations first obtain the selected configuration, stored
analysis, normalised settings and current rail/timber records through
`_chair_generation_context`. The retained context rejects missing or stale
analysis. Its final wrapper also recalculates the analysis input signature
using the requested settings. A mismatch raises:

> Chair settings have changed since the stored analysis. Analyse chair positions again before preparing model support, building the 2D layout or creating export chair solids.

This check prevents a pending support-setting change from silently using an
older analysis. Accepting the settings dialogue alone does not persist those
settings; see [settings and reanalysis](chair-analysis.md#set-model-scale-inputs).
[Retained generation context][generation-context];
[final settings/signature guard][generation-guard]

The compact plan separates supported instances from `analytical_only`
records. At this revision, a supported instance requires a confirmed
assignment, an eligible source family and code (`1` or `7`), a source-classified
footprint, and usable rail/timber and orientation data. Deliberate omissions
and deferred special assignments do not become separate bodies. Failed
eligibility retains a reason in the analytical-only list.
[Eligibility][eligibility]; [instance construction][instance];
[plan assembly][plan]

The plan is ordinary data: instances, analytical-only records, support
adjustments, settings and signatures. Its historical name
`_chair_build_solid_plan` does not mean that this call constructs a Part solid.
The support and layout operations reuse that plan before any later detailed
body construction. [Plan assembly][plan]; [layout operation][layout-operation]

### Place the support rectangle in the timber frame

The source body dimensions locate the base relative to the rail centreline.
The base need not be symmetric about the support point. The instance derives
an outward axis opposite the gauge normal and a perpendicular local Y axis.
For each local corner, this source excerpt performs the planar transform:

```python
corners.append([
    centre[0] + local_x * outward[0] + local_y_value * local_y[0],
    centre[1] + local_x * outward[1] + local_y_value * local_y[1],
])
```

`centre` is the rail support point, not the base rectangle's centroid.
The resulting corners become `physical_footprint_polygon`. The instance
also retains the axes, rotation, source identities and body dimensions.
This excerpt needs the dimensions and orientation checks in its containing
function; it is not a standalone example. [Local dimensions][dimensions];
[transformation and returned instance][instance]

The fit helper projects each transformed corner relative to the timber centre
onto the timber's length and width axes. It then measures the four signed
clearances with this source excerpt:

```python
near_end_clearance = min(length_values) + half_length
far_end_clearance = half_length - max(length_values)
approach_side_clearance = min(width_values) + half_width
exit_side_clearance = half_width - max(width_values)
```

A positive value means the extremity lies inside that edge; a negative value
means overhang. In this calculation, approach and exit identify the negative
and positive timber-width sides. Near and far identify the negative and
positive timber-length ends. These signs belong to the stored timber axes,
not an assumed screen direction. All four distances use model millimetres.
[Final fit helper][fit-measurements]

## Calculate bounded side extensions

The support settings come from the normalised chair-analysis settings.
The UI exposes a **Model support edge margin** (default **0.15 mm**),
**Maximum automatic extension per side** (default **2.0 mm**) and two enabled
defaults: **Calculate model timber support allowances** and **Apply small
model-only timber widening automatically**. The rounding increment is an
implementation constant of **0.05 mm**, not a dialogue field.
[Settings and normalisation][settings]; [settings dialogue][settings-dialogue];
[rounding constant][rounding]

These are inherited model-policy values. The lineage register calls them a
project derivation and requests manufacturing/structural rationale and export
evidence. Treat them as the documented implementation settings, not proven
manufacturing limits. [Model-support policy lineage][support-policy]

For each supported instance, the calculator uses this source excerpt:

```python
approach_required = max(0.0, margin - float(fit.get("approach_side_clearance") or 0.0))
exit_required = max(0.0, margin - float(fit.get("exit_side_clearance") or 0.0))
near_end_required = max(0.0, -float(fit.get("near_end_clearance") or 0.0))
far_end_required = max(0.0, -float(fit.get("far_end_clearance") or 0.0))
```

The side requirements include the requested margin. The end requirements
record actual overhang only; they do not add the minimum timber-end preference.
The calculator groups instances by timber identity and takes the maximum
requirement independently on each side. Several chairs on one timber therefore
share one widening record rather than adding their requirements together.
[Requirements and grouping][support-calculation]

It rounds each grouped side requirement upwards. The complete source helper is:

```python
def _chair_round_model_support_extension(value):
    """Round a positive support extension upwards to a stable printable step."""
    amount = max(0.0, float(value or 0.0))
    if amount <= 1.0e-9:
        return 0.0
    step = float(CHAIR_MODEL_SUPPORT_INCREMENT_MM)
    return float(math.ceil((amount - 1.0e-12) / step) * step)
```

The small subtraction offsets the value at a step boundary before the ceiling
operation. It does not establish a manufacturing tolerance. The helper needs
the module's `math` import and rounding constant. [Rounding implementation][rounding]

The calculator compares the larger rounded side requirement with the
configured **per-side** limit, allowing the source comparison tolerance
`1.0e-9`. It does not compare the total width increase with that limit.
When automatic application is enabled, an over-limit side prevents both
side extensions for that timber. Requirements and chair identities remain
in the adjustment record even when application is refused.
[Rounding, limit and applied fields][support-calculation]

Application requires both support-recommendation and automatic-application
settings. The preparation stage separately blocks required widening when
automatic application is off. There is an inherited edge case: with
recommendations off but automatic application still on, the calculator can
retain required yet unapplied widths while preparation reports clear support.
A later layout check can expose the unsupported envelope. Disabling either
checkbox is therefore not a reliable shorthand for “blocked”.
[Calculator switches][support-calculation]; [preparation decision][prepare]

### Preserve the prototype and derive an effective outline

For applied approach extension `a` and exit extension `e`, the transform uses
these relationships:

```text
effective width = original width + a + e
centre shift along the width axis = (e - a) / 2
```

The centre shift allows asymmetric widening. Extending the exit side alone
leaves the approach edge in place. The transform scales transverse coordinates
and preserves longitudinal coordinates. It updates the effective outline,
support polygon and edge segments, then rebuilds the collision hull and bounds.
The near/far end segments can become wider, but their longitudinal positions
do not move. [Effective transformation][support-transform]

The adjusted record stores `prototype_width`, `prototype_centre` and
`model_support_adjustment`. It preserves the original source record and its
prototype reference. The final B15 application helper copies only adjusted
records; it returns unchanged timber records directly. These effective records
serve validation and display. Preparing support does not replace the source
timber solids. [Transformation metadata][support-transform];
[final application helper][support-application]; [preparation transaction][prepare]

`unresolved_near_end_extension` and `unresolved_far_end_extension` remain
separate findings in the adjustment data. This operation widens supports; it
does not lengthen them or settle the required railway support arrangement.
[Support requirements][support-calculation]

## Worked example: one skewed envelope

This is a fully declared, independent arithmetic fixture. It uses the pinned
code-1 source dimensions and synthetic rail/timber placement. It is not a
FreeCAD run or a complete turnout/crossover recipe. The accompanying
{download}`figure tool <../../tools/render_chair_support_figure.py>` uses
standard-library rational arithmetic and reproduces the saved SVG without
importing TrackTemplate.

### Declare the inputs and local dimensions

Take one confirmed, supported source-labelled code-1 position, with no deferred
assignment or deliberate omission. There is one timber, one intended straight
rail, no neighbouring rails and no second chair. Leave key direction unresolved;
the example makes no production-readiness claim.

| Input | Declared value |
| --- | --- |
| Timber centre, width axis, length axis | `(0, 0)`, `(1, 0)`, `(0, 1)` |
| Timber width and length | `4 mm` and `30 mm`; outline corners `(−2, −15)`, `(2, −15)`, `(2, 15)`, `(−2, 15)` |
| Chair support point `C` | `(3/5, 0) mm = (0.6, 0) mm` |
| Rail tangent `t` | `(4/5, −3/5)` |
| Gauge normal `g`; outward axis `o` | `(−3/5, −4/5)`; `(3/5, 4/5)` |
| Chair local Y axis | `(−4/5, 3/5)` |
| Intended rail centreline | Endpoints `C − 10t` and `C + 10t`, in millimetres |
| Named gauge and outer faces | Centreline endpoints plus `0.45g` and minus `0.45g`, respectively |
| Support policy | Both switches on; margin `0.15 mm`; limit `2.0 mm` per side; increment `0.05 mm` |
| Other relevant source defaults | Position tolerance `0.20 mm`; timber-end preference `0.50 mm`; advisory skew threshold `5°`; rail-fit clearance `0.04 mm` per side; overlap-area tolerance `0.0025 mm²`; rail-interference clearance `0.02 mm` |

The axes have unit length and are perpendicular. The supplied chair tangent
matches the intended rail exactly. Its skew relative to the timber-width axis
is about **36.87°**; that is distinct from a mismatch between chair and rail
tangents. This planar fixture supplies no Z coordinate because it constructs
no display or solid. [Orientation extraction][gauge-normal];
[instance checks][instance]; [rail/tangent validation][validation-rail];
[default settings][settings]

The retained scale is `76.2`, so the code's `25.4 / 76.2` gives
`1/3` model millimetre per prototype inch. With the fixed rail-head width
`0.90 mm`, `gauge_face_x = −0.45 mm`. For code 1, the local support rectangle
therefore has:

```text
x minimum = −0.45 − 5.25/3 = −11/5 mm = −2.2 mm
x maximum = −0.45 + 9.25/3 = 79/30 mm ≈ 2.633333 mm
y minimum / maximum = −4/3 mm / +4/3 mm
```

These are source-derived example dimensions, with the provenance limits
already stated. In particular, the local rectangle is asymmetric about the
rail support point. [Scale constant][scale]; [fixed profile][profile];
[body dimensions][dimensions]

### Transform, measure, round and widen

Applying `P = C + local_x × o + local_y × local_Y` gives these corners in
the source's order. Decimal values are rounded for reading; the figure tool
keeps exact fractions.

| Corner | X (mm) | Y (mm) |
| --- | ---: | ---: |
| A | `26/75 ≈ 0.346667` | `−64/25 = −2.560000` |
| B | `487/150 ≈ 3.246667` | `98/75 ≈ 1.306667` |
| C | `167/150 ≈ 1.113333` | `218/75 ≈ 2.906667` |
| D | `−134/75 ≈ −1.786667` | `−24/25 = −0.960000` |

The initial approach clearance is **0.213333 mm**; exit clearance is
**−1.246667 mm**. The near and far end clearances are **12.44 mm** and
**12.093333 mm**. The exit side requires:

```text
raw requirement = 0.15 − (−1.246666…) = 419/300 mm ≈ 1.396667 mm
rounded extension = 0.05 × ceiling((419/300) / 0.05) = 1.40 mm
```

The approach side already has more than the requested margin, so its extension
is zero. The larger rounded requirement, **1.40 mm**, is within the **2.0 mm**
per-side limit. The effective width becomes **5.40 mm** and its centre moves
to **`(0.70, 0) mm`**. Its width edges become **−2.0 mm** and **+3.4 mm**.
The new exit clearance is **0.153333 mm**, while the approach clearance and
both end clearances remain unchanged.

For comparison, the earlier centred, timber-aligned analytical rectangle at
the same support point gives approach/exit clearances of **1.266667 mm** and
**0.066667 mm**. It cannot substitute for the rotated rectangle in this
calculation. [Analytical dimensions][analytical-dimensions];
[analytical placement][analytical-placement]

```{figure} ../_static/figures/chair-support-example.svg
:alt: Three synthetic support cases: a bounded exit-side extension, an over-limit extension, and a shorter timber with an unresolved end overhang. The rotated validation envelope is separate from the schematic decorative symbol.
:width: 480px

Independent plan geometry for the declared fixture. The decorative symbol is
schematic; the rectangular envelope supplies the calculated clearances.
```

### Change one input to exceed the limit

Move the support point and its rail/face records together from `C.x = 0.6 mm`
to **`1.25 mm`**. The centre remains exactly on its intended rail. The maximum
envelope X becomes **3.896667 mm**, so the exit clearance becomes
**−1.896667 mm**. The raw requirement **2.046667 mm** rounds to **2.05 mm**,
which exceeds the **2.0 mm** limit.

For this timber, `limit_exceeded=True` and `applied=False`; both applied side
extensions are zero. The effective timber remains **4 mm** wide with its
original centre. Source inspection predicts blocked support preparation and
no new 2D layout or 3D chair body. The operation still commits the blocked
support result and resets an older layout, as explained below.
[Per-timber limit decision][support-calculation]; [preparation operation][prepare]

### Keep the side extension but shorten the timber

Return to `C.x = 0.6 mm` and change only the timber length to **5.5 mm**.
Its ends now lie at **−2.75 mm** and **+2.75 mm**. The side calculations still
give the allowed **1.40 mm** exit extension. Near-end clearance becomes
**0.19 mm**, but far-end clearance is **`−47/300 mm ≈ −0.156667 mm`**.

The support adjustment records `unresolved_far_end_extension=47/300 mm`.
Width-only widening leaves that overhang in place. Preparation does not use
the unresolved end requirement as its blocking condition, so this case can
reach layout validation. In the isolated fixture, the source predicates
identify both `CHAIR_BODY_EXTENDS_BEYOND_TIMBER` and
`CHAIR_BODY_UNSUPPORTED`. Those are **two critical findings for one chair**,
not two failed chairs. [Preparation decision][prepare];
[containment and unsupported-edge checks][validation-support]

Source inspection predicts a created layout with failed status, red chair
and effective-timber outlines, and `fit_validated=False`. This differs from
the over-limit case, where layout construction cannot proceed. A positive
end clearance below the configured preference would instead produce an
advisory finding. [Layout result and commit][layout-operation];
[failure rendering][display-failures]; [end-clearance advisory][validation-support]

Run the independent example from the documentation checkout:

```bash
python tools/render_chair_support_figure.py --check-only
```

This checks the declared arithmetic and byte-for-byte SVG reproduction.
The floating-point production helper has the small boundary tolerances shown
above; the example's rational calculation does not execute that helper.
No upstream validator, FreeCAD transaction or GUI action runs in this example.

## What support preparation commits

On a reuse miss, the preparation operation classifies the plan's adjustments
as exceeded, applied or required. It uses this source excerpt:

```python
status = (
    CHAIR_MODEL_SUPPORT_STATUS_BLOCKED if (exceeded or disabled_required) else
    CHAIR_MODEL_SUPPORT_STATUS_APPLIED if adjusted else
    CHAIR_MODEL_SUPPORT_STATUS_CLEAR
)
```

The blocked reasons are either required automatic widening being disabled or
a required side extension exceeding the limit. The stored support state
includes adjustments, counts, maximum/limit values, rounding increment and
signatures. It records `prototype_timber_references_changed=False` and
`rail_geometry_changed=False`. [Support state][prepare]

The operation then opens a document transaction. It removes an earlier 2D
display, marks existing chair-solid status properties stale and hides that
object, writes the support state and a **not built** layout reset, recomputes,
and commits. **A blocked support result follows this transaction too.**
Its `prepared` field is false, but the diagnostic state is still stored.
Exceptions after the transaction opens attempt an abort and propagate.
[Preparation transaction][prepare]; [solid-stale helper][solid-stale]

The panel warning includes **“No 2D layout or 3D chair object was committed.”**
Read that as no **new** layout or chair body: it does not mean the document
was untouched. Existing bodies remain with stale status properties and hidden
visibility. This helper does not itself rewrite their stored physical-state
JSON. [Panel warning][handlers]; [solid-stale assignments][solid-stale]

An adjustment's `applied` flag describes the effective-support plan. Even a
blocked multi-timber plan can contain other eligible adjustments with that
flag set. It does not prove that original timber solids were modified.
[Adjustment flags][support-calculation]; [preparation transaction][prepare]

## Validate and retain a useful 2D result

On a reuse miss, **Build 2D chair layout** requires stored support, rejects
blocked support, and compares the current plan signature with the support
signature. Missing support asks the operator to prepare it first; a changed
plan asks for preparation again. The inherited blocked-state diagnostic says
the limit was exceeded, even though disabled automatic widening can also
cause the blocked state. [Build prerequisites][layout-operation]

The validator applies effective timber records and checks the compact plan.
Its relevant checks include:

| Check | Meaning in this retained validator |
| --- | --- |
| Timber/rail records and centre containment | The instance still refers to available support and its centre lies on that support within the configured tolerance. |
| Rectangle containment and signed clearance | The transformed envelope stays within the effective support; a short positive end clearance can be advisory. |
| Intended rail and tangent | The centre projects within tolerance of the assigned rail and its orientation matches that rail. |
| Gauge orientation and jaw gap | Orientation is usable and the source body leaves room for the fixed Code 75 rail-foot envelope. |
| Neighbouring rail and chair envelopes | The source rectangle does not reach an incompatible rail or overlap another chair beyond the configured area tolerance. |

These are source geometry checks, not measured fit of a printed component.
The `physical_fit_failure_count` name is inherited; its value counts critical
findings, including support-envelope failures.
[Support checks][validation-support]; [rail/interface checks][validation-rail];
[overlap and result aggregation][validation-result]; [physical-fit meaning][chair-terms]

The layout operation chooses its result with this source excerpt:

```python
validation = _chair_validate_solid_plan(plan, rails, timbers, settings)
failure_count = int(validation.get("physical_fit_failure_count") or 0)
status = CHAIR_2D_LAYOUT_STATUS_FAILED if failure_count else CHAIR_2D_LAYOUT_STATUS_VALIDATED
```

It then creates the display, marks existing 3D objects stale, writes the
layout state, recomputes and commits **whether the fit result is validated
or failed**. A validation finding is a recorded outcome; an exception is the
path that attempts transaction abort. The panel reports **2D chair fit needs
review** when failures remain. [Layout transaction][layout-operation];
[panel result handling][handlers]

This explains why a red layout can remain visible while **Build 3D chairs for
export** is disabled. That button requires the validated layout status. The
underlying 3D operation also validates its plan and rejects critical findings
before constructing solids. Its complete workflow remains separate.
[Export-button enablement][panel-refresh]; [3D pre-construction check][solid-guard]

### Read the final display layers

The final B15 renderer uses one group and batched `Part::Feature` objects for
non-empty layers. It constructs Part wires and compounds, without constructing
detailed chair bodies. Its final definition replaces two earlier display
implementations in the retained file.
[Feature helper][feature-helper]; [final display][display]

| Visible layer | Content |
| --- | --- |
| Amber support outlines | Effective outlines for timbers with applied widening. |
| Pale-blue rounded bases | Cached source-labelled `S1`/`S1J` plan bases. |
| Darker-blue details | Rail seats, source `S1` jaws/ribs, rail-foot lines, and a key indication only where its direction is resolved. |
| Red failure outlines | Transformed support rectangles for critically affected chair IDs and effective outlines for affected timber IDs. |
| Magenta crosses | Analytical-only positions with an available source position, excluding deliberate omissions. |

The symbol cache uses representation revision, chair code, rail profile ID
and rounded rail-fit clearance. Placement copies/positions the cached shapes
using each instance's centre and rotation. Decorative shape detail does not
change the support calculation. [Canonical symbols and placement][symbols];
[final layers][display-layers]; [representation metadata][display-metadata]

Unresolved special/unsupported positions and unresolved key directions have
their own counts and readiness blockers. They do not themselves increase the
critical-fit count. Consequently, **2D chair layout and fit validated** can
coexist with unresolved positions. Every layout still stores
`detailed_chair_solids_generated=False` and `production_ready=False`.
[Counts and blockers][validation-result]; [layout state][layout-operation]

## Follow signatures, persistence and reuse

The plan hashes its schema/prototype revision, selected entity, analysis
signature, fixed rail profile, physical/support settings, analytical-only
records and support adjustments. For hashing, each supported instance is
reduced to its identity, code, centre, base Z, angle and transformed corners.
Coordinates/Z use six decimal places; angle uses eight.
[Plan signature payload][plan-signature]

| State field | Saved value |
| --- | --- |
| Support `source_analysis_signature` | Analysis `geometry_signature` |
| Support `support_signature` | Plan `solid_signature` |
| Layout `source_analysis_signature` | Analysis `geometry_signature` |
| Layout `support_signature` | Stored support `support_signature` |
| Layout `layout_signature` | Plan `solid_signature` |

These links connect analysis, support and layout. B16's analysis signature
includes support settings, while excluding five display flags and
`cache_enabled`. The earlier chapter explains its
[current-input signature](chair-analysis.md#decide-whether-the-stored-analysis-is-current).
[Support fields][prepare]; [layout fields][layout-operation];
[B16 signature definition][analysis-signature]

The workflow-state writer updates the selected configuration/catalogue and
the combined analysis result. It writes `ChairModelSupportStatus`,
`ChairModelSupportResultJSON`, `Chair2DLayoutStatus` and
`Chair2DLayoutResultJSON`, and clears the complete-solids, final-validation
and production-ready summary flags. These are document properties and
catalogue state; this operation does not automatically save an `.FCStd` file.
[State writer][state-writer]; [configuration writer][configuration-writer]

### Effective status is separate from display existence

Effective support status follows missing/stale analysis and the stored
source-analysis signature. Effective layout status follows support status
and its stored analysis/support signature relationships. Neither function
checks whether the display objects still exist.
[Effective-status functions][effective-status]

| Saved outcome | Exact status text |
| --- | --- |
| Support missing / stale | `Model timber support not prepared` / `Model timber support is stale` |
| Support clear / bounded width applied | `No model timber widening required` / `Bounded model timber widening prepared` |
| Support blocked | `Model timber widening is blocked` |
| Layout missing / stale | `2D chair layout not built` / `2D chair layout is stale` |
| Layout validated / failed | `2D chair layout and fit validated` / `2D chair layout has production-critical fit failures` |

The first clear-support label is the source's status wording; retain the
two-switch exception described earlier when interpreting it.
[Status constants][status-constants]; [preparation decision][prepare]

### The final B15 reuse predicates are deliberately specific

Both public wrappers perform the current generation-context check first.
The support wrapper then uses this complete source predicate:

```python
reusable = (
    bool(normalised.get("cache_enabled"))
    and str(state.get("macro_version") or "") == MACRO_VERSION_NUMBER
    and str(state.get("source_analysis_signature") or "") == str(analysis.get("geometry_signature") or "")
    and str(state.get("status") or "") in (
        CHAIR_MODEL_SUPPORT_STATUS_CLEAR,
        CHAIR_MODEL_SUPPORT_STATUS_APPLIED,
        CHAIR_MODEL_SUPPORT_STATUS_BLOCKED,
    )
)
```

A hit returns a copied outer dictionary with `unchanged_result_reused=True`.
It avoids the underlying preparation's metadata writes, layout reset,
transaction and recompute. **Blocked support can be reused.** The predicate
does not independently rebuild/compare the support signature or validate
every stored schema/identity field. These are B15 support guards, not B16's
stricter unchanged-analysis guards. [Final support reuse][support-reuse]

The layout wrapper additionally requires matching macro/source-analysis
values, both layout signatures equal to the support signature, a validated
**or failed** layout status, some tagged 2D objects, and exactly one layout
group at representation revision **2**. Its decisive display checks are:

```python
and bool(_chair_2d_objects(doc, kind, entity_id))
and _chair_layout_group_representation_current(doc, kind, entity_id)
```

This is an excerpt from the larger predicate, not standalone Python.
It does not inspect every expected child layer, visibility or shape. A
remaining group can satisfy the first check; a build action is therefore
not guaranteed to repair every missing child. An entirely removed display
or an old group revision prevents reuse and falls through to construction.
[Group revision check and final layout reuse][layout-reuse]

A hit returns `unchanged_result_reused=True` and `display_cache_reused=True`
before constructing wires. The returned flags are not automatically persisted.
The panel handler still makes the existing layout visible, so the application
early return does not imply that the complete button action changes nothing.
[Layout reuse][layout-reuse]; [panel handler][handlers]

The compact-plan cache is a separate, eight-entry session cache. Its key
includes document identity, entity identity, analysis signature, rounded
physical top Z and relevant fit/support settings. It returns the same cached
plan object and does not itself test `cache_enabled`. The canonical symbol
cache is separate again. [Plan cache][plan-cache]; [cache bound][cache-bound];
[symbol cache][symbols]

On layout reuse, stored `validation_time_ms` and the group's
`Chair2DDisplayBuildTimeMs` describe the earlier work. The latter measures
display construction before document recompute. They are not fresh timings
for the reused action; B15's action wrapper supplies separate wall/CPU and
cache/recompute observations. [Validation timing][validation-result];
[display timing metadata][display-metadata]; [action measurement][measurement]

## Change visibility, clear display and recover

**Show 2D chair layout** changes visibility on existing tagged objects. It
does not reconstruct missing layers, validate currentness or write analysis
settings. Panel refresh checks the box when any relevant feature is visible.
The guided **Show 2D layout** control likewise enables only when display
objects exist, although its callback contains a missing-display fallback.
[Visibility operation][visibility]; [panel refresh][panel-refresh];
[guided display callback][guided-display]

**Clear temporary chair display** composes analytical-marker, separate
unresolved-marker and 2D-layout cleanup. It retains logical analysis, nested
support/layout state and physical chair bodies. A cached validated status
can therefore remain after its display disappears. Use **Build 2D chair
layout** to reconstruct an entirely removed current display when support
remains eligible. [Original cleanup][clear-analysis];
[unresolved cleanup][clear-unresolved]; [final 2D cleanup][clear-layout];
[layout reuse guard][layout-reuse]

**Remove generated chair solids** has a different scope: it removes physical
solids and separate unresolved markers, resets physical state and retains
the lightweight layout and its nested cached states. Its physical-state
write also changes shared summary fields, so this does not preserve every
support-related aggregate unchanged. [Solid removal][remove-solids];
[physical-state writer][physical-state]

| Observed condition | Recovery supported by this route |
| --- | --- |
| Analysis or requested settings are stale | Reanalyse with the intended settings, then prepare support and build the layout. |
| Side widening is blocked | Inspect the required side values and stored reason. Resolve the geometry or settings deliberately, then reanalyse and prepare again. |
| Support-plan signature changed | Prepare current support before rebuilding the layout. |
| Layout contains red outlines | Inspect its findings and affected chair/timber IDs. Correct the input cause, then repeat the dependent stages. |
| Display is hidden | Show the existing layout; visibility does not change its validation result. |
| Entire display was cleared | Build again with eligible current support; cached status alone does not recreate geometry. |

These recovery paths follow the currentness guards and callbacks above.
Raising an automatic limit is a model-policy choice, not evidence that the
result meets an accepted manufacturing requirement. [Generation guard][generation-guard];
[layout prerequisites][layout-operation]; [support-policy evidence gap][support-policy]

## Evidence and implementation limits

The numerical fixture and SVG reproduction were executed independently with
standard-library Python. All macro excerpts and predicted branches were
checked against the recorded source. No FreeCAD operation or upstream
validation tool was executed for this chapter.

| Pinned source or retained evidence | What it covers | Boundary |
| --- | --- | --- |
| [B15 standalone checks][standalone-checks] | Display batching/symbol reuse; synthetic rotated support and limit cases; compact-plan and operation reuse. | Source/stub checks; some context and display predicates are replaced by fixtures. |
| [B15 FreeCAD smoke test][freecad-smoke] | Real Part symbol validity, placement, compound creation and reuse without detailed-prototype-cache growth. | Headless symbol scope; not the complete GUI workflow. |
| [Retained B14-to-B15 acceptance][retained-acceptance] | The declared `XO-001` real-panel support/layout/reuse path and save/reopen checks. | Historical checkpoint `7379eb468ec3cb4821388b37994c32b94a8c2230`, isolated FreeCAD 1.1.1 GUI and one preserved crossover recipe. |

The retained report records unchanged layout reuse without new objects or a
document recompute and preserves its own semantic/identity evidence. Its
timings were not accepted performance budgets, and its scope does not qualify
all Undo, export or whole-product behaviour. It does not execute the synthetic
example above. [Retained results][retained-results];
[timing limits][retained-limits]; [coverage boundary][retained-coverage]

The later B16 analysis evidence must not be transferred to this chain: its
fixture explicitly does not prepare the validated 2D layout, and the analysis
persistence characterisation excludes qualification of the B15
support/layout/solid sequence. [B16 fixture boundary][analysis-evidence-limit];
[persistence-characterisation boundary][persistence-limit]

Live requirements, runtime qualification and output acceptance remain with
their upstream owners. Formal ASD-STE100 Issue 9 and TT-DOC-001 conformance
are not verified.

For a code change, start with the owning functions below and retain the final
runtime bindings:

| Responsibility | Source entry |
| --- | --- |
| Side requirements and effective support | [`_chair_physical_model_support_adjustments`][support-calculation] and [`_chair_transform_timber_for_model_support`][support-transform] |
| Support preparation and layout transaction | [Underlying operations][prepare] and [layout build][layout-operation] |
| Currentness, saved state and reuse | [Effective status][effective-status], [state writer][state-writer], [final support/layout wrappers][support-reuse] |
| Symbols, overlays and metadata | [Canonical symbols][symbols] and [final display constructor][display] |
| GUI entry and B16 composition | [Final panel bindings][handlers], [measurement wrapper][measurement-bindings] and [B16 installation][b16-install] |

[revision]: https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf
[solids-issue]: https://github.com/Richard-Gnitnub/tracktemplate-docs/issues/23
[terms]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md#L52-L68
[chair-terms]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md#L188-L214
[host-loader]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/b15_workflow_host.py#L159-L208
[b16-install]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L1219-L1258
[schema]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44030-L44043
[representation-revision]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L47448-L47456
[manager-entry]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4631-L4641
[crossover-controls]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L38050-L38083
[turnout-controls]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L39902-L39928
[panel]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46537-L46558
[panel-refresh]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46560-L46591
[handlers]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46594-L46643
[measurement-bindings]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L47794-L47815
[guided-crossover]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46764-L46806
[guided-turnout]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46840-L46882
[safe-step]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46887-L46963
[generation-context]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L45221-L45234
[generation-guard]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46092-L46102
[eligibility]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44479-L44495
[instance]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44498-L44554
[plan]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44738-L44814
[dimensions]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44409-L44457
[fit-measurements]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L43374-L43404
[settings]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44108-L44186
[settings-dialogue]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L45654-L45710
[rounding]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44558-L44568
[support-policy]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/lineage/phase1-s1-core-lineage.json#L715-L741
[support-calculation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44570-L44656
[support-transform]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44659-L44720
[support-application]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L47857-L47871
[gauge-normal]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44383-L44406
[scale]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L489
[profile]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44064-L44078
[analytical-dimensions]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L36051-L36078
[analytical-placement]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L36363-L36374
[prepare]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46231-L46307
[solid-stale]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44351-L44366
[layout-operation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46427-L46486
[validation-support]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44850-L44916
[validation-rail]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44917-L44962
[validation-result]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44963-L45028
[solid-guard]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L45237-L45261
[feature-helper]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46319-L46334
[display]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L48123-L48283
[display-failures]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L48154-L48204
[display-layers]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L48206-L48231
[display-metadata]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L48237-L48269
[symbols]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L48028-L48120
[plan-signature]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44777-L44814
[analysis-signature]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/application/chair_analysis_signature.py#L9-L66
[state-writer]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46189-L46228
[configuration-writer]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L45137-L45149
[effective-status]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46154-L46186
[status-constants]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46055-L46069
[support-reuse]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L47874-L47896
[layout-reuse]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L47899-L47937
[plan-cache]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L47818-L47854
[cache-bound]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L47448-L47456
[measurement]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L47561-L47661
[visibility]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46489-L46507
[guided-display]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46663-L46721
[clear-analysis]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L36961-L36981
[clear-unresolved]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44322-L44348
[clear-layout]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46113-L46139
[remove-solids]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L45451-L45491
[physical-state]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L45152-L45188
[standalone-checks]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_b15.py#L224-L341
[freecad-smoke]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/freecad_validate_b15.py#L21-L68
[retained-acceptance]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-07-19-b14-to-b15-chair-acceptance.md#L21-L101
[retained-results]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-07-19-b14-to-b15-chair-acceptance.md#L103-L135
[retained-limits]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-07-19-b14-to-b15-chair-acceptance.md#L137-L161
[retained-coverage]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-07-19-b14-to-b15-chair-acceptance.md#L208-L217
[analysis-evidence-limit]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/freecad_validate_chair_analysis_signature.py#L361-L364
[persistence-limit]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-07-21-b14-chair-analysis-persistence-characterisation.md#L156-L167
