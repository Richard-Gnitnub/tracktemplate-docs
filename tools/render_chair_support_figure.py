#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
"""Draw and check the handbook's independent model-support illustration.

Run with the Python standard library only:
    python tools/render_chair_support_figure.py
    python tools/render_chair_support_figure.py --check-only

The timber, rail and chair position form a synthetic plan-only fixture in model
millimetres. Exact rational arithmetic checks the transformed support rectangle,
clearances, bounded side extension, over-limit variant and unresolved end
overhang. No workbench module, validator, test or process is imported or run.
The rounded symbol in the SVG is schematic; its details are deliberately absent.
This script does not establish a complete turnout recipe or physical fit.

Source interpretation: tracktemplate revision
7965bfc4671668f889c1f43fb8336c5146c3f5cf, retained macro
model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro:
489 (scale), 43374-43404 (clearances), 44064-44078 (fixed rail profile),
44409-44554 (dimensions and transform), 44558-44656 (bounded side extensions),
44659-44720 (effective support), 44894-44916 (unsupported ends),
46231-46307 (support preparation), 46427-46486 (failed layout result),
47857-47871 (final support application), 48028-48120 (cached symbols), and
48123-48283 (final display and separate validation-envelope metadata).
"""

import argparse
from dataclasses import dataclass
from fractions import Fraction
from html import escape
import json
from math import ceil
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "_static" / "figures" / "chair-support-example.svg"
SOURCE_REVISION = "7965bfc4671668f889c1f43fb8336c5146c3f5cf"
SOURCE_FILE = (
    "model_railway_curve_template_multitrack_v10_2a8a7b15_"
    "chair_performance_and_representation.FCMacro"
)
SOURCE_URL = (
    f"https://github.com/Richard-Gnitnub/tracktemplate/blob/"
    f"{SOURCE_REVISION}/{SOURCE_FILE}"
)
F = Fraction
OUTWARD = (F(3, 5), F(4, 5))
LOCAL_Y = (-F(4, 5), F(3, 5))
TANGENT = (F(4, 5), -F(3, 5))
GAUGE_NORMAL = (-F(3, 5), -F(4, 5))
MARGIN, INCREMENT, LIMIT = F("0.15"), F("0.05"), F(2)
INK = "#17364d"
MUTED = "#455b68"
RAIL = "#27636c"
SYMBOL = "#8aa5b8"
SYMBOL_FILL = "#e5edf3"
TIMBER_FILL = "#e9edef"
TIMBER_STROKE = "#647680"
SUPPORT = "#9b560c"
SUPPORT_FILL = "#f7deb4"
FAILURE = "#ad282c"


@dataclass(frozen=True)
class Example:
    """One exact calculation fixture, not a workbench state or execution."""

    support: tuple
    timber_length: Fraction
    timber_width: Fraction
    original_bounds: tuple
    local_bounds: tuple
    footprint: tuple
    rail_start: tuple
    rail_end: tuple
    gauge_face: tuple
    outer_face: tuple
    clearances: dict
    raw_extensions: tuple
    rounded_extensions: tuple
    limit_exceeded: bool
    applied_extensions: tuple
    effective_width: Fraction
    effective_centre: tuple
    effective_bounds: tuple
    effective_clearances: dict
    unresolved_ends: tuple


def dot(first, second):
    return sum(a * b for a, b in zip(first, second))


def shifted(point, direction, distance):
    return tuple(value + distance * component for value, component in zip(point, direction))


def side_rounding(amount):
    """Check the stated 0.05 mm upward rule with its source numerical guards."""
    if amount <= F(1, 10**9):
        return F(0)
    return ceil((amount - F(1, 10**12)) / INCREMENT) * INCREMENT


