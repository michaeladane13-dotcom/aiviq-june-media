#!/usr/bin/env python3
"""Static site generator for the Overseas Premier League and Vancouver Huskies sites.

Two fully independent static sites, each rendered to its own output folder so each
can be deployed to its own domain. Pure standard library -- no dependencies, no
client-side rendering. Run `python3 build.py` to regenerate the static HTML.

To update event dates, contact emails, the Square link, or copy: edit the JSON in
content/ and re-run this script. The generated HTML in opl-site/ and huskies-site/
is what gets hosted.
"""
import json
import os
import shutil
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
CONTENT = os.path.join(ROOT, "content")
OUT = {"opl": os.path.join(REPO, "opl-site"), "huskies": os.path.join(REPO, "huskies-site")}

AIVIQ_CREDIT = "Built by Aiviq Enterprises Inc."
YEAR = 2026


# --------------------------------------------------------------------------- #
# Shared building blocks
# --------------------------------------------------------------------------- #
def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def css(theme):
    t = theme
    return f""":root {{
  --navy: {t['navy']};
  --navy-deep: {t['navy_deep']};
  --red: {t['red']};
  --white: {t['white']};
  --gold: {t['gold']};
  --ink: #11203b;
  --muted: #c9d4e8;
  --line: rgba(255,255,255,.14);
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: var(--ink);
  background: var(--white);
  line-height: 1.6;
}}
a {{ color: var(--red); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
img {{ max-width: 100%; display: block; }}
.container {{ width: min(1120px, 92vw); margin: 0 auto; }}

/* Header / nav */
.site-header {{
  background: var(--navy-deep);
  border-bottom: 3px solid var(--red);
  position: sticky; top: 0; z-index: 50;
}}
.nav {{
  display: flex; align-items: center; justify-content: space-between;
  gap: 1rem; padding: .75rem 0;
}}
.brand {{ display: flex; align-items: center; gap: .65rem; color: var(--white); }}
.brand:hover {{ text-decoration: none; }}
.brand .mark {{ width: 46px; height: 46px; flex: 0 0 auto; }}
.brand .brand-text {{ display: flex; flex-direction: column; line-height: 1.1; }}
.brand .brand-text strong {{ font-size: 1.05rem; letter-spacing: .5px; }}
.brand .brand-text span {{ font-size: .72rem; color: var(--muted); letter-spacing: 2px; text-transform: uppercase; }}
.nav-links {{ display: flex; gap: .25rem; flex-wrap: wrap; }}
.nav-links a {{
  color: var(--muted); padding: .5rem .8rem; border-radius: 6px;
  font-weight: 600; font-size: .92rem; letter-spacing: .3px;
}}
.nav-links a:hover {{ color: var(--white); background: rgba(255,255,255,.08); text-decoration: none; }}
.nav-links a.active {{ color: var(--white); background: var(--red); }}
.nav-toggle {{ display: none; }}

/* Hero */
.hero {{
  background:
    radial-gradient(1200px 500px at 80% -10%, rgba(200,16,46,.45), transparent 60%),
    linear-gradient(160deg, var(--navy) 0%, var(--navy-deep) 100%);
  color: var(--white);
  position: relative; overflow: hidden;
}}
.hero::after {{
  content: ""; position: absolute; inset: 0;
  background-image: repeating-linear-gradient(90deg, rgba(255,255,255,.04) 0 2px, transparent 2px 60px);
  pointer-events: none;
}}
.hero-inner {{ padding: 5rem 0 4.5rem; position: relative; z-index: 1; max-width: 760px; }}
.hero h1 {{ font-size: clamp(2.1rem, 5vw, 3.5rem); line-height: 1.07; margin: .2rem 0 1rem; }}
.hero p.lead {{ font-size: clamp(1.05rem, 2.2vw, 1.3rem); color: var(--muted); margin: 0 0 1.8rem; }}
.eyebrow {{
  display: inline-block; text-transform: uppercase; letter-spacing: 3px;
  font-size: .72rem; font-weight: 700; color: var(--gold);
  border: 1px solid var(--gold); border-radius: 999px; padding: .35rem .8rem; margin-bottom: 1rem;
}}
.cta-row {{ display: flex; gap: .8rem; flex-wrap: wrap; }}
.btn {{
  display: inline-block; font-weight: 700; letter-spacing: .4px;
  padding: .85rem 1.5rem; border-radius: 8px; border: 2px solid transparent;
  cursor: pointer; font-size: 1rem;
}}
.btn-primary {{ background: var(--red); color: var(--white); }}
.btn-primary:hover {{ background: #a50d26; text-decoration: none; }}
.btn-ghost {{ background: transparent; color: var(--white); border-color: rgba(255,255,255,.5); }}
.btn-ghost:hover {{ border-color: var(--white); text-decoration: none; }}
.btn-gold {{ background: var(--gold); color: var(--navy-deep); }}
.btn-gold:hover {{ filter: brightness(1.07); text-decoration: none; }}
.btn-lg {{ padding: 1.05rem 2rem; font-size: 1.1rem; }}

/* Sections */
section {{ padding: 4rem 0; }}
.section-head {{ max-width: 760px; margin-bottom: 2.2rem; }}
.section-head h2 {{ font-size: clamp(1.6rem, 3.5vw, 2.4rem); color: var(--navy); margin: .2rem 0 .6rem; }}
.section-head .kicker {{ text-transform: uppercase; letter-spacing: 3px; font-size: .72rem; font-weight: 700; color: var(--red); }}
.section-head p {{ color: #46546e; font-size: 1.05rem; }}
.alt {{ background: #f4f6fb; }}
.dark {{ background: var(--navy); color: var(--white); }}
.dark h2 {{ color: var(--white); }}
.dark .section-head p {{ color: var(--muted); }}

/* Grid + cards */
.grid {{ display: grid; gap: 1.25rem; }}
.cols-2 {{ grid-template-columns: repeat(2, 1fr); }}
.cols-3 {{ grid-template-columns: repeat(3, 1fr); }}
.card {{
  background: var(--white); border: 1px solid #e4e8f1; border-radius: 12px;
  padding: 1.5rem; box-shadow: 0 1px 2px rgba(11,35,73,.05);
}}
.card h3 {{ margin: .1rem 0 .5rem; color: var(--navy); font-size: 1.2rem; }}
.card .num {{ color: var(--red); font-weight: 800; font-size: .9rem; letter-spacing: 2px; }}
.dark .card {{ background: rgba(255,255,255,.05); border-color: var(--line); color: var(--muted); }}
.dark .card h3 {{ color: var(--white); }}

/* Perk / checklist */
.checks {{ list-style: none; padding: 0; margin: 0; display: grid; gap: .7rem; }}
.checks li {{ position: relative; padding-left: 2rem; }}
.checks li::before {{
  content: ""; position: absolute; left: 0; top: .35em;
  width: 1.1rem; height: 1.1rem; border-radius: 50%;
  background: var(--red);
  -webkit-mask: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M20 6L9 17l-5-5' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/></svg>") center / 80% no-repeat;
  mask: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M20 6L9 17l-5-5' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/></svg>") center / 80% no-repeat;
}}

/* Logo slot placeholder */
.logo-slot {{
  display: flex; align-items: center; justify-content: center; text-align: center;
  border: 2px dashed rgba(201,166,74,.7); border-radius: 12px;
  background: rgba(255,255,255,.04); color: var(--gold);
  min-height: 120px; padding: 1rem; font-size: .8rem; letter-spacing: 1px;
  text-transform: uppercase; font-weight: 700;
}}
.logo-slot.light {{ background: #eef1f7; border-color: #c4ccdb; color: #7b879c; }}

/* Image / photo slot placeholder */
.photo-slot {{
  position: relative; aspect-ratio: 4 / 3; border-radius: 12px; overflow: hidden;
  background:
    repeating-linear-gradient(45deg, #e9edf5 0 14px, #f3f6fb 14px 28px);
  border: 1px solid #dbe1ec; display: flex; align-items: center; justify-content: center;
  color: #6b7891; text-align: center; padding: 1rem;
}}
.photo-slot .tag {{
  position: absolute; top: .6rem; left: .6rem; background: var(--navy);
  color: var(--white); font-size: .65rem; letter-spacing: 1.5px; text-transform: uppercase;
  padding: .25rem .55rem; border-radius: 4px; font-weight: 700;
}}
.photo-slot .label {{ font-weight: 700; font-size: .95rem; }}

/* Events */
.event {{
  display: grid; grid-template-columns: 130px 1fr auto; gap: 1.25rem; align-items: center;
  padding: 1.25rem 0; border-bottom: 1px solid #e4e8f1;
}}
.event:last-child {{ border-bottom: none; }}
.event .date {{
  text-align: center; background: var(--navy); color: var(--white);
  border-radius: 10px; padding: .8rem .5rem; font-weight: 700;
}}
.event .date .d {{ display: block; font-size: .85rem; color: var(--gold); letter-spacing: .5px; }}
.event h3 {{ margin: 0 0 .25rem; color: var(--navy); font-size: 1.2rem; }}
.event p {{ margin: 0; color: #51607a; font-size: .95rem; }}
.pill {{
  display: inline-block; font-size: .7rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1px; padding: .3rem .65rem; border-radius: 999px;
  background: rgba(200,16,46,.12); color: var(--red); white-space: nowrap;
}}

/* Banner / callout */
.banner {{
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-deep) 100%);
  color: var(--white); border-radius: 16px; padding: 2.5rem; text-align: center;
  border: 1px solid var(--line);
}}
.banner h2 {{ color: var(--white); margin-top: 0; }}
.banner p {{ color: var(--muted); max-width: 560px; margin: 0 auto 1.4rem; }}

/* Footer */
.site-footer {{ background: var(--navy-deep); color: var(--muted); padding: 3rem 0 2rem; }}
.footer-grid {{ display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 2rem; }}
.footer-grid h4 {{ color: var(--white); font-size: .85rem; letter-spacing: 1.5px; text-transform: uppercase; margin: 0 0 .8rem; }}
.footer-grid a {{ color: var(--muted); display: block; padding: .15rem 0; }}
.footer-grid a:hover {{ color: var(--white); }}
.aiviq-credit {{
  margin-top: 2.5rem; padding-top: 1.5rem; border-top: 1px solid var(--line);
  display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
  font-size: .85rem;
}}
.aiviq-credit .gold {{ color: var(--gold); font-weight: 700; letter-spacing: .5px; display: flex; align-items: center; gap: .5rem; }}
.aiviq-credit .gold svg {{ width: 22px; height: 22px; }}

/* Notice (placeholder banner) */
.notice {{
  background: rgba(201,166,74,.14); border: 1px solid rgba(201,166,74,.5);
  color: #6a571f; border-radius: 10px; padding: .9rem 1.1rem; font-size: .9rem; margin-top: 1rem;
}}
.dark .notice {{ color: var(--gold); }}

/* Two-column prose */
.split {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2.5rem; align-items: center; }}
.prose h3 {{ color: var(--navy); }}
.dark .prose h3 {{ color: var(--white); }}

@media (max-width: 860px) {{
  .cols-2, .cols-3, .footer-grid, .split {{ grid-template-columns: 1fr; }}
  .nav-links {{
    display: none; position: absolute; top: 100%; left: 0; right: 0;
    background: var(--navy-deep); flex-direction: column; padding: .5rem 5vw 1rem; gap: .2rem;
    border-bottom: 3px solid var(--red);
  }}
  .nav-links.open {{ display: flex; }}
  .nav-toggle {{
    display: inline-flex; background: transparent; border: 1px solid var(--line);
    color: var(--white); border-radius: 8px; padding: .5rem .7rem; cursor: pointer; font-size: 1rem;
  }}
  .event {{ grid-template-columns: 90px 1fr; }}
  .event .pill {{ grid-column: 1 / -1; justify-self: start; }}
}}
"""


