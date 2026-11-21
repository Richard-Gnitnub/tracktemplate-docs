<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted for the TrackTemplate developer handbook, 2026-11-21.
-->

# From rail–timber support to current chair analysis

A rail needs support at the appropriate timber positions. In a turnout or
crossover, the required support also depends on the rail's function, the
switch or crossing region, and any support shared with another rail.
TrackTemplate records those relationships as logical chair positions. It
assigns source-labelled chair families, retains unresolved special positions
and draws analytical envelopes for clearance checks. Detailed chair–rail
fit requires its own geometry and evidence.
[Assignment implementation][assignment]; [physical-fit terminology][chair-terms]

The workflow keeps several questions separate:

| Question | Evidence in the analysis |
| --- | --- |
| Where does this rail receive support? | A projected support point, rail-polyline station and stable rail/timber identities. |
| Which support does the implementation assign? | Family, code, assignment status, protected features and any deliberate shared-support omission. |
| What does the analytical envelope occupy? | A planar footprint and clearance findings, with the dimensions' source classification. |
| Can the stored result still describe this document? | Current input signature, persisted result consistency and live diagnostic-display checks. |

**Source revision:** [TrackTemplate
`7965bfc4671668f889c1f43fb8336c5146c3f5cf`][revision]. The retained B15
macro supplies the panel, extraction, assignment and display operations.
B16 replaces the signature calculation and guards a captured inner analysis
operation with a reuse adapter. Both outer B15 wrappers remain active.
The final stored analysis schema is **5**; the retained host's
`macro_version` remains **`10.2A8A7B15`**.
[Schema and host version][schema]; [B16 installation][adapter-install]

Read [C10 turnout placement](turnout-placement-and-editing.md) for the
mapped source geometry and [Crossover timbering](crossover-timbering.md)
for effective timber arrangements. This chapter covers the pinned route;
it does not establish runtime admission on a later checkout.

## Choose the explicit analysis control

Open **REA C10 turnout and crossover manager...**, select **Turnouts**
or **Crossovers**, then select a managed entity. Enable **Show specialist
and maintenance controls** to expose the group titled **Chair analysis,
model support and 2D layout**. The earlier title *Chair analysis and
physical fit* has been replaced at this revision.
[Manager entry][manager-entry]; [specialist controls][manager];
[final panel title][panel-final]

| Specialist control | What it does |
| --- | --- |
| **Analyse chair positions** | Pass the selected identity and pending settings to the final analysis operation. |
| **Chair settings…** | Edit the settings that the next analysis will use. |
| **Show chair details**; **Copy readable chair summary** | Read or copy the cached result, including its stored status and findings. |
| **Show chair-position markers** | Show cross-shaped diagnostic position markers. |
| **Show protected chair positions** | Show larger markers for mandatory positions or positions with protected features. |
| **Show analytical chair footprints** | Show closed wires from stored analytical footprint polygons. |
| **Clear temporary chair display** | Remove owned diagnostic and lightweight 2D display objects while retaining cached analysis. |

These labels and their connections come from the retained panel.
Without a selected configuration, its controls are disabled. Details and
copy additionally require a cached result. The final refresh adds model
support, layout and export statuses and still ends with **Production
ready: No.** [Panel controls and enablement][panel-controls];
[final refresh][panel-final]

The following source excerpt from `ChairAnalysisPanel.run_analysis`
captures the current display choices before calling the application:

```python
self.settings.update({
    "markers_visible": self.marker_box.isChecked(),
    "protected_markers_visible": self.protected_box.isChecked(),
    "footprints_visible": self.footprint_box.isChecked(),
    "physical_solids_visible": self.solid_box.isChecked(),
    "unresolved_markers_visible": self.unresolved_box.isChecked(),
})
analyse_entity_chair_positions(self.doc, self.entity_kind, self.entity_id(config), self.settings)
```

The selected entity supplies the identity; the panel supplies pending
settings. The handler refreshes the panel after the operation. Its final
B15 instrumentation wrapper delegates to this retained handler.
[Analysis handler][analyse-handler]; [handler instrumentation][instrumentation]

### The guided button has a different retained callback

The guided step also displays **Analyse chair positions**. For a crossover,
it requires current clear B4 timbering and inactive host integration. For
a turnout, it requires current timber geometry, enabled timber outlines
and no active edit. These guided prerequisites do not become extra guards
on the specialist analysis button.
[Crossover guided state][guided-crossover]; [turnout guided state][guided-turnout]

At this pin, the guided primary callbacks still call `_chair_guided_action`.
That helper runs analysis only for **Not analysed** or **Analysis stale**.
With current analysis, it can generate missing or stale physical chairs,
validate existing physical chairs, or return complete. The later rendering
replaced the label without replacing those two primary callbacks. Use the
specialist **Analyse chair positions** control when explicitly requesting
analysis or reanalysis. This is an observed binding discrepancy, not an
intended new workflow inferred from the label.
[Retained guided action and callbacks][guided-action];
[retained callback bindings][guided-primary-bindings]

