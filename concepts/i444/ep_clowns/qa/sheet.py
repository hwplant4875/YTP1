# contact sheet of a clip: one frame every STEP s, labelled with its time -> <out>.jpg (for picking in-points)
import sys, subprocess, os, io
from PIL import Image, ImageDraw, ImageFont
src, out = sys.argv[1], sys.argv[2]; STEP = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
t0 = float(sys.argv[4]) if len(sys.argv) > 4 else 0; t1 = float(sys.argv[5]) if len(sys.argv) > 5 else 1e9
TW, TH, C = 256, 144, 8
raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(t0), '-i', src, '-t', str(t1 - t0), '-vf', f'fps=1/{STEP},scale={TW}:{TH}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
n = len(raw) // (TW * TH * 3); P = 48; fnt = ImageFont.truetype('arial.ttf', 20)
for p in range(0, n, P):  # one sheet per 48 frames: <out>_<part>.jpg
    m = min(P, n - p); R = (m + C - 1) // C
    im = Image.new('RGB', (C * TW, R * TH), 'black'); d = ImageDraw.Draw(im)
    for j in range(m):
        i = p + j; fr = Image.frombytes('RGB', (TW, TH), raw[i * TW * TH * 3:(i + 1) * TW * TH * 3]); x, y = j % C * TW, j // C * TH
        im.paste(fr, (x, y)); d.text((x + 4, y + 2), f'{t0 + i * STEP:.0f}', font=fnt, fill='yellow', stroke_width=2, stroke_fill='black')
    im.save(f'{out}_{p // P}.jpg', quality=80)
print(out, n)
