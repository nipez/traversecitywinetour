# Traverse City Wine Tour

Michigan wine country guide — wineries, breweries, cideries, and trip-planning pages for Traverse City, Old Mission Peninsula, and Leelanau Peninsula.

This is a **static site**, recovered from the live Cloudflare Pages direct-upload deployment (`tcwinetours`, production domain [traversecitywinetour.com](https://traversecitywinetour.com)). It was not previously on Git, so the published files are the source of truth.

## Run locally

Static pages only:

```bash
npx serve .
```

Then open the URL `serve` prints (usually http://localhost:3000). Newsletter and lead forms need the Pages Function below.

Lead capture (newsletter, lodging “Get listed”, bachelorette planning kit):

```bash
npm install
cp .dev.vars.example .dev.vars
npm run db:migrate:local
npm run dev
```

`wrangler pages dev` serves the site and `/api/leads`. Open the printed URL, then review submissions at `/admin/leads` with the token from `.dev.vars`.

The production D1 database is `tcwinetour-leads`. After connecting this repo to the `tcwinetours` Pages project, bind that database as `DB` and set:

```bash
npx wrangler pages secret put ADMIN_TOKEN
```

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
- `privacy.html` — privacy policy for form submissions
- `js/leads.js` — shared form client
- `functions/api/leads.js` — Pages Function that writes leads to D1
- `admin/leads.html` — token-gated inbox (not in the sitemap)

## generate.py

`generate.py` is a Python static site generator (v2) that reads winery/article JSON and writes HTML pages with fully inlined CSS. Paths inside it still point at the original `/home/claude/site/...` machine; update those before re-running it.

## Cloudflare Pages

- **Project name:** `tcwinetours`
- **Production domain:** https://traversecitywinetour.com
- **Pages.dev:** https://tcwinetours.pages.dev

Direct Upload originally (not Git-connected). Re-deploy from this repo after connecting the project to GitHub if you want Git-based deploys.

## Search Console & Google Business Profile

These steps cannot be completed from the repo. After a production deploy:

1. In [Google Search Console](https://search.google.com/search-console), verify `https://traversecitywinetour.com` if it is not already.
2. Submit `https://traversecitywinetour.com/sitemap.xml`.
3. Inspect `/wineries/45-north` and confirm it 301s to `/wineries/forty-five-north`.
4. Request indexing for `/events`, `/wine-tours`, `/where-to-stay`, and `/cideries/tandem-ciders` after the content SEO pass ships.
5. In Google Business Profile, keep the public site URL as `https://traversecitywinetour.com` (or the specific landing page you want to rank) and make sure hours/address match the homepage.
6. Do not submit placeholder `#` links or “Coming Soon” pages as the primary listing URL.
