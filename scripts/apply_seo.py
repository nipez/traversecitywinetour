#!/usr/bin/env python3
"""Apply technical SEO fixes across the static Traverse City Wine Tour site."""

from __future__ import annotations

import json
import re
from datetime import date
from html import escape, unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://traversecitywinetour.com"
TODAY = date.today().isoformat()
OG_IMAGE = f"{SITE}/vineyard.jpg"
OG_ALT = "Vineyards in Traverse City wine country, Michigan"

PAGE_TITLES = {
    "index.html": "Traverse City Wine Tours | Michigan Winery Guide",
    "wineries/index.html": "Traverse City Wineries | Old Mission & Leelanau",
    "breweries/index.html": "Traverse City Breweries | Craft Beer Guide",
    "cideries/index.html": "Traverse City Cideries | Hard Cider Guide",
    "journal/index.html": "Wine Country Journal | Traverse City Guides",
    "plan-your-day.html": "Plan Your Wine Day | Traverse City Itineraries",
    "plan-your-visit.html": "Visitor Guide | Traverse City Wine Country",
    "wine-tours.html": "Book a Traverse City Wine Tour | Private & Group",
    "winery-map.html": "Interactive Winery Map | Traverse City Wine Trail",
    "where-to-stay.html": "Where to Stay | Traverse City Wine Country",
    "old-mission-peninsula.html": "Old Mission Peninsula Wineries | Traverse City",
    "leelanau-peninsula.html": "Leelanau Peninsula Wineries | Traverse City",
    "about.html": "About | Traverse City Wine Tour",
    "privacy.html": "Privacy Policy | Traverse City Wine Tour",
    "contact.html": "Contact | Traverse City Wine Tour",
    "events.html": "Wine Country Seasons | Traverse City Events Guide",
    "advertise.html": "Advertise | Traverse City Wine Tour",
    "bachelorette.html": "Bachelorette Wine Tours | Traverse City",
    "sitemap.html": "Sitemap | Traverse City Wine Tour",
    "wineries/forty-five-north.html": "Forty-Five North | TC Winery Guide",
    "wineries/gills-pier.html": "Gill's Pier | TC Winery Guide",
    "breweries/shorts-brewing-elk-rapids.html": "Short's Elk Rapids | TC Brewery Guide",
    "breweries/shorts-brewing-bellaire.html": "Short's Bellaire Pub | TC Brewery Guide",
    "breweries/jolly-pumpkin.html": "Jolly Pumpkin | TC Brewery Guide",
    "wineries/tandem-ciders.html": "Tandem Ciders on the Wine Trail | TC Winery Guide",
    "cideries/tandem-ciders.html": "Tandem Ciders | Traverse City Cidery Guide",
    "journal/first-timers-guide-wine-tasting-traverse-city.html": "First-Timer's Wine Tasting Guide | TC Wine Journal",
    "journal/48-hour-traverse-city-wine-weekend.html": "48-Hour Wine Weekend | TC Wine Journal",
    "journal/best-rieslings-traverse-city.html": "Best Traverse City Rieslings | TC Wine Journal",
    "journal/harvest-season-traverse-city.html": "Harvest Season Wineries | TC Wine Journal",
    "journal/l-mawby-michigan-sparkling-wine.html": "L. Mawby Sparkling Wine | TC Wine Journal",
    "journal/michigan-riesling-moment.html": "Why Michigan Riesling Matters | TC Wine Journal",
    "journal/old-mission-vs-leelanau.html": "Old Mission vs Leelanau | TC Wine Journal",
    "journal/traverse-city-wine-dinner-itinerary.html": "Wine & Dinner Itinerary | TC Wine Journal",
    "journal/winter-wine-trail.html": "Winter Wine Trail | TC Wine Journal",
}

