"""Upload a video to the RageStyles channel (private by default) via the YouTube Data API.
usage: python3 yt_upload.py meta.json video.mp4        -> prints the video id
       python3 yt_upload.py --whoami                     -> prints the channel the token belongs to
meta.json: {"title": ..., "description": ..., "tags": [...], "privacy": "private", "categoryId": "17"}
Env: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN_RS (override with YT_TOKEN_VAR)."""
import json, os, sys, urllib.request, urllib.parse


def token():
    body = urllib.parse.urlencode({'client_id': os.environ['YT_CLIENT_ID'], 'client_secret': os.environ['YT_CLIENT_SECRET'],
                                   'refresh_token': os.environ[os.environ.get('YT_TOKEN_VAR', 'YT_REFRESH_TOKEN_RS')], 'grant_type': 'refresh_token'}).encode()
    return json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token', body))['access_token']


def whoami(tok):
    r = urllib.request.Request('https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true', headers={'Authorization': 'Bearer ' + tok})
    items = json.load(urllib.request.urlopen(r)).get('items', [])
    return [(i['id'], i['snippet']['title']) for i in items]


def upload(tok, meta, path):
    body = {'snippet': {'title': meta['title'][:100], 'description': meta.get('description', ''), 'tags': meta.get('tags', []),
                        'categoryId': meta.get('categoryId', '17')},
            'status': {'privacyStatus': meta.get('privacy', 'private'), 'selfDeclaredMadeForKids': False}}
    size = os.path.getsize(path)
    init = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',
                                  data=json.dumps(body).encode(), method='POST',
                                  headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json; charset=UTF-8',
                                           'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(size)})
    loc = urllib.request.urlopen(init).headers['Location']
    with open(path, 'rb') as f:
        put = urllib.request.Request(loc, data=f.read(), method='PUT', headers={'Content-Type': 'video/mp4', 'Content-Length': str(size)})
        return json.load(urllib.request.urlopen(put))['id']


if __name__ == '__main__':
    tok = token()
    if sys.argv[1] == '--whoami': print(whoami(tok)); sys.exit()
    print(upload(tok, json.load(open(sys.argv[1])), sys.argv[2]))