The final **Run next safe step** has its own analysis, model-support and
2D-layout sequence. It stops on incomplete assignments, conflicts or
critical conflicts before proceeding. Its later binding does not repair
the separate guided primary callbacks described above.
[Safe-step implementation and bindings][safe-step]

## Set model-scale inputs

The settings dialogue exposes the following final defaults. Distances are
model millimetres; the skew threshold uses degrees. These are implementation
settings, not approved prototype or manufacturing tolerances.
[Defaults and normalisation][settings]; [dialogue fields][settings-dialogue]

| Dialogue row | Default | Allowed range |
| --- | ---: | ---: |
| Chair-position tolerance | 0.20 mm | 0–5 mm |
| Footprint broad-phase clearance | 0.15 mm | 0–5 mm |
| Minimum timber-end clearance | 0.50 mm | 0–10 mm |
| Maximum advisory chair skew | 5.0° | 0–30° |
| Maximum unsupported rail span | 15.0 mm | 1–100 mm |
| Code 75 rail-fit clearance | 0.04 mm per side | 0–0.50 mm per side |
| Chair body embed depth | 0.20 mm | 0–5 mm |
| Model support edge margin | 0.15 mm | 0–3 mm |
| Maximum automatic extension per side | 2.0 mm | 0–10 mm |

The shared dialogue also enables **Calculate model timber support
allowances**, **Apply small model-only timber widening automatically** and
**Reuse analysis and supported solids when signatures match** by default.
Position markers default to visible; protected markers, footprints,
physical solids and unresolved markers default to hidden. Analysis records
a read-only support recommendation with
`applied_to_production_geometry=False`.
[Settings controls][settings-dialogue]; [recommendation calculation][support-recommendation]

Normalisation fills missing defaults, converts numeric values to floats,
rejects nonnumeric, non-finite or out-of-range values, and supplies the
fixed schema and rail-profile identifiers. Settings for later physical
work remain in this normalised dictionary even though analytical position
generation constructs no chair body. [Normalisation][settings]

Accepting **Chair settings…** updates `self.settings` and sets the panel
text to **Analysis stale**. It neither runs analysis nor writes the saved
analysis settings. These values remain pending until the analysis action
uses them; a panel refresh reloads settings from the persisted
configuration. [Settings acceptance][settings-acceptance];
[settings reload][panel-controls]

## Read the effective rails and timbers

For a turnout, the final rail extractor pairs each named gauge face with
its outer face. It samples both polylines at matching fractions of their
respective lengths, averages each pair of points, then maps the resulting
centre path through the turnout placement. The record retains the named
faces, sampled points, route identity and source configuration. The
crossover route combines both turnout rail sets with offset connector
polylines. [Midline construction][midline]; [final rail extractors][rail-extractors];
[entity rail selection][rail-selection]

The centre path is sampled planar geometry. Its `rail_role` and
`supported_feature` come from separate source-name mappings. For example,
`main-side stock rail` becomes role `stock rail` and supported feature
`stock-rail support`; `vee point rail` becomes role `vee point rail` and
feature `vee nose and point-rail support`.
[Role and feature mappings][rail-roles]

Turnout timbers come from the mapped source layout. Crossover timbers come
from `crossover_timber_records`, which selects the current effective
arrangement through the B4, B3, shared-envelope and inherited routes.
Applying or removing a timber arrangement can therefore change chair
inputs even when the rails remain unchanged.
[Timber extraction][timber-extraction]; [effective crossover records][effective-timbers]

| Record data | Meaning in this calculation |
| --- | --- |
| Rail and timber stable identities | Links between source records and position records, independent of display-object names. |
| XY rail points and timber outline | Model-space support geometry in the common mapped frame. |
| Timber centre, length and width axes | Origin and directions used for support projection, skew and analytical footprint measurements. |
| Rail parent turnout/crossover and route side | Ownership and route context for source assignments. |
| Timber source identifier and support requirements | Source-region identity and route-specific protected support obligations. |
| `rail_station` | Derived distance from the first point along the selected logical rail polyline, in point order. |

The last quantity is distinct from the host centreline's chainage and the
timber's longitudinal station. Identify the owning path, origin and
direction whenever comparing them. Missing host geometry or a missing
stable entity identity prevents extraction or generation.
[Extraction guards][rail-selection]; [position generation][position-generation];
[station terminology][terms]

## Project a support point, then assign its meaning

The final `generate_chair_positions` prepares each rail's non-degenerate
segments, accumulated lengths and spatial index. For each timber it uses
the outline polygon, falling back to the collision polygon, and skips
polygons with fewer than three vertices. Padded bounding boxes reject
irrelevant rail–timber pairs. The timber centre, or polygon centroid when
needed, becomes the projection point.
[Preparation and indexing][projection-index]; [final generator][position-generation]