PAGE_DESCS = {
    "index.html": "Plan a Traverse City wine trip. Explore 40+ wineries on Old Mission and Leelanau Peninsulas, plus cideries, breweries, maps, and tasting itineraries.",
    "wineries/index.html": "Complete guide to Traverse City wineries on Old Mission and Leelanau Peninsulas, with tasting hours, directions, and what each room is known for.",
    "breweries/index.html": "Guide to Traverse City craft breweries — downtown taprooms, Leelanau beer gardens, and brewpubs including Rare Bird, Workshop, and Hop Lot.",
    "cideries/index.html": "Find Traverse City cideries and hard-cider tasting rooms, from Tandem Ciders on Leelanau to downtown Taproot and Left Foot Charley.",
    "journal/index.html": "Traverse City wine-country guides: first-timer tasting tips, peninsula comparisons, Riesling picks, harvest season, and weekend itineraries.",
    "plan-your-day.html": "Build a Traverse City wine-day itinerary. Click winery pins on the map or start with a curated Old Mission or Leelanau route.",
    "plan-your-visit.html": "Plan your Traverse City wine country visit: when to go, how many tasting rooms to book, where to stay, and how to get between the peninsulas.",
    "wine-tours.html": "Book a guided Traverse City wine tour. Compare private drivers, group shuttles, and custom Old Mission or Leelanau itineraries.",
    "winery-map.html": "Explore 40+ Traverse City wineries on an interactive map of Old Mission and Leelanau Peninsulas. Zoom, filter, and plan tasting stops.",
    "where-to-stay.html": "Find hotels, vineyard B&Bs, and downtown inns for a Traverse City wine-country trip, including stays at Chateau Chantal and Black Star Farms.",
    "old-mission-peninsula.html": "Visit Old Mission Peninsula wineries near Traverse City. Tasting rooms, hours, and a compact bay-to-bay wine trail you can drive in a day.",
    "leelanau-peninsula.html": "Explore Leelanau Peninsula wineries near Traverse City. Tasting rooms from Suttons Bay to Northport, plus hours and visitor tips.",
    "about.html": "Traverse City Wine Tour is an independent guide to wineries, cideries, and breweries on Old Mission and Leelanau Peninsulas.",
    "privacy.html": "How Traverse City Wine Tour collects, stores, and uses emails and form submissions for newsletters, lodging listings, and planning kits.",
    "contact.html": "Contact Traverse City Wine Tour for listing updates, advertising, and visitor questions about Michigan wine country.",
    "events.html": "A seasonal guide to Traverse City wine country: blossom trail, cherry festival, harvest tastings, and winter wine rooms on Old Mission and Leelanau.",
    "advertise.html": "Advertise on Traverse City Wine Tour. Reach visitors planning Michigan wine-country trips with enhanced listings and sponsored profiles.",
    "bachelorette.html": "Plan a Traverse City bachelorette wine tour. Private drivers, tasting-room etiquette, and itineraries for Old Mission and Leelanau.",
    "wineries/willow-vineyard.html": "Willow Vineyard sits on a wind-swept Suttons Bay hillside with West Bay views, estate Pinot Noir, Chardonnay, and seasonal tastings.",
    "wineries/shady-lane-cellars.html": "Taste Riesling and Pinot Noir at Shady Lane Cellars, a Leelanau winery in a restored 1800s fieldstone chicken coop.",
    "wineries/left-foot-charley.html": "Left Foot Charley is an urban Traverse City winery in the Commons, known for natural Rieslings and a lively tasting room.",
    "wineries/forty-five-north.html": "Forty-Five North sits on the 45th parallel above Lake Leelanau, with bold reds, hilltop views, and a modern tasting room.",
    "wineries/ciccone-vineyard.html": "Ciccone Vineyard is a family estate on Leelanau Peninsula making Italian-inspired wines, from Dolcetto to Gewürztraminer.",
    "wineries/gills-pier.html": "Gill's Pier is a small Northport-area estate winery with limited Riesling, Pinot Noir, and Pinot Gris from Leelanau fruit.",
    "wineries/chateau-grand-traverse.html": "Chateau Grand Traverse pioneered Old Mission vinifera in 1974 and remains a must-stop for Riesling, ice wine, and bay views.",
    "wineries/laurentide-winery.html": "Laurentide Winery takes its name from the glacier that shaped Leelanau, with estate wines on rolling peninsula farmland.",
    "wineries/bowers-harbor-vineyards.html": "Bowers Harbor is a relaxed Old Mission favorite for approachable wines, a friendly tasting room, and a fun wine-trail stop.",
    "wineries/chateau-de-leelanau.html": "Chateau de Leelanau makes estate grape wines and hard cider on the Leelanau Peninsula wine trail.",
    "cideries/bel-lago-cidery.html": "Bel Lago crafts estate wines and heritage-style hard ciders on a Lake Leelanau hillside tasting-room property.",
    "wineries/verterra-winery.html": "Verterra is a small-batch Leland winery known for Grüner Veltliner, Pinot Noir, and artisan wines near Fishtown.",
    "sitemap.html": "Browse every Traverse City Wine Tour page: wineries, cideries, breweries, journal guides, and trip-planning tools.",
    "wineries/tandem-ciders.html": "Visit Tandem Ciders as a Leelanau wine-trail stop. Farmhouse ciders from local apples in a rustic Suttons Bay barn tasting room.",
    "cideries/tandem-ciders.html": "Tandem Ciders crafts small-batch, terroir-driven hard cider from Leelanau and Old Mission apples in a rustic Suttons Bay barn.",
    "journal/first-timers-guide-wine-tasting-traverse-city.html": "Everything you need before a first Traverse City tasting: fees, how many wineries to visit, what to wear, and where to start on each peninsula.",
    "journal/48-hour-traverse-city-wine-weekend.html": "A 48-hour Traverse City wine-country weekend: where to taste, eat, and stay on Old Mission and Leelanau without overbooking the day.",
    "journal/best-rieslings-traverse-city.html": "A tasting guide to the best Rieslings in Traverse City, from dry Old Mission bottles to late-harvest and ice wines on Leelanau Peninsula.",
    "journal/harvest-season-traverse-city.html": "The best Traverse City wineries to visit during harvest, when the vineyards are working and tasting rooms pour the vintage as it comes in.",
    "journal/l-mawby-michigan-sparkling-wine.html": "Why L. Mawby is America's most acclaimed sparkling-wine house, and what to taste on a quiet back road in Leelanau County.",
    "journal/michigan-riesling-moment.html": "Why Rieslings from Old Mission and Leelanau are winning awards and drawing comparisons to the world's best cool-climate whites.",
    "journal/old-mission-vs-leelanau.html": "Old Mission vs. Leelanau: a side-by-side look at Traverse City's two wine trails to help you choose the right peninsula for your day.",
    "journal/traverse-city-wine-dinner-itinerary.html": "A Traverse City wine-and-dinner itinerary that sequences tasting rooms so you arrive at the table calibrated, not exhausted.",
    "journal/winter-wine-trail.html": "Why winter may be the best time for a Traverse City wine trail: quieter tasting rooms, cozy hours, and ice wine from the vine.",
}

