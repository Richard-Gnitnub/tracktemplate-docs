#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
"""Draw the handbook's independent universal-sectioning examples.

Run manually with Python and Matplotlib 3.10.8:
    python tools/render_section_figures.py

Check arithmetic and saved JSON without Matplotlib or file changes:
    python tools/render_section_figures.py --check-only

Sphinx uses the committed SVGs. This documentation tool imports no workbench
module and executes no workbench tool, validator, macro or FreeCAD process.
It illustrates source-inspected arithmetic, not a native partition result.

The source is tracktemplate@7965bfc4671668f889c1f43fb8336c5146c3f5cf.
The B15 planner is at lines 10537-10584. Its active masks use perpendicular
halfspaces at lines 10660-10700, not the earlier sampled mask-strip helper.
The source indexes alignment stations by sampled XY chords and interpolates
points and headings. This tool instead uses ideal circular arc distance.

The curved drawing is a NEW 300 mm main-reference circular example, not the
full Euler example from the preceding chapters. It retains their two radii,
32 mm strips, 150 mm outside platform, 20 mm clearance, 30 mm width/tapers,
10 mm formation margin, 120 mm minimum width and 12 mm board thickness.
Main s=0 is (0, 0), initially travelling along +X; the circle centre is
(0, 600). With theta=s/600, a signed left-normal offset v gives
P(s,v)=((600-v)*sin(theta), 600-(600-v)*cos(theta)).
The platform's local outer-host distance u maps to s=120+u*600/655.
Only s=100 and s=200 are illustrated cutting boundaries. The board's end
caps retain 10 mm tangent margins beyond s=0 and s=300. Drawing vertices
sample these continuous teaching equations; they are not host samples.
"""

import argparse
import hashlib
import json
import math
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "_static" / "figures"
CHECKS = ROOT / "_build" / "section-review"
SOURCE_REVISION = "7965bfc4671668f889c1f43fb8336c5146c3f5cf"
SOURCE_BASE = "https://github.com/Richard-Gnitnub/tracktemplate/blob/" + SOURCE_REVISION
HOST_PATH = (
    "model_railway_curve_template_multitrack_v10_2a8a7b15_"
    "chair_performance_and_representation.FCMacro"
)
COPYRIGHT = "Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors."
ARITHMETIC_TOLERANCE = 1e-10  # Illustration check, not a product tolerance.
SOURCE_GEOMETRY_TOLERANCE = 1e-8
SOURCE_MAXIMUM_COUNT = 999
MAIN_RADIUS = 600.0
OUTER_RADIUS = 655.0
MAIN_LENGTH = 300.0
STRIP_WIDTH = 32.0
PLATFORM_START_MAIN = 120.0
PLATFORM_LENGTH = 150.0
PLATFORM_TAPER = 30.0
PLATFORM_CLEARANCE = 20.0
PLATFORM_WIDTH = 30.0
PLATFORM_NOSE = 0.1
PLATFORM_HEIGHT = 12.0
MARGIN = 10.0
MINIMUM_WIDTH = 120.0
BOARD_THICKNESS = 12.0
MAXIMUM_SLOPE = 0.5
MAIN_PER_OUTER = MAIN_RADIUS / OUTER_RADIUS
PLATFORM_FINISH_MAIN = PLATFORM_START_MAIN + PLATFORM_LENGTH * MAIN_PER_OUTER
FULL_WIDTH_START = PLATFORM_START_MAIN + PLATFORM_TAPER * MAIN_PER_OUTER
FULL_WIDTH_FINISH = PLATFORM_START_MAIN + (PLATFORM_LENGTH - PLATFORM_TAPER) * MAIN_PER_OUTER

INK = "#263747"
BLUE = "#245b86"
ORANGE = "#b54818"
TEAL = "#247a74"
CUT = "#8b3153"
GREY = "#778592"
PALE_BLUE = "#dce8f2"
PALE_ORANGE = "#f2dfd1"
PALE_TEAL = "#d7ebe6"
BOARD_FILL = "#edf0f4"


def close(actual, expected):
    assert math.isclose(actual, float(expected), rel_tol=0.0, abs_tol=ARITHMETIC_TOLERANCE), (actual, expected)


