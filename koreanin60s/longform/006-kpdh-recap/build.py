"""Long-form #4 builder: KPop Demon Hunters one-year recap (16:9). Voice: Jennie on ElevenLabs v3 (JC key), one request per beat;
each visual switches when its sentence starts (alignment), pauses inside a beat are squeezed to 0.5 s, 0.45 s between beats.
Usage: python3 build.py <img dir> <outdir> [sample]  -> short.html, img/, timeline.json, mix.wav; render with engine/prender.js (VW=1920 VH=1080)."""
import base64, hashlib, json, os, re, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from script import HOOK, CHAPTERS, OUTRO
from sound import load, music2
Image.MAX_IMAGE_PIXELS = None
SR = 48000; VOICE = "z6Kj0hecH20CdetSElRT"; MODEL = "eleven_v3"
KEY = os.environ.get("ELEVENLABS_JC_API_KEY") or os.environ["ELEVENLABS_API_KEY"]
CACHE = os.path.expanduser("~/.cache/k60_tts"); os.makedirs(CACHE, exist_ok=True)
STK = os.path.join(HERE, "..", "..", "assets", "baepsae")
SAY = {"HUNTR/X": "Huntrix", "1위": "일위", "Ji-young Yoo": "Jiyoung Yoo"}  # spoken spelling; the captions keep the display spelling
def say(s):
    for a, b in SAY.items(): s = s.replace(a, b)
    return s
SUBS = ["2FS3JAPTKXs", "HT46zbEQdiw", "LyM5k1d65TY"]
NUM = ["one", "two", "three", "four", "five", "six", "seven", "eight"]

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

def prep_img(src_dir, name, out):
    """Crop black bars, save a 1600px card image + a small dark blurred backdrop. Returns aspect ratio."""
    f = next(p for p in os.listdir(src_dir) if os.path.splitext(p)[0] == name)
    im = Image.open(os.path.join(src_dir, f)).convert("RGB")
    if max(im.size) > 4000: im.thumbnail((3200, 3200))
    g = np.asarray(im.convert("L"), np.float32); cols = np.flatnonzero(g.mean(0) > 14); rows = np.flatnonzero(g.mean(1) > 14)
    if len(cols) and len(rows) and not name.startswith("h1_"): im = im.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))
    if any(k in name for k in SUBS): im = im.crop((0, 0, im.size[0], int(im.size[1] * 0.8)))  # burned-in lyric subtitles at the bottom
    c = im.copy(); c.thumbnail((1600, 1600)); c.save(f"{out}/img/{name}.jpg", quality=90)
    b = im.copy(); b.thumbnail((480, 480)); b = b.filter(ImageFilter.GaussianBlur(14)); b = ImageEnhance.Brightness(b).enhance(0.45); b.save(f"{out}/img/{name}_bg.jpg", quality=85)
    return round(im.size[0] / im.size[1], 3)

