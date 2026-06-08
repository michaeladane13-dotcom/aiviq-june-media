#!/usr/bin/env python3
"""Static site generator for the Overseas Premier League and Vancouver Huskies sites.

Two fully independent static sites, each rendered to its own output folder so each
deploys to its own domain. Pure standard library -- no dependencies, no client-side
rendering. Run `python3 build.py` to regenerate the static HTML.

Images: drop client files into site-builder/assets/<opl|huskies|aiviq>/ using the
exact filenames from the brief. When a file is present the builder emits a real <img>;
when it is absent it emits a clearly labelled placeholder slot naming the missing file.

To update events, emails, the Square link, domains, or socials: edit content/*.json
and re-run this script. The generated HTML in opl-site/ and huskies-site/ is hosted.
"""
import json
import os
import shutil
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
CONTENT = os.path.join(ROOT, "content")
ASSETS = os.path.join(ROOT, "assets")
OUT = {"opl": os.path.join(REPO, "opl-site"), "huskies": os.path.join(REPO, "huskies-site")}

AIVIQ_CREDIT = "Aiviq Enterprises Inc."
YEAR = 2026

# Filenames that exist on disk and must be copied into the output assets/img folder.
_to_copy = {"opl": set(), "huskies": set()}
_aiviq_logo_present = os.path.isfile(os.path.join(ASSETS, "aiviq", "aiviq-enterprises.png"))


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# --------------------------------------------------------------------------- #
# Reusable components
# --------------------------------------------------------------------------- #
def media(key, filename, caption, ratio="4 / 3"):
    """Real <img> if the source file exists, else a labelled placeholder slot."""
    src = os.path.join(ASSETS, key, filename)
    if os.path.isfile(src):
        _to_copy[key].add(filename)
        return (f'<figure class="media"><img src="assets/img/{esc(filename)}" '
                f'alt="{esc(caption)}" loading="lazy"></figure>')
    return (f'<div class="photo-slot" style="aspect-ratio:{ratio}">'
            f'<span class="tag">Asset pending</span>'
            f'<span class="label">{esc(caption)}</span>'
            f'<span class="fname">{esc(filename)}</span></div>')


def logo_slot(text, light=False):
    cls = "logo-slot light" if light else "logo-slot"
    return f'<div class="{cls}"><span class="tag">Logo pending</span><span>{esc(text)}</span></div>'


def dev_note(text):
    return (f'<div class="dev-note"><strong>Dev note &mdash; client review:</strong> '
            f'{esc(text)}</div>')


def social_icons(socials):
    """Footer social row. Live link if a URL is set, else a labelled pending chip."""
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


# ---- Brand marks (SVG) -------------------------------------------------------
# OPL logo recreated as SVG from the client description: globe with a white "O" cut
# out, basketball seam lines on the globe, a red plane circling the O, blue & red on
# white. Used in the nav (compact) until the IMG_2090 file is supplied.
def opl_mark(key):
    f = os.path.join(ASSETS, key, "IMG_2090.png")
    if os.path.isfile(f):
        _to_copy[key].add("IMG_2090.png")
        return '<img class="mark" src="assets/img/IMG_2090.png" alt="Overseas Premier League logo">'
    return """<svg class="mark" viewBox="0 0 64 64" role="img" aria-label="Overseas Premier League logo">
  <defs><clipPath id="g"><circle cx="32" cy="32" r="24"/></clipPath></defs>
  <circle cx="32" cy="32" r="24" fill="#1c4fa0"/>
  <g clip-path="url(#g)" fill="none" stroke="#bcd2f2" stroke-width="1.3" opacity=".8">
    <ellipse cx="32" cy="32" rx="11" ry="24"/><line x1="8" y1="32" x2="56" y2="32"/>
    <path d="M10 21H54 M10 43H54"/>
  </g>
  <g clip-path="url(#g)" fill="none" stroke="#c8102e" stroke-width="1.7">
    <path d="M32 8V56"/><path d="M12 15Q32 26 52 15"/><path d="M12 49Q32 38 52 49"/>
  </g>
  <circle cx="32" cy="32" r="24" fill="none" stroke="#c8102e" stroke-width="3.4"/>
  <circle cx="32" cy="32" r="9.5" fill="#ffffff"/><circle cx="32" cy="32" r="6" fill="#1c4fa0"/>
  <path d="M23 39 L42 24 l2.6 .8 -7.6 7.6 5 .9 2.6 -1.7 1.7 .9 -3.4 3.4 -4.3 4.3 -.9 -1.7 .9 -2.6 -.9 -5z" fill="#c8102e"/>
</svg>"""


