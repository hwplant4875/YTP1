"""Long-form: K-drama phrases (16:9). Voice: Jennie on ElevenLabs v3, one request per phrase ("English. ... 한국어. ... 한국어, 천천히."),
a guessing pause is inserted in the silent gap between the English and the Korean (never inside speech); every clip fades out.
Usage: python3 build.py <outdir> [sample]  -> short.html (template), timeline.json, mix.wav; render with engine/prender.js (VW=1920 VH=1080)."""
import base64, hashlib, json, os, re, subprocess, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from phrases import CHAPTERS, NUM, HOOK, OUTRO
from sound import load, music
SR = 48000; VOICE = "z6Kj0hecH20CdetSElRT"; MODEL = "eleven_v3"
KEY = os.environ.get("ELEVENLABS_JC_API_KEY") or os.environ["ELEVENLABS_API_KEY"]
CACHE = os.path.expanduser("~/.cache/k60_tts"); os.makedirs(CACHE, exist_ok=True)
STK = os.path.join(HERE, "..", "..", "assets", "baepsae")
GUESS = 1.4  # extra silence so viewers can guess before the Korean

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
    return x, a["character_start_times_seconds"], a["character_end_times_seconds"]

def fade(x, d=0.15):
    n = min(len(x), int(d * SR)); y = x.copy(); y[len(y) - n:] *= np.linspace(1, 0, n); return y

def span(text, part, st, en, cur=0):
    i = text.index(part, cur); j = i + len(part) - 1; return st[i], en[j], j + 1

def slow(ko):  # read again a little slower: a comma between words
    w = ko.rstrip(".!?"); end = ko[len(w):] or "."
    return (", ".join(w.split()) if " " in w else w) + end

def build(out, sample=False):
    os.makedirs(out, exist_ok=True)
    clips, ev = [], []  # clips: (t, samples); ev: timeline events for the page
    t = 0.6
    def say(text, gap_after=0.5):
        nonlocal t
        x, st, en = tts(text); clips.append((t, fade(x))); t0 = t; t += len(x) / SR + gap_after; return t0, len(x) / SR
    t0, d = say(HOOK, 0.8); ev.append({"k": "hook", "t": 0, "t1": t - 0.3})
    n = 0
    chapters = CHAPTERS[:1] if sample else CHAPTERS
    for ci, (title, emo, col, items) in enumerate(chapters):
        c0 = t; say(f"Chapter {NUM[ci]}. {title}.", 0.9); ev.append({"k": "chapter", "t": c0 - 0.2, "t1": t - 0.25, "i": ci + 1, "title": title, "emo": emo, "c": col})
        for en_, ko, rom, pose in (items[:5] if sample else items):
            n += 1; text = f"{en_} ... {ko} ... {slow(ko)}"
            x, st, en = tts(text)
            e0, e1, cur = span(text, en_, st, en); k0, k1, cur = span(text, ko, st, en, cur); s0, s1, _ = span(text, slow(ko), st, en, cur)
            cut = int((e1 + k0) / 2 * SR); p0 = t
            clips.append((t, fade(x[:cut], 0.05))); t2 = t + cut / SR + GUESS; clips.append((t2, fade(x[cut:])))
            sh = lambda v: (p0 + v) if v * SR < cut else (t2 + v - cut / SR)
            ev.append({"k": "phrase", "n": n, "t": p0 - 0.35, "en": en_, "ko": ko.rstrip("."), "rom": rom, "pose": pose, "c": col, "ch": title, "emo": emo,
                       "reveal": sh(k0) - 0.12, "slow": sh(s0), "t1": t2 + len(x) / SR - cut / SR + 0.55})
            t = ev[-1]["t1"] + 0.25
    o0 = t; say(OUTRO, 1.2); ev.append({"k": "outro", "t": o0 - 0.2, "t1": t + 1})
    END = round(t + 1.2, 2)
    # audio: voice + music bed (ducked) + soft pop on each reveal
    N = int((END + 0.5) * SR); vo = np.zeros(N); sfx = np.zeros(N)
    for t_, x in clips: i = int(t_ * SR); vo[i:i + len(x)] += x[:N - i]
    for e in ev:
        if e["k"] == "phrase":
            p = load("pop", .5) * .25; i = int(e["reveal"] * SR); sfx[i:i + len(p)] += p[:N - i]
    mus = music(N, "lf_music")
    def w(name, x):
        x = np.clip(x, -1, 1); s = (np.stack([x, x], 1) * 32767).astype(np.int16)
        with wave.open(f"{out}/{name}", "wb") as f: f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(s.tobytes())
    w("vo.wav", vo * .9); w("music.wav", mus); w("sfx.wav", sfx)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{out}/vo.wav", "-i", f"{out}/music.wav", "-i", f"{out}/sfx.wav", "-filter_complex",
        "[0]asplit[vo][sc];[1]volume=0.28[m];[m][sc]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=400[md];[vo][md][2]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[out]",
        "-map", "[out]", "-ar", str(SR), "-ac", "2", f"{out}/mix.wav"], check=True)
    poses = sorted({e["pose"] for e in ev if e["k"] == "phrase"} | {"popcorn_tv", "excited", "hi_wave", "love_heart"})
    imgs = {p: "data:image/png;base64," + base64.b64encode(open(f"{STK}/{p}.png", "rb").read()).decode() for p in poses}
    html = open(os.path.join(HERE, "template.html")).read().replace("/*DATA*/", "const D=" + json.dumps({"ev": ev, "END": END, "TOTAL": 50}, ensure_ascii=False) + ";const IMG=" + json.dumps(imgs) + ";")
    open(f"{out}/short.html", "w").write(html); json.dump({"END": END, "ev": ev}, open(f"{out}/timeline.json", "w"), ensure_ascii=False)
    print("END", END, "phrases", n)

if __name__ == "__main__":
    build(sys.argv[1], len(sys.argv) > 2 and sys.argv[2] == "sample")
