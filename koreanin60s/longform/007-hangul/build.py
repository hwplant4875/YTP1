"""Long-form #7 builder: Learn the Korean Alphabet in 15 Minutes (16:9, cream lesson style, layout v4: no intro/chapter cards).
Voice: Jennie on ElevenLabs v3 (JC key), one request per beat; each visual switches when its sentence starts, pauses squeezed to 0.5 s.
Usage: python3 build.py <outdir> [sample]  -> short.html, timeline.json, mix.wav; render: VW=1920 VH=1080 node ../../engine/prender.js <outdir> 30 4"""
import base64, hashlib, json, os, subprocess, sys, wave
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from script import CHAPTERS, OUTRO
from sound import load
SR = 48000; VOICE = "z6Kj0hecH20CdetSElRT"; MODEL = "eleven_v3"
KEY = os.environ.get("ELEVENLABS_JC_API_KEY") or os.environ["ELEVENLABS_API_KEY"]
CACHE = os.path.expanduser("~/.cache/k60_tts"); os.makedirs(CACHE, exist_ok=True)
IMGS = os.environ.get("HANGUL_IMG", "/mnt/project-files/plans/toptechs/longform/07-hangul/img")  # third-party photos stay out of the repo (CREDITS.md there)
STK = os.path.join(HERE, "..", "..", "assets", "baepsae")

def tts(text):
    h = hashlib.sha1(f"{VOICE}|{MODEL}|lf|{text}".encode()).hexdigest()[:16]; js = f"{CACHE}/{h}.json"
    if not os.path.exists(js):
        body = {"text": text, "model_id": MODEL, "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.3, "use_speaker_boost": True}}
        out = subprocess.run(["curl", "-s", "-X", "POST", f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_192",
            "-H", "xi-api-key: " + KEY, "-H", "Content-Type: application/json", "-d", json.dumps(body)], capture_output=True, text=True).stdout
        r = json.loads(out)
        if "audio_base64" not in r: raise SystemExit(f"ElevenLabs TTS failed: {out[:300]}")
        json.dump(r, open(js, "w"))
    r = json.load(open(js)); mp3 = f"{CACHE}/{h}.mp3"
    if not os.path.exists(mp3): open(mp3, "wb").write(base64.b64decode(r["audio_base64"]))
    x = np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-i", mp3, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"]), np.float32).astype(np.float64)
    a = r["alignment"]; assert "".join(a["characters"]) == text
    return x, a["character_start_times_seconds"]

def squeeze(x, keep=0.5):
    """Shorten silent gaps to `keep` s and trim the head to 0.05 s / tail to 0.15 s. Returns (y, f) with f mapping old -> new times."""
    w = int(0.01 * SR); n = len(x) // w; rms = np.sqrt((x[:n * w].reshape(n, w) ** 2).mean(1)); thr = 10 ** (-32 / 20) * np.abs(x).max()
    quiet = rms < thr; cuts, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]: j += 1
            if i == 0: cuts.append((0, max(0, j * w - int(0.05 * SR))))
            elif j >= n: cuts.append((i * w + int(0.15 * SR), len(x)))
            elif (j - i) * 0.01 > keep: cuts.append((i * w + int(keep / 2 * SR), j * w - int(keep / 2 * SR)))
            i = j
        else: i += 1
    cuts = [(a, b) for a, b in cuts if b > a]
    y = np.concatenate([x[a:b] for a, b in zip([0] + [c[1] for c in cuts], [c[0] for c in cuts] + [len(x)])])
    def f(t):
        s = t * SR - sum(min(b, max(a, t * SR)) - a for a, b in cuts); return max(0, s / SR)
    return y, f

def fade(x, d=0.2):
    n = min(len(x), int(d * SR)); y = x.copy(); y[len(y) - n:] *= np.linspace(1, 0, n) ** 2; return y

