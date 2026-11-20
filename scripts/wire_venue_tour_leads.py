#!/usr/bin/env python3
"""Add tour-quote CTAs to brewery, cidery, and wine-tour-guides pages.

Idempotent. Reuses the existing js/leads.js modal (data-tour-quote).
Does not touch titles, meta descriptions, canonicals, or schema blocks.
"""

from __future__ import annotations

import re
from html import escape, unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

H1_RE = re.compile(r"<h1>([^<]+)</h1>", re.IGNORECASE)
OG_TITLE_RE = re.compile(
    r'<meta property="og:title" content="([^"|]+)',
    re.IGNORECASE,
)

GUIDE_CONTEXT = {
    "index": {
        "interest": "Guided Traverse City wine tour",
        "headline": "Get a guided tour quote",
        "copy": "Tell us your date and group size — we’ll match you with a local wine-tour operator.",
        "button": "Get a tour quote",
        "operator": "Wine tour guides hub quote",
    },
    "private-group-tours": {
        "interest": "Private or group wine tour",
        "headline": "Get a private or group tour quote",
        "copy": "Share your party size and preferred date — we’ll follow up with private and join-in options.",
        "button": "Get a tour quote",
        "operator": "Private / group tour quote",
    },
    "limo-bus-tours": {
        "interest": "Limo or bus wine tour",
        "headline": "Get a limo or bus tour quote",
        "copy": "Need Sprinter, shuttle, limo, or bus capacity? Tell us your date and headcount.",
        "button": "Get a tour quote",
        "operator": "Limo / bus tour quote",
    },
    "how-to-choose": {
        "interest": "Guided Traverse City wine tour",
        "headline": "Ready to request a tour quote?",
        "copy": "Once you know the format you want, send a short request — we’ll match you with a local operator.",
        "button": "Get a tour quote",
        "operator": "How to choose — tour quote",
    },
    "leelanau-peninsula": {
        "interest": "Leelanau Peninsula wine tour",
        "headline": "Get a Leelanau Peninsula tour quote",
        "copy": "Planning a longer Leelanau day? Tell us your date and group size for local driver options.",
        "button": "Get a tour quote",
        "operator": "Leelanau Peninsula tour quote",
    },
    "old-mission-peninsula": {
        "interest": "Old Mission Peninsula wine tour",
        "headline": "Get an Old Mission Peninsula tour quote",
        "copy": "Short drives and bay views — tell us your date and group size for guided Old Mission options.",
        "button": "Get a tour quote",
        "operator": "Old Mission Peninsula tour quote",
    },
}


def venue_name_from(html: str, slug: str) -> str:
    m = H1_RE.search(html)
    if m:
        return unescape(m.group(1)).strip()
    m = OG_TITLE_RE.search(html)
    if m:
        return unescape(m.group(1)).strip()
    return slug.replace("-", " ").title()


def venue_button(
    name: str,
    slug: str,
    venue_type: str,
    *,
    label: str | None = None,
    extra_class: str = "",
) -> str:
    classes = "winery-tour-cta" + (f" {extra_class}" if extra_class else "")
    text = label or f"Visit {name} on a guided tour"
    return (
        f'<button type="button" class="{classes}" data-tour-quote '
        f'data-venue-name="{escape(name, quote=True)}" '
        f'data-venue-slug="{escape(slug, quote=True)}" '
        f'data-venue-type="{escape(venue_type, quote=True)}">'
        f"{escape(text)}</button>"
    )


def guide_button(ctx: dict) -> str:
    return (
        '<button type="button" class="winery-tour-cta" data-tour-quote '
        f'data-tour-interest="{escape(ctx["interest"], quote=True)}" '
        f'data-operator="{escape(ctx["operator"], quote=True)}" '
        f'data-tour-label="{escape(ctx["interest"], quote=True)}">'
        f'{escape(ctx["button"])}</button>'
    )


def cta_band(headline: str, copy: str, button_html: str) -> str:
    return (
        '\n<section class="winery-tour-cta-band" aria-label="Request a guided tour">'
        '\n  <div class="winery-tour-cta-band-inner">'
        '\n    <div class="winery-tour-cta-copy">'
        f"\n      <h2>{escape(headline)}</h2>"
        f"\n      <p>{escape(copy)}</p>"
        f"\n    </div>\n    {button_html}\n  </div>\n</section>\n"
    )


def ensure_band_before_footer(html: str, band: str) -> str:
    if "winery-tour-cta-band" in html:
        return html
    marker = "<footer>"
    idx = html.find(marker)
    if idx == -1:
        return html
    return html[:idx] + band + html[idx:]


