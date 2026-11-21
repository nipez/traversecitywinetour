#!/usr/bin/env python3
"""One-shot GSC SEO pass: titles/meta, money pages, wineries index, winery templates,
internal links, BreadcrumbList/ItemList item fields, sitemap lastmod.
Does NOT regenerate pages via generate.py — edits HTML in place.
"""
from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = date.today().isoformat()
CHANGELOG: list[tuple[str, str, str, str]] = []  # path, field, old, new


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def log_change(rel: str, field: str, old: str, new: str) -> None:
    if old != new:
        CHANGELOG.append((rel, field, old, new))


def unescape_title(s: str) -> str:
    return html.unescape(s)


def esc_attr(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def set_meta_bundle(text: str, rel: str, new_title: str | None = None, new_desc: str | None = None) -> str:
    """Update title, meta description, og/twitter title & description consistently."""
    if new_title is not None:
        m = re.search(r"<title>(.*?)</title>", text, re.S)
        if m:
            old = unescape_title(m.group(1))
            log_change(rel, "title", old, new_title)
            text = text[: m.start(1)] + esc_attr(new_title) + text[m.end(1) :]
        for prop in (
            'property="og:title"',
            'name="twitter:title"',
        ):
            pat = rf'(<meta {prop} content=")(.*?)(">)'
            m = re.search(pat, text)
            if m:
                old = unescape_title(m.group(2))
                log_change(rel, prop, old, new_title)
                text = text[: m.start(2)] + esc_attr(new_title) + text[m.end(2) :]

    if new_desc is not None:
        for prop in (
            'name="description"',
            'property="og:description"',
            'name="twitter:description"',
        ):
            pat = rf'(<meta {prop} content=")(.*?)(">)'
            m = re.search(pat, text)
            if m:
                old = unescape_title(m.group(2))
                log_change(rel, prop, old, new_desc)
                text = text[: m.start(2)] + esc_attr(new_desc) + text[m.end(2) :]
    return text


def replace_h1(text: str, new_h1_html: str, rel: str) -> str:
    m = re.search(r"<h1\b[^>]*>(.*?)</h1>", text, re.S)
    if not m:
        return text
    old = re.sub(r"<[^>]+>", "", m.group(1))
    old = re.sub(r"\s+", " ", old).strip()
    new_plain = re.sub(r"<[^>]+>", "", new_h1_html)
    new_plain = re.sub(r"\s+", " ", new_plain).strip()
    log_change(rel, "h1", old, new_plain)
    return text[: m.start(1)] + new_h1_html + text[m.end(1) :]


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"pattern not found:\n{old[:120]}")
    return text.replace(old, new, 1)


# ── 1. Homepage money page ──────────────────────────────────────────────
def update_homepage() -> None:
    path = ROOT / "index.html"
    rel = "index.html"
    text = read(path)
    new_title = "Traverse City Wine Tours | Private Drivers & Group Shuttles"
    new_desc = (
        "Book a private or group wine tour on Old Mission or Leelanau. "
        "Local drivers, custom itineraries, and 40+ wineries. Get a quote today."
    )
    text = set_meta_bundle(text, rel, new_title, new_desc)

    # Schema WebPage / Website descriptions
    text = text.replace(
        '"name": "Traverse City Wine Tours | Michigan Winery Guide"',
        f'"name": "{new_title}"',
    )
    old_schema_desc = (
        "Plan a Traverse City wine trip. Explore 40+ wineries on Old Mission and "
        "Leelanau Peninsulas, plus cideries, breweries, maps, and tasting itineraries."
    )
    text = text.replace(f'"description": "{old_schema_desc}"', f'"description": "{new_desc}"')

    old_hero = '''    <div class="hero-tag">Traverse City, Michigan</div>
    <h1>Discover the Heart of<br><em>Michigan Wine Country</em></h1>
    <p class="hero-desc">Explore over 40 wineries across the Old Mission and Leelanau Peninsulas. From world-class Rieslings to stunning bay views, your perfect wine country escape starts here.</p>
    <div class="hero-buttons">
      <a href="/wineries/" class="btn-primary">
        Explore Wineries
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </a>
      <a href="/wine-tours" class="btn-outline">Book a Wine Tour</a>
    </div>'''

    new_hero = '''    <div class="hero-tag">Private Drivers &amp; Group Shuttles</div>
    <h1>Traverse City<br><em>Wine Tours</em></h1>
    <p class="hero-desc">Book a private driver or group shuttle with hotel pickup on Old Mission or Leelanau. Custom itineraries across 40+ wineries — get a quote today.</p>
    <div class="hero-buttons">
      <button type="button" class="btn-primary" data-tour-quote data-tour-interest="Traverse City wine tour" data-tour-label="Private or group wine tour" data-operator="Homepage quote">
        Get a Quote
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </button>
      <a href="/wine-tours" class="btn-outline">Pricing &amp; Details</a>
    </div>'''
    text = replace_once(text, old_hero, new_hero)
    log_change(rel, "h1", "Discover the Heart of Michigan Wine Country", "Traverse City Wine Tours")

    # Internal link to /wineries/ with required anchor (below first viewport)
    old_feat = '''      <div class="section-tag">Hand-Selected Favorites</div>
      <h2 class="section-title">Featured Wineries</h2>
      <div class="section-divider"></div>'''
    new_feat = '''      <div class="section-tag">Hand-Selected Favorites</div>
      <h2 class="section-title">Featured Wineries</h2>
      <div class="section-divider"></div>
      <p class="section-desc">Browse all <a href="/wineries/" style="color:var(--burgundy);font-weight:600;text-decoration:none;border-bottom:1px solid var(--gold);">Traverse City wineries</a> on Old Mission and Leelanau, or jump into a guided day.</p>'''
    text = replace_once(text, old_feat, new_feat)

    write(path, text)


