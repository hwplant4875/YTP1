"""Schedule the 5 news shorts (user 2026-10-12): private upload with publishAt.
Description (user 2026-10-13): one or two sentences, as if a young German woman wrote them; warm, trendy, no emoji, no source list.
`fix` re-writes the descriptions of the already uploaded videos."""
import json, os, sys, urllib.parse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))
import upload as U
HERE = os.path.dirname(__file__)
PREV = "/mnt/project-files/fast_german/preview/shorts_v2/"
SRC = json.load(open("/mnt/project-files/fast_german/cache/photos/news2/sources.json"))
TAGS = ["germany", "german news", "learn german", "german", "germany travel", "fast german"]
PLAN = [  # id, publishAt (UTC), hook, extra tags
 ("n02_ragebait", "2026-10-12T17:00:00Z", "Okay so our youth word of the year is literally English. Ragebait, or Wut-Köder if you want to sound German about it.",
  ["jugendwort 2026", "ragebait", "jugendwort des jahres", "wut-köder"]),
 ("n04_bahn_alkoholverbot", "2026-10-13T09:30:00Z", "Heads up before your next train trip: from October 15 no more beer on the platform. Honestly, I'll miss my Feierabendbier at the station.",
  ["deutsche bahn", "alkoholverbot", "germany train station", "travel germany tips"]),
 ("n03_oktoberfest", "2026-10-13T15:00:00Z", "7.4 million people, a new record, and I still couldn't get a table. Prost to everyone who survived this year's Wiesn.",
  ["oktoberfest 2026", "oktoberfest", "munich", "wiesn", "maß"]),
 ("n01_zwiebelmarkt", "2026-10-14T10:00:00Z", "Yes, we have a whole festival for onions, and yes, it's the cosiest weekend of autumn. Come to Weimar with me next year?",
  ["zwiebelmarkt", "weimar", "german festival", "zwiebelkönigin"]),
 ("n05_zeitumstellung", "2026-10-14T17:00:00Z", "One extra hour of sleep this Sunday, the only part of German autumn I truly love. Gute Nacht, see you on the other side.",
  ["zeitumstellung", "winterzeit", "daylight saving time germany", "clocks go back"]),
]


def sources(sid):
    spec = json.load(open(os.path.join(HERE, sid + ".json")))
    keys = [e["src"].split("/")[-1].rsplit(".", 1)[0] for sc in spec["scenes"] for e in sc["els"] if e.get("type") == "photo"]
    hosts = []
    for k in keys:
        h = urllib.parse.urlparse(SRC[k]["url"]).netloc.replace("www.", "") if k in SRC else None
        if h and h not in hosts:
            hosts.append(h)
    return hosts


def fix():
    import urllib.request
    T = U.token()
    log = json.load(open(U.LOG))
    for sid, at, hook, tags in PLAN:
        vid = log[sid + ".mp4"]["id"]
        H = {"Authorization": "Bearer " + T, "Content-Type": "application/json"}
        sn = json.load(urllib.request.urlopen(urllib.request.Request(f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={vid}", headers=H)))["items"][0]["snippet"]
        body = {"id": vid, "snippet": {k: sn[k] for k in ("title", "tags", "categoryId", "defaultLanguage", "defaultAudioLanguage") if k in sn}}
        body["snippet"]["description"] = hook + "\n\n#germany #germannews #learngerman #shorts"
        r = json.load(urllib.request.urlopen(urllib.request.Request("https://www.googleapis.com/youtube/v3/videos?part=snippet", data=json.dumps(body).encode(), method="PUT", headers=H)))
        print(sid, r["snippet"]["description"].splitlines()[0])


if __name__ == "__main__":
    if sys.argv[1:] == ["fix"]:
        fix(); sys.exit()
    only = sys.argv[1:]
    done = json.load(open(U.LOG)) if os.path.exists(U.LOG) else {}
    for sid, at, hook, tags in PLAN:
        if only and sid not in only:
            continue
        if sid + ".mp4" in done:
            print("skip", sid); continue
        spec = json.load(open(os.path.join(HERE, sid + ".json")))
        hosts = sources(sid)
        desc = hook + "\n\n#germany #germannews #learngerman #shorts"   # user 2026-10-13: short personal voice, no source list, no emoji
        print(sid, U.upload(PREV + sid + ".mp4", spec["title"] + " #shorts", desc, TAGS + tags, at), flush=True)