def menu_js():
    return (
        "<script>"
        "document.querySelectorAll('.nav-toggle').forEach(function(b){"
        "b.addEventListener('click',function(){"
        "document.querySelector('.nav-links').classList.toggle('open');});});"
        "</script>"
    )


# OPL mark recreated as SVG from the client's description: a globe forming an "O"
# with a white "O" cut out of the centre, basketball seam lines across the globe,
# a plane crossing it -- blue and red. (Final logo PENDING from client; this is a
# faithful stand-in built to the description.)
OPL_MARK = """<svg class="mark" viewBox="0 0 64 64" role="img" aria-label="Overseas Premier League logo">
  <defs>
    <clipPath id="oplGlobe"><circle cx="32" cy="32" r="27"/></clipPath>
  </defs>
  <!-- globe body -->
  <circle cx="32" cy="32" r="27" fill="#1c4fa0"/>
  <g clip-path="url(#oplGlobe)" fill="none" stroke="#bcd2f2" stroke-width="1.4" opacity=".85">
    <ellipse cx="32" cy="32" rx="13" ry="27"/>
    <line x1="5" y1="32" x2="59" y2="32"/>
    <path d="M7 20 H57 M7 44 H57"/>
  </g>
  <!-- basketball seam lines across the globe -->
  <g clip-path="url(#oplGlobe)" fill="none" stroke="#c8102e" stroke-width="1.8">
    <path d="M32 5 V59"/>
    <path d="M11 14 Q32 26 53 14"/>
    <path d="M11 50 Q32 38 53 50"/>
  </g>
  <!-- red ring forming the O -->
  <circle cx="32" cy="32" r="27" fill="none" stroke="#c8102e" stroke-width="3.5"/>
  <!-- white "O" cut out in the centre -->
  <circle cx="32" cy="32" r="11" fill="#ffffff"/>
  <circle cx="32" cy="32" r="7" fill="#1c4fa0"/>
  <!-- plane crossing -->
  <path d="M22 40 L44 24 l3 1 -9 9 6 1 3 -2 2 1 -4 4 -5 5 -1 -2 1 -3 -1 -6 -9 9z" fill="#ffffff" stroke="#0b2349" stroke-width=".6"/>
</svg>"""

