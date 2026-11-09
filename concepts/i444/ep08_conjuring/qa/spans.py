# QA before rendering: for every shot of the given sections, 8 frames spread over the exact source span it will use
# (in -> in + slot * speed), labelled with the section, phrase time, clip, in-point, speed and span.  Film-line inserts are marked.
# usage: python qa/spans.py <clips_dir> <out.jpg> s05 s06 ...
import json, sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
E = json.load(open(D + 'edl.json')); C0 = sys.argv[1]; TW, TH, N = 240, 135, 8; rows = []
def src(n):
    for ext in ('_hd.mp4', '.mp4', '.webm', '.mkv'):
        if os.path.exists(os.path.join(C0, n + ext)): return os.path.join(C0, n + ext)
    raise FileNotFoundError(n)
for S in E['sections']:
    if S['voice'] not in sys.argv[3:]: continue
    sh = S['shots']
    for k, (t, n, tin, sp, *rest) in enumerate(sh):
        op = rest[0] if rest else {}; t1 = sh[k + 1][0] if k + 1 < len(sh) else S['len']; span = (t1 - t) * (1.0 if op.get('ins') else sp)
        vf = ('hflip,' if op.get('flip') else '') + f'scale={TW}:{TH}'; fr = []
        for i in range(N):
            m = tin + span * i / (N - 1) * 0.98
            raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f'{m:.2f}', '-i', src(n), '-frames:v', '1', '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
            fr.append(Image.frombytes('RGB', (TW, TH), raw))
        rows.append((f"{S['voice']} {t:6.2f} {n}@{tin} x{sp} {span:.2f}s" + ('  INSERT' if op.get('ins') else ''), fr))
im = Image.new('RGB', (N * TW, max(1, len(rows)) * TH)); d = ImageDraw.Draw(im)
try: fnt = ImageFont.truetype('arial.ttf', 16)
except OSError: fnt = ImageFont.load_default()
for r, (lab, fr) in enumerate(rows):
    for i, f in enumerate(fr): im.paste(f, (i * TW, r * TH))
    d.text((4, r * TH + 2), lab, font=fnt, fill='yellow', stroke_width=2, stroke_fill='black')
im.save(sys.argv[2], quality=78); print(sys.argv[2], len(rows), 'shots')
