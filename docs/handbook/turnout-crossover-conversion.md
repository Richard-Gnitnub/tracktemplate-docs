<!-- SPDX-License-Identifier: GPL-3.0-or-later
Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
Adapted for the TrackTemplate developer handbook, 2026-10-24.
-->

# How turnout–crossover conversion preserves identities

A standalone REA C10 turnout and a managed C10 crossover are **different railway
entities**. The crossover contains two mapped turnout constructions and their
connecting road; it also has its own identity, generated geometry and
production-record entries. Conversion therefore cannot be implemented safely by
renaming the turnout's FreeCAD group or adding an untracked connecting line.

TrackTemplate provides two related GUI actions:

- **Convert selected turnout to crossover** replaces one eligible standalone
  turnout with a solved managed crossover, preserving enough of the source
  configuration to support a later reversal.
- **Convert selected crossover to turnout** chooses one constituent turnout,
  reconstructs its geometry and replaces the crossover with a standalone
  entity. It does not retain both branches.

The design intent stated in the manager is **transactional replacement with
reversible identity and source data**, subject to the geometry actually
available. An inference from the implementation is that keeping a source
snapshot avoids treating the crossover's deliberately simplified timber
references as the original turnout's exact output choices.
[Forward GUI][forward-ui]; [forward construction][forward-commit];
[reverse resolver][reverse-resolve]

**Source revision:** [TrackTemplate
`7965bfc4671668f889c1f43fb8336c5146c3f5cf`][revision]. The active
conversion handlers, geometry builders and document transactions are in the
retained B15 macro. B16's [crossover preflight adapter][preflight] guards the
underlying solver/build route used during turnout extension. These are
current internal GUI workflows, **not** promises of a stable Python API or
a finished public FreeCAD Addon. Read the separate
[C10 turnout chapter](turnout-placement-and-editing.md) and
[crossover solver chapter](crossover-geometry.md) first.

## Identify the controls and their prerequisites

Open **REA C10 turnout and crossover manager...** with a generated template
set in the FreeCAD document. Use **Turnouts** for forward conversion and
**Crossovers** for reversal. The specialist buttons are normally hidden until
**Show specialist and maintenance controls** is selected. The guided
workflow can also offer conversion as an optional final action; it delegates
to the same handlers. [GUI bindings][gui-bindings]

| Action | Eligible state and effect |
| --- | --- |
| **Convert selected turnout to crossover** | Select a recognised, complete standalone turnout. No turnout edit may be in progress; remove any existing **turnout host integration** first. |
| **Convert selected crossover to turnout** | Select a managed crossover. A crossover originally extended from a turnout automatically retains Host A. An independently created crossover prompts for **Host A** or **Host B**. |
| Reject confirmation | Leave the existing managed entity and production records in place. An in-memory candidate may already have been calculated, but no conversion transaction has been committed. |
| Confirm conversion | Commit the new entity and removal of the old one in the conversion transaction. Separate catalogue and production-record updates are part of that operation. |

The forward button calls
`TurnoutManagerDialog.begin_selected_turnout_extension`. The reverse
button calls `CrossoverManagerPanel.convert_crossover_to_turnout`.
These are the actual connected handlers, not names inferred from
the button captions. [Connected GUI callbacks][gui-bindings]

### What the forward preview tells the reader