TITLE_SHORTEN = [
    (" | Traverse City Wine Country Journal", " | TC Wine Journal"),
    (" | Traverse City Winery Guide", " | TC Winery Guide"),
    (" | Traverse City Brewery Guide", " | TC Brewery Guide"),
    (" | Traverse City Cidery Guide", " | TC Cidery Guide"),
    (" | Traverse City Wine Tours", " | TC Wine Tours"),
    (" | Traverse City Wine Tour", " | TC Wine Tour"),
    (" | Traverse City Wine Guide", " | TC Wine Guide"),
    (" | Traverse City Wine & Craft Beverage Guide", " | TC Wine Guide"),
    (" | Ultimate Planning Guide", " | Planning Guide"),
]


def load_json(name: str):
    return json.loads((ROOT / name).read_text())


WINERIES = {w["slug"]: w for w in load_json("data-wineries.json")["wineries"]}
BREWERIES = {b["slug"]: b for b in load_json("data-breweries.json")}
CIDERIES = {c["slug"]: c for c in load_json("data-cideries.json")}


def html_pages() -> list[Path]:
    return sorted(
        p
        for p in ROOT.rglob("*.html")
        if ".git" not in p.parts
        and "scripts" not in p.parts
        and "admin" not in p.parts
        and "node_modules" not in p.parts
        and "functions" not in p.parts
    )


