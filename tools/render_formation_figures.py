#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
"""Draw the handbook's independent formation-board example.

Run manually with Python and Matplotlib 3.10.8:
    python tools/render_formation_figures.py

Check arithmetic and saved JSON without Matplotlib or file changes:
    python tools/render_formation_figures.py --check-only

Sphinx uses the committed SVGs. This script imports no workbench module and
executes no workbench validator, macro or FreeCAD process. It calculates a
continuous nominal illustration, not the host's sampled projected geometry.

The example follows tracktemplate@7965bfc4671668f889c1f43fb8336c5146c3f5cf.
The retained B15 host's _simple_formation_swept_face applies occupied limits,
margin, two-pass broadening and minimum width at lines 10338-10428. It uses
the main alignment's stations. Its body extrusion is at lines 10504-10508.

Here the two centrelines are ideal concentric circles of radii 600 and 655 mm.
The outer track carries the previous chapter's 150 mm platform with 30 mm
end tapers. Ideal main arc distance s = u * 600 / 655, where u is ideal outer
arc distance from the platform start. Neither is an absolute host station.
The unrolled plot keeps local transverse offsets, not global XY coordinates.

For this continuous idealisation, the right margin limit reaches -115 mm
through the full-width part. Its slope-limited envelope is the plateau plus
0.5 mm/mm run-outs, bounded above by the -81 mm track-only margin limit.
All lateral values use the source's positive-left normal frame. This closed
form is checked against the minimum of all sampled 0.5-slope cones, then the
minimum-width rule is applied to both edges.
"""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "_static" / "figures"
CHECKS = ROOT / "_build" / "formation-review"
SOURCE_REVISION = "7965bfc4671668f889c1f43fb8336c5146c3f5cf"
SOURCE_BASE = "https://github.com/Richard-Gnitnub/tracktemplate/blob/" + SOURCE_REVISION
HOST_PATH = (
    "model_railway_curve_template_multitrack_v10_2a8a7b15_"
    "chair_performance_and_representation.FCMacro"
)
COPYRIGHT = "Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors."

MAIN_RADIUS = 600.0
OUTER_RADIUS = 655.0
TRACK_GAP = OUTER_RADIUS - MAIN_RADIUS
STRIP_WIDTH = 32.0
PLATFORM_LENGTH = 150.0
PLATFORM_TAPER_LENGTH = 30.0
PLATFORM_CLEARANCE = 20.0
PLATFORM_WIDTH = 30.0
PLATFORM_HEIGHT = 12.0
PLATFORM_NOSE = 0.10
MARGIN = 10.0
MINIMUM_WIDTH = 120.0
BOARD_THICKNESS = 12.0
MAXIMUM_SLOPE = 0.5
MAIN_PER_OUTER = MAIN_RADIUS / OUTER_RADIUS
MAIN_PLATFORM_LENGTH = PLATFORM_LENGTH * MAIN_PER_OUTER
MAIN_TAPER_LENGTH = PLATFORM_TAPER_LENGTH * MAIN_PER_OUTER
TRACK_MARGIN_LEFT = STRIP_WIDTH / 2.0 + MARGIN
TRACK_MARGIN_RIGHT = -TRACK_GAP - STRIP_WIDTH / 2.0 - MARGIN
FULL_PLATFORM_MARGIN_RIGHT = -(
    TRACK_GAP + PLATFORM_CLEARANCE + PLATFORM_WIDTH + MARGIN
)
TABLE_OUTER_STATIONS = (0.0, 3.0, 15.0, 30.0, 75.0, 120.0, 135.0, 147.0, 150.0)
ARITHMETIC_TOLERANCE = 1e-10  # Illustration check, not a product tolerance.

INK = "#263747"
BLUE = "#245b86"
ORANGE = "#b54818"
TEAL = "#247a74"
PALE_TEAL = "#d7ebe6"
PALE_BLUE = "#dce8f2"
GREY = "#778592"


