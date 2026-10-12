"""Schedule the 5 news shorts (user 2026-10-12): private upload with publishAt, picture sources credited in the description."""
import json, os, sys, urllib.parse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))
import upload as U
HERE = os.path.dirname(__file__)
PREV = "/mnt/project-files/fast_german/preview/shorts_v2/"
SRC = json.load(open("/mnt/project-files/fast_german/cache/photos/news2/sources.json"))
TAGS = ["germany", "german news", "learn german", "german", "germany travel", "fast german"]
PLAN = [  # id, publishAt (UTC), hook, extra tags
 ("n02_ragebait", "2026-10-12T17:00:00Z", "Germany's Youth Word of the Year 2026 is Ragebait, and the top 3 are all English. The German version: Wut-Köder.",
  ["jugendwort 2026", "ragebait", "jugendwort des jahres", "wut-köder"]),
 ("n04_bahn_alkoholverbot", "2026-10-13T09:30:00Z", "From October 15, Deutsche Bahn bans drinking alcohol at about 5,400 train stations in Germany. What is still allowed, and what happens if you break the rule.",
  ["deutsche bahn", "alkoholverbot", "germany train station", "travel germany tips"]),
 ("n03_oktoberfest", "2026-10-13T15:00:00Z", "Oktoberfest 2026 set a new all-time record: 7.4 million visitors, 6.7 million Maß of beer, and up to €15.90 for one Maß.",
  ["oktoberfest 2026", "oktoberfest", "munich", "wiesn", "maß"]),
 ("n01_zwiebelmarkt", "2026-10-14T10:00:00Z", "Weimar's Zwiebelmarkt: a German onion festival since 1653, with 250,000 visitors and its own onion queen, the Zwiebelkönigin.",
  ["zwiebelmarkt", "weimar", "german festival", "zwiebelkönigin"]),
 ("n05_zeitumstellung", "2026-10-14T17:00:00Z", "On Sunday, October 25, Germany's clocks go back from 3:00 to 2:00. Zeitumstellung, Winterzeit, and one extra hour of sleep.",
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


if __name__ == "__main__":
    only = sys.argv[1:]
    done = json.load(open(U.LOG)) if os.path.exists(U.LOG) else {}
    for sid, at, hook, tags in PLAN:
        if only and sid not in only:
            continue
        if sid + ".mp4" in done:
            print("skip", sid); continue
        spec = json.load(open(os.path.join(HERE, sid + ".json")))
        hosts = sources(sid)
        desc = (hook + "\n\nGerman news for travellers and learners, in under 30 seconds. Follow for more German news."
                + ("\n\nPictures: " + ", ".join(hosts) + " (all rights with their owners; shown for news reporting)." if hosts else "")
                + "\n\n#germany #germannews #learngerman #shorts")
        print(sid, U.upload(PREV + sid + ".mp4", spec["title"] + " #shorts", desc, TAGS + tags, at), flush=True)