def plan_arithmetic(total, maximum, minimum, balanced, enabled=True):
    """Independent teaching calculation with the inspected planner's branches.

    The symbolic errors below identify source branches. They are not quoted
    workbench diagnostics, and running this function is no workbench test.
    """
    total, maximum, minimum = float(total), float(maximum), float(minimum)
    tolerance = SOURCE_GEOMETRY_TOLERANCE
    if total <= tolerance:
        raise ValueError("no_usable_reference_length")
    active = enabled and maximum > tolerance and maximum < total - tolerance
    if not active:
        return {"enabled": False, "boundaries_mm": [0.0, total],
                "lengths_mm": [total], "initial_unbalanced_boundaries_mm": None,
                "last_pair_redistributed": False}
    if minimum > maximum + tolerance:
        raise ValueError("minimum_exceeds_maximum")
    count = math.ceil(total / maximum)
    if count > SOURCE_MAXIMUM_COUNT:
        raise ValueError("more_than_999_pieces")
    initial = None
    repaired = False
    if balanced:
        if total / count + tolerance < minimum:
            raise ValueError("balanced_length_below_minimum")
        boundaries = [total * index / count for index in range(count + 1)]
    else:
        boundaries = [0.0]
        next_boundary = maximum
        while next_boundary < total - tolerance:
            boundaries.append(next_boundary)
            next_boundary += maximum
        boundaries.append(total)
        initial = list(boundaries)
        if len(boundaries) > 2 and total - boundaries[-2] + tolerance < minimum:
            last_pair_length = total - boundaries[-3]
            replacement = last_pair_length / 2.0
            if replacement + tolerance < minimum or replacement > maximum + tolerance:
                raise ValueError("last_pair_cannot_meet_limits")
            boundaries[-2] = boundaries[-3] + replacement
            repaired = True
    lengths = [b - a for a, b in zip(boundaries, boundaries[1:])]
    assert all(length + tolerance >= minimum for length in lengths)
    assert all(length <= maximum + 1e-6 for length in lengths)
    return {"enabled": True, "boundaries_mm": boundaries, "lengths_mm": lengths,
            "initial_unbalanced_boundaries_mm": initial,
            "last_pair_redistributed": repaired}


def corner_cases():
    cases = [
        ("maximum_covers_reference", 400, 500, 250, True, True),
        ("zero_maximum_disables_splitting", 1200, 0, 250, True, True),
        ("disabled_keeps_one_range", 1200, 500, 250, True, False),
        ("exact_maximum_multiple", 1000, 500, 250, False, True),
        ("remainder_equals_minimum", 1200, 500, 200, False, True),
        ("balanced_feasible_at_400_minimum", 1200, 500, 400, True, True),
        ("unbalanced_last_pair_fails_at_400_minimum", 1200, 500, 400, False, True),
        ("balanced_fails_at_450_minimum", 1200, 500, 450, True, True),
        ("minimum_exceeds_maximum", 1200, 500, 550, True, True),
        ("no_usable_length", 0, 500, 250, True, True),
        ("count_limit", 1000, 1, 0, True, True),
    ]
    results = []
    for name, total, maximum, minimum, balanced, enabled in cases:
        row = {"name": name, "inputs": {"total_mm": total, "maximum_mm": maximum,
               "minimum_mm": minimum, "balance_lengths": balanced, "enabled": enabled}}
        try:
            row["result"] = plan_arithmetic(total, maximum, minimum, balanced, enabled)
        except ValueError as error:
            row["rejected_branch"] = str(error)
        results.append(row)
    return results


def point_at(main_station, left_offset=0.0, tangent_shift=0.0):
    theta = main_station / MAIN_RADIUS
    radius = MAIN_RADIUS - left_offset
    return [radius * math.sin(theta) + tangent_shift * math.cos(theta),
            MAIN_RADIUS - radius * math.cos(theta) + tangent_shift * math.sin(theta)]


def platform_width(local_outer_station):
    fraction = min(1.0, local_outer_station / PLATFORM_TAPER,
                   (PLATFORM_LENGTH - local_outer_station) / PLATFORM_TAPER)
    return max(PLATFORM_NOSE, PLATFORM_WIDTH * fraction)


