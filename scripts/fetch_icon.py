#!/usr/bin/env python3
"""Download an open-source SVG icon via the Iconify API and append an
attribution row. Usage:

    fetch_icon.py <prefix>:<name> -o OUT.svg [--attribution FILE]
                  [--module TEXT] [--confidence high|medium|low]

Exit 2 on any failure (caller should fall back to the trace/generic path).
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

API = "https://api.iconify.design"


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "sketch-to-drawio/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


_COLLECTIONS: dict | None = None


def collection_license(prefix: str) -> tuple[str, str]:
    """Return (license_title, spdx) for an icon set, best effort.

    Uses the /collections index (the per-set /collection endpoint often
    returns license: null, e.g. for lucide)."""
    global _COLLECTIONS
    try:
        if _COLLECTIONS is None:
            _COLLECTIONS = json.loads(_get(f"{API}/collections"))
        lic = _COLLECTIONS.get(prefix, {}).get("license", {}) or {}
        return lic.get("title", "unknown"), lic.get("spdx", "unknown")
    except Exception:
        return "unknown", "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("icon", help="icon id as <prefix>:<name>, e.g. lucide:camera")
    parser.add_argument("-o", "--output", required=True, help="output .svg path")
    parser.add_argument("--attribution", help="attribution markdown file to append to")
    parser.add_argument("--module", default="", help="figure module using this icon")
    parser.add_argument("--confidence", default="high",
                        choices=("high", "medium", "low"))
    args = parser.parse_args()

    if ":" not in args.icon:
        print("icon must be <prefix>:<name>", file=sys.stderr)
        return 2
    prefix, name = args.icon.split(":", 1)

    try:
        svg = _get(f"{API}/{prefix}/{name}.svg")
    except Exception as e:
        print(f"download failed: {e}", file=sys.stderr)
        return 2
    if b"<svg" not in svg[:500]:
        print("response is not an SVG (unknown icon?)", file=sys.stderr)
        return 2

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(svg)
    print(f"saved {out} ({len(svg)} bytes)")

    if args.attribution:
        title, spdx = collection_license(prefix)
        needs = "yes" if args.confidence != "high" else "no"
        attribution = Path(args.attribution)
        attribution.parent.mkdir(parents=True, exist_ok=True)
        if not attribution.exists():
            attribution.write_text(
                "| icon | 模块 | 来源 | 库/名称 | 许可证 | 署名要求 | 处理方式 | 置信度 | 待确认 |\n"
                "|---|---|---|---|---|---|---|---|---|\n",
                encoding="utf-8",
            )
        row = (f"| {name} | {args.module} | open_source | {prefix}:{name} | {title} ({spdx}) "
               f"| {'见许可证' if spdx not in ('MIT', 'ISC', 'Apache-2.0') else '无'} "
               f"| as_svg | {args.confidence} | {needs} |\n")
        with attribution.open("a", encoding="utf-8") as fh:
            fh.write(row)
        print(f"attribution appended to {attribution}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