# ── 2. wine-tours booking page ──────────────────────────────────────────
def update_wine_tours() -> None:
    path = ROOT / "wine-tours.html"
    rel = "wine-tours.html"
    text = read(path)
    new_title = "Book a Private Wine Tour in Traverse City | Pricing & Quote"
    new_desc = (
        "Request a private or group wine tour quote in Traverse City. "
        "Compare pricing, pickup options, and Old Mission or Leelanau itineraries."
    )
    text = set_meta_bundle(text, rel, new_title, new_desc)

    old_h1_block = (
        '<div class="page-hero-tag">Guided Experiences</div>'
        "<h1>Traverse City <em>Wine Tours</em></h1>"
        '<p class="page-hero-desc">Sit back, relax, and let someone else drive. '
        "Explore both peninsulas with our trusted tour partners.</p>"
    )
    new_h1_block = (
        '<div class="page-hero-tag">Pricing &amp; Quote</div>'
        "<h1>Book a Private <em>Wine Tour</em> in Traverse City</h1>"
        '<p class="page-hero-desc">Compare private drivers and group shuttles, '
        "request a quote, and lock in hotel pickup for Old Mission or Leelanau.</p>"
    )
    text = replace_once(text, old_h1_block, new_h1_block)
    log_change(rel, "h1", "Traverse City Wine Tours", "Book a Private Wine Tour in Traverse City")

    # Schema breadcrumb name + any WebPage name
    text = text.replace(
        '"name": "Book a Traverse City Wine Tour"',
        '"name": "Book a Private Wine Tour in Traverse City"',
    )

    old_intro = (
        'Comparing operators by peninsula or vehicle type? See the full '
        '<a href="/wine-tour-guides/" style="color:var(--burgundy);font-weight:600;'
        'text-decoration:none;border-bottom:1px solid var(--gold);">'
        "Traverse City wine tour guides</a> hub for Old Mission, Leelanau, "
        "private vs group, and limo/bus guides."
    )
    new_intro = (
        'Start with our homepage overview of '
        '<a href="/" style="color:var(--burgundy);font-weight:600;text-decoration:none;'
        'border-bottom:1px solid var(--gold);">Traverse City wine tours</a>, '
        "then use this page to request a quote. Comparing operators by peninsula "
        "or vehicle type? See the full "
        '<a href="/wine-tour-guides/" style="color:var(--burgundy);font-weight:600;'
        'text-decoration:none;border-bottom:1px solid var(--gold);">'
        "Traverse City wine tour guides</a> hub for Old Mission, Leelanau, "
        "private vs group, and limo/bus guides."
    )
    text = replace_once(text, old_intro, new_intro)
    write(path, text)


# ── 3. wine-tour-guides hub ─────────────────────────────────────────────
def update_tour_guides() -> None:
    path = ROOT / "wine-tour-guides" / "index.html"
    rel = "wine-tour-guides/index.html"
    text = read(path)
    new_title = "Traverse City Wine Tour Companies Compared | Shuttles & Private Drivers"
    new_desc = (
        "Compare Traverse City wine tour companies side by side — private drivers, "
        "group shuttles, vehicles, and booking links for Old Mission and Leelanau."
    )
    text = set_meta_bundle(text, rel, new_title, new_desc)

    old_h1_block = (
        '<div class="page-hero-tag">Operator Comparison Hub</div>\n'
        "  <h1>Compare Traverse City <em>Wine Tour Operators</em></h1>\n"
        '  <p class="page-hero-desc">Private vs join-in, vehicles, and outbound '
        "booking links for verified local guides.</p>"
    )
    new_h1_block = (
        '<div class="page-hero-tag">Operator Comparison Hub</div>\n'
        "  <h1>Traverse City Wine Tour Companies <em>Compared</em></h1>\n"
        '  <p class="page-hero-desc">Shuttles and private drivers side by side — '
        "vehicles, styles, and booking links for Old Mission and Leelanau.</p>"
    )
    text = replace_once(text, old_h1_block, new_h1_block)
    log_change(
        rel,
        "h1",
        "Compare Traverse City Wine Tour Operators",
        "Traverse City Wine Tour Companies Compared",
    )

    old_p = (
        "<p>Searching “Traverse City wine tour guides” or “best wine tour company "
        "Traverse City” usually means you want a clear operator comparison:"
    )
    new_p = (
        "<p>Looking for "
        '<a href="/">Traverse City wine tours</a>? This comparison hub sits beside '
        "our booking page — start on the homepage for the overview, then use the "
        "tables here when you want a clear operator comparison:"
    )
    # Keep rest of sentence intact by splicing carefully
    # Find the full first intro paragraph and rewrite opening.
    m = re.search(
        r'(<div class="intro">\s*<p>)(.*?)(</p>)',
        text,
        re.S,
    )
    if not m:
        raise ValueError("intro p not found on wine-tour-guides")
    rest = m.group(2)
    # Strip the old opening clause through "comparison:"
    rest2 = re.sub(
        r'^Searching .+? usually means you want a clear operator comparison:\s*',
        "",
        rest,
        count=1,
        flags=re.S,
    )
    new_intro_p = (
        'Looking for <a href="/">Traverse City wine tours</a>? This comparison hub '
        "sits beside our booking page — start on the homepage for the overview, then "
        "use the tables here when you want a clear operator comparison: " + rest2
    )
    text = text[: m.start(2)] + new_intro_p + text[m.end(2) :]
    write(path, text)


