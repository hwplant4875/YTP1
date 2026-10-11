"""2D motion graphics for the long-form episodes: maps, flows, station light-ups, counters.

Called by assemble.py for visuals {"type": "g2d", "name": ..., "args": {...}} and beat overlays {"overlay": {...}}.
Every graphic gets the narration timing of the beats it covers, so things light up when they are named.
Rendered with PIL + numpy and piped to ffmpeg (mp4, or qtrle mov with alpha for overlays).
"""
import json
import math
import os
import subprocess
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts")
W, H, FPS = 1920, 1080, 30

BG = (12, 12, 13)
INK = (242, 238, 230)
AMBER = (255, 178, 92)
GREY = (150, 148, 142)
ZONE_COL = {"soviet": AMBER, "american": (110, 150, 205), "british": (100, 170, 150), "french": (160, 140, 200)}
ZONE_NAME = {"soviet": "SOVIET", "american": "AMERICAN", "british": "BRITISH", "french": "FRENCH"}


# ---------------------------------------------------------------- helpers

@lru_cache(None)
def font(size, name="YouTubeSans-DarkBlack.otf"):
    return ImageFont.truetype(os.path.join(FONTS, name), int(size))


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ramp(t, a, d=0.5):
    return smooth((t - a) / d) if d > 0 else float(t >= a)


def mix(c1, c2, k):
    return tuple(int(a + (b - a) * k) for a, b in zip(c1, c2))


def text(dr, xy, s, size, fill=INK, name="YouTubeSans-DarkBlack.otf", anchor="mm", stroke=None, alpha=255):
    """Main on-screen text: highlight or white fill with a black outer stroke."""
    stroke = max(3, int(size * 0.07)) if stroke is None else stroke
    if alpha <= 0:
        return
    img = dr._image
    if alpha < 255 and img.mode == "RGB":   # RGB canvases ignore fill alpha: draw on a layer and paste through it
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).text(xy, s, font=font(size, name), fill=(*fill[:3], 255), anchor=anchor,
                                 stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
        lay.putalpha(lay.getchannel("A").point(lambda v: v * alpha // 255))
        img.paste(lay, (0, 0), lay)
        return
    dr.text(xy, s, font=font(size, name), fill=(*fill[:3], alpha), anchor=anchor,
            stroke_width=stroke, stroke_fill=(0, 0, 0, alpha))


def word_time(timing, needle, lag=0.12):
    """When the narrator says `needle` (estimated from its character position in the line)."""
    for b in timing:
        i = b["say"].find(needle)
        if i >= 0:
            return b["say_at"] + b["say_d"] * i / max(len(b["say"]), 1) + lag
    raise KeyError(needle)


def beat_at(timing, k):
    return timing[min(k, len(timing) - 1)]["start"]


class Out:
    def __init__(self, path, ext, alpha=False):
        self.alpha = alpha
        fmt = ["-c:v", "qtrle", "-pix_fmt", "argb", "-f", "mov"] if alpha else \
              ["-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-f", "mp4"]
        self.p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba" if alpha else "rgb24",
                                   "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", *fmt, path], stdin=subprocess.PIPE)

    def write(self, im):
        im = im.convert("RGBA" if self.alpha else "RGB")
        if im.size != (W, H):
            im = im.resize((W, H), Image.LANCZOS)
        self.p.stdin.write(im.tobytes())

    def close(self):
        self.p.stdin.close()
        if self.p.wait():
            raise SystemExit("ffmpeg failed")


STILLS = None   # set to a list of times to render preview stills instead of a clip


def frames(d):
    return STILLS if STILLS is not None else [i / FPS for i in range(max(1, round(d * FPS)))]


def glow(layer, radius=14, strength=1.6):
    """Additive bloom for a light layer (RGBA on black)."""
    b = layer.filter(ImageFilter.GaussianBlur(radius))
    a = np.asarray(layer, np.float32) + np.asarray(b, np.float32) * strength
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), layer.mode)