def raw_board_right(main_station):
    if not PLATFORM_START_MAIN <= main_station <= PLATFORM_FINISH_MAIN:
        return -81.0
    u = (main_station - PLATFORM_START_MAIN) / MAIN_PER_OUTER
    return -55.0 - PLATFORM_CLEARANCE - platform_width(u) - MARGIN


def board_edges(main_station):
    distance_to_plateau = max(FULL_WIDTH_START - main_station,
                              main_station - FULL_WIDTH_FINISH, 0.0)
    left = 26.0
    right = min(-81.0, -115.0 + MAXIMUM_SLOPE * distance_to_plateau)
    if left - right < MINIMUM_WIDTH:
        midpoint = (left + right) / 2.0
        left, right = midpoint + MINIMUM_WIDTH / 2.0, midpoint - MINIMUM_WIDTH / 2.0
    return left, right


def formation_knots():
    return {
        "broadening_start": FULL_WIDTH_START - 68.0,
        "minimum_width_expansion_finishes": FULL_WIDTH_START - 42.0,
        "platform_start": PLATFORM_START_MAIN,
        "full_platform_width_start": FULL_WIDTH_START,
        "full_platform_width_finish": FULL_WIDTH_FINISH,
        "platform_finish": PLATFORM_FINISH_MAIN,
        "minimum_width_expansion_resumes": FULL_WIDTH_FINISH + 42.0,
        "broadening_finish": FULL_WIDTH_FINISH + 68.0,
    }


def curve_values():
    boundaries = []
    for station in (0.0, 100.0, 200.0, 300.0):
        theta = station / MAIN_RADIUS
        left, right = board_edges(station)
        boundaries.append({
            "main_reference_station_mm": station,
            "is_internal_cut": station in (100.0, 200.0),
            "heading_rad": theta, "heading_deg": math.degrees(theta),
            "main_point_xy_mm": point_at(station),
            "outer_point_xy_mm": point_at(station, -55.0),
            "unit_tangent_xy": [math.cos(theta), math.sin(theta)],
            "unit_left_normal_xy": [-math.sin(theta), math.cos(theta)],
            "outer_absolute_arc_station_mm": station / MAIN_PER_OUTER,
            "formation_left_offset_mm": left,
            "formation_right_offset_mm": right,
            "formation_width_mm": left - right,
        })
    coverage = []
    for index, start in enumerate((0.0, 100.0, 200.0), 1):
        finish = start + 100.0
        first = max(start, PLATFORM_START_MAIN)
        last = min(finish, PLATFORM_FINISH_MAIN)
        local_range = None
        if last > first:
            local_range = [max(0.0, (first - PLATFORM_START_MAIN) / MAIN_PER_OUTER),
                           min(PLATFORM_LENGTH, (last - PLATFORM_START_MAIN) / MAIN_PER_OUTER)]
        coverage.append({
            "section": index, "main_reference_range_mm": [start, finish],
            "main_centreline_arc_length_mm": finish - start,
            "outer_centreline_arc_length_mm": (finish - start) / MAIN_PER_OUTER,
            "platform_local_outer_host_range_mm": local_range,
            "platform_outer_host_coverage_mm": 0.0 if local_range is None else local_range[1] - local_range[0],
        })
    caps = []
    for station, shift in ((0.0, -MARGIN), (MAIN_LENGTH, MARGIN)):
        left, right = board_edges(station)
        caps.append({"main_reference_endpoint_mm": station, "tangent_shift_mm": shift,
                     "left_xy_mm": point_at(station, left, shift),
                     "right_xy_mm": point_at(station, right, shift),
                     "is_cut_mask": False})
    return {
        "description": "New nominal circular teaching construction, not the preceding full Euler fixture.",
        "inputs": {"main_radius_mm": MAIN_RADIUS, "outer_radius_mm": OUTER_RADIUS,
                   "main_arc_length_mm": MAIN_LENGTH, "total_turn_rad": MAIN_LENGTH / MAIN_RADIUS,
                   "total_turn_degrees": math.degrees(MAIN_LENGTH / MAIN_RADIUS),
                   "maximum_section_length_mm": 100.0, "minimum_section_length_mm": 50.0,
                   "balance_lengths": True, "template_strip_width_each_mm": STRIP_WIDTH,
                   "platform_length_on_outer_host_mm": PLATFORM_LENGTH,
                   "platform_start_main_station_mm": PLATFORM_START_MAIN,
                   "platform_clearance_from_outer_centreline_mm": PLATFORM_CLEARANCE,
                   "platform_full_width_mm": PLATFORM_WIDTH, "platform_end_taper_each_mm": PLATFORM_TAPER,
                   "platform_nose_width_mm": PLATFORM_NOSE, "platform_full_height_mm": PLATFORM_HEIGHT,
                   "formation_outer_margin_mm": MARGIN, "formation_minimum_width_mm": MINIMUM_WIDTH,
                   "formation_thickness_mm": BOARD_THICKNESS},
        "frame": {"origin": "Main reference start at (0,0), initially travelling along +X.",
                  "circle_centre_xy_mm": [0.0, MAIN_RADIUS],
                  "station": "Ideal arc distance along the main reference from its start, in travel direction.",
                  "left_offset": "Positive left of travel; main centreline v=0, outer centreline v=-55 mm.",
                  "equation": "theta=s/600; P(s,v)=((600-v)*sin(theta), 600-(600-v)*cos(theta)).",
                  "platform_mapping": "s=120+u*600/655; u is ideal outer-host arc distance from the platform start.",
                  "vertical": "Formation top Z=0, bottom Z=-12 mm; platform height is a separate input."},
        "plan": plan_arithmetic(MAIN_LENGTH, 100, 50, True),
        "boundaries": boundaries, "layer_coverage": coverage,
        "platform_absolute_outer_host_range_mm": [131.0, 281.0],
        "platform_main_reference_range_mm": [PLATFORM_START_MAIN, PLATFORM_FINISH_MAIN],
        "outer_total_arc_length_mm": MAIN_LENGTH / MAIN_PER_OUTER,
        "equivalent_platform_centre_offset_on_complete_outer_arc_mm": 42.25,
        "platform_full_width_main_reference_range_mm": [FULL_WIDTH_START, FULL_WIDTH_FINISH],
        "formation_transition_main_stations_mm": formation_knots(),
        "formation_end_caps": caps,
        "board_cap_note": "The drawing extends the nominal endpoint offsets by 10 mm along each end tangent. These are source-outline caps, not additional cutting masks.",
        "physical_length_note": "The table gives centreline arc lengths and platform-host coverage. It does not assign a single length to a tapered platform edge, a variable-width board, or a native solid.",
    }