# ── 4. Wineries index ───────────────────────────────────────────────────
WINERIES_INTRO_HTML = r'''
<section class="wineries-intro" id="guide" style="padding:48px 40px 20px;background:var(--white);">
  <div style="max-width:860px;margin:0 auto;">
    <div class="section-tag" style="margin-bottom:12px;">Planning Guide</div>
    <h2 style="font-family:'Playfair Display',serif;font-size:clamp(1.6rem,3vw,2.2rem);font-weight:500;color:var(--burgundy);line-height:1.2;margin-bottom:18px;">How to explore Traverse City wineries</h2>
    <p style="font-size:1rem;line-height:1.85;color:var(--text);margin-bottom:16px;">Traverse City anchors one of the Midwest’s most concentrated wine regions: more than 40 tasting rooms spread across two peninsulas that meet at Grand Traverse Bay. Old Mission is the narrow eastern finger — about a dozen wineries along a single scenic spine, often with water views on both sides. Leelanau stretches west with 25+ rooms, rolling hills, inland lakes, and village stops from Suttons Bay to Northport. Together they sit near the 45th parallel, the same latitude band as classic cool-climate regions, which is why Riesling, sparkling wine, Pinot Noir, and aromatic whites define so many local lists.</p>
    <p style="font-size:1rem;line-height:1.85;color:var(--text);margin-bottom:16px;">A smart day usually means three to four stops, not a marathon. Pick one peninsula unless you have a driver; crossings eat tasting time. Build a route with our <a href="/winery-map" style="color:var(--burgundy);font-weight:600;text-decoration:none;border-bottom:1px solid var(--gold);">interactive winery map</a> or <a href="/plan-your-day" style="color:var(--burgundy);font-weight:600;text-decoration:none;border-bottom:1px solid var(--gold);">Plan Your Day</a> tool, then confirm hours — winter and midweek schedules tighten. First-timers often start on Old Mission for a compact loop, or choose Leelanau when they want sparkling specialists and more variety between pours. Still deciding? Read <a href="/journal/old-mission-vs-leelanau" style="color:var(--burgundy);font-weight:600;text-decoration:none;border-bottom:1px solid var(--gold);">Old Mission vs Leelanau</a>, then book <a href="/" style="color:var(--burgundy);font-weight:600;text-decoration:none;border-bottom:1px solid var(--gold);">Traverse City wine tours</a> if you’d rather leave the driving to a local.</p>
    <p style="font-size:1rem;line-height:1.85;color:var(--text);margin-bottom:20px;">Use the jump links below to browse by peninsula, or search the full directory. Each winery page covers hours, map pins, and how to add the stop to a private tour.</p>
    <div style="display:flex;flex-wrap:wrap;gap:12px;">
      <a href="#sec-old" style="display:inline-flex;align-items:center;padding:10px 16px;border:1px solid rgba(74,14,27,0.15);border-radius:4px;color:var(--burgundy);text-decoration:none;font-size:0.78rem;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;">Old Mission Peninsula →</a>
      <a href="#sec-lee" style="display:inline-flex;align-items:center;padding:10px 16px;border:1px solid rgba(74,14,27,0.15);border-radius:4px;color:var(--burgundy);text-decoration:none;font-size:0.78rem;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;">Leelanau Peninsula →</a>
      <a href="#winery-faq" style="display:inline-flex;align-items:center;padding:10px 16px;border:1px solid rgba(74,14,27,0.15);border-radius:4px;color:var(--burgundy);text-decoration:none;font-size:0.78rem;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;">Winery FAQ →</a>
    </div>
  </div>
</section>
'''

WINERIES_FAQ_HTML = r'''
<section id="winery-faq" style="padding:64px 40px 80px;background:var(--cream);">
  <div style="max-width:860px;margin:0 auto;">
    <div class="section-tag" style="margin-bottom:12px;">FAQ</div>
    <h2 style="font-family:'Playfair Display',serif;font-size:clamp(1.6rem,3vw,2.2rem);font-weight:500;color:var(--burgundy);line-height:1.2;margin-bottom:28px;">Traverse City wineries — common questions</h2>
    <div class="faq-item" style="border-bottom:1px solid rgba(74,14,27,0.1);padding:20px 0;">
      <h3 style="font-family:'Playfair Display',serif;font-size:1.15rem;color:var(--burgundy);margin:0 0 10px;">How many wineries are in Traverse City?</h3>
      <p style="margin:0;line-height:1.75;color:var(--text);">Visitors usually find 40+ tasting rooms across Old Mission and Leelanau combined. Counts shift as rooms open or pause seasonally — this directory lists the active stops we track, with peninsula filters above.</p>
    </div>
    <div class="faq-item" style="border-bottom:1px solid rgba(74,14,27,0.1);padding:20px 0;">
      <h3 style="font-family:'Playfair Display',serif;font-size:1.15rem;color:var(--burgundy);margin:0 0 10px;">Which peninsula is best for first-timers?</h3>
      <p style="margin:0;line-height:1.75;color:var(--text);">Old Mission is the easiest first day: fewer miles between stops and a straight Center Road corridor. Leelanau rewards a second day or visitors who want sparkling wine and more countryside variety. Compare both in our <a href="/journal/old-mission-vs-leelanau" style="color:var(--burgundy);font-weight:600;">Old Mission vs Leelanau guide</a>.</p>
    </div>
    <div class="faq-item" style="border-bottom:1px solid rgba(74,14,27,0.1);padding:20px 0;">
      <h3 style="font-family:'Playfair Display',serif;font-size:1.15rem;color:var(--burgundy);margin:0 0 10px;">Are Traverse City wineries open in winter?</h3>
      <p style="margin:0;line-height:1.75;color:var(--text);">Many stay open year-round with shorter hours; some lean on appointments. Always call ahead after a storm. See our <a href="/journal/winter-wine-trail" style="color:var(--burgundy);font-weight:600;">winter wine trail guide</a> for off-season planning.</p>
    </div>
    <div class="faq-item" style="border-bottom:1px solid rgba(74,14,27,0.1);padding:20px 0;">
      <h3 style="font-family:'Playfair Display',serif;font-size:1.15rem;color:var(--burgundy);margin:0 0 10px;">Do I need reservations for wine tasting?</h3>
      <p style="margin:0;line-height:1.75;color:var(--text);">Walk-ins are common on quieter weekdays, but weekends, harvest, and holidays fill fast — especially for larger groups or seated experiences. Check each winery page and book when a room lists appointments.</p>
    </div>
    <div class="faq-item" style="border-bottom:1px solid rgba(74,14,27,0.1);padding:20px 0;">
      <h3 style="font-family:'Playfair Display',serif;font-size:1.15rem;color:var(--burgundy);margin:0 0 10px;">How do I get between wineries?</h3>
      <p style="margin:0;line-height:1.75;color:var(--text);">Self-drive works if you designate a sober driver. Rideshares are unreliable on the peninsulas. Most visitors hire a private driver or group shuttle — start with <a href="/" style="color:var(--burgundy);font-weight:600;">Traverse City wine tours</a> or request a quote on our booking page.</p>
    </div>
    <div class="faq-item" style="border-bottom:1px solid rgba(74,14,27,0.1);padding:20px 0;">
      <h3 style="font-family:'Playfair Display',serif;font-size:1.15rem;color:var(--burgundy);margin:0 0 10px;">How many wineries can I visit in one day?</h3>
      <p style="margin:0;line-height:1.75;color:var(--text);">Plan on three to four tastings with travel and a meal. Five-plus stops rush the experience and raise alcohol and timing risk. Use <a href="/plan-your-day" style="color:var(--burgundy);font-weight:600;">Plan Your Day</a> to check drive times before you lock the order.</p>
    </div>
  </div>
</section>
'''

