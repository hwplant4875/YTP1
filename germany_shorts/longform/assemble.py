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
W, H, FPS = 1920, 1080, 30
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
        make(tmp)
        os.replace(tmp, path)
    return path


def http(url, data=None, headers=None, timeout=300):
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    return urllib.request.urlopen(req, timeout=timeout).read()


# ---------------------------------------------------------------- audio

def tts(text, voice):
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


def sfx(prompt, seconds=None):
    body = {"text": prompt, "prompt_influence": 0.5}
    if seconds:
        body["duration_seconds"] = seconds
    return cached(f"sfx_{key(body)}.mp3", lambda p: open(p, "wb").write(http(
        "https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128", json.dumps(body).encode(),
        {"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})))


# ---------------------------------------------------------------- visuals

LOOK = "eq=saturation=0:contrast=1.08:brightness=-0.02"   # archive material goes black and white


def render_3d(v, d):
    k = key(v, round(d, 3))
    def make(p):
        sh("node", os.path.join(HERE, "render.mjs"), f"scenes/{v['scene']}.js", p + ".mp4",
           "--dur", f"{d:.3f}", "--fps", FPS, "--shot", v.get("shot", ""), "--t0", v.get("t0", 0))
        os.replace(p + ".mp4", p)
    return cached(f"3d_{v['scene']}_{v.get('shot', '')}_{k}.mp4", make)


def render_image(v, d, base):
    """Ken Burns on a still, done in float precision (no zoompan jitter)."""
    from PIL import Image
    k = key(v, round(d, 3))
    def make(p):
        src = Image.open(os.path.join(base, v["file"])).convert("L").convert("RGB")
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
    k = key(v, round(d, 3))
    speed = v.get("speed", 1.0)
    crop = v.get("crop")  # [x, y, w, h] in source pixels, to cut away old captions or logos
    vf = (f"crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]}," if crop else "") + \
        f"setpts=PTS/{speed},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1,{LOOK}"
    return cached(f"vid_{k}.mp4", lambda p: sh(
        "ffmpeg", "-y", "-ss", v.get("start", 0), "-i", os.path.join(base, v["file"]), "-t", f"{d * speed:.3f}",
        "-an", "-vf", vf, "-t", f"{d:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-f", "mp4", p))


def render_black(d):
    return cached(f"black_{round(d, 3)}.mp4", lambda p: sh(
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
Style: TITLE,Noto Serif KR Black,118,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,2,0,1,0,6,5,0,0,0,1
Style: QUOTE,Noto Serif KR SemiBold,64,&H00F0F0F0,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,0,4,5,0,0,0,1
Style: CREDIT,Pretendard Medium,22,&H99FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,3,0,30,22,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def text_event(tx, start, end):
    kind = tx.get("kind", "label")
    style = {"year": "YEAR", "label": "LABEL", "title": "TITLE", "quote": "QUOTE"}[kind]
    px, py = tx.get("pos", [0.5, 0.5])
    body = tx["content"].replace("\n", "\\N")
    if kind == "year":
        fx = "{\\fad(180,250)\\t(0,1200,\\fscx104\\fscy104)}"
    elif kind == "title":
        fx = "{\\fad(500,600)\\blur1}"
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
    voice = {"voice_id": PILJAE, **spec.get("voice", {})}
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
            wav = tts(b["say"], {**voice, **({"emotion": b["emotion"]} if b.get("emotion") else {})})
            d = dur(wav)
            lines.append((t + lead, wav, d, b["say"]))
        else:
            d = 0.0
        b["_start"], b["_end"] = t, t + lead + d + b.get("hold", 0.0) + gap
        t = b["_end"]
    total = t + 1.0
    anchors["end"] = total
    print(f"narration {total / 60:.1f} min, {len(lines)} lines")
    json.dump({"total": total, "anchors": anchors,
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
    fx = []
    for k, b in enumerate(spec["beats"]):
        if not b.get("sfx"):
            continue
        sx = b["sfx"] if isinstance(b["sfx"], dict) else {"prompt": b["sfx"]}
        inputs += ["-i", sfx(sx["prompt"], sx.get("len"))]
        at = b["_start"] + sx.get("at", 0)
        filt.append(f"[{len(inputs) // 2 - 1}:a]aresample=48000,adelay={int(at * 1000)}:all=1,volume={sx.get('vol', 0.45)}[f{k}]")
        fx.append(f"[f{k}]")
    mus = []
    for k, m in enumerate(spec.get("music", [])):
        a, z = anchors[m["from"]] + m.get("offset", 0), anchors[m["to"]]
        inputs += ["-stream_loop", "-1", "-i", os.path.join(base, m["file"])]
        idx = len([x for x in inputs if x == "-i"]) - 1
        L = z - a
        filt.append(f"[{idx}:a]aresample=48000,atrim=0:{L:.2f},asetpts=PTS-STARTPTS,volume={m.get('vol', 0.16)},"
                    f"afade=t=in:d={m.get('fade_in', 1.5)},afade=t=out:st={max(L - m.get('fade_out', 2.0), 0):.2f}:d={m.get('fade_out', 2.0)},"
                    f"adelay={int(a * 1000)}:all=1[m{k}]")
        mus.append(f"[m{k}]")
    # fix input indexing for narration/sfx (they were counted in pairs above)
    graph = ";".join(filt)
    if mus:
        graph += f";{''.join(mus)}amix=inputs={len(mus)}:normalize=0:duration=longest[mraw];" \
                 f"[mraw][key]sidechaincompress=threshold=0.04:ratio=5:attack=30:release=600:makeup=1[mduck]"
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
        else:
            shots.append({"v": v if v != "same" else {"type": "black"}, "start": b["_start"], "end": b["_end"]})
    shots[-1]["end"] = total
    segs = []
    for i, s in enumerate(shots):
        d = s["end"] - s["start"]
        v = s["v"]
        print(f"shot {i + 1}/{len(shots)} {v['type']} {d:.1f}s", flush=True)
        if v["type"] == "3d":
            segs.append(render_3d(v, d))
        elif v["type"] == "image":
            segs.append(render_image(v, d, base))
        elif v["type"] == "video":
            segs.append(render_video(v, d, base))
        else:
            segs.append(render_black(d))
    lst = os.path.join(work, "shots.txt")
    open(lst, "w").write("".join(f"file '{os.path.abspath(s)}'\n" for s in segs))

    # 4. overlays
    ev = []
    for b in spec["beats"]:
        if b.get("text"):
            tx = b["text"]
            end = b["_end"] if not tx.get("span") else b["_end"] + tx["span"]
            ev.append(text_event(tx, b["_start"] + tx.get("delay", 0), end))
    for s in shots:
        if s["v"].get("credit"):
            ev.append(f"Dialogue: 2,{ass_time(s['start'])},{ass_time(s['end'])},CREDIT,,0,0,0,,{s['v']['credit']}")
    ass = os.path.join(work, "overlay.ass")
    open(ass, "w", encoding="utf-8").write(ASS_HEAD + "\n".join(ev) + "\n")

    esc = lambda p: p.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    grade = ("noise=alls=7:allf=t+u,vignette=angle=PI/4.6,"
             f"ass='{esc(ass)}':fontsdir='{esc(os.path.abspath(FONTS))}'")
    sh("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", audio,
       "-vf", grade, "-map", "0:v", "-map", "1:a", "-t", f"{total:.2f}",
       "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out)
    print(out, f"{total:.1f}s")


if __name__ == "__main__":
    main()
