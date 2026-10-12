"""Private (unscheduled) long-form upload with captions: python3 upload_long.py <mp4> <thumb.jpg|-> <meta.json> [captions.srt]
meta.json: title, description, tags. The user runs the thumbnail A/B test in Studio."""
import os, json, sys, subprocess, urllib.request, urllib.parse
video, thumb, meta = sys.argv[1:4]; srt = sys.argv[4] if len(sys.argv) > 4 else None
tok = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", urllib.parse.urlencode({
    "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
    "refresh_token": os.environ["YT_REFRESH_TOKEN_" + os.environ.get("YT_CH", "CC")], "grant_type": "refresh_token"}).encode()))["access_token"]
m = json.load(open(meta)); H = {"Authorization": "Bearer " + tok}
body = {"snippet": {k: m[k] for k in ("title", "description", "tags")} | {"categoryId": "27", "defaultLanguage": "en", "defaultAudioLanguage": "en"},
        "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False}}
r = urllib.request.Request("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
    data=json.dumps(body).encode(), headers=H | {"Content-Type": "application/json; charset=UTF-8",
    "X-Upload-Content-Length": str(os.path.getsize(video)), "X-Upload-Content-Type": "video/mp4"})
loc = urllib.request.urlopen(r).headers["Location"]
out = subprocess.run(["curl", "-sS", "-X", "PUT", "-H", "Authorization: Bearer " + tok, "-H", "Content-Type: video/mp4", "--upload-file", video, loc],
                     capture_output=True, text=True, check=True).stdout
vid = json.loads(out)["id"]; print("video", vid, flush=True)
if thumb != "-":
    r = urllib.request.Request(f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid}", data=open(thumb, "rb").read(), headers=H | {"Content-Type": "image/jpeg"})
    print("thumb", urllib.request.urlopen(r).status, flush=True)
if srt:
    b = "k60boundary"; meta_ = json.dumps({"snippet": {"videoId": vid, "language": "en", "name": "English"}})
    data = (f"--{b}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{meta_}\r\n--{b}\r\nContent-Type: application/octet-stream\r\n\r\n").encode() + open(srt, "rb").read() + f"\r\n--{b}--".encode()
    r = urllib.request.Request("https://www.googleapis.com/upload/youtube/v3/captions?uploadType=multipart&part=snippet", data=data, headers=H | {"Content-Type": f"multipart/related; boundary={b}"})
    print("captions", urllib.request.urlopen(r).status)