def widened_edges(left, right, minimum=MINIMUM_WIDTH):
    """Expand positive-left offsets equally about their current midpoint."""
    if left - right < minimum:
        centre = (left + right) / 2.0
        return centre + minimum / 2.0, centre - minimum / 2.0
    return left, right


def cross_section(include_platform):
    occupied_left = STRIP_WIDTH / 2.0
    occupied_right = -TRACK_GAP - STRIP_WIDTH / 2.0
    if include_platform:
        occupied_right = min(occupied_right, -TRACK_GAP - PLATFORM_CLEARANCE - PLATFORM_WIDTH)
    margin_left, margin_right = occupied_left + MARGIN, occupied_right - MARGIN
    final_left, final_right = widened_edges(margin_left, margin_right)
    return {
        "include_platform": include_platform,
        "occupied_left_offset_mm": occupied_left,
        "occupied_right_offset_mm": occupied_right,
        "occupied_width_mm": occupied_left - occupied_right,
        "margin_left_offset_mm": margin_left,
        "margin_right_offset_mm": margin_right,
        "margin_width_mm": margin_left - margin_right,
        "final_left_offset_mm": final_left,
        "final_right_offset_mm": final_right,
        "final_width_mm": final_left - final_right,
        "minimum_width_added_each_side_mm": final_left - margin_left,
        "board_top_z_mm": 0.0,
        "board_bottom_z_mm": -BOARD_THICKNESS,
    }


def raw_right_margin(main_station):
    """Use ideal circular arc stations and the previous platform's plan taper."""
    if not 0.0 <= main_station <= MAIN_PLATFORM_LENGTH:
        return TRACK_MARGIN_RIGHT
    outer_station = main_station / MAIN_PER_OUTER
    fraction = min(1.0, outer_station / PLATFORM_TAPER_LENGTH,
                   (PLATFORM_LENGTH - outer_station) / PLATFORM_TAPER_LENGTH)
    width = max(PLATFORM_NOSE, PLATFORM_WIDTH * fraction)
    return -TRACK_GAP - PLATFORM_CLEARANCE - width - MARGIN


def broadened_right_margin(main_station):
    """Closed-form 0.5-slope envelope for this continuous ideal illustration."""
    distance_to_plateau = max(
        MAIN_TAPER_LENGTH - main_station,
        main_station - (MAIN_PLATFORM_LENGTH - MAIN_TAPER_LENGTH),
        0.0,
    )
    return min(TRACK_MARGIN_RIGHT,
               FULL_PLATFORM_MARGIN_RIGHT + MAXIMUM_SLOPE * distance_to_plateau)


def profile_row(main_station):
    broadened = broadened_right_margin(main_station)
    left, right = widened_edges(TRACK_MARGIN_LEFT, broadened)
    return {
        "relative_main_arc_station_mm": main_station,
        "corresponding_outer_arc_station_mm": main_station / MAIN_PER_OUTER,
        "raw_right_margin_offset_mm": raw_right_margin(main_station),
        "broadened_right_margin_offset_mm": broadened,
        "final_left_offset_mm": left,
        "final_right_offset_mm": right,
        "final_width_mm": left - right,
    }


def transition_stations():
    runout = (TRACK_MARGIN_RIGHT - FULL_PLATFORM_MARGIN_RIGHT) / MAXIMUM_SLOPE
    minimum_threshold = TRACK_MARGIN_LEFT - MINIMUM_WIDTH
    minimum_runout = (minimum_threshold - FULL_PLATFORM_MARGIN_RIGHT) / MAXIMUM_SLOPE
    return {
        "broadening_start": MAIN_TAPER_LENGTH - runout,
        "minimum_width_expansion_finishes": MAIN_TAPER_LENGTH - minimum_runout,
        "platform_start": 0.0,
        "full_platform_width_start": MAIN_TAPER_LENGTH,
        "platform_midpoint": MAIN_PLATFORM_LENGTH / 2.0,
        "full_platform_width_finish": MAIN_PLATFORM_LENGTH - MAIN_TAPER_LENGTH,
        "platform_finish": MAIN_PLATFORM_LENGTH,
        "minimum_width_expansion_resumes": MAIN_PLATFORM_LENGTH - MAIN_TAPER_LENGTH + minimum_runout,
        "broadening_finish": MAIN_PLATFORM_LENGTH - MAIN_TAPER_LENGTH + runout,
    }


