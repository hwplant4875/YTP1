# QA grid from the sources (no render): frames at 15% / 85% of every shot of the given sections, labelled with the anchor word
import json, sys, subprocess
from PIL import Image, ImageDraw, ImageFont
E = json.load(open('edl.json')); C0 = 'E:/YTP2/Horror Ranked/EP05 Halloween Night/1_work/clips/'; W = json.load(open('voice/words.json'))
cells = []
for S in E['sections']:
    if S['voice'] not in sys.argv[2:]: continue
    sh = S['shots']; L = W[S['voice']][-1][1] + S['pad']
    for k, (t, n, tin, *sp) in enumerate(sh):
        sp = sp[0] if sp else 1.0; t1 = sh[k + 1][0] if k + 1 < len(sh) else L
        for q in (0.15, 0.85):
            m = tin + (t1 - t) * q * sp
            raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(m), '-i', (C0 + n + '_hd.mp4' if __import__('os').path.exists(C0 + n + '_hd.mp4') else C0 + n + '.mp4'), '-frames:v', '1', '-vf', 'scale=320:180', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
            cells.append((f"{S['voice']}.{k} {n}@{m:.1f}", Image.frombytes('RGB', (320, 180), raw)))
C = 6; im = Image.new('RGB', (C * 320, (len(cells) + C - 1) // C * 180)); d = ImageDraw.Draw(im); fnt = ImageFont.truetype('arial.ttf', 15)
for i, (lab, c) in enumerate(cells):
    x, y = i % C * 320, i // C * 180; im.paste(c, (x, y)); d.text((x + 3, y + 2), lab, font=fnt, fill='yellow', stroke_width=2, stroke_fill='black')
im.save(sys.argv[1], quality=80)
