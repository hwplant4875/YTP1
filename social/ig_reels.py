#!/usr/bin/env python3
"""Publish a Reel to Instagram through the Graph API (standard library only).

Credentials come from environment variables, one set per channel key
(RS, CC, EC, FP, TT, JC, ...):

  IG_TOKEN_<KEY>     access token (Facebook system-user token or Instagram Login token)
  IG_USER_ID_<KEY>   Instagram professional account id
  IG_LOGIN_<KEY>     "facebook" (graph.facebook.com, local file upload) or
                     "instagram" (graph.instagram.com, needs a public video URL; default)

For the legacy single account, IG_ACCESS_TOKEN / IG_USER_ID are used when KEY is "DEFAULT".

Usage:
  python3 social/ig_reels.py check  --channel CC
  python3 social/ig_reels.py upload --channel CC --video out.mp4 --caption-file cap.txt [--cover-ms 1500] [--no-publish]
  python3 social/ig_reels.py upload --channel CC --video-url https://... --caption "..."

--no-publish creates the media container and waits until Instagram has processed it,
but does not publish it (unpublished containers expire after 24 hours). Use it to test
a token and a file without anything going public.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

API_VERSION = "v23.0"
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def creds(key):
    if key == "DEFAULT":
        token, uid, login = os.environ.get("IG_ACCESS_TOKEN"), os.environ.get("IG_USER_ID"), "instagram"
    else:
        token = os.environ.get(f"IG_TOKEN_{key}")
        uid = os.environ.get(f"IG_USER_ID_{key}")
        login = os.environ.get(f"IG_LOGIN_{key}", "instagram").lower()
    if not token or not uid:
        sys.exit(f"missing IG_TOKEN_{key} / IG_USER_ID_{key}")
    host = "graph.facebook.com" if login == "facebook" else "graph.instagram.com"
    return token, uid, host, login


def call(method, url, params=None, data=None, headers=None):
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    body = data
    if isinstance(data, dict):
        body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {url.split('?')[0]} -> {e.code}: {e.read().decode()[:800]}")


def check(key):
    token, uid, host, login = creds(key)
    base = f"https://{host}/{API_VERSION}"
    me = call("GET", f"{base}/{uid}", {"fields": "username,media_count", "access_token": token})
    lim = call("GET", f"{base}/{uid}/content_publishing_limit",
               {"fields": "quota_usage,config", "access_token": token})
    print(json.dumps({"channel": key, "login": login, "account": me, "publishing_limit": lim}, ensure_ascii=False))


MEDIA_BRANCH = "ig-media"


def push_branch(files, message):
    """Force-push a one-commit branch holding exactly `files` to the repo's origin."""
    run = lambda *a: subprocess.run(a, check=True, capture_output=True, text=True)
    remote = run("git", "-C", REPO_DIR, "remote", "get-url", "origin").stdout.strip()
    tmp = tempfile.mkdtemp(prefix="igmedia-")
    run("git", "init", "-q", tmp)
    for name, src in files.items():
        shutil.copy(src, os.path.join(tmp, name)) if src else open(os.path.join(tmp, name), "w").write(
            "Temporary media for Instagram to fetch. Emptied after every upload.\n")
        run("git", "-C", tmp, "add", name)
    run("git", "-C", tmp, "-c", "user.name=ytp1-bot", "-c", "user.email=bot@localhost", "commit", "-q", "-m", message)
    subprocess.run(["git", "-C", tmp, "push", "-f", "-q", remote, f"HEAD:refs/heads/{MEDIA_BRANCH}"],
                   capture_output=True)  # the proxy can report a harmless negotiation error
    shutil.rmtree(tmp, ignore_errors=True)
    return remote


def host_publicly(path):
    """Instagram Login tokens can't take a local file, so put it on a throwaway branch of the
    public repo and hand Instagram the raw URL. The branch is emptied again afterwards."""
    name = f"{int(time.time())}.mp4"
    remote = push_branch({name: path}, "temporary media for Instagram fetch")
    owner_repo = remote.rstrip("/").removesuffix(".git").split("github.com")[-1].strip("/:")
    if "/git/" in owner_repo:  # local proxy remotes look like http://.../git/owner/repo
        owner_repo = owner_repo.split("/git/")[-1]
    url = f"https://raw.githubusercontent.com/{owner_repo}/{MEDIA_BRANCH}/{name}"
    for _ in range(12):  # wait until the raw URL serves the file
        try:
            urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30)
            return url
        except urllib.error.URLError:
            time.sleep(5)
    sys.exit(f"pushed media is not reachable at {url}")


def drop_hosted():
    push_branch({"README.md": None}, "empty after upload")


def wait_ready(base, cid, token):
    for _ in range(120):
        st = call("GET", f"{base}/{cid}", {"fields": "status_code,status", "access_token": token})
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            sys.exit(f"container {cid} failed: {st}")
        time.sleep(5)
    sys.exit(f"container {cid} still not ready after 10 minutes")


def upload(a):
    token, uid, host, login = creds(a.channel)
    base = f"https://{host}/{API_VERSION}"
    caption = a.caption or ""
    if a.caption_file:
        caption = open(a.caption_file, encoding="utf-8").read().strip()
    params = {"media_type": "REELS", "caption": caption, "share_to_feed": "true", "access_token": token}
    if a.cover_ms is not None:
        params["thumb_offset"] = str(a.cover_ms)

    hosted = False
    if a.video_url:
        params["video_url"] = a.video_url
        cid = call("POST", f"{base}/{uid}/media", data=params)["id"]
    elif login == "facebook":
        params["upload_type"] = "resumable"
        cid = call("POST", f"{base}/{uid}/media", data=params)["id"]
        size = os.path.getsize(a.video)
        with open(a.video, "rb") as f:
            res = call("POST", f"https://rupload.facebook.com/ig-api-upload/{API_VERSION}/{cid}",
                       data=f.read(),
                       headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)})
        if not res.get("success"):
            sys.exit(f"byte upload failed: {res}")
    else:
        url, hosted = host_publicly(a.video), True
        params["video_url"] = url
        cid = call("POST", f"{base}/{uid}/media", data=params)["id"]

    try:
        wait_ready(base, cid, token)
        if a.no_publish:
            print(json.dumps({"channel": a.channel, "container": cid, "published": False}))
            return
        media_id = call("POST", f"{base}/{uid}/media_publish", data={"creation_id": cid, "access_token": token})["id"]
        link = call("GET", f"{base}/{media_id}", {"fields": "permalink", "access_token": token}).get("permalink")
        print(json.dumps({"channel": a.channel, "media_id": media_id, "permalink": link, "published": True}))
    finally:
        if hosted:
            drop_hosted()


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--channel", required=True)
    u = sub.add_parser("upload")
    u.add_argument("--channel", required=True)
    src = u.add_mutually_exclusive_group(required=True)
    src.add_argument("--video")
    src.add_argument("--video-url")
    u.add_argument("--caption")
    u.add_argument("--caption-file")
    u.add_argument("--cover-ms", type=int)
    u.add_argument("--no-publish", action="store_true")
    a = p.parse_args()
    a.channel = a.channel.upper()
    check(a.channel) if a.cmd == "check" else upload(a)


if __name__ == "__main__":
    main()
