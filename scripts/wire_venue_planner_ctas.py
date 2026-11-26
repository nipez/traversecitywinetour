#!/usr/bin/env python3
"""Wire Plan-a-day + Get-a-driver-quote CTAs on venue detail pages.

Idempotent. Reuses js/leads.js tour modal and /plan-your-day?stops=<slug>.
Does not touch titles, meta descriptions, canonicals, or schema blocks.
Skips redirect stubs (e.g. wineries/45-north.html).
"""

from __future__ import annotations

import re
from html import escape, unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

H1_RE = re.compile(r"<h1>([^<]+)</h1>", re.IGNORECASE)
REFRESH_RE = re.compile(r'http-equiv=["\']refresh["\']', re.IGNORECASE)

# Existing Visitor Guide / Plan Your Visit sidebar card on winery pages.
WINERY_SIDEBAR_CARD_RE = re.compile(
    r'<div class="sidebar-card">\s*'
    r"<h3>(?:Visitor Guide|Plan Your Visit)</h3>.*?"
    r"</div>\s*(?=<div class=\"sidebar-card\">|</div>\s*</div>\s*"
    r'<section class="related-wineries">|</div>\s*</div>\s*'
    r"<section)",
    re.IGNORECASE | re.DOTALL,
)

WINERY_BAND_RE = re.compile(
    r'<section class="winery-tour-cta-band"[^>]*>.*?</section>\s*',
    re.IGNORECASE | re.DOTALL,
)

# Leftover pre-planner "Visitor Guide" card with guided-tour CTA (replace missed these).
LEGACY_VISITOR_GUIDE_CARD_RE = re.compile(
    r'\n?\s*<div class="sidebar-card">\s*'
    r"<h3>Visitor Guide</h3>\s*"
    r"<p[^>]*>Need a ride\?.*?</p>\s*"
    r'<button type="button" class="winery-tour-cta"[^>]*>'
    r".*?on a guided wine tour</button>\s*"
    r'(?:<a href="/wine-tours" class="winery-tour-secondary">.*?</a>\s*)?'
    r"</div>",
    re.IGNORECASE | re.DOTALL,
)

# Brewery/cidery: replace previous tour CTA block after Visit Website.
VENUE_CTA_AFTER_WEBSITE_RE = re.compile(
    r'(<a href="[^"]*" target="_blank" rel="noopener" class="cta-btn">'
    r"Visit Website</a>)\s*"
    r'(?:<button type="button" class="winery-tour-cta"[^>]*>.*?</button>\s*)?'
    r'(?:<a href="/wine-tours" class="winery-tour-secondary">.*?</a>\s*)?'
    r'(?:<div class="venue-plan-actions">.*?</div>\s*)?',
    re.IGNORECASE | re.DOTALL,
)

VENUE_BAND_RE = re.compile(
    r'<section class="winery-tour-cta-band"[^>]*>.*?</section>\s*',
    re.IGNORECASE | re.DOTALL,
)


def venue_name_from(html: str, slug: str) -> str:
    m = H1_RE.search(html)
    if m:
        return unescape(m.group(1)).strip()
    return slug.replace("-", " ").title()


def planner_href(slug: str) -> str:
    return f"/plan-your-day?stops={escape(slug, quote=True)}"


def winery_actions(name: str, slug: str) -> str:
    plan = (
        f'<a href="{planner_href(slug)}" class="winery-tour-cta">'
        f"Plan a day here</a>"
    )
    quote = (
        f'<button type="button" class="winery-tour-quote" data-tour-quote '
        f'data-winery-name="{escape(name, quote=True)}" '
        f'data-winery-slug="{escape(slug, quote=True)}" '
        f'data-planner-stop="{escape(slug, quote=True)}">'
        f"Get a driver quote</button>"
    )
    return (
        '<div class="venue-plan-actions">\n'
        f"      {plan}\n"
        f"      {quote}\n"
        f'      <a href="/wine-tours" class="winery-tour-secondary">'
        f"Browse wine tour operators</a>\n"
        f"    </div>"
    )


def venue_actions(name: str, slug: str, venue_type: str) -> str:
    plan = (
        f'<a href="{planner_href(slug)}" class="winery-tour-cta">'
        f"Plan a day here</a>"
    )
    quote = (
        f'<button type="button" class="winery-tour-quote" data-tour-quote '
        f'data-venue-name="{escape(name, quote=True)}" '
        f'data-venue-slug="{escape(slug, quote=True)}" '
        f'data-venue-type="{escape(venue_type, quote=True)}" '
        f'data-planner-stop="{escape(slug, quote=True)}">'
        f"Get a driver quote</button>"
    )
    return (
        '<div class="venue-plan-actions">\n'
        f"      {plan}\n"
        f"      {quote}\n"
        f'      <a href="/wine-tours" class="winery-tour-secondary">'
        f"Browse wine tour operators</a>\n"
        f"    </div>"
    )


def winery_sidebar_card(name: str, slug: str) -> str:
    return (
        '<div class="sidebar-card">\n'
        "      <h3>Plan Your Visit</h3>\n"
        '      <p style="font-size:0.88rem;color:var(--text-light);line-height:1.6;'
        f'margin-bottom:16px;">Build a tasting day that includes {escape(name)}, '
        "or request a short driver quote — no payment collected here.</p>\n"
        f"      {winery_actions(name, slug)}\n"
        "    </div>"
    )


