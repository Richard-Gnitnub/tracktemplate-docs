# GUI workflow coverage

This page maps the current interface to the developer explanations still needed.
It is a source inventory, not evidence of complete GUI acceptance or a claim
that the handbook already explains every action. Use the
[authoring guide](authoring.md) to turn a row into a narrated code walkthrough.

The inventory covers workbench revision
[`7965bfc4671668f889c1f43fb8336c5146c3f5cf`][revision].
Labels, callbacks and composition were inspected in source; the GUI was not
executed for this inventory. **Not yet written** means that the intended
explanation has no handbook chapter. It does not mean the operation is absent
from the code. The linked chapters cover main generation, curve and spacing
calculations, straight routes, physical platforms, and the separate transition
editor within their stated limits.

## Read the current interface correctly

B16 composes selected package operations into the retained B15 workflow host.
`TrackTemplate.FCMacro.run_macro(launch_workflow=True)` explicitly launches that
workflow; the default `run_macro()` prepares the foundation without opening it.
The inherited `CurveInputDialog` remains the main dialogue. See the
[launcher][launcher] and [session composition][composition].

Check the final callback binding before writing a chapter. The host replaces
several chair-panel and guided-workflow methods after their first definitions;
B16 then binds selected modular operations and recovery adapters. For example,
the current chair panel adds model support and 2D layout, and renames its exact
geometry action to **Build 3D chairs for export**. The
[final panel bindings][chair-panel] and [guided bindings][guided] own those routes.

## Alignments and generated template sets

| Workflow and visible control | Current entry point and explanation | Coverage |
| --- | --- | --- |
| Generate or replace a set: **Output behaviour:** | `CurveInputDialog.values` and host `run_macro`: remembered inputs, preparation, generated identities, replacement, transaction, recompute, visible results and failure limits. [Source][generation] | [Detailed generation walkthrough](handbook/generate-template-set.md). Optional feature calculations and export publication remain separate. |
| **Main curve** and **Independent parallel-track controls** | Track add/remove/duplicate handlers, then `main_circle_centre`, `build_concentric_core` and `prepare_track_alignment`: Euler easing, circular arcs, signed turn, spacing modes, handedness, strip and centreline output. [UI][main-ui]; [calculations][alignment] | [Detailed calculation walkthrough](handbook/curves-and-spacing.md): the three modes, controls, frame, sampling and generated geometry. |
| **Straight Track Manager** | `_add_straight`, `_add_curve_connection_pair`, `build_straight_route` and connected-route validation: independent datums, parallel tracks, tangent inheritance and disabled fields. The entrance/exit-pair action replaces all straight rows with two 600 mm routes. [Source][straights] | [Detailed straight-route walkthrough](handbook/straight-routes.md): controls, Forward/Reverse arithmetic, connected endpoints, identities, geometry and validation. Optional production features remain separate; current Core export excludes enabled straight routes. |
| **Platforms** | Platform add/duplicate/remove/reorder handlers and `calculate_platform_boundaries`: host references, edge clearance, coverage, length, taper/ramp and edge/face/solid outputs. Separate physical platforms from track **Platform widening**. [Source][platforms] | [Detailed platform walkthrough](handbook/platforms.md): Track A stationing, independent-host projection, worked end profiles, manager identity, native shapes and current state limitations. Formation-board and sectioning algorithms remain separate. |
| **Formation board** | `create_formation_geometry_multi`: occupied footprints, margin, width, outline/solid and engraving; explain how the board relates to tracks and platforms. [Controls][formation-ui]; [calculation][formation] | [Detailed formation walkthrough](handbook/formation-board.md): reference projection, sampled limits, broadening, minimum width, connected end caps, native outputs, engraving, protection and saved state. Includes a nominal two-track/platform example; sectioning and registration remain separate. |
| **Universal sectioning** | `calculate_section_plan`, `create_section_masks` and `validate_section_partition`: shared boundaries, balanced lengths, travel order, retained unsplit objects and rejected partitions. [Controls][section-ui]; [calculations][sectioning] | [Detailed sectioning walkthrough](handbook/sectioning.md): controls, balanced and unbalanced examples, perpendicular masks, exact area/volume checks, partial platforms, per-route plans, numbering and preservation. Later assembly changes remain separate. |
| **Formation-board registration features** and **Track-template assembly and fixing** | `apply_registration_features`, `apply_track_template_joints`, `create_track_template_fixing_holes` and `cut_formation_matching_holes`: separate board placement from per-strip joints, centreline fixing and copied board holes. [Source][assembly] | [Detailed assembly walkthrough](handbook/assembly-and-fixing.md): mode and editor enablement, protected-board searches, track-station mapping, fit guards, 400 mm hole example, propagation, object state and failure limits. |

