# EP01 final compositor: shot frames + glass HUD + big subtitles + comparison cards + audio mix -> mp4.
# python3 compose.py <frames_dir> <out.mp4> [--preview] [--from S --to S]
import json, math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "..", "ep01_pov", "fonts") + "/"
AUD = os.environ.get("WHATIF_AUDIO", "/mnt/project-files/whatif_kr/assets/audio")
CARDS = os.environ.get("WHATIF_CARDS", "/mnt/project-files/whatif_kr/assets/cards")
FPS = 30; W, H = 1920, 1080
sys.path.insert(0, os.path.join(HERE, "..", "ep01_pov"))
from hud import tnt, weight, height as hstr  # noqa

def F(w, s, _c={}):
    k = (w, s)
    if k not in _c: _c[k] = ImageFont.truetype(FD + f"Pretendard-{w}.otf", s)
    return _c[k]

LINES = {d["id"]: d for d in json.load(open(os.path.join(HERE, "script.json")))}
def vodur(i):
    p = os.path.join(HERE, "vo", f"{i}.mp3")
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))

SEG = [("k8192", "hold", ["c00"]), ("e25", "cold", ["c01"]),
       ("s1", "still", ["l00", "l01", "l02"]),
       ("w2", "step", ["l03", "l04"]), ("w4", "step", ["l05"]), ("w8", "step", ["l06"]), ("w16", "step", ["l07"]),
       ("w32", "step", ["l08"]), ("s3", "step", ["l09"]), ("w128", "step", ["l10"]), ("w256", "step", ["l11"]),
       ("s_step9", "step", ["l12", "l13"]), ("k1024", "step", ["l14", "l15"]), ("k2048", "step", ["l16"]),
       ("k4096", "step", ["l17"]), ("k8192", "step", ["l18", "l19"]), ("k16384", "step", ["l20", "l21"]),
       ("e16", "step", ["l22"]), ("e18", "step", ["l23"]), ("e19", "step", ["l24"]), ("e21", "step", ["l25"]),
       ("e23", "step", ["l26"]), ("e25", "break", ["l27", "l28"]), ("end", "still", ["l29", "l30"])]
CARD = {"lotte": ("lotte.jpg", "롯데월드타워", "높이 555 m"), "baekdu": ("baekdu.jpg", "백두산", "높이 2,744 m"),
        "everest": ("everest.jpg", "에베레스트", "높이 8,849 m"), "iss": ("iss.jpg", "국제우주정거장", "고도 약 420 km"),
        "moon": ("moon.jpg", "달", "지름 3,474 km")}
LEAD = {"step": 0.95, "still": 0.6, "hold": 0.35, "cold": 0.2, "break": 0.3}
GAP = 0.35; NF = 18; HIT = 16; NF25 = 72

# ------------------------------------------------------------------ timeline
def build():
    t = 0.0; segs = []; subs = []; sfx = []
    for shot, mode, ids in SEG:
        d = {"shot": shot, "mode": mode, "t0": t, "step": LINES[ids[0]]["step"], "lines": []}
        x = t + LEAD[mode]
        if mode == "break":   # l27 slow descent, l28: hit 1.25 s into the line
            d0 = vodur(ids[0]); d1 = vodur(ids[1])
            d["lines"] = [(ids[0], x, d0)]; x2 = x + d0 + GAP
            d["lines"].append((ids[1], x2, d1)); d["hit"] = x2 + 1.25; x = max(x2 + d1, d["hit"] + 2.6) + 1.2
        elif mode == "cold":
            d0 = vodur(ids[0]); d["lines"] = [(ids[0], x, d0)]; d["hit"] = x + 0.55; x = max(x + d0, d["hit"] + 2.4) + 0.2
        else:
            for i in ids:
                dd = vodur(i); d["lines"].append((i, x, dd)); x += dd + GAP
            x += {"step": 0.45, "still": 0.5, "hold": 0.0}[mode]
        if mode == "step": d["land"] = t + NF / 24.0
        d["t1"] = x; t = x; segs.append(d)
        for i, s0, dd in d["lines"]:
            subs.append((s0, s0 + dd, LINES[i]["text"], LINES[i].get("card"), i))
        if "land" in d: sfx.append((d["land"], d["step"], "step"))
        if "hit" in d: sfx.append((d["hit"], 25, "break"))
    return segs, subs, sfx, t

# ------------------------------------------------------------------ frames
_cache = {}
def img(path, full=True):
    if path not in _cache:
        if len(_cache) > 40: _cache.clear()
        if not os.path.exists(path):
            print("MISSING", path); im = Image.new("RGB", (W, H), (60, 60, 60))
        else: im = Image.open(path).convert("RGB")
        if im.size != (W, H): im = im.resize((W, H), Image.LANCZOS)
        _cache[path] = im
    return _cache[path]

