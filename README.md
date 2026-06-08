# AIVIQ June 2026 media host

Always-on social poster for three brands — **Chaya**, **Ren**, **David** —
across **Instagram**, **Facebook**, and **TikTok**.

## How it works

- `june_schedule.json` — the full June posting plan (2 slots/day, 9:00 & 18:00
  Pacific) with the brand, target platforms, and caption for each reel.
- `media_urls.json` — maps each scheduled file to its hosted video URL (the
  videos live as assets on the `june2026` GitHub Release).
- `post.py` — the poster. For every item that's due, it posts to each listed
  platform and records it in `post_done.json` so nothing posts twice.
- `.github/workflows/poster.yml` — runs `post.py` every 30 minutes and commits
  the updated `post_done.json` back to the repo.

Platforms per brand (from the schedule): Chaya → IG + FB + TikTok ·
Ren → IG + FB + TikTok · David → FB + TikTok.

## Going live (one-time setup)

1. **Merge this to `main`.** GitHub runs scheduled workflows only from the
   default branch, so the poster stays dormant until then.
2. **Add the repo secrets** (Settings → Secrets and variables → Actions):

   `META_CREDS` (JSON):
   ```json
   {
     "chaya": {"instagram_id": "...", "page_id": "...", "page_token": "..."},
     "ren":   {"instagram_id": "...", "page_id": "...", "page_token": "..."},
     "david": {"page_id": "...", "page_token": "..."}
   }
   ```
   `TIKTOK_CREDS` (JSON):
   ```json
   {
     "chaya": {"access_token": "..."},
     "ren":   {"access_token": "..."},
     "david": {"access_token": "..."}
   }
   ```
   Any platform whose creds are missing is skipped, so you can switch them on
   one at a time.

3. **Test first.** Actions → *Multi-platform poster* → *Run workflow* with
   *dry_run = true* to see exactly what would post, then run again with
   *dry_run = false*.

## Catch-up guard

By default the poster only sends items due within the last **12 hours**
(`BACKLOG_HOURS`). This stops the whole month's missed posts from flooding out
the first time it runs. Older due items are skipped (and logged) but not marked
done, so they can be backfilled manually. Set `BACKLOG_HOURS=0` to post
everything outstanding.

## Notes on credentials

- **Instagram & Facebook** use the Meta Graph API — a long-lived Facebook Page
  access token per brand (with `pages_manage_posts` and, for IG,
  `instagram_content_publish`), plus the IG business account id and Page id.
- **TikTok** uses the Content Posting API (`video.publish` scope). Direct
  publishing requires an approved/audited TikTok app; the pull-from-URL flow
  also requires the media domain to be verified with TikTok.
