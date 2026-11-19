# EP08 shot-audit contact sheets (v6, same layout as audit_v5): one sheet per section, 4 tiles of 480 px per row, each tile = the
# middle frame of one shot from the final render, labelled with the shot id, its time in the video, clip@in-point and the words spoken
# over it (film-line inserts show their subtitle). Frames darker than luma 45 also go through a brightened copy (marked).
# usage: python qa/audit_sheets.py <render.mp4> <out_dir> [sections...]   (needs edl.json and voice/words.json)
import json, sys, os, subprocess, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageStat, ImageEnhance
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
E = json.load(open(D + 'edl.json')); W = json.load(open(D + 'voice/words.json'))
R, OUT = sys.argv[1], sys.argv[2]; secs = sys.argv[3:]; os.makedirs(OUT, exist_ok=True)
FPS, TW, TH, CAP, C = 30, 480, 270, 62, 4
fb = ImageFont.truetype('arialbd.ttf', 15); fn = ImageFont.truetype('arial.ttf', 15)
def mmss(t): return f'{int(t // 60)}:{t % 60:05.2f}'
def words(S, a, b):   # section time a..b -> the take words that start inside it
    out = []
    for ta, tb, s0 in S['pieces']:
        lo, hi = max(a, s0), min(b, s0 + tb - ta)
        if hi > lo: out += [w[2] for w in W[S['voice']] if ta + (lo - s0) - 0.1 <= w[0] < ta + (hi - s0) - 0.1]
    return ' '.join(out)
tg = 0.0
for S in E['sections']:
    base = round(tg * FPS) / FPS; tg += S['len']
    if secs and S['voice'] not in secs: continue
    sh = S['shots']; tiles = []
    for k, s in enumerate(sh):
        t1 = sh[k + 1][0] if k + 1 < len(sh) else S['len']; op = s[4] if len(s) > 4 and isinstance(s[4], dict) else {}
        mid = base + (s[0] + t1) / 2
        raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f'{mid:.3f}', '-i', R, '-frames:v', '1', '-vf', f'scale={TW}:{TH}',
                                       '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
        f = Image.frombytes('RGB', (TW, TH), raw); br = ImageStat.Stat(f.convert('L')).mean[0] < 45
        if br: f = ImageEnhance.Brightness(f).enhance(2.3)
        if op.get('ins'): said = next((f'[film line] {x["sub"]}' if x['sub'] else f'[film sound: {x["kind"]}]' for x in S['inserts'] if x['s0'] - 0.05 <= s[0] < x['s1']), '[film sound]')
        else: said = words(S, s[0], t1)
        tiles.append((f, f"{S['voice']}#{k:02d}  {mmss(base + s[0])}  {s[1]}@{s[2]}" + ('  (brightened copy)' if br else ''), said))
    rows = (len(tiles) + C - 1) // C; im = Image.new('RGB', (C * TW, rows * (TH + CAP)), (24, 24, 24)); d = ImageDraw.Draw(im)
    for i, (f, lab, said) in enumerate(tiles):
        x, y = i % C * TW, i // C * (TH + CAP); im.paste(f, (x, y))
        d.text((x + 4, y + TH + 4), lab, font=fb, fill=(255, 214, 10))
        for j, line in enumerate(textwrap.wrap(said, 58)[:2]): d.text((x + 4, y + TH + 23 + j * 17), line, font=fn, fill='white')
    im.save(os.path.join(OUT, S['voice'] + '.jpg'), quality=85); print(S['voice'], len(tiles), 'shots')
