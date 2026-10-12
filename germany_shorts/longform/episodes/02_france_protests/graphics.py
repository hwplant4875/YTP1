"""2D infographics for STRATA long-form #02, France's 2026 lycée protests (1920x1080).

Registered with assemble.py through {"type": "g2d", "name": ..., "module": "graphics.py", "args": {...}}.
House style (from graphics2d.py): big amber numbers with a black outer stroke, cream text, dark or blurred-photo
backgrounds, no red arrows or circles. Every key moment is tied to a word of the narration ("at": a phrase from the
line, or seconds into the shot), so numbers land when Mattes says them.

Graphics: crowd, icons, stat, bars, line, donut, split, montage, phone_posts, tiktok, lycee_def, day_counter, doc,
blackfade, quote.
"""
import math
import os
import subprocess
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

import graphics2d as G

INK, AMBER, GREY = G.INK, G.AMBER, (150, 148, 142)
DIM = (70, 68, 64)
FPS = G.FPS
BOLD = "YouTubeSans-DarkBlack.otf"
SEMI = "YouTubeSans-Black.otf"
CREDIT_COL = (180, 180, 180)


def W():
    return G.W


def H():
    return G.H


# ---------------------------------------------------------------- helpers

def at(timing, x, default=0.0):
    """Seconds into the shot for a narration phrase (or a number of seconds)."""
    if x is None:
        return default
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, list):   # [phrase, offset]
        return at(timing, x[0]) + x[1]
    return G.word_time(timing, x)


def fmt(v, dec=0):
    return f"{v:,.{dec}f}"


def roll(t, a, target, d=1.3, start=0.0):
    k = G.smooth((t - a) / d) if d > 0 else float(t >= a)
    return start + (target - start) * (1 - (1 - k) ** 2)


def fade_env(t, d, fin=0.35, fout=0.35):
    return G.smooth(t / fin) * G.smooth((d - t) / fout) if d > 0 else 1.0


@lru_cache(None)
def _photo(path, blur, dark, w, h, color=False):
    im = Image.open(path)
    im.draft("RGB", (w, h))
    im = ImageOps.exif_transpose(im).convert("RGB")
    im = ImageOps.fit(im, (w, h), Image.LANCZOS)
    if not color:
        im = im.convert("L").convert("RGB")
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(im, np.float32) * dark
    return a


def background(args, base):
    """Dark backdrop: a blurred, darkened photo (args.bg) or the house vignette."""
    if args.get("bg"):
        a = _photo(os.path.join(base, args["bg"]), args.get("bg_blur", 26), args.get("bg_dark", 0.3), W(), H())
        y, x = np.mgrid[0:H(), 0:W()]
        r = np.hypot((x - W() / 2) / W(), (y - H() / 2) / H())
        v = np.clip(1.15 - r * 1.1, 0.35, 1)[..., None]
        return Image.fromarray(np.clip(a * v, 0, 255).astype(np.uint8))
    return G.vignette_bg()


def credit(dr, s, alpha=1.0):
    """Bottom-left source line, grey at 50 %, like the assembler's CREDIT style."""
    if s and alpha > 0:
        dr.text((30, H() - 26), s, font=G.font(22, SEMI), fill=(*CREDIT_COL, int(128 * alpha)), anchor="ls")


def source(dr, s, alpha=1.0, xy=None):
    """Small data-source line under a graphic (cream, quiet)."""
    if s and alpha > 0:
        xy = xy or (W() - 40, H() - 30)
        dr.text(xy, s, font=G.font(26, SEMI), fill=(*GREY, int(220 * alpha)), anchor="rs")


def T(dr, xy, s, size, fill=INK, alpha=1.0, anchor="mm", name=BOLD, stroke=None):
    G.text(dr, xy, s, size, fill=fill, name=name, anchor=anchor, stroke=stroke, alpha=int(255 * max(0, min(1, alpha))))


def rgba_canvas(bg):
    return bg.copy().convert("RGBA") if bg is not None else Image.new("RGBA", (W(), H()), (0, 0, 0, 0))


# ---------------------------------------------------------------- icon grids

def stamp(shape, cw, ch):
    """Coverage mask (float 0..1) of one icon, drawn at 4x and reduced."""
    s = 4
    im = Image.new("L", (cw * s, ch * s), 0)
    d = ImageDraw.Draw(im)
    w, h = cw * s, ch * s
    if shape == "person":
        r = w * 0.2
        d.ellipse([w / 2 - r, h * 0.06, w / 2 + r, h * 0.06 + 2 * r], fill=255)
        d.rounded_rectangle([w * 0.2, h * 0.06 + 2 * r + h * 0.04, w * 0.8, h * 0.94], radius=w * 0.22, fill=255)
    elif shape == "school":
        d.polygon([(w * 0.1, h * 0.42), (w * 0.5, h * 0.1), (w * 0.9, h * 0.42)], fill=255)
        d.rectangle([w * 0.16, h * 0.42, w * 0.84, h * 0.9], fill=255)
    elif shape == "slot":
        d.rounded_rectangle([w * 0.06, h * 0.12, w * 0.94, h * 0.88], radius=w * 0.08, fill=255)
    elif shape == "desk":
        d.rectangle([w * 0.08, h * 0.3, w * 0.92, h * 0.45], fill=255)
        d.rectangle([w * 0.14, h * 0.45, w * 0.24, h * 0.88], fill=255)
        d.rectangle([w * 0.76, h * 0.45, w * 0.86, h * 0.88], fill=255)
    else:   # square
        d.rectangle([w * 0.1, h * 0.1, w * 0.9, h * 0.9], fill=255)
    return np.asarray(im.resize((cw, ch), Image.LANCZOS), np.float32) / 255


