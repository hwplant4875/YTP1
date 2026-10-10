"""Banner (2026-10-10, user): just a highway. The road fills the mobile crop (1546x423) and runs the full width;
the rest of the 2560x1440 canvas is a plain grey that continues the road's tone."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageDraw
from branding_v4 import W, H, CX, CY, SAFE
from branding_v5 import asphalt, worn, dashes, YEL
from branding_v10 import hblur, PAINT
D = "/mnt/project-files/fast_german/branding/final/"


def banner():
    rnd = np.random.default_rng(3)
    yy = np.linspace(-1, 1, H)[:, None]
    grey = 92 - 22 * np.abs(yy)                                    # soft grey, a touch darker toward the edges
    bg = np.repeat((grey + rnd.normal(0, 3, (H, W)))[..., None], 3, axis=2) + np.array([0, 1, 4])
    im = Image.fromarray(bg.clip(0, 255).astype("uint8")).convert("RGBA")
    top, bot = SAFE[1], SAFE[3]                                     # road = exactly the mobile crop height
    im.alpha_composite(asphalt(W, bot - top, 9), (0, top))
    d = ImageDraw.Draw(im)
    d.rectangle((0, top, W, top + 10), fill=(150, 152, 156, 255)); d.rectangle((0, bot - 10, W, bot), fill=(150, 152, 156, 255))  # kerbs
    for y in (top + 26, bot - 46):
        d.rectangle((0, y, W, y + 20), fill=PAINT + (255,))                                         # edge lines
    d.rectangle((0, CY - 15, W, CY - 5), fill=YEL + (255,)); d.rectangle((0, CY + 5, W, CY + 15), fill=YEL + (255,))  # centre line
    lane = (CY - 5 - (top + 46)) / 2
    for y in (int(top + 46 + lane), int(CY + 15 + lane)):
        im.alpha_composite(worn(dashes(W + 600, 16, 260, 380, PAINT), y), (-(y * 7) % 600, y - 8))
    road = im.crop((0, top - 4, W, bot + 4))
    road = hblur(road.convert("RGB"), 30).convert("RGBA")             # motion: the road rushes past
    im.alpha_composite(road, (0, top - 4))
    # soft shadow above and below the road strip so it sits on the grey
    sh = np.zeros((H, W, 4), np.uint8)
    for k in range(40):
        a = int(70 * (1 - k / 40) ** 2)
        sh[top - 4 - k, :, 3] = a; sh[bot + 4 + k, :, 3] = a
    im.alpha_composite(Image.fromarray(sh))
    return im


if __name__ == "__main__":
    im = banner()
    im.convert("RGB").save(D + "banner_fast_german.png")
    im.crop(SAFE).convert("RGB").save(D + "banner_mobile_view.png")
    print("ok")
