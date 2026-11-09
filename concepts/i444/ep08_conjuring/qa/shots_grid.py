# QA on the render: one frame from the middle of every shot (and film lines at 15% and 85%), labelled, in grids of 40 cells.
# usage: python qa/shots_grid.py <render.mp4> <out_prefix> [sections...]   (section starts = running sum of each section's len, as the renderer)
import json, sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
E = json.load(open(D + 'edl.json')); R, OUT = sys.argv[1], sys.argv[2]; secs = sys.argv[3:]
FPS = 30; t0 = 0.0; cells = []
for S in E['sections']:
    base = round(t0 * FPS) / FPS; sh = S['shots']
    if not secs or S['voice'] in secs:
        for k, s in enumerate(sh):
            t1 = sh[k + 1][0] if k + 1 < len(sh) else S['len']; ins = len(s) > 4 and isinstance(s[4], dict) and s[4].get('ins')
            pts = [s[0] + (t1 - s[0]) * f for f in ((0.15, 0.85) if ins else (0.5,))]
            for p in pts: cells.append((f"{S['voice']} {k} {s[1]}@{s[2]}{' INS' if ins else ''}", base + p))
    t0 += S['len']
TW, TH, C, P = 384, 216, 5, 40; fnt = ImageFont.truetype('arial.ttf', 16)
for p in range(0, len(cells), P):
    part = cells[p:p + P]; im = Image.new('RGB', (C * TW, (len(part) + C - 1) // C * TH)); d = ImageDraw.Draw(im)
    for i, (lab, t) in enumerate(part):
        raw = b''
        for tt in (t, t - 0.2, t - 0.5):
          if len(raw) < TW * TH * 3: raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f'{tt:.3f}', '-i', R, '-frames:v', '1', '-vf', f'scale={TW}:{TH}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
        x, y = i % C * TW, i // C * TH; im.paste(Image.frombytes('RGB', (TW, TH), raw), (x, y))
        d.text((x + 3, y + 2), f'{lab} {t:.1f}', font=fnt, fill='yellow', stroke_width=2, stroke_fill='black')
    im.save(f'{OUT}_{p // P}.jpg', quality=80)
print(len(cells), 'cells')