# Larger OPL lockup for the hero (globe mark + wordmark with red rule lines).
def opl_hero_lockup(key):
    f = os.path.join(ASSETS, key, "IMG_2090.png")
    if os.path.isfile(f):
        _to_copy[key].add("IMG_2090.png")
        return '<img class="hero-logo" src="assets/img/IMG_2090.png" alt="Overseas Premier League logo">'
    return f"""<div class="hero-logo-lockup">
  <div class="hl-mark">{opl_mark(key)}</div>
  <div class="hl-word">
    <span class="hl-rule"></span>
    <strong>OVERSEAS PREMIER LEAGUE</strong>
    <span class="hl-rule"></span>
  </div>
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
        return f'<img class="aiviq-logo" src="assets/img/aiviq-enterprises.png" alt="Aiviq Enterprises Inc.">'
    return f'<span class="aiviq-fallback">{AIVIQ_MARK}<span>Built by <strong>Aiviq Enterprises Inc.</strong></span></span>'


# --------------------------------------------------------------------------- #
# Header / footer / page shell
# --------------------------------------------------------------------------- #
def header(cfg, active, mark):
    parts = []
    for l in cfg["nav"]:
        cls = ' class="active"' if l["href"] == active else ""
        parts.append(f'<a href="{esc(l["href"])}"{cls}>{esc(l["label"])}</a>')
    links = "".join(parts)
    return f"""<header class="site-header">
  <div class="container nav">
    <a class="brand" href="index.html">
      {mark}
      <span class="brand-text"><strong>{esc(cfg['site_name'])}</strong><span>{esc(cfg['short_name'])}</span></span>
    </a>
    <button class="nav-toggle" aria-label="Open menu">&#9776;</button>
    <nav class="nav-links">{links}</nav>
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
        <p>{esc(cfg['tagline'])}</p>
        <p class="pending-text">Domain pending: {esc(cfg['domain_placeholder'])}</p>
      </div>
      <div>
        <h4>Explore</h4>
        {nav_links}
      </div>
      <div>
        <h4>Contact</h4>
        {contact_html}
        {social_icons(cfg.get('socials', {}))}
      </div>
    </div>
    <div class="aiviq-credit">
      {aiviq_credit()}
      <span>&copy; {YEAR} {esc(cfg['site_name'])}. All rights reserved.</span>
    </div>
  </div>
</footer>"""


def menu_js():
    return ("<script>document.querySelectorAll('.nav-toggle').forEach(function(b){"
            "b.addEventListener('click',function(){document.querySelector('.nav-links')"
            ".classList.toggle('open');});});</script>")


def page(cfg, mark, *, slug, title, description, body, active):
    if title == cfg["site_name"]:
        full_title = f"{cfg['site_name']} — {cfg['tagline']}"
    else:
        full_title = f"{title} | {cfg['site_name']}"
    return f"""<!DOCTYPE html>
<html lang="en">
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
        cta = ('<a class="btn btn-ghost-navy btn-sm pending-btn" href="#" onclick="return false;">'
               'Register / RSVP <em>(link pending)</em></a>') if with_cta else ""
        cards.append(f"""<article class="event-card">
  <div class="date">{chip}</div>
  <div class="event-body">
    <h3>{esc(ev['name'])}</h3>
    <p class="event-meta">{esc(ev['date_display'])} &middot; {esc(ev['location'])}</p>
    <p>{esc(ev['description'])}</p>
    {cta}
  </div>
</article>""")
    return '<div class="event-grid">' + "\n".join(cards) + "</div>"