def example_values():
    return {
        "licence": "GPL-3.0-or-later",
        "copyright": COPYRIGHT,
        "description": "Independent nominal handbook arithmetic; not a workbench or FreeCAD result.",
        "source_revision": SOURCE_REVISION,
        "equation_sources": [
            SOURCE_BASE + "/" + HOST_PATH + "#L10156-L10459",
            SOURCE_BASE + "/" + HOST_PATH + "#L10461-L10521",
            SOURCE_BASE + "/" + HOST_PATH + "#L11505-L11534",
            SOURCE_BASE + "/" + HOST_PATH + "#L11782-L11796",
        ],
        "inputs": {
            "main_radius_mm": MAIN_RADIUS,
            "outer_radius_mm": OUTER_RADIUS,
            "template_strip_width_each_mm": STRIP_WIDTH,
            "both_template_strips_enabled": True,
            "platform_host": "Outer track, Right of travel",
            "platform_length_on_outer_track_mm": PLATFORM_LENGTH,
            "platform_end_length_each_on_outer_track_mm": PLATFORM_TAPER_LENGTH,
            "platform_clearance_from_outer_centreline_mm": PLATFORM_CLEARANCE,
            "platform_full_width_mm": PLATFORM_WIDTH,
            "platform_full_height_mm": PLATFORM_HEIGHT,
            "platform_nose_width_mm": PLATFORM_NOSE,
            "outer_margin_mm": MARGIN,
            "minimum_width_mm": MINIMUM_WIDTH,
            "board_thickness_mm": BOARD_THICKNESS,
            "maximum_transverse_slope_mm_per_main_station_mm": MAXIMUM_SLOPE,
        },
        "frame": {
            "lateral_coordinate": "Positive left of the main track's travel direction; main centreline is zero. This is the source's left-normal frame.",
            "longitudinal_coordinate": "Ideal main-centreline arc distance from the normal through the nominal platform start, in travel direction.",
            "station_conversion": "s_main = u_outer * 600/655. This is ideal common-angle arc arithmetic, not sampled host station mapping.",
            "vertical_coordinate": "Top of formation board is Z=0; its 12 mm extrusion extends to Z=-12.",
        },
        "nominal_occupied_left_and_right_offsets_mm": {
            "main_strip": {"left": 16.0, "right": -16.0},
            "outer_strip": {"left": -39.0, "right": -71.0},
            "full_width_platform": {"left": -75.0, "right": -105.0},
        },
        "midpoint_cross_sections": [cross_section(False), cross_section(True)],
        "nominal_main_per_outer_arc_ratio": MAIN_PER_OUTER,
        "nominal_main_taper_length_mm": MAIN_TAPER_LENGTH,
        "nominal_main_platform_length_mm": MAIN_PLATFORM_LENGTH,
        "continuous_profile_table": [profile_row(u * MAIN_PER_OUTER) for u in TABLE_OUTER_STATIONS],
        "continuous_transition_main_stations_mm": transition_stations(),
        "continuous_transition_values": {
            name: profile_row(s) for name, s in transition_stations().items()
        },
        "straight_end_cap_examples": [
            {"connection": "Independent", "reference_length_mm": 600.0,
             "start_tangent_shift_mm": -10.0, "finish_tangent_shift_mm": 10.0,
             "start_cap_station_coordinate_mm": -10.0, "finish_cap_station_coordinate_mm": 610.0},
            {"connection": "Curve entrance", "reference_length_mm": 600.0,
             "start_tangent_shift_mm": -10.0, "finish_tangent_shift_mm": 0.0,
             "start_cap_station_coordinate_mm": -10.0, "finish_cap_station_coordinate_mm": 600.0},
            {"connection": "Curve exit", "reference_length_mm": 600.0,
             "start_tangent_shift_mm": 0.0, "finish_tangent_shift_mm": 10.0,
             "start_cap_station_coordinate_mm": 0.0, "finish_cap_station_coordinate_mm": 610.0},
        ],
        "evidence_limits": [
            "Teaching dimensions do not establish physical clearance, structural suitability or manufacturing acceptance.",
            "The circles and boundary envelope are continuous idealisations; the workbench projects sampled edges onto sampled main-reference stations.",
            "No absolute host station, actual board outline, native area or volume is claimed.",
            "The mid-platform section uses the ideal constant-circle gap and full platform width; the plateau is unchanged by broadening in this illustration.",
            "The host adds margin, broadens each envelope, then enforces minimum width. Both final edges can move during the last step.",
            "The unrolled profile is not a global XY plot and is not the board's native cutting outline.",
            "The straight cap examples assume a 600 mm reference alignment and illustrate signed shifts, not shared widths or a fused joint.",
            "No workbench module, project validator, macro or FreeCAD process ran.",
        ],
        "illustration_check_absolute_tolerance_mm": ARITHMETIC_TOLERANCE,
    }