WINERIES_FAQ_SCHEMA = {
    "@type": "FAQPage",
    "@id": "https://traversecitywinetour.com/wineries/#faq",
    "mainEntity": [
        {
            "@type": "Question",
            "name": "How many wineries are in Traverse City?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Visitors usually find 40+ tasting rooms across Old Mission and Leelanau combined. Counts shift as rooms open or pause seasonally — this directory lists the active stops we track.",
            },
        },
        {
            "@type": "Question",
            "name": "Which peninsula is best for first-timers?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Old Mission is the easiest first day: fewer miles between stops and a straight Center Road corridor. Leelanau rewards a second day or visitors who want sparkling wine and more countryside variety.",
            },
        },
        {
            "@type": "Question",
            "name": "Are Traverse City wineries open in winter?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Many stay open year-round with shorter hours; some lean on appointments. Always call ahead after a storm.",
            },
        },
        {
            "@type": "Question",
            "name": "Do I need reservations for wine tasting?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Walk-ins are common on quieter weekdays, but weekends, harvest, and holidays fill fast — especially for larger groups or seated experiences. Check each winery page and book when a room lists appointments.",
            },
        },
        {
            "@type": "Question",
            "name": "How do I get between wineries?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Self-drive works if you designate a sober driver. Rideshares are unreliable on the peninsulas. Most visitors hire a private driver or group shuttle through a local wine tour operator.",
            },
        },
        {
            "@type": "Question",
            "name": "How many wineries can I visit in one day?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Plan on three to four tastings with travel and a meal. Five-plus stops rush the experience and raise alcohol and timing risk.",
            },
        },
    ],
}


def update_wineries_index() -> None:
    path = ROOT / "wineries" / "index.html"
    rel = "wineries/index.html"
    text = read(path)
    new_title = "Traverse City Wineries | Old Mission & Leelanau Guide"
    new_desc = (
        "Guide to Traverse City wineries on Old Mission and Leelanau: how many "
        "there are, how to plan a day, peninsula maps, hours, and FAQ."
    )
    text = set_meta_bundle(text, rel, new_title, new_desc)

    # Update CollectionPage / ItemList names in schema
    text = text.replace(
        '"name": "Traverse City Wineries | Old Mission & Leelanau"',
        f'"name": "{new_title}"',
    )
    text = text.replace(
        '"description": "Complete guide to Traverse City wineries on Old Mission and Leelanau Peninsulas, with tasting hours, directions, and what each room is known for."',
        f'"description": "{new_desc}"',
    )

    # Insert intro after breadcrumbs / tabs — after filter-bar closing nav
    anchor = "</nav>\n\n<section class=\"peninsula-section\" id=\"sec-old\">"
    if "wineries-intro" not in text:
        text = replace_once(text, anchor, "</nav>\n" + WINERIES_INTRO_HTML + "\n<section class=\"peninsula-section\" id=\"sec-old\">")

    # Insert FAQ before newsletter
    if 'id="winery-faq"' not in text:
        newsletter = '<section class="newsletter">'
        text = replace_once(text, newsletter, WINERIES_FAQ_HTML + "\n" + newsletter)

    # Patch JSON-LD: add FAQPage + ensure ItemList uses item
    def patch_graph(m: re.Match) -> str:
        data = json.loads(m.group(1))
        graph = data.get("@graph", [])
        # Ensure FAQ present
        if not any(n.get("@type") == "FAQPage" for n in graph):
            graph.append(WINERIES_FAQ_SCHEMA)
        for n in graph:
            if n.get("@type") == "ItemList":
                n["name"] = new_title
                for li in n.get("itemListElement", []):
                    if "url" in li and "item" not in li:
                        li["item"] = li["url"]
                    if "name" not in li and "item" in li:
                        # should not happen
                        pass
            if n.get("@type") == "BreadcrumbList":
                for li in n.get("itemListElement", []):
                    if "name" not in li or not li["name"]:
                        li["name"] = "Wineries" if li.get("position") == 2 else "Home"
                    if "item" not in li:
                        if li.get("position") == 1:
                            li["item"] = "https://traversecitywinetour.com/"
                        else:
                            li["item"] = "https://traversecitywinetour.com/wineries/"
            if n.get("@type") == "CollectionPage":
                n["name"] = new_title
                n["description"] = new_desc
        data["@graph"] = graph
        return '<script type="application/ld+json">\n' + json.dumps(data, indent=2) + "\n</script>"

    text = re.sub(
        r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
        patch_graph,
        text,
        count=1,
        flags=re.S,
    )

    # Hero desc tweak
    text = text.replace(
        "40+ wineries across Old Mission and Leelanau Peninsulas — every tasting room, every grape, every view.",
        "Old Mission and Leelanau tasting rooms in one guide — plan by peninsula, check hours, and map your day.",
    )
    write(path, text)