def make_example(support, timber_length):
    """Calculate only this rectangular support fixture with exact fractions."""
    timber_width = F(4)
    original = (-timber_width / 2, -timber_length / 2,
                timber_width / 2, timber_length / 2)
    inch = F("25.4") / F("76.2")
    gauge_face_x = -F("0.90") / 2
    xmin = gauge_face_x - F("5.25") * inch
    xmax = gauge_face_x + F("9.25") * inch
    half = 4 * inch
    local_bounds = (xmin, -half, xmax, half)
    local_corners = ((xmin, -half), (xmax, -half), (xmax, half), (xmin, half))
    footprint = tuple(
        tuple(support[index] + x * OUTWARD[index] + y * LOCAL_Y[index]
              for index in (0, 1))
        for x, y in local_corners
    )
    xs, ys = zip(*footprint)
    clearances = {
        "approach": min(xs) + timber_width / 2,
        "exit": timber_width / 2 - max(xs),
        "near": min(ys) + timber_length / 2,
        "far": timber_length / 2 - max(ys),
    }
    raw = tuple(max(F(0), MARGIN - clearances[side]) for side in ("approach", "exit"))
    rounded = tuple(side_rounding(value) for value in raw)
    limit_exceeded = max(rounded) > LIMIT + F(1, 10**9)
    applied = (F(0), F(0)) if limit_exceeded else rounded
    approach, exit_side = applied
    effective_width = timber_width + approach + exit_side
    centre_shift = (exit_side - approach) / 2
    effective_bounds = (
        original[0] - approach, original[1],
        original[2] + exit_side, original[3],
    )
    effective_clearances = dict(clearances)
    effective_clearances["approach"] += approach
    effective_clearances["exit"] += exit_side
    unresolved_ends = tuple(max(F(0), -clearances[end]) for end in ("near", "far"))
    rail_start = shifted(support, TANGENT, F(-10))
    rail_end = shifted(support, TANGENT, F(10))
    gauge_face = tuple(shifted(point, GAUGE_NORMAL, F("0.45"))
                       for point in (rail_start, rail_end))
    outer_face = tuple(shifted(point, GAUGE_NORMAL, -F("0.45"))
                       for point in (rail_start, rail_end))
    return Example(
        support, timber_length, timber_width, original, local_bounds, footprint,
        rail_start, rail_end, gauge_face, outer_face, clearances, raw, rounded,
        limit_exceeded, applied, effective_width, (centre_shift, F(0)),
        effective_bounds, effective_clearances, unresolved_ends,
    )


