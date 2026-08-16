#!/usr/bin/env python3
"""
Traverse City Wine Tours - Static Site Generator v2
Fixes: inline CSS, sized SVGs, no ad spots, wedding industry ads
"""

import json, os, shutil

with open('/home/claude/site/data/wineries.json', 'r') as f:
    data = json.load(f)

wineries = data['wineries']
articles = data['articles']

OUTPUT_DIR = '/home/claude/site/output'
os.makedirs(f'{OUTPUT_DIR}/wineries', exist_ok=True)
os.makedirs(f'{OUTPUT_DIR}/journal', exist_ok=True)

old_mission = [w for w in wineries if w['peninsula'] == 'Old Mission']
leelanau = [w for w in wineries if w['peninsula'] == 'Leelanau']
featured = [w for w in wineries if w.get('featured')]

# ─── ALL SVGs WITH EXPLICIT width/height ───
ICON_PIN = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5"/></svg>'
ICON_PIN_18 = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5"/></svg>'
ICON_PHONE = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/></svg>'
ICON_PHONE_18 = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/></svg>'
ICON_CLOCK = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>'
ICON_CLOCK_18 = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>'
ICON_GLOBE_18 = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>'
ICON_ARROW = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>'
ICON_WINE = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 2h8l-1 9a5 5 0 01-3 4.5A5 5 0 019 11L8 2z"/><path d="M12 15.5V22"/><path d="M8 22h8"/></svg>'
ICON_STAR = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>'
ICON_CHECK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>'
ICON_CHECK_16 = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>'
ICON_MENU = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h18M3 6h18M3 18h18"/></svg>'

# ─── FULL INLINE CSS ───
FULL_CSS = """
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
:root {
  --burgundy: #4A0E1B; --wine: #722F37; --merlot: #8B3A3A;
  --gold: #C9A96E; --gold-light: #D4BC8B;
  --cream: #F5F0E8; --cream-dark: #EDE6D8;
  --charcoal: #2C2420; --text: #3A3330; --text-light: #7A7068; --white: #FEFCF9;
}
html { scroll-behavior: smooth; }
body { font-family: 'Outfit', sans-serif; color: var(--text); background: var(--white); overflow-x: hidden; }
svg { flex-shrink: 0; }

/* TOP BAR */
.top-bar { background: var(--burgundy); color: var(--gold-light); font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; padding: 8px 0; text-align: center; }

/* NAV */
nav { position: sticky; top: 0; z-index: 100; background: var(--white); border-bottom: 1px solid rgba(74,14,27,0.08); transition: box-shadow 0.3s; }
nav.scrolled { box-shadow: 0 2px 30px rgba(74,14,27,0.08); }
.nav-inner { max-width: 1340px; margin: 0 auto; padding: 0 40px; display: flex; align-items: center; justify-content: space-between; height: 80px; }
.logo { display: flex; flex-direction: column; line-height: 1; text-decoration: none; }
.logo-main { font-family: 'Playfair Display', serif; font-size: 1.55rem; font-weight: 600; color: var(--burgundy); letter-spacing: -0.01em; }
.logo-sub { font-family: 'Outfit', sans-serif; font-size: 0.6rem; letter-spacing: 0.25em; text-transform: uppercase; color: var(--gold); margin-top: 2px; }
.nav-links { display: flex; gap: 36px; list-style: none; align-items: center; }
.nav-links a { text-decoration: none; font-size: 0.82rem; font-weight: 500; letter-spacing: 0.04em; text-transform: uppercase; color: var(--text); position: relative; padding: 4px 0; transition: color 0.3s; }
.nav-links a::after { content: ''; position: absolute; bottom: -2px; left: 0; width: 0; height: 1.5px; background: var(--gold); transition: width 0.3s; }
.nav-links a:hover { color: var(--burgundy); }
.nav-links a:hover::after { width: 100%; }
.nav-cta { background: var(--burgundy) !important; color: var(--cream) !important; padding: 10px 24px !important; border-radius: 4px; font-size: 0.78rem !important; letter-spacing: 0.06em !important; transition: background 0.3s !important; }
.nav-cta:hover { background: var(--wine) !important; }
.nav-cta::after { display: none !important; }
.nav-toggle { display: none; background: none; border: none; cursor: pointer; padding: 8px; }

/* PAGE HERO */
.page-hero { position: relative; height: 45vh; min-height: 360px; display: flex; align-items: center; justify-content: center; text-align: center; overflow: hidden; }
.page-hero-bg { position: absolute; inset: 0; background-size: cover; background-position: center; }
.page-hero-bg::after { content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(74,14,27,0.82) 0%, rgba(44,36,32,0.65) 50%, rgba(74,14,27,0.5) 100%); }
.page-hero-content { position: relative; z-index: 2; max-width: 800px; padding: 0 40px; }
.page-hero-tag { display: inline-flex; align-items: center; gap: 10px; font-size: 0.72rem; letter-spacing: 0.3em; text-transform: uppercase; color: var(--gold-light); margin-bottom: 20px; }
.page-hero-tag::before, .page-hero-tag::after { content: ''; width: 40px; height: 1px; background: var(--gold); }
.page-hero h1 { font-family: 'Playfair Display', serif; font-size: clamp(2.2rem, 5vw, 3.5rem); font-weight: 500; line-height: 1.12; color: var(--cream); }
.page-hero h1 em { font-style: italic; color: var(--gold-light); }
.page-hero-desc { font-family: 'Cormorant Garamond', serif; font-size: 1.2rem; line-height: 1.6; color: rgba(245,240,232,0.8); margin-top: 16px; max-width: 600px; margin-left: auto; margin-right: auto; }

/* BREADCRUMBS */
.breadcrumbs { max-width: 1340px; margin: 0 auto; padding: 20px 40px; }
.breadcrumbs a { font-size: 0.78rem; color: var(--text-light); text-decoration: none; transition: color 0.3s; }
.breadcrumbs a:hover { color: var(--burgundy); }
.breadcrumbs span { font-size: 0.78rem; color: var(--text-light); margin: 0 8px; }
.breadcrumbs .current { font-size: 0.78rem; color: var(--burgundy); font-weight: 500; }

/* SECTION HEADERS */
.section-header { text-align: center; margin-bottom: 60px; }
.section-tag { font-size: 0.7rem; letter-spacing: 0.3em; text-transform: uppercase; color: var(--gold); margin-bottom: 16px; }
.section-title { font-family: 'Playfair Display', serif; font-size: clamp(2rem, 3.5vw, 3rem); font-weight: 500; color: var(--burgundy); line-height: 1.15; }
.section-divider { width: 60px; height: 1.5px; background: var(--gold); margin: 20px auto 0; }

/* BUTTONS */
.btn-primary { display: inline-flex; align-items: center; gap: 8px; background: var(--gold); color: var(--burgundy); padding: 16px 36px; font-family: 'Outfit', sans-serif; font-size: 0.82rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; text-decoration: none; border: none; cursor: pointer; transition: all 0.3s; border-radius: 4px; }
.btn-primary:hover { background: var(--gold-light); transform: translateY(-1px); }
.btn-outline-dark { display: inline-flex; align-items: center; gap: 8px; background: transparent; color: var(--burgundy); padding: 16px 36px; font-family: 'Outfit', sans-serif; font-size: 0.82rem; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; text-decoration: none; border: 1px solid var(--burgundy); cursor: pointer; transition: all 0.3s; border-radius: 4px; }
.btn-outline-dark:hover { background: var(--burgundy); color: var(--cream); }
.btn-burgundy { display: inline-flex; align-items: center; gap: 8px; background: var(--burgundy); color: var(--cream); padding: 16px 36px; font-family: 'Outfit', sans-serif; font-size: 0.82rem; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; text-decoration: none; border-radius: 4px; transition: background 0.3s; }
.btn-burgundy:hover { background: var(--wine); }
.btn-outline { display: inline-flex; align-items: center; gap: 8px; background: transparent; color: var(--cream); padding: 16px 36px; font-family: 'Outfit', sans-serif; font-size: 0.82rem; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; text-decoration: none; border: 1px solid rgba(245,240,232,0.35); cursor: pointer; transition: all 0.3s; }
.btn-outline:hover { border-color: var(--gold); color: var(--gold); }

/* WINERY CARDS */
.winery-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; }
.winery-card { background: var(--white); border-radius: 8px; overflow: hidden; transition: transform 0.3s, box-shadow 0.3s; border: 1px solid rgba(74,14,27,0.06); text-decoration: none; color: inherit; display: block; }
.winery-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(74,14,27,0.1); }
.winery-img { height: 220px; background: var(--cream-dark); position: relative; overflow: hidden; }
.winery-img-inner { width: 100%; height: 100%; background-size: cover; background-position: center; transition: transform 0.5s; }
.winery-card:hover .winery-img-inner { transform: scale(1.05); }
.winery-badge { position: absolute; top: 16px; left: 16px; background: var(--burgundy); color: var(--gold-light); font-size: 0.62rem; letter-spacing: 0.12em; text-transform: uppercase; padding: 5px 12px; border-radius: 3px; z-index: 2; }
.winery-peninsula-tag { position: absolute; top: 16px; right: 16px; background: rgba(255,255,255,0.92); color: var(--burgundy); font-size: 0.62rem; letter-spacing: 0.08em; text-transform: uppercase; padding: 5px 12px; border-radius: 3px; z-index: 2; backdrop-filter: blur(6px); }
.winery-info { padding: 28px; }
.winery-name { font-family: 'Playfair Display', serif; font-size: 1.25rem; font-weight: 600; color: var(--burgundy); margin-bottom: 6px; }
.winery-type { font-size: 0.75rem; color: var(--text-light); letter-spacing: 0.04em; margin-bottom: 16px; }
.winery-details { display: flex; flex-direction: column; gap: 8px; padding-top: 16px; border-top: 1px solid rgba(74,14,27,0.06); }
.winery-detail { display: flex; align-items: center; gap: 10px; font-size: 0.82rem; color: var(--text-light); }
.winery-detail svg { color: var(--gold); }
.winery-link { display: inline-flex; align-items: center; gap: 6px; margin-top: 16px; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--burgundy); text-decoration: none; transition: gap 0.3s; }
.winery-link:hover { gap: 10px; }

/* NEWSLETTER */
.newsletter { background: var(--burgundy); padding: 80px 40px; text-align: center; }
.newsletter-inner { max-width: 600px; margin: 0 auto; }
.newsletter h2 { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 500; color: var(--cream); margin-bottom: 12px; }
.newsletter p { font-family: 'Cormorant Garamond', serif; font-size: 1.15rem; color: rgba(245,240,232,0.7); margin-bottom: 32px; }
.newsletter-form { display: flex; gap: 12px; max-width: 480px; margin: 0 auto; }
.newsletter-form input { flex: 1; padding: 14px 20px; border: 1px solid rgba(201,169,110,0.3); background: rgba(255,255,255,0.06); color: var(--cream); font-family: 'Outfit', sans-serif; font-size: 0.88rem; border-radius: 4px; outline: none; transition: border-color 0.3s; }
.newsletter-form input::placeholder { color: rgba(245,240,232,0.4); }
.newsletter-form input:focus { border-color: var(--gold); }
.newsletter-form button { padding: 14px 28px; background: var(--gold); color: var(--burgundy); font-family: 'Outfit', sans-serif; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; border: none; border-radius: 4px; cursor: pointer; transition: background 0.3s; white-space: nowrap; }
.newsletter-form button:hover { background: var(--gold-light); }

/* FOOTER */
footer { background: var(--charcoal); padding: 80px 40px 40px; color: rgba(245,240,232,0.6); }
.footer-inner { max-width: 1340px; margin: 0 auto; }
.footer-grid { display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr; gap: 60px; margin-bottom: 60px; }
.footer-brand .logo-main { color: var(--cream); font-size: 1.4rem; }
.footer-brand .logo-sub { color: var(--gold); }
.footer-brand p { font-size: 0.88rem; line-height: 1.7; margin-top: 16px; color: rgba(245,240,232,0.5); }
.footer-col h4 { font-size: 0.72rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--gold); margin-bottom: 20px; }
.footer-col ul { list-style: none; }
.footer-col li { margin-bottom: 10px; }
.footer-col a { font-size: 0.88rem; color: rgba(245,240,232,0.5); text-decoration: none; transition: color 0.3s; }
.footer-col a:hover { color: var(--gold-light); }
.footer-bottom { border-top: 1px solid rgba(245,240,232,0.08); padding-top: 32px; display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem; }
.footer-bottom a { color: rgba(245,240,232,0.4); text-decoration: none; transition: color 0.3s; }
.footer-bottom a:hover { color: var(--gold-light); }

/* FILTER */
.filter-btn { padding: 10px 24px; border: 1px solid var(--burgundy); background: transparent; color: var(--burgundy); font-family: 'Outfit', sans-serif; font-size: 0.78rem; font-weight: 500; letter-spacing: 0.06em; text-transform: uppercase; border-radius: 4px; cursor: pointer; transition: all 0.3s; }
.filter-btn.active, .filter-btn:hover { background: var(--burgundy); color: var(--cream); }

/* ANIMATIONS */
@keyframes fadeUp { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: translateY(0); } }

/* RESPONSIVE */
@media (max-width: 1024px) { .winery-grid { grid-template-columns: repeat(2, 1fr); } .footer-grid { grid-template-columns: 1fr 1fr; gap: 40px; } }
@media (max-width: 768px) { .nav-links { display: none; } .nav-toggle { display: block; } .winery-grid { grid-template-columns: 1fr; } .newsletter-form { flex-direction: column; } .footer-grid { grid-template-columns: 1fr; gap: 32px; } .footer-bottom { flex-direction: column; gap: 12px; text-align: center; } .page-hero { height: 35vh; min-height: 280px; } }
"""

