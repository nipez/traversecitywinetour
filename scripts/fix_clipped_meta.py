#!/usr/bin/env python3
"""Rewrite clipped titles and mid-sentence meta descriptions without a full SEO pass."""

from __future__ import annotations

import re
from html import escape
from pathlib import Path

from apply_seo import (
    PAGE_TITLES,
    choose_desc,
    choose_title,
    existing_desc,
    existing_title,
    html_pages,
    rel_of,
)

ROOT = Path(__file__).resolve().parents[1]


def is_clipped_title(title: str) -> bool:
    return "…" in title or title.endswith("...") or title.endswith("|")


def is_clipped_desc(desc: str) -> bool:
    if not desc:
        return True
    text = desc.strip()
    if text.endswith(("…", "...")):
        return True
    if text[-1] not in ".!?":
        return True
    # Sentence was cut at a word boundary and a period was glued on.
    fragments = (
        " that has.",
        " produces elegant.",
        " to.",
        " from their.",
        " in the region.",
        " in a relaxed.",
        " and to.",
        " and deposited.",
        " using.",
        " overlooking Lake.",
        " heritage to.",
        " exceptional Rieslings.",
    )
    return text.endswith(fragments)


def patch_attr(html: str, pattern: str, value: str) -> str:
    escaped = escape(value, quote=True)
    return re.sub(pattern, lambda m: f"{m.group(1)}{escaped}{m.group(m.lastindex)}", html, count=1, flags=re.I)


def patch_page(path: Path) -> bool:
    rel = rel_of(path)
    if rel in {"404.html", "wineries/45-north.html", "admin/leads.html"}:
        return False
    html = path.read_text(errors="replace")
    title = existing_title(html)
    desc = existing_desc(html)
    new_title = PAGE_TITLES.get(rel) or choose_title(path, html)
    new_desc = choose_desc(path, html)
    changed = False
    if is_clipped_title(title) or (rel in PAGE_TITLES and title != new_title):
        html = patch_attr(html, r"(<title>)(.*?)(</title>)", new_title)
        html = patch_attr(html, r'(<meta property="og:title" content=")([^"]*)(")', new_title)
        html = patch_attr(html, r'(<meta name="twitter:title" content=")([^"]*)(")', new_title)
        changed = True
    if is_clipped_desc(desc):
        html = patch_attr(html, r'(<meta name="description" content=")([^"]*)(")', new_desc)
        html = patch_attr(html, r'(<meta property="og:description" content=")([^"]*)(")', new_desc)
        html = patch_attr(html, r'(<meta name="twitter:description" content=")([^"]*)(")', new_desc)
        changed = True
    if changed:
        path.write_text(html)
    return changed


def main() -> None:
    updated = 0
    for path in html_pages():
        if patch_page(path):
            updated += 1
            print(f"updated {rel_of(path)}")
    print(f"patched {updated} pages")


if __name__ == "__main__":
    main()
