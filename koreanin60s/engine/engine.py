#!/usr/bin/env python3
"""Korean in 60s short engine: spec.json -> voice (ElevenLabs Jennie) -> timeline -> audio mix -> short.html.
Render with: NODE_PATH=/opt/node22/lib/node_modules node render.js <outdir>"""
import json, os, sys, hashlib, subprocess, urllib.request, base64, re
import numpy as np, wave
HERE = os.path.dirname(os.path.abspath(__file__))
STK = os.path.join(HERE, "..", "assets", "baepsae")
VOICE = "z6Kj0hecH20CdetSElRT"  # Jennie
CACHE = os.path.expanduser("~/.cache/k60_tts"); os.makedirs(CACHE, exist_ok=True)
SR = 48000

MODEL = "eleven_v3"  # v3 reads Hangul inside English lines as real Korean; v2 said "il ai saem" (user chose v3, 2026-10-11)

def tts(text):
    """One request per utterance: English with the Korean words in Hangul inline, one speaker (Jennie).
    Returns (wav, duration, alignment) where alignment gives per-character start/end seconds."""
    h = hashlib.sha1(f"{VOICE}|{MODEL}|speed1|{text}".encode()).hexdigest()[:16]
    js = f"{CACHE}/{h}.json"; wav = f"{CACHE}/{h}.wav"
    if not os.path.exists(js):
        body = {"text": text, "model_id": MODEL, "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.4, "use_speaker_boost": True}}
        out = subprocess.run(["curl", "-s", "-X", "POST", f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_192",
            "-H", "xi-api-key: " + os.environ["ELEVENLABS_API_KEY"], "-H", "Content-Type: application/json", "-d", json.dumps(body)],
            capture_output=True, text=True).stdout
        r = json.loads(out)
        if "audio_base64" not in r: raise SystemExit(f"ElevenLabs TTS failed: {out[:300]}")
        json.dump(r, open(js, "w"))
    r = json.load(open(js))
    if not os.path.exists(wav):
        open(f"{CACHE}/{h}.mp3", "wb").write(base64.b64decode(r["audio_base64"]))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{CACHE}/{h}.mp3", "-ar", str(SR), "-ac", "2", wav], check=True)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav]))
    return wav, d, r["alignment"]

def utterances(lines):
    # a Korean line is always read together with the line before it (and the English that follows it, until a "gap"),
    # so the language switch sounds natural
    U = []
    for ln in lines:
        if not U or (ln.get("lang") != "ko" and ("gap" in ln or len(U[-1]) >= 3)): U.append([ln])
        else: U[-1].append(ln)
    return U

def resolve(at, T):
    # "key", "key@end", "key+0.3", "key@end-0.2", or number
    if isinstance(at, (int, float)): return float(at)
    m = re.match(r"^([\w]+)(@end)?([+-][\d.]+)?$", at)
    k, end, off = m.group(1), m.group(2), m.group(3)
    t = T[k][1] if end else T[k][0]
    return t + (float(off) if off else 0.0)

def build(spec_path, out):
    spec = json.load(open(spec_path)); os.makedirs(out, exist_ok=True)
    # 1. voice + timeline
    T = {}; t = 0.0; wavs = []
    for u in utterances(spec["lines"]):
        text = " ".join(ln["say"] for ln in u)
        wav, d, al = tts(text)
        t += u[0].get("gap", 0.25 if t > 0 else 0.3)
        chars = "".join(al["characters"]); st, en = al["character_start_times_seconds"], al["character_end_times_seconds"]
        assert chars == text, (chars, text)
        cur = 0
        for ln in u:
            i = text.index(ln["say"], cur); j = i + len(ln["say"]) - 1; cur = j + 1
            T[ln["k"]] = [round(t + st[i], 3), round(t + en[j], 3)]
        wavs.append((wav, t)); t += d
    END = round(t + spec.get("tail", 1.8), 3); T["END"] = [END, END]
    # 2. scenes + elements absolute times
    scenes = []
    for i, sc in enumerate(spec["scenes"]):
        s0 = 0.0 if i == 0 else resolve(sc["from"], T) - 0.22
        scenes.append({"id": f"sc{i}", "t0": s0, "els": sc["els"], "bg": sc.get("bg")})
    for i, sc in enumerate(scenes):
        sc["t1"] = scenes[i + 1]["t0"] if i + 1 < len(scenes) else END + 1
        for j, e in enumerate(sc["els"]):
            e["id"] = f"{sc['id']}e{j}"
            e["t"] = max(sc["t0"] + 0.12, resolve(e.get("at", sc["els"][0].get("at", 0)), T) + e.get("lead", -0.04)) if "at" in e else sc["t0"] + 0.15 + 0.08 * j
            for key in ("out", "hl", "dim"):
                if key in e: e[key + "T"] = resolve(e[key], T)
    # 3. captions + poses
    caps, poses = [], []
    for ln in spec["lines"]:
        a, b = T[ln["k"]]
        if ln.get("lang") == "ko":
            html = f'<span class="kor {ln.get("c","k")}">{ln.get("show", ln["say"])}</span>' + (f'<span class="rom">{ln["rom"]}</span>' if ln.get("rom") else "")
        else:
            html = ln.get("cap", ln["say"])
        caps.append({"t0": a - 0.05, "t1": b + 0.15, "html": html})
        if "pose" in ln: poses.append([a - 0.05, ln["pose"]])
    if not poses or poses[0][0] > 0.01: poses.insert(0, [0, spec.get("pose0", "hi_wave")])
    stickers = sorted({p for _, p in poses} | {e["name"] for sc in scenes for e in sc["els"] if e["type"] == "sticker"})
    imgs = {n: "data:image/png;base64," + base64.b64encode(open(f"{STK}/{n}.png", "rb").read()).decode() for n in stickers}
    data = {"T": T, "END": END, "scenes": scenes, "caps": caps, "poses": poses, "label": spec.get("label", ""), "pillOut": min(3.0, scenes[1]["t0"] - .3) if len(scenes) > 1 else 3.0, "labelColor": spec.get("labelColor", "#1C1718")}
    html = open(os.path.join(HERE, "template.html")).read().replace("/*DATA*/", "const D=" + json.dumps(data, ensure_ascii=False).replace("YouTube Sans,Pretendard", "GmarketSans,Pretendard") + ";const IMG=" + json.dumps(imgs) + ";")
    open(f"{out}/short.html", "w").write(html)
    json.dump({"T": T, "END": END}, open(f"{out}/timeline.json", "w"))
    # 4. audio
    mix_audio(out, wavs, scenes, END)
    print(out, "END", END)

def mix_audio(out, wavs, scenes, END):
    from sound import load, music
    N = int((END + 0.4) * SR); sfx = np.zeros(N)
    def put(name, t, g=1.0):
        x = load(name); i = int(max(0, t) * SR); j = min(N, i + len(x))
        if i < N: sfx[i:j] += x[:j - i] * g
    for i, sc in enumerate(scenes):
        if i: put("whoosh", sc["t0"] - .05, .7)
        for e in sc["els"]:
            if e["type"] == "stamp" and e.get("sfx") != "none": put("stamp", e["t"])
            elif e.get("sfx") in ("ding", "buzz"): put(e["sfx"], e["t"])
            elif e.get("sfx") != "none": put("pop", e["t"], .7)
            if "hlT" in e: put("ding", e["hlT"])
            if "dimT" in e: put("buzz", e["dimT"])
    mus = music(N)
    def w(name, x):
        x = np.clip(x, -1, 1); s = (np.stack([x, x], 1) * 32767).astype(np.int16)
        with wave.open(name, "wb") as f: f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(s.tobytes())
    w(f"{out}/sfx.wav", sfx * .55); w(f"{out}/music.wav", mus)
    wavs = [w for w in wavs if w[0]]
    if not wavs: wavs = [(f"{out}/sfx.wav", 0.0)]  # dry preview: no voice yet
    inp = []; flt = []
    for i, (wav, t) in enumerate(wavs):
        inp += ["-i", wav]; d = int(t * 1000); flt.append(f"[{i}]adelay={d}|{d}[v{i}]")
    flt.append("".join(f"[v{i}]" for i in range(len(wavs))) + f"amix=inputs={len(wavs)}:normalize=0,apad=whole_dur={END + .4}[vo]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(flt), "-map", "[vo]", "-ar", str(SR), "-ac", "2", f"{out}/vo.wav"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{out}/vo.wav", "-i", f"{out}/music.wav", "-i", f"{out}/sfx.wav", "-filter_complex",
        "[0]asplit[vo][sc];[1]volume=0.3[m];[m][sc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=300[md];[vo][md][2]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[out]",
        "-map", "[out]", "-ar", str(SR), "-ac", "2", f"{out}/mix.wav"], check=True)

if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
    if len(sys.argv) > 3 and sys.argv[3] == "--remux":  # audio-only change: swap the new mix into the existing render
        o = sys.argv[2]; subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{o}/out.mp4", "-i", f"{o}/mix.wav", "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", f"{o}/final.mp4"], check=True)
