"""Upload videos to the Fast German channel (TT token since 2026-10-10) with scheduled publishing. Records results in uploads.json."""
import json
import os
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "uploads.json")


def token():
    d = urllib.parse.urlencode({"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                                "refresh_token": os.environ[os.environ.get("FG_TOKEN_VAR", "YT_REFRESH_TOKEN_TT")], "grant_type": "refresh_token"}).encode()
    return json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", d))["access_token"]


def upload(path, title, description, tags, publish_at, thumb=None):
    T = token()
    meta = {"snippet": {"title": title[:100], "description": description, "tags": tags, "categoryId": "27",
                        "defaultLanguage": "en", "defaultAudioLanguage": "en"},
            "status": {"privacyStatus": "private", "publishAt": publish_at, "selfDeclaredMadeForKids": False}}
    size = os.path.getsize(path)
    req = urllib.request.Request(
        "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
        data=json.dumps(meta).encode(), method="POST",
        headers={"Authorization": "Bearer " + T, "Content-Type": "application/json; charset=UTF-8",
                 "X-Upload-Content-Length": str(size), "X-Upload-Content-Type": "video/mp4"})
    loc = urllib.request.urlopen(req).headers["Location"]
    with open(path, "rb") as f:
        put = urllib.request.Request(loc, data=f.read(), method="PUT",
                                     headers={"Authorization": "Bearer " + T, "Content-Type": "video/mp4"})
        vid = json.load(urllib.request.urlopen(put, timeout=3600))["id"]
    thumb_ok = None
    if thumb:
        try:
            r = urllib.request.Request(f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid}",
                                       data=open(thumb, "rb").read(), method="POST",
                                       headers={"Authorization": "Bearer " + T, "Content-Type": "image/jpeg"})
            urllib.request.urlopen(r).read()
            thumb_ok = True
        except urllib.error.HTTPError as e:
            thumb_ok = f"failed {e.code}: {e.read()[:200]!r}"
    log = json.load(open(LOG)) if os.path.exists(LOG) else {}
    log[os.path.basename(path)] = {"id": vid, "url": f"https://youtu.be/{vid}", "title": title, "publishAt": publish_at,
                                   "thumbnail": thumb_ok}
    json.dump(log, open(LOG, "w"), ensure_ascii=False, indent=1)
    return vid, thumb_ok


if __name__ == "__main__":
    plan = json.load(open(sys.argv[1]))
    done = json.load(open(LOG)) if os.path.exists(LOG) else {}
    for item in plan:
        name = os.path.basename(item["file"])
        if name in done:
            print("skip", name)
            continue
        if not os.path.exists(os.path.join(ROOT, item["file"])):
            print("not rendered yet", name)
            continue
        print(name, upload(os.path.join(ROOT, item["file"]), item["title"], item["description"], item["tags"],
                           item["publishAt"], item.get("thumb") and os.path.join(ROOT, item["thumb"])), flush=True)