def checked_examples():
    """Assert independently derived exact values and their stated limits."""
    assert dot(OUTWARD, OUTWARD) == dot(LOCAL_Y, LOCAL_Y) == 1
    assert dot(TANGENT, TANGENT) == dot(GAUGE_NORMAL, GAUGE_NORMAL) == 1
    assert dot(OUTWARD, LOCAL_Y) == dot(TANGENT, GAUGE_NORMAL) == 0
    assert OUTWARD == tuple(-value for value in GAUGE_NORMAL)
    assert LOCAL_Y == (-OUTWARD[1], OUTWARD[0])

    bounded = make_example((F("0.60"), F(0)), F(30))
    over_limit = make_example((F("1.25"), F(0)), F(30))
    end_failure = make_example((F("0.60"), F(0)), F("5.50"))
    assert bounded.local_bounds == (-F(11, 5), -F(4, 3), F(79, 30), F(4, 3))
    assert bounded.footprint == (
        (F(26, 75), -F(64, 25)), (F(487, 150), F(98, 75)),
        (F(167, 150), F(218, 75)), (-F(134, 75), -F(24, 25)),
    )
    assert bounded.clearances == {
        "approach": F(16, 75), "exit": -F(187, 150),
        "near": F(311, 25), "far": F(907, 75),
    }
    assert bounded.raw_extensions == (0, F(419, 300))
    assert bounded.rounded_extensions == bounded.applied_extensions == (0, F(7, 5))
    assert not bounded.limit_exceeded
    assert bounded.effective_width == F(27, 5)
    assert bounded.effective_centre == (F(7, 10), 0)
    assert bounded.effective_bounds == (-2, -15, F(17, 5), 15)
    assert bounded.effective_clearances["exit"] == F(23, 150) >= MARGIN
    assert bounded.effective_clearances["approach"] == F(16, 75) >= MARGIN
    assert bounded.unresolved_ends == (0, 0)

    assert over_limit.clearances["approach"] == F(259, 300)
    assert over_limit.clearances["exit"] == -F(569, 300)
    assert over_limit.raw_extensions == (0, F(307, 150))
    assert over_limit.rounded_extensions == (0, F(41, 20))
    assert over_limit.limit_exceeded and over_limit.applied_extensions == (0, 0)
    assert over_limit.effective_width == 4 and over_limit.effective_centre == (0, 0)
    assert over_limit.effective_bounds == over_limit.original_bounds

    assert end_failure.footprint == bounded.footprint
    assert end_failure.applied_extensions == bounded.applied_extensions
    assert not end_failure.limit_exceeded
    assert end_failure.clearances["near"] == F(19, 100)
    assert end_failure.clearances["far"] == -F(47, 300)
    assert end_failure.unresolved_ends == (0, F(47, 300))
    assert end_failure.effective_clearances["far"] == -F(47, 300)
    assert end_failure.original_bounds[1::2] == end_failure.effective_bounds[1::2]
    # The earlier timber-aligned analytical rectangle would have positive
    # end clearance here. It is not the transformed physical support envelope.
    assert F("5.50") / 2 - F(29, 6) / 2 == F(1, 3)

    for example in (bounded, over_limit, end_failure):
        assert tuple((a + b) / 2 for a, b in zip(example.rail_start, example.rail_end)) == example.support
        for rail_point, gauge_point, outer_point in zip(
            (example.rail_start, example.rail_end), example.gauge_face, example.outer_face
        ):
            assert tuple((a + b) / 2 for a, b in zip(gauge_point, outer_point)) == rail_point
            assert tuple((a - b) / F("0.90") for a, b in zip(gauge_point, outer_point)) == GAUGE_NORMAL
        left, _near, right, _far = example.effective_bounds
        assert right - left == example.effective_width
        assert (left + right) / 2 == example.effective_centre[0]
    return bounded, over_limit, end_failure


@dataclass(frozen=True)
class View:
    """A Cartesian crop with the same scale on both axes."""

    top: Fraction
    left: Fraction = F(51)
    xmin: Fraction = F(-3)
    ymax: Fraction = F(7, 2)
    scale: Fraction = F(42)

    def point(self, point):
        x, y = point
        return self.left + (x - self.xmin) * self.scale, self.top + (self.ymax - y) * self.scale


def number(value):
    """Round display coordinates only; all fixture arithmetic stays rational."""
    return f"{float(value):.6f}".rstrip("0").rstrip(".") or "0"


def text(x, y, value, size=20, colour=INK, weight="400", anchor="start"):
    return (
        f'<text x="{number(x)}" y="{number(y)}" font-size="{size}" '
        f'fill="{colour}" font-weight="{weight}" text-anchor="{anchor}">'
        f'{escape(value)}</text>'
    )


def line(start, end, colour=MUTED, width=1.5, extra=""):
    return (
        f'<path d="M {number(start[0])} {number(start[1])} '
        f'L {number(end[0])} {number(end[1])}" '
        f'fill="none" stroke="{colour}" stroke-width="{width}"{extra}/>'
    )


def rectangle(bounds, view, fill, stroke="none", stroke_width=1.5):
    xmin, ymin, xmax, ymax = bounds
    x, y = view.point((xmin, ymax))
    return (
        f'<rect x="{number(x)}" y="{number(y)}" '
        f'width="{number((xmax - xmin) * view.scale)}" '
        f'height="{number((ymax - ymin) * view.scale)}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
    )


