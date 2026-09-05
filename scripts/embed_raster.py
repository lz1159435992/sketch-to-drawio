#!/usr/bin/env python3
"""Crop + enhance a raster patch and wrap it in an SVG <image> for drawio.

    embed_raster.py in.png -o out.svg [--crop WxH+X+Y] [--scale N]
                [--denoise] [--bg-remove-white TOL] [--bg-flatten-white TOL]
                [--uri out.uri]

Enhancement is limited to resampling (Lanczos), optional median denoise, and
mild unsharp masking -- it never invents detail that is not in the source.

The wrapped form (<svg><image href="data:image/png;base64,...">) is used
because headless drawio desktop exports render direct raster data URIs
(base64, percent-encoded, file://) as blank, while percent-encoded SVG data
URIs render correctly (verified 2026-09-05). Use --uri to also write the
percent-encoded data:image/svg+xml URI for a drawio `image=` style value.

Background handling: --bg-remove-white TOL makes ALL near-white pixels
transparent (can eat white interior details such as clouds or dashes and
leave ragged edges). --bg-flatten-white TOL instead flood-fills only the
background region connected to the image corners and repaints it pure white
(opaque) -- it preserves enclosed whites and blends seamlessly when the
patch sits on a white cell; prefer it for light-tinted sketch backgrounds.

Exit 2 on any failure.
"""

from __future__ import annotations

import argparse
import base64
import io
import sys
import urllib.parse
from pathlib import Path
from collections import deque


def _parse_crop(spec: str) -> tuple[int, int, int, int]:
    try:
        dims, x, y = spec.replace("+", " ").split()
        w, h = dims.lower().split("x")
        return int(x), int(y), int(x) + int(w), int(y) + int(h)
    except ValueError:
        raise SystemExit("crop must look like 230x180+412+520")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="source raster (e.g. the original sketch)")
    parser.add_argument("-o", "--output", required=True, help="output wrapped .svg")
    parser.add_argument("--crop", help="WxH+X+Y crop box before enhancing")
    parser.add_argument("--scale", type=float, default=3.0,
                        help="upscale factor (default 3; keep within 2-4)")
    parser.add_argument("--denoise", action="store_true",
                        help="median-filter before upscaling")
    parser.add_argument("--bg-remove-white", type=int, metavar="TOL", default=0,
                        help="make near-white pixels transparent (tolerance 0-255)")
    parser.add_argument("--bg-flatten-white", type=int, metavar="TOL", default=0,
                        help="flood-fill corner-connected background to opaque white")
    parser.add_argument("--uri", help="also write the percent-encoded data URI here")
    args = parser.parse_args()

    try:
        from PIL import Image, ImageFilter
    except ImportError:
        print("PIL is required", file=sys.stderr)
        return 2

    try:
        im = Image.open(args.input).convert("RGBA")
        if args.crop:
            im = im.crop(_parse_crop(args.crop))
        if args.bg_remove_white > 0:
            tol = args.bg_remove_white
            px = im.load()
            for yy in range(im.height):
                for xx in range(im.width):
                    r, g, b, a = px[xx, yy]
                    if r >= 255 - tol and g >= 255 - tol and b >= 255 - tol:
                        px[xx, yy] = (r, g, b, 0)
        if args.bg_flatten_white > 0:
            tol = args.bg_flatten_white
            w, h = im.size
            px = im.load()
            seed = px[2, 2][:3]
            def _close(c):
                return all(abs(c[i] - seed[i]) <= tol for i in range(3))
            visited = bytearray(w * h)
            queue = deque()
            for xx in range(w):
                for yy in (0, h - 1):
                    if _close(px[xx, yy][:3]):
                        queue.append((xx, yy))
            for yy in range(h):
                for xx in (0, w - 1):
                    if _close(px[xx, yy][:3]):
                        queue.append((xx, yy))
            while queue:
                xx, yy = queue.popleft()
                idx = yy * w + xx
                if visited[idx]:
                    continue
                visited[idx] = 1
                px[xx, yy] = (255, 255, 255, 255)
                for nx, ny in ((xx + 1, yy), (xx - 1, yy), (xx, yy + 1), (xx, yy - 1)):
                    if 0 <= nx < w and 0 <= ny < h and not visited[ny * w + nx] \
                            and _close(px[nx, ny][:3]):
                        queue.append((nx, ny))
        if args.denoise:
            im = im.filter(ImageFilter.MedianFilter(3))
        if args.scale != 1.0:
            im = im.resize((max(1, round(im.width * args.scale)),
                            max(1, round(im.height * args.scale))), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    except SystemExit:
        raise
    except Exception as exc:
        print(f"processing failed: {exc}", file=sys.stderr)
        return 2

    buf = io.BytesIO()
    im.save(buf, format="PNG")
    png_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
           f'xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'width="{im.width}" height="{im.height}" '
           f'viewBox="0 0 {im.width} {im.height}">'
           f'<image width="{im.width}" height="{im.height}" '
           f'xlink:href="data:image/png;base64,{png_b64}"/></svg>')

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    print(f"wrote {out} ({im.width}x{im.height}, png {len(buf.getvalue())} bytes)")

    if args.uri:
        uri = "data:image/svg+xml," + urllib.parse.quote(svg)
        Path(args.uri).write_text(uri, encoding="utf-8")
        print(f"wrote {args.uri} ({len(uri)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