def example_values():
    return {
        "licence": "GPL-3.0-or-later", "copyright": COPYRIGHT,
        "description": "Independent handbook arithmetic; not a workbench, GUI or native partition result.",
        "source_revision": SOURCE_REVISION,
        "equation_sources": [SOURCE_BASE + "/" + HOST_PATH + anchor for anchor in (
            "#L4263-L4299", "#L8473-L8520", "#L10338-L10459", "#L10461-L10521",
            "#L10537-L10584", "#L10660-L10700", "#L10744-L10824")],
        "source_parameters": {"geometry_tolerance_mm": SOURCE_GEOMETRY_TOLERANCE,
                              "maximum_section_count": SOURCE_MAXIMUM_COUNT,
                              "section_mask_margin_mm": 100.0,
                              "halfspace_overlap_beyond_cut_each_side_mm": 1e-5,
                              "nominal_cut_overlap_mm": 0.0},
        "straight_example": {"total_length_mm": 1200.0, "maximum_section_length_mm": 500.0,
                             "minimum_section_length_mm": 250.0,
                             "balanced": plan_arithmetic(1200, 500, 250, True),
                             "unbalanced": plan_arithmetic(1200, 500, 250, False),
                             "last_pair_combined_mm": 700.0, "last_pair_replacement_each_mm": 350.0},
        "planner_corner_cases": corner_cases(),
        "curve_example": curve_values(),
        "evidence_limits": [
            "No workbench module, upstream tool, validator, macro or FreeCAD process ran.",
            "The planning function is independent documentation arithmetic, not the workbench implementation.",
            "The curved construction is new; it does not reproduce the prior complete Euler alignment or its absolute host stations.",
            "Ideal circular arc distances differ from the source's sampled XY chord stations and interpolated headings.",
            "The formation envelope is a continuous idealisation of the source's sampled projection and broadening rules.",
            "Drawing vertices sample continuous equations at 1 mm main-reference intervals or finer; they are not host samples.",
            "Only the two internal cut lines are shown; real masks are bounded halfspaces with 1e-5 mm overlap beyond each cut.",
            "The diagram supplies no native-shape clipping, partition, GUI, export, physical-fit or manufacturing proof.",
            "Reference interval lengths do not bound every physical edge, centreline or layer's complete dimensions.",
        ],
        "illustration_check_absolute_tolerance_mm": ARITHMETIC_TOLERANCE,
    }


