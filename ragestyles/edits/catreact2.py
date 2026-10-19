"""Meme-reaction fail short v2: full 9:16 canvas. The footage window ratio is picked per clip (9:16, 3:4, 1:1);
anything not covered by the window is the same video stretched and blurred (FitFix style). Crop keyframes keep
the person in focus. Memes pop up semi-transparent with a Vine Boom for a moment and fade out. The only text is
the score during the slow-mo replay. The next clip pushes the last one out with a whoosh.

    python3 catreact2.py spec.json out.mp4

spec:
  "font", "boom", "pop", "whoosh": paths; "memeAlpha": 0.5; "memeW": 640
  "clips": [{"src", "in", "out", "ratio": "9:16"|"3:4"|"1:1",
             "track": [[t, x, y, zoom], ...]   source time, focus point (0..1 of the source), zoom (1 = widest)
             "memes": [{"at": t, "src", "dur": 1.0}],    at = source time in the live part
             "replay": {"in", "out", "speed"},
             "score": 9.5}]          one big number stamped mid-screen (old rows form [["IMPACT", 8], ...] still works)
"""
import json, subprocess, sys, tempfile
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
PUSH = 7
RATIOS = {"9:16": 16 / 9, "3:4": 4 / 3, "1:1": 1.0, "4:5": 5 / 4}


def probe(src):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=width,height',
                          '-of', 'csv=p=0', src], capture_output=True, text=True).stdout.split(',')
    return int(out[0]), int(out[1])


def stream(src, ss, dur, speed=1.0):
    w, h = probe(src)
    pts = f"setpts=PTS/{speed}," if speed != 1 else ''
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{ss:.3f}', '-t', f'{dur:.3f}', '-i', src, '-vf',
                          f'{pts}fps={FPS},format=rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
    n = w * h * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)
    p.wait()


def load_meme(src, width, ss=0.0):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{ss:.3f}', '-i', src, '-vf',
                          f'scale={width}:-2:flags=lanczos,fps={FPS},format=rgb24', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    w, h = probe(src)
    mh = int(round(h * width / w / 2)) * 2
    return np.frombuffer(raw, np.uint8).reshape(-1, mh, width, 3)


def interp(track, t):
    if t <= track[0][0]:
        return track[0][1:]
    for a, b in zip(track, track[1:]):
        if t <= b[0]:
            u = (t - a[0]) / (b[0] - a[0])
            u = u * u * (3 - 2 * u)                       # smoothstep between keyframes
            return [a[k] + (b[k] - a[k]) * u for k in (1, 2, 3)]
    return track[-1][1:]


