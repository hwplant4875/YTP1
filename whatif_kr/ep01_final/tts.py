import json, os, sys, urllib.request
KEY = os.environ["ELEVENLABS_JC_API_KEY"]; VOICE = "BbsagRO6ohd8MKPS2Ob0"
d = json.load(open("script.json"))
only = set(sys.argv[1:])
for x in d:
    out = f"vo/{x['id']}.mp3"
    if (os.path.exists(out) and not only) or (only and x["id"] not in only): continue
    body = json.dumps({"text": x["text"], "model_id": "eleven_v4", "language_code": "ko",
                       "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.2}}).encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_192", body,
                                 {"xi-api-key": KEY, "Content-Type": "application/json"})
    open(out, "wb").write(urllib.request.urlopen(req).read()); print(out)
