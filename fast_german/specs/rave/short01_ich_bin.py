"""German Rave short 01: "Ich bin Nick" (sein). 9:16 club-lyric render.

python3 specs/rave/short01_ich_bin.py AUDIO.wav OUT.mp4
"""
import math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
FONT = "/mnt/project-files/fonts/rave/Anton-Regular.ttf"
ACID = (182, 255, 0)
UV = (150, 60, 255)
PINK = (255, 40, 170)
WHITE = (255, 255, 255)

# word timings (s) in the edited track; "en" pairs are sung in English, "de" in German
LINES = [
    ("en", [("MY", 0.00), ("NAME", 0.44), ("IS", 0.64), ("NICK", 0.88)], 1.10),
    ("de", [("ICH", 2.20), ("BIN", 2.76), ("NICK", 2.96)], 3.30),
    ("en", [("MY", 3.68), ("NAME", 4.24), ("IS", 4.52), ("NICK", 4.70)], 4.95),
    ("de", [("ICH", 6.18), ("BIN", 6.62), ("NICK", 6.82)], 7.20),
    ("tbl", [("ICH BIN", 7.57), ("ICH BIN", 8.71), ("DU BIST", 9.67), ("DU BIST", 10.57),
             ("ER IST", 11.39), ("SIE IST", 12.21)], 13.30),
    ("de", [("ICH", 13.59), ("BIN", 13.93), ("NICK", 14.15)], 14.45),
    ("en", [("MY", 15.19), ("NAME", 15.45), ("IS", 15.67), ("NICK", 15.87)], 16.10),
    ("de", [("ICH", 16.91), ("BIN", 17.35), ("NICK", 17.57)], 17.85),
    ("en", [("MY", 18.57), ("NAME", 18.87), ("IS", 19.09), ("NICK", 19.31)], 19.55),
    ("de", [("ICH", 20.39), ("BIN", 20.79), ("NICK", 21.01)], 21.50),
]
PAIRS = [(0, 1), (2, 3), (4, None), (5, None), (6, 7), (8, 9)]
TABLE = [("ICH BIN", "I am"), ("DU BIST", "you are"), ("ER IST", "he is"), ("SIE IST", "she is")]

_fonts = {}
def F(s):
    if s not in _fonts: _fonts[s] = ImageFont.truetype(FONT, s)
    return _fonts[s]

def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

def kicks(audio):
    sr, hop = 22050, 220
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", audio, "-af", "lowpass=f=120", "-f", "s16le",
                          "-ac", "1", "-ar", str(sr), "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    env = np.sqrt(np.convolve(a ** 2, np.ones(hop) / hop, "same"))[::hop]
    d = np.maximum(np.diff(env, prepend=0), 0)
    th, out, last = d.max() * 0.3, [], -1
    for i in range(1, len(d) - 1):
        s = i * hop / sr
        if d[i] > th and d[i] >= d[i - 1] and d[i] >= d[i + 1] and s - last > 0.2:
            out.append(s); last = s
    return np.array(out), len(a) / sr

def pulse(t, K):
    p = K[K <= t]
    return math.exp(-(t - p[-1]) * 9) if len(p) else 0.0

def background():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    bg = np.zeros((H, W, 3), np.float32) + np.array([7, 5, 12], np.float32)
    for cx, cy, r, col in [(540, -100, 800, (28, 10, 55)), (100, 1600, 600, (35, 5, 30)), (1000, 1200, 500, (8, 22, 12))]:
        g = np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * r * r))[..., None]
        bg += g * np.array(col, np.float32)
    return bg

