#!/usr/bin/env python3
"""Always-on multi-platform reel poster for AIVIQ June 2026.

Posts each scheduled item to Instagram (Reels), Facebook (Page video), and
TikTok at its scheduled Pacific time. Self-dedupes via post_done.json which is
committed back to the repo, so every post goes out exactly once.

Runs on GitHub Actions on a cron (see .github/workflows/poster.yml).

----------------------------------------------------------------------------
Credentials (set as GitHub repo secrets, each a JSON object keyed by brand):

  META_CREDS = {
    "chaya": {"instagram_id": "...", "page_id": "...", "page_token": "..."},
    "ren":   {"instagram_id": "...", "page_id": "...", "page_token": "..."},
    "david": {                       "page_id": "...", "page_token": "..."}
  }
    - instagram_id + page_token  -> needed for Instagram Reels
    - page_id      + page_token  -> needed for Facebook video
    (david has no Instagram in the schedule, so instagram_id is optional)

  TIKTOK_CREDS = {
    "chaya": {"access_token": "..."},
    "ren":   {"access_token": "..."},
    "david": {"access_token": "..."}
  }
    - TikTok Content Posting API token (video.publish scope).

Any platform whose creds are missing is simply skipped (logged), so you can
turn the platforms on one at a time.

----------------------------------------------------------------------------
Env flags:

  DRY_RUN=1         Log what *would* post and write nothing live. Nothing is
                    marked done, no API calls are made.

  BACKLOG_HOURS=12  Only auto-post items whose scheduled time is within this
                    many hours of "now". This prevents a flood of the whole
                    month's missed posts the first time the workflow runs.
                    Items older than the window are skipped (and logged) but
                    NOT marked done, so you can still backfill them manually.
                    Set BACKLOG_HOURS=0 to disable the window (post everything
                    due that isn't done yet).
"""
import json, os, time, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timezone, timedelta

GRAPH = "https://graph.facebook.com/v22.0"
TIKTOK_INIT = "https://open.tiktokapis.com/v2/post/publish/video/init/"

# Schedule times are in the user's local Pacific time (PDT for June).
PT = timezone(timedelta(hours=-7))

# Map the schedule's platform tokens to internal platform names.
PLATFORM_TOKENS = {"meta_ig": "ig", "meta_fb": "fb", "tiktok": "tiktok"}

DONE_FILE = "post_done.json"
LEGACY_DONE_FILE = "ig_done.json"  # carried over so old IG dedup keys still count

DRY_RUN = os.environ.get("DRY_RUN", "").strip() not in ("", "0", "false", "False")
try:
    BACKLOG_HOURS = float(os.environ.get("BACKLOG_HOURS", "12") or 0)
except ValueError:
    BACKLOG_HOURS = 12.0


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def load_creds(var):
    raw = os.environ.get(var, "").strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except ValueError:
        print(f"WARN: {var} is set but is not valid JSON; treating as empty.", flush=True)
        return {}


# ---------------------------------------------------------------------------
# Platform posters. Each returns {"id": ...} on success or {"error": ...}.
# ---------------------------------------------------------------------------

def post_ig_reel(ig, tok, url, cap):
    data = urllib.parse.urlencode(
        {"media_type": "REELS", "video_url": url, "caption": cap, "access_token": tok}
    ).encode()
    r = urllib.request.urlopen(f"{GRAPH}/{ig}/media", data=data, timeout=60)
    cid = json.loads(r.read().decode()).get("id")
    if not cid:
        return {"error": "no container"}
    for _ in range(40):
        time.sleep(6)
        s = urllib.request.urlopen(
            f"{GRAPH}/{cid}?fields=status_code&access_token={tok}", timeout=30
        )
        st = json.loads(s.read().decode()).get("status_code")
        if st == "FINISHED":
            break
        if st == "ERROR":
            return {"error": "processing"}
    pub = urllib.parse.urlencode({"creation_id": cid, "access_token": tok}).encode()
    r = urllib.request.urlopen(f"{GRAPH}/{ig}/media_publish", data=pub, timeout=60)
    return json.loads(r.read().decode())


