"""News-card layout for the STRATA France-protest Shorts (1080x1920), loaded by assemble.py via the visual's "module".

One g2d visual per narration line. Layout (user safe-area rules for Shorts):
  - top badge, centred under the Dynamic Island (y ~212), nothing ever covers it;
  - the picture window, full width, y 290..1000 (real photo / news clip / CC footage / cached 3D render);
  - a big caption directly under the picture (top y 1036), centred at x 490 and never wider than 800 px, so it stays
    inside x 80..900 and above y 1500 (clear of the right-hand buttons and the bottom title area);
  - behind everything, a dark blurred copy of the picture (no black bars).
Pictures change at word cues inside the line ("at": a word of the narration, or seconds), so the visual changes every
2-3 s while each sentence stays one TTS take. Cuts are hard with a short settle, the very first frame is fully drawn.

args:
  items: [{"photo": path, "kb": [z0, cx0, cy0, z1, cx1, cy1]} | {"video": path, "start": s, "speed": 1, "fx": .5, "fy": .5,
           "grade": true} | {"full": path} (full-frame clip, e.g. the end card, no badge/caption),
          "at": word | seconds (first item: 0), "cap": caption text ("\\n" breaks, *accent*), "col": accent colour name,
          "size": caption px, "count": [from, to, secs] (caption "{n}" counts up), "arrow": [x0, y0, x1, y1, at_s]
          in window pixels}]
  badge: badge text (omit for none)
"""
import math
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import graphics2d as g

W, H, FPS = 1080, 1920, 30
WX0, WY0, WX1, WY1 = 0, 290, 1080, 1000
WW, WH = WX1 - WX0, WY1 - WY0
CAP_TOP, CAP_CX, CAP_W, CAP_BOTTOM = 1036, 490, 800, 1480
BADGE_Y = 212
COLS = {"white": (246, 244, 238), "blue": (110, 170, 255), "red": (240, 72, 60), "cyan": (120, 220, 245),
        "green": (95, 220, 125), "amber": (255, 178, 92), "yellow": (255, 222, 90)}
RED = (230, 42, 42)
FONT = "YouTubeSans-DarkBlack.otf"
GRADE_VF = "eq=contrast=1.06:saturation=1.12:brightness=-0.01,colorbalance=rs=0.035:bs=-0.045:rm=0.025:bm=-0.03"


def grade_img(im):
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = ImageEnhance.Color(im).enhance(1.12)
    r, gg, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.03 + 2)))
    b = b.point(lambda v: int(v * 0.955))
    return Image.merge("RGB", (r, gg, b))


class PhotoSrc:
    def __init__(self, path, kb, d):
        src = Image.open(path)
        src.draft("RGB", (WW * 3, WH * 3))
        src = grade_img(src.convert("RGB"))
        s = max(WW * 2 / src.width, WH * 2 / src.height)
        self.big = src.resize((max(1, int(src.width * s)), max(1, int(src.height * s))), Image.LANCZOS)
        self.kb = kb or [1.04, 0.5, 0.5, 1.14, 0.5, 0.5]
        self.d = max(d, 0.1)

    def frame(self, t):
        z0, x0, y0, z1, x1, y1 = self.kb
        u = g.smooth(t / self.d)
        z, cx, cy = z0 + (z1 - z0) * u, x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
        big = self.big
        cw, ch = big.width / z, big.width / z * WH / WW
        if ch > big.height / z:
            ch = big.height / z
            cw = ch * WW / WH
        left = min(max(cx * big.width - cw / 2, 0), big.width - cw)
        top = min(max(cy * big.height - ch / 2, 0), big.height - ch)
        return big.transform((WW, WH), Image.EXTENT, (left, top, left + cw, top + ch), Image.BICUBIC)