def close(actual, expected):
    assert math.isclose(actual, expected, rel_tol=0.0, abs_tol=ARITHMETIC_TOLERANCE), (actual, expected)


def check_values(values):
    """Check fixed values and the continuous envelope with an independent oracle."""
    without, included = values["midpoint_cross_sections"]
    for row, wanted in ((without, (16, -71, 26, -81, 32.5, -87.5, 120, 6.5)),
                        (included, (16, -105, 26, -115, 26, -115, 141, 0))):
        keys = ("occupied_left_offset_mm", "occupied_right_offset_mm",
                "margin_left_offset_mm", "margin_right_offset_mm",
                "final_left_offset_mm", "final_right_offset_mm",
                "final_width_mm", "minimum_width_added_each_side_mm")
        for key, expected in zip(keys, wanted):
            close(row[key], expected)
        close(row["board_top_z_mm"], 0)
        close(row["board_bottom_z_mm"], -12)
    close(MAIN_PER_OUTER, 120 / 131)
    close(MAIN_TAPER_LENGTH, 3600 / 131)
    close(MAIN_PLATFORM_LENGTH, 18000 / 131)
    knots = transition_stations()
    close(knots["broadening_start"], -5308 / 131)
    close(knots["broadening_finish"], 23308 / 131)
    close(knots["minimum_width_expansion_finishes"], -1902 / 131)
    close(knots["minimum_width_expansion_resumes"], 19902 / 131)
    close(profile_row(0)["broadened_right_margin_offset_mm"], -13265 / 131)
    close(profile_row(0)["final_width_mm"], 16671 / 131)
    close(profile_row(knots["broadening_start"])["final_right_offset_mm"], -87.5)
    close(profile_row(knots["minimum_width_expansion_finishes"])["final_right_offset_mm"], -94)
    close(profile_row(knots["minimum_width_expansion_finishes"])["final_left_offset_mm"], 26)
    expected_broadened = (-13265 / 131, -13445 / 131, -14165 / 131, -115,
                          -115, -115, -14165 / 131, -13445 / 131, -13265 / 131)
    for outer, row, expected in zip(TABLE_OUTER_STATIONS,
                                    values["continuous_profile_table"], expected_broadened):
        close(row["corresponding_outer_arc_station_mm"], outer)
        close(row["relative_main_arc_station_mm"] / MAIN_RADIUS, outer / OUTER_RADIUS)
        close(row["broadened_right_margin_offset_mm"], expected)
        close(row["final_left_offset_mm"], 26)
        close(row["final_width_mm"], 26 - expected)

    # A cone centred at every raw sample supplies an independent envelope check.
    stations = sorted(set([-65 + i * 0.5 for i in range(541)] + list(knots.values())))
    raw = [(s, raw_right_margin(s)) for s in stations]
    for station in stations:
        cone_minimum = min(value + MAXIMUM_SLOPE * abs(station - other) for other, value in raw)
        close(broadened_right_margin(station), cone_minimum)
        row = profile_row(station)
        mirrored = profile_row(MAIN_PLATFORM_LENGTH - station)
        close(row["final_width_mm"], mirrored["final_width_mm"])
        close(row["final_left_offset_mm"], mirrored["final_left_offset_mm"])
        assert row["final_width_mm"] >= MINIMUM_WIDTH - ARITHMETIC_TOLERANCE
        assert row["final_left_offset_mm"] >= TRACK_MARGIN_LEFT - ARITHMETIC_TOLERANCE
        assert row["final_right_offset_mm"] <= raw_right_margin(station) + ARITHMETIC_TOLERANCE
    for row, cap_pair in zip(values["straight_end_cap_examples"], ((-10, 610), (-10, 600), (0, 610))):
        close(row["start_cap_station_coordinate_mm"], cap_pair[0])
        close(row["finish_cap_station_coordinate_mm"], cap_pair[1])
        close(row["start_cap_station_coordinate_mm"], row["start_tangent_shift_mm"])
        close(row["finish_cap_station_coordinate_mm"], 600 + row["finish_tangent_shift_mm"])


