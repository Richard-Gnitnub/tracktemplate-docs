#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors.
"""Draw and check the handbook's independent chair-position illustration.

Run with the Python standard library only:
    python tools/render_chair_analysis_figure.py
    python tools/render_chair_analysis_figure.py --check-only

The isolated T1 record, rail segment and timber dimensions are synthetic model
millimetres, not captured REA or FreeCAD output. Exact rational arithmetic
checks the declared projection, analytical rectangle, clearances and identity.
No workbench module, validator, test or process is imported or executed.
These checks do not establish a complete turnout assignment or physical fit.

The source interpretation was inspected at tracktemplate revision
7965bfc4671668f889c1f43fb8336c5146c3f5cf, retained macro
model_railway_curve_template_multitrack_v10_2a8a7b15_chair_performance_and_representation.FCMacro:
489 (fixed scale), 35577-35579 and 36404-36405 (identity), 36013-36035
(segment projection), 36051-36077 (analytical dimensions), 36363-36374
(footprint axes), 43147-43252 (assignment), 43374-43404 (clearances), and
43458-43590 (final generator). This script checks only its elementary example;
it does not call or reproduce the whole generator, assignment or validation.
"""

import argparse
from dataclasses import dataclass
from fractions import Fraction
from html import escape
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "_static" / "figures" / "chair-analysis-example.svg"
SOURCE_REVISION = "7965bfc4671668f889c1f43fb8336c5146c3f5cf"
SOURCE_FILE = (
    "model_railway_curve_template_multitrack_v10_2a8a7b15_"
    "chair_performance_and_representation.FCMacro"
)
SOURCE_URL = (
    f"https://github.com/Richard-Gnitnub/tracktemplate/blob/"
    f"{SOURCE_REVISION}/{SOURCE_FILE}"
)
ENTITY_ID = "TO-001"
TIMBER_ID = "TO-001:timber:T1"
RAIL_ID = "TO-001:rail:main-side-stock-rail"
POSITION_ID = "TO-001:chair:to-001-timber-t1:main-side-stock-rail"

INK = "#122433"
MUTED = "#405363"
BLUE = "#245b86"
ORANGE = "#a94f12"
PURPLE = "#70508b"
TIMBER_FILL = "#e9eff2"
FOOTPRINT_FILL = "#f9e3cf"
F = Fraction


@dataclass(frozen=True)
class Example:
    """Exact values for this one declared, axis-aligned illustration."""

    centre: tuple
    rail_start: tuple
    rail_end: tuple
    support: tuple
    station: Fraction
    distance: Fraction
    timber: tuple
    footprint: tuple
    length: Fraction
    width: Fraction
    side_clearance: Fraction
    end_clearance: Fraction


