#!/usr/bin/env python3
"""Get a TikTok refresh token for one account. Run on your own computer (Python 3 only).

  python3 tiktok_auth.py --client-key XXX --client-secret YYY --redirect https://hwplant4875.github.io/YTP1/

1. A login link is printed. Open it in a browser where the right TikTok account is
   signed in and press Authorize.
2. The browser lands on the redirect page. Copy the WHOLE address from the address bar
   and paste it here.
3. The refresh token is printed. Put it in the environment as TIKTOK_REFRESH_TOKEN_<KEY>.
   Do not paste it into chat.
"""
import argparse
import json
import secrets
import urllib.parse
import urllib.request

SCOPES = "user.info.basic,video.upload,video.publish"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--client-key", required=True)
    p.add_argument("--client-secret", required=True)
    p.add_argument("--redirect", required=True, help="exactly as registered in the TikTok app")
    p.add_argument("--scopes", default=SCOPES)
    a = p.parse_args()

    state = secrets.token_urlsafe(16)
    url = "https://www.tiktok.com/v2/auth/authorize/?" + urllib.parse.urlencode({
        "client_key": a.client_key, "response_type": "code", "scope": a.scopes,
        "redirect_uri": a.redirect, "state": state})
    print("\n1) Open this link and press Authorize:\n\n" + url + "\n")
    back = input("2) Paste the full address you were sent to: ").strip()
    q = urllib.parse.parse_qs(urllib.parse.urlparse(back).query)
    if q.get("state", [""])[0] != state:
        raise SystemExit("state mismatch: paste the address from this login attempt")
    code = q["code"][0]

    body = urllib.parse.urlencode({"client_key": a.client_key, "client_secret": a.client_secret,
                                   "code": code, "grant_type": "authorization_code",
                                   "redirect_uri": a.redirect}).encode()
    req = urllib.request.Request("https://open.tiktokapis.com/v2/oauth/token/", data=body,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    res = json.loads(urllib.request.urlopen(req).read().decode())
    if "refresh_token" not in res:
        raise SystemExit(f"failed: {res}")
    print(f"\nscopes granted: {res.get('scope')}")
    print(f"refresh token valid for {int(res.get('refresh_expires_in', 0)) // 86400} days")
    print("\nTIKTOK_REFRESH_TOKEN_<KEY>=" + res["refresh_token"])


if __name__ == "__main__":
    main()