# Placeholder Huskies mark: simple wolf head silhouette (navy/red/white).
HUSKIES_MARK = """<svg class="mark" viewBox="0 0 64 64" role="img" aria-label="Huskies logo placeholder">
  <circle cx="32" cy="32" r="29" fill="#c8102e"/>
  <circle cx="32" cy="32" r="25" fill="#0b2349"/>
  <path d="M16 22l6 8-3 12 13 8 13-8-3-12 6-8-9 4-7-6-7 6-9-4z" fill="#ffffff"/>
  <path d="M27 34l5 4 5-4-5-2-5 2z" fill="#c8102e"/>
  <circle cx="26" cy="30" r="1.8" fill="#0b2349"/>
  <circle cx="38" cy="30" r="1.8" fill="#0b2349"/>
</svg>"""

# Small Aiviq gold diamond mark for the footer credit.
AIVIQ_MARK = """<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2l7 10-7 10-7-10z" fill="#c9a64a"/><path d="M12 6l4.2 6L12 18 7.8 12z" fill="#0b2349"/></svg>"""


def logo_slot(text="League logo pending", light=False):
    cls = "logo-slot light" if light else "logo-slot"
    return f'<div class="{cls}">{esc(text)}</div>'


def photo_slot(label, tag="Photo pending"):
    return (
        f'<div class="photo-slot"><span class="tag">{esc(tag)}</span>'
        f'<span class="label">{esc(label)}</span></div>'
    )


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
    <button class="nav-toggle" aria-label="Menu">&#9776;</button>
    <nav class="nav-links">{links}</nav>
  </div>
