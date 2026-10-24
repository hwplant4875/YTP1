"""EP1 graphics layer: composites HUD captions, name tags, counters, map graphics and the glitch cut onto rendered
PNG frames. Pure PIL/numpy, runs after Blender, no GPU. Driven by one timeline JSON per segment (graphics_timeline.md).

    python hud2.py timeline.json                       render every frame of the segment (+ mp4 if "mp4" is set)
    python hud2.py timeline.json --only 0,117,150      just these frame indices (quick checks)
    python hud2.py timeline.json --still in.png out.png --index 117 [--t 7.8]   one still, any image

Library:
    import hud2
    tl = hud2.load("graphics/seg_trost.json")
    img = hud2.compose(tl, Image.open(frame_png), index=i)          # -> RGB PIL image

Track types: place, caption, title, tag, counter, map, glitch, fade (see graphics_timeline.md).
Fonts (theme, per the user's rule: never Pretendard / YouTube Sans): Pirata One = tags, places, labels;
Grenze Gotisch (bold) = numbers (Pirata One digits read worse at 480p); Ditty = big title words only
(Ditty has no digits or punctuation: any title text with them falls back to Pirata One).
"""
import argparse, glob, json, math, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hudcam, maps  # noqa: E402

F = lambda n: os.path.join(HERE, "fonts", n)
F_TITLE, F_LABEL, F_NUM = F("Ditty.ttf"), F("PirataOne-Regular.ttf"), F("GrenzeGotisch-VF.ttf")
COL = {
    "cream": (238, 228, 204), "ink": (238, 228, 204), "gold": (214, 176, 102), "red": (196, 52, 40),
    "green": (96, 150, 92), "blue": (112, 150, 190), "dark": (14, 11, 8), "grey": (150, 146, 138),
}
SS = 2                                    # supersampling of the vector layers

_FC = {}


def font(path, size, wght=None):
    k = (path, int(size), wght)
    if k not in _FC:
        f = ImageFont.truetype(path, max(4, int(size)))
        if wght is not None:
            try:
                f.set_variation_by_axes([wght])
            except Exception:
                pass
        _FC[k] = f
    return _FC[k]


def col(c, a=1.0):
    c = COL.get(c, c) if isinstance(c, str) else c
    return (int(c[0]), int(c[1]), int(c[2]), int(255 * max(0.0, min(1.0, a))))


def ease(u):
    u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)


def env(t, e, fin=0.35, fout=0.35):
    t0, t1 = e.get("t0", -1e9), e.get("t1", 1e9)
    fin, fout = e.get("fade_in", fin), e.get("fade_out", fout)
    if t < t0 or t > t1:
        return 0.0
    a = ease((t - t0) / fin) if fin > 0 else 1.0
    b = ease((t1 - t) / fout) if fout > 0 else 1.0
    return min(a, b)


class Ctx:
    def __init__(self, W, H, t, index, cam):
        self.W, self.H, self.t, self.i, self.cam = W, H, t, index, cam
        self.s = H / 480.0 * SS           # 1 unit = 1 px at 480p, on the supersampled layers
        self.under = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))   # plates (no drop shadow)
        self.ink = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))     # text and lines (drop shadow)
        self.du, self.d = ImageDraw.Draw(self.under), ImageDraw.Draw(self.ink)


def spaced(d, xy, text, fnt, fill, anchor="ls", track=0.0, **kw):
    """Letter-spaced text; returns its width. anchor[0] in l/m/r."""
    widths = [d.textlength(c, font=fnt) for c in text]
    total = sum(widths) + track * max(0, len(text) - 1)
    x = xy[0] - {"l": 0, "m": total / 2, "r": total}[anchor[0]]
    if fill is not None:
        for c, w in zip(text, widths):
            d.text((x, xy[1]), c, font=fnt, fill=fill, anchor="l" + anchor[1], **kw); x += w + track
    return total