# ── 5. Retitle ranking pages ────────────────────────────────────────────
def update_retitles() -> None:
    pages = [
        (
            "where-to-stay.html",
            "Where to Stay for Traverse City Winery Tours | Vineyard Inns & Hotels",
            "Vineyard inns like Chateau Chantal and Black Star Farms, downtown Traverse City hotels, and tips for pairing your stay with a wine tour.",
            "Where to Stay for <em>Winery Tours</em>",
            "Vineyard inns, downtown hotels, and wine-country bases for Old Mission and Leelanau tasting days.",
        ),
        (
            "journal/winter-wine-trail.html",
            "Are Traverse City Wineries Open in Winter? | Winter Wine Trail Guide",
            "Yes — many Traverse City wineries stay open in winter with quieter tasting rooms, cozy hours, and ice wine. Plan your winter wine trail.",
            None,
            None,
        ),
        (
            "journal/harvest-season-traverse-city.html",
            "Traverse City Harvest Season | Best Wineries to Visit in Fall",
            "The best Traverse City wineries to visit during harvest season, when vineyards are working and tasting rooms pour the vintage as it comes in.",
            None,
            None,
        ),
        (
            "journal/old-mission-vs-leelanau.html",
            "Old Mission vs Leelanau Wine Trail | Which Peninsula to Tour",
            "Old Mission vs Leelanau: a side-by-side look at Traverse City's two wine trails to help you choose the right peninsula for your tour.",
            None,
            None,
        ),
    ]
    for rel, title, desc, h1, hero_desc in pages:
        path = ROOT / rel
        text = read(path)
        text = set_meta_bundle(text, rel, title, desc)
        if h1:
            text = replace_h1(text, h1, rel)
        if hero_desc:
            text = re.sub(
                r'(<p class="page-hero-desc">)(.*?)(</p>)',
                rf"\1{hero_desc}\3",
                text,
                count=1,
                flags=re.S,
            )
        write(path, text)

    # Bachelorette — keep title, tighten meta/H1
    rel = "bachelorette.html"
    path = ROOT / rel
    text = read(path)
    new_desc = (
        "Plan a Michigan winery bachelorette party in Traverse City — private drivers, "
        "group buses, tasting-room etiquette, and Old Mission or Leelanau itineraries."
    )
    text = set_meta_bundle(text, rel, None, new_desc)
    text = replace_h1(
        text,
        "Michigan Winery <em>Bachelorette</em> Party<br>in Traverse City",
        rel,
    )
    text = re.sub(
        r'(<p class="bach-hero-desc">)(.*?)(</p>)',
        r"\1Plan a Traverse City bachelorette weekend around vineyard views, private buses, and 40+ wineries — with zero stress for the maid of honor.\3",
        text,
        count=1,
        flags=re.S,
    )
    write(path, text)

    # Remaining TC Wine Journal titles
    journal_map = {
        "journal/48-hour-traverse-city-wine-weekend.html": "48-Hour Traverse City Wine Weekend | Traverse City Wine Tour",
        "journal/first-timers-guide-wine-tasting-traverse-city.html": "First-Timer's Guide to Wine Tasting in Traverse City | Traverse City Wine Tour",
        "journal/michigan-riesling-moment.html": "Why Michigan Riesling Matters | Traverse City Wine Tour",
        "journal/best-rieslings-traverse-city.html": "Best Traverse City Rieslings | Traverse City Wine Tour",
        "journal/traverse-city-wine-dinner-itinerary.html": "Traverse City Wine & Dinner Itinerary | Traverse City Wine Tour",
        "journal/l-mawby-michigan-sparkling-wine.html": "L. Mawby Sparkling Wine | Traverse City Wine Tour",
        "journal/traverse-city-group-wine-tour-guide.html": "Traverse City Group Wine Tours | Parties & Corporate Outings",
        "journal/traverse-city-wines-for-thanksgiving.html": "Traverse City Wines for Thanksgiving | Traverse City Wine Tour",
        "journal/michigan-winery-bachelorette-party.html": "Michigan Winery Bachelorette Party Guide | Traverse City Wine Tour",
        "journal/traverse-city-wine-gift-guide.html": "Traverse City Wine Gifts: Holiday Gift Guide | Traverse City Wine Tour",
        "journal/traverse-city-wineries-winter-guide.html": "Traverse City Wineries in Winter | What's Open & How to Plan",
    }
    for rel, title in journal_map.items():
        path = ROOT / rel
        if not path.exists():
            print("missing", rel)
            continue
        text = read(path)
        text = set_meta_bundle(text, rel, title, None)
        write(path, text)