def compose(fr, c, t):
    sh, sw = fr.shape[:2]
    wh = int(W * RATIOS[c.get('ratio', '9:16')] // 2 * 2)   # window height on the canvas
    x, y, z = interp(c.get('track', [[0, 0.5, 0.5, 1.0]]), t)
    ar = W / wh
    cw = min(sw, sh * ar) / z
    ch = cw / ar
    x0 = min(max(x * sw - cw / 2, 0), sw - cw)
    y0 = min(max(y * sh - ch / 2, 0), sh - ch)
    win = cv2.resize(fr[int(y0):int(y0 + ch), int(x0):int(x0 + cw)], (W, wh), interpolation=cv2.INTER_LANCZOS4)
    if wh >= H:
        return win[:H]
    # blurred stretched background from the same frame
    bg = cv2.resize(fr, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
    bg = cv2.GaussianBlur(bg, (0, 0), 6)
    bg = cv2.resize(bg, (W, H), interpolation=cv2.INTER_LINEAR)
    bg = (bg.astype(np.float32) * 0.6).astype(np.uint8)
    top = (H - wh) // 2 - c.get('lift', 60)
    bg[top:top + wh] = win
    return bg


def sharpen(img):
    blur = cv2.GaussianBlur(img, (0, 0), 1.2)
    return cv2.addWeighted(img, 1.5, blur, -0.5, 0)


def score_rgba(font, rows, shown, pop):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, (label, val) in enumerate(rows[:shown]):
        total = k == len(rows) - 1
        s = pop if k == shown - 1 else 1.0
        f = ImageFont.truetype(font, int((120 if total else 96) * s))
        y = 1180 + k * 118 + (14 if total else 0)
        d.text((70, y), label, font=f, fill='white', stroke_width=8, stroke_fill='black', anchor='ls')
        x = 70 + d.textlength(label + ' ', font=f)
        d.text((x, y), str(val), font=f, fill='#ffd400', stroke_width=8, stroke_fill='black', anchor='ls')
    return np.asarray(im)


def stamp_rgba(font, val):
    """one big score number, yellow (low) to red (high), thick black stroke; tight RGBA crop"""
    u = min(max((val - 5) / 5, 0), 1)
    col = (255, int(212 * (1 - u) + 40 * u), int(0 * (1 - u) + 40 * u))
    f = ImageFont.truetype(font, 330)
    txt = f'{val:g}'
    im = Image.new('RGBA', (W, 520), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((W / 2, 260), txt, font=f, fill=col, stroke_width=16, stroke_fill='black', anchor='mm')
    return np.asarray(im.crop(im.getbbox()))


def put_stamp(canvas, st, age):
    """slam in: scale 1.9 -> 1 over 5 frames with a small overshoot, then hold"""
    k = age * FPS
    s = 1.9 - 0.95 * min(k / 5, 1) + (0.05 * max(0, 1 - (k - 5) / 4) if k >= 5 else 0)
    h, w = st.shape[:2]
    img = cv2.resize(st, (max(2, int(w * s)), max(2, int(h * s))), interpolation=cv2.INTER_LINEAR)
    h, w = img.shape[:2]
    cx, cy = W // 2, 1250
    x0, y0 = cx - w // 2, cy - h // 2
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    sub = img[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32)
    a = sub[..., 3:4] / 255 * min(1.0, k / 2 + 0.3)
    roi = canvas[ya:yb, xa:xb].astype(np.float32)
    canvas[ya:yb, xa:xb] = (roi * (1 - a) + sub[..., :3] * a).astype(np.uint8)
    return canvas


def blend(canvas, rgba):
    a = rgba[..., 3:4].astype(np.float32) / 255
    if a.max() == 0:
        return canvas
    return (canvas * (1 - a) + rgba[..., :3] * a).astype(np.uint8)


def meme_on(canvas, m, age, dur, alpha):
    """pop in (scale 1.25 -> 1 over 0.12s), hold, fade out over the last 0.25s"""
    fr = m[int(age * FPS) % len(m)]
    s = 1 + 0.25 * max(0.0, 1 - age / 0.12)
    a = alpha * min(1.0, age / 0.06) * min(1.0, max(0.0, (dur - age) / 0.25))
    h, w = fr.shape[:2]
    fr = cv2.resize(fr, (int(w * s) // 2 * 2, int(h * s) // 2 * 2), interpolation=cv2.INTER_LINEAR)
    h, w = fr.shape[:2]
    x0, y0 = (W - w) // 2, 640 - h // 2
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    roi = canvas[ya:yb, xa:xb].astype(np.float32)
    src = fr[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32)
    canvas[ya:yb, xa:xb] = (roi * (1 - a) + src * a).astype(np.uint8)
    return canvas


def build(spec, out):
    tmp = tempfile.mkdtemp(prefix='cat2_')
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                            '-pix_fmt', 'yuv420p', f'{tmp}/v.mp4'], stdin=subprocess.PIPE)
    alpha, mw = spec.get('memeAlpha', 0.5), spec.get('memeW', 640)
    audio, sfx, t, prev = [], [], 0.0, None
    for ci, c in enumerate(spec['clips']):
        r = c['replay']
        memes = [(m, load_meme(m['src'], m.get('w', mw), m.get('ss', 0.0))) for m in c.get('memes', [])]
        for m, _ in memes:
            sfx.append((spec['boom'], t + (m['at'] - c['in']), 0.55))
        if ci:
            sfx.append((spec['whoosh'], t, 0.45))
        single = not isinstance(c['score'], list)
        if single:
            st = stamp_rgba(spec['font'], c['score'])
        else:
            rows = [list(x) for x in c['score']] + [['TOTAL', sum(v for _, v in c['score'])]]
        i, n_live = 0, 0
        parts = [('live', stream(c['src'], c['in'], c['out'] - c['in'])),
                 ('slow', stream(c['src'], r['in'], r['out'] - r['in'], r['speed']))]
        for kind, gen in parts:
            for j, fr in enumerate(gen):
                ts = c['in'] + j / FPS if kind == 'live' else r['in'] + j * r['speed'] / FPS
                canvas = sharpen(compose(fr, c, ts))
                if kind == 'live':
                    n_live += 1
                    for m, mf in memes:
                        age = ts - m['at']
                        if 0 <= age < m.get('dur', 1.0):
                            canvas = meme_on(canvas, mf, age, m.get('dur', 1.0), m.get('alpha', alpha))
                elif single:
                    at = 3
                    if j == at:
                        sfx.append((spec.get('stamp', spec['pop']), t + (n_live + at) / FPS, 0.6))
                    if j >= at:
                        canvas = put_stamp(canvas, st, (j - at) / FPS)
                else:
                    pops = [4 + k * 8 for k in range(len(rows))]
                    if j == 0:
                        for k in pops:
                            sfx.append((spec['pop'], t + (n_live + k) / FPS, 0.45))
                    shown = sum(1 for k in pops if j >= k)
                    if shown:
                        pop = 1 + 0.35 * max(0, 1 - (j - pops[shown - 1]) / 4)
                        canvas = blend(canvas, score_rgba(spec['font'], rows, shown, pop))
                if prev is not None and i < PUSH - 1:
                    off = int(W * (1 - (1 - (i + 1) / PUSH) ** 3))
                    canvas = np.concatenate([prev[:, off:], canvas[:, :off]], axis=1)
                enc.stdin.write(np.ascontiguousarray(canvas).tobytes())
                last, i = canvas, i + 1
        prev = last
        n_slow = i - n_live
        has_a = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index',
                                '-of', 'csv=p=0', c['src']], capture_output=True, text=True).stdout.strip()
        for k, (ss, dur, sp, n) in enumerate([(c['in'], c['out'] - c['in'], 1.0, n_live),
                                              (r['in'], r['out'] - r['in'], r['speed'], n_slow)]):
            a = f'{tmp}/a{ci}_{k}.wav'
            if has_a:
                tempo = 'anull' if sp == 1 else ','.join(['atempo=0.5'] * (sp < 0.5) + [f'atempo={sp / (0.5 if sp < 0.5 else 1):.4f}'])
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{ss:.3f}', '-t', f'{dur:.3f}', '-i', c['src'], '-af',
                                f'{tempo},volume={0.5 if k else 1.0},aresample=48000,apad', '-t', f'{n / FPS:.3f}', '-ac', '2', a], check=True)
            else:
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
                                '-t', f'{n / FPS:.3f}', a], check=True)
            audio.append(a)
        t += i / FPS
    enc.stdin.close(); enc.wait()
    total = t
    open(f'{tmp}/a.txt', 'w').write(''.join(f"file '{a}'\n" for a in audio))
    ins, chain, mix = ['-f', 'concat', '-safe', '0', '-i', f'{tmp}/a.txt'], '', ['[0:a]']
    for k, (f, at, vol) in enumerate(sfx):
        ins += ['-i', f]
        chain += f"[{k + 1}:a]volume={vol},adelay={int(at * 1000)}:all=1,aresample=48000[s{k}];"
        mix.append(f'[s{k}]')
    chain += f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0,afade=t=out:st={total - 0.4:.3f}:d=0.4[a]"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', chain, '-map', '[a]', '-t', f'{total:.3f}',
                    f'{tmp}/a.wav'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{tmp}/v.mp4', '-i', f'{tmp}/a.wav', '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out], check=True)
    print(out, round(total, 1))


if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2])
