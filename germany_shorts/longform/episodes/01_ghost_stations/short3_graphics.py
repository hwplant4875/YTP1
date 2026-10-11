"""Portrait (1080x1920) money graphics for STRATA Short #3 'West Berlin paid the East' (loaded by assemble.py via the
visual's "module"). Re-lays out the episode's g_money (graphics2d.py) for a vertical frame and adds an S-Bahn ridership
graphic. Everything important stays in x 90..900, y 220..1400: clear of the Shorts top bar, the right-hand buttons and
the bottom 25 % (title / channel area).

Figures (research_ghost.md, S3/S1/S6): monthly fee 181,132 DM (1963-70) rising to 495,756 DM (Apr 1989 - Jun 1990),
i.e. ~5.95 million DM a year; S-Bahn ridership in West Berlin from ~500,000 a day to under 50,000 after the boycott.
"""
import math

from PIL import Image, ImageDraw

import graphics2d as g

RED = (230, 42, 42)


def fit_text(dr, xy, s, size, maxw=860, **k):
    """g.text, shrunk so the line never exceeds maxw pixels (no text off-frame)."""
    while size > 40 and g.font(size).getlength(s) + 2 * max(3, int(size * 0.07)) > maxw:
        size -= 4
    g.text(dr, xy, s, size, **k)


def red_arrow_down(dr, x, y0, y1, k=1.0, w=26, alpha=255):
    """Red arrow pointing down, drawn from y0 to y0 + (y1 - y0) * k, black edge."""
    if k <= 0:
        return
    ye = y0 + (y1 - y0) * k
    hh = 70
    shaft = max(y0, ye - hh)
    dr.line([x, y0, x, shaft], fill=(0, 0, 0, alpha), width=w + 12)
    dr.polygon([(x - 62, ye - hh - 6), (x + 62, ye - hh - 6), (x, ye + 8)], fill=(0, 0, 0, alpha))
    dr.line([x, y0, x, shaft], fill=(*RED, alpha), width=w)
    dr.polygon([(x - 50, ye - hh), (x + 50, ye - hh), (x, ye - 4)], fill=(*RED, alpha))



def red_arrow(dr, x0, y0, x1, y1, k=1.0, alpha=255):
    """Red arrow from (x0, y0) to the tip (x1, y1), black edge, grows in (user 2026-10-12: arrows, not circles)."""
    import math
    if k <= 0:
        return
    k = min(k, 1.0)
    L = math.hypot(x1 - x0, y1 - y0) * (0.4 + 0.6 * k)
    ux, uy = (x1 - x0) / math.hypot(x1 - x0, y1 - y0), (y1 - y0) / math.hypot(x1 - x0, y1 - y0)
    tx, ty = x1, y1
    sx, sy = tx - ux * L, ty - uy * L
    sw, hw, hl = 16, 46, 80
    nx, ny = -uy, ux
    bx, by = tx - ux * hl, ty - uy * hl
    pts = [(sx + nx * sw, sy + ny * sw), (bx + nx * sw, by + ny * sw), (bx + nx * hw, by + ny * hw), (tx, ty),
           (bx - nx * hw, by - ny * hw), (bx - nx * sw, by - ny * sw), (sx - nx * sw, sy - ny * sw)]
    a = int(alpha * k)
    dr.line(pts + [pts[0]], fill=(0, 0, 0, a), width=12, joint="curve")
    dr.polygon(pts, fill=(*RED, a))


def ring(dr, cx, cy, rx, ry, k=1.0, alpha=255):
    """Red ellipse (pops in), black edge."""
    if k <= 0:
        return
    s = 1.3 - 0.3 * k
    box = [cx - rx * s, cy - ry * s, cx + rx * s, cy + ry * s]
    dr.ellipse(box, outline=(0, 0, 0, int(alpha * k)), width=18)
    dr.ellipse(box, outline=(*RED, int(alpha * k)), width=11)


def flow_down(img, p0, p1, t, n=6, swing=150, speed=0.45, alpha=1.0, scale=0.3):
    """Notes travelling from p0 down to p1 along a sideways arc."""
    for i in range(n):
        u = (t * speed + i / n) % 1.0
        a = math.sin(u * math.pi) * alpha
        x = p0[0] + (p1[0] - p0[0]) * u + swing * math.sin(u * math.pi) * (1 if i % 2 else -1)
        y = p0[1] + (p1[1] - p0[1]) * u
        g.paste_note(img, x, y, scale, math.sin(u * 6 + i) * 18, a, seed=i % 3 + 1)


