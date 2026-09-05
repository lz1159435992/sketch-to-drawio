#!/usr/bin/env python3
"""Remap an SVG's colors onto a target palette, preserving shading structure.

Unique colors are sorted by relative luminance and mapped rank-by-rank onto
the palette (also sorted by luminance). When the SVG has more colors than
the palette, colors are grouped into contiguous luminance bands, one band
per palette entry. Usage:

    remap_svg_colors.py in.svg -o out.svg --palette "#8AA5BE,#39739D,#3F7E5A"

Exit 2 on any failure. Gradients are flattened to their stop colors being
remapped individually (use --report to inspect the mapping).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
RGB_RE = re.compile(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)[^)]*\)")


def _lum(r: int, g: int, b: int) -> float:
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def collect_colors(text: str) -> dict[str, tuple[int, int, int]]:
    colors: dict[str, tuple[int, int, int]] = {}
    for match in HEX_RE.finditer(text):
        token = match.group(0)
        colors[token] = _hex_to_rgb(token)
    for match in RGB_RE.finditer(text):
        token = match.group(0)
        colors[token] = (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return colors


def build_mapping(colors: dict[str, tuple[int, int, int]],
                  palette: list[tuple[int, int, int]]) -> dict[str, tuple[int, int, int]]:
    ordered = sorted(colors.items(), key=lambda kv: _lum(*kv[1]))
    pal = sorted(palette, key=lambda rgb: _lum(*rgb))
    n, m = len(ordered), len(pal)
    mapping: dict[str, tuple[int, int, int]] = {}
    for rank, (token, _rgb) in enumerate(ordered):
        band = min(rank * m // n, m - 1)  # contiguous luminance bands
        mapping[token] = pal[band]
    return mapping


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="input SVG")
    parser.add_argument("-o", "--output", required=True, help="output SVG")
    parser.add_argument("--palette", required=True,
                        help="comma-separated palette colors, e.g. '#8AA5BE,#39739D'")
    parser.add_argument("--report", action="store_true", help="print the color mapping")
    args = parser.parse_args()

    try:
        palette = [_hex_to_rgb(c.strip()) for c in args.palette.split(",") if c.strip()]
    except ValueError:
        print("palette must be hex colors like #8AA5BE", file=sys.stderr)
        return 2
    if not palette:
        print("empty palette", file=sys.stderr)
        return 2

    text = Path(args.input).read_text(encoding="utf-8")
    colors = collect_colors(text)
    if not colors:
        print("no colors found in SVG", file=sys.stderr)
        return 2
    mapping = build_mapping(colors, palette)

    for token, new_rgb in sorted(mapping.items(), key=lambda kv: -len(kv[0])):
        replacement = _rgb_to_hex(*new_rgb)
        text = text.replace(token, replacement)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out} ({len(colors)} colors -> {len(palette)} palette entries)")
    if args.report:
        for token, new_rgb in sorted(mapping.items(), key=lambda kv: _lum(*colors[kv[0]])):
            print(f"  {token} -> {_rgb_to_hex(*new_rgb)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
