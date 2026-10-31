# QA: 8 frames over clip@start:dur for each arg (uses <clip>_hd.mp4 when present)
import sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont
C0 = 'E:/YTP2/Instruction444/clips/halloween/'; TW, TH, N = 240, 135, 8; rows = []
for a in sys.argv[2:]:
    n, rest = a.split('@'); t0, d = map(float, rest.split(':'))
    src = C0 + n + '_hd.mp4' if os.path.exists(C0 + n + '_hd.mp4') else C0 + n + '.mp4'; fr = []
    for i in range(N):
        raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f'{t0 + d * i / (N - 1):.2f}', '-i', src, '-frames:v', '1', '-vf', f'scale={TW}:{TH}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
        fr.append(Image.frombytes('RGB', (TW, TH), raw))
    rows.append((a, fr))
im = Image.new('RGB', (N * TW, len(rows) * TH)); d = ImageDraw.Draw(im); fnt = ImageFont.truetype('arial.ttf', 16)
for r, (lab, fr) in enumerate(rows):
    for i, f in enumerate(fr): im.paste(f, (i * TW, r * TH))
    d.text((4, r * TH + 2), lab, font=fnt, fill='yellow', stroke_width=2, stroke_fill='black')
im.save(sys.argv[1], quality=78)
