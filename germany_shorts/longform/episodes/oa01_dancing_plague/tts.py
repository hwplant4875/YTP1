"""Generate the narration line by line (ElevenLabs eleven_v4, Mattes) with character timestamps; cached in .cache/."""
import base64, json, os, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from script import LINES
VOICE = "DrBEKFgWMDWUG6bjTSTk"
C = os.path.join(HERE, ".cache"); os.makedirs(C, exist_ok=True)
for i, (say, _, _) in enumerate(LINES):
    out = os.path.join(C, f"l{i:02d}.json")
    if os.path.exists(out): continue
    prev = " ".join(l[0] for l in LINES[max(0, i - 2):i]); nxt = LINES[i + 1][0] if i + 1 < len(LINES) else ""
    body = {"text": say, "model_id": "eleven_v4", "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "speed": 1.0},
            "previous_text": prev or None, "next_text": nxt or None}
    body = {k: v for k, v in body.items() if v is not None}
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_192",
                                 json.dumps(body).encode(), {"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.HTTPError as e:
        sys.exit(f"{e.code} {e.read()[:300]}")
    open(os.path.join(C, f"l{i:02d}.mp3"), "wb").write(base64.b64decode(d["audio_base64"]))
    json.dump(d["alignment"], open(out, "w"))
    print(i, len(say), "chars", flush=True)
