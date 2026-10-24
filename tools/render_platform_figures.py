#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
"""Draw the handbook's independent physical-platform example.

Run manually with Python and Matplotlib 3.10.8:
    python tools/render_platform_figures.py

The arithmetic and saved JSON can be checked without Matplotlib or file changes:
    python tools/render_platform_figures.py --check-only

The Sphinx build uses the committed SVGs and does not need Matplotlib. This
script imports no workbench module and executes no project validator, macro
or FreeCAD process. Its assertions check the illustration, not the workbench.

Source: tracktemplate@7965bfc4671668f889c1f43fb8336c5146c3f5cf.
The retained 655 mm outside-track fixture is in tests/validate_phase1_alignment.py:
101-119. The profile equations follow the retained host's plan-taper calculation
at lines 9029-9098 and tracktemplate/domain/alignment.py:1866-1905. All dimensions
of this particular physical platform are teaching inputs, not a runtime receipt.

For the plan only, relative station s is replaced by ideal circular arc distance:
delta = (s - 75) / 655; x = r*sin(delta); y = r*cos(delta) - 655.
The origin is Track A's midpoint, X its tangent and Y its right normal there.
The workbench instead locates points by sampled chord station and interpolation.
Consequently this smooth-circle plan does not reproduce native platform geometry.
"""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "_static" / "figures"
CHECKS = ROOT / "_build" / "platform-review"
SOURCE_REVISION = "7965bfc4671668f889c1f43fb8336c5146c3f5cf"
SOURCE_BASE = "https://github.com/Richard-Gnitnub/tracktemplate/blob/" + SOURCE_REVISION
HOST_PATH = (
    "model_railway_curve_template_multitrack_v10_2a8a7b15_"
    "chair_performance_and_representation.FCMacro"
)
COPYRIGHT = "Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors."

MAIN_RADIUS = 600.0
TRACK_A_RADIUS = 655.0
MATCHED_EULER_LENGTH = 559.4102547270278  # Retained fixture; no solver runs here.
TOTAL_TURN = math.pi / 2.0
PLATFORM_LENGTH = 150.0
CLEARANCE = 20.0
FULL_WIDTH = 30.0
FULL_HEIGHT = 12.0
END_LENGTH = 30.0
NOSE_WIDTH = 0.10
TRACKBED_HEIGHT = 1.0
TABLE_STATIONS = (0.0, 3.0, 15.0, 30.0, 75.0, 120.0, 135.0, 147.0, 150.0)
ARITHMETIC_TOLERANCE = 1e-10  # Illustration check; not a product tolerance.

INK = "#263747"
BLUE = "#245b86"
ORANGE = "#b54818"
TEAL = "#247a74"
PALE_TEAL = "#d7ebe6"
GREY = "#778592"
LIGHT_GREY = "#d8e0e7"


def profile_values(station, full_width=FULL_WIDTH):
    """Evaluate this symmetric example's plan width and solid-top height."""
    fraction = max(0.0, min(1.0, station / END_LENGTH,
                            (PLATFORM_LENGTH - station) / END_LENGTH))
    # A nose limit prevents further reduction; it cannot enlarge a narrow section.
    width = min(full_width, max(NOSE_WIDTH, full_width * fraction))
    height = TRACKBED_HEIGHT + (FULL_HEIGHT - TRACKBED_HEIGHT) * fraction
    return width, height


def ideal_plan_point(radius, station):
    """Draw a smooth concentric circle, using s as illustrative arc distance."""
    delta = (station - PLATFORM_LENGTH / 2.0) / TRACK_A_RADIUS
    return radius * math.sin(delta), radius * math.cos(delta) - TRACK_A_RADIUS