def plate(c, box, a, side="l"):
    """Soft dark gradient plate behind text (under layer): fades out toward the far side."""
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = max(1, x1 - x0), max(1, y1 - y0)
    gx = np.linspace(0, 1, w)
    gx = 1 - gx if side == "l" else (gx if side == "r" else 1 - np.abs(gx * 2 - 1))
    gy = (1 - np.linspace(-1, 1, h) ** 2) ** 1.5
    alpha = (np.outer(gy, np.clip(gx * 1.6, 0, 1) ** 1.5) * 255 * 0.42 * a).astype(np.uint8)
    p = Image.new("RGBA", (w, h), COL["dark"] + (0,)); p.putalpha(Image.fromarray(alpha))
    c.under.alpha_composite(p, (max(0, x0), max(0, y0)), (max(0, -x0), max(0, -y0)))


# ---------------------------------------------------------------- place / year / sub ("SHIGANSHINA · 845", "Eren, age 10")
def el_place(c, e):
    a = env(c.t, e, 0.5, 0.5)
    if a <= 0:
        return
    s, W, H = c.s, c.W * SS, c.H * SS
    ain = ease((c.t - e.get("t0", 0)) / 0.6)
    right = e.get("pos", "tl") == "tr"
    m = 20 * s
    y = m + 22 * s - (1 - ain) * 6 * s
    f1, fy, f2 = font(F_LABEL, 24 * s), font(F_NUM, 24 * s, 760), font(F_LABEL, 16 * s)
    place, year, sub = e.get("place", "").upper(), str(e.get("year", "")), e.get("sub", "")
    tr = 1.4 * s
    wp = spaced(c.d, (0, 0), place, f1, None, track=tr)
    sep = "  ·  " if place and year else ""
    ws = c.d.textlength(sep, font=f1)
    wy = c.d.textlength(year, font=fy)
    wtot = wp + ws + wy
    x0 = W - m - wtot if right else m
    plate(c, (W - m - wtot - 70 * s, y - 34 * s, W, y + 34 * s) if right else (0, y - 34 * s, x0 + wtot + 70 * s, y + 34 * s),
          a, "r" if right else "l")
    spaced(c.d, (x0, y), place, f1, col("cream", a), "ls", track=tr)
    c.d.text((x0 + wp, y), sep, font=f1, fill=col("gold", a), anchor="ls")
    c.d.text((x0 + wp + ws, y), year, font=fy, fill=col("gold", a), anchor="ls")
    rw = wtot * ease((c.t - e.get("t0", 0) - 0.1) / 0.7)
    ry = y + 6 * s
    if right:
        c.d.line([(W - m - rw, ry), (W - m, ry)], fill=col("gold", a * 0.9), width=max(1, int(1.2 * s)))
    else:
        c.d.line([(x0, ry), (x0 + rw, ry)], fill=col("gold", a * 0.9), width=max(1, int(1.2 * s)))
    if sub:
        a2 = a * ease((c.t - e.get("t0", 0) - 0.3) / 0.5)
        c.d.text((W - m if right else x0, ry + 5 * s), sub, font=f2, fill=col("cream", a2 * 0.9), anchor="ra" if right else "la")


# ---------------------------------------------------------------- one caption line, bottom centre
def el_caption(c, e):
    a = env(c.t, e, 0.4, 0.4)
    if a <= 0:
        return
    s, W, H = c.s, c.W * SS, c.H * SS
    y = (e.get("y", 40) * s) if e.get("top") else H - e.get("y", 34) * s
    f = font(F_LABEL, e.get("size", 20) * s)
    text = e.get("text", "")
    caps = e.get("caps", False)
    if caps:
        text = text.upper()
    tw = spaced(c.d, (0, 0), text, f, None, track=(1.2 * s if caps else 0))
    plate(c, (W / 2 - tw / 2 - 80 * s, y - 30 * s, W / 2 + tw / 2 + 80 * s, y + 14 * s), a, "m")
    spaced(c.d, (W / 2, y), text, f, col(e.get("color", "cream"), a), "ms", track=(1.2 * s if caps else 0))
    rl = 22 * s * ease((c.t - e.get("t0", 0)) / 0.6)
    yy = y - 6 * s
    for sgn in (-1, 1):
        xa = W / 2 + sgn * (tw / 2 + 10 * s)
        c.d.line([(xa, yy), (xa + sgn * rl, yy)], fill=col("gold", a * 0.9), width=max(1, int(1.2 * s)))


