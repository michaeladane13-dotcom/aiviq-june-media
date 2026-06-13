# Edge Functions (Deno/TS)

All run with the **service-role key** (bypass RLS) and read secrets from the
function environment — never from the client. The LLM (Kimi) is only ever
called from here, and only ever with computed chart JSON + a prompt.

## `compute-chart`
- **In:** `{ user_id }`
- **Does:** loads birth data from `user_profiles`, runs Swiss Ephemeris
  (`swisseph-wasm`), upserts the full chart JSON into `natal_charts`.
- **Verify against:** `chart_work/chart_report.txt` — positions must match to the tick.
- **Secrets:** none (ephemeris is local).

## `daily-content`
- **In:** `{ user_id, date }`
- **Does:** reads `natal_charts.chart`, builds the daily prompt, calls **Kimi**,
  upserts `daily_content` (kind = insight | tarot). Moon phase is computed, not LLM'd.
- **Secrets:** `KIMI_API_KEY`.

## `monthly-report`
- **In:** `{ user_id, period }`  (period = 'YYYY-MM')
- **Gate:** require an active `entitlements` row (`product = 'month_ahead'`) before generating.
- **Does:** reads chart, builds the month-ahead prompt, calls **Kimi**, upserts `monthly_reports`.
- **Secrets:** `KIMI_API_KEY`.

## `revenuecat-webhook`
- **In:** RevenueCat webhook payload (verify signature).
- **Does:** on a non-consumable `month_ahead` purchase, upsert an `entitlements` row.
- **Secrets:** `REVENUECAT_WEBHOOK_SECRET`.

## Prompt inputs — privacy rule
The prompt sent to Kimi contains the **computed chart** (signs, degrees, houses,
aspects) and nothing else. Do **not** include the user's name, raw birth time,
or birth place in the prompt.
