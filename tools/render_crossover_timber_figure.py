#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
"""Draw and check the handbook's independent crossover timber illustration.

Run with the Python standard library only:
    python tools/render_crossover_timber_figure.py
    python tools/render_crossover_timber_figure.py --check-only

The fixed rectangles are illustrative model dimensions, not captured REA or
FreeCAD output. No workbench module, resolver, test or process is executed.
The arithmetic checks concern this figure; they do not validate the product.

The chapter explains the relevant gates in tracktemplate at revision
7965bfc4671668f889c1f43fb8336c5146c3f5cf, retained macro
model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro:
30580-30598 (body overlap), 31148-31153 (shared width), 32980-32991
(original support centre), 33031-33050 (pair clearance), 33304-33325
(pair movement bounds). This script performs elementary rectangle arithmetic,
not a reimplementation of those routines or their whole-arrangement checks.
"""

import argparse
from dataclasses import dataclass
from html import escape
import math
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "_static" / "figures" / "crossover-timber-pair.svg"
INK = "#122433"
MUTED = "#405363"
BLUE = "#245b86"
ORANGE = "#b54818"
PURPLE = "#76508c"


@dataclass(frozen=True)
class Rectangle:
    """An axis-aligned rectangle in the illustration's model millimetres."""

    xmin: float
    ymin: float
    width: float
    length: float

    @property
    def xmax(self):
        return self.xmin + self.width

    @property
    def ymax(self):
        return self.ymin + self.length

    @property
    def centre(self):
        return self.xmin + self.width / 2, self.ymin + self.length / 2

    def shifted(self, distance):
        return Rectangle(self.xmin + distance, self.ymin, self.width, self.length)

    def contains(self, point):
        return self.xmin <= point[0] <= self.xmax and self.ymin <= point[1] <= self.ymax


ORIGINAL = (Rectangle(-1, -15, 2, 30), Rectangle(0, -5, 2, 30))
MINIMUM_GAP = 0.50
WIDTH_ALLOWANCE = 0.35
STRICT_LIMIT = 0.25
PAIR_INCREMENT = 0.25


def overlap(first, second):
    """Return the elementary rectangular intersection, if it has area."""
    xmin = max(first.xmin, second.xmin)
    ymin = max(first.ymin, second.ymin)
    width = min(first.xmax, second.xmax) - xmin
    length = min(first.ymax, second.ymax) - ymin
    return Rectangle(xmin, ymin, width, length) if width > 0 and length > 0 else None


def checked_values():
    """Check this chosen example independently, without searching for a solution."""
    first, second = ORIGINAL
    intersection = overlap(first, second)
    station_offset = second.centre[0] - first.centre[0]
    enclosing_width = max(first.xmax, second.xmax) - min(first.xmin, second.xmin)
    allowed_width = max(first.width, second.width) + WIDTH_ALLOWANCE
    required_spacing = (first.width + second.width) / 2 + MINIMUM_GAP
    added_separation = required_spacing - station_offset
    movements = (-added_separation / 2, added_separation / 2)
    candidate = tuple(rect.shifted(move) for rect, move in zip(ORIGINAL, movements))
    gap = candidate[1].xmin - candidate[0].xmax

    def close(actual, expected, label):
        # This tolerance checks illustration arithmetic, not product geometry.
        if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-10):
            raise ValueError(f"{label}: expected {expected}, got {actual}")

    if intersection is None:
        raise ValueError("The original rectangles must intersect")
    overlap_area = intersection.width * intersection.length
    close(overlap_area, 20.0, "Overlap area / mm²")
    smaller_area = min(first.width * first.length, second.width * second.length)
    close(overlap_area / smaller_area, 1 / 3, "Coverage of the smaller body")
    intersection_threshold = 0.05 ** 2
    close(intersection_threshold, 0.0025, "Body intersection threshold / mm²")
    if overlap_area <= intersection_threshold or overlap_area / smaller_area >= 0.98:
        raise ValueError("The pair must intersect without reaching 98% coverage")
    close(enclosing_width, 3.0, "Enclosing width / mm")
    close(allowed_width, 2.35, "Allowed width / mm")
    if enclosing_width <= allowed_width:
        raise ValueError("The original pair must fail the shared width gate")
    close(station_offset, 1.0, "Initial station offset / mm")
    close(required_spacing, 2.5, "Required centre spacing / mm")
    close(added_separation, 1.5, "Additional pair separation / mm")
    close(movements[0], -0.75, "A movement / mm")
    close(movements[1], 0.75, "B movement / mm")
    close(gap, 0.50, "Candidate gap / mm")
    close(added_separation / PAIR_INCREMENT, 6.0, "Pair separation increments")
    if station_offset + added_separation - PAIR_INCREMENT >= required_spacing:
        raise ValueError("The preceding pair increment must remain insufficient")
    if overlap(*candidate) is not None:
        raise ValueError("The candidate rectangles must not intersect")
    for original, moved, movement in zip(ORIGINAL, candidate, movements):
        if not moved.contains(original.centre) or abs(movement) > 1.5:
            raise ValueError("Candidate loses a support centre or exceeds 1.50 mm")
    close(STRICT_LIMIT, 0.25, "Strict per-record movement / mm")
    strict_spacing = station_offset + 2 * STRICT_LIMIT
    close(strict_spacing, 1.5, "Largest spacing under strict limits / mm")
    if strict_spacing >= required_spacing:
        raise ValueError("Strict movement limits must leave this pair unresolved")

    # A separate chapter variant changes only B's x centre from 1 to 0.25.
    # Check its enclosing rectangle; do not model a shared-timber resolver.
    shifted_second = second.shifted(-0.75)
    variant_xmin = min(first.xmin, shifted_second.xmin)
    variant_xmax = max(first.xmax, shifted_second.xmax)
    variant_ymin = min(first.ymin, shifted_second.ymin)
    variant_ymax = max(first.ymax, shifted_second.ymax)
    variant_width = variant_xmax - variant_xmin
    close(shifted_second.centre[0], 0.25, "Variant B x centre / mm")
    close(variant_width, 2.25, "Variant enclosing width / mm")
    close(variant_ymax - variant_ymin, 40.0, "Variant enclosing length / mm")
    close((variant_xmin + variant_xmax) / 2, 0.125, "Variant enclosing x centre / mm")
    close((variant_ymin + variant_ymax) / 2, 5.0, "Variant enclosing y centre / mm")
    if variant_width > allowed_width:
        raise ValueError("The variant must fit the declared shared width allowance")
    return candidate


