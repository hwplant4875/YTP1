# QA: for every shot of the given sections, 8 frames spread over the exact source span it will use (in -> in + dur*speed)
import json, sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont
E = json.load(open('edl.json')); C0 = 'E:/YTP2/Instruction444/clips/halloween/'; W = json.load(open('voice/words.json'))
TW, TH, N = 240, 135, 8; rows = []
for S in E['sections']:
    if S['voice'] not in sys.argv[2:]: continue
    sh = S['shots']; L = W[S['voice']][-1][1] + S['pad']
    for k, (t, n, tin, *sp) in enumerate(sh):
        sp = sp[0] if sp else 1.0; t1 = sh[k + 1][0] if k + 1 < len(sh) else L; span = (t1 - t) * sp
        src = C0 + n + '_hd.mp4' if os.path.exists(C0 + n + '_hd.mp4') else C0 + n + '.mp4'
        fr = []
        for i in range(N):
            m = tin + span * i / (N - 1) * 0.98
            raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f'{m:.2f}', '-i', src, '-frames:v', '1', '-vf', f'scale={TW}:{TH}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
            fr.append(Image.frombytes('RGB', (TW, TH), raw))
        rows.append((f"{S['voice']}.{k} {n}@{tin} x{sp} {span:.2f}s", fr))
im = Image.new('RGB', (N * TW, len(rows) * TH)); d = ImageDraw.Draw(im); fnt = ImageFont.truetype('arial.ttf', 16)
for r, (lab, fr) in enumerate(rows):
    for i, f in enumerate(fr): im.paste(f, (i * TW, r * TH))
    d.text((4, r * TH + 2), lab, font=fnt, fill='yellow', stroke_width=2, stroke_fill='black')
im.save(sys.argv[1], quality=78)