def polygon(points, view, colour, width=2.6, dashed=False):
    values = " ".join(f"{number(x)},{number(y)}" for x, y in map(view.point, points))
    dash = ' stroke-dasharray="7 4"' if dashed else ""
    return f'<polygon points="{values}" fill="none" stroke="{colour}" stroke-width="{width}"{dash}/>'


def schematic_symbol(example, view):
    """Draw a rounded base schematic, without claiming the source's wire mesh."""
    xmin, ymin, xmax, ymax = example.local_bounds
    x, y = view.point(example.support)
    matrix = " ".join(number(value) for value in (
        OUTWARD[0], -OUTWARD[1], LOCAL_Y[0], -LOCAL_Y[1], x, y,
    ))
    return (
        f'<rect x="{number(xmin * view.scale)}" y="{number(ymin * view.scale)}" '
        f'width="{number((xmax - xmin) * view.scale)}" '
        f'height="{number((ymax - ymin) * view.scale)}" '
        f'rx="{number(view.scale / 3)}" fill="{SYMBOL_FILL}" '
        f'stroke="{SYMBOL}" stroke-width="1.7" transform="matrix({matrix})"/>'
    )


def panel(top, height):
    return f'<rect x="16" y="{top}" width="448" height="{height}" rx="12" fill="#f6f8fa"/>'


def dimension(start, end, y, label, colour):
    return [
        line((start, y), (end, y), colour),
        line((start, y - 6), (start, y + 6), colour),
        line((end, y - 6), (end, y + 6), colour),
        text((start + end) / 2, y + 27, label, 20, colour, anchor="middle"),
    ]


def diagram(example, top, clip_id, failure=False):
    view = View(F(top))
    left, right = example.original_bounds[0], example.effective_bounds[2]
    support_point = view.point(example.support)
    parts = [
        f'<clipPath id="{clip_id}"><rect x="51" y="{top}" width="378" height="294"/></clipPath>',
        f'<g clip-path="url(#{clip_id})">',
        rectangle(example.original_bounds, view, TIMBER_FILL, TIMBER_STROKE),
        rectangle((F(2), example.original_bounds[1], right, example.original_bounds[3]),
                  view, SUPPORT_FILL),
        line(view.point((right, example.original_bounds[1])),
             view.point((right, example.original_bounds[3])), SUPPORT, 2.5),
        schematic_symbol(example, view),
        line(view.point(example.rail_start), view.point(example.rail_end), RAIL, 2,
             ' stroke-dasharray="11 4 2 4"'),
        polygon(example.footprint, view, FAILURE if failure else INK, dashed=True),
        f'<circle cx="{number(support_point[0])}" cy="{number(support_point[1])}" '
        f'r="4" fill="{RAIL}" stroke="#ffffff" stroke-width="1.5"/>',
    ]
    if failure:
        parts.append(rectangle(example.effective_bounds, view, "none", FAILURE, 2.7))
        corner = view.point(example.footprint[2])
        parts.extend([
            f'<circle cx="{number(corner[0])}" cy="{number(corner[1])}" r="4" fill="{FAILURE}"/>',
            line((corner[0] + 7, corner[1] - 3), (328, top + 12), FAILURE),
            text(334, top + 18, "End", 20, FAILURE, "700"),
            text(334, top + 43, "overhang", 20, FAILURE),
        ])
    parts.append('</g>')
    if not failure:
        # The 30 mm timber continues beyond this central crop. These marks
        # are view breaks, not the timber's physical near and far ends.
        for edge in (left, right):
            x = view.point((edge, F(0)))[0]
            for y in (top + 6, top + 288):
                parts.append(line((x - 5, y + 3), (x + 5, y - 3), MUTED, 2))
        start = view.point((F(-2), F(0)))[0]
        original_end = view.point((F(2), F(0)))[0]
        effective_end = view.point((right, F(0)))[0]
        parts.extend(dimension(start, original_end, top + 310, "4.00", MUTED))
        parts.extend(dimension(original_end, effective_end, top + 310, "1.40", SUPPORT))
    return parts


