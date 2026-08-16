#!/usr/bin/env python3
"""Idempotently add the shared lead-capture script and Privacy Policy footer links."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {
    "404.html",
    "wineries/45-north.html",
    "admin/leads.html",
}


def rel_of(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def prefix_for(path: Path) -> str:
    return "../" * (len(path.relative_to(ROOT).parts) - 1)


def ensure_script(html: str, prefix: str) -> str:
    src = f"{prefix}js/leads.js"
    if f'src="{src}"' in html:
        return html
    tag = f'<script src="{src}" defer></script>\n'
    idx = html.lower().rfind("</body>")
    if idx == -1:
        return html
    return html[:idx] + tag + html[idx:]


def ensure_privacy_links(html: str, prefix: str) -> str:
    privacy = f"{prefix}privacy.html"
    if f'href="{privacy}"' in html:
        return html

    resources = f'<li><a href="{prefix}sitemap.html">Sitemap</a></li>'
    if resources in html:
        html = html.replace(
            resources,
            f'<li><a href="{privacy}">Privacy Policy</a></li>\n        {resources}',
            1,
        )

    # Footer-bottom sitemap link (first remaining occurrence after Resources).
    bottom_variants = [
        f'<div style="display: flex; gap: 24px;">\n        <a href="{prefix}sitemap.html">Sitemap</a>',
        f'<div style="display:flex;gap:24px;"><a href="{prefix}sitemap.html">Sitemap</a>',
        f'<div style="display: flex; gap: 24px;"><a href="{prefix}sitemap.html">Sitemap</a>',
    ]
    for variant in bottom_variants:
        if variant in html:
            html = html.replace(
                variant,
                variant.replace(
                    f'<a href="{prefix}sitemap.html">Sitemap</a>',
                    f'<a href="{privacy}">Privacy</a>\n        <a href="{prefix}sitemap.html">Sitemap</a>',
                ),
                1,
            )
            return html

    lone = f'<a href="{prefix}sitemap.html">Sitemap</a>'
    # Prefer the last sitemap anchor (footer-bottom) when Resources already has Privacy.
    if html.count(lone) >= 1:
        head, sep, tail = html.rpartition(lone)
        if sep:
            html = f'{head}<a href="{privacy}">Privacy</a> · {sep}{tail}'
    return html


def main() -> None:
    updated = 0
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts or "node_modules" in path.parts or "admin" in path.parts:
            continue
        rel = rel_of(path)
        if rel in SKIP:
            continue
        original = path.read_text(errors="replace")
        prefix = prefix_for(path)
        html = ensure_privacy_links(original, prefix)
        html = ensure_script(html, prefix)
        if html != original:
            path.write_text(html)
            updated += 1
            print(f"updated {rel}")
    print(f"wired {updated} pages")


if __name__ == "__main__":
    main()
