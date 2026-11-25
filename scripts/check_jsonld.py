#!/usr/bin/env python3
"""Parse every application/ld+json block in built HTML; exit non-zero on failure.

Usage:
  python3 scripts/check_jsonld.py              # all *.html under repo root
  python3 scripts/check_jsonld.py --sitemap    # only paths listed in sitemap.xml
  python3 scripts/check_jsonld.py --fix       # strip known orphan-hours corruption, then check
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
LD_RE = re.compile(
    r'(<script type="application/ld\+json">)(.*?)(</script>)',
    re.S,
)
ORPHAN_AFTER_GEO_RE = re.compile(
    r'("geo"\s*:\s*\{\s*"@type"\s*:\s*"GeoCoordinates"\s*,\s*'
    r'"latitude"\s*:\s*-?[0-9.]+\s*,\s*"longitude"\s*:\s*-?[0-9.]+\s*\})'
    r'\s*,\s*"opens"[\s\S]*?\](?=\s*\n\s*\})',
)


def strip_orphan_hours_after_geo(block: str) -> str:
    return ORPHAN_AFTER_GEO_RE.sub(r"\1", block, count=1)


def loc_to_html(loc: str) -> Path:
    p = urlparse(loc).path.strip("/")
    if not p:
        return ROOT / "index.html"
    as_file = ROOT / f"{p}.html"
    as_index = ROOT / p / "index.html"
    if as_file.exists():
        return as_file
    if as_index.exists():
        return as_index
    return as_file


def html_paths_from_sitemap() -> list[Path]:
    tree = ET.parse(ROOT / "sitemap.xml")
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [el.text.strip() for el in tree.findall(".//sm:loc", ns) if el.text]
    return [loc_to_html(loc) for loc in locs]


def all_html_paths() -> list[Path]:
    skip = {".git", "node_modules", ".wrangler"}
    out = []
    for p in ROOT.rglob("*.html"):
        if any(part in skip for part in p.parts):
            continue
        out.append(p)
    return sorted(out)


def iter_ld_blocks(text: str):
    for m in LD_RE.finditer(text):
        yield m.start(2), m.end(2), m.group(2)


def check_file(path: Path, fix: bool = False) -> tuple[list[str], bool]:
    """Return (errors, did_fix)."""
    if not path.exists():
        return [f"missing file: {path.relative_to(ROOT)}"], False

    text = path.read_text(encoding="utf-8")
    blocks = list(iter_ld_blocks(text))
    if not blocks:
        return [], False

    new_parts: list[str] = []
    last = 0
    changed = False
    for start, end, block in blocks:
        new_parts.append(text[last:start])
        if fix:
            fixed = strip_orphan_hours_after_geo(block)
            if fixed != block:
                block = fixed
                changed = True
        new_parts.append(block)
        last = end
    new_parts.append(text[last:])
    new_text = "".join(new_parts)

    errors: list[str] = []
    for start, _end, block in iter_ld_blocks(new_text):
        try:
            json.loads(block)
        except json.JSONDecodeError as e:
            rel = path.relative_to(ROOT)
            errors.append(f"{rel}: ld+json @{start}: {e}")

    if fix and changed and not errors:
        path.write_text(new_text, encoding="utf-8")
        return [], True

    return errors, False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--sitemap",
        action="store_true",
        help="Only check HTML files corresponding to sitemap.xml URLs",
    )
    ap.add_argument(
        "--fix",
        action="store_true",
        help="Strip known orphan-hours corruption after geo, then re-check",
    )
    args = ap.parse_args()

    paths = html_paths_from_sitemap() if args.sitemap else all_html_paths()
    all_errors: list[str] = []
    checked_blocks = 0
    fixed_files = 0
    for path in paths:
        errs, did_fix = check_file(path, fix=args.fix)
        if did_fix:
            fixed_files += 1
        if path.exists():
            checked_blocks += len(LD_RE.findall(path.read_text(encoding="utf-8")))
        all_errors.extend(errs)

    if args.fix and fixed_files:
        print(f"Fixed {fixed_files} HTML file(s) with orphan hours after geo.")

    if all_errors:
        print(f"FAIL: {len(all_errors)} invalid JSON-LD block(s)", file=sys.stderr)
        for e in all_errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    print(
        f"OK: {len(paths)} HTML file(s), {checked_blocks} JSON-LD block(s) parsed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