def check_values(values):
    straight = values["straight_example"]
    assert straight["balanced"]["boundaries_mm"] == [0, 400, 800, 1200]
    assert straight["balanced"]["lengths_mm"] == [400, 400, 400]
    assert straight["unbalanced"]["initial_unbalanced_boundaries_mm"] == [0, 500, 1000, 1200]
    assert straight["unbalanced"]["boundaries_mm"] == [0, 500, 850, 1200]
    assert straight["unbalanced"]["lengths_mm"] == [500, 350, 350]
    for result in (straight["balanced"], straight["unbalanced"]):
        close(math.fsum(result["lengths_mm"]), 1200)
        assert all(250 <= length <= 500 for length in result["lengths_mm"])
    cases = {case["name"]: case for case in values["planner_corner_cases"]}
    for name in ("maximum_covers_reference", "zero_maximum_disables_splitting", "disabled_keeps_one_range"):
        assert cases[name]["result"]["enabled"] is False
        assert len(cases[name]["result"]["lengths_mm"]) == 1
    assert cases["exact_maximum_multiple"]["result"]["lengths_mm"] == [500, 500]
    assert cases["remainder_equals_minimum"]["result"]["lengths_mm"] == [500, 500, 200]
    assert cases["balanced_feasible_at_400_minimum"]["result"]["lengths_mm"] == [400, 400, 400]
    for name, reason in (("unbalanced_last_pair_fails_at_400_minimum", "last_pair_cannot_meet_limits"),
                         ("balanced_fails_at_450_minimum", "balanced_length_below_minimum"),
                         ("minimum_exceeds_maximum", "minimum_exceeds_maximum"),
                         ("no_usable_length", "no_usable_reference_length"),
                         ("count_limit", "more_than_999_pieces")):
        assert cases[name]["rejected_branch"] == reason

    curve = values["curve_example"]
    assert curve["plan"]["boundaries_mm"] == [0, 100, 200, 300]
    close(MAIN_PER_OUTER, Fraction(120, 131))
    close(curve["outer_total_arc_length_mm"], Fraction(655, 2))
    close(PLATFORM_FINISH_MAIN, Fraction(33720, 131))
    coverage = curve["layer_coverage"]
    assert coverage[0]["platform_local_outer_host_range_mm"] is None
    for row in coverage:
        close(row["main_centreline_arc_length_mm"], 100)
        close(row["outer_centreline_arc_length_mm"], Fraction(655, 6))
    close(coverage[1]["platform_outer_host_coverage_mm"], Fraction(262, 3))
    close(coverage[2]["platform_outer_host_coverage_mm"], Fraction(188, 3))
    close(sum(row["platform_outer_host_coverage_mm"] for row in coverage), 150)
    close(curve["equivalent_platform_centre_offset_on_complete_outer_arc_mm"], 131 + 75 - 327.5 / 2)
    knots = formation_knots()
    close(knots["broadening_start"], Fraction(10412, 131))
    close(knots["broadening_finish"], Fraction(39028, 131))
    assert 0 < knots["broadening_start"] < 100 < PLATFORM_START_MAIN < 200 < PLATFORM_FINISH_MAIN < 300

    # Common-angle points on different layers lie on the same normal line.
    for station in (100.0, 200.0):
        origin = point_at(station)
        tangent = (math.cos(station / MAIN_RADIUS), math.sin(station / MAIN_RADIUS))
        for offset in (16.0, -16.0, -39.0, -71.0, -75.0, -105.0, *board_edges(station)):
            point = point_at(station, offset)
            close(sum((p - o) * t for p, o, t in zip(point, origin, tangent)), 0)
        for offset in (16.0, -55.0, -105.0):
            before, after = point_at(station - 10, offset), point_at(station + 10, offset)
            assert sum((p - o) * t for p, o, t in zip(before, origin, tangent)) < 0
            assert sum((p - o) * t for p, o, t in zip(after, origin, tangent)) > 0

    # Check the continuous formation envelope against cones from its raw limits.
    stations = sorted(set([index / 2 for index in range(601)] + list(knots.values())))
    raw = [(station, raw_board_right(station)) for station in stations]
    for station in stations:
        expected_right = min(value + MAXIMUM_SLOPE * abs(station - other) for other, value in raw)
        distance = max(FULL_WIDTH_START - station, station - FULL_WIDTH_FINISH, 0.0)
        close(min(-81.0, -115.0 + MAXIMUM_SLOPE * distance), expected_right)
        left, right = board_edges(station)
        assert left - right >= MINIMUM_WIDTH - ARITHMETIC_TOLERANCE
        assert left >= 26.0 - ARITHMETIC_TOLERANCE
        assert right <= raw_board_right(station) + ARITHMETIC_TOLERANCE
    for cap in curve["formation_end_caps"]:
        station = cap["main_reference_endpoint_mm"]
        origin = point_at(station)
        tangent = (math.cos(station / MAIN_RADIUS), math.sin(station / MAIN_RADIUS))
        for side in ("left_xy_mm", "right_xy_mm"):
            close(sum((p - o) * t for p, o, t in zip(cap[side], origin, tangent)), cap["tangent_shift_mm"])
        assert not cap["is_cut_mask"]


