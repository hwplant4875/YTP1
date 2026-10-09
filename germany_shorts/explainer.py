"""Build an original narrated Short from a beat script (JSON).

  python3 explainer.py spec.json out.mp4

Each beat = one narration line (Typecast, 필재 by default) over one licensed
clip (Pexels id or local file), with Korean subtitles, an optional ElevenLabs
sound effect at the start of the beat, and a quiet ambience bed under it all.

Spec:
{
  "title": "독일 크리스마스 마켓\\n*컵 가져가도 되는* 이유",   # top card, whole video
  "ambience": "christmas market crowd chatter, distant bells",  # optional
  "voice": {"voice_id": "tc_...", "emotion": "happy", "tempo": 1.1},
  "beats": [
    {"say": "narration", "sub": "subtitle (optional, *accent*)",
     "clip": {"pexels": 35006787, "start": 0.5} | {"file": "x.mp4"},
     "sfx": "short whoosh", "emotion": "normal"}
  ]
}
Needs TYPECAST_API_KEY, PEXELS_API_KEY, ELEVENLABS_API_KEY.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
CACHE = os.environ.get("SHORTS_CACHE", os.path.join(HERE, ".cache"))
W, H, FPS = 1080, 1920, 30
UA = {"User-Agent": "Mozilla/5.0 (germany-shorts)"}
PILJAE = "tc_68257f68bc6e3c161ab5078d"


def sh(*cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-2000:])
    return r.stdout


def duration(path):
    return float(sh("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path))


def cached(name, make):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name)
    if not os.path.exists(path):
        data = make()
        open(path, "wb").write(data)
    return path


def key(*parts):
    return hashlib.sha1(json.dumps(parts, ensure_ascii=False).encode()).hexdigest()[:16]


def http(url, data=None, headers=None, timeout=120):
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    return urllib.request.urlopen(req, timeout=timeout).read()


# ---------------------------------------------------------------- sources

def tts(text, voice):
    body = {"voice_id": voice.get("voice_id", PILJAE), "text": text, "model": voice.get("model", "ssfm-v21"),
            "language": "kor",
            "prompt": {"emotion_preset": voice.get("emotion", "normal"), "emotion_intensity": voice.get("intensity", 1.0)},
            "output": {"audio_format": "wav", "audio_tempo": voice.get("tempo", 1.1), "volume": 100}}
    return cached(f"tts_{key(body)}.wav", lambda: http(
        "https://api.typecast.ai/v1/text-to-speech", json.dumps(body).encode(),
        {"X-API-KEY": os.environ["TYPECAST_API_KEY"], "Content-Type": "application/json"}))


def sfx(prompt, seconds=None):
    body = {"text": prompt, "prompt_influence": 0.5}
    if seconds:
        body["duration_seconds"] = seconds
    return cached(f"sfx_{key(body)}.mp3", lambda: http(
        "https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128", json.dumps(body).encode(),
        {"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"}))


def pexels(vid):
    def fetch():
        info = json.loads(http(f"https://api.pexels.com/videos/videos/{vid}",
                               headers={"Authorization": os.environ["PEXELS_API_KEY"]}))
        files = [f for f in info["video_files"] if f.get("width") and f["file_type"] == "video/mp4"]
        portrait = [f for f in files if f["height"] >= f["width"]] or files
        best = min(portrait, key=lambda f: abs(f["height"] - 1920))
        return http(best["link"], timeout=300)
    return cached(f"pexels_{vid}.mp4", fetch)


# ---------------------------------------------------------------- subtitles

def ass_color(hexrgb):
    return f"&H00{hexrgb[4:6]}{hexrgb[2:4]}{hexrgb[0:2]}".upper()


def accent(text, color="FFD400"):
    text = text.replace("\n", "\\N")
    return re.sub(r"\*(.+?)\*", lambda m: "{\\c" + ass_color(color) + "&}" + m.group(1) + "{\\c&HFFFFFF&}", text)


def ass_time(t):
    h, t = divmod(max(t, 0), 3600)
    m, s = divmod(t, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def chunks(text, limit=14):
    """Split a line into subtitle chunks of about `limit` characters, at spaces and commas."""
    words = re.findall(r"\S+", text)
    out, cur = [], ""
    for w in words:
        if cur and len((cur + " " + w).replace("*", "")) > limit:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
        if cur.endswith((",", "?", "!", ".")) and len(cur.replace("*", "")) >= limit * 0.5:
            out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    # keep *accent* pairs balanced inside each chunk
    fixed, carry = [], False
    for c in out:
        if carry:
            c = "*" + c
        carry = c.count("*") % 2 == 1
        fixed.append(c + ("*" if carry else ""))
    return [c.rstrip(".,") for c in fixed]


def build_ass(title, timeline, path):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: SUB,Pretendard Black,86,&H00FFFFFF,&H00FFFFFF,&H00141414,&H8C000000,0,0,0,0,100,100,0,0,1,7,5,5,40,40,40,1
Style: TITLE,Black Han Sans,96,&H00FFFFFF,&H00FFFFFF,&H00101010,&H8C000000,0,0,0,0,100,100,1,0,1,8,6,8,50,50,250,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    total = timeline[-1][1] if timeline else 0
    ev = []
    if title:
        ev.append(f"Dialogue: 1,{ass_time(0)},{ass_time(total)},TITLE,,0,0,0,,{{\\fad(150,0)}}{accent(title)}")
    pop = "{\\fscx86\\fscy86\\t(0,90,\\fscx104\\fscy104)\\t(90,160,\\fscx100\\fscy100)}"
    for start, end, sub in timeline:
        parts = chunks(sub)
        weights = [max(len(p.replace("*", "")), 3) for p in parts]
        t = start
        for p, wgt in zip(parts, weights):
            d = (end - start) * wgt / sum(weights)
            ev.append(f"Dialogue: 0,{ass_time(t)},{ass_time(t + d)},SUB,,0,0,0,,{{\\pos({W // 2},{int(H * 0.66)})}}{pop}{accent(p)}")
            t += d
    open(path, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")


# ---------------------------------------------------------------- build

def clip_segment(src, start, dur, out):
    zoom = f"scale=w='trunc({W}*(1.06+0.06*t/{dur:.3f})/2)*2':h=-2:eval=frame,crop={W}:{H}"
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
          f"{zoom},fps={FPS},setsar=1,eq=saturation=1.08:contrast=1.03")
    src_len = duration(src)
    loop = ["-stream_loop", "-1"] if start + dur > src_len else []
    sh("ffmpeg", "-y", "-loglevel", "error", *loop, "-ss", f"{min(start, max(src_len - 0.5, 0)):.2f}", "-i", src,
       "-t", f"{dur:.3f}", "-an", "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
       "-pix_fmt", "yuv420p", out)


def build(spec_path, out):
    spec = json.load(open(spec_path, encoding="utf-8"))
    voice = {"voice_id": PILJAE, **spec.get("voice", {})}
    work = os.path.splitext(out)[0] + "_work"
    os.makedirs(work, exist_ok=True)
    gap = spec.get("gap", 0.12)

    t, timeline, segs, voice_parts, sfx_parts = 0.0, [], [], [], []
    for i, b in enumerate(spec["beats"]):
        wav = tts(b["say"], {**voice, **({"emotion": b["emotion"]} if b.get("emotion") else {})})
        d = duration(wav) + gap
        clip = b["clip"]
        src = pexels(clip["pexels"]) if "pexels" in clip else clip["file"]
        seg = os.path.join(work, f"seg{i:02d}.mp4")
        clip_segment(src, clip.get("start", 0), d, seg)
        segs.append(seg)
        voice_parts.append((wav, t))
        if b.get("sfx"):
            sfx_parts.append((sfx(b["sfx"], b.get("sfx_len")), t + b.get("sfx_at", 0), b.get("sfx_vol", 0.55)))
        timeline.append((t, t + d - gap, b.get("sub", b["say"])))
        t += d
    total = t + 0.3

    lst = os.path.join(work, "list.txt")
    open(lst, "w").write("".join(f"file '{os.path.abspath(s)}'\n" for s in segs))
    video = os.path.join(work, "video.mp4")
    sh("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video)

    ass = os.path.join(work, "subs.ass")
    build_ass(spec.get("title"), timeline, ass)

    inputs, filters, mix = [], [], []
    for k, (path, at) in enumerate(voice_parts):
        inputs += ["-i", path]
        filters.append(f"[{k + 1}:a]adelay={int(at * 1000)}:all=1,volume=1.0[v{k}]")
        mix.append(f"[v{k}]")
    n = len(voice_parts)
    for k, (path, at, vol) in enumerate(sfx_parts):
        inputs += ["-i", path]
        filters.append(f"[{n + k + 1}:a]adelay={int(at * 1000)}:all=1,volume={vol}[s{k}]")
        mix.append(f"[s{k}]")
    if spec.get("ambience"):
        amb = sfx(spec["ambience"], 22)
        inputs += ["-stream_loop", "-1", "-i", amb]
        idx = n + len(sfx_parts) + 1
        filters.append(f"[{idx}:a]atrim=0:{total:.2f},volume={spec.get('ambience_vol', 0.18)},"
                       f"afade=t=out:st={total - 0.8:.2f}:d=0.8[amb]")
        mix.append("[amb]")
    esc = lambda p: p.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    graph = ";".join(filters) + f";{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=longest," \
        f"atrim=0:{total:.2f},loudnorm=I=-14:TP=-1.5:LRA=11[a];" \
        f"[0:v]tpad=stop_mode=clone:stop_duration=0.5,ass='{esc(ass)}':fontsdir='{esc(FONTS)}'[v]"
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", video, *inputs, "-filter_complex", graph,
       "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out)
    # second pass: hit -14 LUFS exactly (single-pass loudnorm undershoots on short clips)
    meas = subprocess.run(["ffmpeg", "-i", out, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", meas)[-1])
    if abs(lufs + 14) > 0.5:
        tmp = out + ".tmp.mp4"
        sh("ffmpeg", "-y", "-loglevel", "error", "-i", out, "-c:v", "copy",
           "-af", f"volume={-14 - lufs:.2f}dB,alimiter=limit=0.8:level=false", "-c:a", "aac", "-b:a", "192k", tmp)
        os.replace(tmp, out)
    credits = sorted({f"Pexels video {b['clip']['pexels']}" for b in spec["beats"] if "pexels" in b["clip"]})
    print(f"{out}  {total:.1f}s\nfootage: {', '.join(credits)}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    build(sys.argv[1], sys.argv[2])
