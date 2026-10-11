"""Profile (user 2026-10-11): white donut box seen at 45 degrees, lid slightly open, pretzel inside, white bg.
Orthographic 3D box drawn face by face (back to front) with PIL; the pretzel is mapped onto the box floor."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import common as C
D = "/mnt/project-files/fast_german/branding/final/"
S, K = 800, 3
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
    right = [L(hx, -hz), L(hx, hz), L(hx, hz, flap), L(hx, -hz, flap)]
    return top, front, right


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
    pz = C.icon("pretzel", 470).resize((470 * K, 470 * K), Image.LANCZOS)
    m = 0.06
    y = 0.02
    corners = [(-BW / 2 + m, y, -BD / 2 + m), (BW / 2 - m, y, -BD / 2 + m), (-BW / 2 + m, y, BD / 2 - m)]
    dst = np.array([proj(p) for p in corners])            # screen positions of image corners (0,0),(w,0),(0,h)
    w, h = pz.size
    src = np.array([(0, 0), (w, 0), (0, h)], float)
    # affine screen -> image for PIL (inverse map)
    A = np.hstack([dst, np.ones((3, 1))])
    cx = np.linalg.solve(A, src[:, 0]); cy = np.linalg.solve(A, src[:, 1])
    out = pz.transform(im.size, Image.AFFINE, (*cx, *cy), Image.BICUBIC)
    sh = out.split()[3].point(lambda v: v * 60 // 255).filter(ImageFilter.GaussianBlur(9 * K))
    im.paste((120, 110, 100), (0, int(10 * K)), sh)
    im.alpha_composite(out)


def profile(theta_deg=42):
    th = math.radians(theta_deg)
    im = Image.new("RGBA", (S * K, S * K), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    hx, hz = BW / 2, BD / 2
    # ground shadow
    sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).polygon([proj(p) for p in [(-hx - .05, 0, -hz - .05), (hx + .1, 0, -hz), (hx + .1, 0, hz + .1), (-hx, 0, hz + .1)]], fill=110)
    im.paste((60, 60, 70), (0, 0), sh.filter(ImageFilter.GaussianBlur(22 * K)))
    top, front, right = lid_pts(th)
    if theta_deg > 70:                       # lid leaning back: its inner side shows, behind the box
        face(d, right, (206, 207, 212))
        face(d, top, (240, 240, 238))
        face(d, front, (226, 226, 224))
    # inside: floor, back + left inner walls
    face(d, [(-hx, 0, -hz), (hx, 0, -hz), (hx, 0, hz), (-hx, 0, hz)], (238, 236, 232))
    face(d, [(-hx, 0, -hz), (hx, 0, -hz), (hx, BH, -hz), (-hx, BH, -hz)], (214, 212, 208))
    face(d, [(-hx, 0, -hz), (-hx, 0, hz), (-hx, BH, hz), (-hx, BH, -hz)], (226, 224, 220))
    pretzel_on_floor(im)
    d = ImageDraw.Draw(im)
    # outer walls facing us: front (+z) and right (+x)
    face(d, [(-hx, 0, hz), (hx, 0, hz), (hx, BH, hz), (-hx, BH, hz)], (244, 244, 242))
    face(d, [(hx, 0, -hz), (hx, 0, hz), (hx, BH, hz), (hx, BH, -hz)], (212, 213, 218))
    dots(d, [(-hx, 0.03, hz), (hx, 0.03, hz), (hx, BH - 0.03, hz), (-hx, BH - 0.03, hz)], (8, 2), 0.022)
    dots(d, [(hx, 0.03, hz), (hx, 0.03, -hz), (hx, BH - 0.03, -hz), (hx, BH - 0.03, hz)], (8, 2), 0.022,
         (236, 186, 30))
    # lid
    if theta_deg > 70:
        return im.resize((S, S), Image.LANCZOS)
    face(d, right, (206, 207, 212))
    face(d, top, (252, 252, 251))
    dots(d, top, (6, 6), 0.026)
    face(d, front, (236, 236, 234))
    dots(d, front, (8, 1), 0.018, (236, 186, 30))
    return im.resize((S, S), Image.LANCZOS)


if __name__ == "__main__":
    profile(20).convert("RGB").save(D + "profile_box45_A_ajar.png")
    SCALE, OY = 350, 560
    profile(105).convert("RGB").save(D + "profile_box45_B_open.png")
