"""German Rave 01 final: "Ich bin! / I am!" call and response, one pair at a time.

python3 specs/rave/short01c_sein.py AUDIO.wav EVENTS.json OUT.mp4
EVENTS.json: [[t, "de"|"en", pair_index], ...] on the final (edited) track.
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
from short01_ich_bin import ACID, WHITE, F, W, H, FPS, background, kicks, lasers, pulse, text_w

PAIRS = [("ICH BIN!", "I AM!"), ("DU BIST!", "YOU ARE!"), ("ER IST!", "HE IS!"), ("SIE IST!", "SHE IS!"),
         ("ES IST!", "IT IS!"), ("WIR SIND!", "WE ARE!"), ("IHR SEID!", "YOU ALL ARE!"), ("SIE SIND!", "THEY ARE!")]
LIST = ["ich bin", "du bist", "er ist", "sie ist", "es ist", "wir sind", "ihr seid", "sie sind"]


def pop(dt):
    """Scale for a pop-in: 0.55 -> 1.1 -> 1.0 over ~0.22 s."""
    if dt < 0: return 0.0
    if dt < 0.12: return 0.55 + 0.55 * (dt / 0.12)
    if dt < 0.22: return 1.1 - 0.1 * ((dt - 0.12) / 0.1)
    return 1.0


def centered(d, s, size, y, fill, sc, stroke=9, maxw=920):
    size = min(size, int(size * maxw / text_w(s, size)))
    sz = max(8, int(size * sc))
    d.text((W / 2 - text_w(s, sz) / 2, y + (size - sz) / 2), s, font=F(sz), fill=fill, stroke_width=stroke,
           stroke_fill=(0, 0, 0))


def frame_text(t, E):
    T = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(T)
    d.text((W / 2 - text_w("GERMAN RAVE", 132) / 2, 190), "GERMAN RAVE", font=F(132), fill=ACID,
           stroke_width=9, stroke_fill=(0, 0, 0))
    sub = "LESSON 1: SEIN"
    d.text((W / 2 - text_w(sub, 92) / 2, 350), sub, font=F(92), fill=WHITE, stroke_width=7, stroke_fill=(0, 0, 0))
    past = [e for e in E if e[0] <= t]
    de = [e for e in past if e[1] == "de"]
    cur = de[-1] if de else E[0]
    k = cur[2]
    # frame 0 is the cover: first pair already at full size
    sc = 1.0 if t < 0.05 else pop(t - cur[0])
    centered(d, PAIRS[k][0], 250, 600, ACID, sc)
    en = [e for e in past if e[1] == "en" and e[2] == k and e[0] >= cur[0]]
    if en:
        centered(d, PAIRS[k][1], 130, 900, WHITE, pop(t - en[-1][0]), stroke=8)
    # list of the forms sung so far, newest pops in
    sung = []
    for e in de:
        if e[2] not in [s[0] for s in sung]: sung.append((e[2], e[0]))
    for j, (idx, t0) in enumerate(sung):
        col, row = (0, j) if j < 4 else (1, j - 4)
        x, y = 150 + col * 430, 1130 + row * 92
        s = LIST[idx]
        sz = 72 if t < 0.05 else max(8, int(72 * pop(t - t0)))
        fill = WHITE if idx == k else ACID
        d.text((x, y + (72 - sz) / 2), s, font=F(sz), fill=fill, stroke_width=5, stroke_fill=(0, 0, 0))
    return T


def main(audio, events, out):
    E = sorted(json.load(open(events)))
    K, dur = kicks(audio)
    bg = background()
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                           "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
                           "-shortest", out], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        t = i / FPS
        pk = pulse(t, K)
        # softer beat flash than v1/v2 (user 2026-10-19)
        img = bg * (0.85 + 0.2 * pk) + lasers(t, pk) * (0.8 + 0.12 * pk)
        T = frame_text(t, E)
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
