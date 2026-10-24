#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
"""Draw the handbook's independent straight-track direction illustration.

Run manually with Python and Matplotlib 3.10.8:
    python tools/render_straight_route_figure.py

The Sphinx build uses the committed SVG and does not need Matplotlib. This
script imports no workbench module and executes no workbench tool or FreeCAD
process. Its assertions check this illustration, not the workbench.

Equations: tracktemplate@7965bfc4671668f889c1f43fb8336c5146c3f5cf,
tracktemplate/domain/alignment.py:116-117,1558-1590. The example inputs are
chosen for this handbook; they are not a retained workbench test fixture.
The figure represents mathematical centrelines only, with equal X/Y scale.
It makes no claim about strip geometry, gauge, physical fit or GUI behaviour.
"""

import json
import math
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "_static" / "figures"
CHECKS = ROOT / "_build" / "straight-review"
SOURCE_REVISION = "7965bfc4671668f889c1f43fb8336c5146c3f5cf"
SOURCE_URL = (
    "https://github.com/Richard-Gnitnub/tracktemplate/blob/"
    + SOURCE_REVISION
    + "/tracktemplate/domain/alignment.py"
)
DATUM = (100.0, 200.0)
LENGTH = 600.0
SPACING = 50.0
ROTATION_DEGREES = 0.0
COLOURS = ("#245b86", "#b54818")
INK = "#263747"


def direction_values(reverse=False):
    """Calculate two independent tracks from a tangent and its left normal."""
    heading = math.radians(ROTATION_DEGREES) + (math.pi if reverse else 0.0)
    tangent = (math.cos(heading), math.sin(heading))
    normal = (-math.sin(heading), math.cos(heading))
    tracks = []
    for index in range(2):
        offset = index * SPACING
        start = tuple(DATUM[axis] + offset * normal[axis] for axis in range(2))
        finish = tuple(start[axis] + LENGTH * tangent[axis] for axis in range(2))
        tracks.append({
            "track_number": index + 1,
            "offset_left_of_travel_mm": offset,
            "start_mm": list(start),
            "finish_mm": list(finish),
        })
    return {
        "direction": "Reverse" if reverse else "Forward",
        "heading_rad": heading,
        "heading_deg": math.degrees(heading),
        "unit_tangent_xy": list(tangent),
        "unit_left_normal_xy": list(normal),
        "tracks": tracks,
    }


def check_values(examples):
    """Check the fixed illustration's coordinates, lengths and spacing."""
    expected = (
        (((100.0, 200.0), (700.0, 200.0)),
         ((100.0, 250.0), (700.0, 250.0))),
        (((100.0, 200.0), (-500.0, 200.0)),
         ((100.0, 150.0), (-500.0, 150.0))),
    )
    tolerance_mm = 1e-10  # Illustration arithmetic check, not a product tolerance.
    for example, endpoints in zip(examples, expected):
        tracks = example["tracks"]
        assert tracks[0]["start_mm"] == list(DATUM)
        for track, (expected_start, expected_finish) in zip(tracks, endpoints):
            for actual, target in zip(track["start_mm"], expected_start):
                assert math.isclose(actual, target, rel_tol=0, abs_tol=tolerance_mm)
            for actual, target in zip(track["finish_mm"], expected_finish):
                assert math.isclose(actual, target, rel_tol=0, abs_tol=tolerance_mm)
            assert math.isclose(
                math.dist(track["start_mm"], track["finish_mm"]),
                LENGTH, rel_tol=0, abs_tol=tolerance_mm,
            )
        for endpoint in ("start_mm", "finish_mm"):
            separation = [tracks[1][endpoint][axis] - tracks[0][endpoint][axis]
                          for axis in range(2)]
            assert math.isclose(
                math.hypot(*separation), SPACING,
                rel_tol=0, abs_tol=tolerance_mm,
            )
            assert math.isclose(
                sum(value * component for value, component in
                    zip(separation, example["unit_tangent_xy"])),
                0.0, rel_tol=0, abs_tol=tolerance_mm,
            )
            assert math.isclose(
                sum(value * component for value, component in
                    zip(separation, example["unit_left_normal_xy"])),
                SPACING, rel_tol=0, abs_tol=tolerance_mm,
            )


