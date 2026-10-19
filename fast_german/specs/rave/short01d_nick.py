"""German Rave 01 "Ich bin Nick": word-synced lyrics on the original Ich-bin-Nick song.

python3 specs/rave/short01d_nick.py AUDIO.wav LINES.json OUT.mp4
LINES.json: [{"words": [[WORD, t], ...], "en": "MY NAME IS NICK", "form": 0|null}, ...] on the edited track.
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
from short01_ich_bin import ACID, WHITE, F, W, H, FPS, background, kicks, lasers, pulse, text_w
from short01c_sein import pop

LIST = ["ich bin", "du bist", "er ist", "sie ist"]


def words_line(d, words, t, y, size, fill, first, maxw=940):
    full = " ".join(w for w, _ in words)
    size = min(size, int(size * maxw / text_w(full, size)))
    gap = F(size).getlength(" ") * 0.6
    x = W / 2 - (sum(F(size).getlength(w) for w, _ in words) + gap * (len(words) - 1)) / 2
    for w, ws in words:
        # frame 0 is the cover: the first line is already complete
        sc = 1.0 if first and t < 0.05 else pop(t - ws)
        if sc > 0:
            sz = max(8, int(size * sc)); ww = F(size).getlength(w)
            d.text((x + ww / 2 - text_w(w, sz) / 2, y + (size - sz) / 2), w, font=F(sz), fill=fill,
                   stroke_width=9, stroke_fill=(0, 0, 0))
        x += F(size).getlength(w) + gap


def frame_text(t, L):
    T = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(T)
    d.text((W / 2 - text_w("GERMAN RAVE", 132) / 2, 190), "GERMAN RAVE", font=F(132), fill=ACID,
           stroke_width=9, stroke_fill=(0, 0, 0))
    sub = "LESSON 1: SEIN"
    d.text((W / 2 - text_w(sub, 92) / 2, 350), sub, font=F(92), fill=WHITE, stroke_width=7, stroke_fill=(0, 0, 0))
    started = [i for i, l in enumerate(L) if l["words"][0][1] <= t]
    i = started[-1] if started else 0
    line = L[i]
    ws = line["words"]
    if len(ws) > 3:  # long line: two rows so the words stay big
        words_line(d, ws[:2], t, 540, 210, ACID, i == 0)
        words_line(d, ws[2:], t, 760, 210, ACID, i == 0)
    else:
        words_line(d, ws, t, 600, 230, ACID, i == 0)
    t_en = ws[-1][1]
    if i == 0 and t < 0.05: t_en = -1
    if t >= t_en:
        en = "= " + line["en"]
        sz = min(110, int(110 * 900 / text_w(en, 110)))
        sc = 1.0 if t_en < 0 else pop(t - t_en)
        s2 = max(8, int(sz * sc))
        d.text((W / 2 - text_w(en, s2) / 2, (1000 if len(ws) > 3 else 900) + (sz - s2) / 2), en, font=F(s2), fill=WHITE, stroke_width=8,
               stroke_fill=(0, 0, 0))
    # sein forms sung so far
    seen = []
    for l in L[:i + 1]:
        if l.get("form") is not None and l["form"] not in [s[0] for s in seen]:
            seen.append((l["form"], l["words"][0][1]))
    for j, (f, t0) in enumerate(seen):
        x, y = 150 + (j % 2) * 430, 1180 + (j // 2) * 92
        sz = max(8, int(72 * pop(t - t0)))
        fill = WHITE if f == line.get("form") else ACID
        d.text((x, y + (72 - sz) / 2), LIST[f], font=F(sz), fill=fill, stroke_width=5, stroke_fill=(0, 0, 0))
    return T


def main(audio, lines, out):
    L = json.load(open(lines))
    K, dur = kicks(audio)
    bg = background()
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                           "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
                           "-shortest", out], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        t = i / FPS
        pk = pulse(t, K)
        img = bg * (0.85 + 0.2 * pk) + lasers(t, pk) * (0.8 + 0.12 * pk)
        T = frame_text(t, L)
        ta = np.asarray(T, np.float32)
        glow = np.asarray(T.resize((W // 4, H // 4)).filter(ImageFilter.GaussianBlur(6)).resize((W, H)), np.float32)
        img += glow[..., :3] * (glow[..., 3:] / 255) * (0.5 + 0.25 * pk)
        al = ta[..., 3:] / 255
        img = img * (1 - al) + ta[..., :3] * al
        fr = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
        z = 1 + 0.008 * pk
        if z > 1.001:
            cw, ch = int(W / z), int(H / z)
            fr = fr.crop(((W - cw) // 2, (H - ch) // 2, (W - cw) // 2 + cw, (H - ch) // 2 + ch)).resize((W, H), Image.BILINEAR)
        ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait()


if __name__ == "__main__":
    main(*sys.argv[1:4])
