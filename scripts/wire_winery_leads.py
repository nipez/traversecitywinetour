#!/usr/bin/env python3
"""Fix dead newsletter forms and add winery-page tour quote CTAs.

Idempotent. Does not touch titles, meta descriptions, or schema blocks.
"""

from __future__ import annotations

import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LIVE_NEWSLETTER = (
    '<form class="newsletter-form">'
    '<input type="email" name="email" placeholder="Enter your email address" '
    'required autocomplete="email">'
    '<button type="submit">Subscribe</button></form>'
)

# Single-line or multiline dead newsletter stubs.
DEAD_NEWSLETTER = re.compile(
    r'<form\s+class="newsletter-form"\s+onsubmit="return false;"\s*>'
    r'\s*<input\s+type="email"[^>]*>\s*'
    r'<button\s+type="submit">Subscribe</button>\s*</form>',
    re.IGNORECASE | re.DOTALL,
)

WINERY_NAME_RE = re.compile(
    r'<meta property="og:title" content="([^"|]+)',
    re.IGNORECASE,
)
H1_RE = re.compile(r"<h1>([^<]+)</h1>", re.IGNORECASE)


def winery_name_from(html: str, slug: str) -> str:
    from html import unescape

    m = H1_RE.search(html)
    if m:
        return unescape(m.group(1)).strip()
    m = WINERY_NAME_RE.search(html)
    if m:
        return unescape(m.group(1)).strip()
    return slug.replace("-", " ").title()


def fix_newsletter(html: str) -> str:
    return DEAD_NEWSLETTER.sub(LIVE_NEWSLETTER, html)


def tour_button(name: str, slug: str, extra_class: str = "") -> str:
    classes = "winery-tour-cta" + (f" {extra_class}" if extra_class else "")
    return (
        f'<button type="button" class="{classes}" data-tour-quote '
        f'data-winery-name="{escape(name, quote=True)}" '
        f'data-winery-slug="{escape(slug, quote=True)}">'
        f"Visit {escape(name)} on a guided wine tour</button>"
    )


def patch_sidebar_card(html: str, name: str, slug: str) -> str:
    if 'data-tour-quote' in html and 'sidebar-card' in html:
        # Already has a tour CTA somewhere; still ensure sidebar primary CTA.
        pass

    # Replace the existing Visitor Guide / Plan Your Visit sidebar card body.
    pattern = re.compile(
        r'(<div class="sidebar-card">\s*'
        r'<h3>(?:Visitor Guide|Plan Your Visit)</h3>\s*'
        r'<p[^>]*>Need a ride\?.*?</p>\s*)'
        r'(?:<a href="[^"]*" class="sidebar-cta"[^>]*>Browse Wine Tours</a>\s*)'
        r'(</div>)',
        re.IGNORECASE | re.DOTALL,
    )

    replacement = (
        r"\1"
        + tour_button(name, slug)
        + '\n      <a href="/wine-tours" class="winery-tour-secondary">Browse wine tour operators</a>\n    '
        + r"\2"
    )
    updated, n = pattern.subn(replacement, html, count=1)
    if n:
        return updated

    # Fallback: insert a new card before related-wineries if no guide card.
    if 'data-tour-quote' not in html:
        card = (
            '\n    <div class="sidebar-card">\n'
            "      <h3>Plan a Guided Visit</h3>\n"
            f'      <p style="font-size:0.88rem;color:var(--text-light);line-height:1.6;margin-bottom:16px;">'
            f"Want a driver for {escape(name)} and nearby stops? Request a short tour quote — "
            "we’ll match you with a local operator.</p>\n"
            f"      {tour_button(name, slug)}\n"
            '      <a href="/wine-tours" class="winery-tour-secondary">Browse wine tour operators</a>\n'
            "    </div>\n  </div>\n</div>"
        )
        # Insert before closing of winery-sidebar / winery-body if possible.
        html = html.replace(
            "  </div>\n</div>\n<section class=\"related-wineries\">",
            card + "\n<section class=\"related-wineries\">",
            1,
        )
    return html


def ensure_bottom_cta(html: str, name: str, slug: str) -> str:
    if 'winery-tour-cta-band' in html:
        return html
    band = (
        f'\n<section class="winery-tour-cta-band" aria-label="Request a guided tour">'
        f'\n  <div class="winery-tour-cta-band-inner">'
        f'\n    <div class="winery-tour-cta-copy">'
        f"\n      <h2>Visit {escape(name)} on a guided wine tour</h2>"
        f"\n      <p>Tell us your date and group size — we’ll follow up with local driver options "
        f"that can include {escape(name)}.</p>"
        f"\n    </div>\n    {tour_button(name, slug)}\n  </div>\n</section>\n"
    )
    marker = '<section class="newsletter">'
    if marker in html:
        return html.replace(marker, band + marker, 1)
    return html


def patch_winery(path: Path) -> bool:
    slug = path.stem
    if slug == "index":
        return False
    original = path.read_text(errors="replace")
    html = fix_newsletter(original)
    name = winery_name_from(html, slug)
    html = patch_sidebar_card(html, name, slug)
    html = ensure_bottom_cta(html, name, slug)
    if html != original:
        path.write_text(html)
        return True
    return False


def patch_all_newsletters() -> int:
    updated = 0
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts or "node_modules" in path.parts or "admin" in path.parts:
            continue
        # Winery detail pages handled separately (with CTAs).
        if path.parent.name == "wineries" and path.stem != "index":
            continue
        original = path.read_text(errors="replace")
        html = fix_newsletter(original)
        if html != original:
            path.write_text(html)
            updated += 1
            print(f"newsletter {path.relative_to(ROOT)}")
    return updated


def main() -> None:
    newsletter_pages = patch_all_newsletters()
    winery_pages = 0
    for path in sorted((ROOT / "wineries").glob("*.html")):
        if path.stem == "index":
            original = path.read_text(errors="replace")
            html = fix_newsletter(original)
            if html != original:
                path.write_text(html)
                newsletter_pages += 1
                print(f"newsletter {path.relative_to(ROOT)}")
            continue
        if patch_winery(path):
            winery_pages += 1
            print(f"winery {path.relative_to(ROOT)}")
    print(f"updated newsletter pages={newsletter_pages} winery pages={winery_pages}")


if __name__ == "__main__":
    main()