def example_values():
    entry_angle = MATCHED_EULER_LENGTH / (2.0 * TRACK_A_RADIUS)
    circle_angle = TOTAL_TURN - 2.0 * entry_angle
    nominal_coverage = TRACK_A_RADIUS * circle_angle
    rows = []
    for station in TABLE_STATIONS:
        width, height = profile_values(station)
        rows.append({
            "relative_track_a_station_mm": station,
            "near_edge_offset_mm": CLEARANCE,
            "plan_width_mm": width,
            "far_edge_offset_mm": CLEARANCE + width,
            "solid_top_z_mm": height,
        })
    gap = TRACK_A_RADIUS - MAIN_RADIUS
    comparisons = [{
        "clearance_a_mm": clearance,
        "clearance_b_mm": clearance,
        "nominal_centreline_gap_mm": gap,
        "nominal_full_width_mm": gap - 2.0 * clearance,
        "ideal_width_sign": "positive" if gap > 2.0 * clearance else "non-positive",
    } for clearance in (20.0, 26.0, 27.0, 28.0)]
    return {
        "licence": "GPL-3.0-or-later",
        "copyright": COPYRIGHT,
        "description": "Independent handbook arithmetic; not a workbench or GUI test result.",
        "source_revision": SOURCE_REVISION,
        "equation_sources": [
            SOURCE_BASE + "/tests/validate_phase1_alignment.py#L92-L119",
            SOURCE_BASE + "/tracktemplate/domain/alignment.py#L1866-L1972",
            SOURCE_BASE + "/tracktemplate/domain/alignment.py#L1992-L2137",
            SOURCE_BASE + "/" + HOST_PATH + "#L9029-L9098",
            SOURCE_BASE + "/" + HOST_PATH + "#L9220-L9454",
        ],
        "inputs": {
            "arrangement": "Outside one track",
            "track_a": "Matched Outside track",
            "track_a_radius_mm": TRACK_A_RADIUS,
            "main_radius_mm": MAIN_RADIUS,
            "retained_track_a_euler_length_each_mm": MATCHED_EULER_LENGTH,
            "total_turn_degrees": 90.0,
            "outside_side": "Right of travel",
            "coverage": "Constant curve only",
            "platform_length_mm": PLATFORM_LENGTH,
            "centre_offset_mm": 0.0,
            "clearance_a_mm": CLEARANCE,
            "platform_width_mm": FULL_WIDTH,
            "body_output": "3D platform solid",
            "platform_height_mm": FULL_HEIGHT,
            "entry_end_style": "Tapered",
            "exit_end_style": "Tapered",
            "entry_end_length_mm": END_LENGTH,
            "exit_end_length_mm": END_LENGTH,
            "required_clearance_mm": 20.0,
            "check_clearance": True,
            "strip_width_mm": 32.0,
            "create_template": True,
        },
        "constants": {
            "plan_nose_limit_mm": NOSE_WIDTH,
            "trackbed_top_z_mm": TRACKBED_HEIGHT,
        },
        "station_and_frame": {
            "profiles": "Station along Track A from the platform start, in travel direction.",
            "plan_origin": "Track A midpoint on the ideal constant-radius circle.",
            "plan_x": "Tangent in the travel direction at the midpoint, in mm.",
            "plan_y": "Right normal at the midpoint, in mm.",
            "plan_equation": "delta=(s-75)/655; x=r*sin(delta); y=r*cos(delta)-655",
            "plan_parameter_limit": (
                "The plan substitutes relative station s for ideal arc distance. "
                "The workbench uses sampled chord distance and interpolated points."
            ),
        },
        "nominal_smooth_circle": {
            "entry_angle_rad": entry_angle,
            "constant_angle_rad": circle_angle,
            "constant_coverage_length_mm": nominal_coverage,
            "centred_platform_inset_each_mm": (nominal_coverage - PLATFORM_LENGTH) / 2.0,
            "limit": "Ideal arc arithmetic only; these are not host station results.",
        },
        "profile_table": rows,
        "nominal_between_track_comparison": comparisons,
        "between_track_limit": (
            "55-clearance_a-clearance_b describes the ideal concentric circles. "
            "The host projects Track B's offset edge onto Track A's normal and "
            "checks the computed cross-section width; it does not pair equal stations. "
            "This comparison does not establish native-shape validity or practical width."
        ),
        "nose_limit_note": (
            "A positive cross-section narrower than 0.10 mm is left at that width; "
            "the taper does not enlarge it to 0.10 mm."
        ),
        "evidence_limits": [
            "The physical-platform dimensions are teaching inputs, not a retained runtime receipt.",
            "No workbench module, project test, validator, macro or FreeCAD process ran.",
            "The plan is a smooth-circle illustration, not sampled or native workbench geometry.",
            "The profile table applies the independent equations to relative Track A stations.",
            "No absolute host station, native solid, GUI or export result is claimed.",
            "Top z values describe the solid calculation, not the separately lifted edge wires.",
            "These values establish no railway-standard clearance, physical fit or output acceptance.",
        ],
        "illustration_check_absolute_tolerance_mm": ARITHMETIC_TOLERANCE,
    }