def patch_venue_detail(path: Path, venue_type: str) -> bool:
    slug = path.stem
    if slug == "index":
        return False
    original = path.read_text(errors="replace")
    html = original
    name = venue_name_from(html, slug)
    kind_label = "brewery" if venue_type == "brewery" else "cidery"

    # Sidebar / info-card primary CTA after Visit Website button.
    if 'data-venue-slug="' + slug + '"' not in html:
        sidebar_btn = venue_button(name, slug, venue_type)
        secondary = (
            '\n      <a href="/wine-tours" class="winery-tour-secondary">'
            "Browse wine tour operators</a>"
        )
        pattern = re.compile(
            r'(<a href="[^"]*" target="_blank" rel="noopener" class="cta-btn">'
            r"Visit Website</a>)",
            re.IGNORECASE,
        )

        def repl(match: re.Match[str]) -> str:
            return match.group(1) + "\n      " + sidebar_btn + secondary

        html, n = pattern.subn(repl, html, count=1)
        if not n:
            # Fallback: insert near end of info-card.
            card_end = re.compile(
                r'(<div class="info-card">.*?)(</div>\s*</div>\s*</div>)',
                re.IGNORECASE | re.DOTALL,
            )

            def card_repl(match: re.Match[str]) -> str:
                return (
                    match.group(1)
                    + "\n      "
                    + sidebar_btn
                    + secondary
                    + "\n    "
                    + match.group(2)
                )

            html, _ = card_end.subn(card_repl, html, count=1)

    band = cta_band(
        f"Visit {name} on a guided tour",
        f"Tell us your date and group size — we’ll follow up with local driver options "
        f"that can include this {kind_label} stop with nearby wineries.",
        venue_button(name, slug, venue_type),
    )
    html = ensure_band_before_footer(html, band)

    if html != original:
        path.write_text(html)
        return True
    return False


def patch_venue_index(path: Path, venue_type: str) -> bool:
    original = path.read_text(errors="replace")
    if "winery-tour-cta-band" in original:
        return False
    plural = "breweries" if venue_type == "brewery" else "cideries"
    interest = (
        "Wine tour with brewery stops"
        if venue_type == "brewery"
        else "Wine tour with cidery stops"
    )
    button = (
        '<button type="button" class="winery-tour-cta" data-tour-quote '
        f'data-tour-interest="{escape(interest, quote=True)}" '
        f'data-operator="{escape(interest + " quote", quote=True)}" '
        f'data-tour-label="{escape(interest, quote=True)}">'
        "Get a tour quote</button>"
    )
    band = cta_band(
        f"Planning a day that includes {plural}?",
        "Many guided wine tours can add a craft stop — tell us your date and group size.",
        button,
    )
    html = ensure_band_before_footer(original, band)
    if html != original:
        path.write_text(html)
        return True
    return False


def patch_guide(path: Path) -> bool:
    slug = path.stem
    ctx = GUIDE_CONTEXT.get(slug)
    if not ctx:
        return False
    original = path.read_text(errors="replace")
    html = original
    btn = guide_button(ctx)
    band = cta_band(ctx["headline"], ctx["copy"], btn)
    html = ensure_band_before_footer(html, band)
    if html != original:
        path.write_text(html)
        return True
    return False


def main() -> None:
    brewery_n = 0
    for path in sorted((ROOT / "breweries").glob("*.html")):
        if path.stem == "index":
            if patch_venue_index(path, "brewery"):
                brewery_n += 1
                print(f"brewery-index {path.relative_to(ROOT)}")
            continue
        if patch_venue_detail(path, "brewery"):
            brewery_n += 1
            print(f"brewery {path.relative_to(ROOT)}")

    cidery_n = 0
    for path in sorted((ROOT / "cideries").glob("*.html")):
        if path.stem == "index":
            if patch_venue_index(path, "cidery"):
                cidery_n += 1
                print(f"cidery-index {path.relative_to(ROOT)}")
            continue
        if patch_venue_detail(path, "cidery"):
            cidery_n += 1
            print(f"cidery {path.relative_to(ROOT)}")

    guide_n = 0
    for path in sorted((ROOT / "wine-tour-guides").glob("*.html")):
        if patch_guide(path):
            guide_n += 1
            print(f"guide {path.relative_to(ROOT)}")

    print(f"updated breweries={brewery_n} cideries={cidery_n} guides={guide_n}")


if __name__ == "__main__":
    main()
