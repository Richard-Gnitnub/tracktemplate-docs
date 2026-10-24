#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
"""Draw the handbook's independent mathematical illustration.

Run manually with Python and Matplotlib 3.10.8. The Sphinx build uses the
committed SVG files and does not need Matplotlib. No workbench module, validator,
macro or FreeCAD process is imported or executed here.

Equations and retained fixture: tracktemplate@7965bfc4671668f889c1f43fb8336c5146c3f5cf,
tracktemplate/domain/alignment.py:55-138,322-329,863-1003 and
tests/validate_phase1_alignment.py:92-120. This illustrates smooth mathematical
centrelines; it does not reproduce the host's sampled geometry or validate it.
"""

import json
import math
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "_static" / "figures"
CHECKS = ROOT / "_build" / "generation-review"
SOURCE_REVISION = "7965bfc4671668f889c1f43fb8336c5146c3f5cf"
MAIN_RADIUS = 600.0
MAIN_LENGTH = 600.0
OUTSIDE_RADIUS = 655.0
MATCHED_LENGTH = 559.4102547270278  # Retained Phase 1 fixture, not a new solve.
TOTAL_ANGLE = math.pi / 2.0


def displacement(length, radius, fraction=1.0, exit_curve=False, steps=240):
    """Independently integrate the stated Euler heading equation to L*fraction."""
    alpha = length / (2.0 * radius)
    result = []
    for trig in (math.cos, math.sin):
        total = 0.0
        for index in range(steps + 1):
            u = fraction * index / steps
            heading = alpha * (2.0 * u - u * u if exit_curve else u * u)
            weight = 1 if index in (0, steps) else 4 if index % 2 else 2
            total += weight * trig(heading)
        result.append(length * fraction * total / (3.0 * steps))
    return tuple(result)


def circle_centre():
    x, y = displacement(MAIN_LENGTH, MAIN_RADIUS)
    alpha = MAIN_LENGTH / (2.0 * MAIN_RADIUS)
    return x - MAIN_RADIUS * math.sin(alpha), y + MAIN_RADIUS * math.cos(alpha)


def example_values(radius, length):
    cx, cy = circle_centre()
    x, y = displacement(length, radius)
    alpha = length / (2.0 * radius)
    circular_angle = TOTAL_ANGLE - 2.0 * alpha
    return {
        "radius_mm": radius,
        "transition_length_each_mm": length,
        "transition_angle_each_rad": alpha,
        "transition_angle_each_deg": math.degrees(alpha),
        "start_x_mm": cx + radius * math.sin(alpha) - x,
        "start_y_mm": cy - radius * math.cos(alpha) - y,
        "circular_angle_deg": math.degrees(circular_angle),
        "circular_length_mm": radius * circular_angle,
        "core_length_mm": 2.0 * length + radius * circular_angle,
    }


def centreline(radius, length):
    """Evaluate a smooth centreline for drawing, using 101 points per section."""
    cx, cy = circle_centre()
    values = example_values(radius, length)
    alpha = values["transition_angle_each_rad"]
    points = []
    for index in range(101):
        x, y = displacement(length, radius, index / 100.0)
        points.append((values["start_x_mm"] + x, values["start_y_mm"] + y))
    for index in range(1, 101):
        heading = alpha + (TOTAL_ANGLE - 2.0 * alpha) * index / 100.0
        points.append((cx + radius * math.sin(heading), cy - radius * math.cos(heading)))
    heading = TOTAL_ANGLE - alpha
    circle_end = points[-1]
    for index in range(1, 101):
        x, y = displacement(length, radius, index / 100.0, exit_curve=True)
        points.append((
            circle_end[0] + x * math.cos(heading) - y * math.sin(heading),
            circle_end[1] + x * math.sin(heading) + y * math.cos(heading),
        ))
    return points


def save_svg(figure, filename):
    """Keep generated SVG paths reproducible and free of trailing whitespace."""
    path = ASSETS / filename
    figure.savefig(path, metadata={"Date": None})
    path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")


