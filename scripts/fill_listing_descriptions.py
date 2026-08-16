#!/usr/bin/env python3
"""Fill missing winery JSON descriptions and replace thin index-card blurbs."""

from __future__ import annotations

import json
import re
from html import escape, unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "data-wineries.json"
INDEX = ROOT / "wineries" / "index.html"


def first_about_sentence(html: str) -> str:
    match = re.search(r"<h2>About[^<]*</h2>\s*<p>(.*?)</p>", html, re.I | re.S)
    if not match:
        return ""
    text = unescape(re.sub(r"<[^>]+>", " ", match.group(1)))
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)
    sentence = parts[0].strip()
    if sentence and sentence[-1] not in ".!?":
        sentence += "."
    return sentence


def clip(text: str, limit: int = 220) -> str:
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "."


def main() -> None:
    data = json.loads(JSON_PATH.read_text())
    filled = 0
    for winery in data["wineries"]:
        slug = winery["slug"]
        page = ROOT / "wineries" / f"{slug}.html"
        if not page.exists():
            continue
        about = first_about_sentence(page.read_text(errors="replace"))
        if not about:
            continue
        if not (winery.get("description") or "").strip():
            winery["description"] = about
            filled += 1
            print(f"json  {slug}")

    JSON_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"filled {filled} json descriptions")

    html = INDEX.read_text(errors="replace")
    updated = 0
    for winery in data["wineries"]:
        slug = winery["slug"]
        desc = (winery.get("description") or "").strip()
        if not desc:
            continue
        card = escape(clip(desc), quote=False)
        pattern = rf'(<a href="{re.escape(slug)}\.html"[^>]*>.*?<p class="winery-desc">)(.*?)(</p>)'
        new_html, n = re.subn(pattern, lambda m, c=card: f"{m.group(1)}{c}{m.group(3)}", html, count=1, flags=re.S)
        if n:
            html = new_html
            updated += 1
            print(f"card  {slug}")

    INDEX.write_text(html)
    print(f"updated {updated} index cards")


if __name__ == "__main__":
    main()
