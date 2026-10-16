"""Cut the rendered shots to the timeline, upscale 720x1280 -> 1080x1920, burn captions, mix voice + music + SFX.
  python3 assemble.py            -> out/oa01_dancing_plague.mp4"""
import glob, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
TL = json.load(open(os.path.join(HERE, "timeline.json")))
C, SH, OUT = os.path.join(HERE, ".cache"), os.path.join(HERE, ".shots"), os.path.join(HERE, "out")
FONTS = os.path.abspath(os.path.join(HERE, "../../../fonts"))
os.makedirs(OUT, exist_ok=True)
TOTAL = TL["total"]
def sh(*a): subprocess.run(a, check=True)

# ---------------------------------------------------------------- captions (1-3 words, white, black stroke, y ~ 62 %)
def chunks(words, maxc=13):
    out, cur = [], []
    for w in words:
        if cur and len(" ".join(x[0] for x in cur + [w]).rstrip(",.")) > maxc:
            out.append(cur); cur = []
        cur.append(w)
        if len(cur) == 3 or re.search(r"[,.!?]$", w[0]):
            out.append(cur); cur = []
    if cur: out.append(cur)
    return out
def ts(t): t = max(0, t); return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"
ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2", "",
       "[V4+ Styles]", "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Cap,YouTube Sans Dark,108,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,9,3,5,80,180,0,1", "",
       "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for li, L in enumerate(TL["lines"]):
    nxt = TL["lines"][li + 1]["start"] if li + 1 < len(TL["lines"]) else TOTAL
    # caption text may differ from the spoken text ("fifteen eighteen" -> "1518"): map word by word where counts match
    spoken = L["words"]; shown = L["cap"].split()
    if len(shown) != len(spoken):   # numbers written as digits: re-time the shown words across the spoken span
        s0, s1 = spoken[0][1], spoken[-1][2]; n = len(shown); tot = sum(len(w) + 2 for w in shown); acc = 0; ww = []
        for w in shown: a = s0 + (s1 - s0) * acc / tot; acc += len(w) + 2; ww.append([w, a, s0 + (s1 - s0) * acc / tot])
        spoken = ww
    else:
        spoken = [[shown[i], w[1], w[2]] for i, w in enumerate(spoken)]
    cs = chunks(spoken)
    for k, c in enumerate(cs):
        a = c[0][1]; b = cs[k + 1][0][1] if k + 1 < len(cs) else min(c[-1][2] + 0.25, nxt)
        txt = " ".join(w[0] for w in c).rstrip(",.")
        ass.append(f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\pos(490,1190)\\fad(40,0)}}{txt}")
open(os.path.join(HERE, ".cache/caps.ass"), "w").write("\n".join(ass) + "\n")

# ---------------------------------------------------------------- picture
spans = TL["spans"]; files = []
for k, sp in enumerate(spans):
    f = sorted(glob.glob(os.path.join(SH, f"{k:02d}_{sp['shot']}_*.mp4")), key=os.path.getmtime)
    assert f, f"missing shot {k} {sp['shot']}"; files.append(f[-1])
inp, fc = [], []
for k, (f, sp) in enumerate(zip(files, spans)):
    inp += ["-i", f]; fc.append(f"[{k}:v]trim=duration={sp['dur']:.3f},setpts=PTS-STARTPTS,fps=24[v{k}]")
fc.append("".join(f"[v{k}]" for k in range(len(files))) + f"concat=n={len(files)}:v=1:a=0[cat]")
fc.append(f"[cat]scale=1080:1920:flags=lanczos,unsharp=5:5:0.6,eq=saturation=1.08:contrast=1.03,subtitles={os.path.join(C, 'caps.ass')}:fontsdir={FONTS},"
          f"fade=t=out:st={TOTAL - 0.35:.2f}:d=0.35,trim=duration={TOTAL:.3f}[vout]")
pic = os.path.join(C, "picture.mp4")
sh("ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(fc), "-map", "[vout]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "24", pic)

# ---------------------------------------------------------------- sound
ai, parts = [], []
for L in TL["lines"]:
    a0, b0 = L["trim"]; n = len(ai) // 2
    ai += ["-i", os.path.join(C, f"l{L['i']:02d}.wav")]
    parts.append(f"[{n}:a]atrim={a0:.3f}:{b0:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b0 - a0 - 0.08:.3f}:d=0.08,"
                 f"adelay={int(L['start'] * 1000)},apad[l{n}]")
nv = len(TL["lines"])
ai += ["-i", os.path.join(HERE, "music/master_of_the_feast.mp3"), "-i", os.path.join(C, "sfx_crowd.mp3")]
parts.append(f"[{nv}:a]aresample=48000,aformat=channel_layouts=mono,volume=0.2,afade=t=in:d=0.15,afade=t=out:st={TOTAL - 2.2:.2f}:d=2.2[mus]")
# crowd bed under the crowd shots only, quiet, faded in and out
crowd_spans = [(0.0, 4.1), (19.6, 38.1)]
segs = []
for j, (a, b) in enumerate(crowd_spans):
    d = b - a
    parts.append(f"[{nv + 1}:a]aresample=48000,aformat=channel_layouts=mono,aloop=loop=-1:size=578000,atrim=0:{d:.2f},volume=0.09,"
                 f"afade=t=in:d=0.4,afade=t=out:st={d - 0.8:.2f}:d=0.8,adelay={int(a * 1000)},apad[c{j}]" if j else
                 f"[{nv + 1}:a]aresample=48000,aformat=channel_layouts=mono,atrim=0:{d:.2f},volume=0.09,afade=t=out:st={d - 0.8:.2f}:d=0.8,apad[c{j}]")
    segs.append(f"[c{j}]")
mix = "".join(f"[l{k}]" for k in range(nv)) + "[mus]" + "".join(segs)
parts.append(f"{mix}amix=inputs={nv + 1 + len(segs)}:normalize=0:duration=longest,atrim=0:{TOTAL:.3f}[mx]")
raw = os.path.join(C, "mix_raw.wav")
sh("ffmpeg", "-v", "error", "-y", *ai, "-filter_complex", ";".join(parts), "-map", "[mx]", "-ar", "48000", "-ac", "2", raw)
m = subprocess.run(["ffmpeg", "-nostats", "-i", raw, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", m)[-1])
fixed = os.path.join(C, "mix.wav")
sh("ffmpeg", "-v", "error", "-y", "-i", raw, "-af", f"volume={-14 - lufs:.2f}dB,alimiter=limit=0.87:level=false", fixed)
final = os.path.join(OUT, "oa01_dancing_plague.mp4")
sh("ffmpeg", "-v", "error", "-y", "-i", pic, "-i", fixed, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final)
m2 = subprocess.run(["ffmpeg", "-nostats", "-i", final, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
print("raw", lufs, "final", re.findall(r"I:\s+(-?[\d.]+) LUFS", m2)[-1], final)