def draw_figures():
    CHECKS.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(CHECKS / "matplotlib-cache"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.size": 11,
        "font.family": "DejaVu Sans",
        "svg.fonttype": "none",
        "svg.hashsalt": "tracktemplate-alignment-example",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.labelcolor": "#263747",
        "text.color": "#263747",
    })
    main = example_values(MAIN_RADIUS, MAIN_LENGTH)
    matched = example_values(OUTSIDE_RADIUS, MATCHED_LENGTH)
    manual = example_values(OUTSIDE_RADIUS, 600.0)
    cx, cy = circle_centre()
    # Compare independently calculated values with retained source fixtures.
    assert abs(cx - 297.51728975552163) < 1.0e-9
    assert abs(cy - 624.7779655573173) < 1.0e-9
    assert abs(matched["start_y_mm"] + 50.0) < 1.0e-8
    # Increasing quadrature resolution must preserve the printed 0.001 mm values.
    for length, radius in ((600.0, 600.0), (MATCHED_LENGTH, 655.0), (600.0, 655.0)):
        low = displacement(length, radius)
        high = displacement(length, radius, steps=1920)
        assert all(abs(a - b) < 1.0e-6 for a, b in zip(low, high))
    data = {
        "description": "Independent handbook arithmetic; not a workbench or GUI test result.",
        "source_revision": SOURCE_REVISION,
        "retained_matched_length_mm": MATCHED_LENGTH,
        "circle_centre_mm": [cx, cy],
        "main": main,
        "outside_matched": matched,
        "outside_manual_600": manual,
        "drawing": "Smooth Euler equations, 101 drawing points per section; no host sampling claim.",
    }
    (ASSETS / "alignment-example-values.json").write_text(json.dumps(data, indent=2) + "\n")
    main_xy = centreline(MAIN_RADIUS, MAIN_LENGTH)
    outside_xy = centreline(OUTSIDE_RADIUS, MATCHED_LENGTH)
    blue, orange, grey = "#245b86", "#b54818", "#778592"

    fig, ax = plt.subplots(figsize=(9.2, 8.0), constrained_layout=True)
    ax.plot(*zip(*main_xy), color=blue, linewidth=2.5, label="Main: R 600 mm; L 600 mm each end")
    ax.plot(*zip(*outside_xy), color=orange, linewidth=2.5, label="Outside: R 655 mm; L 559.410 mm each end")
    for points, colour in ((main_xy, blue), (outside_xy, orange)):
        ax.plot([-200, points[0][0]], [points[0][1]] * 2, "--", color=colour, linewidth=1.2)
        ax.plot([points[-1][0]] * 2, [points[-1][1], 1190], "--", color=colour, linewidth=1.2)
        ax.scatter(*points[0], color=colour, s=25, zorder=3)
    ax.scatter(cx, cy, marker="+", color=grey, s=95)
    ax.annotate("Common circle centre C", (cx, cy), xytext=(cx - 200, cy + 80),
                arrowprops={"arrowstyle": "-", "color": grey})
    middle = math.pi / 4.0
    radial_main = (cx + MAIN_RADIUS * math.sin(middle), cy - MAIN_RADIUS * math.cos(middle))
    radial_outer = (cx + OUTSIDE_RADIUS * math.sin(middle), cy - OUTSIDE_RADIUS * math.cos(middle))
    ax.plot([cx, radial_outer[0]], [cy, radial_outer[1]], ":", color=grey, linewidth=1)
    ax.annotate("", xy=radial_outer, xytext=radial_main,
                arrowprops={"arrowstyle": "<->", "color": "#263747", "shrinkA": 0, "shrinkB": 0})
    radial_mid = tuple((a + b) / 2 for a, b in zip(radial_main, radial_outer))
    ax.annotate("55 mm radial spacing", xy=radial_mid, xytext=(cx + 90, cy - 230),
                ha="right", arrowprops={"arrowstyle": "-", "color": grey})
    ax.annotate("", xy=(-110, -50), xytext=(-110, 0),
                arrowprops={"arrowstyle": "<->", "color": "#263747", "shrinkA": 0, "shrinkB": 0})
    ax.text(-180, 65, "50 mm entry spacing", ha="left")
    ax.annotate("", xy=(outside_xy[-1][0], 1100), xytext=(main_xy[-1][0], 1100),
                arrowprops={"arrowstyle": "<->", "color": "#263747", "shrinkA": 0, "shrinkB": 0})
    ax.text(1040, 1095, "50 mm\nexit spacing", va="center")
    ax.annotate("Travel", xy=(200, 8), xytext=(90, 8), color=blue,
                arrowprops={"arrowstyle": "->", "color": blue})
    ax.set(xlim=(-230, 1250), ylim=(-150, 1260), xlabel="Local X (mm)", ylabel="Local Y (mm)")
    ax.set_aspect("equal")
    ax.grid(color="#e5eaf0", linewidth=0.7)
    ax.set_title("One common circle centre; different transition lengths", loc="left", pad=16, fontsize=15)
    ax.plot([], [], "--", color=grey, linewidth=1.2, label="Dashed: tangent extensions for measurement")
    ax.legend(loc="upper left", frameon=False, fontsize=10)
    save_svg(fig, "euler-two-track-example.svg")
    fig.savefig(CHECKS / "euler-two-track-example.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.2, 5.0), constrained_layout=True)
    for values, colour, style, label in (
        (main, blue, "-", "Main: L 600 mm; R 600 mm"),
        (matched, orange, "--", "Outside matched: L 559.410 mm; R 655 mm"),
    ):
        length = values["transition_length_each_mm"]
        end_circle = length + values["circular_length_mm"]
        end = values["core_length_mm"]
        ax.plot([0, length, end_circle, end], [0, 1 / values["radius_mm"], 1 / values["radius_mm"], 0],
                color=colour, linestyle=style, linewidth=2.7, label=label)
    ax.annotate("Entry\nCurvature increases linearly", xy=(280, 280 / (600 * 600)), xytext=(40, 0.00125),
                fontsize=10, arrowprops={"arrowstyle": "-", "color": grey})
    ax.annotate("Constant-radius section", xy=(760, 1 / 600), xytext=(700, 0.00187),
                ha="center", fontsize=10, arrowprops={"arrowstyle": "-", "color": grey})
    ax.annotate("Exit\nCurvature decreases linearly", xy=(1240, (main["core_length_mm"] - 1240) / (600 * 600)),
                xytext=(1580, 0.00125), ha="right", fontsize=10,
                arrowprops={"arrowstyle": "-", "color": grey})
    ax.set(xlim=(-30, 1630), ylim=(-0.00007, 0.002), xlabel="Station from each track's own core start (mm)",
           ylabel="Curvature (1/mm)")
    ax.ticklabel_format(axis="y", style="sci", scilimits=(-3, -3), useMathText=True)
    ax.grid(color="#e5eaf0", linewidth=0.7)
    ax.set_title("Euler curvature changes continuously at the joins", loc="left", pad=16, fontsize=15)
    ax.legend(loc="lower center", frameon=False, fontsize=10)
    save_svg(fig, "euler-curvature-example.svg")
    fig.savefig(CHECKS / "euler-curvature-example.png", dpi=140)
    plt.close(fig)
    print(json.dumps({"circle_centre_mm": [cx, cy], "matched_length_mm": MATCHED_LENGTH,
                      "manual_600_spacing_mm": -manual["start_y_mm"], "fixture_comparisons": "passed"}, indent=2))


if __name__ == "__main__":
    draw_figures()
