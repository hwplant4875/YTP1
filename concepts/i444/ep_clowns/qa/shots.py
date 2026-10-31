# QA grid: one frame from the middle of every shot of the given sections (rendered sec files), labelled with the anchor word
import json, sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont
E = json.load(open('edl.json')); WK = 'E:/YTP2/Horror Ranked/EP06 Clowns/2_renders/work_ep06_clowns_v1/'; secs = sys.argv[2:]
cells = []
for si, S in enumerate(E['sections']):
    if S['voice'] not in secs: continue
    L = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', WK + f'sec{si:02d}.mp4']))
    sh = S['shots']
    for k, (t, n, tin, *_) in enumerate(sh):
        t1 = sh[k + 1][0] if k + 1 < len(sh) else L; m = (t + t1) / 2
        raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(m), '-i', WK + f'sec{si:02d}.mp4', '-frames:v', '1', '-vf', 'scale=384:216', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
        cells.append((f"{S['voice']} {k} {n}@{tin}", Image.frombytes('RGB', (384, 216), raw)))
C = 5; im = Image.new('RGB', (C * 384, (len(cells) + C - 1) // C * 216)); d = ImageDraw.Draw(im); fnt = ImageFont.truetype('arial.ttf', 16)
for i, (lab, c) in enumerate(cells):
    x, y = i % C * 384, i // C * 216; im.paste(c, (x, y)); d.text((x + 3, y + 2), lab, font=fnt, fill='yellow', stroke_width=2, stroke_fill='black')
im.save(sys.argv[1], quality=82)
