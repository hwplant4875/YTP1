#!/usr/bin/env python3
"""Post a video to TikTok through Zernio (zernio.com, formerly Late). Standard library only.

Environment: ZERNIO_API_KEY (one key covers every account connected in the Zernio dashboard).

Channel keys map to TikTok usernames (see /mnt/project-files/access/social-connections.md):
  RA = Fast German (@fast_german1), HP = Korean in 60s (@koreanin60s)

Usage:
  python3 social/zernio_post.py accounts
  python3 social/zernio_post.py upload --channel RA --video out.mp4 --caption-file cap.txt \
      [--when 2026-10-20T22:00 --tz Asia/Seoul | --now | --draft] [--privacy PUBLIC_TO_EVERYONE] [--cover-ms 1000]
  python3 social/zernio_post.py status --post POST_ID

Without --when/--now/--draft nothing is sent (dry run prints the request body).
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://zernio.com/api/v1"
CHANNELS = {"RA": "fast_german1", "HP": "koreanin60s"}


def call(method, path, body=None):
    key = os.environ.get("ZERNIO_API_KEY") or sys.exit("missing ZERNIO_API_KEY")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{API}{path}", data=data, method=method,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} -> {e.code}: {e.read().decode()[:800]}")


def accounts():
    res = call("GET", "/accounts")
    return res.get("accounts", res if isinstance(res, list) else [])


def find_account(channel):
    want = CHANNELS.get(channel, channel).lstrip("@").lower()
    for a in accounts():
        names = {str(a.get(k, "")).lstrip("@").lower() for k in ("username", "handle", "displayName", "name")}
        if a.get("platform") == "tiktok" and want in names:
            return a["_id"]
    sys.exit(f"no connected TikTok account matches {want}; run `accounts` to see what Zernio has")


def upload_media(path):
    size = os.path.getsize(path)
    pre = call("POST", "/media/presign", {"filename": os.path.basename(path), "contentType": "video/mp4", "size": size})
    with open(path, "rb") as f:
        req = urllib.request.Request(pre["uploadUrl"], data=f.read(), method="PUT",
                                     headers={"Content-Type": "video/mp4"})
        urllib.request.urlopen(req, timeout=600).read()
    return pre["publicUrl"]


def upload(a):
    caption = open(a.caption_file, encoding="utf-8").read().strip() if a.caption_file else (a.caption or "")
    body = {
        "content": caption,
        "platforms": [{"platform": "tiktok", "accountId": find_account(a.channel)}],
        "tiktokSettings": {
            "privacy_level": a.privacy, "allow_comment": True, "allow_duet": True, "allow_stitch": True,
            "content_preview_confirmed": True, "express_consent_given": True,
            "video_cover_timestamp_ms": a.cover_ms, "draft": a.draft,
        },
    }
    if a.when:
        body.update(scheduledFor=a.when, timezone=a.tz)
    elif a.now:
        body["publishNow"] = True
    elif not a.draft:
        body["mediaItems"] = [{"type": "video", "url": "<uploaded on a real run>"}]
        print(json.dumps({"dry_run": True, "body": body}, ensure_ascii=False, indent=1))
        return
    body["mediaItems"] = [{"type": "video", "url": upload_media(a.video)}]
    post = call("POST", "/posts", body)
    print(json.dumps(post, ensure_ascii=False))


def status(post_id):
    for _ in range(60):
        p = call("GET", f"/posts/{post_id}")
        post = p.get("post", p)
        if post.get("status") not in ("pending", "publishing", "processing"):
            print(json.dumps(post, ensure_ascii=False))
            return
        time.sleep(10)
    print(json.dumps(post, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("accounts")
    u = sub.add_parser("upload")
    u.add_argument("--channel", required=True, help="RA, HP or a TikTok username")
    u.add_argument("--video", required=True)
    u.add_argument("--caption")
    u.add_argument("--caption-file")
    u.add_argument("--privacy", default="PUBLIC_TO_EVERYONE")
    u.add_argument("--cover-ms", type=int, default=1000)
    mode = u.add_mutually_exclusive_group()
    mode.add_argument("--when", help="local time, e.g. 2026-10-20T22:00")
    mode.add_argument("--now", action="store_true")
    mode.add_argument("--draft", action="store_true", help="send to the TikTok app inbox instead")
    u.add_argument("--tz", default="Asia/Seoul")
    s = sub.add_parser("status")
    s.add_argument("--post", required=True)
    a = p.parse_args()
    if a.cmd == "accounts":
        print(json.dumps([{k: x.get(k) for k in ("_id", "platform", "username", "displayName", "status")}
                          for x in accounts()], ensure_ascii=False, indent=1))
    elif a.cmd == "upload":
        a.channel = a.channel.upper() if a.channel.upper() in CHANNELS else a.channel
        upload(a)
    else:
        status(a.post)


if __name__ == "__main__":
    main()
