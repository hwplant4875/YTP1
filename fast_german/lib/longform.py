"""Slide-based 16:9 renderer for Fast German long-form videos.

A video is a list of slides. Each slide = one still image + an audio sequence:
  ("tts", text, {speed, stability}) | ("sil", seconds) | ("sfx", name)
Slides become PNGs and audio pieces; ffmpeg concatenates them.
"""
import concurrent.futures as cf
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
import common as C
from short import font, ui_font, fit_font, text_img, shadowed

W, H = 1920, 1080
SR = 48000

DARK = {"bg": (20, 27, 45), "ink": (240, 236, 228), "muted": (150, 160, 180),
        "der": (110, 160, 255), "die": (255, 120, 125), "das": (110, 215, 140), None: (240, 236, 228)}
LIGHT = {"bg": C.CREAM, "ink": C.INK, "muted": (110, 104, 98),
         "der": C.GENDER["der"], "die": C.GENDER["die"], "das": C.GENDER["das"], None: C.INK}


def bg_image(theme):
    rng = np.random.default_rng(3)
    base = np.zeros((H, W, 3), np.float32) + np.array(theme["bg"], np.float32)
    yy = np.linspace(0, 1, H)[:, None, None]
    if theme is DARK:
        base = base * (0.85 + 0.25 * yy)
        img = Image.fromarray(np.clip(base + rng.normal(0, 2, (H, W, 1)), 0, 255).astype(np.uint8)).convert("RGBA")
        d = ImageDraw.Draw(img)
        for _ in range(140):
            x, y, r = rng.uniform(0, W), rng.uniform(0, H * 0.75), rng.uniform(0.8, 2.6)
            a = int(rng.uniform(60, 200))
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 250, 230, a))
        return img
    base = base * (1 - 0.04 * yy)
    img = Image.fromarray(np.clip(base + rng.normal(0, 4, (H, W, 1)), 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    for y in range(50, H, 80):
        for x in range(40 if (y // 80) % 2 else 0, W, 80):
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(240, 226, 200, 255))
    return img


def pill(text, fill, ink, size=38, icon=None):
    f = ui_font(size)
    t = text_img(text, f, ink + (255,), pad=0)
    ic = C.icon(icon, int(size * 1.5)) if icon else None
    w = t.width + 60 + (ic.width + 12 if ic else 0)
    h = int(size * 2.1)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=fill + (255,))
    x = 30
    if ic:
        im.alpha_composite(ic, (x - 8, (h - ic.height) // 2))
        x += ic.width + 4
    im.alpha_composite(t, (x, (h - t.height) // 2))
    return im


def wrap(text, f, max_w):
    lines, cur = [], ""
    for w in text.split():
        trial = (cur + " " + w).strip()
        if f.getlength(trial) > max_w and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def draw_lines(canvas, lines, f, fill, cx, y, gap=12):
    for l in lines:
        t = text_img(l, f, fill + (255,), pad=0)
        canvas.alpha_composite(t, (int(cx - t.width / 2), int(y)))
        y += t.height + gap
    return y


def slide(theme, top_left=None, top_right=None, icon=None, word=None, article=None, en=None, sub=None,
          caption=None, label=None, big=None, icon_size=420, sub2=None):
    """Compose one 1920x1080 slide."""
    im = bg_image(theme).copy() if not hasattr(slide, "_bg") or slide._bg[0] is not theme else slide._bg[1].copy()
    slide._bg = (theme, im.copy())
    ink, muted = theme["ink"], theme["muted"]
    if top_left:
        im.alpha_composite(pill(top_left, C.YELLOW, C.INK, icon="pretzel"), (50, 40))
    if top_right:
        p = pill(top_right, (255, 255, 255) if theme is LIGHT else (40, 50, 75), ink, size=32)
        im.alpha_composite(p, (W - p.width - 50, 46))
    if label:
        p = pill(label, theme["die"] if label.startswith("QUIZ") else C.YELLOW, C.INK if not label.startswith("QUIZ") else (255, 255, 255), size=40)
        im.alpha_composite(p, ((W - p.width) // 2, 175))
    has_text = word or en or sub
    if icon:
        ic = shadowed(C.icon(icon, icon_size), 10, 16, 60 if theme is LIGHT else 120)
        cx = 500 if has_text else W // 2
        im.alpha_composite(ic, (int(cx - ic.width / 2), int(560 - ic.height / 2)))
    tx = 1260 if icon and has_text else W // 2
    tw = 1020 if icon and has_text else 1600
    y = 330
    if big:
        f = fit_font(big, 1500, 400)
        t = text_img(big, f, C.YELLOW + (255,), stroke=14, stroke_fill=C.INK + (255,))
        im.alpha_composite(t, ((W - t.width) // 2, (H - t.height) // 2 - 40))
    if word:
        col = theme.get(article, ink)
        f = fit_font(word, tw, 150)
        lines = wrap(word, f, tw) if f.size <= 64 else [word]
        if len(lines) > 1:
            f = font(84, "Bold")
            lines = wrap(word, f, tw)
        if theme is LIGHT:
            for l in lines:
                t = shadowed(text_img(l, f, col + (255,), stroke=8, stroke_fill=(255, 255, 255, 255)), 5, 8, 50)
                im.alpha_composite(t, (int(tx - t.width / 2), int(y)))
                y += t.height - 30
        else:
            y = draw_lines(im, lines, f, col, tx, y + 30)
        y += 30
    if en:
        f = fit_font(en, tw, 76, "Medium")
        y = draw_lines(im, wrap(en, f, tw), f, muted if word else ink, tx, y)
        y += 40
    if sub:
        f = font(54, "Medium")
        y = draw_lines(im, wrap(sub, f, tw), f, ink, tx, y)
    if sub2:
        f = font(46, "Regular")
        y = draw_lines(im, wrap(sub2, f, tw), f, muted, tx, y + 6)
    if caption:
        f = ui_font(46)
        lines = wrap(caption, f, 1600)[:3]
        hh = len(lines) * 62 + 40
        box = Image.new("RGBA", (W, hh), (0, 0, 0, 0))
        ImageDraw.Draw(box).rounded_rectangle((120, 0, W - 120, hh), 30,
                                              fill=(255, 255, 255, 235) if theme is LIGHT else (10, 14, 25, 200))
        im.alpha_composite(box, (0, H - hh - 40))
        draw_lines(im, lines, f, ink, W / 2, H - hh - 40 + 20, gap=8)
    return im.convert("RGB")


def _tts_piece(item):
    _, text, opt = item
    mp3, _ = C.tts(text, **opt)
    return mp3


def build(slides, out_path, fps=10, bed=None, workers=4, crf=24, lufs=-14, music=None, music_vol=0.18):
    """slides: list of (PIL image or callable, [audio items]). bed: optional ffmpeg lavfi audio bed source.
    music: optional list of mp3s played in order and looped, ducked under the voice."""
    tmp = tempfile.mkdtemp(dir=os.environ.get("FG_TMP"))
    # 1. TTS in parallel
    items = {it[1] + repr(sorted(it[2].items())): it for _, aud in slides for it in aud if it[0] == "tts"}
    with cf.ThreadPoolExecutor(workers) as ex:
        paths = dict(zip(items, ex.map(_tts_piece, items.values())))
    # 2. Decode each unique clip to raw PCM once
    pcm = {}

    def load(path):
        if path not in pcm:
            raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "s16le", "-ac", "1",
                                           "-ar", str(SR), "-"])
            pcm[path] = np.frombuffer(raw, np.int16)
        return pcm[path]

    audio_path = os.path.join(tmp, "voice.raw")
    concat = os.path.join(tmp, "list.txt")
    total = 0.0
    with open(audio_path, "wb") as af, open(concat, "w") as lf:
        for i, (img, aud) in enumerate(slides):
            chunks = []
            for it in aud:
                if it[0] == "tts":
                    chunks.append(load(paths[it[1] + repr(sorted(it[2].items()))]))
                elif it[0] == "sil":
                    chunks.append(np.zeros(int(it[1] * SR), np.int16))
                elif it[0] == "sfx":
                    chunks.append((load(C.get_sfx(it[1])) * 0.35).astype(np.int16))
            seg = np.concatenate(chunks) if chunks else np.zeros(SR, np.int16)
            # keep slide length a whole number of frames so audio and video stay in sync
            n = int(round(len(seg) / SR * fps))
            n = max(n, 1)
            want = int(n * SR / fps)
            seg = np.pad(seg, (0, max(0, want - len(seg))))[:want]
            af.write(seg.tobytes())
            p = os.path.join(tmp, f"s{i:05d}.png")
            (img() if callable(img) else img).save(p)
            lf.write(f"file '{p}'\nduration {n / fps:.6f}\n")
            total += n / fps
        lf.write(f"file '{p}'\n")
    # 3. Mix voice with optional bed, normalize
    wav = os.path.join(tmp, "mix.m4a")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", audio_path]
    f = ["[0:a]aformat=channel_layouts=stereo,asplit=2[v][key]"]
    mix = ["[v]"]
    if bed:
        cmd += ["-f", "lavfi", "-t", f"{total:.3f}", "-i", bed]
        f.append(f"[{len(mix)}:a]aformat=channel_layouts=stereo[b]")
        mix.append("[b]")
    if music:
        pl = os.path.join(tmp, "music.txt")
        open(pl, "w").write("".join("file '%s'\n" % m.replace("'", "'\\''") for m in music))
        cmd += ["-stream_loop", "-1", "-f", "concat", "-safe", "0", "-i", pl]
        f.append(f"[{len(mix)}:a]aformat=channel_layouts=stereo:sample_rates={SR},atrim=0:{total:.3f},"
                 f"afade=t=in:d=2,afade=t=out:st={max(0, total - 4):.3f}:d=4,volume={music_vol}[m0]")
        f.append("[m0][key]sidechaincompress=threshold=0.03:ratio=5:attack=30:release=500[m]")
        mix.append("[m]")
    else:
        f.append("[key]anullsink")
    f.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,loudnorm=I={lufs}:TP=-1.5:LRA=11[a]")
    cmd += ["-filter_complex", ";".join(f), "-map", "[a]", "-c:a", "aac", "-b:a", "160k", wav]
    subprocess.run(cmd, check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", concat, "-i", wav,
                    "-vf", f"fps={fps},format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage",
                    "-crf", str(crf), "-c:a", "copy", "-shortest", "-movflags", "+faststart", out_path], check=True)
    return total
