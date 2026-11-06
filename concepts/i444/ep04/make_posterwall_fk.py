# EP04 Freddy v3 copy of ../ep07_pinhead/make_posterwall.py: the 9 films (official TMDB theatrical posters, downloaded on the laptop,
# never committed), rows of 5 and 4 around the centre caption band. usage: python make_posterwall_fk.py <poster_dir> <out.mp4>
# EP07 v2 (owner 11/04): all 11 films on one screen before the rules, official TMDB theatrical posters (scratchpad, never committed),
# in release order, popping in one after another, under "We're ranking every Pinhead". -> clips/still_posterwall.mp4 (5 s, 30 fps)
import os, sys, subprocess
from PIL import Image, ImageEnhance, ImageFilter
P = sys.argv[1]; OUT = sys.argv[2]
ORDER = ['n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7', 'fj', 'r10']   # release order 1984 .. 2010; files <key>_*.jpg in the poster folder
files = {f.split('_')[0]: os.path.join(P, f) for f in os.listdir(P) if f.endswith('.jpg')}
# v5 (owner 11/04): the cold-open captions now run over the wall too ("We're ranking / Every Pinhead / By your chance / Of surviving him"),
# so the two rows leave a clear centre band (BAND px) for the caption at y 540 and no poster is ever covered.
PW, PH, G, BAND = 232, 348, 18, 250; W, H, FPS, DUR = 1920, 1080, 30, 5.0
rows = [ORDER[:5], ORDER[5:]]; Y0 = (H - 2 * PH - BAND) // 2
slots = []
for r, row in enumerate(rows):
    x0 = (W - len(row) * PW - (len(row) - 1) * G) // 2
    for i, k in enumerate(row): slots.append((k, x0 + i * (PW + G), Y0 + r * (PH + BAND)))
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
