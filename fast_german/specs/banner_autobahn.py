"""Banner (2026-10-10, user): a real Autobahn, no blur. Top-down, 2 lanes each way (4 lanes), hard shoulders,
grass median with a steel guard-rail. All markings white (yellow only marks roadworks in Germany): solid edge lines,
lane dashes 6 m long with 12 m gaps. The road exactly fills the mobile crop; grey elsewhere."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageDraw
from branding_v4 import W, H, CX, CY, SAFE
from branding_v5 import asphalt, worn
D = "/mnt/project-files/fast_german/branding/final/"
PX = 15.5            # pixels per metre (423 px crop ≈ 27 m of road cross-section)
LINE = (240, 240, 236)


def grey_bg():
    rnd = np.random.default_rng(3)
    yy = np.linspace(-1, 1, H)[:, None]
    g = 92 - 22 * np.abs(yy) + rnd.normal(0, 3, (H, W))
    return Image.fromarray(np.repeat(g[..., None], 3, 2).clip(0, 255).astype("uint8")).convert("RGBA")


def carriageway(h, seed, flip=False):
    """One direction: hard shoulder, edge line, two lanes split by dashes, inner edge line, narrow inner strip."""
    im = asphalt(W, h, seed)
    d = ImageDraw.Draw(im)
    shoulder, edge, lane, inner = int(2.6 * PX), int(0.3 * PX) + 2, int(3.75 * PX), int(0.5 * PX)
    y = shoulder
    rows = []
    d.rectangle((0, y, W, y + edge), fill=LINE + (255,)); y += edge           # outer edge line (solid)
    y += lane
    rows.append(y)                                                             # lane divider
    y += lane
    d.rectangle((0, y, W, y + edge), fill=LINE + (255,))                      # inner edge line (solid)
    dash, gap, th = int(6 * PX), int(12 * PX), int(0.15 * PX) + 3
    for yy in rows:
        x = -(seed * 97) % (dash + gap)
        while x < W:
            d.rectangle((x, yy - th // 2, x + dash, yy + th // 2), fill=LINE + (255,)); x += dash + gap
    im = worn(im, seed, 0.0)
    return im.transpose(Image.FLIP_TOP_BOTTOM) if flip else im


def guardrail(w, h):
    """Steel W-beam rail seen from above, posts every 2 m."""
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    d.rectangle((0, h // 2 - 5, w, h // 2 + 5), fill=(188, 192, 198, 255))
    d.line((0, h // 2 - 5, w, h // 2 - 5), fill=(230, 232, 236, 255), width=2)
    d.line((0, h // 2 + 5, w, h // 2 + 5), fill=(120, 124, 130, 255), width=2)
    for x in range(0, w, int(2 * PX)):
        d.rectangle((x, h // 2 - 3, x + 5, h // 2 + 3), fill=(90, 92, 96, 255))
    return im


def banner():
    im = grey_bg()
    top, bot = SAFE[1], SAFE[3]
    total = bot - top
    side = int(2.6 * PX) + (int(0.3 * PX) + 2) * 2 + int(3.75 * PX) * 2 + int(0.5 * PX)
    median = total - 2 * side
    # grass median with a little texture
    rnd = np.random.default_rng(5)
    g = np.array([78, 118, 62], float)[None, None, :] + rnd.normal(0, 9, (median, W, 1))
    grass = Image.fromarray(g.clip(0, 255).astype("uint8")).convert("RGBA")
    im.alpha_composite(carriageway(side, 1), (0, top))                  # top carriageway: hard shoulder at the outer (top) edge
    im.alpha_composite(grass, (0, top + side))
    im.alpha_composite(guardrail(W, median), (0, top + side))
    im.alpha_composite(carriageway(side, 2, flip=True), (0, top + side + median))   # mirrored: shoulder at the bottom
    # outer guard-rails on the verge edge, and a soft shadow so the strip sits on the grey
    for y in (top - 10, bot - 10):
        im.alpha_composite(guardrail(W, 20), (0, y))
    sh = np.zeros((H, W, 4), np.uint8)
    for k in range(36):
        a = int(60 * (1 - k / 36) ** 2)
        sh[top - 1 - k, :, 3] = a; sh[bot + k, :, 3] = a
    im.alpha_composite(Image.fromarray(sh))
    return im


if __name__ == "__main__":
    im = banner()
    im.convert("RGB").save(D + "banner_fast_german.png")
    im.crop(SAFE).convert("RGB").save(D + "banner_mobile_view.png")
    print("ok")
