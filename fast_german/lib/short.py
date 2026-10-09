"""Render a Fast German short (1080x1920) from a beat spec.

Spec: {"id", "beats": [{"say", "top"?, "icons"?: [..], "ops"?: [..], "word"?: {"de","article"}, "words"?: [..],
       "en"?, "mark"?: "right"|"wrong", "count"?: n, "punch"?: bool, "sfx"?: name, "pause"?: seconds}]}
"""
import json
import math
import re
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import common as C

W, H, FPS = 1080, 1920, 30
GAP = 0.45  # between beats
SENT_GAP = 0.3  # between sentences inside a beat
SFX_VOL = {"pop": 0.8, "ding": 0.7, "start": 0.7, "buzz": 0.6, "snap": 0.8, "whoosh": 0.6, "tick": 0.7, "swoosh_up": 0.7}
MUSIC = os.path.join(C.CACHE, "music", "kpop_bed.mp3")
MUSIC_VOL = 0.22


UI_FONT = os.path.join(C.ROOT, "assets", "fonts", "YouTubeSans-Black.otf")
if not os.path.exists(UI_FONT):  # proprietary file, not in git; shared copy lives in the project folder
    UI_FONT = "/mnt/project-files/fonts/YouTubeSans-Black.otf"


def ui_font(size):
    """YouTube Sans: default English UI font (titles, subtitles, labels)."""
    return ImageFont.truetype(UI_FONT, size)