For each candidate segment, the projection parameter is clamped to its
endpoints. This exact source excerpt uses the prepared segment's start
`(ax, ay)` and direction `(dx, dy)`:

```python
fraction = min(1.0, max(0.0, (
    (px - float(segment["ax"])) * dx + (py - float(segment["ay"])) * dy
) / length_sq))
qx = float(segment["ax"]) + fraction * dx
qy = float(segment["ay"]) + fraction * dy
```

The helper selects among the spatial candidates by distance, accumulated
rail-polyline station and then original segment index. The selected point
must lie inside or within `position_tolerance` of the effective timber
polygon. This route produces at most one position for each eligible
rail–timber pair; it does not enumerate every intersection between rail
and timber edges or intersect curved solids.
[Prepared projection][projection]; [polygon acceptance][point-acceptance]

The position identity connects that relationship to subsequent findings.
Its complete source definition is:

```python
def _chair_position_identity(entity_id, timber_id, rail_id):
    return "{}:chair:{}:{}".format(entity_id, _chair_slug(timber_id), _chair_slug(rail_id.split(":rail:")[-1]))
```

The entity ID remains unchanged. The timber identity and final rail-name
portion become lowercase slugs with runs of non-alphanumeric characters
replaced by hyphens. Coordinates do not enter this identity. A position
can keep its identity while its point or assignment changes, so identity
alone cannot establish cache validity. The generator sorts the final
records and rejects duplicate position identities.
[Identity and slug][position-identity]; [slug definition][slug];
[sorting and duplicate guard][position-generation]

### Assignment follows route and source context

Shared timbers can inherit several support requirements. The assignment
code first matches each requirement to the rail route and any stored
support zone, then filters protected features against the actual rail
role. It recovers the source timber identifier from the direct record,
matched source requirements or stable identity. This prevents a broad
protected-timber label from assigning the same special function to every
rail across a long timber.
[Route and feature filtering][support-filter]; [source identifier][prototype-id]

The final assignment branches include these source-labelled cases:

| Source condition | Recorded assignment |
| --- | --- |
| Ordinary closure/exit support; crossover connecting rail | Initially code `1`, label `S1`; connector classification is an inference. |
| J1/J2; R1 on stock rail | Code `7`, label `S1J`, with joint support context. |
| Stock rail at S1–S7 | Code `2`, label `P`. |
| Stock rail at S8–S9 | Code `11`, label `1P/2P`. |
| Stock rail at S10–S12 | Code `12`; the catalogue label is `3P-11P`, while the assignment description names the `3P-5P` block-heel range. |
| Switch-and-closure rail at S1–S12 | Code `0`, deliberate omission: the adjacent slide or block support owns the shared support. |
| Crossing identifiers or check, wing, knuckle and vee roles | Source family/code labels with `deferred to special-chair assignment`. |

These are implementation classifications. The terminology register keeps
the S1 designation provisional and the ordinary-chair taxonomy under
review. A nonzero special-chair code does not resolve the final subtype.
[Assignment][assignment]; [code catalogue][codes]; [deferred mappings][deferred];
[terminology states][terms]; [chair-term limits][chair-terms]

After generation, pairwise clearance refinement can replace selected
closure/S13 S1 positions with L1 bridge-chair candidates. Those candidates
remain deferred even though the code sets
`assignment_complete_in_current_stage=True`. Read that Boolean together
with `assignment_status` and `special_assignment_deferred`.
[Bridge refinement][bridge]

### Key direction needs separate evidence

The final orientation function leaves the key-direction sign at zero
when the required policy or context is absent. For S1 and other ordinary
assignments, it records the following exact source text:

```python
# The FreeCAD macro does not yet store a key-direction policy, so do
# not manufacture a direction from rail station or display order.
key_orientation = "requires a configurable key-direction policy"
key_sign = 0
key_classification = CHAIR_CLASS_CONFIRM
```

S1J records direction towards the adjacent joint in principle, but needs
stored joint chainage for an exact sign. Deferred special positions need
the final subtype and keying arrangement. A confirmed assignment therefore
does not establish key direction. The retained advisory test searches for
the phrase `requires confirmation`; the S1 policy text above does not
match it, so an absent key advisory is insufficient evidence of resolution.
[Final orientation][orientation]; [retained advisory check][key-advisory]

## Understand the analytical footprint and findings

The footprint is a rectangle centred on the projected support. Its length
follows the timber length axis and its width follows the timber width
axis. The implementation measures rail skew against the timber width
axis, using the absolute tangent dot product. A deliberately omitted
shared-support position has no footprint polygon.
[Footprint construction][footprint]; [skew and omission][position-generation]

For source-labelled S1, the inherited dimensions come from this excerpt:

```python
inch = (25.4 / TURNOUT_DEFAULT_SCALE)
if family == CHAIR_FAMILY_ORDINARY:
    return 14.5 * inch, 8.0 * inch, CHAIR_CLASS_SOURCE, "REA S1"
```

Here `TURNOUT_DEFAULT_SCALE` is fixed at 76.2. The implementation's
`CHAIR_CLASS_SOURCE` label records its claimed basis; it does not itself
approve those prototype dimensions or their provenance. Several special
families instead use an explicit temporary analytical envelope.
`footprint_clearance` is stored with the result but is not added to the
rectangle's length and width.
[Dimension classes][dimensions]; [fixed scale][scale]; [recorded parameters][position-generation]

The retained validator checks missing protected support, end/side
clearance, excessive skew, analytical overlap and unsupported rail spans.
The final wrapper adjusts findings for deferred special envelopes and
read-only support recommendations. It also checks the C-switch sequence
for each parent turnout: 14 code-2, four code-11 and six code-12
assignments, plus 24 shared switch-support omissions.
[Retained checks][validation-base]; [final validation][validation-final]

An overlap involving a deferred special envelope can therefore become
`SPECIAL_CHAIR_CLEARANCE_REQUIRES_CONFIRMATION`, an advisory, rather than a
resolved physical collision. The overall **Ordinary and turnout
assignments validated** status can coexist with deferred special positions:
the final status function tests critical/conflict findings and explicit
ordinary/turnout unresolved assignments. Inspect the position-level status
and deferred count as well as that headline.
[Finding transformation][validation-final]; [final status][result-status]

## Worked example: one synthetic rail and timber

This example uses declared model-space inputs and independently checked
arithmetic. It is not captured REA geometry or FreeCAD output. It stops at
position generation and analytical clearance; the single position cannot
satisfy the complete turnout sequence checked above.

Take entity `TO-001` with one timber and one logical rail:

| Input | Declared value |
| --- | --- |
| Timber | `TO-001:timber:T1`; identifier and prototype reference `T1`; section `closure`. |
| Timber geometry | Centre `(10, 0)`; length 30 mm; width 4 mm; length axis `(0, 1)`; width axis `(1, 0)`; angle 90°. |
| Effective outline | `(8, −15)`, `(12, −15)`, `(12, 15)`, `(8, 15)`. |
| Inherited protection | Empty protected features and support requirements. |
| Rail | `TO-001:rail:main-side-stock-rail`; name `main-side stock rail`; role `stock rail`; feature `stock-rail support`. |
| Rail geometry and context | Points `(0, 4)` and `(20, 4)`; parent turnout `TO-001`; empty route side; no named face geometry supplied. |

Use the final default position tolerance of 0.20 mm, footprint clearance
of 0.15 mm, minimum end clearance of 0.50 mm and model-support edge margin
of 0.15 mm. The calculation follows the final generation, assignment and
measurement functions already linked above.

### Projection and identity

The segment direction is `(20, 0)`. From its start to the timber centre,
the vector is `(10, −4)`. The projection fraction is
**(10 × 20 + (−4) × 0) / (20² + 0²) = 1/2**.
Clamping leaves that value unchanged, giving support point **(10, 4)**.

That point lies inside the timber. Its distance from the timber centre is
4 mm, its station from the rail's first point is 10 mm, and its tangent is
`(1, 0)`. The tangent and timber width axis agree, giving 0° skew.
The identity rule produces:

```text
TO-001:chair:to-001-timber-t1:main-side-stock-rail
```

The T1 closure record receives source-labelled S1/code 1 and
`confirmed ordinary or turnout assignment`. With only one position, there
is no pair for bridge refinement. Its key-direction sign remains zero
with the configurable-policy requirement.

### Footprint and clearance

At the fixed scale, **25.4 / 76.2 = 1/3 model mm per prototype inch**.
The analytical rectangle is therefore **29/6 mm long × 8/3 mm wide**.
Its half-length is 29/12 mm along Y and its half-width is 4/3 mm along X.

| Corner in source order | Exact model coordinates | Decimal approximation, mm |
| --- | --- | --- |
| 1 | `(26/3, 19/12)` | `(8.666667, 1.583333)` |
| 2 | `(26/3, 77/12)` | `(8.666667, 6.416667)` |
| 3 | `(34/3, 77/12)` | `(11.333333, 6.416667)` |
| 4 | `(34/3, 19/12)` | `(11.333333, 1.583333)` |

The minimum side clearance is **2 − 4/3 = 2/3 mm**. The minimum end
clearance is **15 − 77/12 = 103/12 mm**, approximately 8.583333 mm.
Both overhang values are zero. The 0.15 mm support margin needs no
widening here. The recommendation is eligible under the source's
assignment/dimension gates, but `required=False` and
`applied_to_production_geometry=False`.
[Final clearance measurement][footprint-fit]; [recommendation gates][support-recommendation]