# --------------------------------------------------------------------------- #
# OPL site
# --------------------------------------------------------------------------- #
def build_opl(cfg):
    mark = opl_mark("opl")
    pages = {}

    partner_strip = """<section class="partner-strip">
  <div class="container">
    <p class="ps-title">Official Player Placement Partner: <strong>Valletta BC</strong></p>
    <p class="ps-sub">Delivered via Direct Player Placement, Overseas Tours, and the North American Scouting Combine.</p>
  </div>
</section>"""

    # ---- Page 1: Home ----
    home = f"""<section class="hero">
  <div class="container hero-inner">
    {opl_hero_lockup('opl')}
    <span class="eyebrow">FIBA Licensed &middot; EuroBasket Eligible</span>
    <h1>Your Path to Professional Basketball Overseas</h1>
    <p class="lead">OPL connects North American players with FIBA licensed professional teams in Europe. FIBA Licensed. EuroBasket Eligible.</p>
    <div class="cta-row">
      <a class="btn btn-primary btn-lg" href="events.html">View Upcoming Events</a>
      <a class="btn btn-ghost btn-lg" href="placement.html">Learn About Player Placement</a>
    </div>
  </div>
</section>
{partner_strip}
<section>
  <div class="container">
    <div class="section-head">
      <span class="kicker">How we place players</span>
      <h2>Three routes to the overseas game</h2>
    </div>
    <div class="grid cols-3">
      <div class="card"><span class="num">01</span><h3>Direct Player Placement</h3><p>Sign directly with a professional men's team in Malta through our Valletta BC partnership.</p></div>
      <div class="card"><span class="num">02</span><h3>Overseas Tours</h3><p>Structured overseas trips that put players inside live professional training and competition.</p></div>
      <div class="card"><span class="num">03</span><h3>North American Scouting Combine</h3><p>Scouted combine events that identify and develop players for overseas placement.</p></div>
    </div>
  </div>
</section>
<section class="dark">
  <div class="container">
    <div class="banner">
      <h2>Ready to take your game overseas?</h2>
      <p>Explore the Malta player placement package and the overseas training camp.</p>
      <a class="btn btn-gold btn-lg" href="placement.html">Learn About Player Placement</a>
    </div>
  </div>
</section>"""
    pages["index.html"] = page(cfg, mark, slug="", title=cfg["site_name"],
        description="OPL connects North American players with FIBA licensed professional teams in Europe. FIBA Licensed. EuroBasket Eligible.",
        body=home, active="index.html")

    # ---- Page 2: About / Partnership ----
    about = f"""<section class="page-hero">
  <div class="container">
    <span class="eyebrow">About / Partnership</span>
    <h1>An official player placement partner</h1>
  </div>
</section>
<section>
  <div class="container split">
    <div class="prose">
      <span class="kicker">The partnership</span>
      <h2>Valletta BC &times; OPL</h2>
      <p>The Valletta BC partnership is a formal partnership that makes the Overseas Premier League an official player placement partner.</p>
      <p>The partnership is delivered through three mechanisms:</p>
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
<section class="dark">
  <div class="container"><div class="banner">
    <h2>See how placement works</h2>
    <p>Direct placement, overseas tours, and the scouting combine all feed the overseas pathway.</p>
    <a class="btn btn-gold btn-lg" href="placement.html">View Player Placement</a>
  </div></div>
</section>"""
    pages["about.html"] = page(cfg, mark, slug="about.html", title="About / Partnership",
        description="The Valletta BC partnership makes the Overseas Premier League an official player placement partner, delivered via direct placement, overseas tours, and a North American scouting combine.",
        body=about, active="about.html")

    # ---- Page 3: Player Placement ----
    placement = f"""<section class="page-hero">
  <div class="container">
    <span class="eyebrow">Player Placement</span>
    <h1>Two ways to reach the professional game</h1>
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
          <p>Directly join a professional men's team in Malta. FIBA Licensed. EuroBasket Eligible.</p>
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
          <p>Professional men's training camp in Malta. Compete in front of team owners and executives. Opportunities to sign with 1st or 2nd Division.</p>
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
<section class="dark">
  <div class="container"><div class="banner">
    <h2>Passport ready?</h2>
    <p>See upcoming camps and league dates.</p>
    <a class="btn btn-gold btn-lg" href="events.html">View Events</a>
  </div></div>
</section>"""
    pages["placement.html"] = page(cfg, mark, slug="placement.html", title="Player Placement",
        description="Overseas player placement package and overseas training camp in Malta. FIBA Licensed, EuroBasket Eligible. Perks include FIBA & MBA registration, VISA, housing, transport, and a media package.",
        body=placement, active="placement.html")

    # ---- Page 4: Events ----
    events = f"""<section class="page-hero">
  <div class="container">
    <span class="eyebrow">Events</span>
    <h1>Upcoming OPL events</h1>
  </div>
</section>
<section>
  <div class="container">
    {event_cards(cfg['events'], with_cta=True)}
  </div>
</section>"""
    pages["events.html"] = page(cfg, mark, slug="events.html", title="Events",
        description="OPL 2026 events: Overseas Training Camp (Sept 21-28, Malta), Summer League (July 5), and the League Combine (TBD).",
        body=events, active="events.html")

    # ---- Page 5: Contact ----
    contact = f"""<section class="page-hero">
  <div class="container">
    <span class="eyebrow">Contact</span>
    <h1>Get in touch</h1>
  </div>
</section>
<section>
  <div class="container split">
    <div class="prose">
      <span class="kicker">Reach the team</span>
      <h2>Contact OPL</h2>
      <p><strong>Email:</strong> <span class="pending-text">Pending from client</span></p>
      {dev_note('OPL contact email address is pending from the client. Add it to content/opl.json (contact_email) and rebuild.')}
      <p>Follow OPL on social — links coming soon.</p>
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
# Huskies site
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
    <p class="ps-title">Official OPL Development League Partner</p>
    <p class="ps-sub"><a href="{esc(opl_url)}" target="_blank" rel="noopener">Visit the Overseas Premier League &rarr;</a>
    <span class="pending-text">(OPL domain pending)</span></p>
  </div>
</section>"""

    # ---- Page 1: Home ----
    gallery = "".join(media("huskies", g["file"], g["caption"]) for g in cfg["gallery"])
    home = f"""<section class="hero hero-huskies">
  <div class="container hero-inner">
    <div class="hero-logo-slot">{logo_slot('Vancouver Huskies wolf logo')}</div>
    <h1>Vancouver Huskies Basketball</h1>
    <p class="lead">Competing at the highest level of North American development basketball. Affiliated with the Overseas Premier League.</p>
    <div class="cta-row">
      <a class="btn btn-primary btn-lg" href="signup.html">Sign Up &amp; Pay</a>
    </div>
  </div>
</section>
{partner_strip}
<section id="gallery">
  <div class="container">
    <div class="section-head">
      <span class="kicker">The team</span>
      <h2>On the floor</h2>
    </div>
    <div class="gallery-grid">{gallery}</div>
  </div>
</section>
<section class="dark">
  <div class="container"><div class="banner">
    <h2>Join the Huskies</h2>
    <p>Register and pay through the Vancouver Huskies Square account.</p>
    {square_btn}
  </div></div>
</section>"""
    pages["index.html"] = page(cfg, mark, slug="", title=cfg["site_name"],
        description="Vancouver Huskies Basketball — competing at the highest level of North American development basketball. Affiliated with the Overseas Premier League.",
        body=home, active="index.html")

    # ---- Page 2: Events ----
    events = f"""<section class="page-hero">
  <div class="container">
    <span class="eyebrow">Events</span>
    <h1>Huskies schedule</h1>
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
        description="Vancouver Huskies events: OPL Overseas Training Camp (Sept 21-28), OPL Summer League (July 5), OPL League Combine (TBD), plus local Huskies events.",
        body=events, active="events.html")

    # ---- Page 3: Sign Up & Pay ----
    sp = cfg.get("signup_photo", {"file": "IMG_2081.png", "caption": "Vancouver Huskies"})
    signup = f"""<section class="page-hero">
  <div class="container">
    <span class="eyebrow">Sign Up &amp; Pay</span>
    <h1>Join the Huskies</h1>
  </div>