# ─── TEMPLATES ───

def head(title, desc, canonical_path="", extra_css=""):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://traversecitywinetours.com{canonical_path}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
{FULL_CSS}
{extra_css}
</style>
</head>
<body>'''

def topbar():
    return '<div class="top-bar">Michigan\'s #1 Wine Destination &nbsp;·&nbsp; 40+ Wineries on Two Peninsulas &nbsp;·&nbsp; Plan Your Visit Today</div>'

def navbar(prefix=""):
    return f'''<nav id="mainNav">
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
</nav>'''

def newsletter_section():
    return '''<section class="newsletter">
  <div class="newsletter-inner">
    <h2>Stay Connected to Wine Country</h2>
    <p>Weekly updates on new wines, events, seasonal guides, and exclusive offers from Traverse City's finest wineries.</p>
    <form class="newsletter-form" onsubmit="return false;"><input type="email" placeholder="Enter your email address"><button type="submit">Subscribe</button></form>
  </div>
</section>'''

def footer_section(prefix=""):
    return f'''<footer>
  <div class="footer-inner">
    <div class="footer-grid">
      <div class="footer-brand">
        <div class="logo"><span class="logo-main">Traverse City Wine</span><span class="logo-sub">Tours & Winery Guide</span></div>
        <p>Your complete guide to exploring Michigan's premier wine region. Discover wineries, plan tours, and experience the best of Traverse City wine country.</p>
      </div>
      <div class="footer-col"><h4>Explore</h4><ul>
        <li><a href="{prefix}wineries/index.html">All Wineries</a></li>
        <li><a href="{prefix}old-mission-peninsula.html">Old Mission Peninsula</a></li>
        <li><a href="{prefix}leelanau-peninsula.html">Leelanau Peninsula</a></li>
        <li><a href="{prefix}journal/index.html">Wine Country Journal</a></li>
        <li><a href="{prefix}events.html">Events Calendar</a></li>
      </ul></div>
      <div class="footer-col"><h4>Plan Your Trip</h4><ul>
        <li><a href="{prefix}wine-tours.html">Wine Tours</a></li>
        <li><a href="{prefix}where-to-stay.html">Hotels & Lodging</a></li>
        <li><a href="{prefix}plan-your-visit.html">Visitor Guide</a></li>
        <li><a href="{prefix}about.html">About Us</a></li>
      </ul></div>
      <div class="footer-col"><h4>Resources</h4><ul>
        <li><a href="{prefix}advertise.html">Advertise With Us</a></li>
        <li><a href="{prefix}contact.html">Contact</a></li>
        <li><a href="{prefix}sitemap.html">Sitemap</a></li>
      </ul></div>
    </div>
    <div class="footer-bottom">
      <span>&copy; 2026 TraverseCityWineTours.com &middot; All Rights Reserved</span>
      <div style="display: flex; gap: 24px;">
        <a href="{prefix}sitemap.html">Sitemap</a>
      </div>
    </div>
  </div>
</footer>'''

def scripts():
    return '''<script>
const nav=document.getElementById('mainNav');
window.addEventListener('scroll',()=>{nav.classList.toggle('scrolled',window.scrollY>10);});
const obs=new IntersectionObserver(e=>{e.forEach(x=>{if(x.isIntersecting){x.target.style.opacity='1';x.target.style.transform='translateY(0)';}});},{threshold:0.1});
document.querySelectorAll('.winery-card,.article-card,.plan-card,.tour-card,.stay-card,.pricing-card,.fade-in,.journal-card,.pen-card').forEach(el=>{el.style.opacity='0';el.style.transform='translateY(20px)';el.style.transition='opacity 0.6s ease, transform 0.6s ease';obs.observe(el);});
</script>'''

def close():
    return '</body></html>'

def winery_card_html(w, show_peninsula=True, img_prefix=""):
    badges = ""
    if w.get('featured'): badges += '<span class="winery-badge">Featured</span>'
    if show_peninsula: badges += f'<span class="winery-peninsula-tag">{w["peninsula"]}</span>'
    img = "vineyard.jpg" if w['peninsula'] == 'Old Mission' else "wine-glasses.jpg"
    filt = f' filter: {w.get("photo_filter","")};' if w.get("photo_filter") else ''
    return f'''<a href="{img_prefix}wineries/{w["slug"]}.html" class="winery-card">
  <div class="winery-img"><div class="winery-img-inner" style="background-image: url('{img_prefix}{img}');{filt}"></div>{badges}</div>
  <div class="winery-info">
    <h3 class="winery-name">{w["name"]}</h3>
    <div class="winery-type">{w["type"]}</div>
    <div class="winery-details">
      <div class="winery-detail">{ICON_PIN} {w["address"].split(",")[0]}</div>
      <div class="winery-detail">{ICON_CLOCK} {w["hours"]}</div>
    </div>
    <span class="winery-link">View Details {ICON_ARROW}</span>
  </div>