# ---------------------------------------------------------------- big title (Ditty) + sub line
def el_title(c, e):
    a = env(c.t, e, 0.8, 0.6)
    if a <= 0:
        return
    s, W, H = c.s, c.W * SS, c.H * SS
    text = e.get("text", "")
    ditty_ok = all(ch.isalpha() or ch == " " for ch in text)
    ft = font(F_TITLE if ditty_ok else F_LABEL, e.get("size", 62) * s)
    y = e.get("y", 0.40) * H
    dur = max(0.1, e.get("t1", c.t + 1) - e.get("t0", 0))
    tr = (1.0 + 2.0 * ease((c.t - e.get("t0", 0)) / dur)) * s          # slow tracking widen
    tw = spaced(c.d, (0, 0), text, ft, None, track=tr)
    plate(c, (W / 2 - tw / 2 - 120 * s, y - 70 * s, W / 2 + tw / 2 + 120 * s, y + 46 * s), a * 0.8, "m")
    spaced(c.d, (W / 2, y), text, ft, col("cream", a), "ms", track=tr)
    if e.get("sub"):
        a2 = a * ease((c.t - e.get("t0", 0) - 0.5) / 0.6)
        fs = font(F_LABEL, e.get("sub_size", 18) * s)
        sw = spaced(c.d, (0, 0), e["sub"], fs, None, track=1.0 * s)
        yy = y + 24 * s
        spaced(c.d, (W / 2, yy), e["sub"], fs, col("gold", a2), "mm", track=1.0 * s)
        rl = 30 * s * a2
        for sgn in (-1, 1):
            xa = W / 2 + sgn * (sw / 2 + 10 * s)
            c.d.line([(xa, yy), (xa + sgn * rl, yy)], fill=col("gold", a2 * 0.8), width=max(1, int(1.2 * s)))


# ---------------------------------------------------------------- name tag pinned to a 3D point
def _lerp_keys(keys, t):
    if t <= keys[0][0]:
        return keys[0][1:]
    for k0, k1 in zip(keys, keys[1:]):
        if t <= k1[0]:
            u = (t - k0[0]) / max(1e-9, k1[0] - k0[0])
            return [a + (b - a) * u for a, b in zip(k0[1:], k1[1:])]
    return keys[-1][1:]


def tag_anchor(c, e):
    """Screen point (px at 1x) of the tag's anchor, or None when off-screen / behind the camera / no camera."""
    if "screen" in e:
        u, v = e["screen"]
        return u * c.W, v * c.H
    if c.cam is None:
        return None
    if "obj" in e:
        p = hudcam.point(c.cam, e["obj"])
        if p is None:
            return None
    elif "world_keys" in e:
        p = _lerp_keys(e["world_keys"], c.t)
    else:
        p = e["world"]
    off = e.get("offset", (0, 0, 0))
    p = (p[0] + off[0], p[1] + off[1], p[2] + off[2])
    (x, y), depth = hudcam.project(c.cam, p, (c.W, c.H))
    if depth <= 0 or not (-0.05 * c.W < x < 1.05 * c.W and -0.05 * c.H < y < 1.05 * c.H):
        return None
    return x, y