```{figure} ../_static/figures/chair-analysis-example.svg
:alt: Synthetic timber, logical rail and projected support, with an enlarged analytical rectangle and its clearances.
:width: 480px
:align: center

Synthetic model-mm geometry. The footprint is an analytical rectangle;
the figure contains no physical chair body or named rail-face geometry.
```

The independent {download}`figure and arithmetic tool <../../tools/render_chair_analysis_figure.py>`
checks the declared values and reproduces the SVG. It uses the Python
standard library and does not import the workbench. From the docs
repository root, run:

```bash
python tools/render_chair_analysis_figure.py --check-only
```

### A fitting envelope can still have a deferred assignment

Keep the same geometry but use timber `X1-A`, crossing suffix `A`, and
rail role/name `vee point rail`, with their corresponding stable IDs.
The deferred mapping selects code `24`, label `AA`, and family
`crossing-nose support`. The assignment remains deferred, mandatory and
incomplete in the current stage.
[Deferred branch][deferred]; [assignment flags][assignment]

Its temporary footprint is 29/6 × 3.5 mm, leaving 0.25 mm side clearance.
The protected interval projects the timber corners onto this rail tangent
and adds 0.20 mm tolerance: **10 + [−2, 2] + [−0.20, 0.20] =
[7.80, 12.20] mm** along the declared rail. Apparent envelope fit supplies
no final subtype or physical chair–rail fit evidence. The model-support
recommendation remains ineligible because the assignment is deferred.
[Temporary dimensions][dimensions]; [protected interval][support-zone];
[recommendation gates][support-recommendation]

## Decide whether the stored analysis is current

B16's `chair_analysis_signature` describes exact selected neutral inputs.
The host adapter normalises settings first. The helper retains rail/timber
record order, uses a format discriminator and hashes JSON with sorted
dictionary keys. It does not round coordinates or other selected values.
Missing fields remain distinguishable from fields explicitly set to
`None`. [Signature helper][signature]; [signature adapter][signature-adapter]

| Input group | Fields included in the signature |
| --- | --- |
| Identity/version | Signature format `tracktemplate:chair-analysis-inputs:1`, analysis schema and entity kind. |
| Configuration | `turnout_id`, `crossover_id`, `template_set_id`, `handing`, when present. |
| Rails | Stable identity, points, role, name, parent turnout/crossover identities, supported feature, source configuration and turnout side. |
| Timbers | Stable identity, identifier, prototype reference, centre, angles, width, length, outline/collision polygons, length/width axes, protected features, section, source configuration, support requirements and turnout side. |
| Settings | Every value supplied after normalisation except the six keys below. |

The exact excluded keys are:

```python
_EXCLUDED_SETTINGS = (
    "markers_visible", "protected_markers_visible", "footprints_visible",
    "physical_solids_visible", "unresolved_markers_visible", "cache_enabled",
)
```

Visibility controls change presentation; `cache_enabled` controls whether
reuse is allowed. Neither enters the calculation identity. Other shared
settings, including rail-fit clearance, do enter it. Stored analysis
feedback does not enter the selected configuration subset. The macro
version is checked separately by reuse eligibility.
[Selected fields and excluded settings][signature]; [version guard][reuse-candidate]

The final encoding rejects unsupported or non-finite values:

```python
encoded = json.dumps(
    payload, sort_keys=True, separators=(",", ":"), allow_nan=False,
).encode("utf-8")
return hashlib.sha256(encoded).hexdigest()
```

The helper mutates no inputs. Its format discriminator makes earlier
signature keys obsolete without changing the inherited analysis-result
schema. Equality describes these selected records and settings; it is
not a geometry or manufacturing acceptance test.
[Signature contract and encoding][signature]

### Effective status reads current records

`chair_analysis_effective_status` compares the saved signature with one
calculated from current rail/timber records and saved settings. A mismatch
or an exception during that calculation produces **Analysis stale**. If
no saved signature exists, the function returns the stored status.
[Effective status][effective-status]

Consequently, a rail edit or a different effective timber arrangement can
invalidate the analysis without every operation calling one universal
invalidator. Clearing display objects is a separate action. An explicit
invalidation helper also exists and its later wrapper marks physical
chairs stale, but that does not mean every timber or rail edit calls it.
[Invalidation helper][invalidation]; [physical-state invalidation][physical-invalidation]

The downstream chair-generation context rejects stale analysis. Its
final wrapper also checks the requested normalised settings against the
stored analysis signature. Refreshing analysis is therefore a prerequisite
when those inputs change.
[Generation-context guards][generation-guard]; [settings guard][generation-settings]

## Separate logical reuse from the unchanged-document return

A matching signature can permit reuse of calculated positions. B16's
earliest return has stricter conditions: the request, persisted result,
current records and diagnostic display must all agree. Failure to prove
that route sends the request to the retained analysis operation.
[Neutral reuse guards][reuse-candidate]; [live adapter and fallback][reuse-adapter]

