"""Profile (user 2026-10-11): white donut box seen at 45 degrees, lid slightly open, pretzel inside, white bg.
Orthographic 3D box drawn face by face (back to front) with PIL; the pretzel is mapped onto the box floor."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import common as C
D = "/mnt/project-files/fast_german/branding/final/"
S, K = 800, 3
OX_SHIFT = 0
YAW, PITCH = math.radians(42), math.radians(40)
BW, BD, BH = 1.0, 1.0, 0.26          # box width (x), depth (z), height (y)
SCALE, OX, OY = 400, 400, 470


def proj(p):
    x, y, z = p
    xr = x * math.cos(YAW) - z * math.sin(YAW)
    zr = x * math.sin(YAW) + z * math.cos(YAW)
    yr = y * math.cos(PITCH) - zr * math.sin(PITCH)      # +z comes toward the viewer
    return ((OX + xr * SCALE) * K, (OY - yr * SCALE) * K)


EDGE = (196, 196, 200)


def face(d, pts, fill, outline=EDGE):
    q = [proj(p) for p in pts]
    d.polygon(q, fill=fill)
    if outline:
        d.line(q + [q[0]], fill=outline, width=3 * K, joint="curve")


def lid_pts(theta, flap=0.07):
    """Lid hinged on the back top edge, opened by theta. Returns (top, front flap, left flap, right flap)."""
    def L(x, z, down=0.0):        # z in [-BD/2, BD/2] along the closed lid, down = flap drop
        r = z + BD / 2
        y = BH + r * math.sin(theta) - down * math.cos(theta)
        zz = -BD / 2 + r * math.cos(theta) + down * math.sin(theta)
        return (x, y, zz)
    hx, hz = BW / 2 + 0.012, BD / 2 + 0.012
    top = [L(-hx, -hz), L(hx, -hz), L(hx, hz), L(-hx, hz)]
    front = [L(-hx, hz), L(hx, hz), L(hx, hz, flap), L(-hx, hz, flap)]
    left = [L(-hx, -hz), L(-hx, hz), L(-hx, hz, flap), L(-hx, -hz, flap)]
    right = [L(hx, -hz), L(hx, hz), L(hx, hz, flap), L(hx, -hz, flap)]
    return top, front, left, right


def view():
    return np.array([math.sin(YAW) * math.cos(PITCH), math.sin(PITCH), math.cos(YAW) * math.cos(PITCH)])


def dots(d, quad3d, n=(7, 7), r=0.018, col=(255, 200, 40)):
    """Polka dots spread over a 3D quad (our yellow, not any brand's)."""
    a, b, c, e = [np.array(p) for p in quad3d]
    for i in range(n[0]):
        for j in range(n[1]):
            u, v = (i + 0.5 + 0.5 * (j % 2)) / n[0], (j + 0.5) / n[1]
            if u > 0.95: continue
            p = a + (b - a) * u + (e - a) * v
            cx, cy = proj(p)
            rr = r * SCALE * K
            d.ellipse((cx - rr, cy - rr * 0.75, cx + rr, cy + rr * 0.75), fill=col)


def pretzel_on_floor(im):
    """Pretzel sitting upright in the box, facing the camera; the near walls drawn afterwards hide its bottom."""
    pz = C.icon("pretzel", 330).resize((330 * K, 330 * K), Image.LANCZOS).rotate(-6, Image.BICUBIC, expand=True)
    cx, cy = proj((0.02, 0.20, 0.0))
    x, y = int(cx - pz.width / 2), int(cy - pz.height * 0.62)
    sh = Image.new("L", im.size, 0)
    sh.paste(pz.split()[3].point(lambda v: v * 70 // 255), (x + 14 * K, y + 18 * K))
    im.paste((110, 100, 90), (0, 0), sh.filter(ImageFilter.GaussianBlur(12 * K)))
    im.alpha_composite(pz, (x, y))


def profile(theta_deg=42):
    th = math.radians(theta_deg)
    v = view()
    im = Image.new("RGBA", (S * K, S * K), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    hx, hz = BW / 2, BD / 2
    sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).polygon([proj(p) for p in [(-hx - .06, 0, -hz - .06), (hx + .06, 0, -hz - .06),
                                                  (hx + .06, 0, hz + .06), (-hx - .06, 0, hz + .06)]], fill=110)
    im.paste((60, 60, 70), (0, 0), sh.filter(ImageFilter.GaussianBlur(22 * K)))
    walls = {"front": ((0, 0, 1), [(-hx, 0, hz), (hx, 0, hz), (hx, BH, hz), (-hx, BH, hz)]),
             "back": ((0, 0, -1), [(-hx, 0, -hz), (hx, 0, -hz), (hx, BH, -hz), (-hx, BH, -hz)]),
             "right": ((1, 0, 0), [(hx, 0, -hz), (hx, 0, hz), (hx, BH, hz), (hx, BH, -hz)]),
             "left": ((-1, 0, 0), [(-hx, 0, -hz), (-hx, 0, hz), (-hx, BH, hz), (-hx, BH, -hz)])}
    light = np.array([-0.5, 0.8, 0.45]); light /= np.linalg.norm(light)

    def shade(n, base=248, amb=0.80):
        k = amb + (1 - amb) * max(0, float(np.dot(n, light)))
        return tuple(int(base * k * c) for c in (1.0, 1.0, 1.01))

    top, front, left, right = lid_pts(th)
    lid_n = np.array([0, math.cos(th), math.sin(th)])            # lid top normal
    side = left if v[0] < 0 else right
    lid_behind = theta_deg > 70
    if lid_behind:
        face(d, side, shade(np.array([np.sign(v[0]), 0, 0]), 236))
        face(d, top, (236, 236, 238))
        face(d, front, shade(np.array([0, -math.sin(th), math.cos(th)]), 236))
    # inner walls (seen from inside), floor, pretzel
    for n, q in walls.values():
        if np.dot(n, v) < 0:
            face(d, q, shade(-np.array(n), 232, 0.72))
    face(d, [(-hx, 0, -hz), (hx, 0, -hz), (hx, 0, hz), (-hx, 0, hz)], (238, 236, 232))
    pretzel_on_floor(im)
    d = ImageDraw.Draw(im)
    for n, q in walls.values():
        if np.dot(n, v) > 0:
            face(d, q, shade(np.array(n)))
    if not lid_behind:
        face(d, side, shade(np.array([np.sign(v[0]), 0, 0]), 236))
        face(d, top, shade(lid_n, 252))
        face(d, front, shade(np.array([0, -math.sin(th), math.cos(th)]), 240))
    return im.resize((S, S), Image.LANCZOS)


if __name__ == "__main__":
    YAW, PITCH = math.radians(42 - 90), math.radians(24)
    SCALE, OY = 360, 540
    for a in (65,):
        profile(a).convert("RGB").save(D + f"profile_box_left_{a}.png")