def el_tag(c, e):
    a = env(c.t, e, 0.45, 0.35)
    if a <= 0:
        return
    P = tag_anchor(c, e)
    if P is None:
        return
    s = c.s
    px, py = P[0] * SS, P[1] * SS
    W, H = c.W * SS, c.H * SS
    name, sub = e.get("name", ""), e.get("sub", "")
    fn, fsb = font(F_LABEL, e.get("size", 19) * s), font(F_LABEL, 13 * s)
    tw = max(c.d.textlength(name, font=fn), c.d.textlength(sub, font=fsb) if sub else 0)
    L = e.get("len", 34) * s
    lean = e.get("lean", None)
    if lean is None:
        lean = 14 if px < W * 0.62 else -14
    lean *= s
    up = e.get("dir", "auto")
    up = (py - L - 34 * s > 0) if up == "auto" else (up == "up")
    kx, ky = px + lean, py - L if up else py + L
    shelf = tw + 8 * s
    sx1 = kx + shelf if lean >= 0 else kx - shelf
    if sx1 > W - 8 * s or sx1 < 8 * s:                      # flip the shelf if it would leave the frame
        lean = -lean; kx = px + lean; sx1 = kx + shelf if lean >= 0 else kx - shelf
    p = ease((c.t - e.get("t0", 0)) / e.get("fade_in", 0.45))
    lw = max(1, int(1.3 * s))
    ink = col(e.get("line", "cream"), a * 0.95)
    # leader (draws in from the dot), then the shelf
    f1 = min(1.0, p * 2)
    segs = [[(px, py), (px + (kx - px) * f1, py + (ky - py) * f1)]]
    if p > 0.5:
        f2 = (p - 0.5) * 2
        segs.append([(kx, ky), (kx + (sx1 - kx) * f2, ky)])
    for sg in segs:
        c.d.line(sg, fill=col("dark", a * 0.35), width=lw + max(1, int(1.6 * s)))
    for sg in segs:
        c.d.line(sg, fill=ink, width=lw)
    # the dot
    r = e.get("dot", 2.8) * s
    c.d.ellipse([px - r - 1.3 * s, py - r - 1.3 * s, px + r + 1.3 * s, py + r + 1.3 * s], fill=col("dark", a * 0.8))
    c.d.ellipse([px - r, py - r, px + r, py + r], fill=col(e.get("color", "cream"), a))
    # text sits on the shelf (above it); sub below it
    ta = a * ease((c.t - e.get("t0", 0) - 0.2) / 0.35)
    tx = kx + 4 * s if lean >= 0 else kx - 4 * s
    anc = "l" if lean >= 0 else "r"
    halo = dict(stroke_width=max(1, int(1.1 * s)), stroke_fill=col("dark", ta * 0.5))
    c.d.text((tx, ky - 3 * s), name, font=fn, fill=col(e.get("text_color", "cream"), ta), anchor=anc + "s", **halo)
    if sub:
        c.d.text((tx, ky + 3 * s), sub, font=fsb, fill=col("gold", ta * 0.95), anchor=anc + "a", **halo)


# ---------------------------------------------------------------- animated counter with label (+ optional bar)
def counter_value(e, t):
    v0, v1 = float(e["from"]), float(e["to"])
    ra, rb = e.get("run", [e.get("t0", 0) + 0.4, e.get("t1", 0) - 0.8])
    u = (t - ra) / max(1e-6, rb - ra)
    u = min(1.0, max(0.0, u))
    if e.get("ease", "inout") == "out":
        u = 1 - (1 - u) ** 3
    else:
        u = ease(u)
    if e.get("mode", "log") == "log" and v0 > 0 and v1 > 0:
        v = math.exp(math.log(v0) + (math.log(v1) - math.log(v0)) * u)
    else:
        v = v0 + (v1 - v0) * u
    return v, u


def fmt_count(e, v, u):
    n = int(round(v))
    q = e.get("round", 0)                                    # round to a step while counting (e.g. 10)
    if q and u < 1:
        n = int(round(v / q) * q)
    s = f"{n:,}"
    if u >= 1 and e.get("approx_end"):
        s = "~" + s
    return e.get("prefix", "") + s + e.get("suffix", "")


def tabular(d, xy, text, fnt, fill, anchor="r"):
    """Digits in fixed-width cells so a running counter doesn't jitter. anchor l/r; baseline y."""
    dw = max(d.textlength(ch, font=fnt) for ch in "0123456789")
    ws = [dw if ch.isdigit() else d.textlength(ch, font=fnt) for ch in text]
    x = xy[0] - (sum(ws) if anchor == "r" else (sum(ws) / 2 if anchor == "m" else 0))
    if fill is not None:
        for ch, w in zip(text, ws):
            d.text((x + w / 2, xy[1]), ch, font=fnt, fill=fill, anchor="ms"); x += w
    return sum(ws)


