# Personal Planner

A private, single-user life dashboard built with Next.js (App Router) and
Tailwind, designed for the Vercel free hobby tier. Mobile-first, dark theme.

> This repo also hosts the AIVIQ June 2026 media files and the Instagram reel
> poster (`ig_post.py`, `*.json`). Those are unrelated to the planner app and
> are left untouched.

## Sections

1. **This Week — Shifts** — 7-day strip. Sun/Mon/Tue are fixed night shifts
   (RainCity Housing); Wed–Sat extras come from `EXTRA_SHIFT_DAYS`. Shows
   "next shift in X days".
2. **Upcoming** — next 14 days of Google Calendar events, with appointment
   detection (physio, chiro, massage, doctor, dentist, appointment, meeting).
3. **Email Triage** — last 7 days of Gmail sorted into Needs action /
   Appointments / Unsubscribe candidates / Likely junk. Sender + subject only,
   no body content.
4. **Quick Reminders** — local-only to-dos with optional date, stored in
   `localStorage`.

## Local development

```bash
npm install
cp .env.example .env.local   # fill in values
npm run dev
```

Open http://localhost:3000. If `DASHBOARD_PASSWORD` is unset the password gate
is disabled (handy for local dev).

## Environment variables

| Variable               | Purpose                                              |
| ---------------------- | ---------------------------------------------------- |
| `DASHBOARD_PASSWORD`   | Simple password gate, enforced by middleware         |
| `GOOGLE_CLIENT_ID`     | OAuth client ID                                      |
| `GOOGLE_CLIENT_SECRET` | OAuth client secret                                  |
| `GOOGLE_REFRESH_TOKEN` | Long-lived refresh token (read-only Gmail + Calendar)|
| `EXTRA_SHIFT_DAYS`     | Comma list of extra shift days, e.g. `THU,SAT`       |

### Generating the Google refresh token

1. Create a Google Cloud project and enable the **Gmail API** and
   **Google Calendar API**.
2. Create an OAuth client ID (Web application). Add
   `https://developers.google.com/oauthplayground` as an authorised redirect URI.
3. In the [OAuth Playground](https://developers.google.com/oauthplayground),
   tick "Use your own OAuth credentials", paste the client ID/secret, select
   scopes `gmail.readonly` and `calendar.readonly`, authorise, and exchange the
   code for tokens. Copy the **refresh token**.

Read-only scopes only — the app never sends, deletes, or modifies anything.

## Deploy to Vercel

1. Import this repo into Vercel (framework auto-detected as Next.js).
2. Add the environment variables above in **Settings → Environment Variables**.
3. Deploy. Update `EXTRA_SHIFT_DAYS` any time from the Vercel dashboard — no
   redeploy of code needed (a new deployment picks up the value).

## Notes

- API responses (Gmail/Calendar) are cached in-process for 30 minutes to stay
  under Google rate limits.
- No database, no user accounts, no business logic.
