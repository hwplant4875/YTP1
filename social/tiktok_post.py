#!/usr/bin/env python3
"""Send a video to TikTok through the Content Posting API (standard library only).

Environment, per channel key (RS, CC, EC, FP, TT, JC, ...):
  TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET   the TikTok developer app (shared)
  TIKTOK_REFRESH_TOKEN_<KEY>                from social/tiktok_auth.py, valid ~365 days

Modes:
  draft   (default) video lands in the TikTok app inbox; the user finishes and posts it
          there. Needs scope video.upload.
  direct  posts straight to the profile. Needs scope video.publish; until the app passes
          TikTok's audit every post is forced to SELF_ONLY (private).

Usage:
  python3 social/tiktok_post.py check  --channel CC
  python3 social/tiktok_post.py upload --channel CC --video out.mp4 [--mode direct --title "..." --privacy SELF_ONLY]
"""
import argparse
import json
import math
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://open.tiktokapis.com/v2"
MIN_CHUNK = 5 * 1024 * 1024
CHUNK = 10 * 1024 * 1024


def http(method, url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {url} -> {e.code}: {e.read().decode()[:800]}")


def access_token(key):
    rt = os.environ.get(f"TIKTOK_REFRESH_TOKEN_{key}")
    ck, cs = os.environ.get("TIKTOK_CLIENT_KEY"), os.environ.get("TIKTOK_CLIENT_SECRET")
    if not (rt and ck and cs):
        sys.exit(f"missing TIKTOK_CLIENT_KEY / TIKTOK_CLIENT_SECRET / TIKTOK_REFRESH_TOKEN_{key}")
    body = urllib.parse.urlencode({"client_key": ck, "client_secret": cs,
                                   "grant_type": "refresh_token", "refresh_token": rt}).encode()
    res = http("POST", f"{API}/oauth/token/", body, {"Content-Type": "application/x-www-form-urlencoded"})
    if "access_token" not in res:
        sys.exit(f"token refresh failed: {res}")
    if res.get("refresh_token") and res["refresh_token"] != rt:
        print(f"note: TikTok issued a new refresh token for {key}; the old one keeps working "
              f"until it expires ({res.get('refresh_expires_in')} s).", file=sys.stderr)
    return res["access_token"], res.get("scope", "")


def api_json(token, path, payload):
    res = http("POST", f"{API}{path}", json.dumps(payload).encode(),
               {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8"})
    err = res.get("error", {})
    if err.get("code") not in (None, "ok"):
        sys.exit(f"{path} error: {err}")
    return res.get("data", {})


def check(key):
    token, scope = access_token(key)
    info = {}
    if "video.publish" in scope:
        info = api_json(token, "/post/publish/creator_info/query/", {})
    user = http("GET", f"{API}/user/info/?fields=open_id,display_name,username",
                headers={"Authorization": f"Bearer {token}"}).get("data", {}).get("user", {})
    print(json.dumps({"channel": key, "scope": scope, "user": user, "creator_info": info}, ensure_ascii=False))


def upload(a):
    token, scope = access_token(a.channel)
    size = os.path.getsize(a.video)
    chunk = size if size < MIN_CHUNK else CHUNK
    count = max(1, size // chunk)  # remainder rides on the last chunk
    source = {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": chunk, "total_chunk_count": count}

    if a.mode == "direct":
        info = api_json(token, "/post/publish/creator_info/query/", {})
        privacy = a.privacy if a.privacy in info.get("privacy_level_options", []) else "SELF_ONLY"
        post_info = {"title": a.title or "", "privacy_level": privacy,
                     "disable_comment": False, "disable_duet": False, "disable_stitch": False}
        data = api_json(token, "/post/publish/video/init/", {"post_info": post_info, "source_info": source})
    else:
        data = api_json(token, "/post/publish/inbox/video/init/", {"source_info": source})

    pid, up = data["publish_id"], data["upload_url"]
    with open(a.video, "rb") as f:
        for i in range(count):
            start = i * chunk
            end = size - 1 if i == count - 1 else start + chunk - 1
            f.seek(start)
            http("PUT", up, f.read(end - start + 1),
                 {"Content-Type": "video/mp4", "Content-Range": f"bytes {start}-{end}/{size}"})

    for _ in range(120):
        st = api_json(token, "/post/publish/status/fetch/", {"publish_id": pid})
        s = st.get("status")
        if s in ("SEND_TO_USER_INBOX", "PUBLISH_COMPLETE"):
            print(json.dumps({"channel": a.channel, "publish_id": pid, "status": s,
                              "post_ids": st.get("publicaly_available_post_id", [])}))
            return
        if s == "FAILED":
            sys.exit(f"TikTok processing failed: {st}")
        time.sleep(5)
    sys.exit(f"publish {pid} still processing after 10 minutes")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--channel", required=True)
    u = sub.add_parser("upload")
    u.add_argument("--channel", required=True)
    u.add_argument("--video", required=True)
    u.add_argument("--mode", choices=["draft", "direct"], default="draft")
    u.add_argument("--title", help="caption incl. hashtags (direct mode)")
    u.add_argument("--privacy", default="SELF_ONLY",
                   help="PUBLIC_TO_EVERYONE, MUTUAL_FOLLOW_FRIENDS, FOLLOWER_OF_CREATOR or SELF_ONLY")
    a = p.parse_args()
    a.channel = a.channel.upper()
    check(a.channel) if a.cmd == "check" else upload(a)


if __name__ == "__main__":
    main()