def el_counter(c, e):
    a = env(c.t, e, 0.4, 0.5)
    if a <= 0:
        return
    s, W, H = c.s, c.W * SS, c.H * SS
    v, u = counter_value(e, c.t)
    text = fmt_count(e, v, u)
    label = e.get("label_end") if (u >= 1 and e.get("label_end")) else e.get("label", "")
    fl, fnum, fnote = font(F_LABEL, 15 * s), font(F_NUM, e.get("size", 40) * s, 780), font(F_LABEL, 13 * s)
    pos = e.get("pos", "br")
    m = 22 * s
    bw = e.get("bar_w", 150) * s
    nw = tabular(c.d, (0, 0), text, fnum, None)
    lw = spaced(c.d, (0, 0), label.upper(), fl, None, track=1.2 * s)
    bw = max(bw, nw, lw)
    h = 15 * s + 44 * s + (12 * s if e.get("bar") else 0) + (16 * s if e.get("note") else 0)
    if isinstance(pos, (list, tuple)):
        cx, cy = pos[0] * W, pos[1] * H; anc = "m"
        x0, y0 = cx - bw / 2, cy - h / 2
    else:
        anc = "r" if pos[1] == "r" else ("l" if pos[1] == "l" else "m")
        x0 = W - m - bw if anc == "r" else (m if anc == "l" else W / 2 - bw / 2)
        y0 = H - m - h if pos[0] == "b" else m
    y0 += (1 - ease((c.t - e.get("t0", 0)) / 0.5)) * 6 * s
    ax = {"r": x0 + bw, "l": x0, "m": x0 + bw / 2}[anc]
    plate(c, (x0 - 60 * s, y0 - 14 * s, x0 + bw + 60 * s, y0 + h + 10 * s), a,
          {"r": "r", "l": "l", "m": "m"}[anc])
    spaced(c.d, (ax, y0 + 12 * s), label.upper(), fl, col("cream", a * 0.9), anc + "s", track=1.2 * s)
    c.d.line([(x0 if anc != "r" else x0 + bw - lw, y0 + 17 * s), (x0 + lw if anc == "l" else (x0 + bw if anc == "r" else x0 + bw / 2 + lw / 2), y0 + 17 * s)],
             fill=col("gold", a * 0.8), width=max(1, int(1.1 * s)))
    ncol = e.get("color", "cream")
    if u >= 1 and e.get("color_end"):
        ncol = e["color_end"]
    tabular(c.d, (ax, y0 + 56 * s), text, fnum, col(ncol, a), anc)
    yb = y0 + 66 * s
    if e.get("bar"):
        frac = max(0.0, min(1.0, v / max(float(e["from"]), float(e["to"]))))
        c.d.rectangle([x0, yb, x0 + bw, yb + 3 * s], fill=col("cream", a * 0.18))
        c.d.rectangle([x0, yb, x0 + bw * frac, yb + 3 * s], fill=col(e.get("bar_color", "red"), a * 0.95))
        yb += 12 * s
    if e.get("note"):
        na = a * (ease((c.t - e.get("note_t", e.get("t0", 0))) / 0.4))
        c.d.text((ax, yb + 2 * s), e["note"], font=fnote, fill=col("gold", na), anchor=anc + "a")


# ---------------------------------------------------------------- map (full frame or inset card)
def _map_spec(e):
    sp = e.get("spec", {})
    if isinstance(sp, str):
        sp = {"preset": sp}
    base = dict(maps.PRESETS.get(sp.get("preset", ""), {}))
    base.update({k: v for k, v in sp.items() if k != "preset"})
    return base


def el_map(c, e, frame):
    a = env(c.t, e, 0.5, 0.5)
    if a <= 0:
        return frame
    tl = c.t - e.get("t0", 0) + e.get("map_t0", 0)
    spec = _map_spec(e)
    if e.get("mode", "full") == "full":
        m = maps.render(c.W, c.H, tl, spec)
        return Image.blend(frame.convert("RGBA"), m, a) if a < 1 else m
    u, v, w, h = e.get("rect", [0.03, 0.50, 0.34, 0.44])
    W, H = c.W, c.H
    mw, mh = int(w * W), int(h * H)
    spec.setdefault("compass", False); spec.setdefault("scale_bar", False)
    spec.setdefault("ui_scale", max(1.0, 340.0 / mh))       # labels ~11 px tall in the card at any card size
    m = maps.render(mw * 2, mh * 2, tl, spec).resize((mw, mh), Image.LANCZOS)   # 2x: legible text in a small card
    card = Image.new("RGBA", (mw + 6, mh + 6), col("dark", 1.0))
    card.paste(m, (3, 3))
    dd = ImageDraw.Draw(card)
    dd.rectangle([1, 1, mw + 4, mh + 4], outline=col("gold", 0.85), width=1)
    card.putalpha(Image.eval(card.getchannel("A"), lambda q: int(q * a)))
    x, y = int(u * W), int(v * H + (1 - ease((c.t - e.get("t0", 0)) / 0.5)) * 8)
    out = frame.convert("RGBA")
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    sa = Image.new("L", out.size, 0)
    ImageDraw.Draw(sa).rectangle([x + 2, y + 3, x + mw + 8, y + mh + 9], fill=int(150 * a))
    sh.putalpha(sa.filter(ImageFilter.GaussianBlur(4)))
    out.alpha_composite(sh)
    out.alpha_composite(card, (x, y))
    return out