def rel_of(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def page_url(path: Path) -> str:
    rel = rel_of(path)
    if rel == "index.html":
        return f"{SITE}/"
    if rel.endswith("/index.html"):
        return f"{SITE}/{rel[:-10]}"
    return f"{SITE}/{rel[:-5]}"


def prefix_for(path: Path) -> str:
    depth = len(path.relative_to(ROOT).parts) - 1
    return "../" * depth


def attr(text: str) -> str:
    return escape(text, quote=True)


def fully_unescape(text: str) -> str:
    prev = None
    while text != prev:
        prev = text
        text = unescape(text)
    return text.replace("\xa0", " ")


def meta_desc(text: str, max_len: int = 155) -> str:
    text = re.sub(r"\s+", " ", (text or "")).strip()
    text = text.replace("...", "").strip()
    if not text:
        return ""
    if len(text) <= max_len:
        if text[-1] not in ".!?" and len(text) >= 80:
            text = text.rstrip(" ,;:") + "."
        return text
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = ""
    for part in parts:
        cand = f"{out} {part}".strip() if out else part
        if len(cand) <= max_len:
            out = cand
        else:
            break
    if len(out) >= 90:
        return out
    chunk = text[:max_len]
    for sep in (" — ", " – ", "; ", ", "):
        idx = chunk.rfind(sep)
        if idx >= 90:
            return chunk[:idx].rstrip(" ,;:") + "."
    return chunk.rsplit(" ", 1)[0].rstrip(" ,;:…") + "."


def fit_title(title: str, max_len: int = 60) -> str:
    title = re.sub(r"\s+", " ", title).strip()
    if len(title) <= max_len:
        return title
    for old, new in TITLE_SHORTEN:
        if old in title:
            title = title.replace(old, new)
            if len(title) <= max_len:
                return title
    if len(title) <= max_len:
        return title
    # Prefer a complete short title over an ellipsis Google will show as-is.
    if " | " in title:
        left = title.split(" | ", 1)[0].strip()
        if len(left) <= max_len:
            return left
        title = left
    return title[:max_len].rsplit(" ", 1)[0]


def existing_title(html: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    return fully_unescape(re.sub(r"\s+", " ", m.group(1)).strip()) if m else ""


def existing_desc(html: str) -> str:
    m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.I | re.S)
    if not m:
        m = re.search(r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']', html, re.I | re.S)
    return fully_unescape(m.group(1).strip()) if m else ""


def first_paragraph(html: str) -> str:
    body = html.split("</head>", 1)[-1]
    about = re.search(r"<h2[^>]*>About[^<]*</h2>\s*<p(?:\s[^>]*)?>(.*?)</p>", body, re.I | re.S)
    candidates = [about] if about else []
    candidates.extend(re.finditer(r"<p(?:\s[^>]*)?>(.*?)</p>", body, re.I | re.S))
    for m in candidates:
        if not m:
            continue
        text = re.sub(r"<[^>]+>", "", m.group(1))
        text = re.sub(r"\s+", " ", text).strip()
        if "›" in text or text.startswith("Home") or "min read" in text.lower():
            continue
        if len(text) >= 60:
            return text
    return ""


def venue_for(path: Path):
    rel = rel_of(path)
    parts = rel.split("/")
    if len(parts) != 2 or parts[1] == "index.html":
        return None
    slug = parts[1][:-5]
    if parts[0] == "wineries":
        return WINERIES.get(slug), "Winery"
    if parts[0] == "breweries":
        return BREWERIES.get(slug), "Brewery"
    if parts[0] == "cideries":
        return CIDERIES.get(slug), "Cidery"
    return None


def parse_address(addr: str) -> dict:
    parts = [p.strip() for p in (addr or "").split(",")]
    street = parts[0] if parts else ""
    city = "Traverse City"
    region = "MI"
    postal = ""
    if len(parts) >= 3:
        city = parts[1]
        m = re.search(r"([A-Z]{2})\s+(\d{5})", parts[-1])
        if m:
            region, postal = m.group(1), m.group(2)
    elif len(parts) == 2:
        m = re.search(r"([A-Z]{2})\s+(\d{5})", parts[1])
        if m:
            region, postal = m.group(1), m.group(2)
        else:
            city = parts[1]
    data = {
        "@type": "PostalAddress",
        "streetAddress": street,
        "addressLocality": city,
        "addressRegion": region,
        "addressCountry": "US",
    }
    if postal:
        data["postalCode"] = postal
    return data


def choose_title(path: Path, html: str) -> str:
    rel = rel_of(path)
    if rel in PAGE_TITLES:
        return PAGE_TITLES[rel]
    return fit_title(existing_title(html) or path.stem.replace("-", " ").title())


def choose_desc(path: Path, html: str) -> str:
    rel = rel_of(path)
    if rel in PAGE_DESCS:
        return PAGE_DESCS[rel]
    venue = venue_for(path)
    if venue and venue[0]:
        rec = venue[0]
        raw = rec.get("description") or rec.get("long_description") or ""
        if raw:
            return meta_desc(raw)
        para = first_paragraph(html)
        if para:
            return meta_desc(para)
    current = existing_desc(html)
    garbage = (not current) or ("›" in current) or current.startswith("Home") or len(current) < 70
    if current and not garbage and len(current) >= 110 and current[-1] in ".!?":
        return meta_desc(current, 160)
    para = first_paragraph(html)
    if para:
        return meta_desc(para)
    if current:
        return meta_desc(current)
    name = (venue[0].get("name") if venue and venue[0] else choose_title(path, html).split("|")[0].strip())
    peninsula = (venue[0].get("peninsula") if venue and venue[0] else "Traverse City")
    return meta_desc(f"Visit {name} on {peninsula} Peninsula. Tasting room details, hours, and what to expect on a Traverse City wine-country stop.")


def breadcrumbs(path: Path) -> list[dict]:
    rel = rel_of(path)
    crumbs = [{"name": "Home", "item": f"{SITE}/"}]
    if rel == "index.html":
        return crumbs
    mapping = {
        "wineries": ("Wineries", f"{SITE}/wineries/"),
        "breweries": ("Breweries", f"{SITE}/breweries/"),
        "cideries": ("Cideries", f"{SITE}/cideries/"),
        "journal": ("Journal", f"{SITE}/journal/"),
    }
    parts = rel.split("/")
    if parts[0] in mapping:
        crumbs.append({"name": mapping[parts[0]][0], "item": mapping[parts[0]][1]})
    if not rel.endswith("/index.html"):
        crumbs.append({"name": choose_title(path, path.read_text(errors="replace")).split("|")[0].strip(), "item": page_url(path)})
    return crumbs


def breadcrumb_ld(path: Path) -> dict:
    crumbs = breadcrumbs(path)
    return {
        "@type": "BreadcrumbList",
        "@id": page_url(path) + "#breadcrumbs",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": c["name"], "item": c["item"]}
            for i, c in enumerate(crumbs)
        ],
    }


def children_of(folder: str) -> list[Path]:
    d = ROOT / folder
    pages = []
    for p in sorted(d.glob("*.html")):
        if p.name == "index.html":
            continue
        if folder == "wineries" and p.name == "45-north.html":
            continue
        pages.append(p)
    return pages


def collection_ld(path: Path, name: str, desc: str, folder: str | None, peninsula: str | None = None) -> dict:
    graph = [
        {
            "@type": "CollectionPage",
            "@id": page_url(path),
            "url": page_url(path),
            "name": name,
            "description": desc,
            "isPartOf": {"@id": f"{SITE}/#website"},
        }
    ]
    if folder:
        items = children_of(folder)
        if peninsula:
            items = [p for p in items if WINERIES.get(p.stem, {}).get("peninsula") == peninsula]
        graph.append(
            {
                "@type": "ItemList",
                "name": name,
                "numberOfItems": len(items),
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "url": page_url(p), "name": choose_title(p, p.read_text(errors="replace")).split("|")[0].strip()}
                    for i, p in enumerate(items)
                ],
            }
        )
    return {"@context": "https://schema.org", "@graph": graph + [breadcrumb_ld(path)]}