def save_figure(figure, filename, title):
    path = ASSETS / filename
    figure.savefig(path, metadata={
        "Date": None, "Creator": "TrackTemplate developer handbook", "Title": title,
        "Description": "Independent nominal illustration. Source " + SOURCE_REVISION
                       + ". No workbench or FreeCAD execution; not native partition or physical-fit proof.",
        "Rights": "SPDX-License-Identifier: GPL-3.0-or-later. " + COPYRIGHT,
    })
    path.write_text("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines())
                    + "\n", encoding="utf-8")
    figure.savefig(CHECKS / (Path(filename).stem + ".png"), dpi=150, facecolor="white")


def draw_lengths(plt, values):
    from matplotlib.patches import Rectangle

    figure = plt.figure(figsize=(10.8, 7.2), facecolor="white")
    figure.text(0.08, 0.965, "One straight reference, two section plans", fontsize=16,
                fontweight="bold", va="top")
    figure.text(0.08, 0.91, "Reference 1,200 mm  ·  Maximum 500 mm  ·  Minimum 250 mm", fontsize=11.5, va="top")
    axis = figure.add_axes((0.08, 0.18, 0.85, 0.65))
    axis.set(xlim=(-20, 1220), ylim=(-0.3, 3.6))
    axis.set_axis_off()
    rows = [
        (2.75, "A  Balanced", values["straight_example"]["balanced"]["boundaries_mm"]),
        (1.5, "B  Unbalanced: initial cuts", [0, 500, 1000, 1200]),
        (0.25, "C  Unbalanced: after the last two sections are redistributed", values["straight_example"]["unbalanced"]["boundaries_mm"]),
    ]
    for row_index, (bottom, title, boundaries) in enumerate(rows):
        axis.text(0, bottom + 0.69, title, fontsize=12, fontweight="bold", va="bottom")
        for index, (start, finish) in enumerate(zip(boundaries, boundaries[1:])):
            short = row_index == 1 and index == 2
            fill = "#f4dfe6" if short else ("#dce8f2", "#e9eff5", "#dce8f2")[index]
            colour = CUT if short else BLUE
            axis.add_patch(Rectangle((start, bottom), finish - start, 0.48,
                                     facecolor=fill, edgecolor=colour, linewidth=1.5))
            axis.text((start + finish) / 2, bottom + 0.24, f"{finish - start:g} mm",
                      ha="center", va="center", fontsize=12.5, fontweight="bold", color=colour)
        for boundary in boundaries:
            axis.text(boundary, bottom - 0.13, f"{boundary:g}", ha="center", va="top", fontsize=10.5)
    figure.text(0.08, 0.095, "The 200 mm remainder is below 250 mm: (500 + 200) ÷ 2 = 350 mm.", fontsize=11.2)
    figure.text(0.08, 0.048, "Independent arithmetic. Boundary values are reference stations in mm.", fontsize=10.2)
    save_figure(figure, "section-lengths-example.svg", "Balanced and unbalanced section lengths")
    plt.close(figure)