def font(size, weight="Bold"):
    """Fredoka: the rounded font for the big German words and meanings."""
    f = ImageFont.truetype(C.FONT, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def fit_font(text, max_w, start, weight="Bold", min_size=60):
    s = start
    while s > min_size:
        f = font(s, weight)
        if f.getlength(text) <= max_w:
            return f
        s -= 6
    return font(min_size, weight)


def ease_pop(t):
    """0..1 -> scale, back-out easing with a small overshoot."""
    if t <= 0:
        return 0.0
    if t >= 1:
        return 1.0
    c1 = 1.9
    u = t - 1
    return 1 + (c1 + 1) * u ** 3 + c1 * u ** 2


def paste_center(canvas, im, cx, cy, scale=1.0):
    if scale <= 0.01:
        return
    if abs(scale - 1) > 0.01:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def text_img(text, f, fill, stroke=0, stroke_fill=None, pad=20):
    l, t, r, b = f.getbbox(text, stroke_width=stroke)
    im = Image.new("RGBA", (r - l + pad * 2, b - t + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - l, pad - t), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im


def shadowed(im, offset=10, blur=14, alpha=70):
    a = im.split()[3].point(lambda v: v * alpha // 255)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(a)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new("RGBA", (im.width + offset * 2 + blur * 2, im.height + offset * 2 + blur * 2), (0, 0, 0, 0))
    out.alpha_composite(sh, (blur + offset, blur + offset * 2))
    out.alpha_composite(im, (blur, blur))
    return out


def word_img(de, article, max_w=980, size=190):
    """'der Handschuh' with the article and word in the gender color, on one line."""
    col = C.GENDER.get(article)
    txt = f"{article} {de}" if article else de
    lines = txt.split("|")
    f = min((fit_font(l, max_w, size) for l in lines), key=lambda x: x.size)
    ims = [text_img(l, f, col + (255,), stroke=10, stroke_fill=(255, 255, 255, 255)) for l in lines]
    im = Image.new("RGBA", (max(i.width for i in ims), sum(i.height - 30 for i in ims) + 30), (0, 0, 0, 0))
    y = 0
    for i in ims:
        im.alpha_composite(i, ((im.width - i.width) // 2, y))
        y += i.height - 30
    return shadowed(im, 6, 8, 60)


def background():
    rng = np.random.default_rng(7)
    base = np.zeros((H, W, 3), np.float32) + np.array(C.CREAM, np.float32)
    yy = np.linspace(0, 1, H)[:, None, None]
    base = base * (1 - 0.05 * yy)  # gentle vertical shade
    noise = rng.normal(0, 4, (H, W, 1))
    bg = Image.fromarray(np.clip(base + noise, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(bg)
    # soft dotted pattern
    for y in range(60, H, 90):
        for x in range(45 if (y // 90) % 2 else 0, W, 90):
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(240, 226, 200, 255))
    return bg


def brand_pill():
    f = ui_font(40)
    t = text_img("FAST GERMAN", f, C.INK + (255,), pad=0)
    ic = C.icon("pretzel", 64)
    im = Image.new("RGBA", (t.width + ic.width + 70, 90), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, 89), 45, fill=C.YELLOW + (255,))
    im.alpha_composite(ic, (22, 13))
    im.alpha_composite(t, (22 + ic.width + 14, (90 - t.height) // 2))
    return im


def top_text(text):
    f = ui_font(76)
    lines, cur = [], ""
    for w in text.split():
        trial = (cur + " " + w).strip()
        if f.getlength(trial) > 900 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    lines.append(cur)
    imgs = [text_img(l, f, C.INK + (255,), pad=8) for l in lines]
    w = max(i.width for i in imgs) + 60
    h = sum(i.height for i in imgs) + 50
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=(255, 255, 255, 255))
    y = 25
    for i in imgs:
        im.alpha_composite(i, ((w - i.width) // 2, y))
        y += i.height
    return shadowed(im, 6, 12, 45)


def op_img(op):
    col = {"+": C.INK, "=": C.INK, "vs": C.GENDER["die"], "≠": C.GENDER["die"], "→": C.INK}.get(op, C.INK)
    return text_img(op, font(150 if op != "vs" else 110, "Bold"), col + (255,))


def mark_img(kind):
    col = (34, 170, 90) if kind == "right" else (229, 72, 77)
    im = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((10, 10, 290, 290), fill=col + (255,), outline=(255, 255, 255, 255), width=14)
    if kind == "right":
        d.line([(80, 155), (130, 210), (225, 95)], fill=(255, 255, 255, 255), width=34, joint="curve")
    else:
        d.line([(95, 95), (205, 205)], fill=(255, 255, 255, 255), width=34)
        d.line([(205, 95), (95, 205)], fill=(255, 255, 255, 255), width=34)
    return shadowed(im, 6, 10, 60)


def build_layers(beat):
    """Returns list of (key, image, cx, cy, delay)."""
    L = []
    if beat.get("top"):
        L.append(("top:" + beat["top"], top_text(beat["top"]), W / 2, 340, 0.0))
    icons = beat.get("icons") or []
    ops = beat.get("ops") or []
    words = beat.get("words") or []
    n = len(icons)
    icy = 860
    if n:
        size = {1: 600, 2: 380, 3: 270}[n]
        opw = 130 if ops else 40
        total = n * size + (n - 1) * opw
        x = W / 2 - total / 2 + size / 2
        for i, name in enumerate(icons):
            L.append((f"icon{i}:{name}", shadowed(C.icon(name, size), 10, 16, 55), x, icy, 0.08 * i))
            if i < len(words):
                w = words[i]
                L.append((f"w{i}:{w['de']}", word_img(w["de"], w.get("article"), max_w=size + 60, size=110),
                          x, icy + size / 2 + 80, 0.1 + 0.08 * i))
            if i < n - 1 and i < len(ops):
                L.append((f"op{i}:{ops[i]}", op_img(ops[i]), x + size / 2 + opw / 2, icy, 0.06 + 0.08 * i))
            x += size + opw
    if beat.get("count") is not None:
        L.append((f"count:{beat['count']}", text_img(str(beat["count"]), font(420, "Bold"), C.YELLOW + (255,),
                                                     stroke=16, stroke_fill=C.INK + (255,)), W / 2, icy, 0))
    if beat.get("mark"):
        L.append(("mark:" + beat["mark"], mark_img(beat["mark"]), W / 2 + 230, icy - 220, 0.15))
    wy = 1320
    if beat.get("word"):
        w = beat["word"]
        wimg = word_img(w["de"], w.get("article"))
        wcy = wy + 60 * w["de"].count("|")
        L.append(("word:" + w["de"] + str(w.get("article")), wimg, W / 2, wcy, 0.12))
        en_y = wcy + wimg.height / 2 + 20
    if beat.get("en"):
        L.append(("en:" + beat["en"], text_img(beat["en"], fit_font(beat["en"], 940, 72, "Medium"), (95, 90, 85, 255)),
                  W / 2, en_y if beat.get("word") else wy + 135, 0.2))
    return L


def sub_chunks(words, max_words=3):
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= max_words or w[0].endswith((".", "!", "?", ",", "...")):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def render(spec_path, out_path):
    spec = json.load(open(spec_path))
    beats = spec["beats"]
    # 1. audio: each sentence is its own clip so the voice ends naturally and pauses between sentences.
    #    "A || B" in a beat's say = one clip with a 2 s break; the beat's "reveal" visuals switch in at B.
    speed = spec.get("speed", 1.0)  # same settings as the approved Carola sample
    t = 0.35
    timeline, clips = [], []
    for b in beats:
        start = t
        words = []
        reveal_at = None
        if "||" in b["say"]:
            pa, pb = [x.strip() for x in b["say"].split("||")]
            mp3, al = C.tts(f'{pa} <break time="{b.get("gap", 2.0)}s" /> {pb}', speed=speed)
            ws = [w for w in C.words_from_alignment(al) if not (w[0].startswith("<") or "time=" in w[0] or w[0] == "/>")]
            n_a = len(pa.split())
            reveal_at = t + ws[n_a][1] - 0.05 if len(ws) > n_a else None
            words += [(w, s0 + t, e0 + t) for w, s0, e0 in ws]
            clips.append((mp3, t))
            t += C.duration(mp3)
        else:
            for sent in [x for x in re.split(r"(?<=[.!?])\s+", b["say"].strip()) if x]:
                mp3, al = C.tts(sent, speed=speed)
                words += [(w, s0 + t, e0 + t) for w, s0, e0 in C.words_from_alignment(al)]
                clips.append((mp3, t))
                t += C.duration(mp3) + SENT_GAP
            t -= SENT_GAP
        t += b.get("pause", 0)
        if reveal_at:
            first = {k: v for k, v in b.items() if k not in ("reveal",)}
            timeline.append({"beat": first, "start": start, "end": reveal_at, "words": words})
            second = dict(first)
            second.update(b["reveal"])
            second["sfx"] = b["reveal"].get("sfx")
            timeline.append({"beat": second, "start": reveal_at, "end": t, "words": []})
        else:
            timeline.append({"beat": b, "start": start, "end": t, "words": words})
        t += GAP
    total = t + 0.5
    # 2. audio mix: voice clips, sound effects (trimmed, faded), music bed ducked under the voice
    tmp = tempfile.mkdtemp()
    inputs, filters = [], []
    for i, (mp3, st) in enumerate(clips):
        inputs += ["-i", mp3]
        filters.append(f"[{i}:a]aformat=channel_layouts=stereo,adelay={int(st * 1000)}:all=1[c{i}]")
    nv = len(clips)
    filters.append("".join(f"[c{i}]" for i in range(nv)) + f"amix=inputs={nv}:normalize=0,apad=whole_dur={total},"
                   f"atrim=0:{total},loudnorm=I=-15:TP=-2:LRA=11,asplit=2[voice][key]")
    k = nv
    fx = []
    for tl in timeline:
        s = tl["beat"].get("sfx")
        if s:
            inputs += ["-i", C.get_sfx(s)]
            vol = SFX_VOL.get(s, 0.8)
            filters.append(f"[{k}:a]aformat=channel_layouts=stereo,atrim=0:1.1,afade=t=out:st=0.8:d=0.3,"
                           f"volume={vol},adelay={int(max(0, tl['start'] - 0.08) * 1000)}:all=1[f{k}]")
            fx.append(f"[f{k}]")
            k += 1
    music = spec.get("music", MUSIC)
    if music and os.path.exists(music):
        inputs += ["-stream_loop", "-1", "-i", music]
        filters.append(f"[{k}:a]aformat=channel_layouts=stereo,atrim=0:{total},afade=t=in:d=0.6,"
                       f"afade=t=out:st={max(0, total - 1.2)}:d=1.2,volume={MUSIC_VOL}[m0]")
        filters.append("[m0][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[music]")
        fx.append("[music]")
        k += 1
    else:
        filters.append("[key]anullsink")
    filters.append("[voice]" + "".join(fx) + f"amix=inputs={1 + len(fx)}:normalize=0,alimiter=limit=0.89,apad[a]")
    wav = os.path.join(tmp, "a.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filters),
                    "-map", "[a]", "-ar", "48000", "-t", f"{total:.3f}", wav], check=True)
    # 3. frames
    bg = background()
    pill = brand_pill()
    layer_cache = [build_layers(tl["beat"]) for tl in timeline]
    sub_font = ui_font(74)
    all_chunks = []
    for tl in timeline:
        for ch in sub_chunks(tl["words"]):
            all_chunks.append(ch)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "warning", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                           out_path], stdin=subprocess.PIPE)
    nframes = int(total * FPS)
    for fi in range(nframes):
        now = fi / FPS
        bi = max([i for i, tl in enumerate(timeline) if tl["start"] - 0.05 <= now] or [0])
        tl = timeline[bi]
        prev_keys = {l[0] for l in layer_cache[bi - 1]} if bi > 0 else set()
        frame = bg.copy()
        local = now - tl["start"]
        for key, im, cx, cy, delay in layer_cache[bi]:
            if key in prev_keys:
                sc = 1.0
            else:
                sc = ease_pop((local - delay) / 0.28)
            # gentle float on icons
            if key.startswith("icon"):
                cy = cy + 8 * math.sin(now * 2.2 + hash(key) % 7)
            paste_center(frame, im, cx, cy, sc)
        frame.alpha_composite(pill, ((W - pill.width) // 2, 70))
        # progress bar
        ImageDraw.Draw(frame).rectangle((0, 0, int(W * now / total), 14), fill=C.YELLOW + (255,))
        # karaoke subtitle
        for ch in all_chunks:
            if ch[0][1] - 0.05 <= now <= ch[-1][2] + 0.25:
                draw_sub(frame, ch, now, sub_font)
                break
        # camera: slow push, punch zoom + flash + shake on punch beats
        zoom = 1.0 + 0.025 * min(1, local / max(0.5, tl["end"] - tl["start"]))
        dx = dy = 0
        if tl["beat"].get("punch") and local < 0.35:
            p = 1 - local / 0.35
            zoom += 0.10 * p
            dx = int(14 * p * math.sin(local * 90))
            dy = int(10 * p * math.cos(local * 77))
        rgb = frame.convert("RGB")
        if zoom > 1.001 or dx or dy:
            zw, zh = W / zoom, H / zoom
            x0, y0 = (W - zw) / 2 + dx, (H - zh) / 2 + dy
            rgb = rgb.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + zw, y0 + zh))
        if tl["beat"].get("punch") and local < 0.12:
            rgb = Image.blend(rgb, Image.new("RGB", (W, H), (255, 255, 255)), 0.55 * (1 - local / 0.12))
        ff.stdin.write(rgb.tobytes())
    ff.stdin.close()
    ff.wait()
    return total


def draw_sub(frame, chunk, now, f):
    parts = []
    for w, s, e in chunk:
        active = s - 0.03 <= now <= e + 0.05
        parts.append((w, active))
    space = f.getlength(" ")
    widths = [f.getlength(w) for w, _ in parts]
    total = sum(widths) + space * (len(parts) - 1)
    scale = min(1.0, 960 / total)
    ff = f if scale >= 1 else ui_font(int(f.size * scale))
    widths = [ff.getlength(w) for w, _ in parts]
    total = sum(widths) + ff.getlength(" ") * (len(parts) - 1)
    x = (W - total) / 2
    y = 1640
    d = ImageDraw.Draw(frame)
    for (w, active), ww in zip(parts, widths):
        if active:
            d.rounded_rectangle((x - 12, y - 6, x + ww + 12, y + ff.size + 18), 18, fill=C.YELLOW + (255,))
        d.text((x, y), w, font=ff, fill=C.INK + (255,), stroke_width=0)
        x += ww + ff.getlength(" ")


if __name__ == "__main__":
    print(render(sys.argv[1], sys.argv[2]))