def add(base, light):
    a = np.asarray(base.convert("RGB"), np.float32) + np.asarray(light.convert("RGB"), np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def panel(img, box, alpha=170, radius=26):
    """Dark translucent backing so text stays readable over a busy map."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle([int(v) for v in box], radius, fill=(8, 8, 9, alpha))
    lay = lay.filter(ImageFilter.GaussianBlur(6))
    img.paste(lay, (0, 0), lay)


def vignette_bg(col=BG, lift=10):
    """Dark backdrop with a soft centre lift and fine paper grain (static)."""
    y, x = np.mgrid[0:H, 0:W]
    r = np.hypot((x - W / 2) / W, (y - H / 2) / H)
    v = np.clip(1 - r * 1.3, 0, 1)[..., None]
    rng = np.random.default_rng(3)
    a = np.array(col, np.float32)[None, None] + v * lift + rng.normal(0, 2.0, (H, W, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------- geography

@lru_cache(None)
def geo():
    return json.load(open(os.path.join(HERE, "data", "geo_zones.json")))


def polys(g):
    """GeoJSON (Multi)Polygon -> list of rings (exterior + holes) as numpy lon/lat arrays."""
    if g["type"] == "Polygon":
        return [[np.array(r) for r in g["coordinates"]]]
    if g["type"] == "MultiPolygon":
        return [[np.array(r) for r in p] for p in g["coordinates"]]
    if g["type"] in ("LineString",):
        return [[np.array(g["coordinates"])]]
    if g["type"] == "MultiLineString":
        return [[np.array(l)] for l in g["coordinates"]]
    if g["type"] == "GeometryCollection":
        return [p for gg in g["geometries"] for p in polys(gg)]
    return []


class Cam:
    """Equirectangular camera: centre lon/lat, pixels per degree of latitude, supersampling factor."""
    def __init__(self, lon, lat, scale, ss=2):
        self.lon, self.lat, self.s, self.ss = lon, lat, scale, ss
        self.k = math.cos(math.radians(52))

    def xy(self, ll):
        ll = np.asarray(ll, float)
        x = (ll[..., 0] - self.lon) * self.k * self.s + W / 2
        y = -(ll[..., 1] - self.lat) * self.s + H / 2
        return np.stack([x, y], -1) * self.ss

    def pt(self, lon, lat):
        x, y = self.xy([lon, lat])
        return float(x) / self.ss, float(y) / self.ss


def lerp_cam(c0, c1, k):
    s = math.exp(math.log(c0[2]) + (math.log(c1[2]) - math.log(c0[2])) * k)
    # keep the zoom feeling linear: move the centre in screen space proportional to the zoom progress
    return Cam(c0[0] + (c1[0] - c0[0]) * k, c0[1] + (c1[1] - c0[1]) * k, s)


def draw_geom(dr, cam, g, fill=None, outline=None, width=2):
    for poly in polys(g):
        for j, ring in enumerate(poly):
            pts = [tuple(p) for p in cam.xy(ring)]
            if len(pts) < 2:
                continue
            if fill is not None and j == 0:
                dr.polygon(pts, fill=fill)
            if fill is not None and j > 0:
                dr.polygon(pts, fill=(0, 0, 0, 0))
            if outline is not None:
                dr.line(pts + ([pts[0]] if fill is not None else []), fill=outline, width=int(width * cam.ss), joint="curve")


def ss_layer(cam):
    return Image.new("RGBA", (W * cam.ss, H * cam.ss), (0, 0, 0, 0))


def down(layer):
    return layer.resize((W, H), Image.LANCZOS)


# subway lines in lon/lat (stations), north to south, for the city-scale maps
U8 = [(13.3733, 52.5571), (13.3814, 52.5523), (13.3883, 52.5487), (13.3929, 52.5421), (13.3964, 52.5379), (13.4015, 52.5297),
      (13.4051, 52.5256), (13.4114, 52.5215), (13.4192, 52.5150), (13.4163, 52.5105), (13.4106, 52.5038), (13.4180, 52.4993),
      (13.4219, 52.4934), (13.4247, 52.4867)]
U6 = [(13.3523, 52.5506), (13.3594, 52.5465), (13.3664, 52.5427), (13.3705, 52.5397), (13.3770, 52.5357), (13.3820, 52.5313),
      (13.3874, 52.5258), (13.3880, 52.5200), (13.3893, 52.5147), (13.3898, 52.5113), (13.3905, 52.5063), (13.3911, 52.4977),
      (13.3878, 52.4935), (13.3858, 52.4855)]
LINE_COL = {"U8": (70, 135, 245), "U6": (170, 115, 235), "S": (50, 200, 105)}


def polyline_len(pts):
    p = np.asarray(pts, float)
    return np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]


def along(pts, u):
    """Point at fraction u along a polyline (screen space)."""
    p = np.asarray(pts, float)
    L = polyline_len(p)
    s = clamp(u) * L[-1]
    i = min(np.searchsorted(L, s, side="right") - 1, len(p) - 2)
    f = (s - L[i]) / max(L[i + 1] - L[i], 1e-9)
    return p[i] + (p[i + 1] - p[i]) * f


def sub_polyline(pts, u):
    p = np.asarray(pts, float)
    L = polyline_len(p)
    s = clamp(u) * L[-1]
    out = [tuple(x) for x, l in zip(p, L) if l <= s]
    out.append(tuple(along(p, u)))
    return out


# ---------------------------------------------------------------- 1. occupation zones -> Berlin sectors

GERMANY_CAM = (10.45, 51.15, 112)
BERLIN_CAM = (13.405, 52.512, 2800)
CITY_CAM = (13.40, 52.522, 6200)


def berlin_layers(dr, cam, t, lit, base_alpha=0.32, labels=None, outline_w=2.0):
    """Four sectors; `lit[sector]` in 0..1 brightens it."""
    g = geo()
    for s in ("american", "british", "french", "soviet"):
        k = lit.get(s, 0)
        a = int(255 * (base_alpha + (0.55 - base_alpha) * k))
        col = mix(mix(ZONE_COL[s], (60, 60, 60), 0.55), ZONE_COL[s], k)
        draw_geom(dr, cam, g["berlin"][s], fill=(*col, a))
    for s in ("american", "british", "french", "soviet"):
        draw_geom(dr, cam, g["berlin"][s], outline=(20, 20, 20, 255), width=outline_w)
    draw_geom(dr, cam, g["berlin_outline"], outline=(200, 196, 188, 200), width=outline_w)


SECTOR_LABEL_AT = {"soviet": (13.52, 52.53), "american": (13.33, 52.44), "british": (13.20, 52.52), "french": (13.30, 52.60)}


def g_zones(args, d, timing, base, out):
    g = geo()
    bg = vignette_bg()
    t_capital = word_time(timing, "capital") - 0.2
    t_four = word_time(timing, "four sectors")
    t_sov = word_time(timing, "Soviets")
    t_us, t_gb, t_fr = word_time(timing, "Americans"), word_time(timing, "British"), word_time(timing, "French")
    zone_t = {"soviet": 0.45, "british": 0.75, "american": 1.05, "french": 1.35}
    for t in frames(d):
        k = smooth((t - t_capital) / 1.9)
        cam = lerp_cam(GERMANY_CAM, BERLIN_CAM, k)
        cam.lon += math.sin(t * 0.25) * 0.0004 * k
        lay = ss_layer(cam)
        dr = ImageDraw.Draw(lay)
        a_de = ramp(t, 0.0, 0.5)
        draw_geom(dr, cam, g["germany"], fill=(34, 34, 36, int(255 * a_de)))
        for z, tz in zone_t.items():
            kz = ramp(t, tz, 0.45)
            if kz > 0:
                draw_geom(dr, cam, g["zones"][z], fill=(*mix((50, 50, 50), ZONE_COL[z], 0.55), int(170 * kz * (1 - 0.82 * k))))
        draw_geom(dr, cam, g["germany"], outline=(190, 186, 178, int(220 * a_de)), width=2)
        for z in zone_t:
            draw_geom(dr, cam, g["zones"][z], outline=(14, 14, 14, int(200 * a_de)), width=1.5)
        # Berlin sectors fade in as we arrive
        kb = ramp(t, t_capital + 1.0, 0.8)
        if kb > 0:
            sub = ss_layer(cam)
            sd = ImageDraw.Draw(sub)
            lit = {"soviet": ramp(t, t_sov, 0.4), "american": ramp(t, t_us, 0.4), "british": ramp(t, t_gb, 0.4), "french": ramp(t, t_fr, 0.4)}
            berlin_layers(sd, cam, t, lit, base_alpha=0.18 + 0.2 * ramp(t, t_four, 0.6))
            lay = Image.alpha_composite(lay, Image.blend(Image.new("RGBA", sub.size, (0, 0, 0, 0)), sub, kb))
        frame = Image.alpha_composite(bg.convert("RGBA"), down(lay))
        fd = ImageDraw.Draw(frame)
        # zone labels on the Germany map
        if k < 0.4:
            la = int(255 * (1 - k / 0.4))
            for z, (lo, la_) in {"soviet": (12.6, 52.0), "british": (8.6, 52.8), "american": (11.0, 49.3), "french": (7.5, 49.0)}.items():
                kz = ramp(t, zone_t[z] + 0.1, 0.35)
                if kz > 0:
                    text(fd, cam.pt(lo, la_), ZONE_NAME[z], 54, fill=mix(INK, ZONE_COL[z], 0.5), alpha=int(la * kz))
            bx, by = cam.pt(13.405, 52.52)
            pa = int(255 * ramp(t, 1.6, 0.4) * (1 - k / 0.4))
            fd.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=(*INK, pa), outline=(0, 0, 0, pa), width=3)
            text(fd, (bx + 24, by - 4), "BERLIN", 58, alpha=pa, anchor="lm")
        # sector labels once in Berlin
        for s, tt in (("soviet", t_sov), ("american", t_us), ("british", t_gb), ("french", t_fr)):
            ka = ramp(t, tt, 0.35)
            if ka > 0 and k > 0.95:
                x, y = cam.pt(*SECTOR_LABEL_AT[s])
                text(fd, (x, y - 10 * (1 - ka)), ZONE_NAME[s], 76, fill=ZONE_COL[s], alpha=int(255 * ka))
                text(fd, (x, y + 48 - 10 * (1 - ka)), "SECTOR", 40, fill=INK, alpha=int(230 * ka))
        if k > 0.9:
            text(fd, (W / 2, 78), "BERLIN · 1945", 64, alpha=int(255 * ramp(t, t_capital + 1.6, 0.5) * (1 - ramp(t, t_sov - 0.3, 0.4))))
        out.write(frame)


# ---------------------------------------------------------------- 2. underground: one ride crosses the line

def city_base(cam, east_dim=1.0):
    g = geo()
    lay = ss_layer(cam)
    dr = ImageDraw.Draw(lay)
    for s in ("american", "british", "french"):
        draw_geom(dr, cam, g["berlin"][s], fill=(30, 31, 34, 255))
    draw_geom(dr, cam, g["berlin"]["soviet"], fill=(*mix((30, 31, 34), (70, 52, 32), east_dim), 255))
    for s in ("american", "british", "french", "soviet"):
        draw_geom(dr, cam, g["berlin"][s], outline=(16, 16, 16, 255), width=2)
    return lay


def wall_line(dr, cam, alpha=255, width=5, col=(235, 232, 225)):
    draw_geom(dr, cam, geo()["wall_inner"], outline=(*col, alpha), width=width)


def line_px(cam, pts):
    return [tuple(p / cam.ss) for p in cam.xy(np.array(pts))]


def g_underground(args, d, timing, base, out):
    t_ride = word_time(timing, "One subway ride")
    t_other = word_time(timing, "other side")
    t_under = word_time(timing, "underground")
    for t in frames(d):
        cam = Cam(13.396 + 0.002 * t / d, 52.524, 13000 + 900 * t / d)
        lay = city_base(cam, 0.6)
        dr = ImageDraw.Draw(lay)
        wall_line(dr, cam, alpha=int(255 * (1 - 0.55 * ramp(t, t_under, 0.6))), width=6)
        frame = Image.alpha_composite(vignette_bg().convert("RGBA"), down(lay))
        light = Image.new("RGB", (W, H))
        ld = ImageDraw.Draw(light)
        for name, pts, t0 in (("U6", U6, t_under + 0.1), ("U8", U8, t_under + 0.4)):
            u = smooth((t - t0) / 1.4)
            if u > 0:
                ld.line(sub_polyline(line_px(cam, pts), u), fill=tuple(int(c * 0.8) for c in LINE_COL[name]), width=14, joint="curve")
        # the ride: a bright train running north to south on the U8, East and back West
        u = smooth((t - t_ride) / max(t_other - t_ride + 0.6, 1.2))
        if t > t_ride:
            pl = line_px(cam, U8)
            for k in range(14):
                p = along(pl, max(u - k * 0.012, 0))
                r = 19 - k
                ld.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=mix((255, 240, 210), LINE_COL["U8"], k / 14))
        frame = add(frame, glow(light, 12, 1.4))
        fd = ImageDraw.Draw(frame)
        text(fd, cam.pt(13.425, 52.532), "EAST", 92, fill=AMBER, alpha=int(255 * ramp(t, 0.2, 0.5)))
        text(fd, cam.pt(13.367, 52.515), "WEST", 84, alpha=int(255 * ramp(t, 0.2, 0.5)))
        text(fd, (W / 2, 90), "UNDERGROUND", 58, fill=INK, alpha=int(255 * ramp(t, t_under, 0.5) * (1 - ramp(t, t_ride, 0.5))))
        out.write(frame)


# ---------------------------------------------------------------- 3. commuters, then the exodus

def g_commuters(args, d, timing, base, out):
    rng = np.random.default_rng(11)
    t_back = word_time(timing, "never came back") - 0.3
    t_1961 = word_time(timing, "summer of 1961") - 0.2
    t_every = word_time(timing, "every single day")
    cam = Cam(13.40, 52.523, 5600)
    base_im = Image.alpha_composite(vignette_bg().convert("RGBA"), down(city_base(cam, 0.7)))
    wl = ss_layer(cam)
    wall_line(ImageDraw.Draw(wl), cam, alpha=235, width=5)
    base_im = Image.alpha_composite(base_im, down(wl))
    east = geo()["berlin"]["soviet"]
    # sample home points in the East and work points in the West on screen
    from shapely.geometry import shape, Point
    E, Wst = shape(east), None
    from shapely.ops import unary_union
    Wst = unary_union([shape(geo()["berlin"][s]) for s in ("american", "british", "french")])
    def sample(poly, n, box):
        pts = []
        while len(pts) < n:
            lo, la = rng.uniform(box[0], box[1]), rng.uniform(box[2], box[3])
            if poly.contains(Point(lo, la)):
                pts.append(cam.pt(lo, la))
        return np.array(pts)
    homes = sample(E, 260, (13.40, 13.56, 52.46, 52.58))
    works = sample(Wst, 260, (13.25, 13.39, 52.46, 52.58))
    N = 520
    a_i, b_i = rng.integers(0, 260, N), rng.integers(0, 260, N)
    phase, speed = rng.uniform(0, 1, N), rng.uniform(0.18, 0.3, N)
    bend = rng.normal(0, 60, N)
    for t in frames(d):
        frame = base_im.copy()
        light = Image.new("RGB", (W, H))
        ld = ImageDraw.Draw(light)
        flow = ramp(t, 0.3, 0.8)
        surge = ramp(t, t_1961, 1.0) + ramp(t, t_every, 0.8)
        for i in range(N):
            active = i < 220 + 300 * min(surge, 1)
            if not active or flow <= 0:
                continue
            u = (phase[i] + t * speed[i] * (1 + 0.8 * surge)) % 2.0
            going = u < 1.0
            p0, p1 = homes[a_i[i]], works[b_i[i]]
            mid = (p0 + p1) / 2 + np.array([0, bend[i]])
            Q = lambda v: (1 - v) ** 2 * p0 + 2 * (1 - v) * v * mid + v * v * p1
            if not going and t > t_back:
                # the return trip stops: they stay in the West and pile up there
                q = p1
                ld.ellipse([q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4], fill=tuple(int(c * 0.75 * flow) for c in AMBER))
                continue
            v = u if going else 2.0 - u
            q, qt = Q(v), Q(clamp(v - (0.07 if going else -0.07)))
            col = AMBER if going else (190, 200, 220)
            ld.line([tuple(qt), tuple(q)], fill=tuple(int(c * flow * 0.6) for c in col), width=4)
            r = 4.5 if going else 3.5
            ld.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=tuple(int(c * flow) for c in col))
        frame = add(frame, glow(light, 6, 1.2))
        fd = ImageDraw.Draw(frame)
        text(fd, cam.pt(13.49, 52.505), "EAST", 72, fill=AMBER)
        text(fd, cam.pt(13.31, 52.505), "WEST", 72)
        kc = ramp(t, 0.4, 0.5) * (1 - ramp(t, t_back - 0.2, 0.4))
        if kc > 0:
            text(fd, (W / 2, 120), "DAILY COMMUTERS: EAST TO WEST", 70, alpha=int(255 * kc))
        kn = ramp(t, t_back, 0.4) * (1 - ramp(t, t_1961 - 0.3, 0.4))
        if kn > 0:
            text(fd, (W / 2, 120), "NO RETURN TRIP", 84, fill=AMBER, alpha=int(255 * kn))
        ka = ramp(t, t_1961, 0.5)
        if ka > 0:
            text(fd, (W / 2, 120), "SUMMER 1961", 96, fill=AMBER, alpha=int(255 * ka))
        kd = ramp(t, t_every, 0.5)
        if kd > 0:
            text(fd, (W / 2, 210), "THOUSANDS LEAVE EVERY DAY", 54, alpha=int(255 * kd))
        out.write(frame)


# ---------------------------------------------------------------- 4. the 1961-89 subway map (c19), dark, with live lines

C19_PAL = [((248, 240, 216), (44, 38, 31)),    # East Berlin area
           ((248, 232, 168), (22, 23, 26)),    # West Berlin area
           ((72, 72, 72), (236, 232, 224)),    # text
           ((48, 48, 48), (236, 232, 224)),
           ((104, 72, 152), (120, 86, 175)),   # U6
           ((8, 56, 128), (45, 92, 180)),      # U8
           ((0, 176, 80), (35, 150, 80)),      # S-Bahn
           ((0, 104, 48), (28, 110, 60)),
           ((152, 144, 120), (105, 100, 92)),  # big district names
           ((96, 96, 96), (120, 118, 112)),    # closed-station discs
           ((248, 248, 248), (30, 30, 30)),    # bar in the closed-station disc
           ((200, 200, 184), (205, 196, 176))]  # dashed sector border
C19_LINES = {  # station centres (c19 pixel coords), north to south, with the map edges as endpoints
    "U8": [(704, 0), (704, 74), (804, 184), (886, 334), (970, 496), (1056, 666), (1132, 924), (1244, 1118), (1434, 1266),
           (1504, 1466), (1454, 1660), (1324, 1916), (1300, 1957)],
    "U6": [(0, 180), (80, 254), (238, 366), (334, 466), (436, 562), (592, 714), (714, 892), (806, 1062), (806, 1314), (872, 1524),
           (880, 1610), (902, 1820), (910, 1957)],
    "S": [(1150, 0), (1150, 158), (1100, 290), (886, 334), (666, 472), (660, 640), (842, 844), (950, 1000), (952, 1124), (806, 1314),
          (710, 1448), (600, 1560), (600, 1686), (698, 1876), (670, 1957)],
}
GHOSTS = {  # the sixteen closed stations, as named in the narration
    "Bernauer Straße": ("U8", (1056, 666)), "Rosenthaler Platz": ("U8", (1132, 924)), "Weinmeisterstraße": ("U8", (1244, 1118)),
    "Alexanderplatz": ("U8", (1434, 1266)), "Jannowitzbrücke": ("U8", (1504, 1466)), "Heinrich-Heine-Straße": ("U8", (1454, 1660)),
    "Schwartzkopffstraße": ("U6", (592, 714)), "Nordbahnhof U": ("U6", (714, 892)), "Oranienburger Tor": ("U6", (806, 1062)),
    "Französische Straße": ("U6", (872, 1524)), "Stadtmitte": ("U6", (880, 1610)),
    "Nordbahnhof S": ("S", (842, 844)), "Oranienburger Straße": ("S", (952, 1124)), "Unter den Linden": ("S", (710, 1448)),
    "Potsdamer Platz": ("S", (600, 1686)), "Bornholmer Straße": ("S", (1150, 158)),
}
FRIEDRICHSTR = (806, 1314)


@lru_cache(None)
def c19_assets(base):
    """Dark re-colouring of the map plus per-line masks with a 0..1 position along the line."""
    src = np.asarray(Image.open(os.path.join(base, "assets", "c19.png")).convert("RGB"), np.float32)
    h, w, _ = src.shape
    pal = np.array([p for p, _ in C19_PAL], np.float32)
    dark = np.array([q for _, q in C19_PAL], np.float32)
    wgt = np.zeros((h, w, len(pal)), np.float32)
    for y0 in range(0, h, 256):   # soft nearest-palette classification keeps the antialiased edges
        d2 = ((src[y0:y0 + 256, :, None, :] - pal[None, None]) ** 2).sum(-1)
        e = np.exp(-(d2 - d2.min(-1, keepdims=True)) / (2 * 28.0 ** 2))
        wgt[y0:y0 + 256] = e / e.sum(-1, keepdims=True)
    out = np.einsum("hwk,kc->hwc", wgt, dark)
    masks = {"U8": wgt[..., 5], "U6": wgt[..., 4], "S": wgt[..., 6] + wgt[..., 7]}
    yy, xx = np.mgrid[0:h, 0:w]
    pos = {}
    for name, pts in C19_LINES.items():
        m = masks[name] > 0.35
        P = np.asarray(pts, float)
        L = polyline_len(P)
        px, py = xx[m].astype(float), yy[m].astype(float)
        best, bs = np.full(px.shape, 1e18), np.zeros(px.shape)
        for i in range(len(P) - 1):
            a, b = P[i], P[i + 1]
            ab = b - a
            tt = np.clip(((px - a[0]) * ab[0] + (py - a[1]) * ab[1]) / max((ab ** 2).sum(), 1e-9), 0, 1)
            dx, dy = px - (a[0] + ab[0] * tt), py - (a[1] + ab[1] * tt)
            dd = dx * dx + dy * dy
            sel = dd < best
            best[sel], bs[sel] = dd[sel], (L[i] + tt[sel] * np.hypot(*ab)) / L[-1]
        s = np.zeros((h, w), np.float32)
        s[m] = bs
        pos[name] = (np.clip(masks[name], 0, 1).astype(np.float32), s)
    return np.clip(out, 0, 255).astype(np.float32), pos


def c19_view(z, cx, cy, size=(1920, 1957)):
    cw, ch = size[0] / z, size[0] / z * H / W
    if ch > size[1] / z:
        ch = size[1] / z
        cw = ch * W / H
    left = min(max(cx * size[0] - cw / 2, 0), size[0] - cw)
    top = min(max(cy * size[1] - ch / 2, 0), size[1] - ch)
    return left, top, cw, ch


def g_c19(args, d, timing, base, out):
    """args: mode = lines | stations | fstr; keys = per-beat camera [z, cx, cy] (start of each beat)."""
    mode = args.get("mode", "lines")
    dark, pos = c19_assets(base)
    keys = args["keys"]          # list of [z, cx, cy] per beat, plus a final one
    starts = [b["start"] for b in timing] + [d]
    lit_at = {}
    if mode == "stations":
        for name in GHOSTS:
            needle = name[:-2] if name.endswith((" U", " S")) else name
            try:
                if name == "Nordbahnhof S":
                    b = next(x for x in timing if "S-Bahn: Nordbahnhof" in x["say"])
                    lit_at[name] = b["say_at"] + b["say_d"] * b["say"].find("Nordbahnhof") / len(b["say"]) + 0.12
                else:
                    lit_at[name] = word_time(timing, needle)
            except KeyError:
                pass
    line_t = {}
    if mode == "lines":
        line_t = {"U6": word_time(timing, "U6"), "U8": word_time(timing, "U8"), "S": word_time(timing, "S-Bahn")}
    t_sixteen = word_time(timing, "sixteen") if mode == "stations" else 1e9
    for t in frames(d):
        # camera: hold each beat's framing, glide to the next over the last 0.9 s of the beat
        i = max(j for j in range(len(timing)) if starts[j] <= t + 1e-6)
        k0, k1 = keys[min(i, len(keys) - 1)], keys[min(i + 1, len(keys) - 1)]
        span = starts[i + 1] - starts[i]
        u = (t - starts[i]) / max(span, 1e-6)
        drift = 0.04 * u
        g = smooth((t - (starts[i + 1] - 0.9)) / 0.9) if i + 1 < len(timing) else 0.0
        z = k0[0] * (1 + drift) * (1 - g) + k1[0] * g
        cx, cy = k0[1] + (k1[1] - k0[1]) * g, k0[2] + (k1[2] - k0[2]) * g
        if mode == "lines" and len(keys) == 2:   # one long continuous zoom, as in the first cut
            uu = smooth(t / d)
            z, cx, cy = [a + (b - a) * uu for a, b in zip(keys[0], keys[1])]
        left, top, cw, ch = c19_view(z, cx, cy)
        box = (int(left), int(top), int(left + cw), int(top + ch))
        light = np.zeros((box[3] - box[1], box[2] - box[0], 3), np.float32)
        for name, (m, s) in pos.items():
            m, s = m[box[1]:box[3], box[0]:box[2]], s[box[1]:box[3], box[0]:box[2]]
            col = np.array(LINE_COL[name], np.float32)
            if mode == "lines":
                # light runs along each line from north (West) to south (West), then pulses keep flowing
                t0 = line_t.get(name, 0) - 1.2
                reach = smooth((t - t0) / 2.2)
                base_lit = 0.25 + 0.75 * reach * (s <= reach + 1e-3)
                pulse = np.maximum(0, np.cos((s * 9 - t * 1.1) * 2 * np.pi)) ** 8 * reach
                inten = m * (base_lit * 0.55 + pulse * 1.3)
            elif mode == "fstr":
                inten = m * 0.35
            else:
                inten = m * 0.3
            light += inten[..., None] * col[None, None]
        crop_dark = Image.fromarray(np.clip(dark[box[1]:box[3], box[0]:box[2]], 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
        crop_light = Image.fromarray(np.clip(light, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
        frame = add(crop_dark, glow(crop_light, 10, 1.5))
        sc = W / cw
        to_s = lambda p: ((p[0] - left) * sc, (p[1] - top) * sc)
        ov = Image.new("RGB", (W, H))
        od = ImageDraw.Draw(ov)
        fd = ImageDraw.Draw(frame)
        if mode == "stations":
            for name, (ln, p) in GHOSTS.items():
                ta = lit_at.get(name, t_sixteen if name == "Bornholmer Straße" else 1e9)
                k = ramp(t, ta, 0.25)
                all16 = ramp(t, t_sixteen, 0.3)
                if k <= 0 and all16 <= 0:
                    continue
                x, y = to_s(p)
                col = LINE_COL[ln]
                pulse = 1 + 0.25 * math.sin((t - ta) * 5) * math.exp(-(t - ta) * 0.8)
                r = 30 * sc / 1.4 * pulse
                inten = max(k, all16 * (0.8 + 0.2 * math.sin(t * 6)))
                od.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(c * inten) for c in col))
                od.ellipse([x - r * 0.45, y - r * 0.45, x + r * 0.45, y + r * 0.45], fill=tuple(int(255 * inten) for _ in range(3)))
                if 0 < t - ta < 1.2:   # expanding ring the moment it is named
                    rr = r * (1 + (t - ta) * 3.5)
                    a = 1 - (t - ta) / 1.2
                    od.ellipse([x - rr, y - rr, x + rr, y + rr], outline=tuple(int(c * a) for c in col), width=5)
            frame = add(frame, glow(ov, 14, 1.6))
            fd = ImageDraw.Draw(frame)
            n = sum(1 for nm in GHOSTS if t >= lit_at.get(nm, 1e9)) if t < t_sixteen else 16
            if n:
                panel(frame, (W - 430, 30, W - 40, 215))
                fd = ImageDraw.Draw(frame)
                text(fd, (W - 70, 100), f"{n}", 130, fill=AMBER, anchor="rm")
                text(fd, (W - 70, 180), "GHOST STATIONS", 44, anchor="rm")
        elif mode == "fstr":
            x, y = to_s(FRIEDRICHSTR)
            for name, (ln, p) in GHOSTS.items():   # every other station stays dark
                gx, gy = to_s(p)
                rr = 21 * sc / 1.4
                fd.ellipse([gx - rr, gy - rr, gx + rr, gy + rr], fill=(16, 16, 16), outline=(70, 70, 70), width=3)
            k = ramp(t, 0.3, 0.5)
            for j in range(3):
                ph = ((t * 0.7 + j / 3) % 1.0)
                rr = 30 + ph * 170
                od.ellipse([x - rr, y - rr, x + rr, y + rr], outline=tuple(int(c * (1 - ph) * k) for c in AMBER), width=6)
            od.ellipse([x - 34, y - 34, x + 34, y + 34], fill=tuple(int(c * k) for c in AMBER))
            frame = add(frame, glow(ov, 16, 1.5))
            fd = ImageDraw.Draw(frame)
            fd.ellipse([x - 13, y - 13, x + 13, y + 13], fill=(255, 250, 240))
            panel(frame, (x + 40, y - 70, x + 760, y + 110), alpha=int(215 * k))
            fd = ImageDraw.Draw(frame)
            text(fd, (x + 70, y - 8), "FRIEDRICHSTRASSE", 76, fill=AMBER, anchor="lm", alpha=int(255 * k))
            text(fd, (x + 72, y + 62), "THE ONLY STOP", 46, anchor="lm", alpha=int(255 * ramp(t, 0.9, 0.5)))
        else:
            for name, tt in line_t.items():
                ka = ramp(t, tt, 0.35) * (1 - ramp(t, tt + 2.6, 0.5))
                if ka > 0:
                    lab = {"U6": "U6", "U8": "U8", "S": "S-BAHN"}[name]
                    panel(frame, (W / 2 - 260, 40, W / 2 + 260, 185), alpha=int(170 * ka))
                    fd = ImageDraw.Draw(frame)
                    text(fd, (W / 2, 112), lab, 110, fill=LINE_COL[name], alpha=int(255 * ka))
        out.write(frame)


# ---------------------------------------------------------------- 5. speedometer: 15 -> 25 km/h

def needle_gauge(img, cx, cy, R, v, vmax=60, glow_v=None):
    dr = ImageDraw.Draw(img)
    a0, a1 = math.radians(140), math.radians(400)   # sweep from lower left, clockwise
    ang = lambda x: a0 + (a1 - a0) * x / vmax
    dr.ellipse([cx - R - 18, cy - R - 18, cx + R + 18, cy + R + 18], fill=(26, 26, 27), outline=(90, 88, 84), width=6)
    dr.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(14, 14, 15))
    for x in range(0, vmax + 1):
        a = ang(x)
        big = x % 10 == 0
        mid = x % 5 == 0
        r0 = R - (44 if big else 30 if mid else 18)
        col = AMBER if 15 <= x <= 25 and glow_v else (210, 206, 198)
        dr.line([cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * (R - 8), cy + math.sin(a) * (R - 8)],
                fill=col if (big or mid) else (120, 118, 112), width=8 if big else 5 if mid else 3)
        if big:
            text(dr, (cx + math.cos(a) * (R - 92), cy + math.sin(a) * (R - 92)), str(x), 52, stroke=0)
    text(dr, (cx, cy + R * 0.42), "km/h", 46, fill=GREY, stroke=0)
    a = ang(v)
    light = Image.new("RGB", img.size)
    ld = ImageDraw.Draw(light)
    ld.line([cx - math.cos(a) * 40, cy - math.sin(a) * 40, cx + math.cos(a) * (R - 30), cy + math.sin(a) * (R - 30)], fill=AMBER, width=14)
    img.paste(add(img, glow(light, 10, 1.2)))
    dr = ImageDraw.Draw(img)
    dr.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(40, 38, 36), outline=(150, 146, 140), width=4)


def tunnel_rush(img, t_pos, speed_k):
    """Concentric tunnel rings streaming towards the viewer; their spacing reads as speed."""
    dr = ImageDraw.Draw(img)
    cx, cy = W * 0.5, H * 0.5
    for i in range(14):
        z = ((i - t_pos) % 14) / 14 + 0.02
        r = 70 / z
        a = int(clamp(1.4 - z * 1.3) * 60 * (0.6 + 0.4 * speed_k))
        if r < 2400:
            dr.rounded_rectangle([cx - r * 1.4, cy - r, cx + r * 1.4, cy + r * 0.9], radius=int(r * 0.7), outline=(a, a, a), width=3)


def g_speed(args, d, timing, base, out):
    t15 = word_time(timing, "fifteen")
    tj = word_time(timing, "tried to jump")
    t25 = word_time(timing, "twenty-five")
    tc = word_time(timing, "too easy")
    pos = 0.0
    prev = 0.0
    for t in frames(d):
        v = 15 * smooth((t - 0.2) / 1.6)
        v += 10 * smooth((t - t25 + 0.6) / 1.3)
        v += 0.4 * math.sin(t * 7) * (v > 1)
        if tj < t < tj + 1.2:
            v += 3 * math.sin((t - tj) * 18) * (1 - (t - tj) / 1.2)
        pos += (t - prev) * v * 0.09
        prev = t
        img = vignette_bg()
        tunnel_rush(img, pos, v / 25)
        needle_gauge(img, 640, 560, 380, v, glow_v=True)
        dr = ImageDraw.Draw(img)
        x0 = 1150
        shown = 25 if t > t25 + 0.6 else 15
        k1 = ramp(t, t15 - 0.3, 0.4)
        if k1 > 0:
            num = int(round(v)) if abs(v - shown) > 0.6 and t < t25 + 1.8 else shown
            text(dr, (x0, 470), f"{max(num, 0)}", 260, fill=AMBER if t > t25 else INK, anchor="lm", alpha=int(255 * k1))
            text(dr, (x0 + 10, 640), "KM/H", 80, anchor="lm", alpha=int(255 * k1))
        kj = ramp(t, tj, 0.4) * (1 - ramp(t, t25 - 0.4, 0.4))
        if kj > 0:
            text(dr, (x0 + 10, 760), "AN ESCAPE ATTEMPT", 58, fill=AMBER, anchor="lm", alpha=int(255 * kj))
        kc = ramp(t, t25 + 0.8, 0.4)
        if kc > 0:
            text(dr, (x0 + 10, 760), "+10 KM/H", 64, fill=AMBER, anchor="lm", alpha=int(255 * kc))
        kk = ramp(t, tc, 0.4)
        if kk > 0:
            text(dr, (x0 + 10, 850), "SLOW = EASY TO CATCH", 50, anchor="lm", alpha=int(255 * kk))
        out.write(img)


# ---------------------------------------------------------------- 6. money

def banknote(w=760, h=380, value="100", tint=(196, 182, 150), seed=1):
    """A period Deutsche Mark note drawn procedurally (no real design copied)."""
    rng = np.random.default_rng(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([0, 0, w - 1, h - 1], 14, fill=(*tint, 255), outline=(60, 54, 44, 255), width=4)
    dark = tuple(int(c * 0.45) for c in tint)
    for k in range(26):   # guilloche bands
        ph = rng.uniform(0, 6.28)
        pts = [(x, h * 0.5 + math.sin(x / w * 6.28 * 2 + ph) * h * 0.32 * math.cos(x / w * 3.1 + k * 0.2)) for x in range(20, w - 20, 6)]
        dr.line(pts, fill=(*dark, 70), width=2)
    dr.rounded_rectangle([18, 18, w - 19, h - 19], 10, outline=(*dark, 255), width=3)
    dr.ellipse([w * 0.06, h * 0.18, w * 0.36, h * 0.82], fill=(*tuple(min(255, c + 20) for c in tint), 255), outline=(*dark, 255), width=3)
    text(dr, (w * 0.21, h * 0.5), "DM", 96, fill=dark, stroke=0)
    text(dr, (w * 0.86, h * 0.24), value, 92, fill=dark, stroke=0)
    text(dr, (w * 0.62, h * 0.55), "DEUTSCHE MARK", 54, fill=dark, stroke=0)
    text(dr, (w * 0.62, h * 0.74), "BUNDESREPUBLIK", 28, fill=dark, stroke=0, name="Pretendard-SemiBold.otf")
    return im


@lru_cache(None)
def note_img(scale=1.0, seed=1):
    n = banknote(seed=seed)
    return n.resize((int(n.width * scale), int(n.height * scale)), Image.LANCZOS)


def paste_note(img, cx, cy, scale, rot, alpha=1.0, seed=1):
    n = note_img(round(scale, 2), seed).rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        n.putalpha(n.getchannel("A").point(lambda v: int(v * alpha)))
    sh = Image.new("RGBA", n.size, (0, 0, 0, 0))
    sh.putalpha(n.getchannel("A").point(lambda v: int(v * 0.6)))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(sh, (int(cx - n.width / 2 + 10), int(cy - n.height / 2 + 16))) if img.mode == "RGBA" else None
    img.paste(n, (int(cx - n.width / 2), int(cy - n.height / 2)), n)


def flow_notes(img, p0, p1, t, n=7, lift=-260, speed=0.45, alpha=1.0, scale=0.22):
    for i in range(n):
        u = (t * speed + i / n) % 1.0
        a = math.sin(u * math.pi) * alpha
        x = p0[0] + (p1[0] - p0[0]) * u
        y = p0[1] + (p1[1] - p0[1]) * u + lift * math.sin(u * math.pi)
        paste_note(img, x, y, scale, math.sin(u * 6 + i) * 18, a, seed=i % 3 + 1)


def g_money_hook(args, d, timing, base, out):
    """Overlay: West Berlin pays East Germany (teaser, over the darkened shot)."""
    tp = word_time(timing, "paying")
    tout = word_time(timing, "First,") - 0.3
    for t in frames(d):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        k = ramp(t, tp - 0.4, 0.5) * (1 - ramp(t, tout, 0.6))
        if k > 0:
            dr = ImageDraw.Draw(img)
            text(dr, (430, 560), "WEST BERLIN", 84, alpha=int(255 * k))
            text(dr, (1490, 560), "EAST GERMANY", 84, fill=AMBER, alpha=int(255 * k))
            flow_notes(img, (520, 480), (1400, 480), t - tp, n=6, lift=-200, alpha=k, scale=0.3)
            text(dr, (W / 2, 760), "PAYS", 120, fill=AMBER, alpha=int(255 * k))
        out.write(img)


def bar(dr, x, y0, wbar, hbar, col, alpha=255):
    dr.rectangle([x - wbar / 2, y0 - hbar, x + wbar / 2, y0], fill=(*col, alpha))


def g_money(args, d, timing, base, out):
    t_note = 0.15
    t_ret = word_time(timing, "In return")
    t63 = word_time(timing, "from 1963")
    t_month = word_time(timing, "Every single month")
    t180 = word_time(timing, "hundred and eighty")
    t89 = word_time(timing, "By 1989")
    t_year = word_time(timing, "six million")
    t_wall = word_time(timing, "built the Wall")
    bg = vignette_bg()
    years = list(range(1963, 1990))
    # fee per month, 181,132 DM in 1963 rising to 495,756 DM in 1989 (two published figures; steps in between interpolated)
    fee = {y: 181132 + (495756 - 181132) * ((y - 1963) / 26) ** 1.25 for y in years}
    for t in frames(d):
        img = bg.copy().convert("RGBA")
        dr = ImageDraw.Draw(img)
        # 1. a single note arrives
        k0 = ramp(t, t_note, 0.6) * (1 - ramp(t, t_ret - 0.2, 0.5))
        if k0 > 0:
            paste_note(img, W / 2, H / 2 - 40 * (1 - k0), 1.0 * (0.9 + 0.1 * k0), -4 + 4 * k0, k0)
        # 2. West -> East flow
        k1 = ramp(t, t_ret - 0.2, 0.5) * (1 - ramp(t, t180 - 0.3, 0.5))
        if k1 > 0:
            text(dr, (380, 640), "WEST BERLIN", 80, alpha=int(255 * k1))
            text(dr, (1540, 640), "EAST GERMANY", 80, fill=AMBER, alpha=int(255 * k1))
            flow_notes(img, (480, 560), (1440, 560), t, n=7, lift=-230, alpha=k1, scale=0.28)
            dr = ImageDraw.Draw(img)
            ky = ramp(t, t63, 0.4)
            if ky > 0:
                text(dr, (W / 2, 160), "1963", 170, fill=AMBER, alpha=int(255 * ky * k1))
            km = ramp(t, t_month, 0.4)
            if km > 0:
                text(dr, (W / 2, 860), "EVERY SINGLE MONTH", 76, alpha=int(255 * km * k1))
        # 3. the fee grows, 1963 -> 1989
        k2 = ramp(t, t180 - 0.3, 0.5) * (1 - ramp(t, t_wall - 0.3, 0.5))
        if k2 > 0:
            x0, x1, yb = 260, 1660, 900
            grow = smooth((t - t89 + 0.2) / 2.2)
            nshow = 1 + int(grow * (len(years) - 1))
            for i, y in enumerate(years[:nshow]):
                x = x0 + (x1 - x0) * i / (len(years) - 1)
                hgt = fee[y] / 495756 * 520
                col = AMBER if i in (0, len(years) - 1) else (150, 120, 80)
                bar(dr, x, yb, 38, hgt * ramp(t, t180 + i * 0.07 if i else t180, 0.35), col, int(255 * k2))
            dr.line([x0 - 40, yb, x1 + 40, yb], fill=(*GREY, int(255 * k2)), width=3)
            text(dr, (x0, yb + 50), "1963", 46, alpha=int(255 * k2))
            if grow > 0.98:
                text(dr, (x1, yb + 50), "1989", 46, alpha=int(255 * k2))
            val = 181132 + (495756 - 181132) * grow if t > t89 - 0.2 else 181132 * smooth((t - t180) / 1.2)
            if t < t_year - 0.2:
                text(dr, (W / 2, 170), f"{int(val):,} DM", 150, fill=AMBER, alpha=int(255 * k2))
                text(dr, (W / 2, 280), "PER MONTH", 60, alpha=int(255 * k2))
            else:
                ky = ramp(t, t_year - 0.2, 0.4)
                text(dr, (W / 2, 170), "≈ 6,000,000 DM" if False else "~ 6 MILLION DM", 150, fill=AMBER, alpha=int(255 * k2 * ky))
                text(dr, (W / 2, 280), "PER YEAR", 60, alpha=int(255 * k2 * ky))
        # 4. paying the country that built the Wall
        k3 = ramp(t, t_wall - 0.3, 0.5)
        if k3 > 0:
            wall_y = 700
            dr.rectangle([W / 2 - 40, wall_y - 360, W / 2 + 40, wall_y + 200], fill=(70, 68, 64, int(255 * k3)))
            dr.rectangle([W / 2 - 60, wall_y - 380, W / 2 + 60, wall_y - 340], fill=(90, 88, 84, int(255 * k3)))
            for yy in range(wall_y - 330, wall_y + 200, 60):
                dr.line([W / 2 - 40, yy, W / 2 + 40, yy], fill=(40, 40, 40, int(255 * k3)), width=3)
            text(dr, (420, 850), "WEST BERLIN", 74, alpha=int(255 * k3))
            text(dr, (1500, 850), "EAST GERMANY", 74, fill=AMBER, alpha=int(255 * k3))
            flow_notes(img, (520, 560), (1400, 560), t, n=8, lift=-330, alpha=k3, scale=0.26, speed=0.6)
            dr = ImageDraw.Draw(img)
            text(dr, (W / 2, 150), "PAYING FOR ITS OWN WALL", 92, fill=AMBER, alpha=int(255 * ramp(t, t_wall, 0.4)))
        out.write(img)


# ---------------------------------------------------------------- 7. photo with Ken Burns + annotation (arrow, highlight)

def g_photo(args, d, timing, base, out):
    """args: file, from/to [z, cx, cy] like assemble's images; arrow: {"to": [x, y], "from": [x, y]} in image px, label."""
    src = Image.open(os.path.join(base, args["file"])).convert("L").convert("RGB")
    s = max(W * 2 / src.width, H * 2 / src.height)
    big = src.resize((int(src.width * s), int(src.height * s)), Image.LANCZOS)
    z0, x0, y0 = args.get("from", [1.0, 0.5, 0.5])
    z1, x1, y1 = args.get("to", [1.12, 0.5, 0.5])
    arrow = args.get("arrow")
    t_arrow = word_time(timing, args["at"]) if args.get("at") else 0.6
    for t in frames(d):
        u = smooth(t / d)
        z, cx, cy = z0 + (z1 - z0) * u, x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
        cw, ch = big.width / z, big.width / z * H / W
        if ch > big.height / z:
            ch = big.height / z
            cw = ch * W / H
        left = min(max(cx * big.width - cw / 2, 0), big.width - cw)
        top = min(max(cy * big.height - ch / 2, 0), big.height - ch)
        frame = big.transform((W, H), Image.EXTENT, (left, top, left + cw, top + ch), Image.BICUBIC)
        frame = Image.eval(frame, lambda v: int(min(255, v * 1.04)))
        if arrow:
            to_s = lambda p: ((p[0] * s - left) * W / cw, (p[1] * s - top) * H / ch)
            k = ramp(t, t_arrow, 0.45)
            if k > 0:
                (ax, ay), (bx, by) = to_s(arrow["from"]), to_s(arrow["to"])
                ex, ey = ax + (bx - ax) * k, ay + (by - ay) * k
                ang = math.atan2(ey - ay, ex - ax)
                head = [(ex, ey), (ex - 70 * math.cos(ang - 0.45), ey - 70 * math.sin(ang - 0.45)),
                        (ex - 70 * math.cos(ang + 0.45), ey - 70 * math.sin(ang + 0.45))]
                sx, sy = ex - 50 * math.cos(ang), ey - 50 * math.sin(ang)
                fd = ImageDraw.Draw(frame)
                fd.line([ax, ay, sx, sy], fill=(0, 0, 0), width=30)
                fd.polygon([(x + 0, y + 0) for x, y in head], fill=(0, 0, 0))
                fd.line([ax, ay, sx, sy], fill=AMBER, width=18)
                shrink = [(ex - 9 * math.cos(ang), ey - 9 * math.sin(ang))] + [((x - ex) * 0.78 + ex - 9 * math.cos(ang), (y - ey) * 0.78 + ey - 9 * math.sin(ang)) for x, y in head[1:]]
                fd.polygon(shrink, fill=AMBER)
                if arrow.get("label"):
                    text(fd, (ax + arrow.get("label_dx", 0), ay + arrow.get("label_dy", -60)), arrow["label"], 70, fill=AMBER,
                         alpha=int(255 * ramp(t, t_arrow + 0.3, 0.4)))
        out.write(frame)


GRAPHICS = {"zones": g_zones, "underground": g_underground, "commuters": g_commuters, "c19": g_c19, "speed": g_speed,
            "money_hook": g_money_hook, "money": g_money, "photo": g_photo}


class Stills:
    def __init__(self, prefix):
        self.prefix, self.n = prefix, 0

    def write(self, im):
        im.convert("RGB").save(f"{self.prefix}_{self.n:02d}.jpg", quality=88)
        self.n += 1


def preview(v, timeline, beats_idx, script, times, prefix):
    """Stills from a real timeline: python3 -c 'import graphics2d as g; g.preview(...)'."""
    global STILLS
    tl = json.load(open(timeline))["beats"]
    sc = json.load(open(script))["beats"]
    st = tl[beats_idx[0]]["start"]
    timing = [{"start": tl[i]["start"] - st, "say_at": tl[i]["start"] - st, "say": sc[i].get("say", ""),
               "say_d": tl[i]["end"] - tl[i]["start"] - 0.12 - sc[i].get("hold", 0), "end": tl[i]["end"] - st} for i in beats_idx]
    d = timing[-1]["end"]
    STILLS = [x for x in times if x < d]
    GRAPHICS[v["name"]](v.get("args", {}), d, timing, os.path.dirname(script), Stills(prefix))
    STILLS = None
    return d


def render(v, d, timing, base, path, ext):
    out = Out(path, ext, alpha=v.get("alpha", False))
    GRAPHICS[v["name"]](v.get("args", {}), d, timing, base, out)
    out.close()