</a>'''

# ═══════════════════════════════════════════════
# GENERATE ALL PAGES
# ═══════════════════════════════════════════════

# ── 1. HOMEPAGE ──
home_css = """
.hero { position: relative; height: 92vh; min-height: 650px; display: flex; align-items: center; overflow: hidden; }
.hero-bg { position: absolute; inset: 0; background: url('wine-glasses.jpg') center/cover no-repeat; }
.hero-bg::after { content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(74,14,27,0.82) 0%, rgba(44,36,32,0.65) 50%, rgba(74,14,27,0.45) 100%); }
.hero-content { position: relative; z-index: 2; max-width: 1340px; margin: 0 auto; padding: 0 40px; width: 100%; }
.hero-tag { display: inline-flex; align-items: center; gap: 10px; font-size: 0.72rem; letter-spacing: 0.3em; text-transform: uppercase; color: var(--gold-light); margin-bottom: 28px; opacity:0; animation: fadeUp 0.8s 0.3s forwards; }
.hero-tag::before { content: ''; width: 40px; height: 1px; background: var(--gold); }
.hero h1 { font-family: 'Playfair Display', serif; font-size: clamp(2.8rem, 6vw, 5.2rem); font-weight: 500; line-height: 1.08; color: var(--cream); max-width: 750px; opacity:0; animation: fadeUp 0.8s 0.5s forwards; }
.hero h1 em { font-style: italic; color: var(--gold-light); }
.hero-desc { font-family: 'Cormorant Garamond', serif; font-size: 1.35rem; line-height: 1.6; color: rgba(245,240,232,0.8); max-width: 500px; margin-top: 24px; opacity:0; animation: fadeUp 0.8s 0.7s forwards; }
.hero-actions { display: flex; gap: 16px; margin-top: 40px; opacity:0; animation: fadeUp 0.8s 0.9s forwards; }
.hero-stats { position: absolute; bottom: 60px; right: 40px; z-index: 2; display: flex; gap: 48px; opacity:0; animation: fadeUp 0.8s 1.1s forwards; }
.stat { text-align: center; }
.stat-num { font-family: 'Playfair Display', serif; font-size: 2.4rem; font-weight: 600; color: var(--gold); }
.stat-label { font-size: 0.68rem; letter-spacing: 0.15em; text-transform: uppercase; color: rgba(245,240,232,0.6); margin-top: 4px; }
.pen-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; max-width: 1340px; margin: 0 auto; }
.pen-card { position: relative; border-radius: 8px; overflow: hidden; height: 420px; cursor: pointer; text-decoration: none; display: block; }
.pen-card-bg { position: absolute; inset: 0; background-size: cover; background-position: center; transition: transform 0.6s ease; }
.pen-card:hover .pen-card-bg { transform: scale(1.05); }
.pen-card::after { content: ''; position: absolute; inset: 0; background: linear-gradient(to top, rgba(74,14,27,0.85) 0%, rgba(74,14,27,0.2) 50%, transparent 100%); z-index: 1; }
.pen-card-content { position: absolute; bottom: 0; left: 0; right: 0; padding: 40px; z-index: 2; }
.pen-card-content h3 { font-family: 'Playfair Display', serif; font-size: 1.8rem; font-weight: 500; color: var(--cream); margin-bottom: 8px; }
.pen-card-content p { font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; color: rgba(245,240,232,0.75); line-height: 1.5; margin-bottom: 20px; }
.pen-winery-count { font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--gold-light); }
.journal-grid { display: grid; grid-template-columns: 1.2fr 1fr 1fr; gap: 28px; }
.journal-card { border-radius: 8px; overflow: hidden; text-decoration: none; color: inherit; transition: transform 0.3s; display: block; }
.journal-card:hover { transform: translateY(-3px); }
.journal-card.featured { grid-row: span 2; }
.journal-img { height: 240px; background: var(--cream-dark); position: relative; overflow: hidden; }
.journal-card.featured .journal-img { height: 100%; min-height: 520px; }
.journal-img-inner { width: 100%; height: 100%; background-size: cover; background-position: center; transition: transform 0.5s; }
.journal-card:hover .journal-img-inner { transform: scale(1.04); }
.journal-overlay { position: absolute; inset: 0; background: linear-gradient(to top, rgba(74,14,27,0.85) 0%, transparent 60%); display: flex; flex-direction: column; justify-content: flex-end; padding: 36px; }
.journal-cat { font-size: 0.65rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--gold-light); margin-bottom: 10px; }
.journal-overlay h3 { font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 500; color: var(--cream); line-height: 1.25; margin-bottom: 8px; }
.journal-overlay p { font-family: 'Cormorant Garamond', serif; font-size: 1.05rem; color: rgba(245,240,232,0.7); line-height: 1.5; }
.journal-text { padding: 24px 0; }
.journal-text .journal-cat { color: var(--gold); }
.journal-text h3 { font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 500; color: var(--burgundy); line-height: 1.3; margin-bottom: 8px; }
.journal-text p { font-size: 0.88rem; color: var(--text-light); line-height: 1.55; }
.plan-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; }
.plan-card { background: var(--white); border-radius: 8px; padding: 40px 32px; text-align: center; border: 1px solid rgba(74,14,27,0.06); transition: transform 0.3s, box-shadow 0.3s; }
.plan-card:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(74,14,27,0.08); }
.plan-icon { width: 56px; height: 56px; margin: 0 auto 20px; background: var(--cream); border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.plan-card h3 { font-family: 'Playfair Display', serif; font-size: 1.3rem; font-weight: 500; color: var(--burgundy); margin-bottom: 10px; }
.plan-card p { font-size: 0.88rem; color: var(--text-light); line-height: 1.6; margin-bottom: 20px; }
.plan-card a { font-size: 0.78rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--gold); text-decoration: none; }
.vineyard-banner { position: relative; height: 480px; display: flex; align-items: center; justify-content: center; text-align: center; overflow: hidden; }
.vineyard-banner-bg { position: absolute; inset: 0; background: url('vineyard.jpg') center/cover no-repeat; }
.vineyard-banner-bg::after { content: ''; position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(74,14,27,0.6), rgba(44,36,32,0.7)); }
.vineyard-banner-content { position: relative; z-index: 2; max-width: 700px; padding: 0 40px; }
.vineyard-banner-content h2 { font-family: 'Playfair Display', serif; font-size: clamp(2rem, 3.5vw, 2.8rem); font-weight: 500; color: var(--cream); line-height: 1.2; margin-bottom: 16px; }
.vineyard-banner-content h2 em { color: var(--gold-light); font-style: italic; }
.vineyard-banner-content p { font-family: 'Cormorant Garamond', serif; font-size: 1.25rem; color: rgba(245,240,232,0.8); line-height: 1.6; margin-bottom: 32px; }
@media (max-width: 1024px) { .journal-grid { grid-template-columns: 1fr 1fr; } .journal-card.featured { grid-row: span 1; } .journal-card.featured .journal-img { min-height: 300px; } }
@media (max-width: 768px) { .pen-grid { grid-template-columns: 1fr; } .journal-grid { grid-template-columns: 1fr; } .plan-grid { grid-template-columns: 1fr; } .hero-stats { display: none; } .hero { height: 80vh; } }
"""

featured_cards = "\n".join([winery_card_html(w) for w in featured[:6]])

def article_card_home(a, is_featured=False):
    img = "vineyard.jpg" if a["photo"]=="vineyard" else "wine-glasses.jpg"
    filt = f' filter: {a["filter"]};' if a["filter"] else ''
    if is_featured:
        return f'<a href="journal/{a["slug"]}.html" class="journal-card featured"><div class="journal-img"><div class="journal-img-inner" style="background-image: url(\'{img}\');{filt}"></div><div class="journal-overlay"><div class="journal-cat">{a["category"]}</div><h3>{a["title"]}</h3><p>{a["excerpt"]}</p></div></div></a>'
    return f'<a href="journal/{a["slug"]}.html" class="journal-card"><div class="journal-img"><div class="journal-img-inner" style="background-image: url(\'{img}\');{filt}"></div></div><div class="journal-text"><div class="journal-cat">{a["category"]}</div><h3>{a["title"]}</h3><p>{a["excerpt"]}</p></div></a>'

article_cards_home = article_card_home(articles[0], True) + "\n".join([article_card_home(a) for a in articles[1:4]])

homepage = f"""{head("Traverse City Wine Tours | Explore Michigan's Premier Wine Region", "Discover the finest wineries, vineyards, and wine tours in Traverse City, Michigan. Your complete guide to Old Mission and Leelanau Peninsula wine country.", "/", home_css)}
{topbar()}{navbar()}
<section class="hero">
  <div class="hero-bg"></div>
  <div class="hero-content">
    <div class="hero-tag">Traverse City, Michigan</div>
    <h1>Discover the Heart of <em>Michigan Wine Country</em></h1>
    <p class="hero-desc">Your complete guide to every winery, vineyard, and tasting room across Old Mission and Leelanau Peninsulas.</p>
    <div class="hero-actions"><a href="wineries/index.html" class="btn-primary">Explore Wineries {ICON_ARROW}</a><a href="wine-tours.html" class="btn-outline">Wine Tours</a></div>
  </div>
  <div class="hero-stats">
    <div class="stat"><div class="stat-num">40+</div><div class="stat-label">Wineries</div></div>
    <div class="stat"><div class="stat-num">2</div><div class="stat-label">Peninsulas</div></div>
    <div class="stat"><div class="stat-num">45th</div><div class="stat-label">Parallel</div></div>
  </div>
</section>
<section style="padding: 120px 40px;">
  <div class="section-header"><div class="section-tag">Two World-Class Wine Regions</div><h2 class="section-title">Explore the Peninsulas</h2><div class="section-divider"></div></div>
  <div class="pen-grid">
    <a href="old-mission-peninsula.html" class="pen-card"><div class="pen-card-bg" style="background-image: url('vineyard.jpg')"></div><div class="pen-card-content"><h3>Old Mission Peninsula</h3><p>Nestled along the 45th parallel, this narrow peninsula stretches 18 miles into Grand Traverse Bay with stunning water views and world-class wines.</p><div class="pen-winery-count">{len(old_mission)} Wineries →</div></div></a>
    <a href="leelanau-peninsula.html" class="pen-card"><div class="pen-card-bg" style="background-image: url('wine-glasses.jpg')"></div><div class="pen-card-content"><h3>Leelanau Peninsula</h3><p>Rolling hills, cherry orchards, and over 25 vineyards make this peninsula a wine lover's paradise with diverse varietals and breathtaking scenery.</p><div class="pen-winery-count">{len(leelanau)} Wineries →</div></div></a>
  </div>
</section>
<section style="background: var(--cream); padding: 120px 40px;">
  <div style="max-width: 1340px; margin: 0 auto;"><div class="section-header"><div class="section-tag">Winery Directory</div><h2 class="section-title">Featured Wineries</h2><div class="section-divider"></div></div>
  <div class="winery-grid">{featured_cards}</div>
  <div style="text-align: center; margin-top: 56px;"><a href="wineries/index.html" class="btn-burgundy">View All {len(wineries)} Wineries {ICON_ARROW}</a></div></div>
</section>
<section class="vineyard-banner"><div class="vineyard-banner-bg"></div><div class="vineyard-banner-content"><h2>Experience the Vineyards with a <em>Guided Wine Tour</em></h2><p>Sit back and enjoy the scenery while our partner tour companies take you on an unforgettable journey through Traverse City wine country.</p><a href="wine-tours.html" class="btn-primary">Browse Wine Tours {ICON_ARROW}</a></div></section>
<section style="padding: 120px 40px; max-width: 1340px; margin: 0 auto;">
  <div class="section-header"><div class="section-tag">Wine Country Journal</div><h2 class="section-title">Stories from the Vine</h2><div class="section-divider"></div></div>
  <div class="journal-grid">{article_cards_home}</div>
  <div style="text-align: center; margin-top: 48px;"><a href="journal/index.html" class="btn-outline-dark">Read More Articles {ICON_ARROW}</a></div>
</section>
<section style="background: var(--cream); padding: 100px 40px;">
  <div style="max-width: 1340px; margin: 0 auto;"><div class="section-header"><div class="section-tag">Plan Your Visit</div><h2 class="section-title">Everything You Need</h2><div class="section-divider"></div></div>
  <div class="plan-grid">
    <div class="plan-card"><div class="plan-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="20" height="18" rx="2"/><path d="M2 9h20M9 21V9"/></svg></div><h3>Wine Tours</h3><p>Guided tours with professional drivers covering both peninsulas. Group, private, and custom options.</p><a href="wine-tours.html">Browse Tour Companies →</a></div>
    <div class="plan-card"><div class="plan-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 21h18M5 21V7l8-4 8 4v14"/><path d="M9 21v-4h4v4"/></svg></div><h3>Where to Stay</h3><p>From luxury resorts to charming B&Bs, find the perfect home base for your wine country getaway.</p><a href="where-to-stay.html">View Accommodations →</a></div>
    <div class="plan-card"><div class="plan-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg></div><h3>Events Calendar</h3><p>Wine festivals, harvest celebrations, live music at the vineyards, and seasonal tastings year-round.</p><a href="events.html">See Upcoming Events →</a></div>
  </div></div>
</section>
{newsletter_section()}{footer_section()}{scripts()}{close()}"""

with open(f'{OUTPUT_DIR}/index.html', 'w') as f: f.write(homepage)
print("✓ index.html")


# ── 2. WINERY DIRECTORY ──
all_cards = "\n".join([winery_card_html(w, img_prefix="../").replace('class="winery-card"', f'class="winery-card" data-peninsula="{w["peninsula"]}"') for w in wineries])

directory = f"""{head("All Wineries | Traverse City Wine Tours", "Complete directory of every winery in Traverse City. Find addresses, hours, phone numbers for all wineries on Old Mission and Leelanau Peninsulas.", "/wineries/")}
{topbar()}{navbar("../")}
<section class="page-hero"><div class="page-hero-bg" style="background-image: url('../vineyard.jpg');"></div><div class="page-hero-content"><div class="page-hero-tag">{len(wineries)} Wineries</div><h1>Traverse City <em>Wineries</em></h1><p class="page-hero-desc">Explore every winery, vineyard, and tasting room across both peninsulas.</p></div></section>
<div class="breadcrumbs"><a href="../index.html">Home</a><span>›</span><span class="current">All Wineries</span></div>
<section style="padding: 60px 40px 120px; max-width: 1340px; margin: 0 auto;">
  <div style="display: flex; gap: 12px; justify-content: center; margin-bottom: 48px; flex-wrap: wrap;">
    <button class="filter-btn active" onclick="filterW('all',this)">All ({len(wineries)})</button>
    <button class="filter-btn" onclick="filterW('Old Mission',this)">Old Mission ({len(old_mission)})</button>
    <button class="filter-btn" onclick="filterW('Leelanau',this)">Leelanau ({len(leelanau)})</button>
  </div>
  <div class="winery-grid">{all_cards}</div>
</section>
{newsletter_section()}{footer_section("../")}{scripts()}
<script>function filterW(p,btn){{document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');document.querySelectorAll('.winery-card').forEach(c=>{{c.style.display=(p==='all'||c.dataset.peninsula===p)?'':'none';}});}}</script>
{close()}"""

with open(f'{OUTPUT_DIR}/wineries/index.html', 'w') as f: f.write(directory)
print("✓ wineries/index.html")


# ── 3. INDIVIDUAL WINERY PAGES ──
winery_css = """
.winery-hero { position: relative; height: 50vh; min-height: 400px; display: flex; align-items: flex-end; overflow: hidden; }
.winery-hero-bg { position: absolute; inset: 0; background-size: cover; background-position: center; }
.winery-hero-bg::after { content: ''; position: absolute; inset: 0; background: linear-gradient(to top, rgba(74,14,27,0.9) 0%, rgba(74,14,27,0.3) 40%, transparent 70%); }
.winery-hero-content { position: relative; z-index: 2; max-width: 1340px; margin: 0 auto; padding: 60px 40px; width: 100%; }
.winery-peninsula-label { display: inline-flex; align-items: center; gap: 8px; font-size: 0.7rem; letter-spacing: 0.25em; text-transform: uppercase; color: var(--gold-light); margin-bottom: 16px; }
.winery-hero-content h1 { font-family: 'Playfair Display', serif; font-size: clamp(2.2rem, 5vw, 3.8rem); font-weight: 500; color: var(--cream); line-height: 1.1; }
.winery-hero-type { font-family: 'Cormorant Garamond', serif; font-size: 1.2rem; color: rgba(245,240,232,0.7); margin-top: 8px; }
.winery-body { max-width: 1340px; margin: 0 auto; padding: 60px 40px; display: grid; grid-template-columns: 2fr 1fr; gap: 60px; }
.winery-main h2 { font-family: 'Playfair Display', serif; font-size: 1.8rem; font-weight: 500; color: var(--burgundy); margin-bottom: 20px; }
.winery-main p { font-size: 1rem; line-height: 1.8; color: var(--text); margin-bottom: 20px; }
.winery-known-for { margin-top: 40px; padding-top: 40px; border-top: 1px solid rgba(74,14,27,0.08); }
.winery-known-for h3, .winery-amenities h3 { font-family: 'Playfair Display', serif; font-size: 1.3rem; font-weight: 500; color: var(--burgundy); margin-bottom: 16px; }
.wine-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.wine-tag { padding: 8px 16px; background: var(--cream); border-radius: 20px; font-size: 0.82rem; color: var(--burgundy); font-weight: 500; }
.winery-amenities { margin-top: 32px; }
.amenity-list { display: flex; flex-direction: column; gap: 10px; }
.amenity-item { display: flex; align-items: center; gap: 10px; font-size: 0.92rem; color: var(--text); }
.amenity-item svg { color: var(--gold); }
.winery-sidebar { position: sticky; top: 120px; align-self: start; }
.sidebar-card { background: var(--cream); border-radius: 8px; padding: 32px; margin-bottom: 24px; }
.sidebar-card h3 { font-family: 'Playfair Display', serif; font-size: 1.15rem; font-weight: 600; color: var(--burgundy); margin-bottom: 20px; }
.sidebar-detail { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 16px; font-size: 0.9rem; color: var(--text); line-height: 1.5; }
.sidebar-detail svg { color: var(--gold); margin-top: 2px; }
.sidebar-detail a { color: var(--burgundy); text-decoration: none; font-weight: 500; }
.sidebar-detail a:hover { text-decoration: underline; }
.sidebar-cta { display: block; width: 100%; text-align: center; padding: 14px; background: var(--burgundy); color: var(--cream); font-family: 'Outfit', sans-serif; font-size: 0.82rem; font-weight: 500; letter-spacing: 0.06em; text-transform: uppercase; text-decoration: none; border-radius: 4px; transition: background 0.3s; margin-top: 24px; }
.sidebar-cta:hover { background: var(--wine); }
.related-wineries { padding: 80px 40px; background: var(--cream); }
.related-inner { max-width: 1340px; margin: 0 auto; }
@media (max-width: 1024px) { .winery-body { grid-template-columns: 1fr; } .winery-sidebar { position: static; } }
"""

for w in wineries:
    img = "vineyard.jpg" if w['peninsula'] == 'Old Mission' else "wine-glasses.jpg"
    filt = f' filter: {w.get("photo_filter","")};' if w.get("photo_filter") else ''
    wine_tags = "".join([f'<span class="wine-tag">{v}</span>' for v in w.get('known_for', [])])
    amenities = "".join([f'<div class="amenity-item">{ICON_CHECK} {a}</div>' for a in w.get('amenities', [])])
    long_desc = w.get('long_description', w['description'])
    paragraphs = "".join([f'<p>{p.strip()}</p>' for p in long_desc.split('\n') if p.strip()])
    same_pen = [x for x in wineries if x['peninsula'] == w['peninsula'] and x['slug'] != w['slug']][:3]
    related_cards = "\n".join([winery_card_html(x, show_peninsula=False, img_prefix="../") for x in same_pen])
    pen_link = "../old-mission-peninsula.html" if w['peninsula'] == 'Old Mission' else "../leelanau-peninsula.html"

    schema = f'''<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Winery","name":"{w['name']}","description":"{w['description'][:200].replace('"','')}","address":{{"@type":"PostalAddress","streetAddress":"{w['address'].split(',')[0]}","addressLocality":"Traverse City","addressRegion":"MI","addressCountry":"US"}},"telephone":"{w['phone']}","url":"{w['website']}"}}</script>'''

    page = f"""{head(f"{w['name']} | Traverse City Winery Guide", w['description'][:155], f"/wineries/{w['slug']}.html", winery_css)}
{schema}
{topbar()}{navbar("../")}
<section class="winery-hero"><div class="winery-hero-bg" style="background-image: url('../{img}');{filt}"></div>
  <div class="winery-hero-content"><div class="winery-peninsula-label">{ICON_PIN} {w['peninsula']} Peninsula</div><h1>{w['name']}</h1><div class="winery-hero-type">{w['type']}</div></div>
</section>
<div class="breadcrumbs"><a href="../index.html">Home</a><span>›</span><a href="index.html">Wineries</a><span>›</span><a href="{pen_link}">{w['peninsula']}</a><span>›</span><span class="current">{w['name']}</span></div>
<div class="winery-body">
  <div class="winery-main">
    <h2>About {w['name']}</h2>{paragraphs}
    <div class="winery-known-for"><h3>Known For</h3><div class="wine-tags">{wine_tags}</div></div>
    <div class="winery-amenities"><h3>Amenities & Features</h3><div class="amenity-list">{amenities}</div></div>
  </div>
  <div class="winery-sidebar">
    <div class="sidebar-card">
      <h3>Visit Information</h3>
      <div class="sidebar-detail">{ICON_PIN_18} <div>{w['address']}</div></div>
      <div class="sidebar-detail">{ICON_PHONE_18} <div>{w['phone']}</div></div>
      <div class="sidebar-detail">{ICON_CLOCK_18} <div>{w['hours']}</div></div>
      <div class="sidebar-detail">{ICON_GLOBE_18} <div><a href="{w['website']}" target="_blank" rel="noopener">{w['website'].replace('https://www.','').replace('https://','')}</a></div></div>
      <a href="{w['website']}" target="_blank" rel="noopener" class="sidebar-cta">Visit Official Website</a>
    </div>
    <div class="sidebar-card">
      <h3>Plan Your Visit</h3>
      <p style="font-size: 0.88rem; color: var(--text-light); line-height: 1.6; margin-bottom: 16px;">Need a ride? Browse our partner wine tour companies for guided visits to {w['name']} and nearby wineries.</p>
      <a href="../wine-tours.html" class="sidebar-cta" style="background: var(--gold); color: var(--burgundy);">Browse Wine Tours</a>
    </div>
  </div>
</div>
<section class="related-wineries"><div class="related-inner"><div class="section-header"><div class="section-tag">More on {w['peninsula']} Peninsula</div><h2 class="section-title">Nearby Wineries</h2><div class="section-divider"></div></div><div class="winery-grid">{related_cards}</div></div></section>
{newsletter_section()}{footer_section("../")}{scripts()}{close()}"""

    with open(f'{OUTPUT_DIR}/wineries/{w["slug"]}.html', 'w') as f: f.write(page)
    print(f'  ✓ wineries/{w["slug"]}.html')

