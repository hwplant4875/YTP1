"""Paint a faded, cracked Victorian oil portrait (procedural, no source image) for the room."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 600, 800
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "generated", "portrait.png")
rng = np.random.default_rng(4)

yy, xx = np.mgrid[0:H, 0:W] / np.array([H, W])[:, None, None]
# dark umber ground, lighter behind the head (classic portrait vignette)
glow = np.exp(-(((xx - 0.5) / 0.35) ** 2 + ((yy - 0.32) / 0.3) ** 2))
base = np.stack([0.10 + 0.16 * glow, 0.08 + 0.12 * glow, 0.05 + 0.07 * glow], -1)
img = Image.fromarray((base * 255).astype(np.uint8))
d = ImageDraw.Draw(img)
# dark coat, shoulders, white collar, pale face, dark swept hair
d.ellipse([60, 470, 540, 1100], fill=(22, 18, 15))
d.polygon([(250, 470), (300, 560), (350, 470), (330, 450), (270, 450)], fill=(175, 160, 130))
d.rectangle([268, 380, 332, 470], fill=(150, 118, 92))
d.ellipse([215, 170, 385, 410], fill=(178, 142, 112))
d.ellipse([205, 140, 395, 290], fill=(30, 22, 17))
d.ellipse([222, 205, 378, 420], fill=(182, 146, 116))
# shadowed eye sockets / nose / mouth, kept vague
for ex in (262, 338):
    d.ellipse([ex - 20, 278, ex + 20, 300], fill=(105, 76, 58))
    d.ellipse([ex - 6, 284, ex + 6, 294], fill=(40, 28, 22))
d.polygon([(300, 300), (288, 345), (312, 345)], fill=(140, 104, 82))
d.line([(278, 372), (322, 372)], fill=(110, 70, 58), width=4)
img = img.filter(ImageFilter.GaussianBlur(6))

a = np.asarray(img).astype(np.float32) / 255
# brush texture, yellowed varnish, fading
a *= 1 + 0.08 * rng.normal(size=(H, W, 1)).astype(np.float32)
a = a * np.array([1.0, 0.9, 0.62]) + np.array([0.03, 0.025, 0.0])
a = 0.55 * a + 0.45 * a.mean(-1, keepdims=True) * np.array([1.0, 0.93, 0.78])
# craquelure: thin dark crack network
cr = Image.new("L", (W, H), 0)
cd = ImageDraw.Draw(cr)
for _ in range(900):
    x, y = rng.uniform(0, W), rng.uniform(0, H)
    ang = rng.uniform(0, 2 * np.pi)
    for _ in range(rng.integers(2, 6)):
        nx, ny = x + 14 * np.cos(ang), y + 14 * np.sin(ang)
        cd.line([(x, y), (nx, ny)], fill=255, width=1)
        x, y, ang = nx, ny, ang + rng.normal(0, 0.8)
c = np.asarray(cr.filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32)[..., None] / 255
a = a * (1 - 0.45 * c)
# mould / foxing blooms and darkened edges
for _ in range(40):
    cx, cy, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(5, 40)
    m = np.exp(-(((np.arange(W)[None] - cx) ** 2 + (np.arange(H)[:, None] - cy) ** 2) / r ** 2))[..., None]
    a = a * (1 - 0.35 * m) + 0.05 * m * np.array([0.55, 0.45, 0.25])
edge = np.clip(np.minimum.reduce([xx, 1 - xx, yy, 1 - yy]) / 0.12, 0, 1)[..., None]
a *= 0.55 + 0.45 * edge
os.makedirs(os.path.dirname(OUT), exist_ok=True)
Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).save(OUT)
print("wrote", OUT)