def sampled_stations(start, finish, extra=()):
    count = max(1, math.ceil(finish - start))
    return sorted(set([start + (finish - start) * index / count for index in range(count + 1)]
                      + [s for s in extra if start <= s <= finish]))


def draw_shared_boundaries(plt, values):
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch, Polygon

    figure = plt.figure(figsize=(10.8, 10.0), facecolor="white")
    figure.text(0.07, 0.97, "The same cuts meet each selected layer", fontsize=16,
                fontweight="bold", va="top")
    figure.text(0.07, 0.925, "New nominal circular example  ·  Main R600 / outer R655  ·  Main reference 300 mm",
                fontsize=11.2, va="top")
    legend = [Patch(facecolor=PALE_BLUE, edgecolor=BLUE, label="Main strip"),
              Patch(facecolor=PALE_ORANGE, edgecolor=ORANGE, label="Outer strip"),
              Patch(facecolor=PALE_TEAL, edgecolor=TEAL, label="Platform"),
              Patch(facecolor=BOARD_FILL, edgecolor=GREY, label="Formation board"),
              Line2D([], [], color=CUT, linestyle=(0, (5, 3)), linewidth=1.7, label="Shared cut")]
    figure.legend(handles=legend, loc="upper left", bbox_to_anchor=(0.06, 0.89), ncols=5,
                  frameon=False, fontsize=10.3, handlelength=1.8, columnspacing=1.5)
    axis = figure.add_axes((0.07, 0.400, 0.86, 0.440))
    axis.set(xlim=(-25, 355), ylim=(-132, 152), xlabel="X (mm)", ylabel="Y (mm)")
    axis.set_aspect("equal", adjustable="box")
    axis.set_xticks([0, 100, 200, 300])
    axis.set_yticks([-100, -50, 0, 50, 100])
    axis.tick_params(labelsize=10.3, length=3, color=GREY)
    axis.grid(color="#e5eaf0", linewidth=0.65, zorder=0)
    for edge in ("left", "bottom"):
        axis.spines[edge].set_color(GREY)
    stations = sampled_stations(0, MAIN_LENGTH, [100, 200, *formation_knots().values()])
    left = [point_at(s, board_edges(s)[0]) for s in stations]
    right = [point_at(s, board_edges(s)[1]) for s in stations]
    cap_start, cap_finish = values["curve_example"]["formation_end_caps"]
    board = [cap_start["left_xy_mm"], *left, cap_finish["left_xy_mm"],
             cap_finish["right_xy_mm"], *reversed(right), cap_start["right_xy_mm"]]
    axis.add_patch(Polygon(board, closed=True, facecolor=BOARD_FILL, edgecolor=GREY,
                           linewidth=1.6, zorder=2))
    for offset, fill, colour in ((0.0, PALE_BLUE, BLUE), (-55.0, PALE_ORANGE, ORANGE)):
        polygon = [point_at(s, offset + STRIP_WIDTH / 2) for s in stations]
        polygon += [point_at(s, offset - STRIP_WIDTH / 2) for s in reversed(stations)]
        axis.add_patch(Polygon(polygon, closed=True, facecolor=fill, edgecolor=colour,
                               linewidth=1.4, zorder=3))
        centreline = [point_at(s, offset) for s in stations]
        axis.plot(*zip(*centreline), color=colour, linewidth=0.8, linestyle=(0, (4, 3)), zorder=4)
    platform_stations = sampled_stations(0, PLATFORM_LENGTH, (PLATFORM_TAPER, 120))
    near = [point_at(PLATFORM_START_MAIN + u * MAIN_PER_OUTER, -75) for u in platform_stations]
    far = [point_at(PLATFORM_START_MAIN + u * MAIN_PER_OUTER, -75 - platform_width(u))
           for u in reversed(platform_stations)]
    axis.add_patch(Polygon(near + far, closed=True, facecolor=PALE_TEAL, edgecolor=TEAL,
                           linewidth=1.5, zorder=5))
    knockout = {"facecolor": "white", "edgecolor": "none", "pad": 5.5}
    for station in (100.0, 200.0):
        ends = [point_at(station, offset) for offset in (board_edges(station)[1] - 20, 47)]
        axis.plot(*zip(*ends), color=CUT, linewidth=1.8, linestyle=(0, (5, 3)), zorder=7)
        label_x, label_y = point_at(station, 69)
        axis.text(label_x, label_y, f"s = {station:g}", ha="center", va="center",
                  color=CUT, fontsize=11.5, fontweight="bold", bbox=knockout, zorder=8)
    for x, label in ((38, "Section 01"), (156, "Section 02"), (278, "Section 03")):
        axis.text(x, 137, label, ha="center", va="center", fontsize=11.7,
                  fontweight="bold", bbox=knockout, zorder=8)
    axis.annotate("", xy=(61, -104), xytext=(8, -104),
                  arrowprops={"arrowstyle": "->", "color": INK, "linewidth": 1.4})
    axis.text(8, -118, "+X travel at s = 0", ha="left", va="center", fontsize=10.2,
              bbox=knockout, zorder=8)

    table_axis = figure.add_axes((0.07, 0.158, 0.86, 0.135))
    table_axis.set_axis_off()
    rows = values["curve_example"]["layer_coverage"]
    table = table_axis.table(cellText=[
        ["Main reference arc", "100.000", "100.000", "100.000"],
        ["Outer centreline arc", *[f'{row["outer_centreline_arc_length_mm"]:.3f}' for row in rows]],
        ["Platform host coverage", "None", *[f'{row["platform_outer_host_coverage_mm"]:.3f}' for row in rows[1:]]]],
        colLabels=["Coverage (mm)", "Section 01", "Section 02", "Section 03"],
        colWidths=[0.40, 0.20, 0.20, 0.20], cellLoc="center", bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10.9)
    for (row, column), cell in table.get_celld().items():
        cell.set_edgecolor("#ccd5dd")
        cell.set_linewidth(0.7)
        cell.PAD = 0.08
        cell.set_facecolor("#edf2f6" if row == 0 else "white")
        if row == 0:
            cell.get_text().set_fontweight("bold")
        if column == 0:
            cell.get_text().set_ha("left")
    figure.text(0.07, 0.325, "Same boundaries; different centreline lengths and platform coverage.",
                fontsize=11.5, fontweight="bold")
    figure.text(0.07, 0.118, "Platform: s = 120 to 257.405 mm. Envelope broadening begins at s = 79.481 mm.", fontsize=10.5)
    figure.text(0.07, 0.085, "Only the labelled dashed lines are cuts. Board end caps retain 10 mm tangent margins.", fontsize=10.5)
    figure.text(0.07, 0.052, "Origin: main start (0,0); offsets positive left of travel. Continuous illustration, not native geometry.", fontsize=10.0)
    save_figure(figure, "section-shared-boundaries-example.svg", "Shared section boundaries across nominal layers")
    plt.close(figure)