print(f"✓ {len(wineries)} winery pages")


# ── 4. PENINSULA PAGES ──
def peninsula_page(name, slug, wlist, desc, hero_img):
    cards = "\n".join([winery_card_html(w, show_peninsula=False) for w in wlist])
    return f"""{head(f"{name} Wineries | Traverse City Wine Tours", f"Explore all {len(wlist)} wineries on {name}. Complete guide with addresses, hours, and tasting room details.", f"/{slug}.html")}
{topbar()}{navbar()}
<section class="page-hero"><div class="page-hero-bg" style="background-image: url('{hero_img}');"></div><div class="page-hero-content"><div class="page-hero-tag">{len(wlist)} Wineries</div><h1><em>{name}</em> Wineries</h1><p class="page-hero-desc">{desc[:120]}...</p></div></section>
<div class="breadcrumbs"><a href="index.html">Home</a><span>›</span><a href="wineries/index.html">Wineries</a><span>›</span><span class="current">{name}</span></div>
<section style="padding: 60px 40px 120px; max-width: 1340px; margin: 0 auto;">
  <div style="max-width: 800px; margin: 0 auto 60px; text-align: center;"><p style="font-family: 'Cormorant Garamond', serif; font-size: 1.2rem; line-height: 1.7; color: var(--text-light);">{desc}</p></div>
  <div class="winery-grid">{cards}</div>
</section>
{newsletter_section()}{footer_section()}{scripts()}{close()}"""