def winery_band(name: str, slug: str) -> str:
    return (
        '<section class="winery-tour-cta-band" aria-label="Plan a day or request a driver quote">\n'
        '  <div class="winery-tour-cta-band-inner">\n'
        '    <div class="winery-tour-cta-copy">\n'
        f"      <h2>Add {escape(name)} to your day</h2>\n"
        "      <p>Open the planner with this stop already added, or send a quick "
        "driver-quote request. We’ll follow up with local options.</p>\n"
        "    </div>\n"
        '    <div class="winery-tour-cta-band-actions">\n'
        f'      <a href="{planner_href(slug)}" class="winery-tour-cta">Plan a day here</a>\n'
        f'      <button type="button" class="winery-tour-quote" data-tour-quote '
        f'data-winery-name="{escape(name, quote=True)}" '
        f'data-winery-slug="{escape(slug, quote=True)}" '
        f'data-planner-stop="{escape(slug, quote=True)}">'
        f"Get a driver quote</button>\n"
        "    </div>\n"
        "  </div>\n"
        "</section>\n"
    )


def venue_band(name: str, slug: str, venue_type: str) -> str:
    kind = "brewery" if venue_type == "brewery" else "cidery"
    return (
        '<section class="winery-tour-cta-band" aria-label="Plan a day or request a driver quote">\n'
        '  <div class="winery-tour-cta-band-inner">\n'
        '    <div class="winery-tour-cta-copy">\n'
        f"      <h2>Add {escape(name)} to your day</h2>\n"
        f"      <p>Open the planner with this {kind} stop already added, or send a "
        "quick driver-quote request with nearby winery options.</p>\n"
        "    </div>\n"
        '    <div class="winery-tour-cta-band-actions">\n'
        f'      <a href="{planner_href(slug)}" class="winery-tour-cta">Plan a day here</a>\n'
        f'      <button type="button" class="winery-tour-quote" data-tour-quote '
        f'data-venue-name="{escape(name, quote=True)}" '
        f'data-venue-slug="{escape(slug, quote=True)}" '
        f'data-venue-type="{escape(venue_type, quote=True)}" '
        f'data-planner-stop="{escape(slug, quote=True)}">'
        f"Get a driver quote</button>\n"
        "    </div>\n"
        "  </div>\n"
        "</section>\n"
    )


def patch_winery(path: Path) -> bool:
    slug = path.stem
    if slug == "index":
        return False
    original = path.read_text(errors="replace")
    if REFRESH_RE.search(original):
        return False
    name = venue_name_from(original, slug)
    html = original

    card = winery_sidebar_card(name, slug)
    if WINERY_SIDEBAR_CARD_RE.search(html):
        html = WINERY_SIDEBAR_CARD_RE.sub(card + "\n    ", html, count=1)
    elif 'data-planner-stop="' + slug + '"' not in html:
        # Insert a Plan Your Visit card after the Visit Information card CTA.
        pattern = re.compile(
            r'(<a href="[^"]*" target="_blank" rel="noopener" class="sidebar-cta">'
            r"Visit Official Website</a>\s*</div>)",
            re.IGNORECASE,
        )
        html, n = pattern.subn(r"\1\n    " + card, html, count=1)
        if not n:
            return False

    # Drop any leftover Visitor Guide card the first-pass regex skipped.
    html = LEGACY_VISITOR_GUIDE_CARD_RE.sub("", html)

    band = winery_band(name, slug)
    if WINERY_BAND_RE.search(html):
        html = WINERY_BAND_RE.sub(band + "\n", html, count=1)
    else:
        marker = '<section class="newsletter">'
        idx = html.find(marker)
        if idx == -1:
            idx = html.find("<footer>")
        if idx != -1:
            html = html[:idx] + band + "\n" + html[idx:]

    if html != original:
        path.write_text(html)
        return True
    return False


def patch_venue(path: Path, venue_type: str) -> bool:
    slug = path.stem
    if slug == "index":
        return False
    original = path.read_text(errors="replace")
    name = venue_name_from(original, slug)
    html = original
    actions = venue_actions(name, slug, venue_type)

    def repl(match: re.Match[str]) -> str:
        return match.group(1) + "\n      " + actions + "\n      "

    html, n = VENUE_CTA_AFTER_WEBSITE_RE.subn(repl, html, count=1)
    if not n and f'data-planner-stop="{slug}"' not in html:
        return False

    band = venue_band(name, slug, venue_type)
    if VENUE_BAND_RE.search(html):
        html = VENUE_BAND_RE.sub(band + "\n", html, count=1)
    else:
        marker = "<footer>"
        idx = html.find(marker)
        if idx != -1:
            html = html[:idx] + band + "\n" + html[idx:]

    if html != original:
        path.write_text(html)
        return True
    return False


def main() -> None:
    winery_n = 0
    for path in sorted((ROOT / "wineries").glob("*.html")):
        if patch_winery(path):
            winery_n += 1
            print(f"winery {path.relative_to(ROOT)}")

    brewery_n = 0
    for path in sorted((ROOT / "breweries").glob("*.html")):
        if patch_venue(path, "brewery"):
            brewery_n += 1
            print(f"brewery {path.relative_to(ROOT)}")

    cidery_n = 0
    for path in sorted((ROOT / "cideries").glob("*.html")):
        if patch_venue(path, "cidery"):
            cidery_n += 1
            print(f"cidery {path.relative_to(ROOT)}")

    print(f"updated wineries={winery_n} breweries={brewery_n} cideries={cidery_n}")


if __name__ == "__main__":
    main()