class IconGrid:
    """n icons packed into box; per-icon colour and alpha resolved per frame through an id map (fast)."""

    def __init__(self, n, box, shape="person", aspect=1.4, gap=0.18, seed=7):
        x0, y0, x1, y1 = box
        bw, bh = x1 - x0, y1 - y0
        cell = math.sqrt(bw * bh / (n * aspect))
        cols = max(1, int(bw / cell))
        rows = math.ceil(n / cols)
        while rows * cell * aspect > bh:
            cell *= 0.98
            cols = max(1, int(bw / cell))
            rows = math.ceil(n / cols)
        cw, ch = max(2, int(cell)), max(2, int(cell * aspect))
        iw, ih = max(2, int(cw * (1 - gap))), max(2, int(ch * (1 - gap)))
        st = stamp(shape, iw, ih)
        ox = x0 + (bw - cols * cw) / 2
        oy = y0 + (bh - rows * ch) / 2
        self.ids = np.full((H(), W()), -1, np.int32)
        self.cov = np.zeros((H(), W()), np.float32)
        self.pos = np.zeros((n, 2), np.float32)
        for i in range(n):
            c, r = i % cols, i // cols
            x, y = int(ox + c * cw), int(oy + r * ch)
            self.pos[i] = (x + cw / 2, y + ch / 2)
            sl = (slice(y, y + ih), slice(x, x + iw))
            m = st > 0.02
            self.ids[sl][m] = i
            self.cov[sl][m] = st[m]
        self.n, self.cols, self.rows = n, cols, rows
        rng = np.random.default_rng(seed)
        self.rand = rng.random(n)
        self.mask = self.ids >= 0
        self.mid = self.ids[self.mask]
        self.mcov = self.cov[self.mask][:, None]

    def draw(self, img, alpha, color):
        """alpha: (n,) 0..1, color: (n,3) floats. img: RGB PIL -> returns RGB PIL."""
        a = np.asarray(img.convert("RGB"), np.float32).copy()
        k = (alpha[self.mid][:, None] * self.mcov)
        px = a[self.mask]
        a[self.mask] = px * (1 - k) + color[self.mid] * k
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def wave(n, t, a, d, order):
    """Per-icon 0..1 reveal sweeping over `d` seconds in `order` (0..1 per icon)."""
    return np.clip((t - a - order * d) / 0.25, 0, 1)


# ---------------------------------------------------------------- crowd: police vs organisers

def g_crowd(args, d, timing, base, out):
    """args: a = {value, label, at}, b = {value, label, at}, title, source, bg."""
    A, B = args["a"], args["b"]
    ta, tb = at(timing, A["at"]), at(timing, B["at"])
    bg = background(args, base)
    n = 4600
    rng = np.random.default_rng(3)
    # crowd perspective: dots denser and larger towards the bottom
    u = rng.random(n)
    ys = 470 + (1 - (1 - u) ** 1.8) * 560
    xs = rng.random(n) * (W() + 80) - 40
    order = np.argsort(rng.random(n))
    na = int(n * A["value"] / B["value"])
    for t in G.frames(d):
        img = bg.copy().convert("RGBA")
        dr = ImageDraw.Draw(img)
        va = roll(t, ta - 0.2, A["value"], 1.4)
        vb = roll(t, tb - 0.2, B["value"], 1.4, start=A["value"]) if t > tb - 0.2 else va
        shown = int(n * (vb if t > tb - 0.2 else va) / B["value"])
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        for j in range(shown):
            i = order[j]
            r = 1.6 + (ys[i] - 470) / 560 * 3.4
            col = (*INK, 200) if j < na else (*AMBER, 230)
            ld.ellipse([xs[i] - r, ys[i] - r, xs[i] + r, ys[i] + r], fill=col)
        img.alpha_composite(lay)
        dr = ImageDraw.Draw(img)
        ka = G.ramp(t, ta - 0.4, 0.4)
        kb = G.ramp(t, tb - 0.4, 0.4)
        if args.get("title"):
            T(dr, (W() / 2, 80), args["title"], 52, alpha=G.ramp(t, 0.1, 0.4))
        xa = W() / 2 - 430 * kb
        T(dr, (xa, 250), fmt(va), 190 if kb < 1 else 170, fill=AMBER, alpha=ka)
        T(dr, (xa, 380), A["label"], 62, alpha=ka)
        if kb > 0:
            T(dr, (W() / 2 + 430, 250), fmt(vb), 170, fill=AMBER, alpha=kb)
            T(dr, (W() / 2 + 430, 380), B["label"], 62, alpha=kb)
        source(dr, args.get("source"), G.ramp(t, 0.3, 0.4))
        out.write(img.convert("RGB"))


# ---------------------------------------------------------------- icon tallies

