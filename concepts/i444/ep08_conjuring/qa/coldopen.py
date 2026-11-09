# QA: the rendered cold open at FPS frames/s, each frame labelled with its time and the word being spoken (voice/words.json s00)
# usage: python qa/coldopen.py <render.mp4> <out_prefix> [fps=10] [t1=15.4]  -> <out_prefix>_<n>.jpg (40 frames per sheet)
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
src, out = sys.argv[1], sys.argv[2]; FPS = float(sys.argv[3]) if len(sys.argv) > 3 else 10; T1 = float(sys.argv[4]) if len(sys.argv) > 4 else 15.4
W = json.load(open(D + os.environ.get('VOICE', 'voice').strip('/\\') + '/words.json'))['s00']; TW, TH, C, P = 320, 180, 8, 40
raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', src, '-t', str(T1), '-vf', f'fps={FPS},scale={TW}:{TH}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
n = len(raw) // (TW * TH * 3); fnt = ImageFont.truetype('arial.ttf', 15)
def word(t): return next((w for a, b, w in reversed(W) if a <= t), '')
for p in range(0, n, P):
    m = min(P, n - p); im = Image.new('RGB', (C * TW, (m + C - 1) // C * TH)); d = ImageDraw.Draw(im)
    for j in range(m):
        i = p + j; t = i / FPS; x, y = j % C * TW, j // C * TH
        im.paste(Image.frombytes('RGB', (TW, TH), raw[i * TW * TH * 3:(i + 1) * TW * TH * 3]), (x, y))
        d.text((x + 3, y + 2), f'{t:.1f} {word(t)}', font=fnt, fill='yellow', stroke_width=2, stroke_fill='black')
    im.save(f'{out}_{p // P}.jpg', quality=80)
print(n, 'frames')