def venue_ld(path: Path, rec: dict, schema_type: str, name: str, desc: str) -> dict:
    schema_type = {"Winery": "Winery", "Brewery": "Brewery", "Cidery": "Winery"}.get(schema_type, "LocalBusiness")
    extra_type = "Cidery" if rel_of(path).startswith("cideries/") or rec.get("type", "").lower().find("cider") >= 0 else None
    node = {
        "@type": [schema_type, "LocalBusiness"] if extra_type else schema_type,
        "@id": page_url(path) + "#place",
        "name": rec.get("name") or name.split("|")[0].strip(),
        "description": rec.get("description") or desc,
        "url": page_url(path),
        "address": parse_address(rec.get("address", "")),
    }
    if extra_type:
        node["@type"] = ["Winery", "LocalBusiness"]
        node["additionalType"] = "https://schema.org/Winery"
    if rec.get("phone"):
        node["telephone"] = rec["phone"]
    if rec.get("website"):
        node["sameAs"] = [rec["website"]]
    if rec.get("lat") and rec.get("lng"):
        node["geo"] = {"@type": "GeoCoordinates", "latitude": rec["lat"], "longitude": rec["lng"]}
    if rec.get("hours"):
        node["openingHours"] = rec["hours"]
    return {"@context": "https://schema.org", "@graph": [node, breadcrumb_ld(path)]}


def website_ld(title: str, desc: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": f"{SITE}/#website",
                "url": f"{SITE}/",
                "name": "Traverse City Wine Tour",
                "alternateName": ["Traverse City Wine Guide", "TraverseCityWineTour.com"],
                "description": desc,
                "inLanguage": "en-US",
                "publisher": {"@id": f"{SITE}/#org"},
            },
            {
                "@type": ["Organization", "TouristInformationCenter"],
                "@id": f"{SITE}/#org",
                "name": "Traverse City Wine Tour",
                "url": f"{SITE}/",
                "logo": f"{SITE}/logo.svg",
                "email": "hello@traversecitywinetour.com",
                "areaServed": [
                    "Traverse City",
                    "Old Mission Peninsula",
                    "Leelanau Peninsula",
                    "Michigan",
                ],
                "description": desc,
            },
            {
                "@type": "WebPage",
                "@id": f"{SITE}/",
                "url": f"{SITE}/",
                "name": title,
                "description": desc,
                "isPartOf": {"@id": f"{SITE}/#website"},
                "about": {"@id": f"{SITE}/#org"},
            },
        ],
    }


def article_ld(path: Path, title: str, desc: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "@id": page_url(path) + "#article",
                "headline": title.split("|")[0].strip(),
                "description": desc,
                "mainEntityOfPage": page_url(path),
                "image": OG_IMAGE,
                "author": {"@id": f"{SITE}/#org"},
                "publisher": {"@id": f"{SITE}/#org"},
                "inLanguage": "en-US",
            },
            breadcrumb_ld(path),
        ],
    }


def webpage_ld(path: Path, title: str, desc: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": page_url(path),
                "url": page_url(path),
                "name": title,
                "description": desc,
                "isPartOf": {"@id": f"{SITE}/#website"},
            },
            breadcrumb_ld(path),
        ],
    }


def json_ld_for(path: Path, title: str, desc: str) -> dict:
    rel = rel_of(path)
    if rel == "index.html":
        return website_ld(title, desc)
    if rel == "wineries/index.html":
        return collection_ld(path, title, desc, "wineries")
    if rel == "old-mission-peninsula.html":
        return collection_ld(path, title, desc, "wineries", peninsula="Old Mission")
    if rel == "leelanau-peninsula.html":
        return collection_ld(path, title, desc, "wineries", peninsula="Leelanau")
    if rel == "breweries/index.html":
        return collection_ld(path, title, desc, "breweries")
    if rel == "cideries/index.html":
        return collection_ld(path, title, desc, "cideries")
    if rel == "journal/index.html":
        return collection_ld(path, title, desc, "journal")
    if rel.startswith("journal/") and rel != "journal/index.html":
        return article_ld(path, title, desc)
    venue = venue_for(path)
    if venue and venue[0]:
        return venue_ld(path, venue[0], venue[1], title, desc)
    return webpage_ld(path, title, desc)