### First check persisted identity and result structure

`chair_analysis_reuse_candidate` requires a turnout or crossover and a
nonempty entity ID, consistent configuration/result identities, cache
enabled, the expected integer schema and the expected macro version.
Status must be present, current and consistent between result and
configuration. The complete normalised settings dictionary must match
the request, result and configuration, **including visibility settings**.
[Candidate checks][reuse-candidate]

It then requires matching nonempty signatures, correctly typed result
containers and JSON-safe values. The summary count must equal the
position-list length. Each position needs nonempty stable chair/rail/timber
identities, footprint parameters, protected-feature data and an actual
Boolean `mandatory` value. Position identities must be unique. A current
result can contain findings; reuse preserves them rather than changing
their meaning. [Structural checks][reuse-candidate]

The live adapter also checks the settings object's persisted status,
signature and JSON settings. It then extracts the current rail and timber
records again and calculates their signature. Agreement between two
stored signatures alone is insufficient. [Live input checks][reuse-adapter]

### Then check the diagnostic display and physical-state references

The display guard checks document ownership, unique names and roles,
entity and template-set identities, group membership and non-null shapes.
In a GUI, actual visibility must match the requested flags. The qualified
GUI-less route instead requires absent `ViewObject` values.
[Presentation checks][presentation-guard]

| Requested layer | When content is required |
| --- | --- |
| Chair-position markers | Positions exist. |
| Protected markers | At least one position is mandatory or has protected features. |
| Analytical footprints | At least one position has a footprint polygon. |

The analysis group must exist, but a populated layer is required only
when both requested and relevant. If a physical-chair object exists, its
source-analysis signature, solid-signature property and non-stale state
must agree. If none exists, the cache must not claim a physical-chair
state. These are structural and state checks; they do not recalculate
every display vertex or establish physical fit.
[Presentation and physical-state checks][presentation-guard]

### Return detached data and no historical timings

Once those checks pass, the neutral helper executes this excerpt:

```python
result = copy.deepcopy(cached)
result["cache_reused"] = True
result["display_cache_reused"] = True
result["performance_timings_ms"] = {}
return result
```

The caller receives detached nested data. Editing a returned position
cannot mutate the stored result. The early route avoids metadata writes,
display construction, recompute and transaction calls; it leaves the
previously stored bytes intact. The empty timing dictionary means **no
measurements returned for this operation**, not a measured duration of
zero. The inherited summary defaults a missing total to `0.0`, which must
not be reported as a new performance result.
[Detached return][reuse-result]; [summary timing default][summary-timing];
[retained unchanged-Analyse evidence][reuse-evidence]

### Preserve the outer wrappers and understand fallback

The final call path is the instrumented panel handler, the final
`analyse_entity_chair_positions` wrapper, the physical-state wrapper,
then B16's adapter at `_A8A7B11_ANALYSE_ENTITY_CHAIR_POSITIONS`. The adapter
returns early or calls the captured original operation. B16 checks those
bindings instead of replacing every function with the same name.
[Final wrapper][outer-wrapper]; [physical wrapper][physical-wrapper];
[installation][adapter-install]; [route validation][binding-validation]

Its fallback boundary is explicit:

```python
def __call__(self, doc, entity_kind, entity_id, settings=None):
    try:
        result = self._reused_result(doc, entity_kind, entity_id, settings)
    except (AttributeError, KeyError, TypeError, ValueError, RuntimeError):
        # Unproved state follows the unchanged operation and diagnostics.
        result = None
    if result is not None:
        return result
    return self.original(doc, entity_kind, entity_id, settings)
```

An unproved shortcut is not itself an analysis failure. The inherited
operation can reuse signature-matching logical data, then open a
transaction, write metadata and update or rebuild presentation. Malformed
state still follows inherited diagnostics; fallback does not guarantee
successful repair. [Fallback and retained operation][reuse-adapter];
[inherited analysis][analysis-operation]

The outer physical wrapper can mark an existing solid stale when its
source signature differs. The final measurement wrapper records a cache
hit from `cache_reused`; even its `unchanged_reused` telemetry field derives
from that flag. That label alone cannot prove the stricter return which
preserved the document. [Physical wrapper][physical-wrapper];
[measurement wrapper][outer-wrapper]

### Compare visibility and geometry changes

