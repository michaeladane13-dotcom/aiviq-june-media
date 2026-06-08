# What's Missing — Inputs Needed to Go Live (OPL + Huskies, Phase 1)

Both sites are **built and production-ready** except for the items below. Everything
here shows as a clearly labelled placeholder slot or a visible "Dev note" on the live
pages. Sites are on branch `claude/opl-huskies-build-fViVg`:
`opl-site/` (5 pages) and `huskies-site/` (3 pages).

Status: 🔴 blocks launch · 🟡 placeholder in place · 🟢 nice-to-have

---

## 0. 🔴 IMPORTANT: image uploads are NOT reaching the build environment
Every brief has referenced files in `/mnt/user-data/uploads/`, but **that folder does
not exist in my session** and none of the named files (`IMG_2080–2095`, `IMG_2090`,
the Aiviq `A1AF4F72…` / `CA56CA7D…` PNGs) are anywhere on the filesystem. So far I have
received **zero image files**. The build is fully wired to use them — drop each file
into `site-builder/assets/<opl|huskies|aiviq>/` with the exact name and rerun the
build and the placeholders swap to real images automatically — but I need the files to
actually arrive. **Please re-attach them directly in chat** so I can confirm receipt.

## 1. 🔴 Logos
- [ ] **OPL logo** `IMG_2090.png` — currently a faithful SVG recreation from your
      description (globe + white "O" + basketball seams + red plane). Swaps in on upload.
- [ ] **Aiviq Enterprises Inc. logo** (gold on black) for both footers — SVG gold mark
      stand-in until received. Save as `assets/aiviq/aiviq-enterprises.png`.
- [ ] **Vancouver Huskies wolf logo** — PENDING per brief; placeholder slot on Huskies
      home + nav SVG stand-in.
- [ ] **Valletta BC logo** — PENDING per brief; placeholder slot on OPL About page.

## 2. 🔴 Domains
Both use `*-domain-pending.com` in canonical tags, sitemaps, footers, and the Huskies→OPL
partner link.
- [ ] **OPL domain:** ____________________
- [ ] **Huskies domain:** ____________________

## 3. 🔴 Square payment link (Huskies)
"Sign Up & Pay via Square" is a labelled, disabled placeholder until provided.
- [ ] **Square link URL:** ____________________  (set `square_link` in `huskies.json`)

## 4. 🔴 OPL contact email
Huskies email is set (`vancouverhuskiesbasketball@gmail.com`). OPL's is PENDING per the
brief — Contact page + footer show "pending".
- [ ] **OPL contact email:** ____________________  (set `contact_email` in `opl.json`)

## 5. 🟡 Player photos (Huskies)
Gallery + sign-up use labelled slots naming each expected file. Send the images and
they auto-populate:
- [ ] `IMG_2080` (dunk), `IMG_2081` (#11), `IMG_2091` (#2 portrait), `IMG_2092`
      (court), `IMG_2093`, `IMG_2094` (#3), `IMG_2095` (bench). (`IMG_2082` is a
      duplicate of `IMG_2081` and is skipped.)

## 6. 🟡 OPL placement flyers
- [ ] `IMG_2087.png` (placement package flyer) → Player Placement card 1
- [ ] `IMG_2088.png` (training camp flyer) → Player Placement card 2

## 7. 🟡 Social media links (both sites)
Footer shows IG / X / TikTok / YouTube icons labelled "pending".
- [ ] Instagram / X / TikTok / YouTube URLs for each site (set `socials` in the JSON).

## 8. 🟡 Event register / RSVP links (OPL)
Each OPL event card has a "Register / RSVP (link pending)" button.
- [ ] RSVP/registration URL per event (Camp / Summer League / Combine), or one shared.
- [ ] **Combine date & location** when known; **Summer League location** (currently TBA).
- [ ] Any **Huskies-specific local events** (training schedules, local games) — the
      Huskies Events page has a labelled placeholder for these.

## 9. 🟡 Copy sign-off (visible "Dev note" boxes on the live pages)
Confirm before launch so I can remove the notes:
- [ ] "Official player placement partner" wording — approved by **Valletta BC**?
- [ ] **"FIBA Licensed"** and **"EuroBasket Eligible"** — OK to claim publicly in these
      exact words?
- [ ] Player **perks** list complete/accurate? (FIBA Reg, Malta Basketball Assoc Reg,
      VISA 90+ days, Gym Membership, Transportation & Housing, Media Package)
- [ ] Camp **tour package** complete/accurate? (Accommodations 7 days, Merch
      reversible/t-shirt/shorts, Transport airport & gym, Media film & interviews,
      Food 2 meals/day)

## 10. ⚠️ Scope conflict to resolve — Las Vegas Empress / Shine On
The asset list includes `IMG_2089` (Las Vegas Empress flyer), `IMG_2083` (Shine On
logo), and `IMG_2084` (Las Vegas Empress logo), with `IMG_2089` noted "use on OPL
Player Placement page." But the **OUT OF SCOPE** section says *do not build, do not
reference* Las Vegas Empress or Shine On. The detailed page content also only assigns
`IMG_2087`/`IMG_2088` to that page. I followed **OUT OF SCOPE** and did **not** use
those three files.
- [ ] Confirm: leave them out (current), **or** tell me exactly where the Vegas Empress
      partner announcement should appear and I'll add it.

---

## Note on research tooling
The brief asked for Perplexity MCP research; no Perplexity server was connected to my
session. I used web search instead and kept copy to client-provided text plus
verifiable Malta/FIBA facts (Malta Basketball Association is a FIBA member; runs the
top men's division). No facts, names, emails, or URLs were invented.

### How to send it back
Answer inline under each number, and **attach the image files in chat** (the
`/mnt/user-data/uploads/` path is not reaching me). Items 0–4 are the true blockers.
