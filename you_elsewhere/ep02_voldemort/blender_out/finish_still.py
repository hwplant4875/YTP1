"""Add slight film grain to a raw render and write the final PNG + a 960px JPG preview.

  python finish_still.py voldemort_room_look_v1_raw.png voldemort_room_look_v1
"""
import sys
import numpy as np
from PIL import Image

src, name = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src).convert("RGB")).astype(np.float32) / 255.0
rng = np.random.default_rng(31)
g = rng.normal(0.0, 1.0, im.shape[:2]).astype(np.float32)
# grain a bit stronger in the mid/shadow tones, monochrome
lum = im.mean(axis=2, keepdims=True)
amp = 0.018 * (1.0 - 0.6 * lum)
out = np.clip(im + g[..., None] * amp, 0, 1)
img = Image.fromarray((out * 255 + 0.5).astype(np.uint8))
img.save(name + ".png")
img.resize((960, 540), Image.LANCZOS).save(name + "_960.jpg", quality=90)
print("wrote", name + ".png", name + "_960.jpg")