The platform track selectors currently list the main curve and its added-track
rows. They do not offer Straight Track Manager routes. The
[platform chapter](handbook/platforms.md#host-names-are-choices-backed-by-list-positions)
explains that boundary and the positional host references.
[Track-choice implementation][platform-hosts]

## Editing, turnouts, crossovers and chairs

The **REA C10 turnout and crossover manager...** button opens one manager with
**Turnouts** and **Crossovers** tabs. Selection, edit mode, current analysis and
integration state affect which actions are available. [Manager entry][manager-entry]

| Workflow and visible control | Current entry point and explanation to write | Coverage |
| --- | --- | --- |
| **TrackTemplate transition editor**: **Apply** | Explicit `activate_transition_editing` lifecycle, `show_editor`, `TransitionParameterEditorController.edit_selected` and `edit_transition_length_mm`: selected identity, length, current state, replacement, rejection and cleanup. [Source][transition-ui] | [Bounded walkthrough](handbook/transition-edit.md) |
| **Create curve-inheriting C10 turnout**, edit/apply/cancel and picked placement | `TurnoutManagerDialog` handlers and `create_curve_inheriting_c10_turnout` / `edit_curve_inheriting_c10_turnout`: host station, orientation, handing, natural C10 mapping, source timbering, retained identity and edit recovery. [Source][turnouts] | [Bounded walkthrough](handbook/turnout-placement-and-editing.md) |
| **Preview geometry diagnostics**, create/edit/remove crossover | `CrossoverManagerPanel.preview_geometry`, inherited `solve_rea_c10_crossover_geometry` and `CrossoverPreflightAdapter`: two-host mapping, connector search, complete-radius rule, occupancy and stale-preview rejection. [Panel][crossovers]; [preflight][crossover-preflight] | [Detailed crossover walkthrough](handbook/crossover-geometry.md): separate host station systems, mapped turnouts and connector, two complete-radius witnesses, signature-bound preview and create/edit recovery. Timber/chair checks and integration remain separate. |
| **Convert selected turnout to crossover** and **Convert selected crossover to turnout** | `extend_turnout_to_rea_c10_crossover` and `convert_rea_c10_crossover_to_turnout`: eligible source, conversion intent, retained/replaced identities, dependent state and recovery. [Source][conversion] | [Detailed conversion walkthrough](handbook/turnout-crossover-conversion.md): nearest valid neighbour, original output snapshot, Host A/B reversion, stable IDs versus rebuilt FreeCAD objects, production record replacement and failure boundaries. |
| **Analyse selected crossover timbering** and automatic/specialist timber controls | `analyse_rea_c10_crossover_timbering`, shared-long-timber, B3 and B4 resolve/apply/clear operations: source records, protected features, conflicts, proposed versus applied geometry, stale results and reversible display. B16 adds B4 recovery. [Controls][timber-controls]; [adapter][timber-recovery] | Not yet written |
| **Analyse chair positions**, details, settings and markers | Final `ChairAnalysisPanel.run_analysis` and `analyse_entity_chair_positions`: rail/timber inputs, assignments, unresolved positions, analytical footprints, signatures and reuse. Explain visibility separately from railway state. [Source][chair-actions] | Not yet written |
| **Prepare model timber support** and **Build 2D chair layout** | `prepare_chair_model_support` and `build_and_validate_chair_2d_layout`: bounded model allowances, prototype references, support outlines, fit checks, failure overlays and enablement conditions. [Source][chair-panel] | Not yet written |
| **Build 3D chairs for export**, **Revalidate 3D export chairs** and removal | `generate_supported_chair_solids`, `validate_generated_chair_solids` and `remove_generated_chair_solids`: the supported inherited bodies labelled `S1` and `S1J` in the source, exact construction, stale solids and fit. The panel still reports “Production ready: No.” [Actions][chair-actions]; [current labels][chair-panel] | Not yet written |
| Integrate/remove host integration; **Create reference copy** | Turnout and crossover integration handlers: prerequisites, source visibility, production records, identity, reference-copy purpose and reversal. Explain the actual B16 transaction/recovery adapters. [Turnout adapter][turnout-integration]; [crossover adapter][crossover-integration] | Not yet written |
| **Run next safe step** and **Show specialist and maintenance controls** | Final `update_guided_workflow` / `run_next_guided_step` bindings: one eligible operation at a time, disabled actions and status interpretation. The panel calls existing operations; it owns no geometry solver. [Source][guided] | Not yet written |
| **Whole-process benchmark** and **Reset timings** | Final workflow measurement wrappers and report callbacks: wall/CPU time, memory snapshots, recomputes, cache reuse and instrumentation cost. Explain measurement limits. [Source][timings] | Not yet written |

## Configuration, reports and output

| Workflow and visible control | Current entry point and explanation to write | Coverage |
| --- | --- | --- |
| **Configuration import and export...** | `ConfigurationImportExportDialog`, validation/migration and `_apply_validated`: JSON schema, diagnostics, proposed changes, dialogue-state application and atomic configuration-file writing. Import does not generate geometry. [Source][configuration] | Not yet written |
| **Named presets...** | `NamedPresetManagerDialog`: new/update/rename/duplicate/delete/apply, transported-preset merging, unsaved changes and explicit **Save preset library**. Distinguish dialogue state from the saved library. [Source][presets] | Not yet written |
| **Production schedule...** | `ProductionScheduleDialog`, `build_production_schedule_rows`: recognised records, grouping, refresh, FreeCAD sheet update and CSV export. [Source][schedule] | Not yet written |
| **Material and length report...** | `MaterialLengthReportDialog`, `build_material_report_rows`: physical-part selection, alternate representations, measured lengths, rectangular sheet-use estimates, settings, sheet update and CSV. [Source][material] | Not yet written |
| **Assembly labels...** | `AssemblyLabelDialog`, `rebuild_assembly_labels_for_set`: text/identity choices, preview, application/removal, derived export sources and persistence. [Source][labels] | Not yet written |
| **Production preflight...** / **Run preflight** | `ProductionPreflightDialog` and `run_production_preflight`: metadata, geometry, numbering, readiness, filenames/paths and optional temporary exporter-bound probes. Explain findings and their limits. [Source][preflight] | Not yet written |
| **Production export** settings in the main dialogue | Host `run_macro` through the composed core-export command: record categories, format availability, individual/combined files, manifest, serialisation, publication and failure reporting. [UI][export-ui]; [application operations][core-export] | Not yet written |
| **Export selected items...** | `SelectedProductionExportDialog` scope/route/row filters, preview and export; `SelectedExportBinding` selects the B16 set operation. Explain exactly which records/files are planned, confirmed and published, and the recovery boundary. [Binding][selected-export]; [set operation][selected-set] | Not yet written |

## Separate developer routes and future interfaces

The session exposes private chair-preview methods, including
`preview_private_catalogue_chair`, `preview_private_catalogue_p_chairs`,
`preview_private_catalogue_s1j_chairs` and crossover variants. These methods
have explicit factories, but no ordinary GUI-button binding was found in the
reviewed source. Their explanation is **Not yet written**. Document them as
session-only developer previews, with their own scope and output limits.
[Session methods][private-previews]

The intended completed Addon and later connected Layout Editor are future
interfaces. This inventory does not supply their menus, commands or network
workflows. Keep those design intentions distinct from the current retained
host, bounded transition editor and private previews. [Product vision][vision]

[revision]: https://github.com/Richard-Gnitnub/tracktemplate/tree/7965bfc4671668f889c1f43fb8336c5146c3f5cf
[launcher]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/TrackTemplate.FCMacro
[composition]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py
[generation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L40796-L42975
[main-ui]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L3651-L3837
[alignment]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/domain/alignment.py
[straights]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L3839-L3936
[platforms]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4045-L4207
[platform-hosts]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L5280-L5308
[formation-ui]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4212-L4259
[formation]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10461-L10521
[section-ui]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4263-L4299
[sectioning]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L10537-L10824
[assembly]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4303-L4391
[manager-entry]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L39686-L39946
[transition-ui]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/ui/transition_parameter_editor.py
[turnouts]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L39686-L40794
[crossovers]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L37746-L39678
[crossover-preflight]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/crossover_preflight.py
[conversion]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L29009-L29663
[timber-controls]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L38907-L39464
[timber-recovery]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/crossover_b4_recovery.py
[chair-actions]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L45823-L45942
[chair-panel]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46537-L46643
[turnout-integration]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/turnout_host_integration_recovery.py
[crossover-integration]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/crossover_host_integration_recovery.py
[guided]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L46724-L46963
[timings]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L47765-L47807
[configuration]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L21421-L21704
[presets]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L21019-L21419
[schedule]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L15268-L15468
[material]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L16620-L16934
[labels]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L20597-L20853
[preflight]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L18908-L19052
[export-ui]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro#L4398-L4566
[core-export]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/application/core_layout_export.py
[selected-export]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/selected_export_workflow.py
[selected-set]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/application/selected_export_set.py
[private-previews]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/tracktemplate/compatibility/transition_workflow.py#L2837-L2982
[vision]: https://github.com/Richard-Gnitnub/tracktemplate/blob/7965bfc4671668f889c1f43fb8336c5146c3f5cf/reference/PRODUCT_VISION.md