with open(f'{OUTPUT_DIR}/old-mission-peninsula.html', 'w') as f:
    f.write(peninsula_page("Old Mission Peninsula", "old-mission-peninsula", old_mission,
        "Stretching 18 miles into Grand Traverse Bay along the 45th parallel, Old Mission Peninsula is home to some of Michigan's most celebrated wineries. The narrow landmass benefits from the moderating influence of the surrounding water, creating a microclimate ideal for cool-climate grape varieties like Riesling, Pinot Grigio, and Chardonnay.", "vineyard.jpg"))
print("✓ old-mission-peninsula.html")

with open(f'{OUTPUT_DIR}/leelanau-peninsula.html', 'w') as f:
    f.write(peninsula_page("Leelanau Peninsula", "leelanau-peninsula", leelanau,
        "The Leelanau Peninsula wine trail winds through rolling hills, cherry orchards, and charming villages on Michigan's western coast. With diverse terroir influenced by Lake Michigan and inland lakes, the peninsula produces an impressive range of wines — from crisp whites and elegant sparklings to bold reds and celebrated ice wines.", "wine-glasses.jpg"))
print("✓ leelanau-peninsula.html")


# ── 5. WINE TOURS ──
tours_css = """
.tour-card { background: var(--white); border-radius: 8px; padding: 36px; border: 1px solid rgba(74,14,27,0.06); transition: transform 0.3s, box-shadow 0.3s; }
.tour-card:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(74,14,27,0.08); }
.tour-card h3 { font-family: 'Playfair Display', serif; font-size: 1.4rem; font-weight: 500; color: var(--burgundy); margin-bottom: 8px; }
.tour-type { font-size: 0.72rem; letter-spacing: 0.15em; text-transform: uppercase; color: var(--gold); margin-bottom: 16px; }
.tour-card p { font-size: 0.92rem; color: var(--text-light); line-height: 1.65; margin-bottom: 20px; }
.tour-features { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
.tour-feature { padding: 6px 14px; background: var(--cream); border-radius: 16px; font-size: 0.78rem; color: var(--text); }
"""
tours = [
    ("Traverse City Wine Tours Co.", "Premium Tour Service", "Full-service guided wine tours covering both Old Mission and Leelanau Peninsulas. Luxury vehicles, knowledgeable guides, and customizable itineraries.", ["Private Tours", "Group Tours", "Custom Routes", "Luxury Vehicles"]),
    ("TC Wine Bus", "Shuttle Service", "Hop-on, hop-off wine trail shuttle service operating daily routes along both peninsulas. Perfect for visitors who want flexibility.", ["Daily Routes", "Hop-On Hop-Off", "Affordable", "Both Peninsulas"]),
    ("Northern Michigan Wine Tours", "Guided Experiences", "Boutique wine tour company specializing in small-group experiences with sommelier-led tastings and behind-the-scenes winery access.", ["Small Groups", "Sommelier Guides", "VIP Access", "Food Pairings"]),
    ("Grand Traverse Limo", "Luxury Private Tours", "Private limousine and luxury SUV wine tours for couples, bridal parties, and special occasions. White-glove service.", ["Private Limo", "Special Occasions", "Bridal Parties", "Champagne Service"]),
]
tc = ""
for t in tours:
    feats = "".join([f'<span class="tour-feature">{f}</span>' for f in t[3]])
    tc += f'<div class="tour-card"><h3>{t[0]}</h3><div class="tour-type">{t[1]}</div><p>{t[2]}</p><div class="tour-features">{feats}</div><a href="#" class="btn-primary" style="font-size:0.75rem;padding:12px 24px;">Learn More {ICON_ARROW}</a></div>\n'