# ---------------------------------------------------------------- glitch cut (Grisha's injection) and fades
def glitch(img, k, seed, s480=1.0, flash=0.0):
    """k in 0..1. RGB split, displaced horizontal slices, scanlines, a few blocks; flash = teal-white lift at the cut."""
    if k <= 0 and flash <= 0:
        return img
    A = np.asarray(img.convert("RGB")).astype(np.float32)
    H, W, _ = A.shape
    rng = np.random.default_rng(seed)
    dx = int(round(5 * k * s480))
    if dx:
        A[..., 0] = np.roll(A[..., 0], dx, axis=1)
        A[..., 2] = np.roll(A[..., 2], -dx, axis=1)
    y = 0
    while y < H:
        hgt = int(rng.integers(2, max(3, int(22 * s480))))
        if rng.random() < 0.3 * k:
            A[y:y + hgt] = np.roll(A[y:y + hgt], int(rng.normal(0, 22 * k * s480)), axis=1)
        y += hgt
    for _ in range(int(4 * k * k)):
        bw, bh = int(rng.integers(8, 60) * s480), int(rng.integers(3, 16) * s480)
        bx, by = int(rng.integers(0, max(1, W - bw))), int(rng.integers(0, max(1, H - bh)))
        A[by:by + bh, bx:bx + bw] = 255 - A[by:by + bh, bx:bx + bw] * 0.8
    A[::2] *= 1 - 0.18 * k
    if k > 0:
        g = A.mean(axis=2, keepdims=True)
        A = A * (1 - 0.25 * k) + g * 0.25 * k
    if flash > 0:
        A = A * (1 - flash) + np.array([205, 245, 235]) * flash
    return Image.fromarray(np.clip(A, 0, 255).astype(np.uint8), "RGB")


def el_glitch(c, e, frame, fps):
    tc, dur = e["t"], e.get("dur", 0.6)
    k = max(0.0, 1 - abs(c.t - tc) / (dur / 2)) ** 1.3 * e.get("strength", 1.0)
    flash = e.get("flash", 0.45) * max(0.0, 1 - abs(c.t - tc) * fps / 1.5)
    if k <= 0 and flash <= 0:
        return frame
    return glitch(frame, k, seed=c.i * 7919 + 13, s480=c.H / 480.0, flash=flash)


def el_fade(c, e, frame):
    a = 0.0
    if "in" in e:
        t0, t1 = e["in"]; a = max(a, 1 - ease((c.t - t0) / max(1e-6, t1 - t0)))
    if "out" in e:
        t0, t1 = e["out"]; a = max(a, ease((c.t - t0) / max(1e-6, t1 - t0)))
    if a <= 0:
        return frame
    return Image.blend(frame.convert("RGB"), Image.new("RGB", frame.size, COL.get(e.get("color", "dark"), (0, 0, 0))[:3]), a)


ELEMENTS = {"place": el_place, "caption": el_caption, "title": el_title, "tag": el_tag, "counter": el_counter}