def shot_frame(fd, shot, i):
    p = os.path.join(fd, f"{shot}_{i:03d}.png")
    if not os.path.exists(p):   # fall back to the hold frame / nearest rendered frame
        for j in list(range(i, -1, -1)) + list(range(i, 200)):
            q = os.path.join(fd, f"{shot}_{j:03d}.png")
            if os.path.exists(q): return q
    return p

def last_index(fd, shot):
    n = [int(f.rsplit("_", 1)[1][:3]) for f in os.listdir(fd) if f.startswith(shot + "_") and f.endswith(".png")]
    return max(n) if n else 0

def base_frame(fd, d, t):
    shot, mode = d["shot"], d["mode"]; tau = t - d["t0"]; dur = d["t1"] - d["t0"]
    zoom = 1.0; shake = 0.0; tl = None
    drift = 0.0
    if mode in ("still", "hold"):
        p = shot_frame(fd, shot, 0 if mode == "still" else NF); zoom = 1.0 + 0.05 * tau / dur
        if shot == "s1": zoom = 1.12 - 0.10 * tau / dur; drift = 70 * (0.5 - tau / dur)
        if shot == "end": zoom = 1.02 + 0.10 * tau / dur; drift = -50 * (0.5 - tau / dur)
        if shot == "end": p = shot_frame(fd, "s1", 0)   # same view as the opening
    elif mode == "step":
        i = min(NF, int(tau * 24)); p = shot_frame(fd, shot, i)
        tl = t - d["land"]
        if tl >= 0: zoom = 1.0 + 0.045 * tl / max(0.1, d["t1"] - d["land"])
    else:   # break / cold on e25
        hit = d["hit"]; last = last_index(fd, "e25")
        if t < hit:
            pre = (t - d["t0"]) / (hit - d["t0"]); i = int(pre * HIT) if mode == "break" else int(8 + 8 * pre)
        else:
            i = HIT + int((t - hit) * 24)
        p = shot_frame(fd, "e25", min(i, last)); tl = t - hit
        if i >= last: zoom = 1.0 + 0.03 * (i - last) / 72.0 + 0.03 * max(0, t - hit - (last - HIT) / 24) / 3
    im = img(p)
    n = d["step"]
    if tl is not None and tl >= 0:
        A = (3 + 1.1 * n) if mode == "step" else 26
        shake = A * math.exp(-tl / 0.35)
    if zoom != 1.0 or shake > 0.3:
        rnd = random.Random(int(t * 1000))
        dx = rnd.uniform(-1, 1) * shake + drift; dy = rnd.uniform(-1, 1) * shake
        z = zoom + shake / 900 + 0.0001
        cw, ch = W / z, H / z; cx, cy = W / 2 + dx, H / 2 + dy
        im = im.resize((W, H), Image.BICUBIC, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))
    else:
        im = im.copy()
    return im

# ------------------------------------------------------------------ overlays
def glass(im, box, r=22, tint=(255, 255, 255), a=46):
    x0, y0, x1, y1 = [int(v) for v in box]
    reg = im.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(18))
    lum = sum(reg.resize((1, 1)).getpixel((0, 0))) / 3
    if lum > 120 and tint == (255, 255, 255):   # bright sky/ground: darker glass so white text stays readable
        tint, a = (25, 30, 40), int(40 + 0.5 * (lum - 120))
    reg = Image.blend(reg, Image.new("RGB", reg.size, tint), a / 255)
    mask = Image.new("L", reg.size, 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, reg.size[0] - 1, reg.size[1] - 1], r, fill=255)
    im.paste(reg, (x0, y0), mask)
    ImageDraw.Draw(im, "RGBA").rounded_rectangle((x0, y0, x1, y1), r, outline=(255, 255, 255, 90), width=2)