# ── 6. Winery page titles/meta ──────────────────────────────────────────
def winery_seo_title(name: str) -> str:
    full = f"{name} | Hours, Map & Wine-Tour Stop in Traverse City"
    if len(full) <= 60:
        return full
    short = f"{name} | Hours, Map & Wine-Tour Stop"
    if len(short) <= 60:
        return short
    return f"{name} | Hours, Map & Tour Stop"


def winery_seo_desc(name: str, peninsula: str) -> str:
    pen = f"{peninsula} Peninsula" if not peninsula.endswith("Peninsula") else peninsula
    return (
        f"Planning a visit to {name} on {pen}? Tasting highlights, hours, "
        "and how to add it to a private wine tour."
    )


def update_winery_pages() -> None:
    data = json.loads(read(ROOT / "data-wineries.json"))
    by_slug = {w["slug"]: w for w in data["wineries"]}
    for path in sorted((ROOT / "wineries").glob("*.html")):
        if path.name in ("index.html", "45-north.html"):
            continue
        slug = path.stem
        w = by_slug.get(slug)
        if not w:
            # try match by reading h1
            text0 = read(path)
            if 'http-equiv="refresh"' in text0 or "noindex" in text0:
                continue
            print("skip unknown winery", path.name)
            continue
        text = read(path)
        rel = f"wineries/{path.name}"
        title = winery_seo_title(w["name"])
        desc = winery_seo_desc(w["name"], w["peninsula"])
        text = set_meta_bundle(text, rel, title, desc)

        # Ensure BreadcrumbList ListItems have name+item
        def patch_ld(m: re.Match) -> str:
            try:
                data = json.loads(m.group(1))
            except json.JSONDecodeError:
                return m.group(0)
            nodes = data.get("@graph", [data] if isinstance(data, dict) else data)
            if isinstance(data, dict) and "@graph" in data:
                nodes = data["@graph"]
            elif isinstance(data, dict):
                nodes = [data]
            for node in nodes:
                if not isinstance(node, dict):
                    continue
                if node.get("@type") == "BreadcrumbList":
                    for li in node.get("itemListElement", []):
                        if not li.get("name"):
                            pos = li.get("position")
                            if pos == 1:
                                li["name"] = "Home"
                            elif pos == 2:
                                li["name"] = "Wineries"
                            else:
                                li["name"] = w["name"]
                        if not li.get("item"):
                            pos = li.get("position")
                            if pos == 1:
                                li["item"] = "https://traversecitywinetour.com/"
                            elif pos == 2:
                                li["item"] = "https://traversecitywinetour.com/wineries/"
                            else:
                                li["item"] = f"https://traversecitywinetour.com/wineries/{slug}"
            if isinstance(data, dict) and "@graph" in data:
                data["@graph"] = nodes
                payload = data
            elif len(nodes) == 1:
                payload = nodes[0]
            else:
                payload = nodes
            return '<script type="application/ld+json">\n' + json.dumps(payload, indent=2) + "\n</script>"

        text = re.sub(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            patch_ld,
            text,
            flags=re.S,
        )
        write(path, text)


# ── 7. Internal links TO /wineries/ ─────────────────────────────────────
def add_wineries_anchor_links() -> None:
    targets = [
        (
            "winery-map.html",
            '<div class="breadcrumbs"><a href="/">Home</a><span>›</span><a href="/wineries/">Wineries</a><span>›</span><span class="current">Interactive Map</span></div>',
            '<div class="breadcrumbs"><a href="/">Home</a><span>›</span><a href="/wineries/">Traverse City wineries</a><span>›</span><span class="current">Interactive Map</span></div>',
        ),
        (
            "journal/old-mission-vs-leelanau.html",
            "<p>But they are not the same experience.",
            '<p>Browse the full list of <a href="/wineries/" class="winery-ref">Traverse City wineries</a> anytime. But they are not the same experience.',
        ),
        (
            "journal/winter-wine-trail.html",
            None,  # handled below
            None,
        ),
    ]
    # winery-map breadcrumb anchor text
    path = ROOT / "winery-map.html"
    text = read(path)
    text = text.replace(
        '<div class="breadcrumbs"><a href="/">Home</a><span>›</span><a href="/wineries/">Wineries</a><span>›</span><span class="current">Interactive Map</span></div>',
        '<div class="breadcrumbs"><a href="/">Home</a><span>›</span><a href="/wineries/">Traverse City wineries</a><span>›</span><span class="current">Interactive Map</span></div>',
        1,
    )
    # Add a body sentence if not present
    if '">Traverse City wineries</a>' not in text or text.count("Traverse City wineries") < 2:
        text = text.replace(
            '<div class="breadcrumbs"><a href="/">Home</a><span>›</span><a href="/wineries/">Traverse City wineries</a><span>›</span><span class="current">Interactive Map</span></div>',
            '<div class="breadcrumbs"><a href="/">Home</a><span>›</span><a href="/wineries/">Traverse City wineries</a><span>›</span><span class="current">Interactive Map</span></div>\n'
            '<p style="max-width:900px;margin:16px auto 0;padding:0 40px;font-size:0.95rem;line-height:1.7;color:var(--text-light);">Use this map alongside our directory of <a href="/wineries/" style="color:var(--burgundy);font-weight:600;">Traverse City wineries</a> to build a tasting day.</p>',
            1,
        )
    write(path, text)

    # Journal articles — inject near top of article-body if missing exact anchor text
    journal_inject = [
        (
            "journal/old-mission-vs-leelanau.html",
            '<div class="article-body">\n\n  <p>Traverse City sits',
            '<div class="article-body">\n\n  <p>Browse all <a href="/wineries/" class="winery-ref">Traverse City wineries</a> by peninsula, then use this guide to choose where to spend your day. Traverse City sits',
        ),
        (
            "journal/winter-wine-trail.html",
            '<div class="article-body">',
            None,  # find first p
        ),
        (
            "journal/harvest-season-traverse-city.html",
            '<div class="article-body">',
            None,
        ),
        (
            "journal/first-timers-guide-wine-tasting-traverse-city.html",
            '<div class="article-body">',
            None,
        ),
    ]

    for rel, *_ in journal_inject:
        path = ROOT / rel
        text = read(path)
        if re.search(r'href="/wineries/"[^>]*>Traverse City wineries</a>', text):
            write(path, text)
            continue
        # Insert after opening of article-body first paragraph start
        m = re.search(r'(<div class="article-body">\s*)(<p>)', text, re.S)
        if not m:
            print("no article-body", rel)
            continue
        inject = (
            '<p>Planning stops? Start with our directory of '
            '<a href="/wineries/" class="winery-ref">Traverse City wineries</a> '
            "on Old Mission and Leelanau.</p>\n  "
        )
        text = text[: m.start(2)] + inject + text[m.start(2) :]
        write(path, text)