The forward dialog first resolves an eligible neighbouring centreline.
It displays its track name, separation, Host A and Host B switch-toe
chainages, arrangement, inherited handing and the **connecting-road**
minimum radius. The subsequent builder still uses the B16
[complete-radius preflight](crossover-geometry.md#test-the-whole-railway-route-before-constructing-shapes);
the dialog's connector figure alone is not permission to generate an
under-radius turnout road.

The original turnout supplies the Host A identity, exact toe chainage,
facing/trailing orientation, handing, gauge and flangeway. The program does
**not** ask the user to type a replacement Host A toe or pick a new hand during
conversion. Its search selects an eligible second track and the crossover
solver determines Host B placement. [Resolver][forward-resolve];
[dialogue][forward-ui]

## Find the nearest **valid** neighbour

`resolve_automatic_turnout_crossover_extension` first checks that the
source turnout exists, is not integrated, refers to a current recognised
host centreline and has valid saved input values.

Each candidate Host B must be a different recognised generated centreline.
The resolver excludes an explicitly different template-set identity and uses
projection at the source toe to measure physical separation. Candidates
beyond the configured maximum separation are excluded. It sorts remaining
candidates by measured distance, then object name as a deterministic
tie-breaker.

A near track is only a **candidate**, not necessarily a valid connection.
The resolver tries the crossover solver on successive candidates. The
following exact excerpt belongs to that loop in the
[retained source][forward-resolve]:

```python
for separation, candidate_name, candidate in candidates:
    try:
        solved = solve_rea_c10_crossover_geometry(
            doc,
            host_a,
            candidate,
            toe,
            arrangement,
            handing,
            gauge,
            flangeway,
            minimum_radius,
            ignored_turnout_id=identifier,
        )
    except Exception as error:
        solver_failures.append((candidate_name, separation, str(error)))
        continue
```

`ignored_turnout_id=identifier` is necessary because the source turnout
already occupies Host A. The proposed crossover replaces it; it must not
reject itself as a conflicting turnout. The returned candidate is the
**nearest one that passes the solver**, not necessarily the closest track
in the document. If every candidate fails, the resolver returns a
diagnostic with rejected neighbours and reasons instead of changing the
document. [Candidate selection and failure][forward-resolve]

## Build the crossover, then replace the standalone turnout

After the user confirms, the forward handler calls
`extend_turnout_to_rea_c10_crossover`. It verifies the existing turnout's
required FreeCAD objects and the two host centreline identities. It maps the
source orientation to a corresponding facing or trailing crossover, then
passes the source's placement and parameters to the complete crossover
builder. The B16 wrapper checks a supplied analytical preview against the
current request and hosts before exact construction.
[Extension operation][forward-commit]; [B16 wrapper][preflight]

The crossover is not a second copy of the standalone turnout. The builder
constructs an **internal Host A turnout**, an **internal Host B turnout**
and a connector. It uses the original `TO-...` identity as Host A's
*internal constituent identity*, while allocating a new `XO-...` crossover
identity. The Host B constituent receives a crossover-derived internal
identifier. [Crossover builder][crossover-builder]

For example, the source creates this internal structure when the first
standalone turnout and crossover IDs are `TO-001` and `XO-001`:

| Entity or field | Before conversion | During the managed crossover |
| --- | --- | --- |
| Standalone turnout | `TO-001` with its own group | Original standalone group removed on commit |
| Crossover | None | `XO-001` with its own group and settings |
| Internal Host A identity | Not a separate internal crossover entity | `turnout_a_id = "TO-001"` |
| Internal Host B identity | None | `turnout_b_id = "XO-001-B001"` |
| Source reference | Original turnout configuration | `extended_from_turnout_id = "TO-001"` |
| Reversion data | Original saved options | `conversion_source_turnout_config` snapshot |
| Production records | Standalone turnout sources | Crossover sources replace the old turnout's sources |

**This is an illustrative identity assignment, not a newly executed FreeCAD
run.** The `TO-001` string inside a crossover does **not** mean the original
FreeCAD object names remain present. The operation creates new crossover
objects and removes the old standalone turnout objects in the same
transaction. The host track itself is not replaced by this standalone
conversion; a source turnout with active host integration must first be
unintegrated. [Commit and object removal][forward-commit];
[crossover object roles][crossover-objects]

### Save the original output choices

When building its own two internal C10s, the crossover uses a restricted
source-reference configuration. In particular, it initially constructs
timber references without the full standalone turnout's identity/length
text labels. This is a construction choice of the crossover route, **not**
a user instruction to discard original turnout output settings.
[Crossover builder][crossover-builder]

The forward conversion records a separate snapshot. This is an exact
excerpt from `extend_turnout_to_rea_c10_crossover`:

```python
config["extended_from_turnout_id"] = identifier
config["extension_preserved_toe_chainage"] = toe
config["extension_preserved_handing"] = handing
config["extension_preserved_orientation"] = orientation
config["extension_mode"] = "Transactional standalone-turnout replacement"
```

The same block subsequently stores:

```python
config["conversion_source_turnout_config"] = dict(original)
config["preferred_reversion_side"] = CROSSOVER_REVERSION_SIDE_A
```

The source turnout's current configuration contains its output options,
including timber outlines, centre lines, engraved timber identities,
rounded length labels and construction datums. Saving `dict(original)`
lets the reverse resolver reconstruct those options rather than assume
that the crossover's temporary constituent geometry represents the
standalone source. The source records this mechanism as a later addition;
older crossovers without the snapshot do not gain it retroactively.
[Snapshot comments and assignment][forward-commit]

After successfully building geometry in memory and checking the template-set
identity, the forward operation opens one FreeCAD transaction. It creates
the managed crossover objects, removes the source turnout's parts and group,
replaces its production-record sources, updates both the turnout and
crossover catalogues, recomputes and commits. An exception after opening the
transaction leads to an **attempted** `abortTransaction()`; it must not be
described as an infallible rollback if FreeCAD itself fails to abort.
[Forward transaction][forward-commit]

## Reverse conversion: which turnout can be restored?

Select **Convert selected crossover to turnout**. The GUI first decides
which constituent railway route the restored turnout will represent.

If the crossover contains `extended_from_turnout_id`, the resolver chooses
**Host A** automatically; that is where the original standalone turnout
came from. If the crossover was independently created, there is no
original standalone turnout to recover. The GUI therefore asks the user
to choose **Host A** or **Host B**. Cancelling that choice leaves the
document untouched. [Reverse GUI][reverse-ui]; [side selection][reverse-resolve]

This exact excerpt is from
`resolve_crossover_to_turnout_conversion`:

```python
source_turnout_id = str(crossover_config.get("extended_from_turnout_id") or "").strip()
if source_turnout_id:
    side = CROSSOVER_REVERSION_SIDE_A
else:
    side = str(keep_side or "").strip().upper()
    if side not in (CROSSOVER_REVERSION_SIDE_A, CROSSOVER_REVERSION_SIDE_B):
        raise ValueError(
            "Choose whether to keep the Host A or Host B turnout from this independently created crossover."
        )
```

For the selected side, the resolver determines the host centreline,
its **current** crossover toe chainage and orientation, and the available
saved C10 options. It validates the crossover's required source objects
and selected host before building the proposed standalone turnout in
memory. [Reverse resolution][reverse-resolve]

### Restoration fidelity is explicit

The source of the rebuilt turnout's parameters depends on what the
crossover actually stored:

| Crossover history | Output-option source | Result |
| --- | --- | --- |
| Converted from a standalone turnout **with** `conversion_source_turnout_config` | Original saved standalone configuration on Host A | Can reproduce the saved optional timber/label/datum choices, subject to a successful rebuild |
| Converted from a standalone turnout **without** that snapshot | Stored internal Host A turnout configuration | Rebuild is possible, but originally unsaved optional choices cannot be reconstructed |
| Created independently | Stored internal Host A or B configuration, as selected | Rebuilds a constituent turnout rather than restoring an earlier standalone one |

The following is an exact excerpt from
`_crossover_reversion_source_config`. It chooses the best available
configuration for the selected side:

```python
if (
    resolved_side == CROSSOVER_REVERSION_SIDE_A
    and isinstance(config.get("conversion_source_turnout_config"), dict)
):
    return dict(config["conversion_source_turnout_config"]), "complete source-turnout snapshot"
key = "turnout_a_config" if resolved_side == CROSSOVER_REVERSION_SIDE_A else "turnout_b_config"
stored = config.get(key)
```

The GUI includes the resulting **Restoration source** in its confirmation.
It does not simply announce that every conversion is perfectly reversible.
The returned source label is either **complete source-turnout snapshot**
or **stored internal crossover turnout configuration**.
[Source selection][reverse-source]; [confirmation][reverse-ui]

A related, easily missed distinction is **which historical values take
precedence after crossover editing**. The reverse resolver takes the
toe chainage and orientation from the *current crossover configuration*
before falling back to source values. Handing, gauge, flangeway and optional
output flags prefer the available source configuration. Therefore,
preserving `TO-001` as a stable identity does **not** guarantee that a later
modified crossover restores the turnout at its original chainage.
[Reconstruction field selection][reverse-resolve]

### An original identity can also be unavailable

A converted source turnout normally keeps its `TO-001` logical ID inside
the crossover record. The reverse path tries to reclaim that same ID, but
it refuses to overwrite a different standalone turnout already using it.

The guard appears in `_crossover_reversion_turnout_id`:

```python
if preferred:
    existing = turnout_config_by_id(doc, preferred)
    if existing is not None:
        raise ValueError(
            "Cannot restore turnout identity {} because a standalone turnout already uses it.".format(preferred)
        )
    return preferred, True
return "TO-{:03d}".format(_next_turnout_number(doc)), False
```

A converted turnout with its original ID still available returns the
original ID; a collision is **an error**, not silent reassignment.
An independent crossover whose internal constituent IDs do not qualify
as standalone `TO-<digits>` names receives a new available `TO-...`
identity. Internal FreeCAD object names are still newly allocated during
reconstruction. [Identity selection][reverse-identity]

## Worked round trip: which fields and records survive?

Consider an **illustrative** `SET-001` example derived from the fixed
curved-host geometry used in the
[crossover preflight witness](crossover-geometry.md#work-through-the-two-curved-host-witnesses).
The solver's documented valid Host A toe is **746.298 mm** and it
calculates Host B toe **1,590.068084 mm**. Start with standalone `TO-001`
on Host A, facing, left-hand, 16.5 mm gauge and 1.0 mm flangeway.

For this example, enable *timber outlines*, *engraved timber identities*,
*engraved rounded timber lengths* and *construction datums* on the
standalone turnout. These output choices are illustrative inputs; the
fixed radius witness alone does **not** prove a FreeCAD conversion with
this exact combination.

```{figure} ../_static/figures/turnout-crossover-conversion.svg
:alt: Three stages of turnout-to-crossover-to-turnout conversion. The original TO-001 group is replaced by XO-001 while the TO-001 logical identity and saved source settings are recorded. Reverse conversion creates a new standalone group bearing TO-001 if that identity is still available.
:width: 100%

An identity string can survive a conversion even though the original
FreeCAD source objects do not. The source snapshot carries optional
configuration, not a preserved solid.
```

| State | Standalone objects and production sources | Logical identities | Optional source settings |
| --- | --- | --- | --- |
| **1. Before** | Standalone `TO-001` group, cutting/solid/engraving sources and selected optional outputs | `TO-001` exists as standalone | Stored in `TO-001` configuration |
| **2. After forward commit** | Original standalone sources removed; `XO-001` combined crossover sources added | Managed `XO-001`, internal A identity `TO-001`, internal B identity `XO-001-B001` | Original `TO-001` configuration saved in `conversion_source_turnout_config`; crossover's internal references can differ |
| **3. After reverse commit** | New standalone turnout group and selected output sources; `XO-001` group and records removed | `TO-001` restored if free, with `restored_from_crossover_id` metadata | Rebuilt from the saved source flags when the snapshot exists |

Step 2 does **not** preserve the original `Part::Feature` objects. Step 3
builds new objects using the saved meaning and logical identity. This
matters to downstream references that use FreeCAD internal object names:
do not assume those names remain valid merely because `TO-001` has
returned. [Object construction][reversion-objects];
[forward transaction][forward-commit]; [reverse transaction][reverse-commit]

An independently created `XO-001` follows a different branch at Step 3.
Choosing Host B gives a turnout on Host B, normally with a newly allocated
standalone ID and options taken from its internal B configuration.
There is no earlier `TO-001` identity to restore from an independent
crossover. [Independent selection][reverse-resolve]

## Commit the reverse operation and restore integrated host records

The reverse GUI calls `resolve_crossover_to_turnout_conversion` **before**
its final Yes/No question. This builds and validates the candidate
turnout in memory and tells the user the selected host, identity and
restoration source. Answering **No** does not open the conversion
transaction. [Reverse GUI][reverse-ui]

On confirmation,
`convert_rea_c10_crossover_to_turnout` checks the selected crossover
identity and retained side against the prepared result, then checks
current crossover presence and that the rebuilt turnout stays in the
same template set. It creates the new turnout objects inside one
FreeCAD transaction, removes old crossover parts and groups, refreshes
both catalogues and commits. The code also records provenance fields:
`restored_from_crossover_id`,
`restored_from_crossover_side`,
`restoration_source` and
`restored_identity_preserved`. [Reversion preparation][reverse-resolve];
[transaction][reverse-commit]

If the crossover has active **host integration**, the reverse path
does **not** just delete the integrated group. It requires a reversible
integration record. It restores recorded source visibility and the
original Host A/B production entries in the same transaction, removes
integrated/crossover entries and appends the restored standalone
turnout sources. An active integration whose reversal record is missing
blocks conversion. This path differs from the forward rule, where an
*integrated source turnout* must be unintegrated before extending it.
[Reverse integration recovery][reverse-commit];
[separate host integration issue][integration-issue]

The relevant record decision inside the transaction is an exact
excerpt from `convert_rea_c10_crossover_to_turnout`:

```python
if restored_base_records is not None:
    retained = [
        record for record in restored_base_records
        if str(record.get("source_name") or "") not in old_source_names
    ]
    _turnout_write_production_records(doc, set_id, retained + list(committed["records"]))
else:
    _turnout_store_production_records(doc, set_id, committed["records"], removed_source_names=old_source_names)
```

With integration, the operation starts from the recorded original
host production entries and excludes obsolete crossover sources;
otherwise it updates the current catalogue by replacing crossover
source names. In both cases it appends the rebuilt standalone
turnout records. [Record restoration][reverse-commit]

## Failed, cancelled or stale conversion

| Situation | Code behaviour and recovery |
| --- | --- |
| No turnout selected, missing source object or integrated source turnout | Forward conversion is unavailable or raises a specific diagnostic. Restore the recognised source objects or remove turnout integration first. |
| No suitable neighbour or failed geometry on every candidate | Resolver returns an error with candidate failures. No forward conversion transaction is started. Check track identity, separation and the [complete radius decision](crossover-geometry.md). |
| User declines either confirmation | No conversion is committed. The generated in-memory candidate is discarded as a proposed result. |
| Source turnout was altered after forward preview | The B16 [signature-bound preflight](crossover-geometry.md#why-the-preview-has-an-input-signature) must match current hosts, request and occupancy before the crossover builder can reuse `pre_solved`; a stale cached result is rejected. |
| Crossover lacks a saved complete source snapshot | Reverse falls back to the internal selected-side configuration and displays that source. Original option values not recorded in the old crossover cannot be inferred. |
| Original turnout ID is now in use | Reverse raises the ID-collision error instead of overwriting that turnout. Investigate the conflicting entity before retrying. |
| Required crossover objects or selected host are missing | Reverse resolution rejects the attempt. A missing integration-recovery record also blocks an integrated reversal. |
| FreeCAD object, recompute or record update fails during a transaction | The code attempts `doc.abortTransaction()` and re-raises the failure. Confirm the document/Undo state before retrying; a failed abort is not guaranteed recovery. |

One more recovery distinction: the forward route's cached crossover
geometry is bound to B16's live input signature. The reverse GUI, by
contrast, passes a **prepared, in-memory** turnout result from the
confirmation step. Its commit function explicitly rechecks the
crossover ID, chosen side, current crossover presence and template set.
That is **not** a claim that it rehashes every source shape or performs
the forward B16 stale-preview check. If the underlying document changes
outside the modal workflow, re-evaluate before relying on an old
candidate. [Forward signature][preflight];
[reverse preparation and checks][reverse-commit]

## Boundaries and source map

These conversions reorganise current model geometry and record identities;
they do not automatically complete crossover timber resolution, qualify
chairs, integrate railway hosts or provide production output clearance.
The forward crossover initially marks timber resolution and production
readiness as incomplete. The related
[crossover timber chapter issue][timber-issue] and
[host integration chapter issue][integration-issue] own the rest of that
story. The wiki remains the development journal rather than this handbook's
source of chronology.

The upstream [terminology register][terms] accepts S&C and
centreline station/chainage within their defined contexts. It marks
*switch/points/turnout*, *crossing/vee/frog* and *sleeper/timber* as
`review-required`. This chapter uses the inherited **REA C10**,
`turnout_a_config` and source labels with their recorded meanings; it
does not approve new prototype classifications.

**Evidence:** The input and output logic above was examined at the
pinned source revision. The before/during/after identifiers and output
options are a **code-derived illustrative scenario**, not an executed
round-trip or a new FreeCAD GUI validation. A strict documentation build
cannot verify native shape fidelity, Undo on a failed abort, old-file
recovery or manufactured fit. **Formal ASD-STE100 Issue 9 / TT-DOC-001
conformance has not been verified.**

| Reader question | Owning source |
| --- | --- |
| Which controls call each conversion? | [Forward GUI][forward-ui], [reverse GUI][reverse-ui] |
| How is the neighbour found and preflight checked? | [Nearest-valid resolver][forward-resolve], [B16 preflight][preflight] |
| How are the original options and identity preserved? | [Forward snapshot and commit][forward-commit], [C10 builder][crossover-builder] |
| Which side and ID are selected on reversal? | [Reverse resolver][reverse-resolve], [source fidelity][reverse-source], [identity guard][reverse-identity] |
| Which objects and production records change? | [Forward transaction][forward-commit], [reverse object creation][reversion-objects], [reverse transaction][reverse-commit] |

[revision]: https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf
[gui-bindings]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L37988-L38020
[forward-ui]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40558-L40679
[reverse-ui]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L39532-L39659
[forward-resolve]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L29009-L29149
[forward-commit]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L29151-L29274
[crossover-builder]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L28489-L28731
[crossover-objects]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L28752-L28847
[reverse-resolve]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L29319-L29422
[reverse-source]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L29277-L29296
[reverse-identity]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L29299-L29316
[reversion-objects]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L29425-L29577
[reverse-commit]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L29580-L29663
[preflight]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/crossover_preflight.py
[terms]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/TERMINOLOGY.md#current-contextual-register
[timber-issue]: https://github.com/Richard-Gnitnub/tracktemplate-docs/issues/20
[integration-issue]: https://github.com/Richard-Gnitnub/tracktemplate-docs/issues/24