</header>"""


def footer(cfg):
    nav_links = "".join(f'<a href="{esc(l["href"])}">{esc(l["label"])}</a>' for l in cfg["nav"])
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <h4>{esc(cfg['site_name'])}</h4>
        <p>{esc(cfg['tagline'])}</p>
        <p>Domain pending: <em>{esc(cfg['domain_placeholder'])}</em></p>
      </div>
      <div>
        <h4>Explore</h4>
        {nav_links}
      </div>
      <div>
        <h4>Contact</h4>
        <a href="mailto:{esc(cfg['contact_email'])}">{esc(cfg['contact_email'])}</a>
      </div>
    </div>
    <div class="aiviq-credit">
      <span class="gold">{AIVIQ_MARK}{esc(AIVIQ_CREDIT)}</span>
      <span>&copy; {YEAR} {esc(cfg['site_name'])}. All rights reserved.</span>
    </div>
  </div>
</footer>"""


def page(cfg, mark, *, slug, title, description, body, active):
    full_title = f"{title} | {cfg['site_name']}" if title != cfg["site_name"] else f"{cfg['site_name']} — {cfg['tagline']}"
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


def event_rows(events):
    rows = []
    for ev in events:
        if ev.get("date_iso"):
            dt = datetime.fromisoformat(ev["date_iso"])
            month = dt.strftime("%b").upper()
            day = dt.strftime("%d").lstrip("0")
        else:
            month, day = "TBD", "&middot;"
        rows.append(f"""<div class="event">
  <div class="date"><span class="d">{month}</span>{day}</div>
  <div>
    <h3>{esc(ev['name'])}</h3>
    <p>{esc(ev['date_display'])} &middot; {esc(ev['location'])} &mdash; {esc(ev['blurb'])}</p>
  </div>
  <span class="pill">{esc(ev['status'])}</span>
</div>""")
    return "\n".join(rows)


