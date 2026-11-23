#!/usr/bin/env python3
"""Idempotent patcher for Open this week. Hours come only from data-*.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = (
    '<script src="/js/hours.js" defer></script>\n'
    '<script src="/js/open-this-week.js" defer></script>'
)
MOUNT = '<div id="openThisWeek" data-otw-scope="directory"></div>'
NOTE = "Hours change seasonally — call ahead to confirm before you go."
MISSING = "Hours not listed — check with the winery"

DAY_ALIASES = {
    "sun": 0, "sunday": 0, "mon": 1, "monday": 1, "tue": 2, "tues": 2, "tuesday": 2,
    "wed": 3, "wednesday": 3, "thu": 4, "thur": 4, "thurs": 4, "thursday": 4,
    "fri": 5, "friday": 5, "sat": 6, "saturday": 6,
}
DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def esc_attr(s: str) -> str:
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def esc_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_datasets():
    wineries = json.loads((ROOT / "data-wineries.json").read_text())["wineries"]
    cideries = json.loads((ROOT / "data-cideries.json").read_text())
    breweries = json.loads((ROOT / "data-breweries.json").read_text())
    return wineries, cideries, breweries


def hours_by_slug():
    wineries, cideries, breweries = load_datasets()
    out = {}
    for v in wineries + cideries + breweries:
        out[v["slug"]] = (v.get("hours") or "").strip()
    out["45-north"] = out.get("forty-five-north", "")
    return out


def hours_by_name():
    wineries, cideries, breweries = load_datasets()
    out = {}
    for v in wineries + cideries + breweries:
        out[v["name"].strip().lower()] = (v.get("hours") or "").strip()
    return out


def ensure_scripts(html: str) -> str:
    if "/js/hours.js" in html:
        return html
    return html.replace("</body>", SCRIPTS + "\n</body>", 1)


def ensure_mount_after(html: str, pattern: str) -> str:
    if 'id="openThisWeek"' in html:
        return html
    m = re.search(pattern, html)
    if not m:
        raise SystemExit(f"mount marker not found: {pattern}")
    i = m.end()
    return html[:i] + "\n" + MOUNT + html[i:]


def _norm(s: str) -> str:
    return (
        s.replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
        .replace("\u00b7", "·")
        .replace("\u2022", "·")
    )


def _parse_time(token: str, inherit_mer: str | None = None):
    t = re.sub(r"\s+", "", token.strip().lower())
    m = re.match(r"^(\d{1,2})(?::(\d{2}))?(am|pm)?$", t)
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    mer = m.group(3) or inherit_mer
    if not mer:
        return None
    if mer == "am":
        if hour == 12:
            hour = 0
    elif hour != 12:
        hour += 12
    return hour, minute


def parse_hours_spec(raw: str):
    if not (raw or "").strip():
        return None
    text = _norm(raw)
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    by_day = [None] * 7
    for seg in [s.strip() for s in text.split("·") if s.strip()]:
        m = re.match(
            r"^((?:daily|[A-Za-z]+(?:\s*-\s*[A-Za-z]+)?))\s+(\d.+)$",
            seg,
            re.I,
        )
        if not m:
            return None
        day_part, time_part = m.group(1).strip(), m.group(2).strip()
        tm = re.match(
            r"^(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s*-\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm))$",
            time_part,
            re.I,
        )
        if not tm:
            return None
        right_mer = None
        rm = re.search(r"([ap]m)$", tm.group(2), re.I)
        if rm:
            right_mer = rm.group(1).lower()
        right = _parse_time(tm.group(2))
        left = _parse_time(tm.group(1), inherit_mer=right_mer)
        if not left or not right:
            return None
        opens = f"{left[0]:02d}:{left[1]:02d}"
        closes = f"{right[0]:02d}:{right[1]:02d}"
        if right == (0, 0) and re.search(r"12\s*am", tm.group(2), re.I):
            closes = "00:00"
        dp = day_part.lower()
        if dp == "daily":
            days = list(range(7))
        elif "-" in dp:
            a, b = [x.strip() for x in re.split(r"\s*-\s*", dp)]
            if a not in DAY_ALIASES or b not in DAY_ALIASES:
                return None
            i, end = DAY_ALIASES[a], DAY_ALIASES[b]
            days = []
            for _ in range(7):
                days.append(i)
                if i == end:
                    break
                i = (i + 1) % 7
        else:
            if dp not in DAY_ALIASES:
                return None
            days = [DAY_ALIASES[dp]]
        for d in days:
            by_day[d] = (opens, closes)
    if not any(by_day):
        return None
    specs = []
    used = set()
    for di in [1, 2, 3, 4, 5, 6, 0]:
        if di in used or not by_day[di]:
            continue
        opens, closes = by_day[di]
        group = [di]
        used.add(di)
        for dj in [1, 2, 3, 4, 5, 6, 0]:
            if dj in used or not by_day[dj]:
                continue
            if by_day[dj] == (opens, closes):
                group.append(dj)
                used.add(dj)
        specs.append(
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": [DAY_NAMES[d] for d in group],
                "opens": opens,
                "closes": closes,
            }
        )
    return specs


def patch_wineries_index(hours_map: dict) -> None:
    path = ROOT / "wineries/index.html"
    html = path.read_text()

    def card_repl(m: re.Match) -> str:
        full = m.group(0)
        href = m.group(1)
        slug = href.rstrip("/").split("/")[-1]
        hours = hours_map.get(slug, "")
        if "data-hours=" in full:
            return re.sub(
                r'data-hours="[^"]*"',
                f'data-hours="{esc_attr(hours)}"',
                full,
                count=1,
            )
        return full.replace(
            'class="winery-card"',
            f'class="winery-card" data-hours="{esc_attr(hours)}"',
            1,
        )

    html = re.sub(
        r'<a href="(/wineries/[^"]+)" class="winery-card"[^>]*>',
        card_repl,
        html,
    )
    html = ensure_mount_after(html, r'<nav class="filter-bar">[\s\S]*?</nav>')
    html = ensure_scripts(html)
    path.write_text(html)
    print("✓ wineries/index.html")


def patch_venue_directory(rel: str, kind: str, items: list) -> None:
    path = ROOT / rel
    html = path.read_text()
    by_name = {v["name"].strip().lower(): (v.get("hours") or "").strip() for v in items}
    by_slug = {v["slug"]: (v.get("hours") or "").strip() for v in items}

    # Add data-hours onto venue-card divs by matching detail link slug or h3 name
    def venue_repl(m: re.Match) -> str:
        block = m.group(0)
        if "data-hours=" in block:
            return block
        slug_m = re.search(rf'href="/{kind}/([^"]+)"', block)
        hours = ""
        if slug_m:
            hours = by_slug.get(slug_m.group(1), "")
        if not hours:
            name_m = re.search(r"<h3>([^<]+)</h3>", block)
            if name_m:
                hours = by_name.get(name_m.group(1).strip().lower(), "")
        return block.replace(
            m.group(1),
            m.group(1) + f' data-hours="{esc_attr(hours)}"',
            1,
        )

    html = re.sub(
        r'(<div class="venue-card[^"]*")([\s\S]*?</div>\s*</div>)',
        lambda m: venue_repl(m) if True else m.group(0),
        html,
    )
    # The regex above is greedy/fragile — do line-oriented replacement instead
    html = path.read_text()
    out = []
    i = 0
    lines = html.splitlines(keepends=True)
    while i < len(lines):
        line = lines[i]
        if re.search(r'<div class="venue-card', line) and "data-hours=" not in line:
            # gather until venue-link closes this card (two closing divs after link)
            chunk = line
            j = i + 1
            while j < len(lines) and not (
                "</div>" in lines[j] and "venue-card" not in chunk[len(line) :]
            ):
                chunk += lines[j]
                j += 1
                # stop after we've seen the card body close — look for venue-link then two closes
                if j < len(lines) and "venue-link" in "".join(lines[max(i, j - 3) : j]):
                    # continue until two consecutive closing divs after link
                    pass
            # simpler: take next 12 lines as card body
            end = min(i + 14, len(lines))
            chunk = "".join(lines[i:end])
            slug_m = re.search(rf'href="/{kind}/([^"]+)"', chunk)
            hours = by_slug.get(slug_m.group(1), "") if slug_m else ""
            if not hours:
                name_m = re.search(r"<h3>([^<]+)</h3>", chunk)
                if name_m:
                    hours = by_name.get(name_m.group(1).strip().lower(), "")
            lines[i] = re.sub(
                r'(<div class="venue-card[^"]*")',
                rf'\1 data-hours="{esc_attr(hours)}"',
                line,
                count=1,
            )
        out.append(lines[i])
        i += 1
    html = "".join(out)

    # Mount after dir-tabs block
    if 'id="openThisWeek"' not in html:
        html = re.sub(
            r'(<div class="dir-tabs">[\s\S]*?</div>\s*</div>)',
            r"\1\n" + MOUNT,
            html,
            count=1,
        )
    html = ensure_scripts(html)
    path.write_text(html)
    print(f"✓ {rel}")


def hours_block(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw or parse_hours_spec(raw) is None:
        body = f"<div>{MISSING}</div><p class=\"winery-hours-note\">{NOTE}</p>"
        attr = ""
    else:
        body = (
            f'<div class="hours-raw">{esc_html(raw)}</div>'
            f'<p class="winery-hours-note">{NOTE}</p>'
        )
        attr = esc_attr(raw)
    return (
        f'<div class="sidebar-detail" data-hours-block data-hours="{attr}">'
        f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">'
        f'<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg> '
        f"<div>{body}</div></div>"
    )


def patch_winery_page(path: Path, hours: str) -> None:
    html = path.read_text()
    if "data-hours-block" in html:
        html = re.sub(
            r'data-hours-block data-hours="[^"]*"',
            f'data-hours-block data-hours="{esc_attr(hours)}"',
            html,
            count=1,
        )
    else:
        # Match ONLY the clock sidebar row (do not cross other sidebar-detail blocks)
        clock_re = re.compile(
            r'<div class="sidebar-detail"><svg[^>]*>'
            r'(?:(?!</svg>).)*'
            r'<circle cx="12" cy="12" r="10"/>'
            r'<path d="M12 6v6l4 2"/></svg>\s*<div>[^<]*</div></div>',
            re.M,
        )
        html, n = clock_re.subn(hours_block(hours), html, count=1)
        if n == 0:
            print(f"  ! clock not found: {path.name}")

    specs = parse_hours_spec(hours)
    if specs and "openingHoursSpecification" not in html:
        payload = json.dumps(specs, ensure_ascii=False)
        if '"openingHours"' in html:
            html = re.sub(
                r'("openingHours"\s*:\s*"[^"]*")',
                rf'\1,\n      "openingHoursSpecification": {payload}',
                html,
                count=1,
            )
        else:
            html = re.sub(
                r'("telephone"\s*:\s*"[^"]*")',
                rf'\1,\n      "openingHoursSpecification": {payload}',
                html,
                count=1,
            )
    html = ensure_scripts(html)
    path.write_text(html)
    print(f"  ✓ {path.name}")


def patch_all_wineries(hours_map: dict) -> None:
    wineries, _, _ = load_datasets()
    for w in wineries:
        slug = w["slug"]
        if slug == "tandem-ciders":
            continue
        page = ROOT / "wineries" / f"{slug}.html"
        if not page.exists() and slug == "forty-five-north":
            page = ROOT / "wineries/45-north.html"
        if page.exists():
            patch_winery_page(page, w.get("hours") or "")
    p45 = ROOT / "wineries/45-north.html"
    if p45.exists():
        patch_winery_page(p45, hours_map.get("forty-five-north", ""))


def patch_winery_map() -> None:
    path = ROOT / "winery-map.html"
    html = path.read_text()
    if 'id="openThisWeek"' not in html:
        html = html.replace(
            '<div class="map-toolbar">',
            MOUNT + '\n    <div class="map-toolbar">',
            1,
        )

    # Sync hours strings on inline data from data-wineries where names match
    wineries, _, _ = load_datasets()
    by_name = {w["name"].lower(): w.get("hours") or "" for w in wineries}
    # also partial matches used on map
    aliases = {
        "brys estate": "brys estate vineyard & winery",
        "45 north vineyard & winery": "forty-five north vineyard & winery",
        "bel lago vineyard": "bel lago vineyard & winery",
        "willow vineyards": "willow vineyard",
        "gill's pier winery": "gill's pier vineyard & winery",
    }

    def hours_repl(m: re.Match) -> str:
        obj = m.group(0)
        name_m = re.search(r'name:"([^"]+)"', obj)
        if not name_m:
            return obj
        name = name_m.group(1)
        key = name.lower()
        hours = by_name.get(key)
        if hours is None:
            alias = aliases.get(key)
            if alias:
                hours = by_name.get(alias)
        if not hours:
            # fuzzy: startswith
            for kn, hv in by_name.items():
                if kn.startswith(key) or key.startswith(kn):
                    hours = hv
                    break
        if not hours:
            return obj
        return re.sub(r'hours:"[^"]*"', f'hours:"{hours}"', obj, count=1)

    html = re.sub(
        r'\{ name:"[^"]+", type:"[^"]+", peninsula:"[^"]+",[\s\S]*?link:"[^"]+" \}',
        hours_repl,
        html,
    )

    hook = """
