"""German Rave short 01 v2: sein chant + full sein table. Reuses the club look of short01_ich_bin.

python3 specs/rave/short01b_sein.py AUDIO.wav WORDS.json CUT_AT CUT_LEN OUT.mp4
WORDS.json: whisper words [[start, end, word], ...] on the uncut track; words after CUT_AT shift by -CUT_LEN.
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
from short01_ich_bin import ACID, UV, WHITE, F, W, H, FPS, background, ease, kicks, lasers, pulse, text_w

ROWS = [("ich bin", "I am"), ("du bist", "you are"), ("er ist", "he is"), ("sie ist", "she is"), ("es ist", "it is"),
        ("wir sind", "we are"), ("ihr seid", "you all are"), ("sie sind", "they are"), ("Sie sind", "you are (formal)")]
EN = {"ich bin": "I AM", "du bist": "YOU ARE", "er ist": "HE IS", "sie ist": "SHE IS", "es ist": "IT IS",
      "wir sind": "WE ARE", "ihr seid": "YOU ALL ARE", "sie sind": "THEY ARE"}
PRON = {"ich", "du", "er", "sie", "es", "wir", "ihr"}


def phrases(words, cut_at, cut_len):
    out, i = [], 0
    # whisper word starts drift early on long shouted words: onset = max(pronoun start, verb end - 0.62)
    clean = [(s, e, w.lower().strip(",.!?").replace("bin's", "bin")) for s, e, w in words]
    while i < len(clean) - 1:
        t, _, w = clean[i]
        if w in PRON:
            t = max(t, clean[i + 1][1] - 0.62)
            out.append((t - (cut_len if t >= cut_at else 0), w + " " + clean[i + 1][2])); i += 2
        else:
            i += 1
    return out


def row_of(ph):
    for k, (de, _) in enumerate(ROWS[:8]):
        if de == ph: return k
    return None


def frame_text(t, P):
    T = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(T)
    d.text((W / 2 - text_w("GERMAN RAVE", 132) / 2, 190), "GERMAN RAVE", font=F(132), fill=ACID,
           stroke_width=9, stroke_fill=(0, 0, 0))
    sub = "LESSON 1: SEIN"
    d.text((W / 2 - text_w(sub, 92) / 2, 350), sub, font=F(92), fill=WHITE, stroke_width=7, stroke_fill=(0, 0, 0))
    cur = [p for p in P if p[0] <= t + 0.02]
    ph_t, ph = cur[-1] if cur else P[0]
    # big current phrase: already visible at its onset, punches from 1.12x to 1.0x
    p = ease((t - ph_t) / 0.14) if cur else 1.0
    big = ph.upper() + "!"
    size = min(235, int(235 * 900 / text_w(big, 235)))
    sz = int(size * (1.12 - 0.12 * p))
    d.text((W / 2 - text_w(big, sz) / 2, 590 - (sz - size) / 2), big, font=F(sz), fill=ACID, stroke_width=10,
           stroke_fill=(0, 0, 0))
    en = "= " + EN[ph]
    d.text((W / 2 - text_w(en, 84) / 2, 935), en, font=F(84), fill=WHITE, stroke_width=6, stroke_fill=(0, 0, 0))
    # sein table: rows light up the first time they are sung, current row in white
    seen = {row_of(x[1]) for x in cur}
    cr = row_of(ph)
    d.rounded_rectangle([60, 1075, 1020, 1555], 26, fill=(0, 0, 0, 150))
    for k, (de, en_) in enumerate(ROWS):
        col, rr = (0, k) if k < 5 else (1, k - 5)
        x, y = 100 + col * 470, 1095 + rr * 90
        lit = k in seen or (k == 8 and 7 in seen)
        if k == cr:
            fill = WHITE
        elif lit:
            fill = ACID
        else:
            fill = (255, 255, 255, 70)
        d.text((x, y), de, font=F(70), fill=fill, stroke_width=4, stroke_fill=(0, 0, 0))
        if lit:
            d.text((x + text_w(de, 70) + 18, y + 26), en_, font=F(40), fill=(225, 225, 225), stroke_width=3,
                   stroke_fill=(0, 0, 0))
    return T


def main(audio, words_json, cut_at, cut_len, out):
    P = phrases(json.load(open(words_json)), float(cut_at), float(cut_len))
    K, dur = kicks(audio)
    bg = background()
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                           "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
                           "-shortest", out], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        t = i / FPS
        pk = pulse(t, K)
        img = bg * (0.8 + 0.4 * pk) + lasers(t, pk) * (0.75 + 0.25 * pk)
        T = frame_text(t, P)
        ta = np.asarray(T, np.float32)
        glow = np.asarray(T.resize((W // 4, H // 4)).filter(ImageFilter.GaussianBlur(6)).resize((W, H)), np.float32)
        img += glow[..., :3] * (glow[..., 3:] / 255) * (0.5 + 0.5 * pk)
        al = ta[..., 3:] / 255
        img = img * (1 - al) + ta[..., :3] * al
        fr = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
        z = 1 + 0.015 * pk
        if z > 1.001:
            cw, ch = int(W / z), int(H / z)
            fr = fr.crop(((W - cw) // 2, (H - ch) // 2, (W - cw) // 2 + cw, (H - ch) // 2 + ch)).resize((W, H), Image.BILINEAR)
        ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait()


if __name__ == "__main__":
    main(*sys.argv[1:6])
