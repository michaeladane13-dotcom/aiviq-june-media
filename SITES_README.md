# OPL + Vancouver Huskies — Phase 1 Build

Two **fully independent static sites**, each for its own domain. Built by Aiviq
Enterprises Inc. for Brandon Mullins.

- `opl-site/` — Overseas Premier League main site (Home, About/Partnership, Player
  Placement, Events, Contact)
- `huskies-site/` — Vancouver Huskies site (Home, Events, Sign Up & Pay)

Pure **static HTML/CSS** — no framework, no client-side rendering — so every page
indexes for SEO. Each folder is self-contained and drops onto any static host
(Netlify, Vercel, Cloudflare Pages, GitHub Pages, S3). Mobile responsive (verified at
390px: zero horizontal overflow). Per-site `robots.txt` + `sitemap.xml`.

## Build / regenerate

```
python3 site-builder/build.py
```

Standard library only — no `pip install`. Source of truth:
- `site-builder/content/opl.json` and `huskies.json` — events, emails, domain, Square
  link, socials, gallery list.
- `site-builder/assets/<opl|huskies|aiviq>/` — drop client image files here (see below).
- `site-builder/build.py` — page templates, CSS, SVG brand marks.

## Wiring in client images (auto-swap)

Drop a file into `site-builder/assets/…` using the **exact filename** and rerun the
build. The labelled placeholder slot is automatically replaced with a real `<img>`
(copied into each site's `assets/img/`). Expected files are listed in
`site-builder/assets/README.md`:

- **OPL:** `IMG_2087.png` (placement flyer), `IMG_2088.png` (camp flyer),
  `IMG_2090.png` (OPL logo — replaces the SVG stand-in in nav/hero).
- **Huskies:** `IMG_2080–2095.png` player photos (gallery + sign-up).
- **Aiviq (both footers):** `aiviq/aiviq-enterprises.png`
  (orig. `A1AF4F72-2F5F-4E86-A931-12A1891C7A6F.png`, gold on black).

Until provided, the OPL logo is a faithful **SVG recreation** from the client's
description (globe with white "O" cut-out, basketball seams, red plane), and the Aiviq
footer uses an SVG gold mark.

## Branding

Navy `#0b2349`, red `#c8102e`, white `#ffffff`, Aiviq gold `#c9a64a`. USA-themed bold
sports aesthetic, navy base with red/white accents. Aiviq footer credit on both sites.

## Visible dev notes & placeholders (by design)

Per the brief, every pending item is a **clearly labelled** slot, and every line of
copy needing client sign-off carries a visible amber **"Dev note — client review"**
box. These are intentional and must be resolved/removed before go-live. See
`NEEDS_FROM_CLIENT.md`.

## Out of scope (Phase 1)

US development-league team pages (Volusia Serpents, Shine On Athletics, Huskies USA,
Las Vegas Empress) and any custom payment/checkout. Payments link OUT to Square only.
Note: three uploaded assets (`IMG_2089` Las Vegas Empress flyer, `IMG_2083` Shine On
logo, `IMG_2084` Las Vegas Empress logo) were intentionally **not used** because the
brief also says "do not reference" those orgs — flagged in `NEEDS_FROM_CLIENT.md`.