def style_axis(axis):
    axis.set_axisbelow(True)
    axis.grid(color="#e5eaf0", linewidth=0.65)
    axis.tick_params(labelsize=10.5, length=3, color=GREY)
    for edge in ("left", "bottom"):
        axis.spines[edge].set_color(GREY)


def save_figure(figure, filename, title):
    path = ASSETS / filename
    figure.savefig(path, metadata={
        "Date": None,
        "Creator": "TrackTemplate developer handbook",
        "Title": title,
        "Description": "Independent continuous nominal illustration. Source " + SOURCE_REVISION
                       + ". No workbench or FreeCAD execution; not native geometry or output acceptance.",
        "Rights": "SPDX-License-Identifier: GPL-3.0-or-later. " + COPYRIGHT,
    })
    path.write_text("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines())
                    + "\n", encoding="utf-8")
    figure.savefig(CHECKS / (Path(filename).stem + ".png"), dpi=150, facecolor="white")


def draw_cross_sections(plt, values):
    from matplotlib.patches import Rectangle

    figure = plt.figure(figsize=(10.8, 9.0), facecolor="white")
    figure.text(0.10, 0.966, "Platform inclusion changes the board's occupied width",
                fontsize=15.5, fontweight="bold", va="top")
    figure.text(0.10, 0.927, "Mid-platform section · 10 mm margin · 120 mm minimum width · 12 mm board",
                fontsize=11, va="top")
    axes = [figure.add_axes((0.10, bottom, 0.85, 0.31)) for bottom in (0.54, 0.16)]
    for axis, row, label in zip(axes, values["midpoint_cross_sections"],
                                ("A  Platform footprint excluded", "B  Platform footprint included")):
        style_axis(axis)
        # Reverse the drawing axis so positive-left lies to the left on the page.
        axis.set(xlim=(45, -135), ylim=(-23, 22), yticks=[-12, 0, 12], ylabel="Z (mm)")
        axis.set_aspect("equal", adjustable="box")
        axis.set_xticks([40, 20, 0, -20, -40, -60, -80, -100, -120])
        axis.set_title(label, loc="left", fontsize=12.5, fontweight="bold", pad=15)
        left = row["final_left_offset_mm"]
        right = row["final_right_offset_mm"]
        axis.add_patch(Rectangle((right, -BOARD_THICKNESS), left - right, BOARD_THICKNESS,
                                 facecolor=PALE_BLUE, edgecolor=BLUE, linewidth=1.8, zorder=3))
        for position, colour, track_label in ((0, BLUE, "Main track"), (-55, ORANGE, "Outer track")):
            axis.add_patch(Rectangle((position - 16, 0), 32, 1,
                                     facecolor=colour, edgecolor=colour, zorder=5))
            axis.plot([position, position], [0, 14], color=colour,
                       linestyle=(0, (4, 3)), linewidth=1, zorder=4)
            axis.text(position, 17, track_label, ha="center", va="center", fontsize=10.5, color=colour)
        axis.add_patch(Rectangle((-105, 0), 30, 12, facecolor=PALE_TEAL,
                                 edgecolor=TEAL, linewidth=1.6, zorder=4))
        axis.text(-90, 6, "Platform", ha="center", va="center", fontsize=10.5, color=TEAL, zorder=6)
        axis.text((left + right) / 2.0, -6, "Board", ha="center", va="center",
                  fontsize=11, color=BLUE, fontweight="bold")
        axis.annotate("", xy=(left, -18), xytext=(right, -18),
                      arrowprops={"arrowstyle": "<->", "color": INK, "linewidth": 1.0,
                                  "shrinkA": 0, "shrinkB": 0})
        axis.text((left + right) / 2.0, -18, f"{left - right:g} mm", ha="center", va="center",
                  fontsize=11, bbox={"facecolor": "white", "edgecolor": "none", "pad": 2.5})
        axis.text(left, -13.5, f"{left:+g}", ha="center", va="top", fontsize=10)
        axis.text(right, -13.5, f"{right:g}", ha="center", va="top", fontsize=10)
        axis.annotate("", xy=(-124, 0), xytext=(-124, -12),
                      arrowprops={"arrowstyle": "<->", "color": INK, "linewidth": 1.0,
                                  "shrinkA": 0, "shrinkB": 0})
        axis.text(-126, -6, "12", ha="left", va="center", fontsize=10)
    axes[0].tick_params(labelbottom=False)
    axes[1].set_xlabel("Signed normal offset from main centreline (mm; +left)", labelpad=9)
    figure.text(0.10, 0.079, "Independent nominal sections. Template strips are shown, not rail profiles.",
                fontsize=10, va="top")
    figure.text(0.10, 0.048, "The platform remains enabled in both cases; inclusion controls the board footprint.",
                fontsize=10, va="top")
    save_figure(figure, "formation-cross-section-example.svg", "Formation-board cross-section comparison")
    plt.close(figure)