| Change before an explicit Analyse | Signature | Earliest B16 return | Retained operation when needed |
| --- | --- | --- | --- |
| Inputs, complete settings, metadata and live display stay current | Same | Eligible | No fallback needed. |
| Change only one of the three analytical visibility checkboxes | Same | Declined: requested settings differ from saved settings. | Can reuse logical positions, then save settings and update or rebuild display. |
| Hide a marker directly while saved settings still request visibility | Same | Declined: live presentation disagrees. | Can reuse logical positions and restore requested visibility. |
| Delete a requested diagnostic layer | Same | Declined: presentation is incomplete. | Can reuse logical positions and reconstruct display. |
| Change a listed rail point, timber axis, identity or relevant source field | Different | Declined | Calculate a fresh logical result. |
| Change a non-excluded normalised setting, such as position tolerance | Different | Declined | Calculate a fresh logical result. |
| Disable cache reuse | Unchanged by that flag alone | Declined | Skip cache lookup, calculate and persist a fresh result. |

The table assumes the remaining configuration is valid. The first case
preserves document state; a logical cache hit in the fallback still writes
metadata. This distinction explains why unchanged geometry alone does
not establish an unchanged-document operation.
[Signature policy][signature]; [settings eligibility][reuse-candidate];
[live eligibility][reuse-adapter]; [fallback effects][analysis-operation]

## Read presentation and saved state correctly

Toggling **Show chair-position markers**, **Show protected chair positions**
or **Show analytical chair footprints** calls
`set_chair_analysis_visibility`. Existing layers receive visibility
changes. If a requested layer is missing, the helper reads cached data,
applies display choices to a local copy, rebuilds display and recomputes.
It neither persists the settings nor checks effective stale status first.
A visible footprint can therefore come from an obsolete cached analysis.
[Panel visibility handler][visibility-handler]; [display visibility helper][visibility]

**Show chair details** and **Copy readable chair summary** also read
cached data. They do not independently recalculate effective status or
prepend a live stale warning. Compare those summaries with the current
panel status, and run analysis after a relevant input change.
[Details and copy handlers][details]

### What analysis writes

When fallback reaches the retained application operation, it calculates
or selects logical data before opening **Analyse {kind} chair positions
{id}**. Inside the transaction, `_chair_write_metadata` stores
`ChairAnalysisStatus`, `ChairAnalysisSignature`,
`ChairAnalysisSettingsJSON` and `ChairAnalysisResultJSON`. It updates
entity configuration and the relevant catalogue.
[Transaction and operation][analysis-operation]; [metadata writer][metadata]

The writer explicitly retains these capability limits:

```python
updated["chair_solids_complete"] = False
updated["chair_final_validation_complete"] = False
updated["production_ready"] = False
```

These writes update the FreeCAD document; this operation does not save an
`.FCStd` file. The returned timing dictionary is completed after the
metadata write and commit, so stored timings and final returned timings
are not interchangeable measurements. B16's early-return correction
does not repair earlier recorded timing payloads.
[Metadata flags][metadata]; [operation completion][analysis-operation];
[timing evidence boundary][reuse-evidence]

On an exception, the retained operation attempts to abort the transaction
and, if it rebuilt display, attempts cleanup before re-raising. Calculations
precede the transaction and the outer physical-state wrapper runs
afterwards. These boundaries do not justify a blanket atomicity claim.
The retained tests and evidence below cover specified document/history
journeys. [Failure handling][analysis-operation]

### Clearing and rebuilding temporary display

The final clear helper composes the earlier analysis/unresolved-marker
cleanup with lightweight 2D-layout removal:

```python
def clear_chair_analysis_display(doc, entity_kind, entity_id):
    removed = _A8A7B13_CLEAR_DISPLAY_WITHOUT_LAYOUT(doc, entity_kind, entity_id)
    return removed + _chair_remove_2d_display(doc, entity_kind, entity_id)
```

It preserves cached logical analysis and physical chair bodies. The
button then requests recompute. Individual removal failures are caught
in the cleanup helpers; duplicate unresolved-marker objects can still
raise an error. [Analysis cleanup][clear-original];
[unresolved markers][clear-unresolved]; [final cleanup][clear-final];
[button handler][clear-handler]

Display construction calls that final helper too. Rebuilding a missing
analytical layer can therefore also remove unresolved and lightweight
2D-layout displays. Reanalyse for current logical results, then use the
appropriate subsequent workflow to reconstruct the required dependent
presentation. [Display construction][display-build]

## Evidence and implementation limits

The source and retained evidence below were inspected at the pinned
revision. The independent example arithmetic and figure reproducibility
were checked for this chapter. No FreeCAD operation, upstream validator
or manufacturing trial was run for this documentation change.

| Evidence | What it supports |
| --- | --- |
| [Signature input tests][signature-test]; [cache invalidation tests][signature-cache-test] | Selected inputs, excluded flags, record order, missing/null distinctions, invalid values and cache invalidation cases. |
| [Reuse test source][reuse-test] | Candidate consistency, detached returns, empty returned timings, changed settings/geometry, display checks and retained wrapper routes. |
| [FreeCAD test source][freecad-test]; [persistence cases][freecad-persistence] | Defined observations for document writes, object identities, shapes, history, display repair and save/reopen. Inspection alone does not execute these assertions. |
| [Retained B16 signature and unchanged-Analyse evidence][reuse-evidence] | Specified XO-001 and TO-001 copies, current-input extraction, preserved unchanged document state and inherited display repair in the qualified host profile. |
| [Historical B14 persistence characterisation][historical-evidence] | Earlier fixed-fixture assignment/persistence behaviour and its explicit prototype/provenance limits. It remains historical comparison evidence. |

