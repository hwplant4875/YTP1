# EP07 v2 (owner 11/04): all 11 films on one screen before the rules, official TMDB theatrical posters (scratchpad, never committed),
# in release order, popping in one after another, under "We're ranking every Pinhead". -> clips/still_posterwall.mp4 (5 s, 30 fps)
import os, sys, subprocess
from PIL import Image, ImageEnhance, ImageFilter
P = sys.argv[1]; OUT = sys.argv[2]
ORDER = ['hr1', 'hr2', 'hr3', 'hr4', 'hr5', 'hr6', 'hr7', 'hr8', 'hr9', 'hr10', 'hr22']
files = {f.split('_')[0]: os.path.join(P, f) for f in os.listdir(P) if f.endswith('.jpg')}
PW, PH, G = 286, 429, 22; W, H, FPS, DUR = 1920, 1080, 30, 5.0
rows = [ORDER[:6], ORDER[6:]]; Y0 = (H - 2 * PH - G) // 2
slots = []
for r, row in enumerate(rows):
    x0 = (W - len(row) * PW - (len(row) - 1) * G) // 2
    for i, k in enumerate(row): slots.append((k, x0 + i * (PW + G), Y0 + r * (PH + G)))
img = {k: Image.open(files[k]).convert('RGB').resize((PW, PH), Image.LANCZOS) for k in ORDER}
bg = Image.new('RGB', (W, H), (8, 4, 6))
mosaic = bg.copy()
for k, x, y in slots: mosaic.paste(img[k], (x, y))
bgblur = ImageEnhance.Brightness(mosaic.resize((W // 8, H // 8)).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(30))).enhance(0.35)
ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)
STEP, POP = 0.09, 0.22
for n in range(int(DUR * FPS)):
    t = n / FPS; fr = bgblur.copy()
    for i, (k, x, y) in enumerate(slots):
        a = (t - i * STEP) / POP
        if a <= 0: continue
        a = min(a, 1.0); s = 1.18 - 0.18 * (1 - (1 - a) ** 3)
        w, h = int(PW * s), int(PH * s); im = img[k].resize((w, h), Image.BILINEAR)
        if a < 1: im = ImageEnhance.Brightness(im).enhance(0.4 + 0.6 * a)
        fr.paste(im, (x + PW // 2 - w // 2, y + PH // 2 - h // 2))
    ff.stdin.write(fr.tobytes())
ff.stdin.close(); ff.wait(); print(OUT)