# --------------------------------------------------------------------------- #
# OPL pages
# --------------------------------------------------------------------------- #
def build_opl(cfg):
    mark = OPL_MARK
    pages = {}

    # ---- Home ----
    channels = "".join(
        f'<div class="card"><span class="num">0{i+1}</span><h3>{esc(c["title"])}</h3><p>{esc(c["detail"])}</p></div>'
        for i, c in enumerate(cfg["channels"])
    )
    home = f"""<section class="hero">
  <div class="container hero-inner">
    <span class="eyebrow">FIBA-Licensed &middot; EuroBasket Eligible</span>
    <h1>The overseas pathway for North American basketball players.</h1>
    <p class="lead">{esc(cfg['subtagline'])}</p>
    <div class="cta-row">
      <a class="btn btn-primary btn-lg" href="placement.html">Explore Malta Placement</a>
      <a class="btn btn-ghost btn-lg" href="events.html">See Upcoming Events</a>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head">
      <span class="kicker">How we place players</span>
      <h2>Three routes overseas</h2>
      <p>OPL moves players from North American gyms onto professional rosters abroad through a partnership-backed, FIBA-licensed pipeline.</p>
    </div>
    <div class="grid cols-3">{channels}</div>
  </div>
</section>

<section class="alt">
  <div class="container split">
    <div class="prose">
      <span class="kicker">Why Malta</span>
      <h2 style="color:var(--navy)">A real federation. A real season.</h2>
      <p>The Malta Basketball Association has been a FIBA member since 1967 and runs the country's top men's division. Malta competes in FIBA-sanctioned competition for small countries, which makes it a genuine, accessible entry point to professional basketball in Europe.</p>
      <p>Through our Valletta BC partnership, OPL places players directly into that environment &mdash; registered, supported, and game-ready.</p>
      <a class="btn btn-primary" href="about.html">About the partnership</a>
    </div>
    <div>{logo_slot('Valletta BC logo pending', light=True)}</div>
  </div>
</section>

<section class="dark">
  <div class="container">
    <div class="banner">
      <h2>Ready to take your game overseas?</h2>
      <p>Spots in the September Overseas Training Camp in Malta are open now. Passport-ready players only.</p>
      <a class="btn btn-gold btn-lg" href="contact.html">Start the conversation</a>
    </div>
  </div>
</section>"""
    pages["index.html"] = page(cfg, mark, slug="", title=cfg["site_name"],
                               description=f"{cfg['site_name']} — {cfg['tagline']} FIBA-licensed, EuroBasket-eligible overseas player placement in Malta.",
                               body=home, active="index.html")

    # ---- About / Partnership ----
    channel_cards = "".join(
        f'<div class="card"><span class="num">0{i+1}</span><h3>{esc(c["title"])}</h3><p>{esc(c["detail"])}</p></div>'
        for i, c in enumerate(cfg["channels"])
    )
    about = f"""<section class="hero">
  <div class="container hero-inner">
    <span class="eyebrow">About OPL</span>
    <h1>An official player-placement partner.</h1>
    <p class="lead">The Valletta BC partnership makes the Overseas Premier League an official player-placement partner into FIBA-licensed, EuroBasket-eligible competition.</p>
  </div>
</section>

<section>
  <div class="container split">
    <div class="prose">
      <span class="kicker">The partnership</span>
      <h2>Valletta BC &times; OPL</h2>
      <p>Our partnership with Valletta BC establishes OPL as an official player-placement partner. That relationship is the foundation for direct, legitimate access to a professional men's roster in Malta &mdash; not a tryout lottery, but a structured placement.</p>
      <p>Malta's basketball federation is a long-standing FIBA member, and its clubs play a real, sanctioned season. For North American players, that means professional experience, international film, and a credible step on the overseas ladder.</p>
    </div>
    <div>{logo_slot('Valletta BC logo pending', light=True)}</div>
  </div>
</section>

<section class="alt">
  <div class="container">
    <div class="section-head">
      <span class="kicker">How placement is delivered</span>
      <h2>Three delivery channels</h2>
      <p>Every OPL player reaches the overseas game through one of three structured channels.</p>
    </div>
    <div class="grid cols-3">{channel_cards}</div>
  </div>
</section>

<section class="dark">
  <div class="container">
    <div class="banner">
      <h2>Built for the next step</h2>
      <p>Whether you want a direct placement, an overseas tour, or a combine evaluation, OPL has a lane for you.</p>
      <a class="btn btn-gold btn-lg" href="placement.html">View the Malta package</a>
    </div>
  </div>
</section>"""
    pages["about.html"] = page(cfg, mark, slug="about.html", title="About / Partnership",
                               description="The Valletta BC partnership makes OPL an official player-placement partner, delivered via direct placement, overseas tours, and a North American scouting combine.",
                               body=about, active="about.html")

    # ---- Player Placement / Malta package ----
    perks = "".join(f"<li>{esc(p)}</li>" for p in cfg["perks"])
    camp = "".join(
        f'<div class="card"><h3>{esc(c["title"])}</h3><p>{esc(c["detail"])}</p></div>'
        for c in cfg["camp_includes"]
    )
    placement = f"""<section class="hero">
  <div class="container hero-inner">
    <span class="eyebrow">Player Placement &middot; Malta</span>
    <h1>Directly join a professional men's team in Malta.</h1>
    <p class="lead">FIBA-licensed. EuroBasket-eligible. A complete placement package that handles registration, paperwork, housing, and media so you can focus on basketball. Players must be passport-ready.</p>
    <div class="cta-row">
      <a class="btn btn-primary btn-lg" href="contact.html">Apply for placement</a>
    </div>
  </div>
</section>

<section>
  <div class="container split">
    <div class="prose">
      <span class="kicker">The placement</span>
      <h2>Player perks</h2>
      <p>Everything an overseas placement requires, handled for you:</p>
      <ul class="checks">{perks}</ul>
      <p class="notice">Passport-ready required. VISA support applies to stays over 90 days.</p>
    </div>
    <div>{photo_slot('Malta placement imagery (ProConnect flyer)', tag='Imagery pending')}</div>
  </div>
</section>

<section class="alt">
  <div class="container">
    <div class="section-head">
      <span class="kicker">Overseas Training Camp</span>
      <h2>The 7-day camp package</h2>
      <p>The OPL Overseas Training Camp gives players a full week inside the overseas environment &mdash; on the court and on film.</p>
    </div>
    <div class="grid cols-3">{camp}</div>
    <p style="margin-top:1.5rem"><strong>Next camp:</strong> September 21 &ndash; 28, 2026 &middot; Malta. <a href="events.html">See all events &rarr;</a></p>
  </div>
</section>

<section class="dark">
  <div class="container">
    <div class="banner">
      <h2>Passport ready? Let's place you.</h2>
      <p>Tell us about your game and your timeline. We'll walk you through registration, the package, and next steps.</p>
      <a class="btn btn-gold btn-lg" href="contact.html">Contact OPL</a>
    </div>
  </div>
</section>"""
    pages["placement.html"] = page(cfg, mark, slug="placement.html", title="Player Placement",
                                   description="Directly join a professional men's team in Malta. FIBA-licensed, EuroBasket-eligible. Player perks include FIBA & MBA registration, VISA support, housing, transport, and a media package.",
                                   body=placement, active="placement.html")

    # ---- Events ----
    events = f"""<section class="hero">
  <div class="container hero-inner">
    <span class="eyebrow">Events</span>
    <h1>Upcoming OPL events</h1>
    <p class="lead">Camps, league play, and combines on the road to overseas placement.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head">
      <span class="kicker">2026 schedule</span>
      <h2>Mark your calendar</h2>
    </div>
    {event_rows(cfg['events'])}
  </div>
</section>

<section class="dark">
  <div class="container">
    <div class="banner">
      <h2>Want in on the next event?</h2>
      <p>Reach out and we'll get you registration details as dates firm up.</p>
      <a class="btn btn-gold btn-lg" href="contact.html">Get event details</a>
    </div>
  </div>
</section>"""
    pages["events.html"] = page(cfg, mark, slug="events.html", title="Events",
                                description="OPL 2026 events: Overseas Training Camp (Sept 21-28), Summer League (July 5), and the League Combine (TBD).",
                                body=events, active="events.html")

    # ---- Contact ----
    contact = f"""<section class="hero">
  <div class="container hero-inner">
    <span class="eyebrow">Contact</span>
    <h1>Let's talk basketball.</h1>
    <p class="lead">Questions about placement, the Malta package, or an upcoming event? Reach the OPL team directly.</p>
    <div class="cta-row">
      <a class="btn btn-primary btn-lg" href="mailto:{esc(cfg['contact_email'])}">Email OPL</a>
    </div>
  </div>
</section>

<section>
  <div class="container split">
    <div class="prose">
      <span class="kicker">Get in touch</span>
      <h2>Reach the team</h2>
      <p>Email is the fastest way to reach us about placement and events.</p>
      <p><strong>Email:</strong> <a href="mailto:{esc(cfg['contact_email'])}">{esc(cfg['contact_email'])}</a></p>
      <p class="notice">Domain pending &mdash; this address will be confirmed once the OPL domain is registered.</p>
    </div>
    <div>{logo_slot('OPL logo pending', light=True)}</div>
  </div>
</section>"""
    pages["contact.html"] = page(cfg, mark, slug="contact.html", title="Contact",
                                 description="Contact the Overseas Premier League about player placement, the Malta package, and events.",
                                 body=contact, active="contact.html")

    return pages