def number(value):
    return f"{value:g}"


def text(x, y, value, size=16, colour=INK, weight="400", anchor="start"):
    return (
        f'<text x="{number(x)}" y="{number(y)}" font-size="{size}" '
        f'fill="{colour}" font-weight="{weight}" text-anchor="{anchor}">'
        f'{escape(value)}</text>'
    )


def body(rectangle, x_origin, top, scale, y_max, fill, stroke, width=1.5):
    return (
        f'<rect x="{number(x_origin + rectangle.xmin * scale)}" '
        f'y="{number(top + (y_max - rectangle.ymax) * scale)}" '
        f'width="{number(rectangle.width * scale)}" '
        f'height="{number(rectangle.length * scale)}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'
    )


def support_dots(x_origin, top, scale, y_max, radius):
    dots = []
    for rectangle in ORIGINAL:
        x, y = rectangle.centre
        dots.append(
            f'<circle cx="{number(x_origin + x * scale)}" '
            f'cy="{number(top + (y_max - y) * scale)}" r="{radius}" '
            f'fill="{INK}" stroke="#ffffff" stroke-width="1.2"/>'
        )
    return dots


def panel(index, top, rectangles):
    """Draw whole bodies at 5 px/mm and a cropped detail at 20 px/mm."""
    plot_top = top + 106
    candidate = index == 2
    items = [
        f'<rect x="16" y="{top}" width="448" height="405" rx="12" fill="#f2f6f8"/>',
        text(32, top + 32, f"{index}  " + ("Candidate movement" if candidate else "Original pair"), 21, weight="700"),
        text(32, top + 58, "A −0.75 mm · B +0.75 mm" if candidate else "20 mm² overlap", 17, MUTED),
        text(32, top + 86, "Whole bodies", 16, MUTED),
        text(270, top + 86, "Detail ×4", 16, MUTED),
        # The enlarged crop is x=[-2.5, 3.5], y=[-1, 11]. Both views
        # use the same scale for x and y; the detail magnifies both by four.
        f'<path d="M 139.5 {top + 176} L 270 {plot_top} M 139.5 {top + 236} L 270 {plot_top + 240}" fill="none" stroke="#a3b4bf" stroke-width="1.2"/>',
    ]
    for rectangle, fill, colour in zip(rectangles, ("#dcebf6", "#f9e1d6"), (BLUE, ORANGE)):
        items.append(body(rectangle, 122, plot_top, 5, 25, fill, colour))
    intersection = overlap(*rectangles)
    if intersection is not None:
        items.append(body(intersection, 122, plot_top, 5, 25, "#c9b5d7", PURPLE, 1))
    items.extend(support_dots(122, plot_top, 5, 25, 2.7))
    items.extend([
        f'<rect x="109.5" y="{top + 176}" width="30" height="60" fill="none" stroke="#526776" stroke-width="1.2" stroke-dasharray="4 3"/>',
        f'<path d="M 72 {top + 302} V {top + 112} M 72 {top + 112} l -4 7 m 4 -7 l 4 7 M 85 {top + 329} H 160 M 160 {top + 329} l -7 -4 m 7 4 l -7 4" fill="none" stroke="#526776" stroke-width="1.5"/>',
        text(51, top + 119, "y", 16, MUTED),
        text(174, top + 334, "x", 16, MUTED),
        f'<clipPath id="detail-{index}"><rect x="270" y="{plot_top}" width="120" height="240"/></clipPath>',
        f'<g clip-path="url(#detail-{index})">',
        f'<rect x="270" y="{plot_top}" width="120" height="240" fill="#ffffff"/>',
    ])
    for rectangle, fill, colour in zip(rectangles, ("#dcebf6", "#f9e1d6"), (BLUE, ORANGE)):
        items.append(body(rectangle, 320, plot_top, 20, 11, fill, colour, 2))
    if intersection is not None:
        items.append(body(intersection, 320, plot_top, 20, 11, "#c9b5d7", PURPLE, 1))
    items.extend(support_dots(320, plot_top, 20, 11, 3.5))
    items.extend([
        '</g>',
        f'<rect x="270" y="{plot_top}" width="120" height="240" fill="none" stroke="#a3b4bf" stroke-width="1.2"/>',
    ])
    if candidate:
        items.extend([
            f'<path d="M 325 {top + 350} V {top + 365} M 335 {top + 350} V {top + 365} M 325 {top + 360} H 335" fill="none" stroke="#526776" stroke-width="1.3"/>',
            text(330, top + 390, "0.50 mm gap", 17, anchor="middle"),
        ])
    else:
        items.append(text(330, top + 390, "Overlap", 17, PURPLE, anchor="middle"))
    return items


