# Chaya — Build Blueprint

The running plan. Decisions below are **locked**; the open items are listed at the end.

## Product
A daily spiritual-guidance app built around the user's **exact natal chart**.
Free daily cards (insight, tarot, moon phase) + a paid one-time **"Your Month
Ahead"** report ($14.99).

## Locked decisions
| Area | Decision |
|---|---|
| Chart math | **Swiss Ephemeris, in-house** (free, exact, Astro-Seek grade). Prototype: `chart_work/natal.py`. |
| Chart depth | Full spec: 10 planets + Chiron + 4 asteroids, nodes (mean/true), Lilith (mean/true), ASC/MC/Vertex, Placidus + Whole Sign houses, aspect grid w/ orbs, declinations, dignities, element/modality balance. |
| Written guidance | **Kimi** (Moonshot). Fast + cheap. Key supplied by owner. |
| Gold standard | Astro-Seek / astro.com — exactness is the bar. No "whimsy", no LLM-guessed numbers. |
| Monetization | One-time **$14.99** unlock via RevenueCat (non-consumable). |
| Birth city | Google Places autocomplete (kept) → resolves lat/lon for the chart. |
| Auth + data | Supabase (auth + Postgres + Edge Functions). |
| Privacy | Raw PII never leaves our backend; the LLM only sees computed chart JSON. |

## Architecture
```
Expo app (React Native)
  │  Supabase auth (session in AsyncStorage)
  │  reads: user_profiles, natal_charts, daily_content, monthly_reports, entitlements (RLS: own rows)
  ▼
Supabase Postgres  ── RLS ──  raw birth PII isolated in user_profiles
  ▲
  │ service role (bypasses RLS)
Supabase Edge Functions (Deno/TS)
  ├─ compute-chart : birth data → Swiss Ephemeris → natal_charts.chart (JSON)
  ├─ daily-content : chart JSON + prompt → Kimi → daily_content
  ├─ monthly-report: chart JSON + prompt → Kimi → monthly_reports   (gated on entitlement)
  └─ revenuecat-webhook : purchase event → entitlements
        │
        ▼ (chart JSON + prompt ONLY — no name/time/place, no key in app)
      Kimi API
```

## Privacy model (the client-facing promise, made real)
1. Birth date/time/place live only in `user_profiles`, RLS-locked to the owner.
2. The **chart is computed by our ephemeris**, server-side — so the LLM never
   needs the birth time or place. It receives finished positions only.
3. The Kimi API key lives in Edge Function secrets, **never in the app bundle**.
4. No raw PII is ever sent to a third-party model.

## Data model
See `supabase/migrations/0001_init.sql`:
`user_profiles` · `natal_charts` · `daily_content` · `monthly_reports` · `entitlements`.

## Build order
1. **DB** — apply `0001_init.sql` (done; needs `supabase db push` to a project). ✅ written
2. **Chart Edge Function** — port `natal.py` → Deno + a WASM Swiss Ephemeris
   (`swisseph-wasm`); write result to `natal_charts`. Validate against
   `chart_work/chart_report.txt` (the reference chart) — must match to the tick.
3. **Config** — fill `constants/config.js` (Supabase URL/anon, Google Places).
4. **Wire onboarding** — on profile create, resolve lat/lon/tz + trigger compute-chart.
5. **Daily content** — `daily-content` function + Home cards read real data.
6. **Paywall** — RevenueCat product `month_ahead`; `revenuecat-webhook` → entitlements; gate `monthly-report`.
7. **Polish + store prep** — icons, screenshots, privacy policy, dev build.

## Open items (need an owner decision / input)
- **Kimi API key** — owner providing.
- **Brand voice / prompt copy** for daily + monthly content (the writing style —
  deliberately deferred; this is where "no AI slop" gets enforced).
- **House system default** for clients (Placidus assumed; confirm).

## Reference artifacts
- `chart_work/natal.py` — Swiss Ephemeris engine (Python prototype).
- `chart_work/chart_report.txt` — a known-good chart used to verify any port.