HEAD_REMOVE = [
    re.compile(r"<title>.*?</title>\s*", re.I | re.S),
    re.compile(r"<meta\s+name=[\"']description[\"'][^>]*>\s*", re.I),
    re.compile(r"<meta\s+content=[\"'][^\"']*[\"']\s+name=[\"']description[\"'][^>]*>\s*", re.I),
    re.compile(r"<link\s+rel=[\"']canonical[\"'][^>]*>\s*", re.I),
    re.compile(r"<link\s+href=[\"'][^\"']*[\"']\s+rel=[\"']canonical[\"'][^>]*>\s*", re.I),
    re.compile(r"<meta\s+property=[\"']og:[^\"']+[\"'][^>]*>\s*", re.I),
    re.compile(r"<meta\s+name=[\"']twitter:[^\"']+[\"'][^>]*>\s*", re.I),
    re.compile(r"<link\s+rel=[\"'](?:icon|shortcut icon|apple-touch-icon)[\"'][^>]*>\s*", re.I),
    re.compile(r"<meta\s+name=[\"']robots[\"'][^>]*>\s*", re.I),
]

LD_RE = re.compile(r'<script\s+type=["\']application/ld\+json["\']>.*?</script>\s*', re.I | re.S)


def seo_head_block(path: Path, title: str, desc: str, canonical: str, noindex: bool = False) -> str:
    prefix = prefix_for(path)
    og_type = "article" if rel_of(path).startswith("journal/") and not rel_of(path).endswith("index.html") else "website"
    robots = "noindex, follow" if noindex else "index, follow"
    return "\n".join(
        [
            f"<title>{attr(title)}</title>",
            f'<meta name="description" content="{attr(desc)}">',
            f'<link rel="canonical" href="{attr(canonical)}">',
            f'<meta name="robots" content="{robots}">',
            f'<link rel="icon" href="{prefix}logo.svg" type="image/svg+xml">',
            f'<link rel="apple-touch-icon" href="{prefix}logo.svg">',
            f'<meta property="og:type" content="{og_type}">',
            '<meta property="og:site_name" content="Traverse City Wine Tour">',
            '<meta property="og:locale" content="en_US">',
            f'<meta property="og:title" content="{attr(title)}">',
            f'<meta property="og:description" content="{attr(desc)}">',
            f'<meta property="og:url" content="{attr(canonical)}">',
            f'<meta property="og:image" content="{OG_IMAGE}">',
            f'<meta property="og:image:alt" content="{attr(OG_ALT)}">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{attr(title)}">',
            f'<meta name="twitter:description" content="{attr(desc)}">',
            f'<meta name="twitter:image" content="{OG_IMAGE}">',
        ]
    )


def insert_head(html: str, block: str) -> str:
    for rx in HEAD_REMOVE:
        html = rx.sub("", html)
    if re.search(r'<meta\s+name=["\']viewport["\']', html, re.I):
        html = re.sub(
            r'(<meta\s+name=["\']viewport["\'][^>]*>)',
            r"\1\n" + block,
            html,
            count=1,
            flags=re.I,
        )
    elif re.search(r"<meta[^>]+charset", html, re.I):
        html = re.sub(r"(<meta[^>]+charset[^>]*>)", r"\1\n" + block, html, count=1, flags=re.I)
    else:
        html = html.replace("<head>", "<head>\n" + block, 1)
    return html


def insert_jsonld(html: str, data: dict) -> str:
    html = LD_RE.sub("", html)
    script = '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + "\n</script>\n"
    html = re.sub(r"(<body[^>]*>)", r"\1\n" + script, html, count=1, flags=re.I)
    return html


def decode_cf_email(hexstr: str) -> str:
    data = bytes.fromhex(hexstr)
    key = data[0]
    return "".join(chr(b ^ key) for b in data[1:])


def normalize_email(addr: str) -> str:
    addr = addr.replace("traversecitywinetours.com", "traversecitywinetour.com")
    return addr


def fix_cloudflare_emails(html: str) -> str:
    def repl_href(m):
        decoded = decode_cf_email(m.group(1))
        if "?" in decoded:
            email, qs = decoded.split("?", 1)
            email = normalize_email(email)
            return f'href="mailto:{email}?{qs}"'
        return f'href="mailto:{normalize_email(decoded)}"'

    html = re.sub(
        r'href="/cdn-cgi/l/email-protection#([0-9a-fA-F]+)"',
        repl_href,
        html,
    )

    def repl_span(m):
        decoded = normalize_email(decode_cf_email(m.group(1)))
        return decoded

    html = re.sub(
        r'<span class="__cf_email__" data-cfemail="([0-9a-fA-F]+)">\[email&#160;protected\]</span>',
        repl_span,
        html,
        flags=re.I,
    )
    html = re.sub(
        r'<script[^>]+src="/cdn-cgi/scripts/[^"]+email-decode[^"]+"[^>]*></script>',
        "",
        html,
        flags=re.I,
    )
    return html