def g_icons(args, d, timing, base, out):
    """args: n, shape, box, appear_at, appear_d, highlight: {k, at, d, label}, groups (instead of highlight):
    [{n, label, at, color}], head: [{text, at, size, color, y}], blank: {k, at} (icons fade out), source, bg."""
    bg = background(args, base)
    box = args.get("box", [140, 300, 1780, 1000])
    shape = args.get("shape", "person")
    groups = args.get("groups")
    n = sum(g["n"] for g in groups) if groups else args["n"]
    if groups and groups[0].get("box"):
        grids = [IconGrid(g["n"], g["box"], shape, aspect=args.get("aspect", 1.4), seed=7 + j) for j, g in enumerate(groups)]
    else:
        grids = None
    grid = IconGrid(n, box, shape, aspect=args.get("aspect", 1.4 if shape == "person" else 1.0)) if not grids else grids[0]
    rng = np.random.default_rng(11)
    t_app = at(timing, args.get("appear_at"), 0.15)
    app_d = args.get("appear_d", 1.2)
    order_app = (np.arange(n) % grid.cols) / max(grid.cols - 1, 1) * 0.6 + (np.arange(n) // grid.cols) / max(grid.rows, 1) * 0.4
    base_col = np.array(args.get("base_color", (205, 200, 190)), np.float32)
    col = np.tile(base_col, (n, 1))
    hl = args.get("highlight")
    hord = rng.random(n)
    if hl:
        hk = int(hl["k"])
        sel = np.zeros(n, bool)
        sel[rng.permutation(n)[:hk]] = True
    blank = args.get("blank")
    if blank:
        bsel = np.zeros(n, bool)
        bsel[rng.permutation(n)[:int(blank["k"])]] = True
    gstart = []
    if groups:
        s = 0
        for g in groups:
            gstart.append((s, s + g["n"]))
            s += g["n"]
    for t in G.frames(d):
        img = bg.copy()
        if groups:
            alpha = np.zeros(n, np.float32)
            for (a0, a1), g in zip(gstart, groups):
                tg = at(timing, g.get("at"), t_app)
                o = np.linspace(0, 1, a1 - a0)
                alpha[a0:a1] = np.clip((t - tg - o * g.get("d", 1.0)) / 0.25, 0, 1) * 0.92
                c = np.array(AMBER if g.get("color") == "amber" else g.get("color", base_col), np.float32)
                col[a0:a1] = c
        else:
            alpha = wave(n, t, t_app, app_d, order_app) * 0.55
            if hl:
                th = at(timing, hl["at"])
                k = np.clip((t - th - hord * hl.get("d", 1.2)) / 0.3, 0, 1) * sel
                alpha = alpha + k * 0.45
                col = base_col[None] * (1 - k[:, None]) + np.array(AMBER, np.float32)[None] * k[:, None]
            if blank:
                tb = at(timing, blank["at"])
                kb = np.clip((t - tb - hord * blank.get("d", 1.0)) / 0.3, 0, 1) * bsel
                alpha = alpha * (1 - 0.88 * kb)
        if grids:
            for gr, (a0, a1) in zip(grids, gstart):
                img = gr.draw(img, alpha[a0:a1], col[a0:a1])
        else:
            img = grid.draw(img, alpha, col)
        img = img.convert("RGBA")
        dr = ImageDraw.Draw(img)
        for h in args.get("head", []):
            th = at(timing, h.get("at"), 0.1)
            k = G.ramp(t, th - 0.15, 0.35) * (1 - G.ramp(t, at(timing, h["until"]) - 0.2, 0.3) if h.get("until") else 1)
            if k <= 0:
                continue
            txt = h["text"]
            if h.get("count"):
                txt = h.get("prefix", "") + fmt(roll(t, th, h["count"], h.get("roll", 1.2))) + h.get("suffix", "")
            if h.get("panel"):
                G.panel(img, h["panel"], alpha=int(190 * k))
                dr = ImageDraw.Draw(img)
            T(dr, (h.get("x", W() / 2), h["y"]), txt, h.get("size", 120), fill=AMBER if h.get("color") == "amber" else INK, alpha=k)
        if groups:
            for (a0, a1), g in zip(gstart, groups):
                if not g.get("label"):
                    continue
                tg = at(timing, g.get("at"), t_app)
                k = G.ramp(t, tg + 0.2, 0.4)
                p = grids[gstart.index((a0, a1))].pos if grids else grid.pos[a0:a1]
                x = float(p[:, 0].mean())
                y = float(p[:, 1].max()) + 60
                if g.get("label_xy"):
                    x, y = g["label_xy"]
                T(dr, (x, y), g["label"], g.get("label_size", 50), fill=AMBER if g.get("color") == "amber" else INK, alpha=k)
        source(dr, args.get("source"), G.ramp(t, 0.3, 0.4))
        out.write(img.convert("RGB"))


# ---------------------------------------------------------------- big numbers

def g_stat(args, d, timing, base, out):
    """args: items: [{value, dec, prefix, suffix, label, at, until, y, x, size, color, roll, text}], source, bg, alpha.
    A number rolls up when its phrase is spoken; `text` instead of `value` shows a fixed word."""
    bg = None if args.get("alpha") else background(args, base)
    for t in G.frames(d):
        img = rgba_canvas(bg)
        dr = ImageDraw.Draw(img)
        if args.get("panel"):
            ks = [G.ramp(t, at(timing, it.get("at"), 0.1) - 0.3, 0.3) for it in args["items"]]
            G.panel(img, args["panel"], alpha=int(180 * max(ks)))
            dr = ImageDraw.Draw(img)
        for it in args["items"]:
            ta = at(timing, it.get("at"), 0.1)
            k = G.ramp(t, ta - 0.15, 0.3)
            if it.get("until") is not None:
                k *= 1 - G.ramp(t, at(timing, it["until"]) - 0.25, 0.3)
            if k <= 0:
                continue
            x, y = it.get("x", W() / 2), it.get("y", H() / 2 - 40)
            if "value" in it:
                v = roll(t, ta - 0.1, it["value"], it.get("roll", 1.1), it.get("from", 0))
                s = it.get("prefix", "") + fmt(v, it.get("dec", 0)) + it.get("suffix", "")
            else:
                s = it["text"]
            col = INK if it.get("color") == "ink" else AMBER
            T(dr, (x, y), s, it.get("size", 220), fill=col, alpha=k)
            if it.get("label"):
                T(dr, (x, y + it.get("size", 220) * 0.62 + 20), it["label"], it.get("label_size", 64), alpha=k)
        source(dr, args.get("source"), G.ramp(t, 0.3, 0.4))
        out.write(img if args.get("alpha") else img.convert("RGB"))


# ---------------------------------------------------------------- bars

def g_bars(args, d, timing, base, out):
    """Horizontal bars. args: items [{label, value, at, color, text}], max, unit_prefix, unit_suffix, title, source, bg."""
    bg = background(args, base)
    items = args["items"]
    vmax = args.get("max", max(i["value"] for i in items))
    n = len(items)
    x0, x1 = args.get("x0", 560), args.get("x1", 1380)
    ytop = args.get("ytop", 330 if n > 2 else 400)
    gap = args.get("gap", min(230, 560 / max(n, 1)))
    for t in G.frames(d):
        img = bg.copy().convert("RGBA")
        dr = ImageDraw.Draw(img)
        if args.get("title"):
            T(dr, (W() / 2, 150), args["title"], args.get("title_size", 76), alpha=G.ramp(t, 0.1, 0.4))
        for i, it in enumerate(items):
            ta = at(timing, it.get("at"), 0.2 + 0.3 * i)
            k = G.ramp(t, ta - 0.2, 0.3)
            if k <= 0:
                continue
            y = ytop + i * gap
            grow = G.smooth((t - ta + 0.1) / 1.0)
            v = it["value"] * grow
            col = AMBER if it.get("color", "amber") == "amber" else (196, 190, 178)
            bh = args.get("bar_h", 86)
            dr.rounded_rectangle([x0, y - bh / 2, x0 + max(4, (x1 - x0) * v / vmax), y + bh / 2], radius=10,
                                 fill=(*col, int(255 * k)))
            T(dr, (x0 - 40, y), it["label"], it.get("label_size", 58), alpha=k, anchor="rm")
            s = it.get("text") or (args.get("unit_prefix", "") + fmt(v, args.get("dec", 0)) + args.get("unit_suffix", ""))
            if it.get("text") and grow < 1:
                s = args.get("unit_prefix", "") + fmt(v, args.get("dec", 0)) + args.get("unit_suffix", "")
            T(dr, (x0 + max(4, (x1 - x0) * v / vmax) + 30, y), s, args.get("value_size", 92), fill=AMBER if col == AMBER else INK,
              alpha=k, anchor="lm")
        for h in args.get("head", []):
            th = at(timing, h.get("at"), 0.1)
            k = G.ramp(t, th - 0.15, 0.35)
            T(dr, (h.get("x", W() / 2), h["y"]), h["text"], h.get("size", 90), fill=AMBER if h.get("color") == "amber" else INK, alpha=k)
        source(dr, args.get("source"), G.ramp(t, 0.3, 0.4))
        out.write(img.convert("RGB"))


# ---------------------------------------------------------------- line chart (Parcoursup)

def g_line(args, d, timing, base, out):
    """args: points [{x_label, value, at}], unit, title, ymax, source, bg, head."""
    bg = background(args, base)
    pts = args["points"]
    ymax = args.get("ymax", max(p["value"] for p in pts) * 1.25)
    x0, x1, yb, yt = 380, 1540, 900, 330
    xy = [(x0 + (x1 - x0) * i / max(len(pts) - 1, 1), yb - (yb - yt) * p["value"] / ymax) for i, p in enumerate(pts)]
    for t in G.frames(d):
        img = bg.copy().convert("RGBA")
        dr = ImageDraw.Draw(img)
        if args.get("title"):
            T(dr, (W() / 2, 140), args["title"], 72, alpha=G.ramp(t, 0.1, 0.4))
        dr.line([x0 - 60, yb, x1 + 60, yb], fill=(*GREY, 200), width=3)
        for i, p in enumerate(pts):
            ta = at(timing, p.get("at"), 0.3 + i * 0.5)
            k = G.ramp(t, ta - 0.2, 0.35)
            if i > 0 and k > 0:
                g = G.smooth((t - ta + 0.2) / 0.6)
                a, b = xy[i - 1], xy[i]
                dr.line([a, (a[0] + (b[0] - a[0]) * g, a[1] + (b[1] - a[1]) * g)], fill=(*AMBER, 255), width=10)
            if k > 0:
                x, y = xy[i]
                last = i == len(pts) - 1
                r = 16 if last else 12
                dr.ellipse([x - r, y - r, x + r, y + r], fill=(*(AMBER if last else INK), int(255 * k)))
                T(dr, (x, y - 80), fmt(p["value"], p.get("dec", 0)) + args.get("unit", "%"), 120 if last else 84,
                  fill=AMBER if last else INK, alpha=k)
                T(dr, (x, yb + 56), p["x_label"], 52, alpha=k)
        for h in args.get("head", []):
            th = at(timing, h.get("at"), 0.1)
            T(dr, (h.get("x", W() / 2), h["y"]), h["text"], h.get("size", 90), fill=AMBER if h.get("color") == "amber" else INK,
              alpha=G.ramp(t, th - 0.15, 0.35))
        source(dr, args.get("source"), G.ramp(t, 0.3, 0.4))
        out.write(img.convert("RGB"))


# ---------------------------------------------------------------- donuts (poll)

def g_donut(args, d, timing, base, out):
    """args: items [{value, label, at, x}], title, source, bg."""
    bg = background(args, base)
    for t in G.frames(d):
        img = bg.copy().convert("RGBA")
        dr = ImageDraw.Draw(img)
        if args.get("title"):
            T(dr, (W() / 2, 140), args["title"], 68, alpha=G.ramp(t, 0.1, 0.4))
        for i, it in enumerate(args["items"]):
            ta = at(timing, it.get("at"), 0.3)
            k = G.ramp(t, ta - 0.2, 0.35)
            if k <= 0:
                continue
            cx, cy, R = it.get("x", W() / 2), 560, 230
            v = roll(t, ta - 0.1, it["value"], 1.2)
            lay = Image.new("RGBA", (W() * 2, H() * 2), (0, 0, 0, 0))
            ld = ImageDraw.Draw(lay)
            bb = [2 * (cx - R), 2 * (cy - R), 2 * (cx + R), 2 * (cy + R)]
            ld.ellipse(bb, outline=(*DIM, int(255 * k)), width=2 * 46)
            ld.arc(bb, -90, -90 + 360 * v / 100, fill=(*AMBER, int(255 * k)), width=2 * 46)
            img.alpha_composite(lay.resize((W(), H()), Image.LANCZOS))
            dr = ImageDraw.Draw(img)
            T(dr, (cx, cy), f"{v:.0f}%", 150, fill=AMBER, alpha=k)
            T(dr, (cx, cy + R + 90), it["label"], 54, alpha=k)
        source(dr, args.get("source"), G.ramp(t, 0.3, 0.4))
        out.write(img.convert("RGB"))


# ---------------------------------------------------------------- two-sided claims

def g_split(args, d, timing, base, out):
    """args: left {head, body, at}, right {head, body, at}, bg, source. A thin cream divider."""
    bg = background(args, base)
    for t in G.frames(d):
        img = bg.copy().convert("RGBA")
        dr = ImageDraw.Draw(img)
        kd = G.ramp(t, 0.1, 0.4)
        dr.line([W() / 2, 260, W() / 2, 260 + 560 * kd], fill=(*GREY, int(200 * kd)), width=3)
        for side, x in (("left", W() / 4 + 20), ("right", 3 * W() / 4 - 20)):
            s = args[side]
            k = G.ramp(t, at(timing, s.get("at"), 0.2) - 0.15, 0.35)
            T(dr, (x, 330), s["head"], 60, alpha=k)
            T(dr, (x, 540), s["big"], s.get("big_size", 200), fill=AMBER, alpha=k)
            for j, line in enumerate(s.get("body", [])):
                T(dr, (x, 730 + j * 70), line, 52, alpha=k)
        source(dr, args.get("source"), G.ramp(t, 0.3, 0.4))
        out.write(img.convert("RGB"))


# ---------------------------------------------------------------- photo / clip montage with in-graphic credits

class ClipReader:
    def __init__(self, path, start, w, h, fps=FPS):
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(start), "-i", path, "-vf",
                                   f"fps={fps},scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}",
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.w, self.h, self.last = w, h, None

    def read(self):
        b = self.p.stdout.read(self.w * self.h * 3)
        if len(b) == self.w * self.h * 3:
            self.last = Image.frombytes("RGB", (self.w, self.h), b)
        return self.last

    def close(self):
        self.p.kill()


def kenburns(src, k, frm, to):
    z0, x0, y0 = frm
    z1, x1, y1 = to
    k = G.smooth(k)
    z, cx, cy = z0 + (z1 - z0) * k, x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
    cw, ch = src.width / z, src.width / z * H() / W()
    if ch > src.height / z:
        ch = src.height / z
        cw = ch * W() / H()
    left = min(max(cx * src.width - cw / 2, 0), src.width - cw)
    top = min(max(cy * src.height - ch / 2, 0), src.height - ch)
    return src.transform((W(), H()), Image.EXTENT, (left, top, left + cw, top + ch), Image.BICUBIC)


@lru_cache(None)
def _still(path):
    im = Image.open(path)
    im.draft("RGB", (W() * 2, H() * 2))
    im = ImageOps.exif_transpose(im).convert("L").convert("RGB")
    s = max(W() * 2 / im.width, H() * 2 / im.height)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


def g_montage(args, d, timing, base, out):
    """Hard cuts on spoken words between stills (Ken Burns) and short framed clips, each with its own credit.
    args: items [{file | video, at, from, to, credit, start, frame}]"""
    items = args["items"]
    starts = [at(timing, it.get("at"), 0.0) if i else 0.0 for i, it in enumerate(items)]
    ends = starts[1:] + [d]
    readers = {}
    for t in G.frames(d):
        i = max(j for j, s in enumerate(starts) if t >= s - 1e-6)
        it = items[i]
        k = (t - starts[i]) / max(ends[i] - starts[i], 0.1)
        if it.get("file"):
            img = kenburns(_still(os.path.join(base, it["file"])), k, it.get("from", [1.05, 0.5, 0.5]), it.get("to", [1.18, 0.5, 0.5]))
        else:
            if i not in readers:
                f = it.get("frame", 0.78)
                readers[i] = (ClipReader(os.path.join(base, it["video"]), it.get("start", 0), int(W() * f) // 2 * 2,
                                         int(H() * f) // 2 * 2), f)
            r, f = readers[i]
            fr = r.read().convert("L").convert("RGB")
            img = fr.resize((W() // 4, H() // 4)).filter(ImageFilter.GaussianBlur(10)).resize((W(), H()))
            img = Image.fromarray((np.asarray(img, np.float32) * 0.45).astype(np.uint8))
            dr0 = ImageDraw.Draw(img)
            x, y = (W() - fr.width) // 2, (H() - fr.height) // 2
            dr0.rectangle([x - 3, y - 3, x + fr.width + 2, y + fr.height + 2], fill=(58, 58, 58))
            img.paste(fr, (x, y))
        img = img.convert("RGBA")
        credit(ImageDraw.Draw(img), it.get("credit"))
        out.write(img.convert("RGB"))
    for r, _ in readers.values():
        r.close()


# ---------------------------------------------------------------- black, then a slow fade into a blurred photo

def g_blackfade(args, d, timing, base, out):
    """args: file, hold (s of black), fade (s), blur, credit."""
    im = Image.fromarray(_photo(os.path.join(base, args["file"]), args.get("blur", 14), args.get("dark", 0.55), W(), H()).astype(np.uint8))
    for t in G.frames(d):
        k = G.smooth((t - args.get("hold", 0.8)) / args.get("fade", 2.0))
        img = Image.blend(Image.new("RGB", (W(), H())), im, k).convert("RGBA")
        credit(ImageDraw.Draw(img), args.get("credit"), k)
        out.write(img.convert("RGB"))


# ---------------------------------------------------------------- phones: two generic posts

def phone(img, cx, cy, w, h, alpha=1.0):
    """Generic phone outline (no brand). Returns the screen box."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    a = int(255 * alpha)
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=w * 0.11, fill=(20, 20, 22, a), outline=(110, 108, 104, a), width=4)
    sx0, sy0, sx1, sy1 = cx - w / 2 + 16, cy - h / 2 + 16, cx + w / 2 - 16, cy + h / 2 - 16
    d.rounded_rectangle([sx0, sy0, sx1, sy1], radius=w * 0.09, fill=(30, 30, 33, a))
    d.rounded_rectangle([cx - 50, sy0 + 10, cx + 50, sy0 + 34], radius=12, fill=(10, 10, 10, a))
    img.alpha_composite(lay)
    return [int(sx0), int(sy0), int(sx1), int(sy1)]


def g_phone_posts(args, d, timing, base, out):
    """Two phones, generic social posts (no real handles), date tag, amber underline on `underline_at`."""
    bg = background(args, base)
    photo = Image.fromarray(_photo(os.path.join(base, args["photo"]), 0, 0.85, 400, 300).astype(np.uint8)) if args.get("photo") else None
    t_u = at(timing, args.get("underline_at"), 999)
    for t in G.frames(d):
        img = bg.copy().convert("RGBA")
        for j, cx in enumerate((W() / 2 - 300, W() / 2 + 300)):
            k = G.ramp(t, 0.2 + 0.35 * j, 0.45)
            if k <= 0:
                continue
            dy = 60 * (1 - k)
            sb = phone(img, cx, 600 + dy, 470, 860, k)
            dr = ImageDraw.Draw(img)
            x0, y0, x1, _ = sb
            a = int(255 * k)
            dr.ellipse([x0 + 24, y0 + 70, x0 + 84, y0 + 130], fill=(*AMBER, a))
            dr.text((x0 + 100, y0 + 80), "MP · LA FRANCE INSOUMISE", font=G.font(22, SEMI), fill=(*INK, a))
            dr.rounded_rectangle([x0 + 100, y0 + 112, x0 + 260, y0 + 126], radius=6, fill=(*GREY, a))
            for r in range(3):
                dr.rounded_rectangle([x0 + 24, y0 + 160 + r * 30, x1 - 24 - (90 if r == 2 else 0), y0 + 176 + r * 30], radius=7,
                                     fill=(200, 196, 188, int(a * 0.8)))
            if photo:
                ph = photo.copy()
                ph.putalpha(a)
                img.alpha_composite(ph.resize((x1 - x0 - 48, 300)), (x0 + 24, y0 + 270))
                dr = ImageDraw.Draw(img)
            for q in range(3):
                dr.ellipse([x0 + 30 + q * 120, y0 + 600, x0 + 62 + q * 120, y0 + 632], outline=(*GREY, a), width=3)
        dr = ImageDraw.Draw(img)
        kt = G.ramp(t, 0.3, 0.4)
        T(dr, (W() / 2, 95), args.get("date", "21 SEPT"), 96, fill=AMBER, alpha=kt)
        T(dr, (W() / 2, 1010), args.get("caption", "TWO LFI MPs VISIT · AND POST"), 56, alpha=kt)
        ku = G.smooth((t - t_u) / 0.5)
        if ku > 0:
            wcap = 760
            dr.rounded_rectangle([W() / 2 - wcap / 2, 1048, W() / 2 - wcap / 2 + wcap * ku, 1060], radius=5, fill=(*AMBER, 255))
        credit(dr, args.get("credit"))
        out.write(img.convert("RGB"))


# ---------------------------------------------------------------- the viral interview, in a generic vertical-video frame

def g_tiktok(args, d, timing, base, out):
    """args: video, start, blur (px), date, lines [...], quote {text, at}, views {value, at}, credit."""
    bg = background(args, base)
    pw, ph = 520, 924
    cx, cy = 1260, 560
    reader = ClipReader(os.path.join(base, args["video"]), args.get("start", 0), pw - 32, ph - 32)
    tq = at(timing, args["quote"]["at"]) if args.get("quote") else 999
    tv = at(timing, args["views"]["at"]) if args.get("views") else 999
    for t in G.frames(d):
        img = bg.copy().convert("RGBA")
        sb = phone(img, cx, cy, pw, ph)
        fr = reader.read().convert("L").convert("RGB").filter(ImageFilter.GaussianBlur(args.get("blur", 16)))
        fr = Image.fromarray((np.asarray(fr, np.float32) * 0.8).astype(np.uint8))
        mask = Image.new("L", fr.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, fr.width - 1, fr.height - 1], radius=40, fill=255)
        img.paste(fr, (sb[0], sb[1]), mask)
        dr = ImageDraw.Draw(img)
        # generic short-video UI: side buttons, caption bars, progress line
        x1, y1 = sb[2], sb[3]
        for q in range(4):
            dr.ellipse([x1 - 78, cy - 40 + q * 100, x1 - 26, cy + 12 + q * 100], fill=(240, 236, 228, 210))
        dr.rounded_rectangle([sb[0] + 26, y1 - 150, sb[0] + 300, y1 - 130], radius=8, fill=(240, 236, 228, 220))
        dr.rounded_rectangle([sb[0] + 26, y1 - 112, sb[0] + 380, y1 - 96], radius=8, fill=(200, 196, 188, 190))
        dr.rectangle([sb[0], y1 - 20, sb[0] + (x1 - sb[0]) * min(1, t / max(d, 1)), y1 - 14], fill=(*AMBER, 255))
        # left column
        k0 = G.ramp(t, 0.2, 0.4)
        T(dr, (480, 210), args.get("date", "24 SEPT"), 96, fill=AMBER, alpha=k0)
        for j, line in enumerate(args.get("lines", [])):
            T(dr, (480, 330 + j * 70), line, 56, alpha=k0)
        kq = G.ramp(t, tq - 0.2, 0.4) * (1 - G.ramp(t, tv - 0.4, 0.3))
        if kq > 0:
            T(dr, (480, 640), args["quote"]["text"], 76, fill=AMBER, alpha=kq)
            if args["quote"].get("sub"):
                T(dr, (480, 730), args["quote"]["sub"], 40, alpha=kq, name=SEMI)
        kv = G.ramp(t, tv - 0.2, 0.35)
        if kv > 0:
            v = roll(t, tv, args["views"]["value"], 1.4)
            T(dr, (480, 640), f"{v / 1e6:.1f}M" if v >= 1e5 else fmt(v), 210, fill=AMBER, alpha=kv)
            T(dr, (480, 780), "VIEWS", 70, alpha=kv)
        credit(dr, args.get("credit"))
        out.write(img.convert("RGB"))
    reader.close()


# ---------------------------------------------------------------- lycée = high school (overlay)

def g_lycee_def(args, d, timing, base, out):
    t0 = at(timing, args.get("at"), 0.1)
    for t in G.frames(d):
        img = Image.new("RGBA", (W(), H()), (0, 0, 0, 0))
        k = G.ramp(t, t0 - 0.2, 0.4) * G.smooth((d - t) / 0.4)
        if k > 0:
            dr = ImageDraw.Draw(img)
            T(dr, (W() / 2, 330), "LYCÉE", 190, fill=AMBER, alpha=k)
            T(dr, (W() / 2, 470), "= HIGH SCHOOL", 92, alpha=k)
            x0, x1, y = 560, 1360, 690
            ages = [15, 16, 17, 18]
            g = G.smooth((t - t0 - 0.6) / 1.6)
            dr.rounded_rectangle([x0, y - 14, x1, y + 14], radius=14, fill=(60, 58, 54, int(220 * k)))
            dr.rounded_rectangle([x0, y - 14, x0 + (x1 - x0) * g, y + 14], radius=14, fill=(*AMBER, int(255 * k)))
            for j, a in enumerate(ages):
                x = x0 + (x1 - x0) * j / 3
                kk = k * G.ramp(t, t0 + 0.5 + j * 0.45, 0.3)
                dr.ellipse([x - 22, y - 22, x + 22, y + 22], fill=(*(AMBER if g >= j / 3 else INK), int(255 * kk)))
                T(dr, (x, y + 80), str(a), 72, alpha=kk)
            T(dr, (W() / 2, 880), "AGES 15 TO 18", 54, alpha=k * G.ramp(t, t0 + 1.8, 0.4))
        out.write(img)


# ---------------------------------------------------------------- date + school counter over the 3D spread map (overlay)

def g_day_counter(args, d, timing, base, out):
    """args: steps [{at, date, day, value}], label. Rolls from step to step; panel top-left."""
    steps = args["steps"]
    ts = [at(timing, s["at"]) for s in steps]
    for t in G.frames(d):
        img = Image.new("RGBA", (W(), H()), (0, 0, 0, 0))
        k = G.ramp(t, ts[0] - 0.4, 0.4) * G.smooth((d - t) / 0.35)
        if k > 0:
            i = max([j for j, x in enumerate(ts) if t >= x - 0.3] or [0])
            prev = steps[i - 1]["value"] if i > 0 else 0
            v = roll(t, ts[i] - 0.3, steps[i]["value"], 1.0, start=prev)
            G.panel(img, [60, 60, 620, 440], alpha=int(170 * k))
            dr = ImageDraw.Draw(img)
            T(dr, (90, 130), steps[i]["date"], 64, fill=INK, alpha=k, anchor="lm")
            T(dr, (590, 130), f"DAY {steps[i]['day']}", 46, fill=GREY, alpha=k, anchor="rm")
            T(dr, (90, 270), ("~" if steps[i].get("approx") else "") + fmt(v), 170, fill=AMBER, alpha=k, anchor="lm")
            T(dr, (90, 395), args.get("label", "LYCÉES HIT"), 44, alpha=k, anchor="lm")
        out.write(img)


# ---------------------------------------------------------------- a generic note with highlighted words

def g_doc(args, d, timing, base, out):
    """args: lines (text with [[word]] marks), marks [{word, at}], tally [{text, at, y}], title, source, bg."""
    bg = background(args, base)
    paper = (226, 222, 212)
    for t in G.frames(d):
        img = bg.copy().convert("RGBA")
        dr = ImageDraw.Draw(img)
        k = G.ramp(t, 0.1, 0.4)
        x0, y0, x1, y1 = 260, 150, 1060, 960
        dr.rectangle([x0, y0, x1, y1], fill=(*paper, int(240 * k)))
        dr.text((x0 + 40, y0 + 40), args.get("title", "NOTE · CONFIDENTIAL"), font=G.font(34, SEMI), fill=(40, 40, 40, int(255 * k)))
        rng = np.random.default_rng(5)
        y = y0 + 120
        for li, line in enumerate(args["lines"]):
            x = x0 + 40
            for word in line.split():
                hl = word.startswith("[[")
                w_ = word.strip("[]")
                f = G.font(30, SEMI)
                ww = dr.textlength(w_ + " ", font=f)
                if hl:
                    th = at(timing, args.get("mark_at"), 0.5) + 0.12 * li
                    kh = G.smooth((t - th) / 0.35)
                    if kh > 0:
                        dr.rectangle([x - 4, y - 4, x + (ww - 8) * kh, y + 36], fill=(*AMBER, int(230 * k)))
                    dr.text((x, y), w_, font=f, fill=(20, 20, 20, int(255 * k)))
                elif set(w_) == {"█"}:
                    ww = 50 * len(w_) + rng.random() * 30
                    if x + ww > x1 - 40:
                        break
                    dr.rectangle([x, y + 4, x + ww - 14, y + 30], fill=(20, 20, 20, int(255 * k)))
                else:
                    dr.text((x, y), w_, font=f, fill=(70, 70, 70, int(255 * k)))
                x += ww
            y += 54
        for tl in args.get("tally", []):
            kk = G.ramp(t, at(timing, tl["at"]) - 0.15, 0.35)
            T(dr, (1470, tl["y"]), tl["text"], tl.get("size", 130), fill=AMBER if tl.get("color", "amber") == "amber" else INK, alpha=kk)
            if tl.get("label"):
                T(dr, (1470, tl["y"] + 105), tl["label"], 50, alpha=kk)
        source(dr, args.get("source"), G.ramp(t, 0.3, 0.4))
        out.write(img.convert("RGB"))


GRAPHICS = {"crowd": g_crowd, "icons": g_icons, "stat": g_stat, "bars": g_bars, "line": g_line, "donut": g_donut,
            "split": g_split, "montage": g_montage, "blackfade": g_blackfade, "phone_posts": g_phone_posts, "tiktok": g_tiktok,
            "lycee_def": g_lycee_def, "day_counter": g_day_counter, "doc": g_doc}