def stext(im, xy, s, font, fill=(255, 255, 255), anchor="la", sh=120):
    d = ImageDraw.Draw(im, "RGBA")
    d.text((xy[0] + 1, xy[1] + 2), s, font=font, fill=(0, 0, 0, sh // 2), anchor=anchor)
    d.text(xy, s, font=font, fill=fill, anchor=anchor)

_static = {}
def hud(im, n, t, land_t):
    M = -1.7 + 0.8 * n
    glass(im, (56, 56, 476, 210))
    stext(im, (86, 82), f"STEP {n}  ·  지진 규모", F("SemiBold", 19))
    stext(im, (80, 108), f"M {M:.1f}".replace("-", "−"), F("Light", 76))
    stext(im, (86, 184), tnt(n) if n > 0 else "≈ TNT 0 g", F("Regular", 19))
    glass(im, (1394, 56, 1864, 264))
    stext(im, (1834, 82), "현재 키", F("SemiBold", 19), anchor="ra")
    v, u = hstr(n); fu = F("Light", 40); fv = F("Light", 84)
    uw = ImageDraw.Draw(im).textlength(u, font=fu)
    stext(im, (1834 - uw - 8, 196), v, fv, anchor="rs"); stext(im, (1834, 196), u, fu, anchor="rs")
    stext(im, (1834, 206), weight(n), F("Regular", 21), anchor="ra")
    d = ImageDraw.Draw(im, "RGBA")
    d.line([(1424, 236), (1834, 236)], fill=(255, 255, 255, 110), width=2)
    frac = min(1, math.log2(1.75 * 2 ** n / 1.75) / 25) if n > 0 else 0
    d.line([(1424, 236), (1424 + 410 * frac, 236)], fill=(255, 214, 92, 255), width=4)
    d.ellipse([1424 + 410 * frac - 5, 231, 1424 + 410 * frac + 5, 241], fill=(255, 238, 180, 255))
    stext(im, (1424, 244), "1.75 m", F("Regular", 13)); stext(im, (1834, 244), "58,720 km", F("Regular", 13), anchor="ra")
    # live seismograph (scrolling), spikes on each landing
    gy0 = 760; glass(im, (56, gy0, 456, gy0 + 122))
    stext(im, (80, gy0 + 20), "지진계", F("SemiBold", 17)); stext(im, (432, gy0 + 20), f"규모 {M:.1f}".replace("-", "−"), F("Regular", 15), anchor="ra")
    pts = []
    for k in range(160):
        tt = t - (159 - k) / 60.0
        amp = 1.5
        if land_t is not None and tt >= land_t:
            amp += 30 * min(1, (M + 2.5) / 7) * math.exp(-(tt - land_t) / 0.9)
        r = random.Random(int(tt * 60)).uniform(-1, 1)
        pts.append((80 + k * 2.2, gy0 + 80 + max(-34, min(34, r * amp))))
    d.line(pts, fill=(255, 255, 255, 230), width=2); x, y = pts[-1]; d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 255, 255, 255))

def wrap(s, font, maxw=1500):
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    if d.textlength(s, font=font) <= maxw: return [s]
    best = None
    for k, ch in enumerate(s):
        if ch in ", " and 0 < k < len(s) - 1:
            a, b = s[:k + 1].strip(), s[k + 1:].strip()
            sc = max(d.textlength(a, font=font), d.textlength(b, font=font)) - (300 if ch == "," else 0)
            if best is None or sc < best[0]: best = (sc, [a, b])
    return best[1] if best else [s]

def subtitle(im, s, alpha=1.0):
    font = F("Bold", 64); lines = wrap(s, font)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    y = 1010 - 80 * (len(lines) - 1)
    for k, l in enumerate(lines):
        d.text((W / 2, y + 80 * k + 5), l, font=font, fill=(0, 0, 0, 170), anchor="ms", stroke_width=6, stroke_fill=(0, 0, 0, 170))
    sh = lay.filter(ImageFilter.GaussianBlur(5))
    d2 = ImageDraw.Draw(sh)
    for k, l in enumerate(lines):
        d2.text((W / 2, y + 80 * k), l, font=font, fill=(255, 255, 255, 255), anchor="ms", stroke_width=5, stroke_fill=(0, 0, 0, 255))
    if alpha < 1: sh.putalpha(sh.getchannel("A").point(lambda v: int(v * alpha)))
    im.paste(sh, (0, 0), sh)

def card(im, key, a):
    fn, title, line = CARD[key]; p = os.path.join(CARDS, fn)
    if not os.path.exists(p): return
    ph = Image.open(p).convert("RGB"); ph = ph.resize((430, int(430 * ph.size[1] / ph.size[0])), Image.LANCZOS)
    ph = ph.crop((0, 0, 430, min(ph.size[1], 400)))
    y0 = 300 + int(30 * (1 - a)); y1 = y0 + 20 + ph.size[1] + 120
    base = im.copy()
    glass(im, (1394, y0, 1864, y1))
    mk = Image.new("L", ph.size, 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, ph.size[0] - 1, ph.size[1] - 1], 16, fill=255)
    im.paste(ph, (1414, y0 + 20), mk)
    ty = y0 + 20 + ph.size[1] + 22
    stext(im, (1416, ty), title, F("SemiBold", 34)); stext(im, (1416, ty + 48), line, F("Regular", 22))
    if a < 1: im.paste(Image.blend(base, im, a))

# ------------------------------------------------------------------ audio
def load(p, sr=48000):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "2", "-ar", str(sr), "-"])
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