# ── 8. Sitewide BreadcrumbList / ItemList hardening ─────────────────────
def harden_listitems() -> None:
    for path in ROOT.rglob("*.html"):
        text = read(path)
        if "BreadcrumbList" not in text and "ItemList" not in text:
            continue
        changed = False

        def patch(m: re.Match) -> str:
            nonlocal changed
            raw = m.group(1)
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                return m.group(0)
            nodes = []
            wrapper = None
            if isinstance(data, dict) and "@graph" in data:
                nodes = data["@graph"]
                wrapper = data
            elif isinstance(data, list):
                nodes = data
            else:
                nodes = [data]
                wrapper = data

            for node in nodes:
                if not isinstance(node, dict):
                    continue
                t = node.get("@type")
                types = t if isinstance(t, list) else [t]
                if "BreadcrumbList" in types:
                    for li in node.get("itemListElement", []):
                        if not isinstance(li, dict):
                            continue
                        if not li.get("name"):
                            # derive from item URL tail
                            it = li.get("item") or li.get("url") or ""
                            if isinstance(it, dict):
                                li["name"] = it.get("name") or "Page"
                                if it.get("@id") and "item" not in li:
                                    li["item"] = it["@id"]
                            else:
                                li["name"] = str(it).rstrip("/").split("/")[-1].replace("-", " ").title() or "Page"
                            changed = True
                        if "item" not in li:
                            if "url" in li:
                                li["item"] = li["url"]
                                changed = True
                if "ItemList" in types:
                    for li in node.get("itemListElement", []):
                        if not isinstance(li, dict):
                            continue
                        if "url" in li and "item" not in li:
                            li["item"] = li["url"]
                            changed = True
                        if not li.get("name") and isinstance(li.get("item"), dict):
                            if li["item"].get("name"):
                                li["name"] = li["item"]["name"]
                                changed = True

            if not changed:
                return m.group(0)
            if isinstance(data, dict) and "@graph" in data:
                data["@graph"] = nodes
                payload = data
            elif isinstance(data, list):
                payload = nodes
            else:
                payload = nodes[0] if len(nodes) == 1 else nodes
            return '<script type="application/ld+json">\n' + json.dumps(payload, indent=2) + "\n</script>"

        new_text = re.sub(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            patch,
            text,
            flags=re.S,
        )
        if new_text != text:
            write(path, new_text)


# ── 9. Sitemap lastmod for changed pages ────────────────────────────────
def update_sitemap(changed_paths: set[str]) -> None:
    path = ROOT / "sitemap.xml"
    text = read(path)
    # Map file paths to loc URLs
    locs = set()
    for p in changed_paths:
        p = p.replace("\\", "/")
        if p.endswith("index.html"):
            if p == "index.html":
                locs.add("https://traversecitywinetour.com/")
            else:
                locs.add("https://traversecitywinetour.com/" + p[: -len("index.html")])
        elif p.endswith(".html"):
            locs.add("https://traversecitywinetour.com/" + p[: -len(".html")])

    def bump(m: re.Match) -> str:
        block = m.group(0)
        loc_m = re.search(r"<loc>(.*?)</loc>", block)
        if not loc_m:
            return block
        loc = loc_m.group(1)
        if loc not in locs:
            return block
        return re.sub(r"<lastmod>.*?</lastmod>", f"<lastmod>{TODAY}</lastmod>", block)

    new_text = re.sub(r"<url>.*?</url>", bump, text, flags=re.S)
    write(path, new_text)