def post_fb_video(page_id, tok, url, cap):
    data = urllib.parse.urlencode(
        {"file_url": url, "description": cap, "access_token": tok}
    ).encode()
    r = urllib.request.urlopen(f"{GRAPH}/{page_id}/videos", data=data, timeout=120)
    return json.loads(r.read().decode())


def post_tiktok(tok, url, cap):
    body = json.dumps(
        {
            "post_info": {
                "title": cap[:2200],
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "disable_comment": False,
            },
            "source_info": {"source": "PULL_FROM_URL", "video_url": url},
        }
    ).encode()
    req = urllib.request.Request(
        TIKTOK_INIT,
        data=body,
        headers={
            "Authorization": f"Bearer {tok}",
            "Content-Type": "application/json; charset=UTF-8",
        },
    )
    r = urllib.request.urlopen(req, timeout=60)
    resp = json.loads(r.read().decode())
    pub_id = (resp.get("data") or {}).get("publish_id")
    if pub_id:
        return {"id": pub_id}
    return {"error": resp.get("error") or resp}


def main():
    sched = load_json("june_schedule.json", [])
    urls = load_json("media_urls.json", {})
    done = set(load_json(DONE_FILE, [])) | set(load_json(LEGACY_DONE_FILE, []))

    meta = load_creds("META_CREDS")
    tiktok = load_creds("TIKTOK_CREDS")

    if DRY_RUN:
        print("DRY_RUN active: no posts will be made.", flush=True)
    if not meta:
        print("NOTE: META_CREDS not set -> Instagram & Facebook are skipped.", flush=True)
    if not tiktok:
        print("NOTE: TIKTOK_CREDS not set -> TikTok is skipped.", flush=True)

    now = datetime.now(PT)
    window = timedelta(hours=BACKLOG_HOURS) if BACKLOG_HOURS > 0 else None
    posted = skipped_stale = 0

    for p in sched:
        dt = datetime.strptime(p["datetime"], "%Y-%m-%d %H:%M").replace(tzinfo=PT)
        if dt > now:
            continue  # not due yet
        if window is not None and (now - dt) > window:
            skipped_stale += 1
            continue  # too old; outside catch-up window, leave for manual backfill
        url = urls.get(p["file"])
        if not url:
            continue

        for token in p.get("platforms", []):
            plat = PLATFORM_TOKENS.get(token)
            if not plat:
                continue
            key = f"{plat}:{p['file']}"
            if key in done:
                continue

            tag = f"{plat} {p['brand']} {p['datetime']}"
            if DRY_RUN:
                print(f"WOULD POST {tag}", flush=True)
                continue

            try:
                b = meta.get(p["brand"], {})
                if plat == "ig":
                    ig, tok = b.get("instagram_id"), b.get("page_token")
                    if not (ig and tok):
                        continue
                    res = post_ig_reel(ig, tok, url, p["caption"])
                elif plat == "fb":
                    pid, tok = b.get("page_id"), b.get("page_token")
                    if not (pid and tok):
                        continue
                    res = post_fb_video(pid, tok, url, p["caption"])
                elif plat == "tiktok":
                    tok = tiktok.get(p["brand"], {}).get("access_token")
                    if not tok:
                        continue
                    res = post_tiktok(tok, url, p["caption"])
                else:
                    continue

                if res.get("id"):
                    print(f"OK {tag} -> {res['id']}", flush=True)
                    done.add(key)
                    posted += 1
                else:
                    print(f"ERR {tag}: {res}", flush=True)
            except urllib.error.HTTPError as e:
                print(f"HTTP {tag}: {e.read().decode()[:200]}", flush=True)
            except Exception as e:
                print(f"EXC {tag}: {str(e)[:160]}", flush=True)
            time.sleep(3)

    if not DRY_RUN:
        with open(DONE_FILE, "w") as f:
            json.dump(sorted(done), f, indent=2)

    print(
        f"DONE: {posted} posted this run, {len(done)} total complete, "
        f"{skipped_stale} due-but-stale skipped (outside {BACKLOG_HOURS}h window).",
        flush=True,
    )


if __name__ == "__main__":
    main()