</section>
<section>
  <div class="container split">
    <div class="prose">
      <span class="kicker">Registration</span>
      <h2>Register and pay via Square</h2>
      <p>Players register and pay via Square. Invoices are issued through the Vancouver Huskies Square account.</p>
      <p style="margin:1.6rem 0">{square_btn}</p>
      {dev_note('Square payment link is pending from the client. Set "square_link" in content/huskies.json and rebuild — the button switches to the real checkout automatically.') if square_pending else ''}
      <p><strong>Contact:</strong> <a href="mailto:{esc(cfg['contact_email'])}">{esc(cfg['contact_email'])}</a></p>
    </div>
    <div>{media('huskies', sp['file'], sp['caption'], ratio='3 / 4')}</div>
  </div>
</section>"""
    pages["signup.html"] = page(cfg, mark, slug="signup.html", title="Sign Up & Pay",
        description="Join the Vancouver Huskies. Players register and pay via Square through the Vancouver Huskies Square account.",
        body=signup, active="signup.html")

    return pages


# --------------------------------------------------------------------------- #
# CSS
# --------------------------------------------------------------------------- #
def css(theme):
    t = theme
    return f""":root {{
  --navy: {t['navy']}; --navy-deep: {t['navy_deep']}; --red: {t['red']};
  --white: {t['white']}; --gold: {t['gold']}; --ink: #11203b; --muted: #c9d4e8;
  --line: rgba(255,255,255,.14);
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  color:var(--ink); background:var(--white); line-height:1.6; overflow-x:hidden; }}
a {{ color:var(--red); text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
img {{ max-width:100%; display:block; }}
.container {{ width:min(1120px,92vw); margin:0 auto; }}

.site-header {{ background:var(--navy-deep); border-bottom:3px solid var(--red); position:sticky; top:0; z-index:50; }}
.nav {{ display:flex; align-items:center; justify-content:space-between; gap:1rem; padding:.7rem 0; }}
.brand {{ display:flex; align-items:center; gap:.65rem; color:var(--white); }}
.brand:hover {{ text-decoration:none; }}
.brand .mark {{ width:46px; height:46px; flex:0 0 auto; border-radius:6px; }}
.brand .brand-text {{ display:flex; flex-direction:column; line-height:1.1; }}
.brand .brand-text strong {{ font-size:1.02rem; letter-spacing:.5px; }}
.brand .brand-text span {{ font-size:.7rem; color:var(--muted); letter-spacing:2px; text-transform:uppercase; }}
.nav-links {{ display:flex; gap:.25rem; flex-wrap:wrap; }}
.nav-links a {{ color:var(--muted); padding:.5rem .8rem; border-radius:6px; font-weight:600; font-size:.92rem; }}
.nav-links a:hover {{ color:var(--white); background:rgba(255,255,255,.08); text-decoration:none; }}
.nav-links a.active {{ color:var(--white); background:var(--red); }}
.nav-toggle {{ display:none; }}

.hero {{ background:radial-gradient(1200px 500px at 80% -10%, rgba(200,16,46,.45), transparent 60%),
  linear-gradient(160deg,var(--navy) 0%,var(--navy-deep) 100%); color:var(--white); position:relative; overflow:hidden; }}
.hero::after {{ content:""; position:absolute; inset:0;
  background-image:repeating-linear-gradient(90deg,rgba(255,255,255,.04) 0 2px,transparent 2px 60px); pointer-events:none; }}
.hero-inner {{ padding:4.5rem 0 4rem; position:relative; z-index:1; max-width:780px; }}
.hero h1 {{ font-size:clamp(2.1rem,5vw,3.6rem); line-height:1.06; margin:.4rem 0 1rem; text-transform:uppercase; letter-spacing:.5px; overflow-wrap:break-word; }}
.hero p.lead {{ font-size:clamp(1.05rem,2.2vw,1.3rem); color:var(--muted); margin:0 0 1.8rem; }}
.eyebrow {{ display:inline-block; text-transform:uppercase; letter-spacing:3px; font-size:.72rem; font-weight:700;
  color:var(--gold); border:1px solid var(--gold); border-radius:999px; padding:.35rem .8rem; margin-bottom:1rem; }}
.hero-logo {{ max-height:96px; width:auto; margin-bottom:1.2rem; }}
.hero-logo-lockup {{ display:inline-flex; align-items:center; gap:1rem; margin-bottom:1.4rem; max-width:100%; flex-wrap:wrap;
  background:rgba(255,255,255,.06); border:1px solid var(--line); padding:.8rem 1.2rem; border-radius:12px; }}
.hero-logo-lockup .mark {{ width:64px; height:64px; }}
.hl-word {{ display:flex; flex-direction:column; align-items:flex-start; gap:.35rem; min-width:0; }}
.hl-word strong {{ color:var(--white); letter-spacing:2px; font-size:clamp(.72rem,2.6vw,.95rem); overflow-wrap:break-word; }}
.hl-rule {{ display:block; height:3px; width:100%; background:var(--red); border-radius:2px; }}
.hero-logo-slot {{ max-width:240px; margin-bottom:1.4rem; }}

.cta-row {{ display:flex; gap:.8rem; flex-wrap:wrap; }}
.btn {{ display:inline-block; font-weight:700; letter-spacing:.4px; padding:.85rem 1.5rem; border-radius:8px;
  border:2px solid transparent; cursor:pointer; font-size:1rem; }}
.btn-primary {{ background:var(--red); color:var(--white); }}
.btn-primary:hover {{ background:#a50d26; text-decoration:none; }}
.btn-ghost {{ background:transparent; color:var(--white); border-color:rgba(255,255,255,.5); }}
.btn-ghost:hover {{ border-color:var(--white); text-decoration:none; }}
.btn-ghost-navy {{ background:transparent; color:var(--navy); border-color:var(--navy); }}
.btn-ghost-navy:hover {{ background:var(--navy); color:var(--white); text-decoration:none; }}
.btn-gold {{ background:var(--gold); color:var(--navy-deep); }}
.btn-gold:hover {{ filter:brightness(1.07); text-decoration:none; }}
.btn-lg {{ padding:1.05rem 2rem; font-size:1.1rem; }}
.btn-sm {{ padding:.55rem 1rem; font-size:.9rem; }}
.pending-btn {{ opacity:.92; outline:2px dashed var(--gold); outline-offset:3px; cursor:not-allowed; }}
.pending-btn em {{ font-style:normal; font-weight:600; font-size:.8em; opacity:.85; }}

section {{ padding:4rem 0; }}
.page-hero {{ background:linear-gradient(160deg,var(--navy) 0%,var(--navy-deep) 100%); color:var(--white); padding:3rem 0; }}
.page-hero h1 {{ font-size:clamp(1.8rem,4vw,2.8rem); margin:.3rem 0 0; text-transform:uppercase; letter-spacing:.5px; }}
.page-hero .lead {{ color:var(--muted); margin:.8rem 0 0; max-width:640px; }}
.section-head {{ max-width:760px; margin-bottom:2.2rem; }}
.section-head h2 {{ font-size:clamp(1.6rem,3.5vw,2.4rem); color:var(--navy); margin:.2rem 0 .6rem; }}
.section-head .kicker, .prose .kicker {{ text-transform:uppercase; letter-spacing:3px; font-size:.72rem; font-weight:700; color:var(--red); }}
.section-head p {{ color:#46546e; font-size:1.05rem; }}
.alt {{ background:#f4f6fb; }}
.dark {{ background:var(--navy); color:var(--white); }}
.dark h2 {{ color:var(--white); }}

.partner-strip {{ background:var(--red); color:var(--white); padding:1.4rem 0; text-align:center; }}
.partner-strip .ps-title {{ margin:0; font-size:1.15rem; font-weight:700; letter-spacing:.3px; text-transform:uppercase; }}
.partner-strip .ps-sub {{ margin:.3rem 0 0; color:#ffe2e7; font-size:.95rem; }}
.partner-strip a {{ color:#fff; text-decoration:underline; }}

.grid {{ display:grid; gap:1.25rem; }}
.cols-2 {{ grid-template-columns:repeat(2,1fr); }}
.cols-3 {{ grid-template-columns:repeat(3,1fr); }}
.card {{ background:var(--white); border:1px solid #e4e8f1; border-radius:12px; padding:1.5rem; box-shadow:0 1px 2px rgba(11,35,73,.05); }}
.card h3 {{ margin:.3rem 0 .5rem; color:var(--navy); font-size:1.2rem; }}
.card .num {{ color:var(--red); font-weight:800; font-size:.9rem; letter-spacing:2px; }}

.checks {{ list-style:none; padding:0; margin:.6rem 0 1rem; display:grid; gap:.6rem; }}
.checks li {{ position:relative; padding-left:2rem; }}
.checks li::before {{ content:""; position:absolute; left:0; top:.35em; width:1.1rem; height:1.1rem; border-radius:50%; background:var(--red);
  -webkit-mask:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M20 6L9 17l-5-5' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/></svg>") center/80% no-repeat;
  mask:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M20 6L9 17l-5-5' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/></svg>") center/80% no-repeat; }}
.must {{ font-weight:700; color:var(--navy); }}

/* offer cards */
.offer-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; }}
.offer-card {{ border:1px solid #e4e8f1; border-radius:14px; overflow:hidden; background:var(--white); display:flex; flex-direction:column; }}
.offer-card .offer-body {{ padding:1.5rem; }}
.offer-card h2 {{ color:var(--navy); margin:.2rem 0 .5rem; font-size:1.4rem; }}
.offer-card h3 {{ color:var(--red); font-size:.85rem; text-transform:uppercase; letter-spacing:1.5px; margin:1.1rem 0 .2rem; }}

/* events */
.event-grid {{ display:grid; gap:1.1rem; }}
.event-card {{ display:grid; grid-template-columns:110px 1fr; gap:1.25rem; align-items:start;
  border:1px solid #e4e8f1; border-radius:12px; padding:1.25rem; background:var(--white); }}
.event-card .date {{ text-align:center; background:var(--navy); color:var(--white); border-radius:10px; padding:1rem .5rem; font-weight:800; font-size:1.5rem; line-height:1; }}
.event-card .date .d {{ display:block; font-size:.8rem; color:var(--gold); letter-spacing:.5px; margin-bottom:.2rem; }}
.event-card h3 {{ margin:0 0 .2rem; color:var(--navy); font-size:1.25rem; }}
.event-card .event-meta {{ margin:0 0 .5rem; color:var(--red); font-weight:600; font-size:.9rem; }}
.event-card p {{ margin:0 0 .6rem; color:#51607a; font-size:.95rem; }}

/* media + placeholder slots */
.media {{ margin:0; }}
.media img {{ width:100%; height:100%; object-fit:cover; border-radius:12px; }}
.offer-card .media img {{ border-radius:0; }}
.gallery-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; }}
.photo-slot {{ position:relative; aspect-ratio:4/3; border-radius:12px; overflow:hidden;
  background:repeating-linear-gradient(45deg,#e9edf5 0 14px,#f3f6fb 14px 28px); border:1px solid #dbe1ec;
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:.3rem; color:#5a667e; text-align:center; padding:1rem; }}
.photo-slot .tag {{ position:absolute; top:.6rem; left:.6rem; background:var(--navy); color:var(--white);
  font-size:.62rem; letter-spacing:1.5px; text-transform:uppercase; padding:.25rem .55rem; border-radius:4px; font-weight:700; }}
.photo-slot .label {{ font-weight:700; font-size:.95rem; color:#3c4a63; }}
.photo-slot .fname {{ font-size:.78rem; color:#7b879c; font-family:ui-monospace,Menlo,Consolas,monospace; }}

/* logo slot */
.logo-slot {{ position:relative; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;
  border:2px dashed rgba(201,166,74,.7); border-radius:12px; background:rgba(255,255,255,.04); color:var(--gold);
  min-height:140px; padding:1.4rem 1rem; font-weight:700; gap:.3rem; }}
.logo-slot .tag {{ position:absolute; top:.6rem; left:.6rem; background:var(--gold); color:var(--navy-deep);
  font-size:.62rem; letter-spacing:1.5px; text-transform:uppercase; padding:.25rem .55rem; border-radius:4px; }}
.logo-slot.light {{ background:#eef1f7; border-color:#c4ccdb; color:#7b879c; }}

/* dev note */
.dev-note {{ background:repeating-linear-gradient(45deg,#fff6e6 0 12px,#fdeecb 12px 24px);
  border:1.5px dashed var(--red); color:#5a4304; border-radius:10px; padding:.85rem 1.1rem; font-size:.9rem; margin:1.2rem 0; }}
.dev-note strong {{ color:var(--red); }}

/* banner */
.banner {{ background:linear-gradient(135deg,var(--navy) 0%,var(--navy-deep) 100%); color:var(--white);
  border-radius:16px; padding:2.5rem; text-align:center; border:1px solid var(--line); }}
.banner h2 {{ color:var(--white); margin-top:0; }}
.banner p {{ color:var(--muted); max-width:560px; margin:0 auto 1.4rem; }}

/* split */
.split {{ display:grid; grid-template-columns:1fr 1fr; gap:2.5rem; align-items:center; }}
.prose h2 {{ color:var(--navy); }}

/* footer */
.site-footer {{ background:var(--navy-deep); color:var(--muted); padding:3rem 0 2rem; }}
.footer-grid {{ display:grid; grid-template-columns:2fr 1fr 1.2fr; gap:2rem; }}
.footer-grid h4 {{ color:var(--white); font-size:.82rem; letter-spacing:1.5px; text-transform:uppercase; margin:0 0 .8rem; }}
.footer-grid a {{ color:var(--muted); display:block; padding:.15rem 0; }}
.footer-grid a:hover {{ color:var(--white); }}
.pending-text {{ color:#8c99b3; font-style:italic; }}
.social-row {{ display:flex; align-items:center; gap:.5rem; margin-top:.8rem; flex-wrap:wrap; }}
.soc {{ display:inline-flex; width:34px; height:34px; align-items:center; justify-content:center; border-radius:8px;
  background:rgba(255,255,255,.08); }}
.soc svg {{ width:18px; height:18px; fill:var(--muted); }}
.soc:hover svg {{ fill:var(--white); }}
.soc.pending {{ opacity:.5; outline:1px dashed var(--gold); cursor:not-allowed; }}
.soc-note {{ font-size:.78rem; color:#8c99b3; font-style:italic; }}
.aiviq-credit {{ margin-top:2.5rem; padding-top:1.5rem; border-top:1px solid var(--line);
  display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap; font-size:.85rem; }}
.aiviq-logo {{ height:40px; width:auto; }}
.aiviq-fallback {{ display:flex; align-items:center; gap:.5rem; color:var(--gold); }}
.aiviq-fallback svg {{ width:22px; height:22px; }}
.aiviq-fallback strong {{ color:var(--gold); }}

@media (max-width:860px) {{
  .cols-2,.cols-3,.footer-grid,.split,.offer-grid {{ grid-template-columns:1fr; }}
  .gallery-grid {{ grid-template-columns:repeat(2,1fr); }}
  .nav-links {{ display:none; position:absolute; top:100%; left:0; right:0; background:var(--navy-deep);
    flex-direction:column; padding:.5rem 5vw 1rem; gap:.2rem; border-bottom:3px solid var(--red); }}
  .nav-links.open {{ display:flex; }}
  .nav-toggle {{ display:inline-flex; background:transparent; border:1px solid var(--line); color:var(--white);
    border-radius:8px; padding:.5rem .7rem; cursor:pointer; font-size:1rem; }}
}}
@media (max-width:520px) {{
  .gallery-grid {{ grid-template-columns:1fr; }}
  .event-card {{ grid-template-columns:1fr; }}
  .event-card .date {{ width:90px; }}
}}
"""


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def write_site(key, cfg, pages):
    out = OUT[key]
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "assets", "css"), exist_ok=True)
    with open(os.path.join(out, "assets", "css", "styles.css"), "w") as f:
        f.write(css(cfg["theme"]))
    # copy any present image assets
    if _to_copy[key] or _aiviq_logo_present:
        img_out = os.path.join(out, "assets", "img")
        os.makedirs(img_out, exist_ok=True)
        for fn in _to_copy[key]:
            shutil.copy(os.path.join(ASSETS, key, fn), os.path.join(img_out, fn))
        if _aiviq_logo_present:
            shutil.copy(os.path.join(ASSETS, "aiviq", "aiviq-enterprises.png"),
                        os.path.join(img_out, "aiviq-enterprises.png"))
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