def money_s3(args, d, timing, base, out):
    wt = lambda s: g.word_time(timing, s)
    t_bill = wt("sent a bill")
    t63 = wt("1963")
    t_month = wt("Every month")
    t180 = wt("hundred and eighty")
    t89 = wt("By 1989")
    t_year = wt("six million")
    t_wall = wt("walled them in")
    W, H = g.W, g.H
    bg = g.vignette_bg()
    years = list(range(1963, 1990))
    # fee per month: 181,132 DM (1963) rising to 495,756 DM (1989), two published figures, steps in between interpolated
    fee = {y: 181132 + (495756 - 181132) * ((y - 1963) / 26) ** 1.25 for y in years}
    for t in g.frames(d):
        img = bg.copy().convert("RGBA")
        dr = ImageDraw.Draw(img)
        # 1. West Berlin -> East Germany, every month
        k1 = g.ramp(t, 0.0, 0.45) * (1 - g.ramp(t, t180 - 0.5, 0.3))
        if k1 > 0:
            ky = g.ramp(t, t63 - 0.1, 0.35)
            if ky > 0:
                g.text(dr, (W / 2, 350), "1963", 200, fill=g.AMBER, alpha=int(255 * ky * k1))
            g.text(dr, (W / 2, 560), "WEST BERLIN", 92, alpha=int(255 * k1))
            dr = ImageDraw.Draw(img)
            ka = g.ramp(t, t_bill - 0.2, 0.6)
            red_arrow_down(dr, W / 2, 650, 1050, ka, alpha=int(255 * k1))
            flow_down(img, (W / 2, 680), (W / 2, 1040), t, alpha=k1 * g.ramp(t, t_bill - 0.2, 0.4))
            dr = ImageDraw.Draw(img)
            g.text(dr, (W / 2, 1150), "EAST GERMANY", 92, fill=g.AMBER, alpha=int(255 * k1))
            km = g.ramp(t, t_month - 0.1, 0.35)
            if km > 0:
                g.text(dr, (W / 2, 1300), "EVERY MONTH", 96, alpha=int(255 * km * k1))
        # 2. the fee grows, 1963 -> 1989
        k2 = g.ramp(t, t180 - 0.2, 0.35) * (1 - g.ramp(t, t_wall - 0.6, 0.3))   # phases never overlap
        if k2 > 0:
            x0, x1, yb, hmax = 150, 830, 1250, 560
            grow = g.smooth((t - t89 + 0.15) / 1.8)
            nshow = 1 + int(grow * (len(years) - 1))
            for i, y in enumerate(years[:nshow]):
                x = x0 + (x1 - x0) * i / (len(years) - 1)
                hgt = fee[y] / 495756 * hmax
                col = g.AMBER if i in (0, len(years) - 1) else (150, 120, 80)
                g.bar(dr, x, yb, 19, hgt * g.ramp(t, t180 + 0.1, 0.35), col, int(255 * k2))
            dr.line([x0 - 30, yb, x1 + 30, yb], fill=(*g.GREY, int(255 * k2)), width=3)
            g.text(dr, (x0 + 10, yb + 55), "1963", 54, alpha=int(255 * k2))
            if grow > 0.98:
                g.text(dr, (x1 - 10, yb + 55), "1989", 54, alpha=int(255 * k2))
                # red arrow at the top of the 1989 bar
                red_arrow(dr, x1 - 330, yb - hmax - 40, x1 - 30, yb - hmax + 30, g.ramp(t, t89 + 1.9, 0.3), alpha=int(255 * k2))
            if t < t_year - 0.15:
                val = 181132 + (495756 - 181132) * grow if t > t89 - 0.15 else 181132 * g.smooth((t - t180) / 1.0)
                fit_text(dr, (W / 2, 360), f"{int(val):,} DM", 170, fill=g.AMBER, alpha=int(255 * k2))
                g.text(dr, (W / 2, 500), "PER MONTH", 72, alpha=int(255 * k2))
            else:
                ky = g.ramp(t, t_year - 0.15, 0.35)
                fit_text(dr, (W / 2, 360), "~6 MILLION DM", 170, fill=g.AMBER, alpha=int(255 * k2 * ky))
                g.text(dr, (W / 2, 500), "PER YEAR", 72, alpha=int(255 * k2 * ky))
        # 3. paid to the country that walled them in: West Berlin inside a ring of wall, the money leaving it
        k3 = g.ramp(t, t_wall - 0.3, 0.35)
        if k3 > 0:
            cx, cy, R = W / 2, 700, 250
            a = int(255 * k3)
            dr.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(0, 0, 0, a), width=46)
            dr.ellipse([cx - R + 4, cy - R + 4, cx + R - 4, cy + R - 4], outline=(118, 114, 106, a), width=36)
            for j in range(48):   # wall segments
                ang = j / 48 * 2 * math.pi
                c, s = math.cos(ang), math.sin(ang)
                dr.line([cx + c * (R - 38), cy + s * (R - 38), cx + c * (R - 2), cy + s * (R - 2)], fill=(52, 50, 47, a), width=3)
            g.text(dr, (cx, cy - 20), "WEST", 96, alpha=a)
            g.text(dr, (cx, cy + 70), "BERLIN", 96, alpha=a)
            flow_down(img, (cx, cy + 120), (cx, 1180), t, n=6, swing=120, speed=0.5, alpha=k3, scale=0.26)
            dr = ImageDraw.Draw(img)
            g.text(dr, (cx, 1290), "EAST GERMANY", 92, fill=g.AMBER, alpha=a)
        out.write(img)