def render(examples):
    bounded, over_limit, end_failure = examples
    description = (
        "Three synthetic support-calculation cases in model millimetres, not captured FreeCAD output. "
        "The timber length axis is y and width axis is x. In the first case its centre is (0,0), "
        "width 4 and length 30. The chair support C=(0.6,0), intended rail tangent (4/5,-3/5), "
        "outward axis (3/5,4/5), gauge normal (-3/5,-4/5) and local y axis (-4/5,3/5) are explicit. "
        "At the retained source's scale 1:76.2 and fixed 0.90 mm rail head width, source-labelled "
        "code 1 has local support-rectangle x limits -11/5 and 79/30 and y limits plus/minus 4/3. "
        "Its transformed corners are (26/75,-64/25), (487/150,98/75), (167/150,218/75), "
        "and (-134/75,-24/25). With both automatic-support settings true, margin 0.15 and "
        "per-side limit 2, its approach extension is zero and exit need 419/300 rounds upwards "
        "to 1.40 in 0.05 mm steps. Effective width becomes 5.40 at centre (0.70,0); edges are "
        "x=-2 and x=3.4. Exit clearance becomes 23/150, approximately 0.153 mm. The first "
        "drawing crops the 30 mm timber to its centre; end stations remain y=plus/minus 15. "
        "The pale rounded base is a schematic symbol; the dashed polygon is the separate support "
        "rectangle used for the arithmetic. Both drawings use equal x/y scale at 42 pixels/mm. "
        "In case 2 the chair and its intended rail move together to C=(1.25,0). Exit need "
        "307/150 rounds to 2.05, above the 2 mm limit, so no side extension applies; source "
        "inspection predicts blocked support metadata with no new layout or chair solid. "
        "Case 3 restores C=(0.6,0) and shortens the timber to 5.50 mm. Side widening still "
        "passes, but far-end clearance remains -47/300, approximately -0.157 mm. The source "
        "can create a failed 2D layout with two critical findings for this one overhanging "
        "chair and red chair-envelope and effective-timber outlines. All three cases are "
        "independently checked rational arithmetic and source-inspected paths, not complete "
        "turnout recipes, GUI test results or evidence of physical fit or production readiness."
    )
    metadata = {
        "generator": "tools/render_chair_support_figure.py",
        "licence": "GPL-3.0-or-later",
        "source_revision": SOURCE_REVISION,
        "source_file": SOURCE_FILE,
        "source_url": SOURCE_URL,
        "source_lines": ["489", "43374-43404", "44064-44078", "44409-44554",
                         "44558-44656", "44659-44720", "44894-44916",
                         "46231-46307", "46427-46486", "47857-47871",
                         "48028-48120", "48123-48283"],
        "input_provenance": "Synthetic rectangular timber and explicit rail/chair axes; model mm",
        "settings": {
            "model_support_recommendations_enabled": True,
            "model_support_auto_apply_enabled": True,
            "model_support_edge_margin_mm": str(MARGIN),
            "maximum_extension_per_side_mm": str(LIMIT),
            "rounding_increment_mm": str(INCREMENT),
        },
        "bounded_exit_extension_mm": str(bounded.applied_extensions[1]),
        "over_limit_required_exit_extension_mm": str(over_limit.rounded_extensions[1]),
        "unresolved_far_end_mm": str(end_failure.unresolved_ends[1]),
        "checked_scope": "Independent rational example arithmetic and exact SVG reproduction",
        "representation": "Schematic rounded base with source local bounds; symbol details omitted",
        "limits": "No workbench execution, captured FreeCAD output, complete turnout recipe or physical fit proof",
    }
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 1578" width="480" height="1578" style="max-width:100%;height:auto" role="img" aria-labelledby="title desc">',
        '<!-- SPDX-License-Identifier: GPL-3.0-or-later -->',
        '<!-- Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors. -->',
        '<!-- Generated by tools/render_chair_support_figure.py; edit that source. -->',
        '<title id="title">Skewed chair envelope and bounded model support</title>',
        '<desc id="desc">' + escape(description) + '</desc>',
        '<metadata>' + escape(json.dumps(metadata, indent=2, sort_keys=True)) + '</metadata>',
        '<rect width="480" height="1578" fill="#ffffff"/>',
        '<g font-family="DejaVu Sans, sans-serif">',
        text(24, 34, "Chair support at a skew", 26, weight="700"),
        text(24, 64, "Synthetic geometry · model millimetres", 20, MUTED),
        text(24, 91, "Source-inspected; no FreeCAD output", 20, MUTED),
        line((25, 119), (65, 119), INK, 2.6, ' stroke-dasharray="7 4"'),
        text(78, 126, "Transformed validation rectangle", 20),
        f'<rect x="25" y="141" width="40" height="13" rx="4" fill="{SYMBOL_FILL}" stroke="{SYMBOL}" stroke-width="1.7"/>',
        text(78, 155, "Rounded symbol (schematic)", 20),
        f'<rect x="25" y="168" width="40" height="13" fill="{SUPPORT_FILL}" stroke="{SUPPORT}"/>',
        text(78, 182, "Model-only width increase", 20),
        panel(199, 526),
        text(32, 235, "1  Width only: add 1.40 mm", 23, weight="700"),
        text(32, 265, "Timber 4 × 30; C = (0.60, 0)", 20, MUTED),
        text(32, 293, "Centre crop; ends stay at y = ±15", 20, MUTED),
        *diagram(bounded, 310, "bounded-crop"),
        text(32, 667, "Exit clearance: −1.247 → +0.153 mm", 20),
        text(32, 695, "Width 5.40 mm; timber centre x = 0.70", 20),
        panel(744, 196),
        text(32, 780, "2  Over limit: no side widening", 23, weight="700"),
        text(32, 811, "Move C and rail to x = 1.25 mm.", 20, MUTED),
        text(32, 842, "Exit need: 2.047 → 2.05 mm", 22, weight="700"),
        text(32, 872, "2.05 > 2.00 limit: support blocked.", 20, FAILURE),
        text(32, 901, "The original width stays 4.00 mm.", 20),
        text(32, 929, "No new layout or 3D chair is built.", 20),
        panel(959, 536),
        text(32, 995, "3  An end overhang remains", 23, weight="700"),
        text(32, 1026, "C = (0.60, 0); timber length 5.50 mm.", 20, MUTED),
        text(32, 1055, "The same 1.40 mm side increase passes.", 20, MUTED),
        *diagram(end_failure, 1080, "end-failure-crop", failure=True),
        text(32, 1409, "Far end after widening: −0.157 mm", 20, FAILURE, "700"),
        text(32, 1439, "A failed 2D layout can show red outlines", 20),
        text(32, 1467, "for the chair rectangle and its timber.", 20),
        text(24, 1530, "x → timber width · y ↑ timber length", 20, MUTED),
        text(24, 1560, "Independent arithmetic; no physical fit proof.", 19, MUTED),
        '</g>',
        '</svg>',
    ]
    content = "\n".join(parts) + "\n"
    ET.fromstring(content)
    return content


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-only", action="store_true",
        help="check rational arithmetic and exact saved SVG; write nothing",
    )
    args = parser.parse_args()
    expected = render(checked_examples())
    if args.check_only:
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != expected.encode("utf-8"):
            parser.error("Saved SVG is missing or differs; run this script without --check-only")
        print("Chair support figure: rational arithmetic and reproducible SVG checks passed.")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(expected, encoding="utf-8")
        print(f"Wrote {OUTPUT.relative_to(ROOT)}; illustration rational arithmetic checks passed.")


if __name__ == "__main__":
    main()