with open(f'{OUTPUT_DIR}/wine-tours.html', 'w') as f:
    f.write(f"""{head("Wine Tours | Traverse City Wine Tours", "Book a guided wine tour in Traverse City. Luxury private tours, group shuttles, and custom wine trail experiences.", "/wine-tours.html", tours_css)}
{topbar()}{navbar()}
<section class="page-hero"><div class="page-hero-bg" style="background-image: url('wine-glasses.jpg');"></div><div class="page-hero-content"><div class="page-hero-tag">Guided Experiences</div><h1>Traverse City <em>Wine Tours</em></h1><p class="page-hero-desc">Sit back, relax, and let someone else drive. Explore both peninsulas with our trusted tour partners.</p></div></section>
<div class="breadcrumbs"><a href="index.html">Home</a><span>›</span><span class="current">Wine Tours</span></div>
<section style="padding: 60px 40px 80px; max-width: 1000px; margin: 0 auto; display: flex; flex-direction: column; gap: 28px;">{tc}</section>
{newsletter_section()}{footer_section()}{scripts()}{close()}""")
print("✓ wine-tours.html")


# ── 6. WHERE TO STAY ──
stay_css = """
.stay-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; }
.stay-card { background: var(--white); border-radius: 8px; overflow: hidden; border: 1px solid rgba(74,14,27,0.06); transition: transform 0.3s, box-shadow 0.3s; }
.stay-card:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(74,14,27,0.08); }
.stay-img { height: 200px; background: var(--cream-dark); display: flex; align-items: center; justify-content: center; }
.stay-img span { font-family: 'Playfair Display', serif; font-size: 1.4rem; color: var(--text-light); opacity: 0.4; }
.stay-info { padding: 28px; }
.stay-info h3 { font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 500; color: var(--burgundy); margin-bottom: 4px; }
.stay-type { font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--gold); margin-bottom: 12px; }
.stay-info p { font-size: 0.88rem; color: var(--text-light); line-height: 1.6; margin-bottom: 16px; }
@media (max-width: 1024px) { .stay-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .stay-grid { grid-template-columns: 1fr; } }
"""
accom = [("Grand Traverse Resort and Spa","Luxury Resort","Full-service resort with golf, spa, and dining. Central location with easy access to both wine trails."),("Chateau Chantal B&B","Winery Inn","Sleep among the vines at this European-inspired estate with breathtaking bay views from every room."),("Black Star Farms Inn","Farm Stay & Inn","Luxury B&B on a working agricultural estate. Wake up to vineyard views and artisan breakfast."),("Park Place Hotel","Downtown Hotel","Historic hotel in the heart of downtown Traverse City. Walking distance to restaurants and shops."),("Cherry Tree Inn & Suites","Boutique Hotel","Charming boutique accommodations with a warm, welcoming atmosphere near the bay."),("Cambria Hotel","Modern Hotel","Contemporary hotel with rooftop bar, downtown location, and modern amenities.")]
sc = "".join([f'<div class="stay-card"><div class="stay-img"><span>Photo</span></div><div class="stay-info"><h3>{s[0]}</h3><div class="stay-type">{s[1]}</div><p>{s[2]}</p><span class="winery-link">View Details {ICON_ARROW}</span></div></div>' for s in accom])

with open(f'{OUTPUT_DIR}/where-to-stay.html', 'w') as f:
    f.write(f"""{head("Where to Stay | Traverse City Wine Tours", "Find the best hotels, inns, and B&Bs for your Traverse City wine country getaway.", "/where-to-stay.html", stay_css)}
{topbar()}{navbar()}
<section class="page-hero"><div class="page-hero-bg" style="background-image: url('vineyard.jpg');"></div><div class="page-hero-content"><div class="page-hero-tag">Accommodations</div><h1>Where to <em>Stay</em></h1><p class="page-hero-desc">From luxury resorts to charming B&Bs in the vineyards — find your perfect wine country home base.</p></div></section>
<div class="breadcrumbs"><a href="index.html">Home</a><span>›</span><span class="current">Where to Stay</span></div>
<section style="padding: 60px 40px 80px; max-width: 1340px; margin: 0 auto;"><div class="stay-grid">{sc}</div></section>
{newsletter_section()}{footer_section()}{scripts()}{close()}""")
print("✓ where-to-stay.html")


# ── 7. JOURNAL INDEX ──
jcss = """
.journal-list { display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; }
.article-card { border-radius: 8px; overflow: hidden; text-decoration: none; color: inherit; transition: transform 0.3s; display: block; }
.article-card:hover { transform: translateY(-3px); }
.article-img { height: 220px; background: var(--cream-dark); position: relative; overflow: hidden; }
.article-img-inner { width: 100%; height: 100%; background-size: cover; background-position: center; transition: transform 0.5s; }
.article-card:hover .article-img-inner { transform: scale(1.04); }
.article-text { padding: 24px 0; }
.article-cat { font-size: 0.65rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--gold); margin-bottom: 10px; }
.article-text h3 { font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 500; color: var(--burgundy); line-height: 1.3; margin-bottom: 8px; }
.article-text p { font-size: 0.88rem; color: var(--text-light); line-height: 1.55; }
@media (max-width: 1024px) { .journal-list { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .journal-list { grid-template-columns: 1fr; } }
"""
acards = ""
for a in articles:
    img = "vineyard.jpg" if a["photo"]=="vineyard" else "wine-glasses.jpg"
    filt = f' filter: {a["filter"]};' if a["filter"] else ''
    acards += f'<a href="{a["slug"]}.html" class="article-card"><div class="article-img"><div class="article-img-inner" style="background-image: url(\'../{img}\');{filt}"></div></div><div class="article-text"><div class="article-cat">{a["category"]}</div><h3>{a["title"]}</h3><p>{a["excerpt"]}</p></div></a>\n'

with open(f'{OUTPUT_DIR}/journal/index.html', 'w') as f:
    f.write(f"""{head("Wine Country Journal | Traverse City Wine Tours", "Stories, guides, and insights from Traverse City wine country.", "/journal/", jcss)}
{topbar()}{navbar("../")}
<section class="page-hero"><div class="page-hero-bg" style="background-image: url('../wine-glasses.jpg');"></div><div class="page-hero-content"><div class="page-hero-tag">Stories & Guides</div><h1>Wine Country <em>Journal</em></h1><p class="page-hero-desc">Winery spotlights, seasonal guides, varietal deep-dives, and the latest from Traverse City wine country.</p></div></section>
<div class="breadcrumbs"><a href="../index.html">Home</a><span>›</span><span class="current">Journal</span></div>
<section style="padding: 60px 40px 80px; max-width: 1340px; margin: 0 auto;"><div class="journal-list">{acards}</div></section>
{newsletter_section()}{footer_section("../")}{scripts()}{close()}""")
print("✓ journal/index.html")


# ── 8. REMAINING PAGES ──
# Plan Your Visit
with open(f'{OUTPUT_DIR}/plan-your-visit.html', 'w') as f:
    f.write(f"""{head("Plan Your Visit | Traverse City Wine Tours", "Everything you need to plan your Traverse City wine country trip.", "/plan-your-visit.html")}
{topbar()}{navbar()}
<section class="page-hero"><div class="page-hero-bg" style="background-image: url('vineyard.jpg');"></div><div class="page-hero-content"><div class="page-hero-tag">Visitor Guide</div><h1>Plan Your <em>Wine Country Visit</em></h1></div></section>
<div class="breadcrumbs"><a href="index.html">Home</a><span>›</span><span class="current">Plan Your Visit</span></div>
<section style="padding: 80px 40px; max-width: 900px; margin: 0 auto;">
  <h2 style="font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 500; color: var(--burgundy); margin-bottom: 24px;">Welcome to Traverse City Wine Country</h2>
  <p style="font-size: 1rem; line-height: 1.8; color: var(--text); margin-bottom: 20px;">Traverse City sits on the 45th parallel — the same latitude as Bordeaux, Burgundy, and the Willamette Valley — making it one of the premier wine regions in the United States. With over 40 wineries spread across two stunning peninsulas, there's a wine experience here for every palate.</p>
  <p style="font-size: 1rem; line-height: 1.8; color: var(--text); margin-bottom: 20px;">Whether you're a first-time visitor or a seasoned wine enthusiast, this guide will help you plan the perfect trip.</p>
  <h3 style="font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 500; color: var(--burgundy); margin: 48px 0 20px;">Getting Here</h3>
  <p style="font-size: 1rem; line-height: 1.8; color: var(--text); margin-bottom: 20px;">Traverse City is served by Cherry Capital Airport (TVC) with direct flights from major Midwest hubs. The city is approximately a 4-hour drive from Detroit, 5 hours from Chicago, and 3.5 hours from Grand Rapids.</p>
  <h3 style="font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 500; color: var(--burgundy); margin: 48px 0 20px;">Best Time to Visit</h3>
  <p style="font-size: 1rem; line-height: 1.8; color: var(--text); margin-bottom: 20px;">Wine tasting is a year-round activity. Summer (June–August) offers the best weather and most events. Fall (September–October) brings harvest season, stunning foliage, and fewer crowds.</p>
  <h3 style="font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 500; color: var(--burgundy); margin: 48px 0 20px;">Quick Links</h3>
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 20px;">
    <a href="wineries/index.html" style="display: flex; align-items: center; gap: 12px; padding: 20px; background: var(--cream); border-radius: 8px; text-decoration: none; color: var(--burgundy); font-weight: 500;">{ICON_WINE} All Wineries</a>
    <a href="wine-tours.html" style="display: flex; align-items: center; gap: 12px; padding: 20px; background: var(--cream); border-radius: 8px; text-decoration: none; color: var(--burgundy); font-weight: 500;">{ICON_PIN} Wine Tours</a>
    <a href="where-to-stay.html" style="display: flex; align-items: center; gap: 12px; padding: 20px; background: var(--cream); border-radius: 8px; text-decoration: none; color: var(--burgundy); font-weight: 500;">{ICON_STAR} Where to Stay</a>
    <a href="events.html" style="display: flex; align-items: center; gap: 12px; padding: 20px; background: var(--cream); border-radius: 8px; text-decoration: none; color: var(--burgundy); font-weight: 500;">{ICON_CLOCK} Events Calendar</a>
  </div>
</section>
{newsletter_section()}{footer_section()}{scripts()}{close()}""")
print("✓ plan-your-visit.html")