def build(out, sample=False):
    os.makedirs(f"{out}/img", exist_ok=True)
    clips, ev, cues = [], [], []; t = 0.2

    def beat(segs, ch, pose):
        nonlocal t
        text = " ".join(s for s, _ in segs); x, st = tts(text); y, f = squeeze(x); st = [f(v) for v in st]; t0 = t; cur = 0
        clips.append((t0, fade(y)))
        for k, (s, v) in enumerate(segs):
            i = text.index(s, cur); cur = i + len(s); a = st[i]; e = st[cur] if cur < len(st) else len(y) / SR
            cues.append((t0 + a, t0 + e, s)); ev.append(dict(v, t=t0 + a - (0.15 if k else 0.25), ch=ch, pose=pose))
        t = t0 + len(y) / SR + 0.45

    chapters = CHAPTERS[:2] if sample else CHAPTERS
    for ci, c in enumerate(chapters, 1):
        n0 = len(ev)
        for b in c["beats"]: beat(b, ci, c["pose"])
        ev[n0]["q"] = c["q"]  # YouTube chapter marker
    for b in OUTRO: beat(b, 99, "love_heart")
    ev[0]["t"] = 0.0
    t += 1.2; END = round(t, 2)
    for a, b in zip(ev, ev[1:]): a["t1"] = b["t"]
    ev[-1]["t1"] = END
    N = int((END + 0.5) * SR); vo = np.zeros(N); sfx = np.zeros(N)
    for t_, x in clips: i = int(t_ * SR); vo[i:i + len(x)] += x[:N - i]
    for e in ev:  # soft pop when a block snaps together / a letter lands
        if e["k"] in ("B", "L") and e["t"] > 0.5:
            p = load("pop", .5) * .12; i = int((e["t"] + (0.75 if e["k"] == "B" else 0.2)) * SR); sfx[i:i + len(p)] += p[:N - i]
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", os.path.join(HERE, "..", "..", "assets", "sfx", "kpdh_bgm_user.mp3"), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"])
    m2 = np.frombuffer(raw, np.float32).astype(np.float64).reshape(-1, 2); mus = np.tile(m2, (N // len(m2) + 1, 1))[:N]
    k = int(1.0 * SR); mus[:k] *= np.linspace(0, 1, k)[:, None]; k = int(3.0 * SR); mus[-k:] *= np.linspace(1, 0, k)[:, None]
    def w(name, x):
        x = np.clip(x, -1, 1); s = ((x if x.ndim == 2 else np.stack([x, x], 1)) * 32767).astype(np.int16)
        with wave.open(f"{out}/{name}", "wb") as f: f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(s.tobytes())
    w("vo.wav", vo * .9); w("music.wav", mus); w("sfx.wav", sfx)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{out}/vo.wav", "-i", f"{out}/music.wav", "-i", f"{out}/sfx.wav", "-filter_complex",
        "[0]asplit[vo][sc];[1]volume=0.13[m];[m][sc]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=400[md];[vo][md][2]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[out]",
        "-map", "[out]", "-ar", str(SR), "-ac", "2", f"{out}/mix.wav"], check=True)
    for e in ev:
        if e.get("img"): Image.open(f"{IMGS}/{e['img']}.jpg").save(f"{out}/img/{e['img']}.jpg", quality=92)
    for p in sorted({e["pose"] for e in ev}): Image.open(f"{STK}/{p}.png").save(f"{out}/img/st_{p}.png")
    html = open(os.path.join(HERE, "template.html")).read().replace("/*DATA*/", "const D=" + json.dumps({"ev": ev, "END": END}, ensure_ascii=False) + ";")
    open(f"{out}/short.html", "w").write(html); json.dump({"END": END, "ev": ev, "cues": cues}, open(f"{out}/timeline.json", "w"), ensure_ascii=False)
    print("END", END, "events", len(ev))

if __name__ == "__main__":
    build(sys.argv[1], len(sys.argv) > 2 and sys.argv[2] == "sample")