def save_values(examples):
    payload = {
        "licence": "GPL-3.0-or-later",
        "copyright": (
            "Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors."
        ),
        "description": (
            "Independent handbook arithmetic; not a workbench or GUI test result."
        ),
        "source_revision": SOURCE_REVISION,
        "equation_sources": [SOURCE_URL + "#L116-L117", SOURCE_URL + "#L1558-L1590"],
        "inputs": {
            "connection_mode": "Independent datum",
            "datum_mm": list(DATUM),
            "rotation_degrees": ROTATION_DEGREES,
            "length_mm": LENGTH,
            "track_count": 2,
            "track_spacing_mm": SPACING,
            "parallel_side": "Left of travel",
        },
        "units": {
            "coordinate_and_length": "mm",
            "heading_rad": "radians",
            "heading_deg": "degrees",
            "unit_tangent_and_normal": "dimensionless",
        },
        "evidence_limits": [
            "The inputs were chosen for this handbook, not taken from a runtime receipt.",
            "No workbench module, project test, validator, macro or FreeCAD process ran.",
            "Assertions check the independent illustration, not workbench implementation.",
            "Only mathematical centrelines are illustrated; strip and gauge are absent.",
            "The illustration does not establish GUI behaviour or physical fit.",
        ],
        "floating_point_note": (
            "JSON retains the calculated Python binary floating-point values without "
            "decimal rounding. The Reverse calculation includes the small sin(pi) "
            "residual. SVG coordinate labels round to whole millimetres."
        ),
        "illustration_check_absolute_tolerance_mm": 1e-10,
        "directions": examples,
    }
    (ASSETS / "straight-route-example-values.json").write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


def coordinate_label(point):
    return "({:.0f}, {:.0f})".format(*point)


def draw_panel(axis, example):
    reverse = example["direction"] == "Reverse"
    sign = -1 if reverse else 1
    axis.set_xlim(-600, 800)
    axis.set_ylim(75, 325)
    axis.set_aspect("equal", adjustable="box")
    axis.set_xticks([-500, -300, -100, 100, 300, 500, 700])
    axis.set_yticks([100, 200, 300])
    axis.grid(color="#e2e7ec", linewidth=0.6)
    axis.set_axisbelow(True)
    axis.axvline(DATUM[0], color="#b7c2ca", linestyle=(0, (3, 3)), linewidth=0.9)
    axis.set_xlabel("X (mm)", labelpad=4)
    axis.set_ylabel("Y (mm)", labelpad=6)
    axis.tick_params(labelsize=9, length=3, color="#8798a5")
    axis.spines["left"].set_color("#8798a5")
    axis.spines["bottom"].set_color("#8798a5")
    axis.set_title(
        "{}: heading {:.0f}°".format(example["direction"], example["heading_deg"]),
        loc="left", fontsize=12, fontweight="bold", pad=11,
    )

    for index, (track, colour) in enumerate(zip(example["tracks"], COLOURS)):
        start = track["start_mm"]
        finish = track["finish_mm"]
        axis.plot(
            [start[0], finish[0]], [start[1], finish[1]],
            color=colour, linewidth=2.2, marker="o", markersize=4, zorder=3,
        )
        midpoint = [(a + b) / 2.0 for a, b in zip(start, finish)]
        axis.annotate(
            "", xy=(midpoint[0] + sign * 50, midpoint[1]),
            xytext=(midpoint[0] - sign * 50, midpoint[1]),
            arrowprops={"arrowstyle": "-|>", "color": colour,
                        "linewidth": 2.2, "mutation_scale": 16},
            zorder=4,
        )
        outward = sign * (-1 if index == 0 else 1)
        label_offset = outward * 12
        vertical_alignment = "bottom" if outward > 0 else "top"
        for point, label in (
            (start, ("Datum " if index == 0 else "") + coordinate_label(start)),
            (midpoint, "Track {}".format(index + 1)),
            (finish, coordinate_label(finish)),
        ):
            axis.annotate(
                label, xy=point, xytext=(0, label_offset), textcoords="offset points",
                ha="center", va=vertical_alignment, color=colour, fontsize=10,
            )

    axis.plot(
        *DATUM, marker="o", markersize=7, markeredgewidth=1.5,
        markerfacecolor="white", markeredgecolor=COLOURS[0], zorder=5,
    )
    dimension_x = DATUM[0] - sign * 70
    second_start = example["tracks"][1]["start_mm"]
    for y in (DATUM[1], second_start[1]):
        axis.plot([dimension_x - 8, DATUM[0]], [y, y],
                  color="#788995", linewidth=0.7, zorder=2)
    axis.annotate(
        "", xy=(dimension_x, second_start[1]), xytext=(dimension_x, DATUM[1]),
        arrowprops={"arrowstyle": "<->", "color": INK, "linewidth": 1.0,
                    "shrinkA": 0, "shrinkB": 0, "mutation_scale": 9},
    )
    axis.text(
        dimension_x - sign * 35, (DATUM[1] + second_start[1]) / 2,
        "50 mm\nLeft of travel", ha="right" if sign > 0 else "left",
        va="center", fontsize=10, linespacing=1.35,
    )


