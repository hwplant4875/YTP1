"""Upload the Odd Ages short PRIVATE (no publishAt) to the FP channel.
  python3 upload.py [--dry]"""
import json, os, sys, time, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from script import TITLE
VID = os.path.join(HERE, "out/oa01_dancing_plague.mp4")
desc = ("In July 1518, one woman in Strasbourg started dancing and could not stop. Within weeks, reportedly up to "
        "400 people had joined her, and the city's cure only made it worse.\n\n"
        "Music: \"Master of the Feast\" by Kevin MacLeod (incompetech.com), licensed under Creative Commons: "
        "By Attribution 4.0, creativecommons.org/licenses/by/4.0/\n"
        "Characters: Microsoft Rocketbox Avatar Library (MIT License), github.com/microsoft/Microsoft-Rocketbox\n\n"
        "#history #dancingplague #strasbourg #weirdhistory #shorts")
tags = ["history", "dancing plague", "dancing plague of 1518", "Strasbourg", "1518", "medieval", "weird history",
        "history facts", "Odd Ages", "shorts"]
assert len(desc) < 5000 and len(TITLE) <= 100


def tok():
    d = urllib.parse.urlencode({"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                                "refresh_token": os.environ["YT_REFRESH_TOKEN_FP"], "grant_type": "refresh_token"}).encode()
    return json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", d))["access_token"]


if "--dry" in sys.argv:
    print(TITLE); print(desc); print(tags); sys.exit()
T = tok()
body = {"snippet": {"title": TITLE, "description": desc, "tags": tags, "categoryId": "27",
                    "defaultLanguage": "en", "defaultAudioLanguage": "en"},
        "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": False}}
size = os.path.getsize(VID)
req = urllib.request.Request("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                             data=json.dumps(body).encode(), headers={"Authorization": "Bearer " + T,
                             "Content-Type": "application/json; charset=UTF-8", "X-Upload-Content-Type": "video/mp4",
                             "X-Upload-Content-Length": str(size)})
loc = urllib.request.urlopen(req).headers["Location"]
data = open(VID, "rb").read()
res = None
for attempt in range(5):
    try:
        r = urllib.request.Request(loc, data=data, method="PUT", headers={"Authorization": "Bearer " + T, "Content-Type": "video/mp4"})
        res = json.load(urllib.request.urlopen(r, timeout=600)); break
    except Exception as e:
        print("retry", e, flush=True); time.sleep(5)
print("VIDEO", res["id"], res["status"].get("privacyStatus"), res["status"].get("publishAt"), flush=True)