def render(candidate):
    description = (
        "Independent rectangle arithmetic in model millimetres, not captured REA "
        "or FreeCAD output. A is 2 by 30 at centre (0, 0); B is 2 by 30 at (1, 10). "
        "The original overlap is 20 square millimetres. The shared enclosing width "
        "of 3 millimetres exceeds the allowed 2.35. The candidate moves A by -0.75 "
        "and B by +0.75 millimetres along x, giving a 0.50 millimetre gap. Black "
        "dots mark the unchanged original support centres in both panels. Each "
        "detail enlarges both x and y by four and crops to x=-2.5 to 3.5 and y=-1 "
        "to 11. Strict 0.25 millimetre movement limits cannot clear this pair. "
        "This illustration does not establish whole-arrangement acceptance."
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 1075" width="480" height="1075" role="img" aria-labelledby="title desc">',
        '<!-- SPDX-License-Identifier: GPL-3.0-or-later -->',
        '<!-- Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors. -->',
        '<!-- Generated by tools/render_crossover_timber_figure.py; edit that source. -->',
        '<title id="title">Illustrative crossover timber overlap and candidate movement</title>',
        '<desc id="desc">' + escape(description) + '</desc>',
        '<rect width="480" height="1075" fill="#ffffff"/>',
        '<g font-family="system-ui, sans-serif">',
        text(24, 33, "Crossover timber pair", 24, weight="700"),
        text(24, 60, "Illustrative geometry in model millimetres", 17, MUTED),
        text(24, 84, "Not captured REA or FreeCAD output", 15, MUTED),
        f'<rect x="26" y="105" width="18" height="14" fill="#dcebf6" stroke="{BLUE}" stroke-width="1.5"/>',
        text(53, 118, "A", 16, BLUE, "700"),
        f'<rect x="101" y="105" width="18" height="14" fill="#f9e1d6" stroke="{ORANGE}" stroke-width="1.5"/>',
        text(128, 118, "B", 16, ORANGE, "700"),
        f'<circle cx="197" cy="112" r="3.5" fill="{INK}"/>',
        text(211, 118, "Original centres", 16, MUTED),
        *panel(1, 140, ORIGINAL),
        *panel(2, 565, candidate),
        text(24, 1001, "x → longitudinal; y ↑ timber length", 16, MUTED),
        text(24, 1027, "Both views use equal x/y scale.", 15, MUTED),
        text(24, 1053, "Strict 0.25 mm limits cannot clear this pair.", 15, MUTED),
        '</g>',
        '</svg>',
    ]
    content = "\n".join(parts) + "\n"
    ET.fromstring(content)
    return content


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="check arithmetic and exact saved SVG; write nothing")
    args = parser.parse_args()
    expected = render(checked_values())
    if args.check_only:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            parser.error("Saved SVG is missing or differs; run this script without --check-only")
        print("Crossover timber figure: arithmetic and reproducible SVG checks passed.")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(expected, encoding="utf-8")
        print(f"Wrote {OUTPUT.relative_to(ROOT)}; illustration arithmetic checks passed.")


if __name__ == "__main__":
    main()
