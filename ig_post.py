#!/usr/bin/env python3
"""Always-on IG reel poster. Runs on GitHub Actions every 30 min.
Posts Chaya + Ren reels due at their scheduled June time. Self-dedupes via ig_done.json committed back to the repo."""
import json, os, time, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timezone, timedelta

GRAPH="https://graph.facebook.com/v22.0"
# Pacific time (schedule is in user's local PT)
PT = timezone(timedelta(hours=-7))  # PDT for June

creds = json.loads(os.environ["META_CREDS"])  # {brand:{instagram_id,page_token}}
sched = json.load(open("june_schedule.json"))
urls  = json.load(open("media_urls.json"))
done  = set(json.load(open("ig_done.json"))) if os.path.exists("ig_done.json") else set()

def post_reel(ig, tok, url, cap):
    data=urllib.parse.urlencode({"media_type":"REELS","video_url":url,"caption":cap,"access_token":tok}).encode()
    r=urllib.request.urlopen(f"{GRAPH}/{ig}/media",data=data,timeout=60)
    cid=json.loads(r.read().decode()).get("id")
    if not cid: return {"error":"no container"}
    for _ in range(40):
        time.sleep(6)
        s=urllib.request.urlopen(f"{GRAPH}/{cid}?fields=status_code&access_token={tok}",timeout=30)
        st=json.loads(s.read().decode()).get("status_code")
        if st=="FINISHED": break
        if st=="ERROR": return {"error":"processing"}
    pub=urllib.parse.urlencode({"creation_id":cid,"access_token":tok}).encode()
    r=urllib.request.urlopen(f"{GRAPH}/{ig}/media_publish",data=pub,timeout=60)
    return json.loads(r.read().decode())

now=datetime.now(PT)
posted=0
for p in sched:
    if "meta_ig" not in p["platforms"] or p["brand"] not in ("chaya","ren"): continue
    key="ig:"+p["file"]
    if key in done: continue
    dt=datetime.strptime(p["datetime"],"%Y-%m-%d %H:%M").replace(tzinfo=PT)
    if dt>now: continue  # not due yet
    if p["file"] not in urls: continue
    b=creds.get(p["brand"],{})
    ig=b.get("instagram_id"); tok=b.get("page_token")
    if not(ig and tok): continue
    try:
        res=post_reel(ig,tok,urls[p["file"]],p["caption"])
        if res.get("id"):
            print(f"OK {p['brand']} {p['datetime']} -> {res['id']}",flush=True)
            done.add(key); posted+=1
        else:
            print(f"ERR {p['brand']} {p['datetime']}: {res}",flush=True)
    except urllib.error.HTTPError as e:
        print(f"HTTP {p['brand']}: {e.read().decode()[:150]}",flush=True)
    except Exception as e:
        print(f"EXC {p['brand']}: {str(e)[:120]}",flush=True)
    time.sleep(3)

json.dump(sorted(done),open("ig_done.json","w"),indent=2)
print(f"DONE: {posted} posted, {len(done)} total complete",flush=True)