def checked_example():
    """Check independent rational arithmetic, without solving a track layout."""
    centre = (F(10), F(0))
    rail_start, rail_end = (F(0), F(4)), (F(20), F(4))
    timber = (F(8), F(-15), F(12), F(15))
    delta = tuple(end - start for start, end in zip(rail_start, rail_end))
    offset = tuple(value - start for value, start in zip(centre, rail_start))
    length_squared = sum(value * value for value in delta)
    parameter = sum(a * b for a, b in zip(offset, delta)) / length_squared
    parameter = min(F(1), max(F(0), parameter))
    support = tuple(start + parameter * value for start, value in zip(rail_start, delta))

    # The declared segment is horizontal. Its exact length is 20 mm, so this
    # example needs no square root or approximation of a sampled curve.
    assert delta == (F(20), F(0)), "The example must retain its horizontal rail"
    assert length_squared == 400
    assert parameter == F(1, 2)
    assert support == (F(10), F(4))
    station = parameter * delta[0]
    distance = abs(support[1] - centre[1])
    assert station == 10 and distance == 4
    assert timber[0] < support[0] < timber[2]
    assert timber[1] < support[1] < timber[3]
    assert timber[2] - timber[0] == 4 and timber[3] - timber[1] == 30
    assert tuple((timber[index] + timber[index + 2]) / 2 for index in (0, 1)) == centre

    # These are the source-labelled S1 analytical dimensions at the source's
    # fixed 1:76.2 scale. They are not independently measured chair dimensions.
    inch = F("25.4") / F("76.2")
    length, width = F("14.5") * inch, F(8) * inch
    assert inch == F(1, 3)
    assert length == F(29, 6) and width == F(8, 3)
    footprint = (
        support[0] - width / 2, support[1] - length / 2,
        support[0] + width / 2, support[1] + length / 2,
    )
    assert footprint == (F(26, 3), F(19, 12), F(34, 3), F(77, 12))
    side_clearance = min(footprint[0] - timber[0], timber[2] - footprint[2])
    end_clearance = min(footprint[1] - timber[1], timber[3] - footprint[3])
    assert side_clearance == F(2, 3)
    assert end_clearance == F(103, 12)
    assert side_clearance > F("0.15") and end_clearance > F("0.50")

    def slug(value):
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "unnamed"

    identity = f"{ENTITY_ID}:chair:{slug(TIMBER_ID)}:{slug(RAIL_ID.split(':rail:')[-1])}"
    assert identity == POSITION_ID
    return Example(
        centre, rail_start, rail_end, support, station, distance, timber,
        footprint, length, width, side_clearance, end_clearance,
    )


@dataclass(frozen=True)
class View:
    """A Cartesian view with one shared pixels-per-mm scale for both axes."""

    left: Fraction
    top: Fraction
    xmin: Fraction
    ymax: Fraction
    scale: Fraction

    def point(self, point):
        x, y = point
        return self.left + (x - self.xmin) * self.scale, self.top + (self.ymax - y) * self.scale


def number(value):
    """Round only SVG display coordinates; the example stays rational."""
    return f"{float(value):.6f}".rstrip("0").rstrip(".") or "0"


def text(x, y, value, size=21, colour=INK, weight="400", anchor="start", rotation=None):
    transform = (
        f' transform="rotate({number(rotation)} {number(x)} {number(y)})"'
        if rotation is not None else ""
    )
    return (
        f'<text x="{number(x)}" y="{number(y)}" font-size="{size}" '
        f'fill="{colour}" font-weight="{weight}" text-anchor="{anchor}"{transform}>'
        f'{escape(value)}</text>'
    )


def rectangle(bounds, view, fill, stroke, stroke_width=2):
    xmin, ymin, xmax, ymax = bounds
    x, y = view.point((xmin, ymax))
    return (
        f'<rect x="{number(x)}" y="{number(y)}" '
        f'width="{number((xmax - xmin) * view.scale)}" '
        f'height="{number((ymax - ymin) * view.scale)}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
    )


def line(start, end, colour=MUTED, width=1.5, extra=""):
    return (
        f'<path d="M {number(start[0])} {number(start[1])} '
        f'L {number(end[0])} {number(end[1])}" '
        f'fill="none" stroke="{colour}" stroke-width="{width}"{extra}/>'
    )


def dot(point, radius, colour):
    return (
        f'<circle cx="{number(point[0])}" cy="{number(point[1])}" '
        f'r="{number(radius)}" fill="{colour}" stroke="#ffffff" stroke-width="1.5"/>'
    )


