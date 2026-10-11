"""Portrait (1080x1920) archive-photo graphic for STRATA Short #5 'Frozen for 28 years' (loaded by assemble.py via the
visual's "module"). Like graphics2d.g_photo, but with timed camera keys (hold, then pan) and a red ring drawn in photo
coordinates, so the ring stays glued to its subject while the frame moves.

args: file; keys: [[t_s, z, cx, cy], ...] (z/cx/cy as in assemble's image visuals, eased between keys);
      ring: {"c": [x, y], "r": [rx, ry]} in source-photo pixels, "at": seconds (or "word" to time it to the narration);
      lift: brightness multiplier (phones).
"""
import math, os

from PIL import Image, ImageDraw

import graphics2d as g

RED = (230, 42, 42)


def cam_at(keys, t):
    if t <= keys[0][0]:
        return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            u = g.smooth((t - a[0]) / max(b[0] - a[0], 1e-6))
            return [a[i] + (b[i] - a[i]) * u for i in (1, 2, 3)]
    return keys[-1][1:]



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


def photo_s5(args, d, timing, base, out):
    W, H = g.W, g.H
    src = Image.open(os.path.join(base, args["file"])).convert("L").convert("RGB")
    s = max(W * 2 / src.width, H * 2 / src.height)
    big = src.resize((int(src.width * s), int(src.height * s)), Image.LANCZOS)
    keys = args.get("keys", [[0, 1.0, 0.5, 0.5], [d, 1.1, 0.5, 0.5]])
    ring = args.get("ring")
    if ring:
        at = ring.get("at", 0.4)
        t_ring = g.word_time(timing, at) if isinstance(at, str) else at
    lift = args.get("lift", 1.06)
    lut = [int(min(255, v * lift)) for v in range(256)] * 3
    for t in g.frames(d):
        z, cx, cy = cam_at(keys, t)
        cw, ch = big.width / z, big.width / z * H / W
        if ch > big.height / z:
            ch = big.height / z
            cw = ch * W / H
        left = min(max(cx * big.width - cw / 2, 0), big.width - cw)
        top = min(max(cy * big.height - ch / 2, 0), big.height - ch)
        frame = big.transform((W, H), Image.EXTENT, (left, top, left + cw, top + ch), Image.BICUBIC).point(lut)
        if ring:
            k = g.ramp(t, t_ring, 0.26)
            if k > 0:
                px = (ring["c"][0] * s - left) * W / cw
                py = (ring["c"][1] * s - top) * H / ch
                rx, ry = ring["r"][0] * s * W / cw, ring["r"][1] * s * H / ch
                # red arrow from the lower left to the subject's lower-left edge (user 2026-10-12: arrows, not circles)
                tx, ty = px - rx * 0.55, py + ry * 1.05
                ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                od = ImageDraw.Draw(ov)
                red_arrow(od, max(60, tx - 240), ty + 250, tx, ty, k)
                frame = Image.alpha_composite(frame.convert("RGBA"), ov).convert("RGB")
        out.write(frame)


GRAPHICS = {"photo_s5": photo_s5}