# Events
with open(f'{OUTPUT_DIR}/events.html', 'w') as f:
    events_list = [("May","Blossom Days Wine Trail","Celebrate spring with special tastings and vineyard tours as cherry blossoms bloom."),("July","Traverse City Cherry Festival","The region's biggest annual celebration features cherry-inspired wines, food, and festivities."),("September–October","Harvest Season","Watch the grapes come in, join harvest celebrations, and taste the year's first wines."),("November","Wine & Food Festival","Indulge in food and wine pairings featuring the region's best chefs and winemakers.")]
    ev = "".join([f'<div style="padding: 24px; background: var(--cream); border-radius: 8px; border-left: 3px solid var(--gold);"><div style="font-size: 0.68rem; letter-spacing: 0.15em; text-transform: uppercase; color: var(--gold); margin-bottom: 6px;">{e[0]}</div><h4 style="font-family: \'Playfair Display\', serif; font-size: 1.1rem; color: var(--burgundy); margin-bottom: 4px;">{e[1]}</h4><p style="font-size: 0.88rem; color: var(--text-light);">{e[2]}</p></div>' for e in events_list])
    f.write(f"""{head("Events Calendar | Traverse City Wine Tours", "Upcoming wine events, festivals, and tastings in Traverse City.", "/events.html")}
{topbar()}{navbar()}
<section class="page-hero"><div class="page-hero-bg" style="background-image: url('wine-glasses.jpg');"></div><div class="page-hero-content"><div class="page-hero-tag">What's Happening</div><h1>Events <em>Calendar</em></h1></div></section>
<div class="breadcrumbs"><a href="index.html">Home</a><span>›</span><span class="current">Events</span></div>
<section style="padding: 60px 40px 80px; max-width: 900px; margin: 0 auto;">
  <div style="padding: 60px; background: var(--cream); border-radius: 12px; text-align: center; margin-bottom: 60px;"><h3 style="font-family: 'Playfair Display', serif; font-size: 1.5rem; color: var(--burgundy); margin-bottom: 12px;">Events Coming Soon</h3><p style="font-size: 0.95rem; color: var(--text-light); line-height: 1.6; margin-bottom: 24px;">We're building a comprehensive events calendar. Subscribe to our newsletter to be the first to know.</p><a href="#" class="btn-primary">Subscribe for Updates {ICON_ARROW}</a></div>
  <h3 style="font-family: 'Playfair Display', serif; font-size: 1.5rem; color: var(--burgundy); margin-bottom: 24px;">Annual Highlights</h3>
  <div style="display: flex; flex-direction: column; gap: 16px;">{ev}</div>
</section>
{newsletter_section()}{footer_section()}{scripts()}{close()}""")
print("✓ events.html")

# About
with open(f'{OUTPUT_DIR}/about.html', 'w') as f:
    f.write(f"""{head("About | Traverse City Wine Tours", "About TraverseCityWineTours.com — your comprehensive guide to Traverse City wine country.", "/about.html")}
{topbar()}{navbar()}
<section class="page-hero" style="height: 35vh; min-height: 280px;"><div class="page-hero-bg" style="background-image: url('vineyard.jpg');"></div><div class="page-hero-content"><div class="page-hero-tag">Our Story</div><h1>About <em>Us</em></h1></div></section>
<div class="breadcrumbs"><a href="index.html">Home</a><span>›</span><span class="current">About</span></div>
<section style="padding: 60px 40px 100px; max-width: 800px; margin: 0 auto;">
  <h2 style="font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 500; color: var(--burgundy); margin-bottom: 24px;">Your Guide to Traverse City Wine Country</h2>
  <p style="font-size: 1rem; line-height: 1.8; color: var(--text); margin-bottom: 20px;">TraverseCityWineTours.com is the most comprehensive online guide to the wineries, vineyards, and wine experiences of Traverse City, Michigan. We're passionate about this region and dedicated to helping visitors and locals alike discover everything wine country has to offer.</p>
  <p style="font-size: 1rem; line-height: 1.8; color: var(--text); margin-bottom: 20px;">Our directory features every winery across both Old Mission and Leelanau Peninsulas, with detailed information including hours, contact details, wine specialties, and what makes each estate unique.</p>
  <h3 style="font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 500; color: var(--burgundy); margin: 48px 0 20px;">Get in Touch</h3>
  <p style="font-size: 1rem; line-height: 1.8; color: var(--text);">Email: <a href="mailto:hello@traversecitywinetours.com" style="color: var(--burgundy); font-weight: 500;">hello@traversecitywinetours.com</a></p>
  <p style="font-size: 1rem; line-height: 1.8; color: var(--text);">Advertising: <a href="advertise.html" style="color: var(--burgundy); font-weight: 500;">Learn about advertising opportunities</a></p>
</section>
{newsletter_section()}{footer_section()}{scripts()}{close()}""")
print("✓ about.html")

# ADVERTISE — with wedding planners + event industry
adv_css = """
.pricing-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; margin: 48px 0; }
.pricing-card { background: var(--white); border: 1px solid rgba(74,14,27,0.08); border-radius: 8px; padding: 36px; text-align: center; transition: transform 0.3s, box-shadow 0.3s; }
.pricing-card:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(74,14,27,0.08); }
.pricing-card.highlight { border-color: var(--gold); background: linear-gradient(to bottom, rgba(201,169,110,0.06), var(--white)); }
.pricing-label { font-size: 0.68rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--gold); margin-bottom: 12px; }
.pricing-card h3 { font-family: 'Playfair Display', serif; font-size: 1.4rem; color: var(--burgundy); margin-bottom: 8px; }
.pricing-card > p { font-size: 0.88rem; color: var(--text-light); line-height: 1.6; margin-bottom: 20px; }
.pricing-features { text-align: left; margin-bottom: 24px; }
.pricing-feature { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; color: var(--text); padding: 6px 0; }
.pricing-feature svg { color: var(--gold); }
@media (max-width: 768px) { .pricing-grid { grid-template-columns: 1fr; } }
"""

