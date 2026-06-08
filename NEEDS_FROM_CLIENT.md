# What's Missing — Inputs Needed to Finish OPL + Huskies (Phase 1)

This is the punch list of everything still blocking or thinning the two sites. Hand
this to the other Claude chat (the comprehensive one) and have it paste back answers
in the same numbered structure. Anything you give me, I'll wire in and rebuild.

Sites already built and on branch `claude/opl-huskies-build-fViVg`:
- `opl-site/` (Home, About/Partnership, Player Placement, Events, Contact)
- `huskies-site/` (Home + gallery, Events, Sign Up & Pay)

Status key: 🔴 blocks launch · 🟡 placeholder in place, needs real content · 🟢 nice-to-have

---

## 1. 🔴 Logos & brand art (files were NOT in the build environment)
The brief said logos/photos were in `/mnt/user-data/uploads/`, but that folder was
empty in my session. Right now everything is a placeholder slot or a simple SVG mark.

Please provide (PNG or SVG, transparent background preferred):
- [ ] **OPL primary logo** (the globe + plane + basketball "O", blue/red)
- [ ] **OPL logo on dark** variant if you have one (for the navy header)
- [ ] **Vancouver Huskies logo** (the wolf mark from the jersey photos)
- [ ] **Valletta BC logo** (used on OPL Home + About partnership sections)
- [ ] **Aiviq gold mark** (currently a stand-in gold diamond in the footer)
- [ ] **Favicon** for each site (or I'll generate from the logos)

## 2. 🔴 Domain names
Both sites use `*-domain-pending.com` placeholders in canonical tags, sitemaps, footers.
- [ ] **OPL domain:** ____________________
- [ ] **Huskies domain:** ____________________
- [ ] Where will each be hosted? (Netlify / Vercel / Cloudflare Pages / GitHub Pages /
      other) — affects nothing in the code, but I can prep deploy config if you tell me.

## 3. 🔴 Square payment link (Huskies)
The "Sign Up & Pay via Square" button is a labelled placeholder until I have the URL.
- [ ] **Square checkout/payment link:** ____________________
- [ ] Is it one link for everyone, or different links per program/fee? If multiple,
      give me the label + URL for each and I'll add buttons.

## 4. 🟡 Player & action photos
Game and training shots go into the photo slots (Huskies home gallery + several
OPL/Huskies pages). None were available, so all are placeholders.
- [ ] **Huskies game photos** (the more the better; I'll size/crop)
- [ ] **Huskies training photos**
- [ ] **Huskies team/group photo** (used on the Sign Up page)
- [ ] **OPL / Malta placement imagery** (the ProConnect flyer visuals referenced in
      the brief) for the Player Placement page
- [ ] Any **hero/background photo** you want behind the home headlines (optional —
      they currently use a clean navy gradient)

## 5. 🟡 Contact details
Placeholders in use: `info@overseaspremierleague.com` and `info@vancouverhuskies.com`.
- [ ] **Real OPL/Huskies email** (the brief says "link to OPL/Huskies email" — one
      shared inbox, or one per site?)
- [ ] **Phone number?** (optional — not currently shown)
- [ ] **Social links** (Instagram / X / TikTok / YouTube) for headers/footers? (optional)
- [ ] **Physical location** to list for the Huskies (Vancouver venue/gym)? (optional)

## 6. 🟡 Copy review / corrections
I wrote launch copy from the brief + verifiable public Malta/FIBA facts. Please confirm
or correct:
- [ ] The **Valletta BC partnership** wording ("official player-placement partner") —
      accurate as stated? Any specific phrasing the partner requires?
- [ ] **"FIBA-licensed / EuroBasket-eligible"** — confirm we can claim both publicly,
      and in these exact words.
- [ ] **Malta package perks** — confirm the list is complete/correct: FIBA Registration,
      Malta Basketball Association Registration, VISA (90+ day stays), Gym Membership,
      Transportation & Housing, Media Package. Anything to add/remove?
- [ ] **Camp package** — Accommodations (7 days), Merch (reversible/t-shirt/shorts),
      Transportation (airport & gym), Media (film & interviews), Food (2 meals/day).
      Correct?
- [ ] **Pricing** — should any prices/fees appear on the sites, or stay off until Square?
- [ ] Tagline/positioning — happy with the current OPL and Huskies headlines, or send
      preferred wording.

## 7. 🟡 Events — confirm & extend
Currently live: OPL Overseas Training Camp (Sept 21–28 2026), OPL Summer League
(July 5 2026), OPL League Combine (TBD); Huskies training (ongoing) + the two OPL events.
- [ ] Confirm those dates/locations.
- [ ] **Combine date** when known.
- [ ] **Specific venues/cities** for Summer League and Combine (currently "TBA").
- [ ] Any **other events** to list on either site?
- [ ] Should events have a **register/RSVP link** (Square, form, email)?

## 8. 🟢 Comprehensive Claude chat — anything else
If the other chat covered things not in my build brief, send them:
- [ ] Extra **pages or sections** you want (e.g. testimonials, FAQ, roster bios,
      sponsors, news/blog).
- [ ] Specific **brand fonts** or an exact hex palette (I used navy `#0b2349`,
      red `#c8102e`, white, Aiviq gold `#c9a64a`).
- [ ] Any **legal/footer** text (privacy, terms, refund policy for Square payments).
- [ ] **Analytics** (Google Analytics / Meta Pixel ID) to embed.

---

### How to send it back
Easiest: answer inline under each number. Drop image/logo files anywhere I can read
them and tell me the path, or attach them. Once I have items 1–3 I can take both sites
from "placeholder" to "launch-ready."