def check_values(values):
    """Check fixed known values, symmetry, normal offsets and nominal fit."""
    expected_widths = (0.10, 3.0, 15.0, 30.0, 30.0, 30.0, 15.0, 3.0, 0.10)
    expected_heights = (1.0, 2.1, 6.5, 12.0, 12.0, 12.0, 6.5, 2.1, 1.0)
    for row, expected_width, expected_height in zip(
        values["profile_table"], expected_widths, expected_heights,
    ):
        station = row["relative_track_a_station_mm"]
        assert math.isclose(row["plan_width_mm"], expected_width,
                            rel_tol=0.0, abs_tol=ARITHMETIC_TOLERANCE)
        assert math.isclose(row["solid_top_z_mm"], expected_height,
                            rel_tol=0.0, abs_tol=ARITHMETIC_TOLERANCE)
        assert row["near_edge_offset_mm"] == 20.0
        assert math.isclose(row["far_edge_offset_mm"], 20.0 + expected_width,
                            rel_tol=0.0, abs_tol=ARITHMETIC_TOLERANCE)
        assert profile_values(station) == profile_values(PLATFORM_LENGTH - station)
        host = ideal_plan_point(TRACK_A_RADIUS, station)
        near = ideal_plan_point(TRACK_A_RADIUS + CLEARANCE, station)
        far = ideal_plan_point(TRACK_A_RADIUS + CLEARANCE + expected_width, station)
        assert math.isclose(math.dist(host, near), CLEARANCE,
                            rel_tol=0.0, abs_tol=ARITHMETIC_TOLERANCE)
        assert math.isclose(math.dist(near, far), expected_width,
                            rel_tol=0.0, abs_tol=ARITHMETIC_TOLERANCE)
        delta = (station - PLATFORM_LENGTH / 2.0) / TRACK_A_RADIUS
        tangent = (math.cos(delta), -math.sin(delta))
        assert abs(sum((near[i] - host[i]) * tangent[i] for i in (0, 1))) < ARITHMETIC_TOLERANCE
        mirrored = ideal_plan_point(TRACK_A_RADIUS, PLATFORM_LENGTH - station)
        assert abs(host[0] + mirrored[0]) < ARITHMETIC_TOLERANCE
        assert abs(host[1] - mirrored[1]) < ARITHMETIC_TOLERANCE
    assert ideal_plan_point(TRACK_A_RADIUS, 75.0) == (0.0, 0.0)
    assert ideal_plan_point(MAIN_RADIUS, 75.0) == (0.0, -55.0)
    assert 2.0 * END_LENGTH < PLATFORM_LENGTH
    nominal = values["nominal_smooth_circle"]
    assert math.isclose(nominal["constant_coverage_length_mm"], 469.46133932362943,
                        rel_tol=0.0, abs_tol=ARITHMETIC_TOLERANCE)
    assert math.isclose(nominal["centred_platform_inset_each_mm"], 159.73066966181471,
                        rel_tol=0.0, abs_tol=ARITHMETIC_TOLERANCE)
    assert nominal["constant_coverage_length_mm"] > PLATFORM_LENGTH
    assert [row["nominal_full_width_mm"] for row in
            values["nominal_between_track_comparison"]] == [15.0, 3.0, 1.0, -1.0]
    assert all(profile_values(s, 0.02)[0] == 0.02 for s in TABLE_STATIONS)