def draw_figures(values):
    CHECKS.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    os.environ["MPLCONFIGDIR"] = str(CHECKS / "matplotlib-cache")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "svg.fonttype": "none", "svg.hashsalt": "tracktemplate-section-examples",
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.labelcolor": INK, "text.color": INK,
                         "xtick.color": INK, "ytick.color": INK})
    draw_lengths(plt, values)
    draw_shared_boundaries(plt, values)
    (ASSETS / "section-example-values.json").write_text(
        json.dumps(values, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return matplotlib.__version__


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true",
                        help="Check arithmetic and saved JSON without Matplotlib or file changes.")
    args = parser.parse_args()
    values = example_values()
    check_values(values)
    result = {"illustration_arithmetic_checks": "passed", "planner_corner_cases": len(values["planner_corner_cases"]),
              "source_revision": SOURCE_REVISION, "workbench_execution": "not performed"}
    if not args.check_only:
        result["matplotlib_version"] = draw_figures(values)
        paths = [Path(__file__).resolve()] + [ASSETS / name for name in (
            "section-lengths-example.svg", "section-shared-boundaries-example.svg", "section-example-values.json")]
        result["sha256"] = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    saved = json.loads((ASSETS / "section-example-values.json").read_text(encoding="utf-8"))
    assert saved == values, "Saved section-example-values.json differs from its calculation."
    result["saved_values_consistency"] = "passed"
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