def lasers(t, pk):
    s = 2; L = Image.new("RGB", (W // s, H // s)); d = ImageDraw.Draw(L)
    ox, oy = W // s // 2, -10
    n = 9
    for i in range(n):
        base = -60 + 120 * i / (n - 1)
        ang = math.radians(90 + base * (0.7 + 0.3 * math.sin(t * 1.3)) + 12 * math.sin(t * 2.1 + i))
        ex, ey = ox + math.cos(ang) * 2000, oy + math.sin(ang) * 2000
        col = ACID if i % 4 != 1 else UV
        k = 0.55 + 0.45 * pk
        d.line([(ox, oy), (ex, ey)], fill=tuple(int(c * k) for c in col), width=2)
    # floor grid
    hz = 1240 // s
    sp = (t * 2.0) % 1.0
    for j in range(12):
        z = (j + sp) / 12
        yy = hz + (H // s - hz) * z ** 2.2
        d.line([(0, yy), (W // s, yy)], fill=(int(60 * z), 15, int(110 * z)), width=1)
    for j in range(-10, 11):
        d.line([(W // s // 2 + j * 12, hz), (W // s // 2 + j * 160, H // s)], fill=(45, 15, 85), width=1)
    glow = L.filter(ImageFilter.GaussianBlur(6))
    arr = np.asarray(L, np.float32) * 0.8 + np.asarray(glow, np.float32) * 1.8
    return np.asarray(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32)

def text_w(s, size, sp=0):
    f = F(size); return sum(f.getlength(c) for c in s) + sp * (len(s) - 1)

def draw_words(d, words, t, y, size, col_on, maxw=900):
    size = min(size, int(size * maxw / max(1, text_w(" ".join(w for w, _ in words), size))))
    f = F(size); gap = f.getlength(" ")
    total = sum(f.getlength(w) for w, _ in words) + gap * (len(words) - 1)
    x = (W - total) / 2
    for w, ws in words:
        on = t >= ws
        p = ease((t - ws) / 0.12) if on else 0
        sc = 1.0 + 0.25 * (1 - p) if on else 1.0
        fw = F(int(size * sc)); ww = fw.getlength(w)
        cx = x + f.getlength(w) / 2
        if on:
            d.text((cx - ww / 2, y - (fw.size - size) * 0.6), w, font=fw, fill=col_on, stroke_width=8, stroke_fill=(0, 0, 0))
        else:
            d.text((x, y), w, font=f, fill=(0, 0, 0, 120), stroke_width=3, stroke_fill=(255, 255, 255, 90))
        x += f.getlength(w) + gap

def frame_text(t, pk):
    T = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(T)
    # brand + lesson chip
    d.text((W / 2 - text_w("GERMAN RAVE", 64) / 2, 230), "GERMAN RAVE", font=F(64), fill=ACID, stroke_width=6, stroke_fill=(0, 0, 0))
    chip = "LESSON 01  ·  SEIN"
    cw = text_w(chip, 40)
    d.rounded_rectangle([W / 2 - cw / 2 - 22, 318, W / 2 + cw / 2 + 22, 378], 30, outline=UV, width=4)
    d.rounded_rectangle([W / 2 - cw / 2 - 22, 318, W / 2 + cw / 2 + 22, 378], 30, fill=(0, 0, 0, 200), outline=UV, width=4)
    d.text((W / 2 - cw / 2, 322), chip, font=F(40), fill=WHITE)
    pair = None
    for a, b in PAIRS:
        st = LINES[a][1][0][1] - 0.35
        en = LINES[b][2] + 0.6 if b is not None else LINES[a][2] + 0.25
        nxt = [LINES[x][1][0][1] - 0.35 for x, _ in PAIRS if LINES[x][1][0][1] - 0.35 > st]
        if nxt: en = min(en, nxt[0])
        if st <= t < en: pair = (a, b)
    if pair is None:
        pair = PAIRS[0] if t < 1 else PAIRS[-1]
    a, b = pair
    if LINES[a][0] == "tbl":
        words = LINES[a][1]
        for i, (de, en) in enumerate(TABLE):
            hits = [ws for w, ws in words if w == de]
            on = hits and t >= hits[0]
            y = 700 + i * 190
            p = ease((t - hits[0]) / 0.15) if on else 0
            col = ACID if on else (255, 255, 255, 45)
            dx = -40 * (1 - p) if on else 0
            d.text((140 + dx, y), de, font=F(150), fill=col, stroke_width=8, stroke_fill=(0, 0, 0))
            if on:
                d.text((640, y + 45), "= " + en, font=F(86), fill=WHITE, stroke_width=4, stroke_fill=(0, 0, 0))
    else:
        top = LINES[a]; bot = LINES[b] if b is not None else None
        if top[0] == "en":
            draw_words(d, top[1], t, 760, 150, WHITE)
            if bot: draw_words(d, bot[1], t, 960, 260, ACID)
        else:
            draw_words(d, top[1], t, 860, 260, ACID)
            d.text((W / 2 - text_w("= I AM NICK", 70) / 2, 1180), "= I AM NICK", font=F(70), fill=WHITE,
                   stroke_width=5, stroke_fill=(0, 0, 0))
    return T

def main(audio, out):
    K, dur = kicks(audio)
    bg = background()
    n = int(dur * FPS)
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                           "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
                           "-shortest", out], stdin=subprocess.PIPE)
    for i in range(n):
        t = i / FPS
        pk = pulse(t, K)
        img = bg * (0.8 + 0.4 * pk) + lasers(t, pk) * (0.75 + 0.25 * pk)
        T = frame_text(t, pk)
        ta = np.asarray(T, np.float32)
        glow = np.asarray(T.resize((W // 4, H // 4)).filter(ImageFilter.GaussianBlur(6)).resize((W, H)), np.float32)
        img += glow[..., :3] * (glow[..., 3:] / 255) * (0.6 + 0.6 * pk)
        al = ta[..., 3:] / 255
        img = img * (1 - al) + ta[..., :3] * al
        z = 1 + 0.015 * pk
        fr = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
        if z > 1.001:
            cw, ch = int(W / z), int(H / z)
            fr = fr.crop(((W - cw) // 2, (H - ch) // 2, (W - cw) // 2 + cw, (H - ch) // 2 + ch)).resize((W, H), Image.BILINEAR)
        ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