def mix(segs, subs, sfx, total, out_wav):
    sr = 48000; N = int((total + 1) * sr); mixb = np.zeros((N, 2), np.float32)
    def add(x, t, g):
        i = int(t * sr); x = x[: max(0, N - i)]; mixb[i:i + len(x)] += x * g
    for s0, s1, txt, c, i in subs:
        add(load(os.path.join(HERE, "vo", f"{i}.mp3")), s0, 1.0)
    imp = load(f"{AUD}/impact.wav"); quake = load(f"{AUD}/skyquake.wav"); crum = load(f"{AUD}/crumble.wav")
    for t, n, kind in sfx:
        if kind == "step":
            g = 10 ** ((-30 + 1.6 * min(n, 16)) / 20); add(imp, t - 0.05, g)
            if n >= 9: add(quake, t - 0.1, 10 ** ((-34 + 1.2 * (n - 9)) / 20))
        else:
            add(imp, t - 0.05, 10 ** (-8 / 20)); add(quake, t - 0.1, 10 ** (-10 / 20)); add(crum, t, 10 ** (-9 / 20))
    # music bed: angelic pad looped with crossfades, quiet, gentle top cut
    mus = load(f"{AUD}/music_angelic_E.wav"); L = len(mus); xf = int(2.0 * sr)
    bed = np.zeros((N, 2), np.float32); pos = 0; ramp = np.linspace(0, 1, xf)[:, None]
    while pos < N:
        m = mus.copy(); m[:xf] *= ramp; m[-xf:] *= ramp[::-1]
        e = min(N, pos + L); bed[pos:e] += m[:e - pos]; pos += L - xf
    # sidechain-ish duck under the voice
    env = np.ones(N, np.float32)
    for s0, s1, *_ in subs: env[int(s0 * sr):int(s1 * sr)] = 0.75
    k = int(0.25 * sr); env = np.convolve(env, np.ones(k) / k, mode="same").astype(np.float32)
    mixb += bed * env[:, None] * 10 ** (-17 / 20)
    mixb = mixb[:int(total * sr)]
    tmp = out_wav + ".raw.f32"; mixb.astype(np.float32).tofile(tmp)
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(sr), "-ac", "2", "-i", tmp,
                           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", out_wav])
    os.remove(tmp)

# ------------------------------------------------------------------ main
def main():
    fd, out = sys.argv[1], sys.argv[2]
    preview = "--preview" in sys.argv
    segs, subs, sfx, total = build()
    print(f"total {total:.1f}s, {len(segs)} segments")
    for d in segs: print(f"  {d['shot']:8s} {d['mode']:6s} {d['t0']:6.2f}-{d['t1']:6.2f} step {d['step']}")
    if "--plan" in sys.argv: return
    if "--stills" in sys.argv:   # QA: write composited stills at given times
        ts = [float(x) for x in sys.argv[sys.argv.index("--stills") + 1].split(",")]
        for t in ts:
            si = max(i for i, d in enumerate(segs) if d["t0"] <= t)
            frame(fd, segs, subs, si, t).save(f"{out}_{t:06.2f}.jpg", quality=90)
        return
    wav = out + ".wav"; mix(segs, subs, sfx, total, wav)
    fps = 15 if preview else FPS; scale = 0.5 if preview else 1.0
    nfr = int(total * fps)
    ow, oh = int(W * scale), int(H * scale)
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ow}x{oh}", "-r", str(fps), "-i", "-",
                            "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18" if not preview else "26", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    si = 0
    for f in range(nfr):
        t = f / fps
        while si < len(segs) - 1 and t >= segs[si]["t1"]: si += 1
        im = frame(fd, segs, subs, si, t)
        if scale != 1: im = im.resize((ow, oh), Image.BILINEAR)
        enc.stdin.write(im.tobytes())
        if f % 300 == 0: print("frame", f, "/", nfr, flush=True)
    enc.stdin.close(); enc.wait(); os.remove(wav)
    print("WROTE", out)

def frame(fd, segs, subs, si, t):
        d = segs[si]
        im = base_frame(fd, d, t)
        if d["mode"] not in ("hold", "cold") and d["shot"] != "end":
            n = d["step"]; land = d.get("land", d.get("hit"))
            if d["mode"] == "step" and t < d["land"]: n = segs[si - 1]["step"] if si > 0 else n
            hud(im, n, t, land)
        for s0, s1, txt, c, i in subs:
            if c and s0 - 0.1 <= t <= d["t1"] and d["t0"] <= s0:
                card(im, c, min(1, (t - s0 + 0.1) / 0.3))
        for s0, s1, txt, c, i in subs:
            if s0 <= t < s1 + 0.15:
                subtitle(im, txt); break
        return im

if __name__ == "__main__":
    main()
