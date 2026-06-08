# OPL + Vancouver Huskies — Phase 1 Build

Two **fully independent static sites**, each intended for its own domain. Built by
Aiviq Enterprises Inc. for Brandon Mullins (OPL / Vancouver Huskies).

- `opl-site/` — Overseas Premier League main site (5 pages)
- `huskies-site/` — Vancouver Huskies site (3 pages)

Both are **pure static HTML/CSS** (no framework, no client-side rendering) so they
index cleanly for SEO. Each folder is self-contained and can be dropped onto any
static host (Netlify, Vercel, Cloudflare Pages, S3, GitHub Pages, etc.).

## Pages

**OPL** — Home, About / Partnership, Player Placement (Malta package), Events, Contact.
**Huskies** — Home (with photo gallery), Events, Sign Up & Pay (Square link out).

## How to update content (dates, links, copy)

Everything that changes lives in JSON. Edit, then rebuild:

```
# Edit one of:
site-builder/content/opl.json
site-builder/content/huskies.json

# Regenerate the static HTML:
python3 site-builder/build.py
```

`build.py` uses only the Python standard library — no `pip install` needed.

- **Event dates:** edit the `events` array (`date_display` is what shows; `date_iso`
  drives the calendar chip — leave it `""` for TBD).
- **Square link (Huskies):** set `square_link` in `huskies.json` to the real Square
  URL. While it starts with `#`, the button renders as a clearly-labelled placeholder.
- **Contact email / domain:** `contact_email` and `domain_placeholder` in each JSON.

## Blocked on client (currently using placeholders)

1. **League logos** — placeholder slots are in place (dashed "logo pending" boxes and
   simple SVG marks: an OPL globe+plane+basketball "O", and a Huskies wolf head).
   Drop final art in and wire it into `build.py`'s `OPL_MARK` / `HUSKIES_MARK` or the
   `logo_slot()` calls.
2. **Domain names** — both sites use `*-domain-pending.com` placeholders in canonical
   tags, sitemaps, and footers. Update `domain_placeholder` once registered.
3. **Square payment link** — placeholder button until provided.
4. **Player photos** — game/training shots drop into the `.photo-slot` placeholders on
   the Huskies home gallery and several OPL/Huskies pages. (The uploaded photo/logo
   files referenced in the brief were not present in the build environment, so all
   imagery is placeholder for now.)

## Branding

Navy base (`#0b2349`), red (`#c8102e`), white accents — USA theme. Aiviq gold
(`#c9a64a`) footer credit on both sites.

## Out of scope (Phase 1)

US development-league team hubs (Volusia Serpents, Shine On Athletics, Huskies USA,
Las Vegas Empress) and any custom payment processing/checkout — payments link out to
Square only.