def draw_figure(examples):
    # Keep every generated cache/inspection file under this ignored directory.
    os.environ["MPLCONFIGDIR"] = str(CHECKS / "matplotlib-cache")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "svg.fonttype": "none",
        "svg.hashsalt": "tracktemplate-straight-route-direction",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
    })
    figure = plt.figure(figsize=(10.8, 6.1), facecolor="white")
    figure.text(0.095, 0.972, "Direction changes the side of a parallel track",
                fontsize=16, fontweight="bold", va="top")
    figure.text(0.095, 0.925,
                "Independent tracks · rotation 0° · length 600 mm · spacing 50 mm",
                fontsize=11, va="top")
    width = 0.86
    height = width * 10.8 / 6.1 * 250.0 / 1400.0
    axes = [figure.add_axes((0.095, bottom, width, height)) for bottom in (0.57, 0.18)]
    for axis, example in zip(axes, examples):
        draw_panel(axis, example)
    figure.text(
        0.095, 0.057,
        "Plan view · identical axes and equal X/Y scale · coordinates rounded to whole mm",
        fontsize=9.5,
    )
    figure.text(
        0.095, 0.028,
        "Mathematical centrelines; no strip or gauge geometry. No workbench or FreeCAD execution.",
        fontsize=9.5,
    )
    figure.canvas.draw()
    assert axes[0].get_xlim() == axes[1].get_xlim()
    assert axes[0].get_ylim() == axes[1].get_ylim()
    for axis in axes:
        origin = axis.transData.transform((0, 0))
        x_unit = axis.transData.transform((1, 0))
        y_unit = axis.transData.transform((0, 1))
        assert math.isclose(
            math.dist(origin, x_unit), math.dist(origin, y_unit), rel_tol=1e-12,
        ), "The plan view must have equal X/Y scale."
    svg = ASSETS / "straight-route-direction.svg"
    figure.savefig(svg, metadata={
        "Date": None,
        "Title": "Independent straight tracks: Forward and Reverse",
        "Description": (
            "Independent centreline arithmetic derived from tracktemplate@"
            + SOURCE_REVISION
            + "; not workbench execution. Same axes and equal X/Y scale."
        ),
        "Rights": "GPL-3.0-or-later; Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.",
    })
    svg.write_text(
        "\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())
        + "\n", encoding="utf-8",
    )
    figure.savefig(CHECKS / "straight-route-direction.png", dpi=160)
    plt.close(figure)


def main():
    CHECKS.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    examples = [direction_values(), direction_values(reverse=True)]
    check_values(examples)
    save_values(examples)
    draw_figure(examples)
    print("Straight-track illustration: coordinates, 600 mm lengths and 50 mm left offsets checked.")
    print("The check covers independent documentation arithmetic, not workbench behaviour.")


if __name__ == "__main__":
    main()
