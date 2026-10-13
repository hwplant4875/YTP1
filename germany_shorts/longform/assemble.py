"""Assemble a narrated long-form documentary from a beat script.

  python3 assemble.py script.json out.mp4 [--only-audio] [--preview]

script.json
{
  "voice": {"voice_id": "...", "tempo": 1.3, "emotion": "normal"},
  "gap": 0.05,                       # silence between narration lines
  "music": [{"file": "m1.mp3", "from": "intro", "to": "act1", "vol": 0.16}],   # section ids
  "beats": [
    {"id": "intro",                    # optional anchor for music cues
     "say": "narration line",
     "visual": {"type": "3d", "scene": "ghost_station", "shot": "platform", "t0": 0}
             | {"type": "image", "file": "x.jpg", "from": [1.0, 0.5, 0.5], "to": [1.15, 0.45, 0.5], "credit": "..."}
             | {"type": "video", "file": "x.mp4", "start": 12.0, "speed": 1.0, "credit": "..."}
             | {"type": "black"}
             | "same",                  # keep the previous shot running
     "text": {"kind": "year" | "label" | "title" | "quote", "content": "1961", "pos": [0.5, 0.5]},
     "sfx": "subway train passing" | {"prompt": "...", "at": 0.3, "vol": 0.5, "len": 3},
     "hold": 0.4}                      # extra seconds of picture after the line
  ]
}
Images and videos get the house look: black and white, grain, vignette.
3D shots are rendered with render.mjs (cached by scene/shot/t0/duration).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts")
CACHE = os.environ.get("LONGFORM_CACHE", os.path.join(HERE, ".cache"))
W, H, FPS = int(os.environ.get("LONGFORM_W", 1920)), int(os.environ.get("LONGFORM_H", 1080)), 30
# non-default frame sizes (e.g. 1080x1920 shorts) go into every visual cache key; the landscape keys stay as they were
SIZE_KEY = [] if (W, H) == (1920, 1080) else [W, H]
UA = {"User-Agent": "Mozilla/5.0 (germany-longform)"}
PILJAE = "tc_68257f68bc6e3c161ab5078d"


def sh(*cmd, quiet=True):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode:
        sys.exit(" ".join(map(str, cmd))[:300] + "\n" + r.stderr[-3000:])
    return r.stdout


def dur(path):
    return float(sh("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path))


def key(*parts):
    return hashlib.sha1(json.dumps(parts, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]


def cached(name, make):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name)
    if not os.path.exists(path):
        tmp = path + ".part"
        if os.environ.get("ASSEMBLE_SHARD") and name.startswith(("3d_", "img_", "vid_")) and (os.path.exists(tmp) or os.path.exists(tmp + ".mp4")):
            print("  already being rendered by another process, skipping", name, flush=True)   # pre-render shards only
            return path
        make(tmp)
        os.replace(tmp, path)
    return path


def http(url, data=None, headers=None, timeout=300):
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    return urllib.request.urlopen(req, timeout=timeout).read()


# ---------------------------------------------------------------- audio

def tts_elevenlabs(text, voice, ctx=None):
    vid = voice["voice_id"]
    body = {"text": text, "model_id": voice.get("model", "eleven_v4"),
            "voice_settings": {"stability": voice.get("stability", 0.5), "similarity_boost": voice.get("similarity", 0.8),
                               "speed": voice.get("speed", 1.0)}}
    if ctx:   # neighbouring lines keep the prosody continuous across separately generated sentences
        body.update({k: v for k, v in ctx.items() if v})
    try:
        raw = cached(f"el_{key(vid, body)}.mp3", lambda p: open(p, "wb").write(http(
            f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_192", json.dumps(body).encode(),
            {"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})))
    except urllib.error.HTTPError as e:
        if not ctx:
            raise
        print("tts context rejected, retrying without it:", e.code, e.read()[:200])
        return tts_elevenlabs(text, voice)
    return raw


def tts(text, voice, ctx=None):
    if voice.get("engine") == "elevenlabs":
        raw = tts_elevenlabs(text, voice, ctx)
        sd, ss = voice.get("squeeze", [0.32, 0.22])
        keep = TAIL.get("keep", 0.05) if TAIL else 0.05
        af = ("silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02,"
              f"areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence={keep},areverse,"
              f"silenceremove=stop_periods=-1:stop_duration={sd}:stop_threshold=-50dB:stop_silence={ss},"
              "aresample=48000,aformat=channel_layouts=mono")
        tight = cached(f"tight_{key(raw, af)}.wav", lambda p: sh("ffmpeg", "-y", "-i", raw, "-af", af, "-f", "wav", p))
        if TAIL:
            return cached(f"dc_{key(tight, TAIL)}.wav", lambda p: declick_tail(tight, p, TAIL.get("fade", 0.012)))
        return cached(f"dc_{key(tight)}.wav", lambda p: declick_tail(tight, p)) if DECLICK else tight
    body = {"voice_id": voice.get("voice_id", PILJAE), "text": text, "model": voice.get("model", "ssfm-v21"),
            "language": "kor",
            "prompt": {"emotion_preset": voice.get("emotion", "normal"), "emotion_intensity": voice.get("intensity", 1.0)},
            "output": {"audio_format": "wav", "audio_tempo": voice.get("tempo", 1.3), "volume": 100}}
    raw = cached(f"tts_{key(body)}.wav", lambda p: open(p, "wb").write(http(
        "https://api.typecast.ai/v1/text-to-speech", json.dumps(body).encode(),
        {"X-API-KEY": os.environ["TYPECAST_API_KEY"], "Content-Type": "application/json"})))
    # trim the lead-in and tail, squeeze long inner pauses so lines run back to back
    af = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,"
          "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.04,areverse,"
          "silenceremove=stop_periods=-1:stop_duration=0.14:stop_threshold=-45dB:stop_silence=0.09,"
          "aresample=48000,aformat=channel_layouts=mono")
    return cached(f"tight_{key(body, af)}.wav", lambda p: sh("ffmpeg", "-y", "-i", raw, "-af", af, "-f", "wav", p))


def _wav_db(path):
    import wave
    import numpy as np
    with wave.open(path) as w:
        sr, raw = w.getframerate(), w.readframes(w.getnframes())
    x = np.frombuffer(raw, np.int16).astype(np.float32)
    fr = sr // 100
    n = len(x) // fr
    db = np.array([20 * np.log10(np.sqrt(np.mean((x[i * fr:(i + 1) * fr] / 32768) ** 2)) + 1e-9) for i in range(n)])
    return sr, x, fr, db


def cap_pauses(src, maxp, thr=-40.0):
    """Shorten silent stretches inside a line (below thr dB) to maxp seconds by cutting out their middle (no speed or
    pitch change): Shorts want ~0.5 s between sentences, never more than 0.6 s."""
    def make(dst):
        import wave
        import numpy as np
        sr, x, fr, db = _wav_db(src)
        q = db < thr
        keep = np.ones(len(x), bool)
        k, n = 0, len(q)
        while k < n:
            if q[k]:
                j = k
                while j < n and q[j]:
                    j += 1
                if k > 0 and j < n and (j - k) / 100 > maxp:   # inner pause only
                    cut = int(((j - k) / 100 - maxp) * sr)
                    a = k * fr + int(maxp * sr / 2)
                    keep[a:a + cut] = False
                k = j
            else:
                k += 1
        y = x[keep]
        with wave.open(dst, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
            w.writeframes(np.clip(y, -32768, 32767).astype(np.int16).tobytes())
    return cached(f"mp_{key(src, maxp, thr)}.wav", make)


def voice_edges(path, thr=-40.0):
    """(start, end) of audible speech in a take, seconds"""
    sr, x, fr, db = _wav_db(path)
    loud = [i for i, v in enumerate(db) if v >= thr]
    return (loud[0] / 100, (loud[-1] + 1) / 100) if loud else (0.0, len(x) / sr)


def declick_tail(src, dst, fade_out=None):
    """eleven_v4 sometimes ends a line with a 10-60 ms burst after half a second of silence; it is heard as a glitch.
    Mute it (same length, so the timeline does not move) and soften both ends of the line."""
    import wave
    import numpy as np
    with wave.open(src) as w:
        sr, ch, raw = w.getframerate(), w.getnchannels(), w.readframes(w.getnframes())
    x = np.frombuffer(raw, np.int16).astype(np.float32).copy()
    fr = sr // 100
    n = len(x) // fr
    db = np.array([20 * np.log10(np.sqrt(np.mean((x[i * fr:(i + 1) * fr] / 32768) ** 2)) + 1e-9) for i in range(n)])
    k = n - 1
    while k > 0 and db[k] > -45:
        k -= 1
    burst, m = n - 1 - k, k
    while m > 0 and db[m] < -45:
        m -= 1
    if 0 < burst <= 8 and k - m >= 25:
        x[(k + 1) * fr:] = 0
    f = min(len(x) // 4, sr * 12 // 1000)
    x[:f] *= np.linspace(0, 1, f)
    if fade_out:   # natural ending: a raised-cosine fade over the decay, never a hard stop
        # eleven_v4 often appends the onset of a breath or a click (up to ~0.16 s, sometimes loud) after the line has
        # already decayed into silence; cut it away, keeping the full decay plus a short stretch of the silence
        q = db < -55
        e = n
        while e > 0 and not q[e - 1]:
            e -= 1
        z = e
        while z > 0 and q[z - 1]:
            z -= 1
        if (0 < n - e <= 16 or (0 < n - e <= 35 and db[e:].max() < -40)) and e - z >= 15 and z > 0:   # a word is louder
            x = x[:min(len(x), (z + int(fade_out * 100) + 5) * fr)]
        fo = min(len(x) // 3, int(sr * fade_out))
        x[len(x) - fo:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fo))
    else:
        x[len(x) - f:] *= np.linspace(1, 0, f)
    with wave.open(dst, "wb") as w:
        w.setnchannels(ch); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(x.astype(np.int16).tobytes())


def sfx(prompt, seconds=None):
    body = {"text": prompt, "prompt_influence": 0.5}
    if seconds:
        body["duration_seconds"] = seconds
    return cached(f"sfx_{key(body)}.mp3", lambda p: open(p, "wb").write(http(
        "https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128", json.dumps(body).encode(),
        {"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})))


# ---------------------------------------------------------------- visuals

LOOK = "eq=saturation=0:contrast=1.08:brightness=-0.02"   # archive material goes black and white
# per-spec options (all off by default, so older specs render and cache exactly as before):
#   "look": ffmpeg grade for photos/footage, kept in colour (e.g. a light warm grade) instead of black and white
#   "tail": {"keep": s, "fade": s} keep more of each TTS line's natural decay and fade it out smoothly
#   "reuse_3d": s  reuse a cached 3D render whose duration differs by up to s seconds (trimmed, or last frame held)
COLOUR, TAIL, REUSE_3D = False, None, 0.0
LOOK_KEY = []


def scene_hash(scene):
    h = hashlib.sha1()
    for f in (f"scenes/{scene}.js", "scenes/lib.js", "scenes/look.js", "render.mjs"):
        p = os.path.join(HERE, f)
        if os.path.exists(p):
            h.update(open(p, "rb").read())
    return h.hexdigest()[:10]


def index_3d():
    p = os.path.join(CACHE, "3d_index.json")
    return p, (json.load(open(p)) if os.path.exists(p) else {})


def record_3d(name, v, d, h):
    p, idx = index_3d()
    idx[name] = {"v": v, "d": round(d, 3), "h": h, "size": SIZE_KEY}
    tmp = p + f".{os.getpid()}"
    json.dump(idx, open(tmp, "w"), ensure_ascii=False)
    os.replace(tmp, p)


def reuse_3d(v, d, h):
    """A cached render of the same shot with a slightly different length: the animation timing does not depend on the
    clip length (shots are stretched by "name:secs"), so a longer one is cut at d and a shorter one holds its last frame."""
    _, idx = index_3d()
    best = None
    for name, e in idx.items():
        if e["v"] == v and e["h"] == h and e["size"] == SIZE_KEY and abs(e["d"] - d) <= REUSE_3D \
                and os.path.exists(os.path.join(CACHE, name)):
            score = (e["d"] < d, abs(e["d"] - d))   # prefer a longer clip (plain cut)
            if best is None or score < best[0]:
                best = (score, name, e["d"])
    if not best:
        return None
    src = os.path.join(CACHE, best[1])
    if best[2] >= d:
        return (src, d)
    return (cached(f"3dpad_{key(best[1], round(d, 3))}.mp4", lambda p: sh(
        "ffmpeg", "-y", "-i", src, "-vf", f"tpad=stop_mode=clone:stop_duration={d - best[2] + 0.1:.3f}", "-t", f"{d:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-f", "mp4", p)), d)


def render_3d(v, d):
    h = scene_hash(v["scene"])
    k = key(v, round(d, 3), h, *SIZE_KEY)
    name = f"3d_{v['scene']}_{v.get('shot', '')}_{k}.mp4"
    if REUSE_3D and not os.path.exists(os.path.join(CACHE, name)):
        r = reuse_3d(v, d, h)
        if r:
            return r
    def make(p):
        for attempt in range(3):   # headless Chromium occasionally exits without writing under heavy load
            r = subprocess.run([str(c) for c in ("node", os.path.join(HERE, "render.mjs"), f"scenes/{v['scene']}.js", p + ".mp4",
                                "--dur", f"{d:.3f}", "--fps", FPS, "--shot", v.get("shot", ""), "--t0", v.get("t0", 0),
                                "--w", W, "--h", H)],
                               capture_output=True, text=True)
            if r.returncode == 0 and os.path.exists(p + ".mp4"):
                break
            print("3d render failed, retrying", v, r.stderr[-400:], flush=True)
        os.replace(p + ".mp4", p)
    out = cached(name, make)
    if REUSE_3D:
        record_3d(name, v, d, h)
    return out


def render_image(v, d, base):
    """Ken Burns on a still, done in float precision (no zoompan jitter)."""
    from PIL import Image
    k = key(v, round(d, 3), *SIZE_KEY, *LOOK_KEY)
    def make(p):
        src = Image.open(os.path.join(base, v["file"])).convert("RGB")
        if not COLOUR:
            src = src.convert("L").convert("RGB")
        # fit to cover 16:9 at 2x so the zoom stays sharp
        s = max(W * 2 / src.width, H * 2 / src.height)
        src = src.resize((int(src.width * s), int(src.height * s)), Image.LANCZOS)
        z0, x0, y0 = v.get("from", [1.0, 0.5, 0.5])
        z1, x1, y1 = v.get("to", [1.12, 0.5, 0.5])
        n = max(1, round(d * FPS))
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                               "-r", str(FPS), "-i", "-", "-vf", LOOK, "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                               "-pix_fmt", "yuv420p", "-f", "mp4", p], stdin=subprocess.PIPE)
        for i in range(n):
            t = i / max(n - 1, 1)
            t = t * t * (3 - 2 * t)
            z, cx, cy = z0 + (z1 - z0) * t, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            cw, ch = src.width / z, src.width / z * H / W
            if ch > src.height / z:
                ch = src.height / z
                cw = ch * W / H
            left = min(max(cx * src.width - cw / 2, 0), src.width - cw)
            top = min(max(cy * src.height - ch / 2, 0), src.height - ch)
            frame = src.transform((W, H), Image.EXTENT, (left, top, left + cw, top + ch), Image.BICUBIC)
            ff.stdin.write(frame.tobytes())
        ff.stdin.close()
        ff.wait()
    return cached(f"img_{k}.mp4", make)


def render_video(v, d, base):
    k = key(v, round(d, 3), *SIZE_KEY, *LOOK_KEY)
    speed = v.get("speed", 1.0)
    crop = v.get("crop")  # [x, y, w, h] in source pixels, to cut away old captions or logos
    vf = (f"crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]}," if crop else "") + \
        f"setpts=PTS/{speed},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1,{LOOK}"
    if v.get("zoom"):   # optional slow push-in [z0, z1], computed on a 2x frame so the motion stays smooth
        z0, z1 = v["zoom"]
        n = max(1, round(d * FPS))
        vf = vf.replace(f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
                        f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{H * 2},fps={FPS},"
                        f"zoompan=z='{z0}+({z1}-{z0})*(3*pow(on/{n},2)-2*pow(on/{n},3))':d=1:s={W}x{H}:fps={FPS}:"
                        f"x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2'")
    if v.get("frame"):   # optional: shown smaller (fraction of the frame) over a dark, blurred copy of itself, e.g. news footage
        f = v["frame"]
        fw, fh = int(W * f) // 2 * 2, int(H * f) // 2 * 2
        vf = (f"crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]}," if crop else "") + \
            f"setpts=PTS/{speed},fps={FPS},setsar=1,{LOOK},split[a][b];" \
            f"[a]scale={W // 4}:{H // 4}:force_original_aspect_ratio=increase,crop={W // 4}:{H // 4},gblur=sigma=12," \
            f"eq=brightness=-0.22:contrast=0.8,scale={W}:{H}[bg];" \
            f"[b]scale={fw}:{fh}:force_original_aspect_ratio=decrease,pad=iw+6:ih+6:3:3:color=0x3a3a3a[fg];" \
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2-{int(H * v.get('lift', 0.0))},setsar=1,tpad=stop_mode=clone:stop_duration={d:.3f}"
    return cached(f"vid_{k}.mp4", lambda p: sh(
        "ffmpeg", "-y", "-ss", v.get("start", 0), "-i", os.path.join(base, v["file"]), "-t", f"{d * speed:.3f}",
        "-an", "-vf", vf, "-t", f"{d:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-f", "mp4", p))


def render_g2d(v, d, start, beats, base):
    """2D motion graphics from graphics2d.py, timed to the narration of the beats they cover."""
    import graphics2d
    graphics2d.W, graphics2d.H = W, H   # graphics follow the frame size override (set here so graphics2d.py, part of the cache key, stays as is)
    extra = ""
    if v.get("module"):   # optional adapter module next to the spec that registers more graphics (e.g. for a short)
        import importlib.util
        mp = os.path.join(base, v["module"])
        m = importlib.util.spec_from_file_location(os.path.splitext(os.path.basename(mp))[0], mp)
        mod = importlib.util.module_from_spec(m)
        m.loader.exec_module(mod)
        graphics2d.GRAPHICS.update(mod.GRAPHICS)
        extra = hashlib.sha1(open(mp, "rb").read()).hexdigest()[:10]
    timing = [{"start": round(b["_start"] - start, 3), "say_at": round(b["_say_at"] - start, 3), "say_d": round(b["_say_d"], 3),
               "say": b.get("say", ""), "end": round(b["_end"] - start, 3)} for b in beats]
    src = open(os.path.join(HERE, "graphics2d.py"), "rb").read()
    k = key(v, round(d, 3), timing, hashlib.sha1(src).hexdigest()[:10], *SIZE_KEY, *([extra] if extra else []))
    ext = "mov" if v.get("alpha") else "mp4"
    return cached(f"g2d_{v['name']}_{k}.{ext}", lambda p: graphics2d.render(v, d, timing, base, p, ext))


def render_black(d):
    return cached(f"black_{round(d, 3)}{''.join(f'_{x}' for x in SIZE_KEY)}.mp4", lambda p: sh(
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}", "-t", f"{d:.3f}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-f", "mp4", p))


# ---------------------------------------------------------------- text overlays (ASS)

def ass_time(t):
    h, t = divmod(max(t, 0), 3600)
    m, s = divmod(t, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


ASS_HEAD = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: YEAR,Pretendard Black,250,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,6,0,1,0,8,5,0,0,0,1
Style: LABEL,Pretendard SemiBold,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,4,0,1,0,3,5,0,0,0,1
Style: TITLE,Noto Serif KR Black,168,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,2,0,1,0,6,5,0,0,0,1
Style: QUOTE,Noto Serif KR SemiBold,64,&H00F0F0F0,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,0,4,5,0,0,0,1
Style: CREDIT,Pretendard Medium,22,&H99FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,3,0,30,22,1
Style: SUB,Pretendard SemiBold,50,&H00F4F4F4,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0.5,0,1,0,2.5,2,120,120,62,1
Style: CHAPTER,YouTube Sans Dark,118,&H00F4F4F4,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,7,0,5,0,0,0,1
Style: FX,Pretendard Black,10,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


AMBER_ASS = "&H5CB2FF&"
SUB_LIMIT = None
DECLICK = False
SFX_GAIN = 1.0


def accent(text):
    return re.sub(r"\*(.+?)\*", lambda m: "{\\c" + AMBER_ASS + "}" + m.group(1) + "{\\c&HF4F4F4&}", text)


def sub_chunks(text, limit=19):
    limit = SUB_LIMIT or limit
    words = re.findall(r"\S+", text)
    out, cur = [], ""
    for w in words:
        plain = (cur + " " + w).replace("*", "").strip()
        if cur and len(plain) > limit:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
        if cur.endswith((",", "?", "!", ".")) and len(cur.replace("*", "")) >= limit * 0.55:
            out.append(cur); cur = ""
    if cur:
        out.append(cur)
    fixed, carry = [], False
    for c in out:
        if carry:
            c = "*" + c
        carry = c.count("*") % 2 == 1
        fixed.append((c + ("*" if carry else "")).rstrip(".,"))
    return fixed


def sub_events(text, start, end):
    parts = sub_chunks(text)
    w = [max(len(p.replace("*", "")), 4) for p in parts]
    ev, t = [], start
    for p, k in zip(parts, w):
        d = (end - start) * k / sum(w)
        ev.append(f"Dialogue: 3,{ass_time(t)},{ass_time(t + d)},SUB,,0,0,0,,{{\\fad(60,40)}}{accent(p)}")
        t += d
    return ev


def box(color, alpha_in, alpha_mid, t_in, t_out):
    # full-frame rectangle drawn with ASS vector drawing, used for flash and dip transitions
    return (f"{{\\pos(0,0)\\an7\\bord0\\shad0\\1c{color}\\alpha{alpha_in}"
            f"\\t(0,{t_in},\\alpha{alpha_mid})\\t({t_in},{t_in + t_out},\\alpha&HFF&)\\p1}}m 0 0 l {W} 0 {W} {H} 0 {H}{{\\p0}}")


def trans_events(kind, at):
    if kind == "flash":       # light burst covering the cut
        return [f"Dialogue: 5,{ass_time(at - 0.12)},{ass_time(at + 0.5)},FX,,0,0,0,,{box('&HE8F4FF&', '&HFF&', '&H10&', 120, 380)}"]
    if kind == "dip":         # quick dip through black
        return [f"Dialogue: 5,{ass_time(at - 0.35)},{ass_time(at + 0.45)},FX,,0,0,0,,{box('&H000000&', '&HFF&', '&H00&', 350, 450)}"]
    return []


def text_event(tx, start, end):
    kind = tx.get("kind", "label")
    style = {"year": "YEAR", "label": "LABEL", "title": "TITLE", "quote": "QUOTE", "flicker": "TITLE", "chapter": "CHAPTER"}[kind]
    px, py = tx.get("pos", [0.5, 0.5])
    body = accent(tx["content"].replace("\n", "\\N"))
    if kind == "year":
        fx = "{\\fad(180,250)\\t(0,1200,\\fscx104\\fscy104)}"
    elif kind == "title":
        fx = "{\\fad(500,600)\\blur1}"
    elif kind == "chapter":   # centred curiosity question at a chapter change
        fx = "{\\fad(350,450)\\fscx96\\fscy96\\t(0,900,\\fscx100\\fscy100)}"
    elif kind == "flicker":   # an old tube catching: off, stutter, on, with a warm bloom
        seq = [(0, 255), (90, 0), (140, 255), (300, 0), (330, 200), (420, 0), (470, 160), (520, 0)]
        tr = "".join(f"\\t({a},{a + 1},\\alpha&H{v:02X}&)" for a, v in seq)
        fx = "{\\alpha&HFF&" + tr + "\\blur0.6\\3c&H2A6BB0&\\bord3\\fad(0,700)}"
    else:
        fx = "{\\fad(220,220)}"
    return f"Dialogue: 1,{ass_time(start)},{ass_time(end)},{style},,0,0,0,,{{\\pos({int(px * W)},{int(py * H)})}}{fx}{body}"


# ---------------------------------------------------------------- main

def main():
    args = sys.argv[1:]
    spec_path, out = args[0], args[1]
    only_audio = "--only-audio" in args
    base = os.path.dirname(os.path.abspath(spec_path))
    spec = json.load(open(spec_path, encoding="utf-8"))
    all_says = [x.get("say") for x in spec["beats"] if x.get("say")]   # context for TTS stays that of the full script
    if "--until" in args:
        stop = args[args.index("--until") + 1]
        cut = next(i for i, b in enumerate(spec["beats"]) if b.get("id") == stop)
        spec["beats"] = spec["beats"][:cut]
        spec["music"] = [m for m in spec.get("music", []) if m["to"] != "end" and
                         [b.get("id") for b in spec["beats"]].count(m["from"])]
        for m in spec["music"]:
            if m["to"] not in [b.get("id") for b in spec["beats"]]:
                m["to"] = "end"
    voice = {"voice_id": PILJAE, **spec.get("voice", {})}
    global SUB_LIMIT, ASS_HEAD, DECLICK, SFX_GAIN
    SUB_LIMIT = spec.get("sub_limit")
    DECLICK = spec.get("declick", False)
    global LOOK, COLOUR, TAIL, REUSE_3D, LOOK_KEY
    if spec.get("look"):
        LOOK, COLOUR, LOOK_KEY = spec["look"], True, [spec["look"]]
    TAIL = spec.get("tail")
    REUSE_3D = float(spec.get("reuse_3d", 0))
    SFX_GAIN = 10 ** (spec.get("sfx_gain_db", 0) / 20)   # global trim for sound effects; announcements and "nogain" cues keep their level
    for name, font in spec.get("fonts", {}).items():   # e.g. {"TITLE": "Some Serif"} for Latin-script episodes
        ASS_HEAD = re.sub(rf"^(Style: {name},)[^,]+", rf"\g<1>{font}", ASS_HEAD, flags=re.M)
    ASS_FIELDS = ["Name", "Fontname", "Fontsize", "PrimaryColour", "SecondaryColour", "OutlineColour", "BackColour", "Bold", "Italic",
                  "Underline", "StrikeOut", "ScaleX", "ScaleY", "Spacing", "Angle", "BorderStyle", "Outline", "Shadow", "Alignment",
                  "MarginL", "MarginR", "MarginV", "Encoding"]
    for name, fields in spec.get("style_fields", {}).items():   # e.g. {"SUB": {"Outline": 2.4}} so subtitles read on light frames
        def patch(m, fields=fields):
            parts = m.group(0)[len("Style: "):].split(",")
            for k, v in fields.items():
                parts[ASS_FIELDS.index(k)] = str(v)
            return "Style: " + ",".join(parts)
        ASS_HEAD = re.sub(rf"^Style: {name},.*$", patch, ASS_HEAD, flags=re.M)
    gap = spec.get("gap", 0.05)
    work = os.path.splitext(out)[0] + "_work"
    os.makedirs(work, exist_ok=True)

    # 1. narration timing
    t, lines, anchors = 0.0, [], {}
    for i, b in enumerate(spec["beats"]):
        if b.get("id"):
            anchors[b["id"]] = t
        lead = b.get("lead", 0.0)
        if b.get("say"):
            says = all_says
            j = says.index(b["say"])
            ctx = {"previous_text": " ".join(says[max(0, j - 2):j]), "next_text": says[j + 1] if j + 1 < len(says) else ""}
            if b.get("ctx") is not None:   # e.g. a short reusing a long-form line: the long-form context hits its cached take
                ctx = b["ctx"] or None
            wav = tts(b["say"], {**voice, **({"emotion": b["emotion"]} if b.get("emotion") else {})},
                      ctx if voice.get("engine") == "elevenlabs" and spec.get("context", True) else None)
            if spec.get("max_pause"):
                wav = cap_pauses(wav, spec["max_pause"])
            d = dur(wav)
            if spec.get("pause") is not None:   # fixed audible pause between lines, measured on the takes themselves
                v0, v1 = voice_edges(wav)
                on = t + lead if not lines else max(t + lead - v0, lines[-1][0] + 0.01)
                lines.append((on, wav, d, b["say"]))
                b["_say_at"], b["_say_d"] = on, d
                b["_start"], b["_end"] = t, on + v1 + b.get("hold", 0.0) + spec["pause"]
                t = b["_end"]
                continue
            lines.append((t + lead, wav, d, b["say"]))
        else:
            d = 0.0
        b["_say_at"], b["_say_d"] = t + lead, d
        b["_start"], b["_end"] = t, t + lead + d + b.get("hold", 0.0) + gap
        t = b["_end"]
    total = t + 1.0
    anchors["end"] = total
    print(f"narration {total / 60:.1f} min, {len(lines)} lines")
    json.dump({"total": total, "anchors": anchors, "lines": [[round(a, 3), w, round(d, 3)] for a, w, d, _ in lines],
               "beats": [{"start": round(b["_start"], 2), "end": round(b["_end"], 2), "say": b.get("say", ""), "id": b.get("id")}
                         for b in spec["beats"]]},
              open(os.path.join(work, "timeline.json"), "w"), ensure_ascii=False, indent=1)

    # 2. audio: narration + sfx + music with ducking
    inputs, filt, vmix = [], [], []
    for k, (at, wav, d, _) in enumerate(lines):
        inputs += ["-i", wav]
        filt.append(f"[{len(inputs) // 2 - 1}:a]adelay={int(at * 1000)}:all=1[n{k}]")
        vmix.append(f"[n{k}]")
    filt.append(f"{''.join(vmix)}amix=inputs={len(vmix)}:normalize=0:duration=longest,apad=whole_dur={total:.2f},asplit=2[voice][key]")
    fx, ducked = [], []
    n = 0
    for b in spec["beats"]:
        items = b.get("sfx") or []
        items = items if isinstance(items, list) else [items]
        for sx in items:
            sx = sx if isinstance(sx, dict) else {"prompt": sx}
            src = os.path.join(base, sx["file"]) if sx.get("file") else sfx(sx["prompt"], sx.get("len"))
            inputs += ["-i", src]
            at = max(0.0, b["_start"] + sx.get("at", 0))
            chain = sx.get("filter", "")
            filt.append(f"[{len(inputs) // 2 - 1}:a]aresample=48000,{chain + ',' if chain else ''}adelay={int(at * 1000)}:all=1,volume={sx.get('vol', 0.45) * (1 if sx.get('nogain') or sx.get('duck') is False else SFX_GAIN):.4f}[f{n}]")
            # dialogue-like layers (announcements) stay on top, everything else ducks under the narration
            (fx if sx.get("duck") is False else ducked).append(f"[f{n}]")
            n += 1
    mus = list(ducked)
    for k, m in enumerate(spec.get("music", [])):
        a, z = anchors[m["from"]] + m.get("offset", 0), anchors[m["to"]]
        inputs += ["-stream_loop", "-1", *(["-ss", str(m["seek"])] if m.get("seek") else []), "-i", os.path.join(base, m["file"])]
        idx = len([x for x in inputs if x == "-i"]) - 1
        L = z - a
        vol = str(m.get('vol', 0.16))
        for gn in m.get("gain", []):   # e.g. {"at": "nordbf", "db": -7, "ramp": 1.5}: drop the bed from a beat on
            x, r, g = anchors[gn["at"]] - a, gn.get("ramp", 1.5), gn["db"] / 20
            vol += f"*if(lt(t,{x:.2f}),1,pow(10,{g}*min((t-{x:.2f})/{r},1)))"
        filt.append(f"[{idx}:a]aresample=48000,atrim=0:{L:.2f},asetpts=PTS-STARTPTS,volume='{vol}':eval=frame,"
                    f"afade=t=in:d={m.get('fade_in', 1.5)},afade=t=out:st={max(L - m.get('fade_out', 2.0), 0):.2f}:d={m.get('fade_out', 2.0)},"
                    f"adelay={int(a * 1000)}:all=1[m{k}]")
        mus.append(f"[m{k}]")
    def duck_expr():
        # optional "music_duck": [{"from": id, "to": id, "db": -9, "ramp": 1.5}] lowers the whole bed over a section
        terms = []
        for dk in spec.get("music_duck", []):
            a, z, r, g = anchors[dk["from"]], anchors[dk["to"]], dk.get("ramp", 1.5), dk["db"] / 20
            w = f"min(max((t-{a - r:.2f})/{r},0),1)*min(max(({z + r:.2f}-t)/{r},0),1)"
            terms.append(f"*pow(10,{g}*{w})")
        return f",volume='1{''.join(terms)}':eval=frame" if terms else ""
    # fix input indexing for narration/sfx (they were counted in pairs above)
    graph = ";".join(filt)
    if mus:
        graph += f";{''.join(mus)}amix=inputs={len(mus)}:normalize=0:duration=longest{duck_expr()}[mraw];" \
                 f"[mraw][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=500:makeup=1[mduck]"
        bed = "[mduck]"
    else:
        graph += ";[key]anullsink"
        bed = ""
    parts = ["[voice]"] + fx + ([bed] if bed else [])
    graph += f";{''.join(parts)}amix=inputs={len(parts)}:normalize=0:duration=first,atrim=0:{total:.2f},loudnorm=I=-14:TP=-1.5:LRA=11[aout]"
    audio = os.path.join(work, "audio.wav")
    cmd = ["ffmpeg", "-y", "-loglevel", "error"] + inputs + ["-filter_complex", graph, "-map", "[aout]", "-ar", "48000", audio]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-3000:])
    # second pass: single-pass loudnorm lands low on speech-heavy mixes, pin it to -14 LUFS
    meas = subprocess.run(["ffmpeg", "-i", audio, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", meas)[-1])
    if abs(lufs + 14) > 0.4 or spec.get("loud_always"):
        fixed = audio.replace(".wav", "_14.wav")
        sh("ffmpeg", "-y", "-i", audio, "-af", f"volume={spec.get('loud_target', -14) - lufs:.2f}dB,alimiter=limit={spec.get('loud_limit', 0.84)}:level=false", fixed)
        os.replace(fixed, audio)

    # subtitles file for upload (not burned in)
    with open(os.path.splitext(out)[0] + ".srt", "w", encoding="utf-8") as f:
        for n, (at, _, d, text) in enumerate(lines, 1):
            ts = lambda x: f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(x * 1000 % 1000):03d}"
            f.write(f"{n}\n{ts(at)} --> {ts(at + d)}\n{text}\n\n")
    if only_audio:
        print(audio)
        return

    # 3. shots: group beats that share a visual
    shots = []
    for b in spec["beats"]:
        v = b.get("visual", "same")
        if v == "same" and shots:
            shots[-1]["end"] = b["_end"]
            shots[-1]["beats"].append(b)
        else:
            shots.append({"v": v if v != "same" else {"type": "black"}, "start": b["_start"], "end": b["_end"], "beats": [b]})
    shots[-1]["end"] = total
    segs = []
    shard = os.environ.get("ASSEMBLE_SHARD")   # "k/n": only pre-render every n-th shot into the cache, then stop
    only = os.environ.get("ASSEMBLE_TYPES")    # with a shard: e.g. "3d" pre-renders only those visual types
    j = -1
    for i, s in enumerate(shots):
        d = s["end"] - s["start"]
        v = s["v"]
        if shard:
            k, n = map(int, shard.split("/"))
            if only:
                if v["type"] not in only.split(","):
                    continue
                j += 1
                if j % n != k:
                    continue
            elif i % n != k:
                continue
        print(f"shot {i + 1}/{len(shots)} {v['type']} {d:.1f}s", flush=True)
        if v["type"] == "3d":
            segs.append(render_3d(v, d))
        elif v["type"] == "image":
            segs.append(render_image(v, d, base))
        elif v["type"] == "video":
            segs.append(render_video(v, d, base))
        elif v["type"] == "g2d":
            segs.append(render_g2d(v, d, s["start"], s["beats"], base))
        else:
            segs.append(render_black(d))
    if shard:
        print("shard done", flush=True)
        return
    lst = os.path.join(work, "shots.txt")
    open(lst, "w").write("".join(f"file '{os.path.abspath(s)}'\n" if isinstance(s, str) else
                                 f"file '{os.path.abspath(s[0])}'\noutpoint {s[1]:.3f}\nduration {s[1]:.3f}\n" for s in segs))

    # 4. overlays
    ev = []
    if spec.get("subtitles", True):
        for b in spec["beats"]:
            if b.get("say") and not b.get("nosub"):
                ev += sub_events(b.get("sub", b["say"]), b["_say_at"], b["_say_at"] + b["_say_d"])
    for b in spec["beats"]:
        if b.get("trans"):
            ev += trans_events(b["trans"], b["_start"])
    for b in spec["beats"]:
        for tx in (b.get("text") if isinstance(b.get("text"), list) else [b["text"]] if b.get("text") else []):
            end = (b["_end"] if not tx.get("span") else b["_end"] + tx["span"]) + tx.get("extend", 0)
            ev.append(text_event(tx, b["_start"] + tx.get("delay", 0), end))
        if b.get("fade_out"):   # picture sinks slowly into black over the first seconds of the beat, then stays black
            a, z = b["_start"], b["_end"]
            ms = int(b["fade_out"] * 1000)
            ev.append(f"Dialogue: 4,{ass_time(a)},{ass_time(z)},FX,,0,0,0,,{{\\pos(0,0)\\an7\\bord0\\shad0\\1c&H000000&\\alpha&HFF&\\t(0,{ms},\\alpha&H00&)\\p1}}m 0 0 l {W} 0 {W} {H} 0 {H}{{\\p0}}")
    for s in shots:
        if s["v"].get("credit"):
            ev.append(f"Dialogue: 2,{ass_time(s['start'])},{ass_time(s['end'])},CREDIT,,0,0,0,,{s['v']['credit']}")
    ass = os.path.join(work, "overlay.ass")
    open(ass, "w", encoding="utf-8").write(ASS_HEAD + "\n".join(ev) + "\n")

    esc = lambda p: p.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    beats = spec["beats"]
    def window(i, b, key):
        n = (b[key].get("beats", 1) if isinstance(b[key], dict) else 1)
        return b["_start"], beats[min(i + n, len(beats)) - 1]["_end"]
    # darken + blur the picture behind graphics and centred text: one blurred branch, blended in over time windows
    dims = [window(i, b, "dim") for i, b in enumerate(beats) if b.get("dim")]
    ovs = []
    for i, b in enumerate(beats):
        if b.get("overlay"):
            a, z = window(i, b, "overlay")
            ovs.append((a, z, render_g2d({**b["overlay"], "alpha": True}, z - a, a, beats[i:i + b["overlay"].get("beats", 1)], base)))
    chain, extra = "[0:v]null[v0]", []
    cur = "[v0]"
    if dims:
        # cheap per-frame filters only: blur switched on inside the windows, darkening ramps in/out
        on = "+".join(f"between(t,{a:.3f},{z:.3f})" for a, z in dims)
        k = "min(" + "+".join(f"clip(min((t-{a:.2f})/0.45,({z:.2f}-t)/0.45),0,1)" for a, z in dims) + ",1)"
        cmds = []
        for a, z in dims:   # ramp the blur radius in 9 steps at both ends of each window
            for i in range(1, 10):
                sg = 16 * i / 9
                cmds.append(f"{a + (i - 1) * 0.05:.3f} gblur sigma {sg:.2f};")
                cmds.append(f"{z - i * 0.05:.3f} gblur sigma {sg:.2f};")
        cmds.sort(key=lambda c: float(c.split()[0]))
        cf = os.path.join(work, "dim_cmds.txt")
        open(cf, "w").write("\n".join(cmds) + "\n")
        chain += (f";{cur}sendcmd=f='{esc(cf)}',gblur=sigma=16:enable='{on}',"
                  f"eq=eval=frame:brightness='-0.16*{k}':saturation='1-0.5*{k}'[vd]")
        cur = "[vd]"
    for n, (a, z, f) in enumerate(ovs):
        extra += ["-i", f]
        chain += f";[{n + 2}:v]setpts=PTS-STARTPTS+{a:.3f}/TB[o{n}];{cur}[o{n}]overlay=eof_action=pass:enable='between(t,{a:.3f},{z:.3f})'[vo{n}]"
        cur = f"[vo{n}]"
    chain += (f";{cur}noise=alls=7:allf=t+u,vignette=angle=PI/4.6,"
              f"ass='{esc(ass)}':fontsdir='{esc(os.path.abspath(FONTS))}',format=yuv420p[vout]")
    chapters = [(b["_start"], b["chapter"]) for b in beats if b.get("chapter")]
    if chapters:
        with open(os.path.splitext(out)[0] + "_chapters.txt", "w", encoding="utf-8") as f:
            f.write("".join(f"{int(a // 60)}:{int(a % 60):02d} {c}\n" for a, c in chapters))
    sh("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", audio, *extra,
       "-filter_complex", chain, "-map", "[vout]", "-map", "1:a", "-t", f"{total:.2f}",
       "-c:v", "libx264", "-preset", "fast", *os.environ.get("FINAL_RATE", "-b:v 8M -maxrate 10M -bufsize 16M").split(), "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out)
    print(out, f"{total:.1f}s")


if __name__ == "__main__":
    main()