with open(f'{OUTPUT_DIR}/advertise.html', 'w') as f:
    f.write(f"""{head("Advertise With Us | Traverse City Wine Tours", "Reach wine enthusiasts planning their Traverse City visits. Advertising for tour companies, hotels, restaurants, wedding planners, and local businesses.", "/advertise.html", adv_css)}
{topbar()}{navbar()}
<section class="page-hero" style="height: 35vh; min-height: 280px;"><div class="page-hero-bg" style="background-image: url('wine-glasses.jpg');"></div><div class="page-hero-content"><div class="page-hero-tag">Partner With Us</div><h1>Advertise on <em>TC Wine Tours</em></h1></div></section>
<div class="breadcrumbs"><a href="index.html">Home</a><span>›</span><span class="current">Advertise</span></div>
<section style="padding: 60px 40px 100px; max-width: 1100px; margin: 0 auto;">
  <div style="max-width: 700px; margin: 0 auto 48px; text-align: center;">
    <h2 style="font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 500; color: var(--burgundy); margin-bottom: 16px;">Reach Wine Country Visitors</h2>
    <p style="font-family: 'Cormorant Garamond', serif; font-size: 1.15rem; color: var(--text-light); line-height: 1.7;">TraverseCityWineTours.com attracts visitors actively planning their Traverse City wine country experience. Put your business in front of an engaged, high-intent audience.</p>
  </div>
  <div class="pricing-grid">
    <div class="pricing-card">
      <div class="pricing-label">Starter</div><h3>Directory Listing</h3>
      <p>Enhanced listing in our directory with premium placement and featured status.</p>
      <div class="pricing-features">
        <div class="pricing-feature">{ICON_CHECK_16} Enhanced business listing</div>
        <div class="pricing-feature">{ICON_CHECK_16} Featured badge</div>
        <div class="pricing-feature">{ICON_CHECK_16} Priority placement</div>
        <div class="pricing-feature">{ICON_CHECK_16} Link to your website</div>
      </div>
      <a href="mailto:advertise@traversecitywinetours.com" class="btn-outline-dark" style="width: 100%; justify-content: center; padding: 12px;">Contact Us</a>
    </div>
    <div class="pricing-card highlight">
      <div class="pricing-label">Most Popular</div><h3>Display Advertising</h3>
      <p>Banner ads across the site targeting visitors planning their wine country trip.</p>
      <div class="pricing-features">
        <div class="pricing-feature">{ICON_CHECK_16} Everything in Starter</div>
        <div class="pricing-feature">{ICON_CHECK_16} Sidebar & banner ads</div>
        <div class="pricing-feature">{ICON_CHECK_16} Page-specific targeting</div>
        <div class="pricing-feature">{ICON_CHECK_16} Monthly performance reports</div>
      </div>
      <a href="mailto:advertise@traversecitywinetours.com" class="btn-primary" style="width: 100%; justify-content: center; padding: 12px;">Contact Us</a>
    </div>
    <div class="pricing-card">
      <div class="pricing-label">Premium</div><h3>Content Partnership</h3>
      <p>Sponsored articles, featured spotlights, and integrated content marketing.</p>
      <div class="pricing-features">
        <div class="pricing-feature">{ICON_CHECK_16} Everything in Display</div>
        <div class="pricing-feature">{ICON_CHECK_16} Sponsored journal articles</div>
        <div class="pricing-feature">{ICON_CHECK_16} Featured spotlight</div>
        <div class="pricing-feature">{ICON_CHECK_16} Newsletter inclusion</div>
      </div>
      <a href="mailto:advertise@traversecitywinetours.com" class="btn-outline-dark" style="width: 100%; justify-content: center; padding: 12px;">Contact Us</a>
    </div>
  </div>
  <div style="text-align: center; margin-top: 48px; padding: 48px; background: var(--cream); border-radius: 8px;">
    <h3 style="font-family: 'Playfair Display', serif; font-size: 1.4rem; color: var(--burgundy); margin-bottom: 16px;">Ideal For</h3>
    <p style="font-size: 0.95rem; color: var(--text-light); line-height: 2;">Wine tour companies · Hotels & resorts · Bed & breakfasts · Restaurants & dining<br>
    <strong style="color: var(--burgundy);">Wedding planners & coordinators · Bridal services · Event venues · Florists</strong><br>
    Local attractions · Transportation services · Photographers · Retail shops</p>
    <p style="font-size: 0.88rem; color: var(--text-light); margin-top: 20px; font-style: italic;">Traverse City wine country is one of Michigan's top wedding destinations. Our audience includes couples actively planning vineyard weddings and wine-themed events.</p>
  </div>
  <div style="text-align: center; margin-top: 48px;">
    <p style="font-size: 1rem; color: var(--text); margin-bottom: 8px;">Ready to get started?</p>
    <p style="font-size: 1rem;"><a href="mailto:advertise@traversecitywinetours.com" style="color: var(--burgundy); font-weight: 600;">advertise@traversecitywinetours.com</a></p>
  </div>
</section>
{newsletter_section()}{footer_section()}{scripts()}{close()}""")
print("✓ advertise.html")

# Contact
with open(f'{OUTPUT_DIR}/contact.html', 'w') as f:
    f.write(f"""{head("Contact Us | Traverse City Wine Tours", "Get in touch with TraverseCityWineTours.com.", "/contact.html")}
{topbar()}{navbar()}
<section class="page-hero" style="height: 35vh; min-height: 280px;"><div class="page-hero-bg" style="background-image: url('vineyard.jpg');"></div><div class="page-hero-content"><div class="page-hero-tag">Get in Touch</div><h1><em>Contact</em> Us</h1></div></section>
<div class="breadcrumbs"><a href="index.html">Home</a><span>›</span><span class="current">Contact</span></div>
<section style="padding: 60px 40px 100px; max-width: 700px; margin: 0 auto;">
  <p style="font-family: 'Cormorant Garamond', serif; font-size: 1.15rem; color: var(--text-light); text-align: center; line-height: 1.7; margin-bottom: 48px;">We'd love to hear from you. Whether you have a question, want to suggest an update, or are interested in advertising, drop us a line.</p>
  <div style="display: flex; flex-direction: column; gap: 24px;">
    <div style="padding: 32px; background: var(--cream); border-radius: 8px;"><h3 style="font-family: 'Playfair Display', serif; font-size: 1.2rem; color: var(--burgundy); margin-bottom: 8px;">General Inquiries</h3><p style="font-size: 0.95rem; color: var(--text);">Email: <a href="mailto:hello@traversecitywinetours.com" style="color: var(--burgundy); font-weight: 500;">hello@traversecitywinetours.com</a></p></div>
    <div style="padding: 32px; background: var(--cream); border-radius: 8px;"><h3 style="font-family: 'Playfair Display', serif; font-size: 1.2rem; color: var(--burgundy); margin-bottom: 8px;">Advertising & Partnerships</h3><p style="font-size: 0.95rem; color: var(--text);">Email: <a href="mailto:advertise@traversecitywinetours.com" style="color: var(--burgundy); font-weight: 500;">advertise@traversecitywinetours.com</a></p><p style="font-size: 0.88rem; color: var(--text-light); margin-top: 8px;"><a href="advertise.html" style="color: var(--burgundy);">View advertising options →</a></p></div>
    <div style="padding: 32px; background: var(--cream); border-radius: 8px;"><h3 style="font-family: 'Playfair Display', serif; font-size: 1.2rem; color: var(--burgundy); margin-bottom: 8px;">Winery Updates</h3><p style="font-size: 0.95rem; color: var(--text);">Own or manage a winery? <a href="mailto:listings@traversecitywinetours.com" style="color: var(--burgundy); font-weight: 500;">listings@traversecitywinetours.com</a></p></div>
  </div>
</section>
{newsletter_section()}{footer_section()}{scripts()}{close()}""")
print("✓ contact.html")

# Sitemap
wsl = "".join([f'<li style="margin-bottom: 8px;"><a href="wineries/{w["slug"]}.html" style="color: var(--burgundy); text-decoration: none; font-size: 0.95rem;">{w["name"]}</a> <span style="color: var(--text-light); font-size: 0.82rem;">— {w["peninsula"]} Peninsula</span></li>' for w in wineries])
with open(f'{OUTPUT_DIR}/sitemap.html', 'w') as f:
    f.write(f"""{head("Sitemap | Traverse City Wine Tours", "Complete sitemap for TraverseCityWineTours.com.", "/sitemap.html")}
{topbar()}{navbar()}
<div class="breadcrumbs"><a href="index.html">Home</a><span>›</span><span class="current">Sitemap</span></div>
<section style="padding: 60px 40px 100px; max-width: 900px; margin: 0 auto;">
  <h1 style="font-family: 'Playfair Display', serif; font-size: 2.2rem; font-weight: 500; color: var(--burgundy); margin-bottom: 48px;">Sitemap</h1>
  <h2 style="font-family: 'Playfair Display', serif; font-size: 1.4rem; color: var(--burgundy); margin-bottom: 16px;">Main Pages</h2>
  <ul style="list-style: none; margin-bottom: 40px; display: flex; flex-direction: column; gap: 8px;">
    <li><a href="index.html" style="color: var(--burgundy); text-decoration: none;">Home</a></li>
    <li><a href="wineries/index.html" style="color: var(--burgundy); text-decoration: none;">All Wineries</a></li>
    <li><a href="old-mission-peninsula.html" style="color: var(--burgundy); text-decoration: none;">Old Mission Peninsula</a></li>
    <li><a href="leelanau-peninsula.html" style="color: var(--burgundy); text-decoration: none;">Leelanau Peninsula</a></li>
    <li><a href="wine-tours.html" style="color: var(--burgundy); text-decoration: none;">Wine Tours</a></li>
    <li><a href="where-to-stay.html" style="color: var(--burgundy); text-decoration: none;">Where to Stay</a></li>
    <li><a href="plan-your-visit.html" style="color: var(--burgundy); text-decoration: none;">Plan Your Visit</a></li>
    <li><a href="events.html" style="color: var(--burgundy); text-decoration: none;">Events Calendar</a></li>
    <li><a href="journal/index.html" style="color: var(--burgundy); text-decoration: none;">Wine Country Journal</a></li>
    <li><a href="about.html" style="color: var(--burgundy); text-decoration: none;">About</a></li>
    <li><a href="advertise.html" style="color: var(--burgundy); text-decoration: none;">Advertise</a></li>
    <li><a href="contact.html" style="color: var(--burgundy); text-decoration: none;">Contact</a></li>
  </ul>
  <h2 style="font-family: 'Playfair Display', serif; font-size: 1.4rem; color: var(--burgundy); margin-bottom: 16px;">All Wineries ({len(wineries)})</h2>
  <ul style="list-style: none;">{wsl}</ul>
</section>
{footer_section()}{scripts()}{close()}""")
print("✓ sitemap.html")

# Copy images
shutil.copy('/home/claude/wine-glasses.jpg', f'{OUTPUT_DIR}/wine-glasses.jpg')
shutil.copy('/home/claude/vineyard.jpg', f'{OUTPUT_DIR}/vineyard.jpg')

total = sum(1 for r,d,fs in os.walk(OUTPUT_DIR) for f in fs if f.endswith('.html'))
print(f"\n{'='*50}\n✅ SITE GENERATED: {total} HTML pages\n   All CSS inlined · All SVGs sized · No ad spots\n   Wedding planners added to advertise page\n{'='*50}")