def save_figure(figure, filename, title):
    """Write reproducible SVG metadata and an ignored PNG inspection copy."""
    path = ASSETS / filename
    figure.savefig(path, metadata={
        "Date": None,
        "Creator": "TrackTemplate developer handbook",
        "Title": title,
        "Description": (
            "Independent mathematical illustration. Source revision " + SOURCE_REVISION
            + ". No workbench or FreeCAD execution; no native geometry or output qualification."
        ),
        "Rights": "SPDX-License-Identifier: GPL-3.0-or-later. " + COPYRIGHT,
    })
    path.write_text("\n".join(line.rstrip() for line in
                              path.read_text(encoding="utf-8").splitlines()) + "\n",
                    encoding="utf-8")
    figure.savefig(CHECKS / (Path(filename).stem + ".png"), dpi=150, facecolor="white")


def style_axis(axis):
    axis.set_axisbelow(True)
    axis.grid(color="#e5eaf0", linewidth=0.65)
    axis.tick_params(labelsize=10, length=3, color=GREY)
    for edge in ("left", "bottom"):
        axis.spines[edge].set_color(GREY)


def draw_plan(plt):
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch, Polygon

    figure = plt.figure(figsize=(10.8, 7.6), facecolor="white")
    figure.text(0.10, 0.97, "Outside platform: the near edge stays fixed",
                fontsize=16, fontweight="bold", va="top")
    figure.text(0.10, 0.925,
                "Track A: matched Outside track · Right of travel · 150 mm centred on the circle",
                fontsize=11, va="top")
    axis = figure.add_axes((0.10, 0.17, 0.85, 0.60))
    style_axis(axis)
    axis.set(xlim=(-135, 135), ylim=(-70, 65),
             xlabel="x: tangent at Track A midpoint (mm)",
             ylabel="y: right at Track A midpoint (mm)")
    axis.set_aspect("equal", adjustable="box")
    axis.set_xticks([-120, -90, -60, -30, 0, 30, 60, 90, 120])
    axis.set_yticks([-60, -40, -20, 0, 20, 40, 60])

    drawing_stations = [PLATFORM_LENGTH * index / 600.0 for index in range(601)]
    extended_stations = [-45.0 + 240.0 * index / 600.0 for index in range(601)]
    for radius, colour in ((MAIN_RADIUS, BLUE), (TRACK_A_RADIUS, ORANGE)):
        points = [ideal_plan_point(radius, s) for s in extended_stations]
        axis.plot(*zip(*points), color=colour, linewidth=2.2, zorder=3)
    near = [ideal_plan_point(TRACK_A_RADIUS + CLEARANCE, s) for s in drawing_stations]
    full_far = [ideal_plan_point(TRACK_A_RADIUS + CLEARANCE + FULL_WIDTH, s)
                for s in drawing_stations]
    tapered_far = [ideal_plan_point(TRACK_A_RADIUS + CLEARANCE + profile_values(s)[0], s)
                   for s in drawing_stations]
    axis.add_patch(Polygon(near + list(reversed(tapered_far)), closed=True,
                           facecolor=PALE_TEAL, edgecolor=TEAL, linewidth=1.7, zorder=3))
    outline = near + list(reversed(full_far)) + [near[0]]
    axis.plot(*zip(*outline), color=GREY, linewidth=1.3, linestyle=(0, (5, 3)), zorder=4)
    axis.plot(*zip(*near), color=TEAL, linewidth=2.0, zorder=5)
    for station in (15.0, 30.0, 120.0, 135.0):
        width, _height = profile_values(station)
        first = ideal_plan_point(TRACK_A_RADIUS + CLEARANCE, station)
        second = ideal_plan_point(TRACK_A_RADIUS + CLEARANCE + width, station)
        axis.plot([first[0], second[0]], [first[1], second[1]],
                  color=TEAL, linewidth=0.8, linestyle=(0, (2, 3)), zorder=4)

    for low, high, label in ((0.0, 20.0, "20 mm\nclearance"),
                             (20.0, 50.0, "30 mm\nfull width")):
        axis.annotate("", xy=(0, high), xytext=(0, low),
                      arrowprops={"arrowstyle": "<->", "color": INK,
                                  "linewidth": 1.1, "shrinkA": 0, "shrinkB": 0},
                      zorder=6)
        axis.text(8, (low + high) / 2.0, label, fontsize=10.5, va="center",
                  bbox={"facecolor": "white", "edgecolor": "none", "pad": 3.5}, zorder=7)
    axis.plot(0, 0, "o", color=ORANGE, markersize=4, zorder=6)
    axis.annotate("Midpoint", xy=(0, 0), xytext=(-35, -23), ha="center",
                  fontsize=10.5, bbox={"facecolor": "white", "edgecolor": "none", "pad": 3.5},
                  arrowprops={"arrowstyle": "-", "color": GREY, "shrinkA": 7, "shrinkB": 6})
    axis.annotate("Travel", xy=(75, -22), xytext=(35, -22), va="center",
                  fontsize=10.5, color=ORANGE,
                  bbox={"facecolor": "white", "edgecolor": "none", "pad": 3.5},
                  arrowprops={"arrowstyle": "-|>", "color": ORANGE, "linewidth": 1.6,
                              "shrinkA": 8, "shrinkB": 0})
    nose = ideal_plan_point(TRACK_A_RADIUS + CLEARANCE + NOSE_WIDTH / 2.0, 0.0)
    axis.annotate("0.10 mm\nend width", xy=nose, xytext=(-111, 35), ha="center",
                  fontsize=10.5, bbox={"facecolor": "white", "edgecolor": "none", "pad": 3.5},
                  arrowprops={"arrowstyle": "-", "color": GREY, "shrinkA": 7, "shrinkB": 4})
    handles = [
        Line2D([], [], color=BLUE, linewidth=2.2, label="Main centreline · R 600 mm"),
        Line2D([], [], color=ORANGE, linewidth=2.2, label="Track A centreline · R 655 mm"),
        Patch(facecolor=PALE_TEAL, edgecolor=TEAL, label="Platform after plan taper"),
        Line2D([], [], color=GREY, linewidth=1.3, linestyle=(0, (5, 3)),
               label="Untapered 30 mm footprint"),
    ]
    figure.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.09, 0.882),
                  ncols=2, frameon=False, fontsize=10, columnspacing=2.5,
                  handlelength=2.7, labelspacing=0.7)
    figure.text(0.10, 0.075,
                "Plan only: smooth circles, using s as ideal arc distance. Equal X/Y scale.",
                fontsize=10, va="top")
    figure.text(0.10, 0.042,
                "Workbench station follows sampled chords. This is not native platform geometry.",
                fontsize=10, va="top")
    save_figure(figure, "platform-plan-example.svg", "Outside platform plan example")
    plt.close(figure)