def build(src_dir, out, sample=False):
    os.makedirs(f"{out}/img", exist_ok=True)
    clips, ev, cues = [], [], []  # clips: (t, samples); ev: visual events; cues: (t0, t1, text) for the .srt
    t = 0.5; cnt = {"views": None, "awards": None}; aspects = {}

    def speak(text):
        x, st = tts(say(text)); y, f = squeeze(x); return y, [f(v) for v in st]

    def beat(segs, ch, m):
        nonlocal t
        text = say(" ".join(s for s, _ in segs if s)); y, st = speak(text); t0 = t; cur = 0; starts = []
        for s, v in segs:
            if s:
                i = text.index(say(s), cur); cur = i + len(say(s)); a = st[i]; e = st[cur] if cur < len(st) else len(y) / SR; starts.append([a, e, s])
            else:  # no words of its own: take over the second half of the previous sentence
                p = starts[-1]; mid = (p[0] + p[1]) / 2; starts.append([mid, p[1], ""]); p[1] = mid
        clips.append((t0, fade(y)))
        for k, ((a, e, s), (_, v)) in enumerate(zip(starts, segs)):
            if s: cues.append((t0 + a, t0 + e, s))
            vis = dict(v); vis["cap"] = vis.pop("t", None); vis["t"] = t0 + a - (0.15 if k else 0.3); vis["ch"] = ch
            if vis.get("cnt"): cnt.update(vis["cnt"])
            vis["cnt"] = dict(cnt); vis["m"] = m(len(ev)) if m else None
            if vis.get("img") and vis["img"] not in aspects: aspects[vis["img"]] = prep_img(src_dir, vis["img"], out)
            if vis.get("head") and vis["head"] not in aspects: aspects[vis["head"]] = prep_img(src_dir, vis["head"], out)
            ev.append(vis)
        t = t0 + len(y) / SR + 0.45

    def card(kind, text, extra, hold=0.6):
        nonlocal t
        y, _ = speak(text); t0 = t; clips.append((t0 + 0.3, fade(y))); cues.append((t0 + 0.3, t0 + 0.3 + len(y) / SR, text))
        ev.append({"k": kind, "t": t0 - 0.1, **extra}); t = t0 + 0.3 + len(y) / SR + hold

    for b in HOOK: beat(b, 0, None)
    ev.append({"k": "T", "t": t - 0.1, "img": ev[-1]["img"], "ch": 0, "cnt": dict(cnt), "m": None}); t += 2.6
    chapters = CHAPTERS[:1] if sample else CHAPTERS
    for ci, c in enumerate(chapters, 1):
        first = next(v["img"] for s, v in c["beats"][0])
        card("C", f"Chapter {NUM[ci - 1]}. {c['q']}", {"i": ci, "q": c["q"], "date": c["date"], "img": first, "ch": ci, "cnt": dict(cnt), "m": c["m"][0]}, 0.7)
        n0 = len(ev); nseg = sum(len(b) for b in c["beats"]); a_, b_ = c["m"]
        m = lambda k, n0=n0, nseg=nseg, a_=a_, b_=b_: round(a_ + (b_ - a_) * (k - n0) / max(1, nseg - 1), 3)
        for b in (c["beats"][:3] if sample else c["beats"]): beat(b, ci, m)
        for e in ev[n0:]: e["date"], e["pose"] = c["date"], c["pose"]
        if c.get("ko"):
            w, rom, mean, line = c["ko"]; card("K", line, {"w": w, "rom": rom, "mean": mean, "pose": c["pose"], "ch": ci, "cnt": dict(cnt), "m": b_}, 0.8)
    if not sample:
        for b in OUTRO: beat(b, 9, None)
    t += 1.5; END = round(t, 2)
    for v in ev:
        if v.get("img"): v["ar"] = aspects.get(v["img"])
    for a, b in zip(ev, ev[1:]): a["t1"] = b["t"]
    ev[-1]["t1"] = END
    # audio: voice + music (Easy Lemon, then Airport Lounge from the chapter nearest the middle) + a soft ding on each Korean moment
    N = int((END + 0.5) * SR); vo = np.zeros(N); sfx = np.zeros(N)
    for t_, x in clips: i = int(t_ * SR); vo[i:i + len(x)] += x[:N - i]
    for e in ev:
        if e["k"] == "K": p = load("ding", .5) * .18; i = int((e["t"] + 0.15) * SR); sfx[i:i + len(p)] += p[:N - i]
    sw = min((e["t"] for e in ev if e["k"] == "C"), key=lambda x: abs(x - END / 2)); mus = music2(N, ["easy_lemon", "airport_lounge"], int(sw * SR))
    k = int(2.0 * SR); mus[:k] *= np.linspace(0, 1, k)
    def w(name, x):
        x = np.clip(x, -1, 1); s = (np.stack([x, x], 1) * 32767).astype(np.int16)
        with wave.open(f"{out}/{name}", "wb") as f: f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(s.tobytes())
    w("vo.wav", vo * .9); w("music.wav", mus); w("sfx.wav", sfx)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{out}/vo.wav", "-i", f"{out}/music.wav", "-i", f"{out}/sfx.wav", "-filter_complex",
        "[0]asplit[vo][sc];[1]volume=0.26[m];[m][sc]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=400[md];[vo][md][2]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[out]",
        "-map", "[out]", "-ar", str(SR), "-ac", "2", f"{out}/mix.wav"], check=True)
    poses = sorted({c["pose"] for c in CHAPTERS} | {"love_heart"})
    for p in poses: Image.open(f"{STK}/{p}.png").save(f"{out}/img/st_{p}.png")
    html = open(os.path.join(HERE, "template.html")).read().replace("/*DATA*/", "const D=" + json.dumps({"ev": ev, "END": END}, ensure_ascii=False) + ";")
    open(f"{out}/short.html", "w").write(html); json.dump({"END": END, "ev": ev, "cues": cues}, open(f"{out}/timeline.json", "w"), ensure_ascii=False)
    print("END", END, "events", len(ev))

if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2], len(sys.argv) > 3 and sys.argv[3] == "sample")
