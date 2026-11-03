# QA: for every shot of the given sections, 8 frames spread over the exact source span it will use (in -> in + dur*speed)
import json, sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont
E = json.load(open('edl.json')); C0 = 'E:/YTP2/Horror Ranked/EP07 Pinhead/1_work/clips/'; W = json.load(open('voice/words.json'))
TW, TH, N = (240, 135, 8) if not os.environ.get('N4') else (300, 169, 4); rows = []
for S in E['sections']:
    if S['voice'] not in sys.argv[2:]: continue
    sh = S['shots']; L = W[S['voice']][-1][1] + S['pad']
    for k, (t, n, tin, *sp) in enumerate(sh):
        op = sp[1] if len(sp) > 1 else {}; sp = sp[0] if sp else 1.0; t1 = sh[k + 1][0] if k + 1 < len(sh) else L; span = (t1 - t) * sp
        src = C0 + n + '_hd.mp4' if os.path.exists(C0 + n + '_hd.mp4') else C0 + n + '.mp4'
        if n == 'hr9_rev': src = C0 + 'Hellraiser Revelations 2011 1080p BluRay x264-OFT.mkv'
        card = next((o[2] for o in S['overlays'] if o[0] == 'stats'), 999); vf = ('hflip,' if op.get('flip') else '') + f'scale={TW}:{TH}'
        fr = []
        for i in range(N):
            m = tin + span * i / (N - 1) * 0.98
            raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f'{m:.2f}', '-i', src, '-frames:v', '1', '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
            f = Image.frombytes('RGB', (TW, TH), raw)
            if t >= card - 0.01: ImageDraw.Draw(f).line([(TW * 840 // 1920, 0), (TW * 840 // 1920, TH)], fill=(255, 0, 0), width=2)   # stat card covers x > 840
            fr.append(f)
        rows.append((f"{S['voice']}.{k} {n}@{tin} x{sp} {span:.2f}s", fr))
im = Image.new('RGB', (N * TW, len(rows) * TH)); d = ImageDraw.Draw(im); fnt = ImageFont.truetype('arial.ttf', 16)
for r, (lab, fr) in enumerate(rows):
    for i, f in enumerate(fr): im.paste(f, (i * TW, r * TH))
    d.text((4, r * TH + 2), lab, font=fnt, fill='yellow', stroke_width=2, stroke_fill='black')
im.save(sys.argv[1], quality=78)