def person(dr, cx, cy, s, col, alpha=255):
    dr.ellipse([cx - 16 * s, cy - 70 * s, cx + 16 * s, cy - 38 * s], fill=(*col, alpha))
    dr.rounded_rectangle([cx - 26 * s, cy - 32 * s, cx + 26 * s, cy + 30 * s], int(14 * s), fill=(*col, alpha))


def riders_s3(args, d, timing, base, out):
    wt = lambda s: g.word_time(timing, s)
    t_half = wt("half a million")
    t_50 = wt("under fifty")
    W, H = g.W, g.H
    bg = g.vignette_bg()
    for t in g.frames(d):
        img = bg.copy().convert("RGBA")
        dr = ImageDraw.Draw(img)
        k0 = g.ramp(t, 0.0, 0.4)
        g.text(dr, (W / 2, 300), "S-BAHN RIDERS", 92, alpha=int(255 * k0))
        g.text(dr, (W / 2, 390), "PER DAY", 60, fill=g.GREY, alpha=int(255 * k0))
        kd = g.ramp(t, t_50 - 0.25, 0.5)   # the collapse
        # 500,000 (turns grey and is struck through)
        kh = g.ramp(t, t_half - 0.2, 0.35)
        col = g.mix(g.AMBER, (120, 116, 110), kd)
        g.text(dr, (W / 2, 560), "500,000", 170, fill=col, alpha=int(255 * kh))
        if kd > 0:
            wline = g.font(170).getlength("500,000") / 2 + 20
            xa, xb = W / 2 - wline, W / 2 - wline + 2 * wline * kd
            dr.line([xa, 575, xb, 545], fill=(0, 0, 0, 255), width=26)
            dr.line([xa, 575, xb, 545], fill=(*RED, 255), width=16)
        red_arrow_down(dr, W / 2, 660, 800, kd)
        kn = g.ramp(t, t_50 - 0.05, 0.35)
        if kn > 0:
            g.text(dr, (W / 2, 900), "< 50,000", 170, fill=g.AMBER, alpha=int(255 * kn))
        # ten riders, each ~50,000: nine go dark
        for i in range(10):
            r, c = divmod(i, 5)
            x = 220 + c * 150
            y = 1140 + r * 170
            lit = 1.0 if i == 0 else 1 - g.ramp(t, t_50 - 0.25 + 0.06 * i, 0.3)
            pc = g.mix((60, 58, 55), g.AMBER if i == 0 else g.INK, lit)
            person(dr, x, y, 1.25, pc, int(255 * g.ramp(t, t_half - 0.2 + 0.03 * i, 0.3)))
        out.write(img)


GRAPHICS = {"money_s3": money_s3, "riders_s3": riders_s3}