# --------------------------------------------------------------------------- #
# Huskies pages
# --------------------------------------------------------------------------- #
def build_huskies(cfg):
    mark = HUSKIES_MARK
    pages = {}
    square = cfg["square_link"]
    square_pending = square.startswith("#")
    square_attr = 'href="#" onclick="return false;"' if square_pending else f'href="{esc(square)}" target="_blank" rel="noopener"'

    gallery = "".join(photo_slot(g["caption"], tag=g["type"].title()) for g in cfg["gallery"])

    # ---- Home ----
    home = f"""<section class="hero">
  <div class="container hero-inner">
    <span class="eyebrow">Vancouver &middot; Navy / Red / White</span>
    <h1>Vancouver Huskies basketball.</h1>
    <p class="lead">{esc(cfg['subtagline'])}</p>
    <div class="cta-row">
      <a class="btn btn-primary btn-lg" href="signup.html">Sign Up &amp; Pay</a>
      <a class="btn btn-ghost btn-lg" href="#gallery">See the team</a>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head">
      <span class="kicker">The program</span>
      <h2>Train hard. Compete. Get seen.</h2>
      <p>The Huskies develop Vancouver players through real competition and a direct line to the Overseas Premier League pathway.</p>
    </div>
    <div class="grid cols-3">
      <div class="card"><h3>Train</h3><p>Weekly skills, conditioning, and team practice with a pro-track standard.</p></div>
      <div class="card"><h3>Compete</h3><p>Game reps through Huskies events and the OPL Summer League slate.</p></div>
      <div class="card"><h3>Advance</h3><p>Eligible players carry their game overseas through the OPL camp in Malta.</p></div>
    </div>
  </div>
</section>

<section class="alt" id="gallery">
  <div class="container">
    <div class="section-head">
      <span class="kicker">Roster &amp; photos</span>
      <h2>On the floor</h2>
      <p>Game and training shots from the Huskies program. Player photos drop into these slots.</p>
    </div>
    <div class="grid cols-3">{gallery}</div>
  </div>
</section>

<section class="dark">
  <div class="container">
    <div class="banner">
      <h2>Join the Huskies</h2>
      <p>Players are invoiced through the Huskies Square account. Tap below to sign up and pay.</p>
      <a class="btn btn-gold btn-lg" {square_attr}>Sign Up &amp; Pay via Square</a>
      {('<p class="notice" style="margin-top:1.2rem">Square payment link pending from client &mdash; button is a placeholder until the link is provided.</p>' if square_pending else '')}
    </div>
  </div>
</section>"""
    pages["index.html"] = page(cfg, mark, slug="", title=cfg["site_name"],
                               description=f"{cfg['site_name']} — {cfg['tagline']} Train, compete, and reach the overseas pathway.",
                               body=home, active="index.html")

    # ---- Events ----
    events = f"""<section class="hero">
  <div class="container hero-inner">
    <span class="eyebrow">Events</span>
    <h1>Huskies schedule</h1>
    <p class="lead">Training, league play, and overseas pathway opportunities.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head">
      <span class="kicker">2026</span>
      <h2>What's coming up</h2>
    </div>
    {event_rows(cfg['events'])}
  </div>
</section>

<section class="dark">
  <div class="container">
    <div class="banner">
      <h2>Ready to play?</h2>
      <p>Sign up and pay through the Huskies Square account to lock your spot.</p>
      <a class="btn btn-gold btn-lg" href="signup.html">Sign Up &amp; Pay</a>
    </div>
  </div>
</section>"""
    pages["events.html"] = page(cfg, mark, slug="events.html", title="Events",
                                description="Vancouver Huskies events: training sessions, OPL Summer League (July 5, 2026), and the overseas camp pathway.",
                                body=events, active="events.html")

    # ---- Signup / Payment ----
    signup = f"""<section class="hero">
  <div class="container hero-inner">
    <span class="eyebrow">Sign Up</span>
    <h1>Join the Huskies &amp; pay securely.</h1>
    <p class="lead">Players are currently invoiced via Square through the Huskies account. Tap the button to sign up and complete payment.</p>
  </div>
</section>

<section>
  <div class="container split">
    <div class="prose">
      <span class="kicker">Payment</span>
      <h2>Pay through Square</h2>
      <p>Payment is handled entirely by Square &mdash; the Huskies don't store any card details on this site. The button below takes you straight to the secure Square checkout.</p>
      <p style="margin:1.6rem 0">
        <a class="btn btn-primary btn-lg" {square_attr}>Sign Up &amp; Pay via Square</a>
      </p>
      {('<p class="notice">Square payment link pending from client. This button is a placeholder &mdash; once the Square link is provided, it will point directly to the Huskies Square checkout.</p>' if square_pending else '')}
    </div>
    <div>{photo_slot('Huskies team photo', tag='Photo pending')}</div>
  </div>
</section>"""
    pages["signup.html"] = page(cfg, mark, slug="signup.html", title="Sign Up & Pay",
                                description="Sign up for the Vancouver Huskies. Players are invoiced via Square through the Huskies account.",
                                body=signup, active="signup.html")

    return pages


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
    for name, html in pages.items():
        with open(os.path.join(out, name), "w") as f:
            f.write(html)
    # robots + sitemap for SEO
    base = f"https://{cfg['domain_placeholder']}"
    with open(os.path.join(out, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
    urls = "".join(f"  <url><loc>{base}/{n if n!='index.html' else ''}</loc></url>\n" for n in pages)
    with open(os.path.join(out, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                f"{urls}</urlset>\n")
    print(f"  {key}: wrote {len(pages)} pages + assets to {os.path.relpath(out, REPO)}/")


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