def draw_width_profiles(plt):
    from matplotlib.lines import Line2D

    figure = plt.figure(figsize=(10.8, 8.7), facecolor="white")
    figure.text(0.11, 0.97, "The board broadens before the platform begins",
                fontsize=15.5, fontweight="bold", va="top")
    figure.text(0.11, 0.927, "Unrolled ideal circles · main-reference distance = outer-track distance × 600/655",
                fontsize=11, va="top")
    axes = [figure.add_axes((0.11, bottom, 0.84, height))
            for bottom, height in ((0.50, 0.30), (0.18, 0.18))]
    knots = transition_stations()
    stations = sorted(set([-65 + i * 0.25 for i in range(1081)] + list(knots.values())
                          + [-1e-6, MAIN_PLATFORM_LENGTH + 1e-6]))
    rows = [profile_row(s) for s in stations]
    for axis in axes:
        style_axis(axis)
        axis.set_xlim(-65, 205)
        axis.set_xticks([-50, 0, 50, 100, 150, 200])
        axis.axvspan(MAIN_TAPER_LENGTH, MAIN_PLATFORM_LENGTH - MAIN_TAPER_LENGTH,
                     color="#f1f5f7", zorder=0)
        for station in (0, MAIN_PLATFORM_LENGTH):
            axis.axvline(station, color=BLUE, linewidth=1.0, linestyle=(0, (3, 4)), zorder=1)
    outer_axis, left_axis = axes
    outer_axis.plot(stations, [row["raw_right_margin_offset_mm"] for row in rows],
                    color=GREY, linestyle=(0, (5, 3)), linewidth=1.5, zorder=3)
    outer_axis.plot(stations, [row["broadened_right_margin_offset_mm"] for row in rows],
                    color=ORANGE, linewidth=4, alpha=0.65, zorder=4)
    outer_axis.plot(stations, [row["final_right_offset_mm"] for row in rows],
                    color=TEAL, linewidth=1.7, zorder=5)
    outer_axis.set(ylim=(-124, -76), yticks=[-115, -105, -94, -81], ylabel="Right edge offset (mm)")
    outer_axis.tick_params(labelbottom=False)
    outer_axis.text(MAIN_PLATFORM_LENGTH / 2, -120, "Full-width platform", ha="center",
                    fontsize=10.5, va="center")
    outer_axis.annotate("0.5 mm per mm\nof main station", xy=(-13, broadened_right_margin(-13)),
                        xytext=(-57, -116), fontsize=10.5,
                        bbox={"facecolor": "white", "edgecolor": "none", "pad": 2.5},
                        arrowprops={"arrowstyle": "-", "color": ORANGE, "shrinkA": 6, "shrinkB": 5})
    outer_axis.text(0, -79, "Platform start", color=BLUE, ha="center", va="bottom", fontsize=10)
    outer_axis.text(MAIN_PLATFORM_LENGTH, -79, "Platform finish", color=BLUE,
                    ha="center", va="bottom", fontsize=10)

    left_axis.axhline(TRACK_MARGIN_LEFT, color=GREY, linestyle=(0, (5, 3)), linewidth=1.5, zorder=3)
    left_axis.plot(stations, [row["final_left_offset_mm"] for row in rows],
                   color=TEAL, linewidth=2.1, zorder=4)
    left_axis.set(ylim=(23, 35), yticks=[26, 32.5], ylabel="Left edge offset (mm)",
                  xlabel="Ideal main-reference station from the platform start (mm)")
    left_axis.set_title("Minimum width also moves the opposite edge", loc="left",
                        fontsize=12, fontweight="bold", pad=13)
    handles = [
        Line2D([], [], color=GREY, linestyle=(0, (5, 3)), linewidth=1.5, label="Occupied limits + margin"),
        Line2D([], [], color=ORANGE, linewidth=4, alpha=0.65, label="After broadening"),
        Line2D([], [], color=TEAL, linewidth=2, label="After minimum width"),
    ]
    figure.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.10, 0.88),
                  ncols=3, frameon=False, fontsize=10, handlelength=2.5, columnspacing=1.6)
    figure.text(0.11, 0.085, "Continuous teaching calculation, not a global XY outline or sampled workbench result.",
                fontsize=10, va="top")
    figure.text(0.11, 0.052, "Signed offsets use the source's left normal: positive left, negative right.",
                fontsize=10, va="top")
    save_figure(figure, "formation-width-example.svg", "Formation-board continuous nominal width profiles")
    plt.close(figure)