def draw_profiles(plt):
    figure = plt.figure(figsize=(10.8, 7.6), facecolor="white")
    figure.text(0.11, 0.94, "Matched ends narrow in plan and descend to the trackbed",
                fontsize=15.5, fontweight="bold", va="top")
    figure.text(0.11, 0.895,
                "150 mm platform · two 30 mm ends · 30 mm full width · 12 mm top height",
                fontsize=11, va="top")
    axes = [figure.add_axes((0.11, bottom, 0.84, 0.265)) for bottom in (0.55, 0.17)]
    stations = [PLATFORM_LENGTH * index / 600.0 for index in range(601)]
    # Include the width-floor breakpoint, which is shorter than a drawing step.
    floor_station = END_LENGTH * NOSE_WIDTH / FULL_WIDTH
    stations = sorted(set(stations + [floor_station, PLATFORM_LENGTH - floor_station]))
    widths, heights = zip(*(profile_values(station) for station in stations))
    for axis in axes:
        style_axis(axis)
        axis.set_xlim(-3, 153)
        axis.set_xticks([0, 15, 30, 75, 120, 135, 150])
        axis.axvspan(0, END_LENGTH, color="#f1f5f7", zorder=0)
        axis.axvspan(PLATFORM_LENGTH - END_LENGTH, PLATFORM_LENGTH,
                     color="#f1f5f7", zorder=0)
        for station in (30, 120):
            axis.axvline(station, color=GREY, linewidth=1.0,
                         linestyle=(0, (4, 4)), zorder=2)
    width_axis, height_axis = axes
    width_axis.plot(stations, widths, color=TEAL, linewidth=2.5, zorder=3)
    width_axis.scatter([0, 150], [NOSE_WIDTH, NOSE_WIDTH], color=TEAL, s=22, zorder=4)
    width_axis.set(ylim=(-1, 37), yticks=[0, 10, 20, 30], ylabel="Plan width (mm)")
    width_axis.tick_params(labelbottom=False)
    width_axis.set_title("Plan: the far edge supplies the taper", loc="left",
                         fontsize=12, fontweight="bold", pad=13)
    width_axis.text(75, 33, "90 mm at full width", ha="center", va="center", fontsize=10.5,
                    bbox={"facecolor": "white", "edgecolor": "none", "pad": 3.5})
    width_axis.text(75, 7, "0.10 mm nose at each end", ha="center", va="center", fontsize=10.5,
                    bbox={"facecolor": "white", "edgecolor": "none", "pad": 3.5})
    height_axis.plot(stations, heights, color=ORANGE, linewidth=2.5, zorder=3)
    height_axis.scatter([0, 150], [TRACKBED_HEIGHT, TRACKBED_HEIGHT], color=ORANGE, s=22, zorder=4)
    height_axis.axhline(TRACKBED_HEIGHT, color=BLUE, linewidth=1.3,
                        linestyle=(0, (5, 3)), zorder=2)
    height_axis.set(ylim=(-0.2, 14.5), yticks=[1, 6, 12], ylabel="Solid top z (mm)",
                    xlabel="Relative station from the platform start on Track A (mm)")
    height_axis.set_title("Solid: the top rises from 1 mm to 12 mm", loc="left",
                          fontsize=12, fontweight="bold", pad=13)
    height_axis.text(75, 3.4, "Trackbed surface: z = 1 mm", color=BLUE,
                     ha="center", va="center", fontsize=10.5,
                     bbox={"facecolor": "white", "edgecolor": "none", "pad": 3.5})
    figure.text(0.11, 0.074,
                "Independent profile arithmetic. Dashed vertical guides mark the two 30 mm ends.",
                fontsize=10, va="top")
    figure.text(0.11, 0.041,
                "No workbench or FreeCAD execution; these profiles do not qualify the native solid.",
                fontsize=10, va="top")
    save_figure(figure, "platform-profiles-example.svg", "Platform taper and height profiles")
    plt.close(figure)


def draw_figures(values):
    CHECKS.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    os.environ["MPLCONFIGDIR"] = str(CHECKS / "matplotlib-cache")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "svg.fonttype": "none",
        "svg.hashsalt": "tracktemplate-physical-platform-example",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
    })
    draw_plan(plt)
    draw_profiles(plt)
    (ASSETS / "platform-example-values.json").write_text(
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
              "source_revision": SOURCE_REVISION,
              "workbench_execution": "not performed"}
    if not args.check_only:
        result["matplotlib_version"] = draw_figures(values)
        files = [Path(__file__).resolve()] + [ASSETS / filename for filename in (
            "platform-plan-example.svg", "platform-profiles-example.svg",
            "platform-example-values.json",
        )]
        result["sha256"] = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in files}
    saved_values = json.loads((ASSETS / "platform-example-values.json").read_text(encoding="utf-8"))
    assert saved_values == values, "Saved platform-example-values.json differs from its calculation."
    result["saved_values_consistency"] = "passed"
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