The retained B16 reuse passage identifies the qualified profile
`linux-x86_64-flatpak-freecad-1.1.4-py3.13.15-qt6.11.2-coin4.0.10`
and states that the reuse tests ran without a visible FreeCAD window.
It records persistence and document/history behaviour for its named
copies, not a new visible-GUI run or whole-product acceptance. It gives
no acceptance for performance, physical fit or production output.
[Retained evidence][reuse-evidence]

[Model timber support and 2D layout](chair-support-and-2d-layout.md) and
[3D export-chair construction][solids-issue] remain separate workflows.
Live requirements, runtime qualification and product acceptance stay
with their upstream owners. The [terminology register][chair-terms]
does not turn source S1/L1 designations, analytical dimensions or code
tables into approved prototype definitions. Formal ASD-STE100 Issue 9
and TT-DOC-001 conformance are not verified.

[revision]: https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf
[solids-issue]: https://github.com/Richard-Gnitnub/tracktemplate-docs/issues/23
[terms]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md#L52-L68
[chair-terms]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md#L188-L214
[schema]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44030-L44043
[manager-entry]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4631-L4641
[manager]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L37616-L37635
[panel-final]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46537-L46591
[panel-controls]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L45713-L45816
[analyse-handler]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L45823-L45839
[instrumentation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L47799-L47814
[guided-crossover]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46764-L46793
[guided-turnout]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46840-L46875
[guided-action]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L45945-L45994
[guided-primary-bindings]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46040-L46045
[safe-step]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46890-L46963
[settings]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44108-L44186
[settings-dialogue]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L45654-L45710
[settings-acceptance]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L45930-L45942
[midline]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L35620-L35635
[rail-extractors]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44189-L44302
[rail-selection]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L35777-L35798
[rail-roles]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L35638-L35680
[timber-extraction]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L35801-L35843
[effective-timbers]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L30345-L30387
[projection-index]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L35882-L35976
[projection]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L35979-L36035
[point-acceptance]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L36040-L36048
[position-generation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L43458-L43590
[position-identity]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L36404-L36405
[slug]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L35577-L35579
[support-filter]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L36081-L36166
[prototype-id]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L43087-L43114
[assignment]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L43147-L43252
[codes]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L42989-L43015
[deferred]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L43122-L43144
[bridge]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L43255-L43326
[orientation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L43329-L43372
[key-advisory]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L36627-L36639
[footprint]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L36363-L36374
[dimensions]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L36051-L36078
[scale]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L485-L496
[validation-base]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L36575-L36818
[validation-final]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L43640-L43743
[result-status]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L43746-L43818
[footprint-fit]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L43374-L43404
[support-recommendation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L43407-L43455
[support-zone]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L36342-L36358
[signature]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/application/chair_analysis_signature.py#L10-L66
[signature-adapter]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L832-L843
[effective-status]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L37176-L37189
[invalidation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L36984-L36998
[physical-invalidation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44369-L44372
[generation-guard]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L45221-L45234
[generation-settings]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46092-L46102
[reuse-candidate]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/application/chair_analysis_reuse.py#L10-L76
[reuse-result]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/application/chair_analysis_reuse.py#L79-L87
[reuse-adapter]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L938-L996
[presentation-guard]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L853-L936
[summary-timing]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L37319-L37338
[outer-wrapper]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L47940-L47945
[physical-wrapper]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L45572-L45580
[adapter-install]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L1219-L1258
[binding-validation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L1501-L1591
[analysis-operation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L37192-L37314
[visibility-handler]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L45881-L45890
[visibility]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L37119-L37173
[details]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L45892-L45906
[metadata]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L36923-L36958
[clear-original]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L36961-L36981
[clear-unresolved]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L44322-L44348
[clear-final]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46124-L46139
[clear-handler]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L45919-L45928
[display-build]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L37061-L37115
[signature-test]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_chair_analysis_signature.py#L122-L202
[signature-cache-test]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_chair_analysis_signature.py#L281-L386
[reuse-test]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/validate_chair_analysis_reuse.py#L126-L373
[freecad-test]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/freecad_validate_chair_analysis_signature.py#L176-L292
[freecad-persistence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tests/freecad_validate_chair_analysis_signature.py#L590-L626
[reuse-evidence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/current/PHASE_EVIDENCE.md#L1274-L1329
[historical-evidence]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/benchmarks/2026-07-21-b14-chair-analysis-persistence-characterisation.md#L34-L85
