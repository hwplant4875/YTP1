"""Portrait (1080x1920) graphics for STRATA Short #4 'Friedrichstrasse, the one stop' (loaded by assemble.py via the
visual's "module"). Everything important stays in x 90..900, y 220..1400: clear of the Shorts top bar, the right-hand
buttons and the bottom 25 % (title / channel area).

map_s4   - the episode's c19 network map (Ericmetro, CC0), re-framed for a vertical frame: West Berlin trains (light
           pulses) run through the dark, sealed stations; Friedrichstrasse lights up as the only stop.
split_s4 - schematic of the split station (research_ghost.md, S7/S4): West Berlin platforms on one side of a guarded
           steel-and-glass wall, a border crossing into East Germany on the other, with passport checks, searches and
           interrogation rooms.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import graphics2d as g

RED = (230, 42, 42)
STEEL = (120, 124, 130)
GLASS = (120, 170, 200)
WESTC = (110, 150, 205)


def fit_text(dr, xy, s, size, maxw=860, **k):
    """g.text, shrunk so the line never exceeds maxw pixels (no text off-frame)."""
    while size > 36 and g.font(size).getlength(s) + 2 * max(3, int(size * 0.07)) > maxw:
        size -= 4
    g.text(dr, xy, s, size, **k)


# ---------------------------------------------------------------- 1. the network map, Friedrichstrasse the only stop

def map_s4(args, d, timing, base, out):
    W, H = g.W, g.H
    dark, pos = g.c19_assets(base)
    mh, mw = dark.shape[:2]
    try:
        t_one = g.word_time(timing, "one station")
    except KeyError:
        t_one = 0.5
    try:
        t_name = g.word_time(timing, "Friedrich", lag=0.0)
    except KeyError:
        t_name = t_one + 1.2
    fx, fy = g.FRIEDRICHSTR
    z0, z1 = args.get("z", [1.0, 1.75])
    for t in g.frames(d):
        # zoom towards Friedrichstrasse, keeping it at ~43 % of the frame height once the frame can move
        z = z0 + (z1 - z0) * g.smooth(t / max(d, 1e-6))
        ch = mh / z
        cw = ch * W / H
        sc = W / cw
        left = min(max(fx - (W / 2) / sc, 0), mw - cw)
        top = min(max(fy - (H * 0.43) / sc, 0), mh - ch)
        box = (int(left), int(top), int(left + cw), int(top + ch))
        light = np.zeros((box[3] - box[1], box[2] - box[0], 3), np.float32)
        for name, (m, s) in pos.items():
            m, s = m[box[1]:box[3], box[0]:box[2]], s[box[1]:box[3], box[0]:box[2]]
            col = np.array(g.LINE_COL[name], np.float32)
            pulse = np.maximum(0, np.cos((s * 7 - t * 0.55) * 2 * np.pi)) ** 8   # trains running through
            inten = m * (0.32 + pulse * 1.25)
            light += inten[..., None] * col[None, None]
        crop_dark = Image.fromarray(np.clip(dark[box[1]:box[3], box[0]:box[2]], 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
        crop_light = Image.fromarray(np.clip(light, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
        frame = g.add(crop_dark, g.glow(crop_light, 10, 1.5))
        to_s = lambda p: ((p[0] - left) * W / (box[2] - box[0]), (p[1] - top) * H / (box[3] - box[1]))
        fd = ImageDraw.Draw(frame)
        for name, (ln, p) in g.GHOSTS.items():      # every sealed station stays dark
            gx, gy = to_s(p)
            rr = 15 * sc
            fd.ellipse([gx - rr, gy - rr, gx + rr, gy + rr], fill=(16, 16, 16), outline=(80, 80, 80), width=3)
            fd.line([gx - rr * 0.6, gy, gx + rr * 0.6, gy], fill=(110, 110, 110), width=max(3, int(rr * 0.3)))
        x, y = to_s((fx, fy))
        k = g.ramp(t, t_one - 0.1, 0.45)
        ov = Image.new("RGB", (W, H))
        od = ImageDraw.Draw(ov)
        for j in range(3):
            ph = ((t * 0.7 + j / 3) % 1.0)
            rr = 34 + ph * 190
            od.ellipse([x - rr, y - rr, x + rr, y + rr], outline=tuple(int(c * (1 - ph) * k) for c in g.AMBER), width=7)
        od.ellipse([x - 38, y - 38, x + 38, y + 38], fill=tuple(int(c * k) for c in g.AMBER))
        frame = g.add(frame, g.glow(ov, 16, 1.5))
        fd = ImageDraw.Draw(frame)
        if k > 0:
            fd.ellipse([x - 15, y - 15, x + 15, y + 15], fill=(255, 250, 240))
        kl = g.ramp(t, t_name - 0.05, 0.35)
        if kl > 0:
            ly = y + 250
            g.panel(frame, (90, ly - 105, W - 180 + 90, ly + 110), alpha=int(215 * kl))
            fd = ImageDraw.Draw(frame)
            fit_text(fd, (W / 2 - 45, ly - 30), "FRIEDRICHSTRASSE", 96, maxw=780, fill=g.AMBER, alpha=int(255 * kl))
            g.text(fd, (W / 2 - 45, ly + 60), "THE ONLY STOP", 58, alpha=int(255 * g.ramp(t, t_name + 0.35, 0.35)))
        out.write(frame)


# ---------------------------------------------------------------- 2. one station, two countries

def train(dr, x, y, w, h, alpha=255):
    """Side view of a lit West Berlin train (two cars)."""
    for c in range(2):
        x0 = x + c * (w / 2 + 8)
        x1 = x0 + w / 2 - 8
        dr.rounded_rectangle([x0, y, x1, y + h], 16, fill=(232, 205, 120, alpha), outline=(0, 0, 0, alpha), width=4)
        nwin = 5
        for i in range(nwin):
            wx0 = x0 + 18 + i * (x1 - x0 - 36) / nwin
            dr.rectangle([wx0 + 5, y + 16, wx0 + (x1 - x0 - 36) / nwin - 5, y + h * 0.55], fill=(255, 238, 190, alpha))
        dr.rectangle([x0 + 6, y + h * 0.7, x1 - 6, y + h * 0.78], fill=(150, 110, 50, alpha))


def box_label(dr, cx, cy, w, h, s, k, lit, alpha=255):
    a = int(alpha * k)
    if a <= 0:
        return
    edge = g.mix((90, 90, 90), RED, lit)
    dr.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 18, fill=(22, 22, 24, a), outline=(*edge, a), width=6)
    fit_text(dr, (cx, cy + 2), s, 50, maxw=w - 30, fill=g.mix(g.INK, g.AMBER, lit), alpha=a)


def split_s4(args, d, timing, base, out):
    W, H = g.W, g.H
    wt = lambda s, lag=0.12: g.word_time(timing, s, lag)
    t_wall = wt("steel")
    t_border = wt("border crossing")
    t_east = wt("East Germany")
    t_pass = wt("passport")
    t_search = wt("searches")
    t_int = wt("interrogation")
    bg = g.vignette_bg()
    WY = 690                    # the wall
    GATE = 140                  # gap in the wall where the controls begin
    path = [(GATE, WY), (GATE, 960), (720, 960), (720, 1250), (540, 1250), (540, 1305)]
    PASS, SEARCH, INTER = (360, 960), (720, 1100), (300, 1180)
    for t in g.frames(d):
        img = bg.copy().convert("RGBA")
        dr = ImageDraw.Draw(img)
        # --- West: platforms and a train that pulls in and stops
        kw = g.ramp(t, 0.0, 0.4)
        a = int(255 * kw)
        g.text(dr, (W / 2 - 40, 300), "WEST BERLIN TRAINS", 66, fill=WESTC, alpha=a)
        dr.rectangle([90, 400, 900, 438], fill=(70, 70, 74, a))
        dr.rectangle([90, 600, 900, 638], fill=(70, 70, 74, a))
        for yy in (470, 568):
            dr.line([90, yy, 900, yy], fill=(55, 55, 58, a), width=4)
        u = g.smooth(t / 1.6)
        tx = -900 + (150 + 900) * u
        train(dr, tx, 452, 740, 130, a)
        # --- the wall of steel and glass
        kwall = g.ramp(t, t_wall - 0.25, 0.7)
        if kwall > 0:
            x1 = 90 + (900 - 90) * kwall
            dr.rectangle([90, WY - 22, x1, WY + 22], fill=(0, 0, 0, 255))
            dr.rectangle([90, WY - 16, x1, WY + 16], fill=(*STEEL, 255))
            for xx in range(110, int(x1) - 20, 70):
                dr.rectangle([xx, WY - 10, xx + 50, WY + 10], fill=(*GLASS, 200))
            dr.rectangle([GATE - 34, WY - 24, GATE + 34, WY + 24], fill=(14, 14, 15, 255))   # the control gate
            g.text(dr, (540, WY - 55), "STEEL & GLASS WALL", 44, fill=(200, 205, 212), alpha=int(255 * g.ramp(t, t_wall + 0.2, 0.4)))
        # --- East: border crossing
        kb = g.ramp(t, t_border - 0.1, 0.4)
        if kb > 0:
            fit_text(dr, (560, 800), "BORDER CROSSING", 84, maxw=700, fill=g.AMBER, alpha=int(255 * kb))
        ke = g.ramp(t, t_east - 0.1, 0.4)
        # path through the controls, drawn as the narrator names them
        kp = g.clamp((t - (t_pass - 0.5)) / max(t_int + 0.9 - (t_pass - 0.5), 0.1))
        if kp > 0:
            pts = g.sub_polyline(path, g.smooth(kp))
            dr.line(pts, fill=(0, 0, 0, 255), width=26, joint="curve")
            dr.line(pts, fill=(*RED, 255), width=14, joint="curve")
            ex, ey = pts[-1]
            dr.ellipse([ex - 16, ey - 16, ex + 16, ey + 16], fill=(255, 235, 225, 255), outline=(0, 0, 0, 255), width=4)
        if t > t_int - 0.2:   # dashed side branch into the interrogation room
            kd = g.ramp(t, t_int - 0.2, 0.5)
            x_a, x_b = 720, INTER[0] + 190
            xe = x_a + (x_b - x_a) * kd
            xx = x_a
            while xx > xe:
                dr.line([xx, INTER[1], max(xe, xx - 26), INTER[1]], fill=(*RED, 255), width=10)
                xx -= 46
        box_label(dr, *PASS, 330, 100, "PASSPORTS", g.ramp(t, t_pass - 0.3, 0.3), g.ramp(t, t_pass, 0.3))
        box_label(dr, *SEARCH, 300, 100, "SEARCH", g.ramp(t, t_search - 0.3, 0.3), g.ramp(t, t_search, 0.3))
        box_label(dr, *INTER, 380, 100, "INTERROGATION", g.ramp(t, t_int - 0.3, 0.3), g.ramp(t, t_int, 0.3))
        if ke > 0:
            fit_text(dr, (500, 1385), "EAST GERMANY", 76, maxw=700, fill=g.AMBER, alpha=int(255 * ke))
        out.write(img)


GRAPHICS = {"map_s4": map_s4, "split_s4": split_s4}