# ── 10. generate.py template sync ───────────────────────────────────────
def update_generate_py() -> None:
    path = ROOT / "generate.py"
    text = read(path)
    text = text.replace(
        'seo_title = (w.get("seo_title") or "").strip() or f"{w[\'name\']} | Traverse City Winery Guide"',
        'seo_title = (w.get("seo_title") or "").strip() or _winery_seo_title(w["name"])',
    )
    text = text.replace(
        'seo_desc = (w.get("seo_description") or "").strip() or w.get("description", w["name"])',
        'seo_desc = (w.get("seo_description") or "").strip() or _winery_seo_desc(w["name"], w["peninsula"])',
    )

    helper = '''
def _winery_seo_title(name: str) -> str:
    full = f"{name} | Hours, Map & Wine-Tour Stop in Traverse City"
    if len(full) <= 60:
        return full
    short = f"{name} | Hours, Map & Wine-Tour Stop"
    if len(short) <= 60:
        return short
    return f"{name} | Hours, Map & Tour Stop"

def _winery_seo_desc(name: str, peninsula: str) -> str:
    pen = f"{peninsula} Peninsula" if not str(peninsula).endswith("Peninsula") else peninsula
    return (
        f"Planning a visit to {name} on {pen}? Tasting highlights, hours, "
        "and how to add it to a private wine tour."
    )

'''
    if "_winery_seo_title" not in text:
        # insert before head()
        text = text.replace("\ndef head(", helper + "\ndef head(", 1)

    # Convert common .html hrefs in templates to clean URLs
    replacements = [
        ('href="{prefix}index.html"', 'href="{prefix}"' if False else 'href="/"'),
        # carefully update navbar/footer — use clean paths
    ]
    # Navbar
    old_nav = '''def navbar(prefix=""):
    return f\'\'\'<nav id="mainNav">
  <div class="nav-inner">
    <a href="{prefix}index.html" class="logo"><span class="logo-main">Traverse City Wine</span><span class="logo-sub">Tours & Winery Guide</span></a>
    <ul class="nav-links">
      <li><a href="{prefix}wineries/index.html">Wineries</a></li>
      <li><a href="{prefix}old-mission-peninsula.html">Old Mission</a></li>
      <li><a href="{prefix}leelanau-peninsula.html">Leelanau</a></li>
      <li><a href="{prefix}journal/index.html">Journal</a></li>
      <li><a href="{prefix}plan-your-visit.html">Plan a Visit</a></li>
      <li><a href="{prefix}wine-tours.html" class="nav-cta">Book a Tour</a></li>
    </ul>
    <button class="nav-toggle" onclick="document.querySelector('.nav-links').classList.toggle('show')">{ICON_MENU}</button>
  </div>
</nav>\'\'\''''
    new_nav = '''def navbar(prefix=""):
    # prefix kept for back-compat; live pages use root-absolute clean URLs
    return f\'\'\'<nav id="mainNav">
  <div class="nav-inner">
    <a href="/" class="logo"><span class="logo-main">Traverse City Wine</span><span class="logo-sub">Tours & Winery Guide</span></a>
    <ul class="nav-links">
      <li><a href="/wineries/">Wineries</a></li>
      <li><a href="/cideries/">Cideries</a></li>
      <li><a href="/breweries/">Breweries</a></li>
      <li><a href="/journal/">Journal</a></li>
      <li><a href="/plan-your-day">Plan Your Day</a></li>
      <li><a href="/wine-tours" class="nav-cta">Book a Tour</a></li>
    </ul>
    <button class="nav-toggle" onclick="document.querySelector('.nav-links').classList.toggle('show')">{ICON_MENU}</button>
  </div>
</nav>\'\'\''''
    if old_nav in text:
        text = text.replace(old_nav, new_nav)

    # Generic .html link cleanup inside generate.py string templates for common patterns
    for a, b in [
        ("wineries/index.html", "wineries/"),
        ("wine-tours.html", "wine-tours"),
        ("old-mission-peninsula.html", "old-mission-peninsula"),
        ("leelanau-peninsula.html", "leelanau-peninsula"),
        ("journal/index.html", "journal/"),
        ("plan-your-visit.html", "plan-your-visit"),
        ("plan-your-day.html", "plan-your-day"),
        ("where-to-stay.html", "where-to-stay"),
        ("bachelorette.html", "bachelorette"),
        ("events.html", "events"),
        ("advertise.html", "advertise"),
        ("contact.html", "contact"),
        ("privacy.html", "privacy"),
        ("about.html", "about"),
        ("sitemap.html", "sitemap"),
        ('href="../index.html"', 'href="/"'),
        ('href="index.html"', 'href="/"'),
        ('href="../wine-tours.html"', 'href="/wine-tours"'),
        ('href="wine-tours.html"', 'href="/wine-tours"'),
    ]:
        text = text.replace(a, b)

    # Fix winery card links that still use {slug}.html → /wineries/{slug}
    text = text.replace(
        'href="{prefix}wineries/{w[\'slug\']}.html"',
        'href="/wineries/{w[\'slug\']}"',
    )
    text = text.replace(
        "href=\"{prefix}wineries/{w['slug']}.html\"",
        "href=\"/wineries/{w['slug']}\"",
    )
    # journal cards
    text = text.replace('href="journal/{a["slug"]}.html"', 'href="/journal/{a["slug"]}"')
    text = text.replace("href=\"journal/{a['slug']}.html\"", "href=\"/journal/{a['slug']}\"")
    text = text.replace('href="{a["slug"]}.html"', 'href="/journal/{a["slug"]}"')

    write(path, text)


def main() -> None:
    update_homepage()
    update_wine_tours()
    update_tour_guides()
    update_wineries_index()
    update_retitles()
    update_winery_pages()
    add_wineries_anchor_links()
    harden_listitems()
    update_generate_py()

    changed = {c[0] for c in CHANGELOG}
    changed.update(
        {
            "wineries/index.html",
            "wine-tour-guides/index.html",
            "winery-map.html",
            "bachelorette.html",
            "generate.py",
        }
    )
    # all winery pages touched
    for p in (ROOT / "wineries").glob("*.html"):
        if p.name not in ("index.html", "45-north.html"):
            changed.add(f"wineries/{p.name}")
    update_sitemap(changed)

    report = ROOT / "scripts" / "_seo_pass_changelog.json"
    report.write_text(json.dumps(CHANGELOG, indent=2), encoding="utf-8")
    print(f"Logged {len(CHANGELOG)} field changes to {report}")
    # titles summary
    titles = [(p, o, n) for p, f, o, n in CHANGELOG if f == "title"]
    print(f"Title changes: {len(titles)}")
    for p, o, n in titles:
        print(f"  {p}\n    OLD: {o}\n    NEW: {n}")


if __name__ == "__main__":
    main()
