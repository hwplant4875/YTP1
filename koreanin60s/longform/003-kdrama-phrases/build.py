"""Long-form: K-drama phrases (16:9). Voice: Jennie on ElevenLabs v3, one request per phrase ("English. ... 한국어. ... 한국어, 천천히."),
a guessing pause is inserted in the silent gap between the English and the Korean (never inside speech); every clip fades out.
Other sets reuse this engine: SET=<dir with phrases.py> python3 build.py <outdir>. An item with a 5th field (parts) is a
compound-word puzzle: "Eye, 눈. Water, 물. Together? 눈물! Tears." (the guessing pause goes before the answer).
Usage: python3 build.py <outdir> [sample]  -> short.html (template), timeline.json, mix.wav; render with engine/prender.js (VW=1920 VH=1080)."""
import base64, hashlib, json, os, re, subprocess, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); SET = os.path.abspath(os.environ.get("SET", HERE)); sys.path.insert(0, HERE); sys.path.insert(0, SET); sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
import phrases as P
from phrases import CHAPTERS, NUM, HOOK, OUTRO
from sound import load, music, music2
SR = 48000; VOICE = "z6Kj0hecH20CdetSElRT"; MODEL = "eleven_v3"
KEY = os.environ.get("ELEVENLABS_JC_API_KEY") or os.environ["ELEVENLABS_API_KEY"]
CACHE = os.path.expanduser("~/.cache/k60_tts"); os.makedirs(CACHE, exist_ok=True)
STK = os.path.join(HERE, "..", "..", "assets", "baepsae")
GUESS = 1.4  # extra silence so viewers can guess before the Korean (a set can override with GUESS in phrases.py)
GUESS = getattr(P, "GUESS", GUESS)

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

def squeeze(x, keep=0.3):
    """Shorten silent gaps inside a clip to `keep` s (speech itself is untouched). Returns (y, f) where f maps old times to new."""
    w = int(0.01 * SR); n = len(x) // w; rms = np.sqrt((x[:n * w].reshape(n, w) ** 2).mean(1)); thr = 10 ** (-30 / 20) * np.abs(x).max()
    quiet = rms < thr; cuts, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]: j += 1
            if (j - i) * 0.01 > keep and i > 0 and j < n: cuts.append((i * w + int(keep / 2 * SR), j * w - int(keep / 2 * SR)))
            i = j
        else: i += 1
    y = np.concatenate([x[a:b] for a, b in zip([0] + [c[1] for c in cuts], [c[0] for c in cuts] + [len(x)])])
    def f(t):
        s = t * SR - sum(min(b, max(a, t * SR)) - a for a, b in cuts); return s / SR
    return y, f

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
        for it in (items[:5] if sample else items):
            en_, ko, rom, pose = it[:4]; parts = it[4] if len(it) > 4 else None; n += 1
            if parts:  # compound puzzle
                (ea, pe, ka), (eb, pe2, kb) = parts; ans = ko + "!"
                text = f"{pe}, {ka}. {pe2}, {kb}. Together? {ans} {en_}"
                x, st, en = tts(text); x, f = squeeze(x, 0.24); st = [f(v) for v in st]; en = [f(v) for v in en]
                _, e1, cur = span(text, "Together?", st, en); k0, k1, cur = span(text, ans, st, en, cur); s0, s1, _ = span(text, en_, st, en, cur)
            else:
                text = f"{en_} ... {ko} ... {slow(ko)}"
                x, st, en = tts(text)
                e0, e1, cur = span(text, en_, st, en); k0, k1, cur = span(text, ko, st, en, cur); s0, s1, _ = span(text, slow(ko), st, en, cur)
            cut = int((e1 + k0) / 2 * SR); p0 = t
            clips.append((t, fade(x[:cut], 0.05))); t2 = t + cut / SR + GUESS; clips.append((t2, fade(x[cut:])))
            sh = lambda v: (p0 + v) if v * SR < cut else (t2 + v - cut / SR)
            e = {"k": "phrase", "n": n, "t": p0 - 0.35, "en": en_, "ko": ko.rstrip("."), "rom": rom, "pose": pose, "c": col, "ch": title, "emo": emo,
                 "reveal": sh(k0) - 0.12, "slow": sh(s0), "t1": t2 + len(x) / SR - cut / SR + 0.55}
            if parts:
                e["parts"] = [list(q) for q in parts]; e["t1"] -= 0.25
            ev.append(e)
            t = ev[-1]["t1"] + 0.25
    o0 = t; say(OUTRO, 1.2); ev.append({"k": "outro", "t": o0 - 0.2, "t1": t + 1})
    END = round(t + 1.2, 2)
    # audio: voice + music bed (ducked) + soft pop on each reveal
    N = int((END + 0.5) * SR); vo = np.zeros(N); sfx = np.zeros(N)
    for t_, x in clips: i = int(t_ * SR); vo[i:i + len(x)] += x[:N - i]
    for e in ev:
        if e["k"] == "phrase":
            p = load("pop", .5) * .25; i = int(e["reveal"] * SR); sfx[i:i + len(p)] += p[:N - i]
    M = getattr(P, "MUSIC", ["lf_music"])
    if len(M) > 1:  # switch beds at the chapter start nearest the middle of the video
        sw = min((e["t"] for e in ev if e["k"] == "chapter"), key=lambda x: abs(x - END / 2)); mus = music2(N, M, int(sw * SR))
    else:
        mus = music(N, M[0])
    def w(name, x):
        x = np.clip(x, -1, 1); s = (np.stack([x, x], 1) * 32767).astype(np.int16)
        with wave.open(f"{out}/{name}", "wb") as f: f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(s.tobytes())
    w("vo.wav", vo * .9); w("music.wav", mus); w("sfx.wav", sfx)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{out}/vo.wav", "-i", f"{out}/music.wav", "-i", f"{out}/sfx.wav", "-filter_complex",
        "[0]asplit[vo][sc];[1]volume=0.28[m];[m][sc]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=400[md];[vo][md][2]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[out]",
        "-map", "[out]", "-ar", str(SR), "-ac", "2", f"{out}/mix.wav"], check=True)
    poses = sorted({e["pose"] for e in ev if e["k"] == "phrase"} | {getattr(P, "HOOK_POSE", "popcorn_tv"), "excited", "hi_wave", getattr(P, "OUTRO_POSE", "love_heart")})
    imgs = {p: "data:image/png;base64," + base64.b64encode(open(f"{STK}/{p}.png", "rb").read()).decode() for p in poses}
    html = open(os.path.join(HERE, "template.html")).read().replace("/*DATA*/", "const D=" + json.dumps({"ev": ev, "END": END, "TOTAL": n, "HOOK_HTML": getattr(P, "HOOK_HTML", None), "OUTRO_HTML": getattr(P, "OUTRO_HTML", None), "HOOK_POSE": getattr(P, "HOOK_POSE", "popcorn_tv"), "OUTRO_POSE": getattr(P, "OUTRO_POSE", "love_heart")}, ensure_ascii=False) + ";const IMG=" + json.dumps(imgs) + ";")
    open(f"{out}/short.html", "w").write(html); json.dump({"END": END, "ev": ev}, open(f"{out}/timeline.json", "w"), ensure_ascii=False)
    print("END", END, "phrases", n)

if __name__ == "__main__":
    build(sys.argv[1], len(sys.argv) > 2 and sys.argv[2] == "sample")