# ---------------------------------------------------------------- compositor
def _flatten(c, frame):
    out = frame.convert("RGBA")
    und = c.under.convert("RGBa").resize((c.W, c.H), Image.LANCZOS).convert("RGBA")
    out.alpha_composite(und)
    ink = c.ink.convert("RGBa").resize((c.W, c.H), Image.LANCZOS).convert("RGBA")
    sh = Image.new("RGBA", ink.size, COL["dark"] + (0,))
    sh.putalpha(ink.getchannel("A").filter(ImageFilter.GaussianBlur(max(1.0, c.H / 400))).point(lambda q: int(min(255, q * 0.85))))
    out.alpha_composite(sh, (0, max(1, c.H // 480)))
    out.alpha_composite(ink)
    return out


def compose(tl, frame, index, t=None, cam=None):
    """Composite every active track onto one frame. `t` defaults to t_offset + (index - first) / fps;
    `cam` defaults to hudcam.load(tl['cams'], index)."""
    fps = tl.get("fps", 15)
    if t is None:
        t = tl.get("t_offset", 0.0) + (index - tl.get("first", 0)) / fps
    if cam is None and tl.get("cams"):
        cam = hudcam.load(tl["cams"], index)
    W, H = frame.size
    c = Ctx(W, H, t, index, cam)
    tracks = tl.get("tracks", [])
    for e in tracks:
        if e["type"] == "map" and e.get("mode", "full") == "full":
            frame = el_map(c, e, frame)
    for e in tracks:
        if e["type"] == "map" and e.get("mode", "full") != "full":
            frame = el_map(c, e, frame)
        elif e["type"] in ELEMENTS:
            ELEMENTS[e["type"]](c, e)
    frame = _flatten(c, frame).convert("RGB")
    for e in tracks:
        if e["type"] == "glitch":
            frame = el_glitch(c, e, frame, fps)
    for e in tracks:
        if e["type"] == "fade":
            frame = el_fade(c, e, frame)
    return frame


def load(path_or_dict):
    tl = dict(path_or_dict) if isinstance(path_or_dict, dict) else json.load(open(path_or_dict, encoding="utf8"))
    if tl.get("frames") and "cams" not in tl:
        tl["cams"] = os.path.dirname(tl["frames"])
    return tl


def frame_list(tl):
    """[(index, path or None)] for the segment window."""
    fr = tl.get("frames")
    first = tl.get("first", 0)
    if not fr:
        n = int(round(tl.get("duration", 5) * tl.get("fps", 15)))
        return [(first + k, None) for k in range(n)]
    if "%" in fr:
        out, i = [], first
        last = tl.get("last")
        while (last is None or i <= last) and os.path.exists(fr % i):
            out.append((i, fr % i)); i += 1
        return out
    files = sorted(glob.glob(fr))
    out = []
    for p in files:
        m = re.search(r"(\d+)(?=\.\w+$)", p)
        i = int(m.group(1)) if m else len(out)
        if i >= first and (tl.get("last") is None or i <= tl["last"]):
            out.append((i, p))
    return out


def render(tl, only=None, verbose=True):
    tl = load(tl)
    out = tl["out"]
    os.makedirs(out, exist_ok=True)
    size = tuple(tl.get("size", (854, 480)))
    pre = tl.get("prefix", "gfx")
    frames = frame_list(tl)
    for k, (i, p) in enumerate(frames):
        if only is not None and i not in only:
            continue
        img = Image.open(p).convert("RGB") if p else Image.new("RGB", size, (0, 0, 0))
        compose(tl, img, i).save(os.path.join(out, f"{pre}_{i - tl.get('first', 0):05d}.png"))
        if verbose and k % 15 == 0:
            print(f"[hud2] {k + 1}/{len(frames)}", flush=True)
    if tl.get("mp4") and only is None:
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-framerate", str(tl.get("fps", 15)),
                        "-i", os.path.join(out, f"{pre}_%05d.png"), "-c:v", "libx264", "-crf", "26", "-pix_fmt", "yuv420p",
                        tl["mp4"]], check=True)
        print("[hud2] mp4:", tl["mp4"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("timeline")
    ap.add_argument("--only", default="")
    ap.add_argument("--still", nargs=2, metavar=("IN", "OUT"))
    ap.add_argument("--index", type=int, default=0)
    ap.add_argument("--t", type=float, default=None)
    a = ap.parse_args()
    tl = load(a.timeline)
    if a.still:
        compose(tl, Image.open(a.still[0]).convert("RGB"), a.index, a.t).save(a.still[1])
    else:
        render(tl, only={int(x) for x in a.only.split(",")} if a.only else None)
