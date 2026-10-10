"""Final branding (2026-10-10): one profile + one banner. Night Autobahn, forward-leaning road paint with a motion smear."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageFilter
import banner_road as B, profile_speed as P
D = "/mnt/project-files/fast_german/branding/final/"
W, H, CX, CY = B.W, B.H, B.CX, B.CY
P.final().convert("RGB").save(D + "profile_fast_german.png")
im = B.asphalt(W, H, base=(22, 24, 30), seed=2, night=True)
paint = Image.new("RGBA", (W, H)); B.markings(paint, (250, 250, 240))
yy, xx = np.mgrid[0:H, 0:W]
light = np.exp(-((yy - CY) / 520.0) ** 2) * (0.45 + 0.55 * np.clip(xx / W * 1.4, 0, 1))
paint.putalpha(Image.fromarray((np.array(paint.split()[3], float) * (0.35 + 0.65 * light)).astype("uint8")))
im.alpha_composite(paint.filter(ImageFilter.GaussianBlur(10))); im.alpha_composite(paint)
im.alpha_composite(B.streaks((W, H), [(255, 60, 50)], 45, 1, 0, H, (4, 12), (500, 1700), 3))
im.alpha_composite(B.streaks((W, H), [(255, 236, 200)], 45, 2, 0, H, (4, 12), (500, 1700), 3))
t = B.title((250, 250, 240), width=1300)
layer = Image.new("RGBA", (W, H)); layer.alpha_composite(t, (CX - t.width // 2 + 30, CY - t.height // 2))
im.alpha_composite(P.smear(layer, 520)); im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(12))); im.alpha_composite(layer)
B.vignette(im, 0.5).convert("RGB").save(D + "banner_fast_german.png")
