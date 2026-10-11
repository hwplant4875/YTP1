import os, json, sys, subprocess, urllib.request, urllib.parse, datetime
video, thumb, meta = sys.argv[1:4]
tok = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", urllib.parse.urlencode({
    "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
    "refresh_token": os.environ["YT_REFRESH_TOKEN_" + os.environ.get("YT_CH", "CC")], "grant_type": "refresh_token"}).encode()))["access_token"]
m = json.load(open(meta))
now = datetime.datetime.now(datetime.timezone.utc)
pub = now.replace(hour=10, minute=0, second=0, microsecond=0)  # 19:00 KST
if pub < now + datetime.timedelta(minutes=30): pub += datetime.timedelta(days=1)
body = {"snippet": {k: m[k] for k in ("title", "description", "tags")} | {"categoryId": "27", "defaultLanguage": "en", "defaultAudioLanguage": "en"},
        "status": {"privacyStatus": "private", "publishAt": pub.isoformat().replace("+00:00", "Z"), "selfDeclaredMadeForKids": False}}
size = os.path.getsize(video)
r = urllib.request.Request("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
    data=json.dumps(body).encode(), headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json; charset=UTF-8",
    "X-Upload-Content-Length": str(size), "X-Upload-Content-Type": "video/mp4"})
loc = urllib.request.urlopen(r).headers["Location"]
out = subprocess.run(["curl", "-sS", "-X", "PUT", "-H", "Authorization: Bearer " + tok, "-H", "Content-Type: video/mp4",
                      "--upload-file", video, loc], capture_output=True, text=True, check=True).stdout
vid = json.loads(out)["id"]; print("video", vid, "publishAt", body["status"]["publishAt"], flush=True)
r = urllib.request.Request(f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid}",
    data=open(thumb, "rb").read(), headers={"Authorization": "Bearer " + tok, "Content-Type": "image/jpeg"})
print("thumb", urllib.request.urlopen(r).status)
