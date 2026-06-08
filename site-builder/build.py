#!/usr/bin/env python3
"""Static site generator for the Overseas Premier League and Vancouver Huskies sites.

Two fully independent static sites with distinct identities:
  OPL      -- the institution. Editorial / FIBA-programme. Fraunces + Archivo.
  Huskies  -- the team. Athletic / jersey. Saira Condensed + Sora.

Pure standard library. No client-side rendering. Run `python3 build.py` to regenerate.
Drop client images into site-builder/assets/<opl|huskies|aiviq>/ and rerun; labelled
placeholder slots swap to real <img> tags automatically.
"""
import json
import os
import shutil
import urllib.parse
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
CONTENT = os.path.join(ROOT, "content")
ASSETS = os.path.join(ROOT, "assets")
OUT = {"opl": os.path.join(REPO, "opl-site"), "huskies": os.path.join(REPO, "huskies-site")}

YEAR = 2026
_to_copy = {"opl": set(), "huskies": set()}
_aiviq_logo_present = os.path.isfile(os.path.join(ASSETS, "aiviq", "aiviq-enterprises.png"))

FONTS = {
    "opl": ('<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Archivo:wght@400;500;600;700&display=swap" rel="stylesheet">'),
    "huskies": ('<link rel="preconnect" href="https://fonts.googleapis.com">'
                '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                '<link href="https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@500;600;700;800&family=Sora:wght@400;500;600;700&display=swap" rel="stylesheet">'),
}


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def data_uri(svg):
    return "data:image/svg+xml," + urllib.parse.quote(svg, safe="")


# --------------------------------------------------------------------------- #
# Atmospheric SVG textures (grain + OPL globe motif)
# --------------------------------------------------------------------------- #
GRAIN = data_uri(
    "<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'>"
    "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/>"
    "<feColorMatrix type='saturate' values='0'/></filter>"
    "<rect width='160' height='160' filter='url(#n)'/></svg>")

GLOBE = data_uri(
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 400' fill='none' stroke='#ffffff' stroke-width='1'>"
    "<circle cx='200' cy='200' r='192'/><circle cx='200' cy='200' r='152'/><circle cx='200' cy='200' r='108'/>"
    "<circle cx='200' cy='200' r='62'/><ellipse cx='200' cy='200' rx='62' ry='192'/><ellipse cx='200' cy='200' rx='128' ry='192'/>"
    "<line x1='8' y1='200' x2='392' y2='200'/><line x1='30' y1='110' x2='370' y2='110'/><line x1='30' y1='290' x2='370' y2='290'/>"
    "<path stroke='#c8102e' stroke-width='2.4' d='M44 132 Q200 214 356 132'/></svg>")


# --------------------------------------------------------------------------- #
# Components
# --------------------------------------------------------------------------- #
def media(key, filename, caption, ratio="4 / 3"):
    src = os.path.join(ASSETS, key, filename)
    if os.path.isfile(src):
        _to_copy[key].add(filename)
        return (f'<figure class="media"><img src="assets/img/{esc(filename)}" '
                f'alt="{esc(caption)}" loading="lazy"></figure>')
    style = f' style="aspect-ratio:{ratio}"' if ratio else ""
    return (f'<div class="photo-slot"{style}>'
            f'<span class="tag">Asset pending</span>'
            f'<span class="label">{esc(caption)}</span>'
            f'<span class="fname">{esc(filename)}</span></div>')


def logo_slot(text, light=False):
    cls = "logo-slot light" if light else "logo-slot"
    return f'<div class="{cls}"><span class="tag">Logo pending</span><span>{esc(text)}</span></div>'


def dev_note(text):
    return (f'<div class="dev-note"><strong>Dev note (client review):</strong> '
            f'{esc(text)}</div>')


def social_icons(socials):
    paths = {
        "instagram": "M12 2.2c3.2 0 3.6 0 4.9.07 1.2.05 1.8.25 2.2.42.6.2 1 .47 1.4.9.4.4.7.8.9 1.4.17.4.37 1 .42 2.2.06 1.3.07 1.7.07 4.9s0 3.6-.07 4.9c-.05 1.2-.25 1.8-.42 2.2-.2.6-.5 1-.9 1.4-.4.4-.8.7-1.4.9-.4.17-1 .37-2.2.42-1.3.06-1.7.07-4.9.07s-3.6 0-4.9-.07c-1.2-.05-1.8-.25-2.2-.42a3.7 3.7 0 0 1-1.4-.9 3.7 3.7 0 0 1-.9-1.4c-.17-.4-.37-1-.42-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.07-4.9c.05-1.2.25-1.8.42-2.2.2-.6.5-1 .9-1.4.4-.4.8-.7 1.4-.9.4-.17 1-.37 2.2-.42C8.4 2.2 8.8 2.2 12 2.2Zm0 1.8c-3.1 0-3.5 0-4.7.07-.9.04-1.4.2-1.7.3-.4.17-.7.36-1 .66-.3.3-.5.6-.66 1-.1.3-.26.8-.3 1.7C3.3 8.5 3.3 8.9 3.3 12s0 3.5.07 4.7c.04.9.2 1.4.3 1.7.17.4.36.7.66 1 .3.3.6.5 1 .66.3.1.8.26 1.7.3 1.2.07 1.6.07 4.7.07s3.5 0 4.7-.07c.9-.04 1.4-.2 1.7-.3.4-.17.7-.36 1-.66.3-.3.5-.6.66-1 .1-.3.26-.8.3-1.7.07-1.2.07-1.6.07-4.7s0-3.5-.07-4.7c-.04-.9-.2-1.4-.3-1.7a2.7 2.7 0 0 0-.66-1 2.7 2.7 0 0 0-1-.66c-.3-.1-.8-.26-1.7-.3C15.5 4 15.1 4 12 4Zm0 3.06A4.94 4.94 0 1 1 12 17a4.94 4.94 0 0 1 0-9.88Zm0 1.8a3.14 3.14 0 1 0 0 6.28 3.14 3.14 0 0 0 0-6.28Zm5.13-.9a1.15 1.15 0 1 1-2.3 0 1.15 1.15 0 0 1 2.3 0Z",
        "x": "M18.9 2.5h3.3l-7.2 8.3 8.5 11.2h-6.7l-5.2-6.9-6 6.9H2.3l7.7-8.8L1.8 2.5h6.8l4.7 6.3 5.6-6.3Zm-1.2 17.7h1.8L7.2 4.3H5.3l12.4 15.9Z",
        "tiktok": "M16.5 2h-3v13.2a3 3 0 1 1-3-3c.2 0 .4 0 .6.05V9.2a6.1 6.1 0 1 0 5.4 6V8.6a7.3 7.3 0 0 0 4 1.2V6.7a4.3 4.3 0 0 1-4-4.7Z",
        "youtube": "M23 7.5a3 3 0 0 0-2.1-2.1C19 4.9 12 4.9 12 4.9s-7 0-8.9.5A3 3 0 0 0 1 7.5 31 31 0 0 0 .5 12 31 31 0 0 0 1 16.5a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 23.5 12 31 31 0 0 0 23 7.5ZM9.8 15.3V8.7l5.7 3.3-5.7 3.3Z",
    }
    labels = {"instagram": "Instagram", "x": "X", "tiktok": "TikTok", "youtube": "YouTube"}
    items = []
    any_live = any(socials.get(k) for k in paths)
    for k, d in paths.items():
        url = socials.get(k, "")
        svg = f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{d}"/></svg>'
        if url:
            items.append(f'<a class="soc" href="{esc(url)}" target="_blank" rel="noopener" aria-label="{labels[k]}">{svg}</a>')
        else:
            items.append(f'<span class="soc pending" title="{labels[k]} link pending" aria-label="{labels[k]} (pending)">{svg}</span>')
    note = "" if any_live else '<span class="soc-note">Social links pending</span>'
    return f'<div class="social-row">{"".join(items)}{note}</div>'


# ---- Brand marks ----
def opl_mark(key):
    f = os.path.join(ASSETS, key, "IMG_2090.png")
    if os.path.isfile(f):
        _to_copy[key].add("IMG_2090.png")
        return '<img class="mark" src="assets/img/IMG_2090.png" alt="Overseas Premier League logo">'
    return """<svg class="mark" viewBox="0 0 64 64" role="img" aria-label="Overseas Premier League logo">
  <defs><clipPath id="g"><circle cx="32" cy="32" r="24"/></clipPath></defs>
  <circle cx="32" cy="32" r="24" fill="#1c4fa0"/>
  <g clip-path="url(#g)" fill="none" stroke="#bcd2f2" stroke-width="1.3" opacity=".8">
    <ellipse cx="32" cy="32" rx="11" ry="24"/><line x1="8" y1="32" x2="56" y2="32"/><path d="M10 21H54 M10 43H54"/></g>
  <g clip-path="url(#g)" fill="none" stroke="#c8102e" stroke-width="1.7">
    <path d="M32 8V56"/><path d="M12 15Q32 26 52 15"/><path d="M12 49Q32 38 52 49"/></g>
  <circle cx="32" cy="32" r="24" fill="none" stroke="#c8102e" stroke-width="3.4"/>
  <circle cx="32" cy="32" r="9.5" fill="#ffffff"/><circle cx="32" cy="32" r="6" fill="#1c4fa0"/>
  <path d="M23 39 L42 24 l2.6 .8 -7.6 7.6 5 .9 2.6 -1.7 1.7 .9 -3.4 3.4 -4.3 4.3 -.9 -1.7 .9 -2.6 -.9 -5z" fill="#c8102e"/>
</svg>"""


def opl_hero_lockup(key):
    f = os.path.join(ASSETS, key, "IMG_2090.png")
    if os.path.isfile(f):
        _to_copy[key].add("IMG_2090.png")
        return '<img class="hero-logo" src="assets/img/IMG_2090.png" alt="Overseas Premier League logo">'
    return f"""<div class="hero-logo-lockup">
  <div class="hl-mark">{opl_mark(key)}</div>
  <div class="hl-word"><span class="hl-rule"></span><strong>OVERSEAS PREMIER LEAGUE</strong></div>
</div>"""


HUSKIES_MARK = """<svg class="mark" viewBox="0 0 64 64" role="img" aria-label="Vancouver Huskies logo placeholder">
  <circle cx="32" cy="32" r="24" fill="#c8102e"/><circle cx="32" cy="32" r="20.5" fill="#0b2349"/>
  <path d="M16 23l6 7-3 11 13 7 13-7-3-11 6-7-9 4-7-6-7 6-9-4z" fill="#ffffff"/>
  <path d="M28 33l4 3 4-3-4-1.6-4 1.6z" fill="#c8102e"/>
  <circle cx="27" cy="30" r="1.6" fill="#0b2349"/><circle cx="37" cy="30" r="1.6" fill="#0b2349"/>
</svg>"""

AIVIQ_MARK = """<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2l7 10-7 10-7-10z" fill="#c9a64a"/><path d="M12 6l4.2 6L12 18 7.8 12z" fill="#0b2349"/></svg>"""


def aiviq_credit():
    if _aiviq_logo_present:
        return '<img class="aiviq-logo" src="assets/img/aiviq-enterprises.png" alt="Aiviq Enterprises Inc.">'
    return (f'<span class="aiviq-fallback">{AIVIQ_MARK}'
            f'<span class="ac-text">Built by <strong>Aiviq Enterprises Inc.</strong></span></span>')


# --------------------------------------------------------------------------- #
# Shell
# --------------------------------------------------------------------------- #
def header(cfg, active, mark):
    parts = []
    for l in cfg["nav"]:
        cls = ' class="active"' if l["href"] == active else ""
        parts.append(f'<a href="{esc(l["href"])}"{cls}>{esc(l["label"])}</a>')
    return f"""<header class="site-header">
  <div class="container nav">
    <a class="brand" href="index.html">{mark}
      <span class="brand-text"><strong>{esc(cfg['site_name'])}</strong><span>{esc(cfg['short_name'])}</span></span></a>
    <button class="nav-toggle" aria-label="Open menu">&#9776;</button>
    <nav class="nav-links">{"".join(parts)}</nav>
  </div>
</header>"""


def footer(cfg):
    nav_links = "".join(f'<a href="{esc(l["href"])}">{esc(l["label"])}</a>' for l in cfg["nav"])
    if cfg.get("contact_email"):
        contact_html = f'<a href="mailto:{esc(cfg["contact_email"])}">{esc(cfg["contact_email"])}</a>'
    else:
        contact_html = '<span class="pending-text">Email pending</span>'
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <h4>{esc(cfg['site_name'])}</h4>
        <p class="foot-tag">{esc(cfg['tagline'])}</p>
        <p class="pending-text">Domain pending: {esc(cfg['domain_placeholder'])}</p>
      </div>
      <div><h4>Explore</h4>{nav_links}</div>
      <div><h4>Contact</h4>{contact_html}{social_icons(cfg.get('socials', {}))}</div>
    </div>
    <div class="aiviq-credit">
      <span class="aiviq-built">{aiviq_credit()}</span>
      <span class="copy">&copy; {YEAR} {esc(cfg['site_name'])}</span>
    </div>
  </div>
</footer>"""


def menu_js():
    return ("<script>document.querySelectorAll('.nav-toggle').forEach(function(b){"
            "b.addEventListener('click',function(){document.querySelector('.nav-links')"
            ".classList.toggle('open');});});</script>")


def page(cfg, mark, *, slug, title, description, body, active):
    if title == cfg["site_name"]:
        full_title = f"{cfg['site_name']} · {cfg['tagline']}"
    else:
        full_title = f"{title} · {cfg['site_name']}"
    return f"""<!DOCTYPE html>
<html lang="en" class="site-{cfg['key']}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(full_title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="theme-color" content="{cfg['theme']['navy_deep']}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{esc(cfg['site_name'])}">
  <meta property="og:title" content="{esc(full_title)}">
  <meta property="og:description" content="{esc(description)}">
  <link rel="canonical" href="https://{esc(cfg['domain_placeholder'])}/{slug}">
  {FONTS[cfg['key']]}
  <link rel="stylesheet" href="assets/css/styles.css">
</head>
<body>
{header(cfg, active, mark)}
<main>
{body}
</main>
{footer(cfg)}
{menu_js()}
</body>
</html>"""


def event_cards(events, with_cta=True):
    cards = []
    for ev in events:
        if ev.get("date_iso"):
            dt = datetime.fromisoformat(ev["date_iso"])
            chip = f'<span class="d">{dt.strftime("%b").upper()}</span>{dt.strftime("%d").lstrip("0")}'
        else:
            chip = '<span class="d">DATE</span>TBD'
        cta = ('<a class="btn btn-line btn-sm pending-btn" href="#" onclick="return false;">'
               'Register / RSVP <em>(link pending)</em></a>') if with_cta else ""
        cards.append(f"""<article class="event-card">
  <div class="date">{chip}</div>
  <div class="event-body">
    <h3>{esc(ev['name'])}</h3>
    <p class="event-meta">{esc(ev['date_display'])} · {esc(ev['location'])}</p>
    <p>{esc(ev['description'])}</p>
    {cta}
  </div>
</article>""")
    return '<div class="event-grid">' + "\n".join(cards) + "</div>"


# --------------------------------------------------------------------------- #
# OPL site  (institutional voice)
# --------------------------------------------------------------------------- #
def build_opl(cfg):
    mark = opl_mark("opl")
    pages = {}

    partner_strip = """<section class="partner-strip">
  <div class="container">
    <span class="ps-label">Official Player Placement Partner</span>
    <span class="ps-value">Valletta BC</span>
    <span class="ps-sub">Direct Player Placement. Overseas Tours. North American Scouting Combine.</span>
  </div>
</section>"""

    # Home
    routes = [
        ("01", "Direct Player Placement", "Sign with a professional men's club in Malta through the Valletta BC partnership."),
        ("02", "Overseas Tours", "Train and compete inside live professional environments abroad."),
        ("03", "North American Scouting Combine", "Scouted combines identify players for overseas placement."),
    ]
    route_html = "".join(
        f'<li class="route"><span class="r-idx">{n}</span>'
        f'<div class="r-body"><h3>{t}</h3><p>{d}</p></div></li>' for n, t, d in routes)
    home = f"""<section class="hero hero-opl">
  <div class="container hero-inner stagger">
    {opl_hero_lockup('opl')}
    <span class="eyebrow">FIBA Licensed · EuroBasket Eligible</span>
    <h1>The overseas route to professional basketball</h1>
    <p class="lead">OPL places North American players with FIBA licensed professional clubs in Europe. Registration, housing, and film are handled.</p>
    <div class="cta-row">
      <a class="btn btn-primary btn-lg" href="events.html">Upcoming events</a>
      <a class="btn btn-ghost btn-lg" href="placement.html">How placement works</a>
    </div>
  </div>
</section>
{partner_strip}
<section class="routes-sec">
  <div class="container">
    <div class="section-head"><span class="kicker">The pathway</span><h2>Three routes overseas</h2></div>
    <ol class="routes">{route_html}</ol>
  </div>
</section>
<section class="dark cta-band">
  <div class="container"><div class="banner">
    <span class="kicker red">Malta</span>
    <h2>Placement runs through Malta</h2>
    <p>Review the placement package and the training camp.</p>
    <a class="btn btn-gold btn-lg" href="placement.html">Player placement</a>
  </div></div>
</section>"""
    pages["index.html"] = page(cfg, mark, slug="", title=cfg["site_name"],
        description="OPL places North American players with FIBA licensed professional clubs in Europe. FIBA Licensed. EuroBasket Eligible.",
        body=home, active="index.html")

    # About
    about = f"""<section class="page-hero">
  <div class="container ph-inner stagger">
    <span class="eyebrow">About</span>
    <h1>The league and its partnership</h1>
  </div>
</section>
<section>
  <div class="container split">
    <div class="prose">
      <span class="kicker">Partnership</span>
      <h2>Valletta BC</h2>
      <p>A formal partnership with Valletta BC makes the Overseas Premier League an official player placement partner.</p>
      <p>It delivers placement through three channels:</p>
      <ul class="checks">
        <li>Direct Player Placement</li>
        <li>Overseas Tours</li>
        <li>North American Scouting Combine</li>
      </ul>
      {dev_note('Confirm the "official player placement partner" wording is accurate and approved by Valletta BC before launch.')}
    </div>
    <div>{logo_slot('Valletta BC logo', light=True)}</div>
  </div>
</section>
<section class="dark cta-band">
  <div class="container"><div class="banner">
    <span class="kicker red">The pipeline</span>
    <h2>From combine to contract</h2>
    <p>Direct placement, overseas tours, and the scouting combine feed one pipeline.</p>
    <a class="btn btn-gold btn-lg" href="placement.html">Player placement</a>
  </div></div>
</section>"""
    pages["about.html"] = page(cfg, mark, slug="about.html", title="About",
        description="A formal partnership with Valletta BC makes the Overseas Premier League an official player placement partner, delivered through direct placement, overseas tours, and a North American scouting combine.",
        body=about, active="about.html")

    # Player Placement
    placement = f"""<section class="page-hero">
  <div class="container ph-inner stagger">
    <span class="eyebrow">Player Placement</span>
    <h1>Two ways into the professional game</h1>
    <p class="lead">FIBA Licensed. EuroBasket Eligible. Players must be passport ready.</p>
  </div>
</section>
<section>
  <div class="container">
    <div class="offer-grid">
      <article class="offer-card">
        {media('opl', 'IMG_2087.png', 'OPL & ProConnect player placement package flyer', ratio='3 / 4')}
        <div class="offer-body">
          <h2>Overseas Player Placement Package</h2>
          <p>Join a professional men's team in Malta. FIBA Licensed. EuroBasket Eligible.</p>
          <h3>Player Perks</h3>
          <ul class="checks">
            <li>FIBA Registration</li>
            <li>Malta Basketball Association Registration</li>
            <li>VISA (for stays over 90 days)</li>
            <li>Gym Membership Fee</li>
            <li>Transportation &amp; Housing</li>
            <li>Media Package (Film &amp; Interviews)</li>
          </ul>
          <p class="must">Must be passport ready.</p>
          {dev_note('Confirm the player perks list is complete and accurate before launch.')}
        </div>
      </article>
      <article class="offer-card">
        {media('opl', 'IMG_2088.png', 'OPL & ProConnect overseas training camp flyer', ratio='3 / 4')}
        <div class="offer-body">
          <h2>Overseas Training Camp</h2>
          <p>A professional men's training camp in Malta. Compete in front of team owners and executives. Opportunities to sign with a 1st or 2nd Division club.</p>
          <h3>Tour Package Includes</h3>
          <ul class="checks">
            <li>Accommodations for 7 Days</li>
            <li>Merch (Reversible, T-Shirt, and Shorts)</li>
            <li>Transportation (Airport &amp; Gym)</li>
            <li>Media (Game Film &amp; Player Interviews)</li>
            <li>Food (Two Meals Per Day)</li>
          </ul>
          <p class="must">Must be passport ready.</p>
          {dev_note('Confirm the tour package list is complete and accurate before launch.')}
        </div>
      </article>
    </div>
    {dev_note('Confirm "FIBA Licensed" and "EuroBasket Eligible" can be claimed publicly in these exact words before launch.')}
  </div>
</section>
<section class="dark cta-band">
  <div class="container"><div class="banner">
    <span class="kicker red">2026</span>
    <h2>Camps and league dates</h2>
    <p>See the schedule.</p>
    <a class="btn btn-gold btn-lg" href="events.html">Events</a>
  </div></div>
</section>"""
    pages["placement.html"] = page(cfg, mark, slug="placement.html", title="Player Placement",
        description="Overseas player placement package and overseas training camp in Malta. FIBA Licensed, EuroBasket Eligible. Perks include FIBA and MBA registration, VISA, housing, transport, and a media package.",
        body=placement, active="placement.html")

    # Events
    events = f"""<section class="page-hero">
  <div class="container ph-inner stagger">
    <span class="eyebrow">Events</span>
    <h1>The 2026 schedule</h1>
  </div>
</section>
<section>
  <div class="container">{event_cards(cfg['events'], with_cta=True)}</div>
</section>"""
    pages["events.html"] = page(cfg, mark, slug="events.html", title="Events",
        description="OPL 2026 events: Overseas Training Camp (Sept 21 to 28, Malta), Summer League (July 5), and the League Combine (TBD).",
        body=events, active="events.html")

    # Contact
    contact = f"""<section class="page-hero">
  <div class="container ph-inner stagger">
    <span class="eyebrow">Contact</span>
    <h1>League office</h1>
  </div>
</section>
<section>
  <div class="container split">
    <div class="prose">
      <span class="kicker">Contact</span>
      <h2>Reach OPL</h2>
      <p class="lead-text"><strong>Email:</strong> <span class="pending-text">Pending from client</span></p>
      {dev_note('OPL contact email address is pending from the client. Add it to content/opl.json (contact_email) and rebuild.')}
      <p>Social links coming soon.</p>
      {social_icons(cfg.get('socials', {}))}
    </div>
    <div>{logo_slot('OPL logo (IMG_2090.png)', light=True)}</div>
  </div>
</section>"""
    pages["contact.html"] = page(cfg, mark, slug="contact.html", title="Contact",
        description="Contact the Overseas Premier League about player placement, the Malta package, and events.",
        body=contact, active="contact.html")

    return pages


# --------------------------------------------------------------------------- #
# Huskies site  (direct, personal voice)
# --------------------------------------------------------------------------- #
def build_huskies(cfg):
    mark = HUSKIES_MARK
    pages = {}
    square = cfg.get("square_link", "#")
    square_pending = (not square) or square.startswith("#")
    if square_pending:
        square_btn = ('<a class="btn btn-gold btn-lg pending-btn" href="#" onclick="return false;">'
                      'Sign Up &amp; Pay via Square <em>(Square link pending)</em></a>')
    else:
        square_btn = (f'<a class="btn btn-gold btn-lg" href="{esc(square)}" target="_blank" '
                      f'rel="noopener">Sign Up &amp; Pay via Square</a>')

    opl_url = cfg.get("opl_site_url", "#")
    partner_strip = f"""<section class="partner-strip">
  <div class="container">
    <span class="ps-label">Official Partner</span>
    <span class="ps-value">Overseas Premier League</span>
    <span class="ps-sub"><a href="{esc(opl_url)}" target="_blank" rel="noopener">Visit the league</a>
    <span class="pending-text">(OPL domain pending)</span></span>
  </div>
</section>"""

    gallery = "".join(media("huskies", g["file"], g["caption"], ratio="") for g in cfg["gallery"])
    home = f"""<section class="hero hero-huskies">
  <span class="ghost" aria-hidden="true">HUSKIES</span>
  <span class="slash" aria-hidden="true"></span>
  <div class="container hero-inner stagger">
    <div class="hero-logo-slot">{logo_slot('Vancouver Huskies wolf logo')}</div>
    <h1>Vancouver Huskies basketball</h1>
    <p class="lead">Train, compete, and put your game on film. A Vancouver development program affiliated with the Overseas Premier League.</p>
    <div class="cta-row"><a class="btn btn-primary btn-lg" href="signup.html">Sign up and pay</a></div>
  </div>
</section>
{partner_strip}
<section id="gallery">
  <div class="container">
    <div class="section-head"><span class="kicker">The roster</span><h2>On the floor</h2></div>
    <div class="gallery-grid">{gallery}</div>
  </div>
</section>
<section class="dark cta-band">
  <div class="container"><div class="banner">
    <span class="kicker red">Roster spots open</span>
    <h2>Ready to play?</h2>
    <p>Register and pay through our Square account.</p>
    {square_btn}
  </div></div>
</section>"""
    pages["index.html"] = page(cfg, mark, slug="", title=cfg["site_name"],
        description="Vancouver Huskies basketball. Train, compete, and put your game on film. A Vancouver development program affiliated with the Overseas Premier League.",
        body=home, active="index.html")

    # Events
    events = f"""<section class="page-hero">
  <div class="container ph-inner stagger">
    <span class="eyebrow">Events</span>
    <h1>Where we play</h1>
  </div>
</section>
<section>
  <div class="container">
    <div class="section-head"><span class="kicker">Through the OPL</span><h2>League events</h2></div>
    {event_cards(cfg['events'], with_cta=False)}
  </div>
</section>
<section class="alt">
  <div class="container">
    <div class="section-head"><span class="kicker">Local</span><h2>Huskies events</h2></div>
    <div class="photo-slot" style="aspect-ratio:auto;min-height:140px">
      <span class="tag">Content pending</span>
      <span class="label">Huskies training schedules &amp; local games</span>
      <span class="fname">Pending from client</span>
    </div>
  </div>
</section>"""
    pages["events.html"] = page(cfg, mark, slug="events.html", title="Events",
        description="Vancouver Huskies events: OPL Overseas Training Camp (Sept 21 to 28), OPL Summer League (July 5), OPL League Combine (TBD), plus local Huskies events.",
        body=events, active="events.html")

    # Sign Up
    sp = cfg.get("signup_photo", {"file": "IMG_2081.png", "caption": "Vancouver Huskies"})
    note = (dev_note('Square payment link is pending from the client. Set "square_link" in content/huskies.json and '
                     'rebuild. The button switches to the real checkout automatically.') if square_pending else "")
    signup = f"""<section class="page-hero">
  <div class="container ph-inner stagger">
    <span class="eyebrow">Sign Up &amp; Pay</span>
    <h1>Join the Huskies</h1>
  </div>
</section>
<section>
  <div class="container split">
    <div class="prose">
      <span class="kicker">Registration</span>
      <h2>Register and pay with Square</h2>
      <p>You register and pay through Square. Invoices come from the Vancouver Huskies Square account.</p>
      <p style="margin:1.6rem 0">{square_btn}</p>
      {note}
      <p><strong>Contact:</strong> <a href="mailto:{esc(cfg['contact_email'])}">{esc(cfg['contact_email'])}</a></p>
    </div>
    <div>{media('huskies', sp['file'], sp['caption'], ratio='3 / 4')}</div>
  </div>
</section>"""
    pages["signup.html"] = page(cfg, mark, slug="signup.html", title="Sign Up & Pay",
        description="Join the Vancouver Huskies. Register and pay through the Vancouver Huskies Square account.",
        body=signup, active="signup.html")

    return pages


# --------------------------------------------------------------------------- #
# CSS  (one stylesheet per site; distinct typography + atmosphere)
# --------------------------------------------------------------------------- #
def css(key, theme):
    t = theme
    if key == "opl":
        font_display = "'Fraunces', Georgia, 'Times New Roman', serif"
        font_body = "'Archivo', system-ui, -apple-system, sans-serif"
        h_transform, h_weight, h_spacing = "none", "600", "-.015em"
        hero_h1 = "clamp(2.6rem,6vw,5rem)"; hero_lh = "1.03"
        hero_extra = f""".hero-opl::after {{ content:""; position:absolute; top:-22%; right:-12%; width:min(72vw,720px); height:min(72vw,720px);
  background:url("{GLOBE}") center/contain no-repeat; opacity:.14; z-index:1; pointer-events:none; }}"""
    else:
        font_display = "'Saira Condensed', 'Arial Narrow', system-ui, sans-serif"
        font_body = "'Sora', system-ui, -apple-system, sans-serif"
        h_transform, h_weight, h_spacing = "uppercase", "700", ".005em"
        hero_h1 = "clamp(3rem,9vw,6.75rem)"; hero_lh = ".9"
        hero_extra = """.hero-huskies .ghost {{ }}"""  # placeholder, real rules below
        hero_extra = f""".hero-huskies {{ }}
.ghost {{ position:absolute; left:-1.5%; bottom:-10%; z-index:1; pointer-events:none; white-space:nowrap;
  font-family:{font_display}; font-weight:800; text-transform:uppercase; letter-spacing:-.03em;
  font-size:clamp(7rem,25vw,21rem); line-height:.8; color:rgba(255,255,255,.05); }}
.slash {{ position:absolute; top:-12%; right:9%; width:9px; height:135%; background:var(--red); z-index:2;
  transform:rotate(13deg); opacity:.92; box-shadow:0 0 40px rgba(200,16,46,.35); }}
@media (max-width:860px) {{ .slash {{ right:5%; }} .ghost {{ bottom:-6%; }} }}"""

    return f""":root {{
  --navy:{t['navy']}; --navy-deep:{t['navy_deep']}; --red:{t['red']}; --white:{t['white']}; --gold:{t['gold']};
  --ink:#16233d; --muted:#aebbd3; --line:rgba(255,255,255,.12); --hair:#e6e9f1;
  --display:{font_display}; --body:{font_body};
  --grain:url("{GRAIN}");
}}
* {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{ margin:0; font-family:var(--body); color:var(--ink); background:var(--white); line-height:1.6;
  overflow-x:hidden; -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility; }}
a {{ color:var(--red); text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
img {{ max-width:100%; display:block; }}
.container {{ width:min(1180px,92vw); margin:0 auto; }}
h1,h2,h3 {{ font-family:var(--display); font-weight:{h_weight}; letter-spacing:{h_spacing}; }}

/* header */
.site-header {{ background:var(--navy-deep); border-bottom:1px solid var(--line); position:sticky; top:0; z-index:50; }}
.site-header::after {{ content:""; display:block; height:2px; background:linear-gradient(90deg,var(--red) 0 22%,transparent 22%); }}
.nav {{ display:flex; align-items:center; justify-content:space-between; gap:1rem; padding:.75rem 0; }}
.brand {{ display:flex; align-items:center; gap:.7rem; color:var(--white); }}
.brand:hover {{ text-decoration:none; }}
.brand .mark {{ width:44px; height:44px; flex:0 0 auto; border-radius:6px; }}
.brand .brand-text {{ display:flex; flex-direction:column; line-height:1.05; }}
.brand .brand-text strong {{ font-family:var(--display); font-size:1.05rem; letter-spacing:.01em; text-transform:{h_transform}; }}
.brand .brand-text span {{ font-family:var(--body); font-size:.66rem; color:var(--gold); letter-spacing:.28em; text-transform:uppercase; }}
.nav-links {{ display:flex; gap:.15rem; flex-wrap:wrap; }}
.nav-links a {{ color:var(--muted); padding:.5rem .85rem; border-radius:6px; font-weight:600; font-size:.82rem;
  letter-spacing:.08em; text-transform:uppercase; transition:color .2s, background .2s; }}
.nav-links a:hover {{ color:var(--white); background:rgba(255,255,255,.06); text-decoration:none; }}
.nav-links a.active {{ color:var(--white); }}
.nav-links a.active::after {{ content:""; display:block; height:2px; background:var(--red); margin-top:3px; }}
.nav-toggle {{ display:none; }}

/* hero */
.hero {{ position:relative; overflow:hidden; background:var(--navy-deep); color:#fff; }}
.hero::before {{ content:""; position:absolute; inset:0; background:
  radial-gradient(120% 90% at 78% -10%, rgba(28,79,160,.45), transparent 55%),
  radial-gradient(80% 70% at 12% 110%, rgba(200,16,46,.18), transparent 60%); z-index:0; }}
.hero .grain, .hero::after, .page-hero::after {{}}
.hero .hero-inner {{ position:relative; z-index:3; padding:5rem 0 4.5rem; max-width:820px; }}
.hero .hero-inner::before {{ content:""; position:absolute; inset:0; background-image:var(--grain); opacity:.07; mix-blend-mode:overlay; pointer-events:none; }}
{hero_extra}
.eyebrow {{ display:inline-block; font-family:var(--body); text-transform:uppercase; letter-spacing:.26em; font-size:.7rem;
  font-weight:700; color:var(--gold); padding:.35rem 0; margin-bottom:.9rem; border-top:1px solid rgba(201,166,74,.5);
  border-bottom:1px solid rgba(201,166,74,.5); }}
.hero h1 {{ font-size:{hero_h1}; line-height:{hero_lh}; margin:.3rem 0 1.1rem; text-transform:{h_transform};
  max-width:14ch; overflow-wrap:break-word; }}
.hero p.lead {{ font-family:var(--body); font-size:clamp(1.05rem,2vw,1.28rem); color:#d7deec; margin:0 0 1.9rem; max-width:54ch; }}

.hero-logo {{ max-height:88px; width:auto; margin-bottom:1.3rem; }}
.hero-logo-lockup {{ display:inline-flex; align-items:center; gap:1rem; margin-bottom:1.4rem; max-width:100%; flex-wrap:wrap;
  background:rgba(255,255,255,.05); border:1px solid var(--line); padding:.7rem 1.1rem; border-radius:10px; }}
.hero-logo-lockup .mark {{ width:60px; height:60px; }}
.hl-word {{ display:flex; flex-direction:column; gap:.4rem; min-width:0; }}
.hl-word strong {{ font-family:var(--body); color:#fff; letter-spacing:.22em; font-size:clamp(.66rem,2.4vw,.85rem); overflow-wrap:break-word; }}
.hl-rule {{ height:2px; width:46px; background:var(--red); }}
.hero-logo-slot {{ max-width:230px; margin-bottom:1.4rem; }}

/* buttons */
.cta-row {{ display:flex; gap:.8rem; flex-wrap:wrap; }}
.btn {{ display:inline-block; font-family:var(--body); font-weight:700; letter-spacing:.04em; padding:.85rem 1.6rem;
  border-radius:7px; border:1.5px solid transparent; cursor:pointer; font-size:.98rem; transition:transform .2s ease,
  background .2s ease, color .2s ease, border-color .2s ease, box-shadow .2s ease; }}
.btn:hover {{ transform:translateY(-2px); text-decoration:none; }}
.btn-primary {{ background:var(--red); color:#fff; box-shadow:0 8px 22px rgba(200,16,46,.28); }}
.btn-primary:hover {{ background:#aa0c25; box-shadow:0 12px 28px rgba(200,16,46,.38); }}
.btn-ghost {{ background:transparent; color:#fff; border-color:rgba(255,255,255,.45); }}
.btn-ghost:hover {{ background:#fff; color:var(--navy-deep); border-color:#fff; }}
.btn-line {{ background:transparent; color:var(--navy); border-color:var(--navy); }}
.btn-line:hover {{ background:var(--navy); color:#fff; }}
.btn-gold {{ background:var(--gold); color:var(--navy-deep); box-shadow:0 8px 22px rgba(201,166,74,.25); }}
.btn-gold:hover {{ filter:brightness(1.06); }}
.btn-lg {{ padding:1.05rem 2.1rem; font-size:1.06rem; }}
.btn-sm {{ padding:.55rem 1.05rem; font-size:.85rem; }}
.pending-btn {{ opacity:.95; outline:2px dashed var(--gold); outline-offset:3px; cursor:not-allowed; }}
.pending-btn em {{ font-style:normal; font-weight:600; font-size:.8em; opacity:.85; }}

/* sections */
section {{ padding:5rem 0; }}
.page-hero {{ position:relative; overflow:hidden; background:var(--navy-deep); color:#fff; padding:3.5rem 0; }}
.page-hero::before {{ content:""; position:absolute; inset:0; background:radial-gradient(90% 120% at 85% -20%, rgba(28,79,160,.4), transparent 55%); }}
.page-hero .ph-inner {{ position:relative; z-index:2; }}
.page-hero h1 {{ font-size:clamp(2rem,5vw,3.4rem); margin:.4rem 0 0; text-transform:{h_transform}; }}
.page-hero .lead {{ font-family:var(--body); color:#d7deec; margin:1rem 0 0; max-width:60ch; font-size:1.1rem; }}
.section-head {{ max-width:760px; margin-bottom:2.6rem; }}
.section-head h2 {{ font-size:clamp(1.7rem,3.6vw,2.6rem); color:var(--navy); margin:.4rem 0 0; text-transform:{h_transform}; }}
.kicker {{ font-family:var(--body); text-transform:uppercase; letter-spacing:.24em; font-size:.7rem; font-weight:700; color:var(--red); }}
.kicker.red {{ color:var(--gold); }}
.alt {{ background:#f5f7fb; }}
.dark {{ background:var(--navy); color:#fff; }}
.dark h2 {{ color:#fff; }}

/* partner strip (red as accent, not fill) */
.partner-strip {{ background:var(--navy-deep); color:#fff; border-top:1px solid var(--line); border-bottom:1px solid var(--line); padding:1.4rem 0; }}
.partner-strip .container {{ display:flex; gap:.4rem 2rem; align-items:baseline; flex-wrap:wrap; }}
.ps-label {{ font-family:var(--body); color:var(--red); font-weight:700; font-size:.7rem; letter-spacing:.2em; text-transform:uppercase; }}
.ps-value {{ font-family:var(--display); font-size:1.4rem; text-transform:{h_transform}; }}
.ps-sub {{ font-family:var(--body); color:var(--muted); font-size:.9rem; margin-left:auto; }}
.ps-sub a {{ color:#fff; text-decoration:underline; }}

/* routes (OPL editorial grid-break) */
.routes {{ list-style:none; margin:0; padding:0; border-top:1px solid var(--hair); }}
.route {{ display:grid; grid-template-columns:minmax(80px,150px) 1fr; gap:2rem; padding:2.4rem .5rem; border-bottom:1px solid var(--hair);
  align-items:start; transition:background .25s ease; }}
.route:hover {{ background:#f7f9fd; }}
.r-idx {{ font-family:var(--display); font-size:clamp(2.6rem,6vw,4.6rem); line-height:.8; color:var(--red); font-weight:{h_weight}; }}
.r-body {{ max-width:52ch; }}
.r-body h3 {{ color:var(--navy); font-size:1.55rem; margin:.1rem 0 .4rem; text-transform:{h_transform}; }}
.r-body p {{ color:#4a5870; font-size:1.08rem; margin:0; }}

/* cards */
.card {{ position:relative; background:#fff; border:1px solid var(--hair); border-radius:12px; padding:1.6rem;
  transition:transform .25s ease, box-shadow .25s ease; overflow:hidden; }}
.card::before {{ content:""; position:absolute; top:0; left:0; height:3px; width:0; background:var(--red); transition:width .3s ease; }}
.card:hover {{ transform:translateY(-6px); box-shadow:0 20px 44px rgba(11,35,73,.14); }}
.card:hover::before {{ width:100%; }}
.card h3 {{ margin:.4rem 0 .5rem; color:var(--navy); font-size:1.2rem; text-transform:{h_transform}; }}

.checks {{ list-style:none; padding:0; margin:.7rem 0 1rem; display:grid; gap:.6rem; font-family:var(--body); }}
.checks li {{ position:relative; padding-left:1.9rem; color:var(--ink); }}
.checks li::before {{ content:""; position:absolute; left:0; top:.35em; width:1.05rem; height:1.05rem; background:var(--red);
  -webkit-mask:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M20 6L9 17l-5-5' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/></svg>") center/contain no-repeat;
  mask:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M20 6L9 17l-5-5' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/></svg>") center/contain no-repeat; }}
.must {{ font-weight:700; color:var(--navy); font-family:var(--body); }}

/* offer cards (asymmetric on desktop) */
.offer-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:1.8rem; align-items:start; }}
.offer-card {{ border:1px solid var(--hair); border-radius:14px; overflow:hidden; background:#fff; display:flex; flex-direction:column;
  transition:transform .25s ease, box-shadow .25s ease; }}
.offer-card:hover {{ transform:translateY(-5px); box-shadow:0 22px 50px rgba(11,35,73,.16); }}
.offer-card:nth-child(2) {{ margin-top:3.5rem; }}
.offer-card .offer-body {{ padding:1.7rem; }}
.offer-card h2 {{ color:var(--navy); margin:.2rem 0 .5rem; font-size:1.5rem; text-transform:{h_transform}; }}
.offer-card h3 {{ color:var(--red); font-family:var(--body); font-size:.78rem; text-transform:uppercase; letter-spacing:.16em; margin:1.2rem 0 .2rem; }}
.offer-card .media img {{ aspect-ratio:3/4; object-fit:cover; }}

/* events */
.event-grid {{ display:grid; gap:1.1rem; }}
.event-card {{ display:grid; grid-template-columns:108px 1fr; gap:1.4rem; align-items:start; border:1px solid var(--hair);
  border-radius:12px; padding:1.4rem; background:#fff; transition:transform .25s ease, box-shadow .25s ease; }}
.event-card:hover {{ transform:translateY(-4px); box-shadow:0 16px 36px rgba(11,35,73,.12); }}
.event-card .date {{ text-align:center; background:var(--navy); color:#fff; border-radius:10px; padding:1rem .5rem; font-family:var(--display);
  font-weight:{h_weight}; font-size:1.7rem; line-height:1; }}
.event-card .date .d {{ display:block; font-family:var(--body); font-size:.72rem; color:var(--gold); letter-spacing:.12em; margin-bottom:.3rem; }}
.event-card h3 {{ margin:0 0 .2rem; color:var(--navy); font-size:1.3rem; text-transform:{h_transform}; }}
.event-card .event-meta {{ margin:0 0 .5rem; color:var(--red); font-family:var(--body); font-weight:600; font-size:.85rem; letter-spacing:.04em; }}
.event-card p {{ margin:0 0 .7rem; color:#51607a; font-family:var(--body); font-size:.96rem; }}

/* media + slots */
.media {{ margin:0; }}
.media img {{ width:100%; height:100%; object-fit:cover; border-radius:12px; }}
.offer-card .media img {{ border-radius:0; }}
.gallery-grid {{ display:grid; grid-template-columns:repeat(3,1fr); grid-auto-rows:200px; gap:14px; }}
.gallery-grid > * {{ height:100%; }}
.gallery-grid .photo-slot {{ height:100%; }}
.gallery-grid .media, .gallery-grid .media img {{ height:100%; }}
.gallery-grid > *:nth-child(1) {{ grid-row:span 2; }}
.gallery-grid > *:nth-child(4) {{ grid-row:span 2; }}
.gallery-grid > *:nth-child(5) {{ grid-column:span 2; }}
.photo-slot {{ position:relative; aspect-ratio:4/3; border-radius:12px; overflow:hidden;
  background:repeating-linear-gradient(45deg,#e9edf5 0 14px,#f3f6fb 14px 28px); border:1px solid #dbe1ec;
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:.3rem; text-align:center; padding:1rem; }}
.photo-slot .tag {{ position:absolute; top:.6rem; left:.6rem; background:var(--navy); color:#fff; font-family:var(--body);
  font-size:.6rem; letter-spacing:.12em; text-transform:uppercase; padding:.25rem .55rem; border-radius:4px; font-weight:700; }}
.photo-slot .label {{ font-family:var(--body); font-weight:700; font-size:.95rem; color:#3c4a63; }}
.photo-slot .fname {{ font-size:.76rem; color:#7b879c; font-family:ui-monospace,Menlo,Consolas,monospace; }}

/* logo slot */
.logo-slot {{ position:relative; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;
  border:2px dashed rgba(201,166,74,.7); border-radius:12px; background:rgba(255,255,255,.04); color:var(--gold);
  min-height:150px; padding:1.5rem 1rem; font-family:var(--body); font-weight:700; gap:.3rem; }}
.logo-slot .tag {{ position:absolute; top:.6rem; left:.6rem; background:var(--gold); color:var(--navy-deep); font-size:.6rem;
  letter-spacing:.12em; text-transform:uppercase; padding:.25rem .55rem; border-radius:4px; }}
.logo-slot.light {{ background:#eef1f7; border-color:#c4ccdb; color:#7b879c; }}

/* dev note */
.dev-note {{ background:repeating-linear-gradient(45deg,#fff6e6 0 12px,#fdeecb 12px 24px); border:1.5px dashed var(--red);
  color:#5a4304; border-radius:10px; padding:.85rem 1.1rem; font-family:var(--body); font-size:.9rem; margin:1.2rem 0; }}
.dev-note strong {{ color:var(--red); }}

/* banner */
.cta-band {{ position:relative; overflow:hidden; }}
.banner {{ position:relative; background:linear-gradient(135deg,#0e2b58 0%,var(--navy-deep) 100%); color:#fff; border:1px solid var(--line);
  border-radius:18px; padding:3rem 2.5rem; text-align:center; }}
.banner::before {{ content:""; position:absolute; inset:0; background-image:var(--grain); opacity:.06; pointer-events:none; }}
.banner .kicker {{ display:block; margin-bottom:.6rem; }}
.banner h2 {{ color:#fff; margin:0 0 .6rem; font-size:clamp(1.6rem,3.4vw,2.4rem); text-transform:{h_transform}; }}
.banner p {{ color:var(--muted); max-width:520px; margin:0 auto 1.5rem; font-family:var(--body); }}

/* split / prose */
.split {{ display:grid; grid-template-columns:1.05fr .95fr; gap:3rem; align-items:center; }}
.prose h2 {{ color:var(--navy); font-size:clamp(1.6rem,3.2vw,2.2rem); margin:.4rem 0 1rem; text-transform:{h_transform}; }}
.prose p {{ font-family:var(--body); color:#3f4d66; font-size:1.05rem; }}

/* footer */
.site-footer {{ background:var(--navy-deep); color:var(--muted); padding:3.5rem 0 2rem; }}
.footer-grid {{ display:grid; grid-template-columns:2fr 1fr 1.3fr; gap:2.5rem; }}
.footer-grid h4 {{ font-family:var(--body); color:#fff; font-size:.74rem; letter-spacing:.2em; text-transform:uppercase; margin:0 0 .9rem; }}
.footer-grid a {{ color:var(--muted); display:block; padding:.18rem 0; font-family:var(--body); font-size:.95rem; }}
.footer-grid a:hover {{ color:#fff; }}
.foot-tag {{ font-family:var(--body); color:#c6d0e3; }}
.pending-text {{ color:#8290ab; font-style:italic; }}
.social-row {{ display:flex; align-items:center; gap:.5rem; margin-top:.9rem; flex-wrap:wrap; }}
.soc {{ display:inline-flex; width:34px; height:34px; align-items:center; justify-content:center; border-radius:8px; background:rgba(255,255,255,.07); }}
.soc svg {{ width:18px; height:18px; fill:var(--muted); }}
.soc:hover svg {{ fill:#fff; }}
.soc.pending {{ opacity:.5; outline:1px dashed var(--gold); cursor:not-allowed; }}
.soc-note {{ font-size:.76rem; color:#8290ab; font-style:italic; }}
/* premium gold credit */
.aiviq-credit {{ margin-top:2.8rem; padding-top:1.6rem; position:relative; display:flex; align-items:center;
  justify-content:space-between; gap:1rem; flex-wrap:wrap; font-family:var(--body); font-size:.84rem; }}
.aiviq-credit::before {{ content:""; position:absolute; top:0; left:0; width:64px; height:1px; background:var(--gold); }}
.aiviq-credit::after {{ content:""; position:absolute; top:0; left:0; right:0; height:1px; background:rgba(201,166,74,.18); z-index:-1; }}
.aiviq-logo {{ height:38px; width:auto; }}
.aiviq-fallback {{ display:flex; align-items:center; gap:.6rem; }}
.aiviq-fallback svg {{ width:22px; height:22px; }}
.ac-text {{ color:#9aa6bf; letter-spacing:.04em; }}
.ac-text strong {{ color:var(--gold); letter-spacing:.06em; }}
.copy {{ color:#73809b; }}

/* motion: one orchestrated page load */
@keyframes rise {{ from {{ opacity:0; transform:translateY(22px); }} to {{ opacity:1; transform:translateY(0); }} }}
.stagger > * {{ opacity:0; animation:rise .8s cubic-bezier(.22,.61,.36,1) forwards; }}
.stagger > *:nth-child(1) {{ animation-delay:.06s; }}
.stagger > *:nth-child(2) {{ animation-delay:.16s; }}
.stagger > *:nth-child(3) {{ animation-delay:.26s; }}
.stagger > *:nth-child(4) {{ animation-delay:.36s; }}
.stagger > *:nth-child(5) {{ animation-delay:.46s; }}
.stagger > *:nth-child(6) {{ animation-delay:.56s; }}
@media (prefers-reduced-motion: reduce) {{ .stagger > * {{ opacity:1; transform:none; animation:none; }} }}

/* responsive */
@media (max-width:860px) {{
  .footer-grid, .split, .offer-grid {{ grid-template-columns:1fr; }}
  .offer-card:nth-child(2) {{ margin-top:0; }}
  .gallery-grid {{ grid-template-columns:repeat(2,1fr); grid-auto-rows:170px; }}
  .gallery-grid > *:nth-child(5) {{ grid-column:span 1; }}
  .nav-links {{ display:none; position:absolute; top:100%; left:0; right:0; background:var(--navy-deep); flex-direction:column;
    padding:.5rem 5vw 1rem; gap:.1rem; border-bottom:2px solid var(--red); }}
  .nav-links.open {{ display:flex; }}
  .nav-toggle {{ display:inline-flex; background:transparent; border:1px solid var(--line); color:#fff; border-radius:8px;
    padding:.5rem .7rem; cursor:pointer; font-size:1rem; }}
  .route {{ grid-template-columns:1fr; gap:.4rem; }}
  .hero .hero-inner {{ padding:3.5rem 0; }}
}}
@media (max-width:520px) {{
  .gallery-grid {{ grid-template-columns:1fr; grid-auto-rows:220px; }}
  .gallery-grid > *:nth-child(1), .gallery-grid > *:nth-child(4) {{ grid-row:span 1; }}
  .event-card {{ grid-template-columns:84px 1fr; }}
  .ps-sub {{ margin-left:0; }}
}}
"""


# --------------------------------------------------------------------------- #
def write_site(key, cfg, pages):
    out = OUT[key]
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "assets", "css"), exist_ok=True)
    with open(os.path.join(out, "assets", "css", "styles.css"), "w") as f:
        f.write(css(key, cfg["theme"]))
    if _to_copy[key] or _aiviq_logo_present:
        img_out = os.path.join(out, "assets", "img")
        os.makedirs(img_out, exist_ok=True)
        for fn in _to_copy[key]:
            shutil.copy(os.path.join(ASSETS, key, fn), os.path.join(img_out, fn))
        if _aiviq_logo_present:
            shutil.copy(os.path.join(ASSETS, "aiviq", "aiviq-enterprises.png"), os.path.join(img_out, "aiviq-enterprises.png"))
    for name, html in pages.items():
        with open(os.path.join(out, name), "w") as f:
            f.write(html)
    base = f"https://{cfg['domain_placeholder']}"
    with open(os.path.join(out, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
    urls = "".join(f"  <url><loc>{base}/{n if n!='index.html' else ''}</loc></url>\n" for n in pages)
    with open(os.path.join(out, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    n_img = len(_to_copy[key]) + (1 if _aiviq_logo_present else 0)
    print(f"  {key}: {len(pages)} pages, {n_img} images wired -> {os.path.relpath(out, REPO)}/")


def main():
    with open(os.path.join(CONTENT, "opl.json")) as f:
        opl = json.load(f)
    with open(os.path.join(CONTENT, "huskies.json")) as f:
        huskies = json.load(f)
    print("Building static sites...")
    write_site("opl", opl, build_opl(opl))
    write_site("huskies", huskies, build_huskies(huskies))
    print("Done.")


if __name__ == "__main__":
    main()
