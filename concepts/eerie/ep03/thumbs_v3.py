# EP03 thumbnails v3 (user 2026-10-21: black background, figures pure flat white, simple).
# Each figure is rendered alone (TH=drawT2g_thing|refl|fingers|me node thumbstill.mjs L/<name>.png), then stacked back to front:
# every figure is flat white with a black outline where it overlaps the one behind it; eyes stay (the thing's red, the reflection's black).
# python3 thumbs_v3.py layerdir out.png [room.png]   (room.png: the full still; its room shows faintly behind the figures)
import sys, numpy as np
from PIL import Image, ImageFilter
d, out = sys.argv[1], sys.argv[2]
def load(n): return np.asarray(Image.open(f'{d}/{n}.png').convert('RGB')).astype(np.float32) / 255
def img(m): return Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8))
def arr(i): return np.asarray(i).astype(np.float32) / 255
def blur(m, r): return arr(img(m).filter(ImageFilter.GaussianBlur(r)))
def grow(m, n): return arr(img(m).filter(ImageFilter.MaxFilter(n)))
def shrink(m, n): return arr(img(m).filter(ImageFilter.MinFilter(n)))
o = np.zeros((1080, 1920)); union = np.zeros((1080, 1920)); redE = np.zeros((1080, 1920)); eyes = np.zeros((1080, 1920))
for n in ['thing', 'refl', 'fingers', 'me']:
    a = load(n); L = a.max(axis=2); m = np.clip((L - 0.04) * 6, 0, 1)
    red = np.clip((a[..., 0] - np.maximum(a[..., 1], a[..., 2]) - 0.15) * 3, 0, 1)
    solid = shrink(grow(m, 41), 41) if n == "refl" else m        # the reflection's eyes filled in, then drawn back black
    edge = blur(grow(solid, 13 if n != 'fingers' else 9), 1.2)  # the black outline ring around this figure
    o = o * (1 - edge); eyes *= (1 - edge); redE *= (1 - edge)
    o = np.maximum(o, blur(solid, 0.8))
    union = np.maximum(union, solid)
    if n == 'refl': eyes = np.maximum(eyes, solid * np.clip((0.3 - L) * 6, 0, 1) * (np.arange(1080)[:, None] < 700))
    if n == 'thing': redE = np.maximum(redE, red)
eyes = shrink(grow(eyes, 9), 9)                                  # solid round eyes
o *= (1 - np.clip(eyes * 1.4, 0, 1))
glow = blur(union, 26) * 0.45 * (1 - union)
rgb = np.stack([o + glow] * 3, -1)
if len(sys.argv) > 3:                                            # the room, dim, for depth (POV)
    R = np.asarray(Image.open(sys.argv[3]).convert('L')).astype(np.float32) / 255
    rgb += (np.clip(R - 0.05, 0, 1) * 1.1 * (1 - grow(union, 15)))[..., None]
rg = blur(redE, 14) * 1.3 + blur(redE, 40) * 0.9
rgb += rg[..., None] * np.array([1, 0, 0.05]) * (1 - redE[..., None])
rgb = rgb * (1 - redE[..., None]) + redE[..., None] * np.array([1, 0.1, 0.16])
Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).resize((1280, 720), Image.LANCZOS).save(out)