def draw_figures(values):
    CHECKS.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    os.environ["MPLCONFIGDIR"] = str(CHECKS / "matplotlib-cache")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "svg.fonttype": "none", "svg.hashsalt": "tracktemplate-formation-board-example",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.labelcolor": INK, "text.color": INK, "xtick.color": INK, "ytick.color": INK,
    })
    draw_cross_sections(plt, values)
    draw_width_profiles(plt)
    (ASSETS / "formation-example-values.json").write_text(
        json.dumps(values, indent=2, allow_nan=False) + "\n", encoding="utf-8",
    )
    return matplotlib.__version__


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true",
                        help="Check arithmetic and saved JSON without drawing or writing files.")
    args = parser.parse_args()
    values = example_values()
    check_values(values)
    result = {"illustration_arithmetic_checks": "passed", "profile_table_rows": 9,
              "source_revision": SOURCE_REVISION, "workbench_execution": "not performed"}
    if not args.check_only:
        result["matplotlib_version"] = draw_figures(values)
        files = [Path(__file__).resolve()] + [ASSETS / filename for filename in (
            "formation-cross-section-example.svg", "formation-width-example.svg",
            "formation-example-values.json",
        )]
        result["sha256"] = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in files}
    saved = json.loads((ASSETS / "formation-example-values.json").read_text(encoding="utf-8"))
    assert saved == values, "Saved formation-example-values.json differs from its calculation."
    result["saved_values_consistency"] = "passed"
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