def whole_view(example):
    view = View(F(140), F(211), F(0), F(15), F(10))
    support, centre = view.point(example.support), view.point(example.centre)
    return [
        '<rect x="16" y="116" width="448" height="455" rx="12" fill="#f6f8fa"/>',
        text(32, 151, "1  Project the timber centre", 23, weight="700"),
        text(32, 181, "Timber 4 × 30 · equal x/y scale", 20, MUTED),
        rectangle(example.timber, view, TIMBER_FILL, MUTED, 1.5),
        rectangle(example.footprint, view, FOOTPRINT_FILL, ORANGE),
        line(view.point(example.rail_start), view.point(example.rail_end), BLUE, 3),
        line((centre[0], centre[1] - 5), (support[0], support[1] + 8), PURPLE, 2.5,
             ' marker-end="url(#projection-arrow)"'),
        dot(centre, 4.5, INK),
        dot(support, 5.5, BLUE),
        text(32, 236, "T1 timber", 21),
        line((132, 231), (218, 231)),
        text(32, 298, "Rail y = 4", 21, BLUE),
        text(280, 278, "Support", 21, BLUE, "700"),
        text(280, 307, "Q = (10, 4)", 21, BLUE),
        line((246, 318), (274, 304), BLUE),
        text(32, 380, "Projection", 21, PURPLE),
        text(32, 407, "4 mm", 21, PURPLE),
        line((153, 374), (233, 342), PURPLE),
        text(280, 383, "Centre", 21, weight="700"),
        text(280, 410, "(10, 0)", 21),
        line((246, 365), (274, 379)),
        line((360, 490), (360, 450)),
        line((360, 490), (400, 490)),
        '<path d="M 356 457 L 360 450 L 364 457 M 393 486 L 400 490 L 393 494" fill="none" stroke="#405363" stroke-width="1.5"/>',
        text(353, 440, "y", 20, MUTED),
        text(410, 496, "x", 20, MUTED),
        text(32, 548, "Rail station at Q: 10 mm", 21),
    ]


def detail_view(example):
    view = View(F(90), F(699), F(7), F(15, 2), F(50))
    left, top = view.point((example.footprint[0], example.footprint[3]))
    right, bottom = view.point((example.footprint[2], example.footprint[1]))
    timber_left = view.point((example.timber[0], F(0)))[0]
    timber_right = view.point((example.timber[2], F(0)))[0]
    support = view.point(example.support)
    parts = [
        '<rect x="16" y="591" width="448" height="548" rx="12" fill="#f6f8fa"/>',
        text(32, 626, "2  Analytical footprint", 23, weight="700"),
        text(32, 654, "Detail ×5 · equal x/y scale", 20, MUTED),
        '<clipPath id="detail-clip"><rect x="90" y="699" width="300" height="350"/></clipPath>',
        '<g clip-path="url(#detail-clip)">',
        '<rect x="90" y="699" width="300" height="350" fill="#ffffff"/>',
        rectangle(example.timber, view, TIMBER_FILL, MUTED, 1.5),
        rectangle(example.footprint, view, FOOTPRINT_FILL, ORANGE, 2.5),
        line(view.point(example.rail_start), view.point(example.rail_end), BLUE, 3),
        dot(support, 5.5, BLUE),
        text(support[0] + 14, support[1] - 10, "Q", 21, BLUE, "700"),
        '</g>',
        '<rect x="90" y="699" width="300" height="350" fill="none" stroke="#a3b4bf" stroke-width="1.2"/>',
        text(240, 724, f"{example.width} mm", 21, ORANGE, anchor="middle"),
        line((left, 737), (right, 737), ORANGE),
        line((left, 730), (left, top - 4), ORANGE),
        line((right, 730), (right, top - 4), ORANGE),
        line((414, top), (414, bottom), ORANGE),
        line((405, top), (424, top), ORANGE),
        line((405, bottom), (424, bottom), ORANGE),
        text(441, support[1], f"{example.length} mm", 21, ORANGE,
             anchor="middle", rotation=-90),
        text(32, support[1] - 12, "Rail", 20, BLUE),
    ]
    for start, finish in ((timber_left, left), (right, timber_right)):
        parts.extend([
            line((start, 1024), (finish, 1024)),
            line((start, 1016), (start, 1032)),
            line((finish, 1016), (finish, 1032)),
        ])
    parts.extend([
        text(32, 1082, f"Side clearance = {example.side_clearance} mm", 21),
        text(32, 1113, f"End clearance = {example.end_clearance} mm", 21),
    ])
    return parts