class VideoSrc:
    def __init__(self, path, start, speed, d, size, fx=0.5, fy=0.5, grade=True):
        w, h = size
        vf = (f"setpts=(PTS-STARTPTS)/{speed},fps={FPS},scale={w}:{h}:force_original_aspect_ratio=increase,"
              f"crop={w}:{h}:(iw-{w})*{fx}:(ih-{h})*{fy},setsar=1" + ("," + GRADE_VF if grade else ""))
        n = max(1, round(d * FPS)) + 2
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", path, "-t", f"{d * speed + 0.3:.3f}", "-an",
                              "-vf", vf, "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True).stdout
        fr = len(raw) // (w * h * 3)
        if fr == 0:
            raise SystemExit(f"no frames from {path} @ {start}")
        self.frames = np.frombuffer(raw[:fr * w * h * 3], np.uint8).reshape(fr, h, w, 3)

    def frame(self, t):
        return Image.fromarray(self.frames[min(int(t * FPS + 1e-6), len(self.frames) - 1)])


LAST_SIZE = [0]


def caption_layer(text, col, size):
    """Caption as an RGBA image: white with *accent* words, thick black outer stroke; auto-shrinks to CAP_W."""
    acc = COLS.get(col, COLS["blue"])
    lines = text.split("\n")

    def segs(line):
        out, on = [], False
        for i, part in enumerate(line.split("*")):
            if part:
                out.append((part, on))
            on = not on
        return out

    while True:
        f = g.font(size, FONT)
        stroke = max(5, int(size * 0.085))
        widths = [sum(f.getlength(p) for p, _ in segs(ln)) + 2 * stroke for ln in lines]
        lh = int(size * 1.06)
        if max(widths) <= CAP_W and lh * len(lines) <= CAP_BOTTOM - CAP_TOP or size <= 56:
            break
        size -= 4
    LAST_SIZE[0] = size
    img = Image.new("RGBA", (CAP_W + 40, lh * len(lines) + 2 * stroke + 20), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    for k, ln in enumerate(lines):
        x = (img.width - widths[k]) / 2 + stroke
        y = stroke + 6 + k * lh
        for p, on in segs(ln):
            dr.text((x, y), p, font=f, fill=(*(acc if on else COLS["white"]), 255), anchor="la",
                    stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
            x += f.getlength(p)
    return img


def badge_layer(text):
    f = g.font(46, FONT)
    tw = f.getlength(text)
    bw, bh = int(tw + 104), 74
    img = Image.new("RGBA", (bw + 8, bh + 8), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([4, 4, 4 + bw, 4 + bh], 37, fill=(14, 40, 92, 235), outline=(255, 255, 255, 70), width=2)
    # small tricolour mark on the left
    cx, cy = 4 + 34, 4 + bh // 2
    for i, c in enumerate([(30, 90, 200), (245, 245, 245), (230, 50, 50)]):
        dr.rectangle([cx - 15 + i * 10, cy - 12, cx - 15 + i * 10 + 9, cy + 12], fill=(*c, 255))
    dr.text((4 + 62, cy + 1), text, font=f, fill=(255, 255, 255, 255), anchor="lm")
    return img


def red_arrow(dr, x0, y0, x1, y1, k=1.0):
    """Red arrow from (x0, y0) to the tip (x1, y1), black edge, grows in."""
    if k <= 0:
        return
    k = min(k, 1.0)
    L = math.hypot(x1 - x0, y1 - y0) * (0.4 + 0.6 * k)
    ux, uy = (x1 - x0) / math.hypot(x1 - x0, y1 - y0), (y1 - y0) / math.hypot(x1 - x0, y1 - y0)
    tx, ty = x1, y1
    sx, sy = tx - ux * L, ty - uy * L
    sw, hw, hl = 14, 40, 70
    nx, ny = -uy, ux
    bx, by = tx - ux * hl, ty - uy * hl
    pts = [(sx + nx * sw, sy + ny * sw), (bx + nx * sw, by + ny * sw), (bx + nx * hw, by + ny * hw), (tx, ty),
           (bx - nx * hw, by - ny * hw), (bx - nx * sw, by - ny * sw), (sx - nx * sw, sy - ny * sw)]
    a = int(255 * k)
    dr.line(pts + [pts[0]], fill=(0, 0, 0, a), width=12, joint="curve")
    dr.polygon(pts, fill=(*RED, a))


def backdrop(win):
    small = win.resize((64, 42), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2.2))
    cw = 42 * W / H
    small = small.crop((int(32 - cw / 2), 0, int(32 + cw / 2), 42))
    bg = small.resize((W, H), Image.BICUBIC)
    return bg.point(lambda v: int(v * 0.36))


def card(args, d, timing, base, out):
    items = args["items"]
    starts = []
    for i, it in enumerate(items):
        at = it.get("at", 0)
        starts.append(0.0 if i == 0 else (g.word_time(timing, at) if isinstance(at, str) else float(at)))
    ends = starts[1:] + [d]
    srcs = []
    for it, a, z in zip(items, starts, ends):
        dd = z - a
        if it.get("photo"):
            srcs.append(PhotoSrc(os.path.join(base, it["photo"]), it.get("kb"), dd))
        elif it.get("full"):
            srcs.append(VideoSrc(os.path.join(base, it["full"]), it.get("start", 0), it.get("speed", 1.0), dd, (W, H),
                                 grade=False))
        else:
            srcs.append(VideoSrc(os.path.join(base, it["video"]), it.get("start", 0), it.get("speed", 1.0), dd, (WW, WH),
                                 it.get("fx", 0.5), it.get("fy", 0.5), it.get("grade", True)))
    badge = badge_layer(args["badge"]) if args.get("badge") else None
    caps, cur = [], None
    for it in items:
        if it.get("cap") is not None:
            cur = it
        caps.append(cur)
    cap_cache = {}

    def cap_img(it, t_in):
        txt = it["cap"]
        if it.get("count") and "{n}" in txt:
            a, b, sec = it["count"]
            v = a + (b - a) * g.smooth(t_in / sec)
            txt = txt.replace("{n}", f"{int(round(v)):,}")
        k = (txt, it.get("col"), it.get("size", 118))
        if k not in cap_cache:
            cap_cache[k] = caption_layer(txt, it.get("col", "blue"), it.get("size", 118))
        return cap_cache[k]

    cap_t0 = {}
    for i, c in enumerate(caps):
        if c is not None and id(c) not in cap_t0:
            cap_t0[id(c)] = starts[i]
    for t in g.frames(d):
        i = max(j for j, a in enumerate(starts) if a <= t + 1e-6)
        it, src, tl = items[i], srcs[i], t - starts[i]
        if it.get("full"):
            out.write(src.frame(tl))
            continue
        win = src.frame(tl)
        settle = 1 - g.smooth(tl / 0.22)
        if settle > 0 and i > 0:   # short settle on each cut (not on the very first frame of a line)
            s = 1 + 0.035 * settle
            ww, wh = int(WW * s), int(WH * s)
            win = win.resize((ww, wh), Image.BILINEAR).crop(((ww - WW) // 2, (wh - WH) // 2, (ww - WW) // 2 + WW, (wh - WH) // 2 + WH))
        img = backdrop(win).convert("RGBA")
        img.paste(win, (WX0, WY0))
        dr = ImageDraw.Draw(img)
        if it.get("arrow"):
            x0, y0, x1, y1, ta = it["arrow"]
            red_arrow(dr, x0 + WX0, y0 + WY0, x1 + WX0, y1 + WY0, g.ramp(tl, ta, 0.3))
        dr.line([(0, WY1), (W, WY1)], fill=(255, 255, 255, 40), width=2)
        dr.line([(0, WY0 - 1), (W, WY0 - 1)], fill=(255, 255, 255, 40), width=2)
        if badge is not None:
            img.alpha_composite(badge, (W // 2 - badge.width // 2, BADGE_Y - badge.height // 2))
        c = caps[i]
        if c is not None:
            ct = t - cap_t0[id(c)]
            ci = base_ci = cap_img(c, ct)
            pop = 1 - g.smooth(ct / 0.18)
            if pop > 0 and t > 0.0:
                s = 1 + 0.12 * pop
                ci = ci.resize((int(ci.width * s), int(ci.height * s)), Image.BILINEAR)
            img.alpha_composite(ci, (int(CAP_CX - ci.width / 2), int(CAP_TOP - (ci.height - base_ci.height) / 2 - 6)))
        out.write(img.convert("RGB"))


GRAPHICS = {"card": card}
