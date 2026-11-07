"""PEEK. ep_money narration: Mattes (eleven_v4, default settings), one call per beat with timestamps.
usage: python3 tts.py [b01 b02 ...]  -> /mnt/project-files/plans/peek/longform/ep_money/audio/takes/<id>.mp3 + .json"""
import os, json, base64, urllib.request, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "/mnt/project-files/plans/peek/longform/ep_money/audio/takes/"
VOICE = "DrBEKFgWMDWUG6bjTSTk"          # Mattes, the channel's narrator since X-RAY ZOO
key = os.environ["ELEVENLABS_JC_API_KEY"]   # never the pay-as-you-go key
S = json.load(open(os.path.join(HERE, "script_v1.json")))
def say(t):  # spoken forms only; captions keep the written text
    return (t.replace("S&P 500", "S and P five hundred").replace("November 5th", "November fifth")
             .replace("re-priced", "repriced"))
def call(text, prev, nxt):
    body = {"text": text, "model_id": "eleven_v4"}
    if prev: body["previous_text"] = prev
    if nxt: body["next_text"] = nxt
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_192",
                                 data=json.dumps(body).encode(), headers={"xi-api-key": key, "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=300))
only = sys.argv[1:]
for i, b in enumerate(S):
    if only and b["id"] not in only: continue
    text = say(b["text"])
    prev = say(S[i - 1]["text"]) if i > 0 else None
    nxt = say(S[i + 1]["text"]) if i + 1 < len(S) else None
    d = None
    for att in range(3):
        try: d = call(text, prev, nxt); break
        except Exception as e:
            print(b["id"], "error", e.read().decode()[:300] if hasattr(e, "read") else e, file=sys.stderr); time.sleep(5)
    if d is None: sys.exit(1)
    open(OUT + b["id"] + ".mp3", "wb").write(base64.b64decode(d["audio_base64"]))
    json.dump({"id": b["id"], "text": text, "display": b["text"], "alignment": d["alignment"]}, open(OUT + b["id"] + ".json", "w"))
    print(b["id"], "ok", round(d["alignment"]["character_end_times_seconds"][-1], 2), "s", len(text), "chars", flush=True)