def render(example):
    description = (
        "Synthetic isolated T1 illustration in model millimetres. The timber is "
        "4 mm wide and 30 mm long at centre (10, 0), with its length axis along y "
        "and width axis along x. The rail runs from (0, 4) to (20, 4). Projecting "
        "the timber centre gives support Q=(10, 4), distance 4 mm and station "
        "10 mm along that rail from (0, 4) towards (20, 4). The analytical "
        "rectangle is 29/6 mm along y and 8/3 mm along x, following the retained "
        "macro's source-labelled S1 footprint at fixed scale 1:76.2. Its corners "
        "are (26/3, 19/12), (26/3, 77/12), (34/3, 77/12), (34/3, 19/12). "
        "The minimum side and end clearances are 2/3 and 103/12 mm respectively. "
        "Both views use equal x/y scale; the lower view magnifies both axes by "
        "five and crops to x=7..13, y=0.5..7.5. The orange rectangle is an "
        "analytical footprint, not a physical chair. Position identity: "
        f"{POSITION_ID}. Independent rational arithmetic only; no captured REA "
        "or FreeCAD output and no full-turnout or physical fit acceptance."
    )
    metadata = {
        "generator": "tools/render_chair_analysis_figure.py",
        "licence": "GPL-3.0-or-later",
        "source_revision": SOURCE_REVISION,
        "source_file": SOURCE_FILE,
        "source_url": SOURCE_URL,
        "source_lines": ["489", "35577-35579", "36013-36035", "36051-36077",
                         "36363-36374", "36404-36405", "43147-43252",
                         "43374-43404", "43458-43590"],
        "input_provenance": "Synthetic isolated T1 record and horizontal rail; model mm",
        "position_identity": POSITION_ID,
        "checked_scope": "Independent rational example arithmetic and exact SVG reproduction",
        "limits": "No workbench execution, captured FreeCAD output, full-turnout acceptance or physical fit check",
    }
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 1220" width="480" height="1220" style="max-width:100%;height:auto" role="img" aria-labelledby="title desc">',
        '<!-- SPDX-License-Identifier: GPL-3.0-or-later -->',
        '<!-- Copyright (C) 2026 Richard-Gnitnub and TrackTemplateMacro contributors. -->',
        '<!-- Generated by tools/render_chair_analysis_figure.py; edit that source. -->',
        '<title id="title">Synthetic chair-position projection and analytical footprint</title>',
        '<desc id="desc">' + escape(description) + '</desc>',
        '<metadata>' + escape(json.dumps(metadata, indent=2, sort_keys=True)) + '</metadata>',
        '<defs><marker id="projection-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="5" markerHeight="5" orient="auto"><path d="M 0 0 L 8 4 L 0 8 Z" fill="#70508b"/></marker></defs>',
        '<rect width="480" height="1220" fill="#ffffff"/>',
        '<g font-family="system-ui, sans-serif">',
        text(24, 34, "Chair-position example", 26, weight="700"),
        text(24, 66, "Synthetic geometry · model millimetres", 20, MUTED),
        text(24, 93, "Source-inspected; no FreeCAD output", 20, MUTED),
        *whole_view(example),
        *detail_view(example),
        text(24, 1170, "x → along rail · y ↑ along timber", 20, MUTED),
        text(24, 1198, "Analytical geometry; no physical fit check.", 19, MUTED),
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
    expected = render(checked_example())
    if args.check_only:
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != expected.encode("utf-8"):
            parser.error("Saved SVG is missing or differs; run this script without --check-only")
        print("Chair analysis figure: rational arithmetic and reproducible SVG checks passed.")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(expected, encoding="utf-8")
        print(f"Wrote {OUTPUT.relative_to(ROOT)}; illustration rational arithmetic checks passed.")


if __name__ == "__main__":
    main()
