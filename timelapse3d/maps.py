"""Stylised 2D island map for the EP1 data graphics (title shot 1, territory loss 7, the 250,000 march 10, inserts).

Used as SMALL INSETS over the running 3D frames (hud2 map mode "inset"); full-frame use is kept but UNUSED
(user 17:41: one continuous camera take, graphics never replace the 3D shot). Pure numpy + PIL, no Blender, no GPU. World units are km, origin = the walls' centre (Mitras), +y = north.
Everything is an analytic field (coast, wall rings with their four district bulges, lost territory), so any view
(pan / zoom) renders crisp at any size; text and routes are drawn on a 2x supersampled PIL layer.

    import maps
    img = maps.render(854, 480, t, maps.TITLE)          # PIL RGBA, opaque
    python maps.py title out_dir [--fps 15]              # quick preview frames of a preset

A spec is a dict (all keys optional):
    view:    [[t, cx_km, cy_km, height_km], ...]   eased camera (log zoom); default whole island
    walls:   {"maria": [t_start, dur], "rose": [...], "sina": [...]}  ring draw-in (sweeps from the south both ways);
             a wall missing from the dict is drawn from t=-inf (always on); {"maria": null} hides it
    wall_labels: t               fade-in time of "WALL MARIA / r 480 km" etc. (None = off)
    districts: {"Shiganshina": t, "Trost": t, ...}   marker + name fade-in times (see DISTRICTS)
    lost:    [t0, t1]            Wall Maria belt turns grey, sweeping north from Shiganshina between t0 and t1
    route:   {"pts": [[x, y], ...], "t": [t0, t1], "color": "red"|"ink"|"gold", "dash": bool,
              "losses": n (red dots left behind), "back": {"pts": [...], "t": [t0, t1]}}  (also a list of routes)
    compass: true, scale_bar: true, grid: true, vignette: true, island_label: t (or None), ui_scale: 1.0 (text/marker size)
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_BIG = os.path.join(HERE, "fonts", "ShareTech-Regular.ttf")              # inset labels: Share Tech + dark stroke (user 17:49)
FONT_SMALL = os.path.join(HERE, "fonts", "ShareTech-Regular.ttf")             # districts, radii, scale bar

# ---------------------------------------------------------------- canon geometry (km)
WALLS = {"maria": 480.0, "rose": 380.0, "sina": 250.0}
WALL_NAMES = {"maria": "WALL MARIA", "rose": "WALL ROSE", "sina": "WALL SINA"}
BULGE = 22.0                      # district salient radius (exaggerated so it reads at island scale)
DIRS = {"S": (0, -1), "E": (1, 0), "N": (0, 1), "W": (-1, 0)}
# district name -> (wall, side). Shiganshina / Trost per the plan; others for later inserts.
DISTRICTS = {
    "Shiganshina": ("maria", "S"),
    "Trost": ("rose", "S"), "Karanes": ("rose", "E"), "Krolva": ("rose", "W"),
    "Ehrmich": ("sina", "S"), "Stohess": ("sina", "E"), "Yalkell": ("sina", "W"),
}
CAPITAL = ("Mitras", (0.0, 0.0))

# ---------------------------------------------------------------- palette (0..1 RGB): dark parchment, ink, cream walls
SEA = np.array([0.085, 0.105, 0.115])
SEA_LINE = np.array([0.20, 0.23, 0.23])
LAND = np.array([0.50, 0.425, 0.31])
LAND_IN = np.array([0.56, 0.48, 0.345])     # inside Wall Maria: a touch warmer / lighter (settled land)
LOST = np.array([0.38, 0.375, 0.36])
INK = np.array([0.13, 0.10, 0.075])
WALL = np.array([0.93, 0.89, 0.80])
RGB = {"ink": (238, 228, 204), "red": (186, 48, 36), "gold": (214, 176, 102), "dark": (30, 23, 17), "cream": (238, 228, 204)}


def district_xy(name):
    wall, side = DISTRICTS[name]
    d = DIRS[side]
    R = WALLS[wall] + BULGE * 0.55
    return (d[0] * R, d[1] * R)


# ---------------------------------------------------------------- procedural textures (fixed seed, world-anchored)
_rng = np.random.default_rng(845)


def _fbm_tex(n=256, octaves=5):
    tex = np.zeros((n, n))
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        k = 4 * 2 ** o
        g = _rng.random((k + 1, k + 1))
        g[-1, :] = g[0, :]; g[:, -1] = g[:, 0]
        xs = np.linspace(0, k, n, endpoint=False)
        i0 = xs.astype(int); f = xs - i0; f = f * f * (3 - 2 * f)
        a = g[i0][:, i0] * (1 - f)[None, :] + g[i0][:, i0 + 1] * f[None, :]
        b = g[i0 + 1][:, i0] * (1 - f)[None, :] + g[i0 + 1][:, i0 + 1] * f[None, :]
        tex += amp * (a * (1 - f)[:, None] + b * f[:, None]); tot += amp; amp *= 0.55
    tex /= tot
    return (tex - tex.min()) / (tex.max() - tex.min())


TEX = _fbm_tex()


def _sample(tex, X, Y, scale):
    n = tex.shape[0]
    u = (X / scale) % 1.0 * n; v = (Y / scale) % 1.0 * n
    i, j = u.astype(int) % n, v.astype(int) % n
    fu, fv = u - np.floor(u), v - np.floor(v)
    i1, j1 = (i + 1) % n, (j + 1) % n
    return (tex[j, i] * (1 - fu) + tex[j, i1] * fu) * (1 - fv) + (tex[j1, i] * (1 - fu) + tex[j1, i1] * fu) * fv


# island coast: radius as a function of angle (harmonics, stretched north / east like the canon island)
_H = [(2, 34, 0.7), (3, 26, 2.1), (5, 16, 4.0), (7, 10, 1.3), (11, 6, 5.5), (17, 4, 0.4), (23, 2.5, 2.9)]


def coast_r(th):
    r = 700.0 + 60 * np.sin(th) + 30 * np.cos(th)
    for k, a, ph in _H:
        r = r + a * np.sin(k * th + ph)
    return r


def _smooth(e0, e1, x):
    u = np.clip((x - e0) / (e1 - e0), 0, 1)
    return u * u * (3 - 2 * u)


def wall_sdf(X, Y, R):
    """Signed distance (km) to a wall ring with its four semicircular district salients (union of disks)."""
    d = np.hypot(X, Y) - R
    for dx, dy in DIRS.values():
        d = np.minimum(d, np.hypot(X - dx * R, Y - dy * R) - BULGE)
    return d


def _ease(u):
    u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)


def view_at(spec, t):
    keys = spec.get("view") or [[0, 0, 40, 1650]]
    if t <= keys[0][0]:
        return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            u = _ease((t - a[0]) / max(1e-6, b[0] - a[0]))
            return (a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u, math.exp(math.log(a[3]) + (math.log(b[3]) - math.log(a[3])) * u))
    return keys[-1][1:]


def _fade(t, t0, dur=0.6):
    if t0 is None:
        return 0.0
    return _ease((t - t0) / dur)


_FONTS = {}


def _font(path, size, wght=None):
    k = (path, size, wght)
    if k not in _FONTS:
        f = ImageFont.truetype(path, size)
        if wght is not None:
            try:
                f.set_variation_by_axes([wght])
            except Exception:
                pass
        _FONTS[k] = f
    return _FONTS[k]


def _spaced(d, xy, text, fnt, fill, anchor="mm", track=0.0):
    """Letter-spaced text (PIL has no tracking): draws glyph by glyph, centred on xy for anchor 'mm'/'ms'."""
    if not track:
        d.text(xy, text, font=fnt, fill=fill, anchor=anchor); return
    widths = [d.textlength(c, font=fnt) for c in text]
    total = sum(widths) + track * (len(text) - 1)
    x = xy[0] - (total / 2 if anchor[0] == "m" else (total if anchor[0] == "r" else 0))
    for c, w in zip(text, widths):
        d.text((x, xy[1]), c, font=fnt, fill=fill, anchor="l" + anchor[1]); x += w + track


# ---------------------------------------------------------------- render
def render(W, H, t, spec=None):
    spec = spec or {}
    cx, cy, hk = view_at(spec, t)
    kpp = hk / H                                     # km per pixel
    xs = cx + (np.arange(W) + 0.5 - W / 2) * kpp
    ys = cy - (np.arange(H) + 0.5 - H / 2) * kpp
    X, Y = np.meshgrid(xs, ys)
    th = np.arctan2(Y, X)
    rr = np.hypot(X, Y)
    aa = kpp                                         # 1 px in km, antialias width

    # sea with coastal ripple lines (screen-constant spacing)
    cs = (rr - coast_r(th)) / kpp                    # px outside the coast (+ = sea)
    img = np.broadcast_to(SEA, (H, W, 3)).copy()
    ripple = (np.abs(((cs + 3.5) % 7.0) - 3.5) < 0.6) * (cs > 4) * np.clip(1 - cs / 40, 0, 1)
    img += (SEA_LINE - SEA) * ripple[..., None] * 0.8
    img *= (0.92 + 0.12 * _sample(TEX, X, Y, 900.0))[..., None]

    # land: parchment, world-anchored grain, warmer inside Wall Maria
    land = _smooth(0.5, -0.5, cs)
    grain = _sample(TEX, X, Y, 160.0) * 0.6 + _sample(TEX, X + 37, Y - 11, 41.0) * 0.4
    maria = wall_sdf(X, Y, WALLS["maria"])
    inside_m = _smooth(aa, -aa, maria)
    lc = LAND + (LAND_IN - LAND) * inside_m[..., None]
    lc = lc * (0.80 + 0.32 * grain)[..., None]
    # faint inland shading toward the coast
    lc *= (1 - 0.18 * _smooth(-60 / kpp, 0, cs))[..., None]
    img = img * (1 - land[..., None]) + lc * land[..., None]

    # lost territory: inside Maria, outside Rose, swept north from Shiganshina
    lost = spec.get("lost")
    if lost:
        u = _ease((t - lost[0]) / max(1e-6, lost[1] - lost[0]))
        if u > 0:
            rose = wall_sdf(X, Y, WALLS["rose"])
            belt = _smooth(aa, -aa, maria) * _smooth(-aa, aa, rose)
            sx, sy = district_xy("Shiganshina")
            dist = np.hypot(X - sx, Y - sy)
            front = u * 1050.0                           # farthest belt point from Shiganshina ~ 960 km
            m = belt * _smooth(front + 6 * kpp, front - 6 * kpp, dist)
            hatch = (np.abs((((X - Y) / kpp) % 9.0) - 4.5) < 0.7) * 0.12
            g = LOST * (0.88 + 0.2 * grain)[..., None] * (1 - hatch)[..., None]
            img = img * (1 - m[..., None]) + g * m[..., None]
            # a thin red front line while it advances
            if u < 1:
                edge = np.exp(-((dist - front) / (2.0 * kpp)) ** 2) * belt * (1 - u) ** 0.3
                img = img * (1 - 0.7 * edge[..., None]) + np.array([0.6, 0.16, 0.12]) * 0.7 * edge[..., None]

    # coast ink line
    coast_line = np.exp(-(cs / 0.9) ** 2)
    img = img * (1 - 0.85 * coast_line[..., None]) + INK * 0.85 * coast_line[..., None]

    # faint graticule
    if spec.get("grid", True):
        step = 100.0
        gx = np.abs(((X + step / 2) % step) - step / 2) / kpp
        gy = np.abs(((Y + step / 2) % step) - step / 2) / kpp
        gl = (np.exp(-(gx / 0.5) ** 2) + np.exp(-(gy / 0.5) ** 2)).clip(0, 1) * 0.06
        img = img * (1 - gl[..., None]) + INK * gl[..., None]

    # the three walls: dark outline + cream stroke, drawn in from the south both ways
    walls = spec.get("walls", {})
    for key, R in WALLS.items():
        if key in walls and walls[key] is None:
            continue
        tw = walls.get(key)
        prog = 1.0 if tw is None else _ease((t - tw[0]) / max(1e-6, tw[1]))
        if prog <= 0:
            continue
        d = wall_sdf(X, Y, R) / kpp                    # px
        ang = np.abs(np.angle(np.exp(1j * (th + math.pi / 2))))   # 0 at south, pi at north
        vis = _smooth(prog * math.pi + 0.02, prog * math.pi - 0.02, ang) if prog < 1 else 1.0
        wpx = max(1.4, min(3.2, 2.0 * 1500 / hk))      # thicker when zoomed in
        outline = _smooth(wpx / 2 + 1.6, wpx / 2 + 0.6, np.abs(d)) * vis
        stroke = _smooth(wpx / 2 + 0.5, wpx / 2 - 0.5, np.abs(d)) * vis
        img = img * (1 - 0.75 * outline[..., None]) + INK * 0.75 * outline[..., None]
        img = img * (1 - stroke[..., None]) + WALL * stroke[..., None]
        # soft glow on the stroke head while drawing
        if prog < 1:
            head = np.exp(-((ang - prog * math.pi) * R / kpp / 6.0) ** 2) * _smooth(8, 0, np.abs(d))
            img = img + np.array([1.0, 0.85, 0.55]) * 0.5 * head[..., None]

    # vignette + screen grain
    if spec.get("vignette", True):
        py, px = np.mgrid[0:H, 0:W]
        v = ((px / W - 0.5) ** 2 * 1.2 + (py / H - 0.5) ** 2 * 1.6)
        img *= (1 - 0.55 * np.clip(v, 0, 1))[..., None]
    img = np.clip(img, 0, 1)
    base = Image.fromarray((img * 255).astype(np.uint8), "RGB").convert("RGBA")

    # ---------------------------------------------------------------- vector layer (2x supersampled)
    SS = 2
    s = H / 480.0 * SS * spec.get("ui_scale", 1.0)    # 1 unit = 1 px at 480p (ui_scale: bigger text in insets)
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)

    def to_px(x, y):
        return ((x - cx) / kpp + W / 2) * SS, (H / 2 - (y - cy) / kpp) * SS

    def col(name, a):
        c = RGB.get(name, name) if isinstance(name, str) else name
        return (c[0], c[1], c[2], int(255 * max(0.0, min(1.0, a))))

    # routes
    routes = spec.get("route")
    routes = routes if isinstance(routes, list) else ([routes] if routes else [])
    for r in routes:
        _draw_route(d, r, t, to_px, s, col)
        if r.get("back"):
            b = dict(r["back"]); b.setdefault("color", "ink"); b.setdefault("dash", True); b.setdefault("width", 1.2)
            _draw_route(d, b, t, to_px, s, col)

    # wall labels: lettered along each ring's belt (classic map style), with the canon radius
    if spec.get("wall_labels") is not None:
        mids = {"maria": (WALLS["maria"] + WALLS["rose"] + BULGE) / 2, "rose": (WALLS["rose"] + WALLS["sina"] + BULGE) / 2,
                "sina": WALLS["sina"] - 34.0}
        for i, (key, rm) in enumerate(mids.items()):
            ai = _fade(t, spec["wall_labels"] + 0.25 * i, 0.7)
            if ai <= 0 or (key in walls and walls[key] is None):
                continue
            fs = int(14 * s * min(1.6, max(0.8, 1500 / hk)))
            f1, f2 = _font(FONT_BIG, fs), _font(FONT_SMALL, int(fs * 0.9))
            runs = [(ch, f1, col("cream", ai), 1.4 * s) for ch in WALL_NAMES[key]] + [(" ", f1, None, 0)] +                    [(ch, f2, col((226, 206, 160), ai), 0.4 * s) for ch in f"{int(WALLS[key])} km"]
            ox, oy = to_px(0, 0)
            _arc_text(lay, (ox, oy), rm / kpp * SS, math.radians(spec.get("wall_label_angle", 62)), runs,
                      stroke=(int(1.5 * s), col("dark", ai * 0.55)))

    # districts: dot with dark ring + name
    for name, td in (spec.get("districts") or {}).items():
        a = _fade(t, td, 0.5)
        if a <= 0:
            continue
        if name == CAPITAL[0]:
            wx, wy = CAPITAL[1]
        else:
            wx, wy = district_xy(name)
        x, y = to_px(wx, wy)
        pop = 1 + 0.6 * math.sin(min(1.0, (t - td) / 0.35) * math.pi) * (t - td < 0.35)
        rd = 3.2 * s * pop
        d.ellipse([x - rd - 1.4 * s, y - rd - 1.4 * s, x + rd + 1.4 * s, y + rd + 1.4 * s], fill=col("dark", a * 0.85))
        d.ellipse([x - rd, y - rd, x + rd, y + rd], fill=col("red" if name in ("Shiganshina", "Trost") else "cream", a))
        fs = int(15 * s)
        side = (spec.get("district_side") or {}).get(name, "r")
        if side == "r":
            d.text((x + 8 * s, y + 5 * s), name, font=_font(FONT_SMALL, fs), fill=col("cream", a), anchor="lm", stroke_width=int(1.6 * s), stroke_fill=col("dark", a * 0.6))
        elif side == "l":
            d.text((x - 7 * s, y), name, font=_font(FONT_SMALL, fs), fill=col("cream", a), anchor="rm", stroke_width=int(1.6 * s), stroke_fill=col("dark", a * 0.6))
        else:
            d.text((x, y + 7 * s), name, font=_font(FONT_SMALL, fs), fill=col("cream", a), anchor="mt", stroke_width=int(1.6 * s), stroke_fill=col("dark", a * 0.6))

    # island name in the sea
    if spec.get("island_label") is not None:
        a = _fade(t, spec["island_label"], 1.0) * 0.8
        x, y = to_px(*spec.get("island_label_xy", (-830, -330)))
        _spaced(d, (x, y), "PARADIS", _font(FONT_BIG, int(15 * s)), col((205, 195, 170), a), "mm", track=4 * s)

    if spec.get("compass", True):
        _compass(d, (W * SS - 34 * s, 40 * s), s, col)
    if spec.get("scale_bar", True):
        _scale_bar(d, (22 * s, H * SS - 22 * s), s, kpp / SS, col)

    lay = lay.convert("RGBa").resize((W, H), Image.LANCZOS).convert("RGBA")
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    sh.putalpha(lay.getchannel("A").filter(ImageFilter.GaussianBlur(max(1, H // 320))).point(lambda v: int(v * 0.6)))
    base.alpha_composite(sh, (0, 1))
    base.alpha_composite(lay)
    return base


def _arc_text(lay, centre, radius, ang_mid, runs, stroke=(0, None)):
    """Glyphs centred on angle ang_mid along a circle (reading clockwise over the top), each rotated to the tangent.
    runs = [(char, font, fill, tracking_px)]."""
    d = ImageDraw.Draw(lay)
    widths = [d.textlength(ch, font=f) + tr for ch, f, _, tr in runs]
    total = sum(widths)
    a = ang_mid + total / 2 / radius                      # start angle (larger), walk clockwise
    for (ch, f, fill, tr), w in zip(runs, widths):
        gw = w - tr
        am = a - gw / 2 / radius
        if fill is not None and ch.strip():
            size = int(f.size * 2.2)
            g = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            ImageDraw.Draw(g).text((size / 2, size / 2), ch, font=f, fill=fill, anchor="mm",
                                   stroke_width=stroke[0], stroke_fill=stroke[1])
            g = g.rotate(math.degrees(am) - 90, resample=Image.BICUBIC)
            x = centre[0] + radius * math.cos(am); y = centre[1] - radius * math.sin(am)
            lay.alpha_composite(g, (int(x - size / 2), int(y - size / 2)))
        a -= w / radius


def _polyline_partial(pts, f):
    """First fraction f (by length) of a polyline, plus the head point."""
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    L = sum(seg) * max(0.0, min(1.0, f))
    out = [pts[0]]
    for (a, b), l in zip(zip(pts, pts[1:]), seg):
        if L >= l:
            out.append(b); L -= l
        else:
            k = L / l if l else 0
            out.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)); break
    return out


def _catmull(pts, n=12):
    """Smooth a polyline through its points (Catmull-Rom), so routes read as marched curves, not zigzags."""
    if len(pts) < 3:
        return pts
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            u = k / n
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * u + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u * u
                                     + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u ** 3) for j in range(2)))
    out.append(pts[-1])
    return out


def _draw_route(d, r, t, to_px, s, col):
    t0, t1 = r.get("t", [0, 1])
    f = _ease((t - t0) / max(1e-6, t1 - t0))
    if f <= 0:
        return
    alpha = r.get("alpha", 1.0) * (1 - _ease((t - r["fade_out"]) / 0.6) if r.get("fade_out") else 1.0)
    if alpha <= 0:
        return
    pts = _catmull([tuple(p) for p in r["pts"]])
    part = [to_px(*p) for p in _polyline_partial(pts, f)]
    c = r.get("color", "red")
    w = r.get("width", 2.6) * s
    if r.get("dash"):
        # dashes along the drawn part
        acc = 0.0; on = True; dash = 5 * s
        for a, b in zip(part, part[1:]):
            l = math.dist(a, b)
            p = 0.0
            while p < l:
                step = min(dash - acc, l - p)
                if on:
                    q0 = (a[0] + (b[0] - a[0]) * p / l, a[1] + (b[1] - a[1]) * p / l)
                    q1 = (a[0] + (b[0] - a[0]) * (p + step) / l, a[1] + (b[1] - a[1]) * (p + step) / l)
                    d.line([q0, q1], fill=col(c, alpha), width=max(1, int(w)))
                p += step; acc += step
                if acc >= dash - 1e-6:
                    acc = 0.0; on = not on
    else:
        d.line(part, fill=col("dark", alpha * 0.7), width=int(w + 2.4 * s), joint="curve")
        d.line(part, fill=col(c, alpha), width=max(1, int(w)), joint="curve")
    # losses: small dots left behind along the drawn route (deterministic)
    n = int(r.get("losses", 0))
    if n:
        rng = np.random.default_rng(250)
        fr = rng.random(n); off = rng.normal(0, 5.0, (n, 2))
        for k in range(n):
            if fr[k] < f * 0.98:
                q = _polyline_partial(pts, fr[k])[-1]
                x, y = to_px(*q)
                x += off[k, 0] * s; y += off[k, 1] * s
                rd = 1.1 * s
                d.ellipse([x - rd, y - rd, x + rd, y + rd], fill=col((120, 30, 24), alpha * 0.75))
    # column head marker
    if f < 1 or r.get("keep_head"):
        hx, hy = part[-1]
        rd = 4.0 * s
        d.ellipse([hx - rd - 1.5 * s, hy - rd - 1.5 * s, hx + rd + 1.5 * s, hy + rd + 1.5 * s], fill=col("dark", alpha * 0.8))
        d.ellipse([hx - rd, hy - rd, hx + rd, hy + rd], fill=col(r.get("head_color", "cream"), alpha))


def _compass(d, c, s, col):
    x, y = c; r = 12 * s
    d.polygon([(x, y - r), (x + 3.2 * s, y), (x, y + r * 0.5), (x - 3.2 * s, y)], fill=col("cream", 0.75))
    d.polygon([(x, y - r), (x, y + r * 0.5), (x - 3.2 * s, y)], fill=col((150, 135, 110), 0.75))
    d.text((x, y - r - 2 * s), "N", font=_font(FONT_BIG, int(12 * s)), fill=col("cream", 0.8), anchor="ms")


def _scale_bar(d, p, s, kpp_ss, col):
    x, y = p
    for km in (25, 50, 100, 200, 250, 500):
        if km / kpp_ss >= 50 * s:
            break
    L = km / kpp_ss
    d.line([(x, y), (x + L, y)], fill=col("cream", 0.7), width=max(1, int(1.4 * s)))
    for xx in (x, x + L / 2, x + L):
        d.line([(xx, y - 3 * s), (xx, y)], fill=col("cream", 0.7), width=max(1, int(1.4 * s)))
    d.text((x + L + 5 * s, y), f"{km} km", font=_font(FONT_SMALL, int(12 * s)), fill=col("cream", 0.75), anchor="lm")


# ---------------------------------------------------------------- presets (seconds are local to the map clip)
# shot 1 title map (~8 s): island fades up, the three rings draw in (Maria, Rose, Sina), labels, Shiganshina + Trost,
# then an eased push south onto Shiganshina to hand over to shot 2.
TITLE = {
    "view": [[0, 0, 40, 1650], [4.6, 0, 10, 1350], [8.0, 0, -470, 210]],
    "walls": {"maria": [0.6, 1.3], "rose": [1.2, 1.2], "sina": [1.8, 1.1]},
    "wall_labels": 2.6,
    "districts": {"Shiganshina": 3.6, "Trost": 4.0},
    "island_label": 0.8,
}
# shot 7 insert: Wall Maria lost, the belt turns grey from Shiganshina north
LOSS = {
    "view": [[0, 0, -60, 1150], [3.5, 0, -90, 1100]],
    "districts": {"Shiganshina": 0.0, "Trost": 0.0},
    "lost": [0.6, 3.0],
}
# shot 10 insert: the 250,000 march from Trost into the lost belt; ~100 come back
_MARCH = [[0, -398], [-30, -418], [-55, -446], [-50, -475], [-22, -492], [-6, -496]]
MARCH = {
    "view": [[0, 0, -250, 760], [6.0, -10, -430, 300]],
    "districts": {"Shiganshina": 0.0, "Trost": 0.0},
    "lost": [-10, -9],
    "route": {"pts": _MARCH, "t": [0.8, 4.6], "color": "red", "losses": 70,
              "back": {"pts": _MARCH[::-1][:3], "t": [4.9, 5.9]}},
}
PRESETS = {"title": TITLE, "loss": LOSS, "march": MARCH}

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("preset"); ap.add_argument("out")
    ap.add_argument("--fps", type=float, default=15); ap.add_argument("--dur", type=float, default=8)
    ap.add_argument("--size", default="854x480")
    a = ap.parse_args()
    W, H = map(int, a.size.split("x"))
    os.makedirs(a.out, exist_ok=True)
    for i in range(int(a.dur * a.fps)):
        render(W, H, i / a.fps, PRESETS[a.preset]).convert("RGB").save(os.path.join(a.out, f"map_{i:05d}.png"))