FOOTER_CLOSE = """        <li><a href="sitemap.html">Sitemap</a></li>
      </ul></div>
    </div>
    <div class="footer-bottom">
      <span>&copy; 2026 TraverseCityWineTour.com &middot; All Rights Reserved</span>
      <div style="display: flex; gap: 24px;">
        <a href="sitemap.html">Sitemap</a>
      </div>
    </div>
  </div>
</footer>
<script>
const nav=document.getElementById('mainNav');
if(nav){window.addEventListener('scroll',()=>{nav.classList.toggle('scrolled',window.scrollY>10);});}
const obs=new IntersectionObserver(e=>{e.forEach(x=>{if(x.isIntersecting){x.target.style.opacity='1';x.target.style.transform='translateY(0)';}});},{threshold:0.1});
document.querySelectorAll('.winery-card,.article-card,.plan-card,.tour-card,.stay-card,.pricing-card,.fade-in,.journal-card,.pen-card').forEach(el=>{el.style.opacity='0';el.style.transform='translateY(20px)';el.style.transition='opacity 0.6s ease, transform 0.6s ease';obs.observe(el);});
</script>
</body>
</html>
"""


def repair_truncated() -> None:
    about = ROOT / "about.html"
    text = about.read_text(errors="replace")
    if "</html>" not in text[-200:]:
        text = re.sub(r"</footer>.*$", "</footer>\n", text, flags=re.S)
        # footer already complete; just close scripts
        if "</footer>" in text:
            text = text.split("</footer>")[0] + "</footer>\n<script>\nconst nav=document.getElementById('mainNav');\nif(nav){window.addEventListener('scroll',()=>{nav.classList.toggle('scrolled',window.scrollY>10);});}\nconst obs=new IntersectionObserver(e=>{e.forEach(x=>{if(x.isIntersecting){x.target.style.opacity='1';x.target.style.transform='translateY(0)';}});},{threshold:0.1});\ndocument.querySelectorAll('.winery-card,.article-card,.plan-card,.tour-card,.stay-card,.pricing-card,.fade-in,.journal-card,.pen-card').forEach(el=>{el.style.opacity='0';el.style.transform='translateY(20px)';el.style.transition='opacity 0.6s ease, transform 0.6s ease';obs.observe(el);});\n</script>\n</body>\n</html>\n"
        about.write_text(text)
        print("repaired about.html")

    contact = ROOT / "contact.html"
    text = contact.read_text(errors="replace")
    if "</html>" not in text[-200:]:
        if "</footer>" in text:
            text = text.split("</footer>")[0] + "</footer>\n<script>\nconst nav=document.getElementById('mainNav');\nif(nav){window.addEventListener('scroll',()=>{nav.classList.toggle('scrolled',window.scrollY>10);});}\n</script>\n</body>\n</html>\n"
        contact.write_text(text)
        print("repaired contact.html")

    advertise = ROOT / "advertise.html"
    text = advertise.read_text(errors="replace")
    if "</html>" not in text[-200:]:
        text = re.sub(r'\s*<li><a href="site\s*$', "\n" + FOOTER_CLOSE, text)
        advertise.write_text(text)
        print("repaired advertise.html")


def write_redirect_stub() -> None:
    (ROOT / "wineries" / "45-north.html").write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Forty-Five North Vineyard &amp; Winery | TC Winery Guide</title>
<meta name="description" content="Forty-Five North Vineyard &amp; Winery is listed at its canonical Traverse City winery page.">
<link rel="canonical" href="{SITE}/wineries/forty-five-north">
<meta name="robots" content="noindex, follow">
<meta http-equiv="refresh" content="0; url=../wineries/forty-five-north.html">
<link rel="icon" href="../logo.svg" type="image/svg+xml">
</head>
<body>
<p>This listing now lives at <a href="forty-five-north.html">Forty-Five North Vineyard &amp; Winery</a>.</p>
<script>location.replace('forty-five-north.html');</script>
</body>
</html>
"""
    )
    print("wrote wineries/45-north.html redirect stub")


def fix_sitewide_links(html: str, path: Path) -> str:
    html = html.replace("wine-glasses.jpg", "wineglasses.jpg")
    html = html.replace("wineries/45-north.html", "wineries/forty-five-north.html")
    html = re.sub(r'href="45-north\.html"', 'href="forty-five-north.html"', html)
    html = re.sub(r"href='45-north\.html'", "href='forty-five-north.html'", html)
    if rel_of(path) == "where-to-stay.html":
        html = html.replace('href="chateau-chantal.html"', 'href="wineries/chateau-chantal.html"')
        html = html.replace('href="black-star-farms.html"', 'href="wineries/black-star-farms.html"')
    if rel_of(path) == "cideries/index.html":
        html = html.replace('href="index.html"', 'href="../index.html"')
        html = html.replace('src="logo.svg"', 'src="../logo.svg"')
        for target in [
            "wineries/index.html",
            "cideries/index.html",
            "breweries/index.html",
            "old-mission-peninsula.html",
            "leelanau-peninsula.html",
            "wine-tours.html",
            "where-to-stay.html",
            "plan-your-visit.html",
            "plan-your-day.html",
            "journal/index.html",
            "advertise.html",
            "contact.html",
            "privacy.html",
            "sitemap.html",
        ]:
            html = html.replace(f'href="{target}"', f'href="../{target}"')
        # venue cards in the same folder should stay local
        html = html.replace('href="../tandem-ciders.html"', 'href="tandem-ciders.html"')
        html = html.replace('href="../suttons-bay-ciders.html"', 'href="suttons-bay-ciders.html"')
        html = html.replace('href="../taproot-cider-house.html"', 'href="taproot-cider-house.html"')
        html = html.replace('href="../northern-natural-cider-house.html"', 'href="northern-natural-cider-house.html"')
        html = html.replace('href="../bel-lago-cidery.html"', 'href="bel-lago-cidery.html"')
        html = html.replace('href="../left-foot-charley-cider.html"', 'href="left-foot-charley-cider.html"')
        # directory tabs were already ../ and got doubled
        html = html.replace("href=\"../../wineries/index.html\"", 'href="../wineries/index.html"')
        html = html.replace("href=\"../../breweries/index.html\"", 'href="../breweries/index.html"')
        html = html.replace("href=\"../../cideries/index.html\"", 'href="../cideries/index.html"')
    return html


def process_page(path: Path) -> None:
    rel = rel_of(path)
    if rel in {"wineries/45-north.html", "404.html", "admin/leads.html"}:
        return
    html = path.read_text(errors="replace")
    html = fix_cloudflare_emails(html)
    html = fix_sitewide_links(html, path)
    title = choose_title(path, html)
    desc = choose_desc(path, html)
    canonical = page_url(path)
    if rel == "wineries/tandem-ciders.html":
        # Keep the wine-trail URL live, but point Google at the stronger cidery page.
        canonical = f"{SITE}/cideries/tandem-ciders"
    html = insert_head(html, seo_head_block(path, title, desc, canonical, noindex=False))
    html = insert_jsonld(html, json_ld_for(path, title, desc))
    path.write_text(html)
    print(f"updated {rel}")


def write_robots() -> None:
    (ROOT / "robots.txt").write_text(
        f"""User-agent: *
