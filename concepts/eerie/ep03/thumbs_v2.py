# EP03 thumbnails v2: map the clean engine still (thumbstill TH=drawT2g) to the channel's three looks.
# python3 thumbs_v2.py in.png outdir  -> outdir/b_bw.png, b_green.png, b_red.png (1280x720)
import sys, numpy as np
from PIL import Image, ImageFilter
im = Image.open(sys.argv[1]).convert('RGB').resize((1280, 720), Image.LANCZOS); out = sys.argv[2]
a = np.asarray(im).astype(np.float32) / 255
r, g, b = a[..., 0], a[..., 1], a[..., 2]
red = np.clip((r - np.maximum(g, b) - 0.15) * 3, 0, 1)
L = 0.3 * r + 0.59 * g + 0.11 * b
fig = np.clip((L - 0.22) / 0.62, 0, 1) ** 0.9 * (1 - red)       # walls and glass go black, figures white, your head (darker grey) stays mid-grey
fig *= np.where(np.mgrid[0:720, 0:1280][0] < 90, 0.4, 1.0)      # the ceiling light stays dim so the faces lead
def blur(m, rad): return np.asarray(Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(rad))).astype(np.float32) / 255
gF = blur(np.clip((fig - 0.6) * 2.5, 0, 1), 16); gR = blur(red, 14); gR2 = blur(red, 40)
yy = np.mgrid[0:720, 0:1280][0]
def save(bg, figc, glowc, redc, redglow, name, scan=False):
    o = np.ones((720, 1280, 3)) * np.array(bg)
    o = o + gF[..., None] * np.array(glowc) * 0.5
    o = o * (1 - fig[..., None]) + fig[..., None] * np.array(figc)
    o = o + (gR * 1.2 + gR2 * 0.9)[..., None] * np.array(redglow)
    o = o * (1 - red[..., None]) + red[..., None] * np.array(redc)
    if scan: o *= (1 - 0.07 * ((yy % 4) < 2))[..., None]
    Image.fromarray((np.clip(o, 0, 1) * 255).astype(np.uint8)).save(f'{out}/{name}.png')
save([0, 0, 0], [1, 1, 1], [1, 1, 1], [1, 0.12, 0.18], [1, 0, 0.05], 'b_bw')
save([0, 0.03, 0.01], [0.45, 1, 0.55], [0.2, 1, 0.35], [1, 0.12, 0.18], [1, 0, 0.05], 'b_green', True)
save([0.9, 0.08, 0.13], [1, 1, 1], [1, 0.6, 0.6], [0.05, 0, 0], [0, 0, 0], 'b_red')