<script src="/js/hours.js"></script>
<script src="/js/open-this-week.js" defer></script>
<script>
(function(){
  if (!window.TCWT_HOURS) return;
  var otwDay = TCWT_HOURS.todayDayIndex();
  var otwOnly = false;
  wineries.forEach(function(w){ w._parsed = TCWT_HOURS.parseHours(w.hours || ''); });
  document.addEventListener('tcwt:open-day', function(e){
    otwDay = e.detail.day;
    otwOnly = !!e.detail.onlyOpen;
    if (typeof draw === 'function') draw();
  });
  function otwVisible(w){
    if (!otwOnly) return true;
    return TCWT_HOURS.dayStatus(w._parsed, otwDay) === 'open';
  }
  var _draw = null;
  function install(){
    if (typeof draw !== 'function' || _draw) return;
    _draw = draw;
    draw = function(){
      var savedFilter = activeFilter;
      // peninsula filter stays; open-day filter applied inside by temp swap
      var all = wineries;
      // Monkey-patch filter lists used in original draw via temporary activeFilter + skip closed
      var realDraw = _draw;
      // Rebuild pin section by wrapping geo draws: patch forEach over filtered
      var ctxReady = true;
      // Override wineries.filter temporarily
      var origFilter = Array.prototype.filter;
      var filteringPins = false;
      Array.prototype.filter = function(fn){
        var res = origFilter.call(this, fn);
        // Only adjust the peninsula-filtered winery arrays
        if (this === wineries || (this && this[0] && this[0].peninsula)) {
          if (otwOnly) res = origFilter.call(res, otwVisible);
        }
        return res;
      };
      try { realDraw(); }
      finally { Array.prototype.filter = origFilter; }
      // Dim closed when not only-open: second pass alpha already handled by unfiltered
      if (!otwOnly) {
        // closed wineries in active peninsula drawn as unfiltered (dim) — move them
        // Original draw already dims non-peninsula; leave as-is for simplicity.
      }
    };
    var _getHovered = getHovered;
    getHovered = function(mx, my){
      var w = _getHovered(mx, my);
      if (w && otwOnly && !otwVisible(w)) return null;
      return w;
    };
    var _show = showTooltip;
    showTooltip = function(w, mx, my){
      _show(w, mx, my);
      if (!w || !window.TCWT_HOURS) return;
      var label = TCWT_HOURS.dayHoursLabel(w._parsed, otwDay);
      var st = TCWT_HOURS.dayStatus(w._parsed, otwDay);
      var extra = document.createElement('div');
      extra.className = 'map-tooltip-detail';
      extra.innerHTML = '<strong>' + TCWT_HOURS.DAY_SHORT[otwDay] + ':</strong> ' +
        (st === 'unknown' ? TCWT_HOURS.MISSING_LABEL : label);
      var body = tooltip.querySelector('.map-tooltip-body');
      if (body) body.insertBefore(extra, body.firstChild);
    };
    draw();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function(){ setTimeout(install, 0); });
  else setTimeout(install, 0);
})();
</script>
"""
    if "otwVisible" not in html:
        html = html.replace('<script src="/js/leads.js" defer></script>', hook + '\n<script src="/js/leads.js" defer></script>')
    elif "/js/hours.js" not in html:
        html = ensure_scripts(html)

    # Avoid double-loading open-this-week if ensure_scripts also added
    # Clean duplicate script tags
    # If hook already has hours.js, strip defer duplicates at end
    path.write_text(html)
    print("✓ winery-map.html")


def patch_journals() -> None:
    cta = (
        '<p style="margin:24px 0;padding:16px 20px;border-left:3px solid var(--gold);'
        'background:rgba(201,169,110,0.08);">'
        "<strong>Who is open this week?</strong> "
        'Use our <a href="/wineries/?day=today#open-this-week" class="winery-ref">'
        "Open this week</a> day picker to filter tasting rooms by day — then call ahead; "
        "winter hours change.</p>"
    )
    for rel in [
        "journal/winter-wine-trail.html",
        "journal/traverse-city-wineries-winter-guide.html",
    ]:
        path = ROOT / rel
        html = path.read_text()
        if "open-this-week" in html:
            print(f"· {rel} (already linked)")
            continue
        m = re.search(
            r"(<p>[^<]*(?:winter hours|Calling ahead|call ahead|reduced winter)[^<]*</p>)",
            html,
            re.I,
        )
        if m:
            html = html.replace(m.group(1), m.group(1) + "\n  " + cta, 1)
        else:
            html = html.replace("</h1>", "</h1>\n  " + cta, 1)
        path.write_text(html)
        print(f"✓ {rel}")


def main() -> None:
    wineries, cideries, breweries = load_datasets()
    hours_map = hours_by_slug()

    # Coverage via node parser
    print("Hours strings present:")
    for label, items in [
        ("wineries", wineries),
        ("cideries", cideries),
        ("breweries", breweries),
    ]:
        n = sum(1 for v in items if (v.get("hours") or "").strip())
        print(f"  {label}: {n}/{len(items)}")

    patch_wineries_index(hours_map)
    patch_venue_directory("cideries/index.html", "cideries", cideries)
    patch_venue_directory("breweries/index.html", "breweries", breweries)
    patch_all_wineries(hours_map)
    patch_winery_map()
    patch_journals()
    print("done")


if __name__ == "__main__":
    main()
