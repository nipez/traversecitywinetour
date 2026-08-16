# Traverse City Wine Tour

Michigan wine country guide — wineries, breweries, cideries, and trip-planning pages for Traverse City, Old Mission Peninsula, and Leelanau Peninsula.

This is a **static site**, recovered from the live Cloudflare Pages direct-upload deployment (`tcwinetours`, production domain [traversecitywinetour.com](https://traversecitywinetour.com)). It was not previously on Git, so the published files are the source of truth.

## Run locally

```bash
npx serve .
```

Then open the URL `serve` prints (usually http://localhost:3000).

## Layout

- `index.html` — homepage
- `wineries/` — 37 winery pages (plus index)
- `breweries/` — 16 brewery pages (plus index)
- `cideries/` — 7 cidery pages (plus index)
- `journal/` — 10 wine-country guides (plus index)
- `wine-tours.html`, `plan-your-day.html`, `winery-map.html` — key planning pages
- `logo.svg`, hero/placeholder JPEGs
- `data-wineries.json`, `data-breweries.json`, `data-cideries.json` — listing data
- `generate.py` — static site generator (inline CSS, sized SVGs) that originally built the HTML from winery JSON
- `sitemap.xml`, `sitemap.html`

## generate.py

`generate.py` is a Python static site generator (v2) that reads winery/article JSON and writes HTML pages with fully inlined CSS. Paths inside it still point at the original `/home/claude/site/...` machine; update those before re-running it.

## Cloudflare Pages

- **Project name:** `tcwinetours`
- **Production domain:** https://traversecitywinetour.com
- **Pages.dev:** https://tcwinetours.pages.dev

Direct Upload originally (not Git-connected). Re-deploy from this repo after connecting the project to GitHub if you want Git-based deploys.