Allow: /
Disallow: /admin/

Sitemap: {SITE}/sitemap.xml
"""
    )
    print("wrote robots.txt")


def write_redirects() -> None:
    (ROOT / "_redirects").write_text(
        """/wineries/45-north /wineries/forty-five-north 301
/wineries/45-north.html /wineries/forty-five-north 301
"""
    )
    print("wrote _redirects")


def write_sitemap() -> None:
    skip = {"wineries/45-north.html", "wineries/tandem-ciders.html", "404.html", "admin/leads.html"}
    urls = []
    for path in html_pages():
        rel = rel_of(path)
        if rel in skip:
            continue
        url = page_url(path)
        if rel == "index.html":
            pri, freq = "1.0", "weekly"
        elif rel in {"wineries/index.html", "winery-map.html", "plan-your-day.html", "wine-tours.html"}:
            pri, freq = "0.9", "weekly"
        elif rel.endswith("/index.html") or rel in {
            "old-mission-peninsula.html",
            "leelanau-peninsula.html",
            "where-to-stay.html",
            "plan-your-visit.html",
        }:
            pri, freq = "0.8", "weekly"
        elif rel.startswith("journal/"):
            pri, freq = "0.8", "monthly"
        elif rel.startswith(("wineries/", "breweries/", "cideries/")):
            pri, freq = "0.7", "monthly"
        elif rel in {"about.html", "contact.html", "advertise.html", "sitemap.html", "privacy.html"}:
            pri, freq = "0.4", "yearly"
        else:
            pri, freq = "0.6", "monthly"
        urls.append((url, freq, pri))
    urls.sort(key=lambda x: (0 if x[0] == f"{SITE}/" else 1, x[0]))
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url, freq, pri in urls:
        lines.extend(
            [
                "  <url>",
                f"    <loc>{url}</loc>",
                f"    <lastmod>{TODAY}</lastmod>",
                f"    <changefreq>{freq}</changefreq>",
                f"    <priority>{pri}</priority>",
                "  </url>",
            ]
        )
    lines.append("</urlset>\n")
    (ROOT / "sitemap.xml").write_text("\n".join(lines))
    print(f"wrote sitemap.xml ({len(urls)} urls)")


def write_404() -> None:
    (ROOT / "404.html").write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Page not found | Traverse City Wine Tour</title>
<meta name="description" content="That page is not on Traverse City Wine Tour. Head back to the winery guide, map, or trip planner.">
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{SITE}/404">
<link rel="icon" href="logo.svg" type="image/svg+xml">
<style>
body{{font-family:Georgia,serif;background:#FEFCF9;color:#3A3330;margin:0;padding:8vh 24px;text-align:center}}
a{{color:#4A0E1B}}
h1{{font-weight:500}}
</style>
</head>
<body>
<p><a href="index.html">Traverse City Wine Tour</a></p>
<h1>This page is not on the trail.</h1>
<p>Try the <a href="wineries/index.html">winery guide</a>, <a href="winery-map.html">winery map</a>, or <a href="plan-your-day.html">day planner</a>.</p>
</body>
</html>
"""
    )
    print("wrote 404.html")


def main() -> None:
    repair_truncated()
    write_redirect_stub()
    for path in html_pages():
        process_page(path)
    write_robots()
    write_redirects()
    write_sitemap()
    write_404()


if __name__ == "__main__":
    main()
