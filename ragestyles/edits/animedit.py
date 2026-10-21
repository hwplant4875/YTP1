"""Anime / movie motivation edit (CapCut / After Effects look) from ONE source: hard cuts on a beat grid, speed
ramps, zoom punches, camera shake, flash and impact frames, RGB split, glow, grade, sharpen, grain and quote
subtitles. No music: the owner lays phonk under it later; only chosen voice lines keep their original audio.

    python3 animedit.py spec.json out.mp4

spec:
  "font": TTF/OTF for subtitles, "grade": {"contrast", "sat", "black", "glow", "sharpen", "grain", "warm"}
  "shots": [{"src", "in", "out",                      source seconds
             "speed": 1.0 | [[t, factor], ...]          constant, or a ramp keyed on source time
             "x", "y": 0.5                               crop centre (fractions of the source)
             "zoom": 1.0 | [z_start, z_end]              eased over the shot (1 = full 9:16 crop of the source)
             "ratio": "9:16" | "16:9"                    16:9 = letterboxed full frame on black
             "punch": 0.0                                zoom kick at the cut that settles (0.15 = +15 %)
             "shake": 0.0                                px of camera shake, decaying over 0.4 s
             "flash": "white" | "black" | "invert" | None   2-4 frames at the cut
             "impact": [t, ...]                          source times of 2-frame invert/high-contrast impact frames
             "rgb": 0                                    px of chromatic split at the cut, decaying
             "bw": false, "freeze": 0.0                  black and white; hold the last frame this long
             "vol": 0.0                                  keep the source audio (voice lines) at this volume
             "text": [{"t", "at", "dur"}]                subtitle lines, at = seconds into the shot}]
"""
import json, os, subprocess, sys, tempfile
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30


def probe(src):
    o = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=width,height',
                        '-of', 'csv=p=0', src], capture_output=True, text=True).stdout.split(',')
    return int(o[0]), int(o[1])


def decode(src, t0, dur):
    w, h = probe(src)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t0:.3f}', '-t', f'{dur:.3f}', '-i', src,
                          '-vf', f'fps={FPS},format=rgb24', '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def source_times(s):
    """source time of every output frame"""
    sp = s.get('speed', 1.0)
    if not isinstance(sp, list):
        sp = [[s['in'], sp]]
    out, t = [], s['in']
    while t < s['out'] - 1e-6:
        out.append(t)
        f = sp[0][1]
        for k, v in sp:
            if t >= k:
                f = v
        t += f / FPS
    return out


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** 3


def crop(fr, s, z, dx, dy):
    sh, sw = fr.shape[:2]
    if s.get('ratio') == '16:9':
        ch, cw = sh / z, sw / z
    else:
        ch = sh / z
        cw = ch * W / H
    x0 = min(max(s.get('x', 0.5) * sw - cw / 2 + dx, 0), sw - cw)
    y0 = min(max(s.get('y', 0.5) * sh - ch / 2 + dy, 0), sh - ch)
    win = fr[int(y0):int(y0 + ch), int(x0):int(x0 + cw)]
    if s.get('ratio') == '16:9':
        wh = int(W * win.shape[0] / win.shape[1]) // 2 * 2
        img = np.zeros((H, W, 3), np.uint8)
        img[(H - wh) // 2:(H - wh) // 2 + wh] = cv2.resize(win, (W, wh), interpolation=cv2.INTER_CUBIC)
        return img
    return cv2.resize(win, (W, H), interpolation=cv2.INTER_CUBIC)


def look(img, g, rng):
    f = img.astype(np.float32)
    if g.get('warm'):
        f[..., 0] *= 1 + g['warm']; f[..., 2] *= 1 - g['warm']
    f = (f - 128) * g.get('contrast', 1.15) + 128
    grey = f.mean(axis=2, keepdims=True)
    f = grey + (f - grey) * g.get('sat', 1.15)
    b = g.get('black', 10)
    f = (f - b) * 255 / (255 - b)
    f = np.clip(f, 0, 255)
    if g.get('glow'):
        hi = np.clip(f - 170, 0, 255)
        small = cv2.resize(hi, (W // 6, H // 6), interpolation=cv2.INTER_AREA)
        f += cv2.resize(cv2.GaussianBlur(small, (0, 0), 6), (W, H)) * g['glow'] * 2.2
    if g.get('sharpen'):
        f += (f - cv2.GaussianBlur(f, (0, 0), 1.6)) * g['sharpen']
    if g.get('grain'):
        f += rng.normal(0, 255 * g['grain'], (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
    return np.clip(f, 0, 255).astype(np.uint8)


def rgb_split(img, px):
    if px < 1:
        return img
    o = img.copy()
    o[..., 0] = np.roll(img[..., 0], int(px), axis=1)
    o[..., 2] = np.roll(img[..., 2], -int(px), axis=1)
    return o


def text_rgba(font, txt, size):
    f = ImageFont.truetype(font, size)
    lines, cur = [], ''
    for wd in txt.split():
        t = (cur + ' ' + wd).strip()
        if f.getlength(t) > W - 160 and cur:
            lines.append(cur); cur = wd
        else:
            cur = t
    lines.append(cur)
    im = Image.new('RGBA', (W, int(size * 1.25 * len(lines)) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        d.text((W // 2, 20 + i * size * 1.25), ln, font=f, fill='white', anchor='ma',
               stroke_width=max(4, size // 12), stroke_fill='black')
    return np.asarray(im)


def put(img, rgba, y, a=1.0, scale=1.0):
    if scale != 1.0:
        rgba = cv2.resize(rgba, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    h, w = rgba.shape[:2]
    x0, y0 = (W - w) // 2, int(y - h / 2)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    src = rgba[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32)
    k = src[..., 3:4] / 255 * a
    img[ya:yb, xa:xb] = (img[ya:yb, xa:xb] * (1 - k) + src[..., :3] * k).astype(np.uint8)


def shot_frames(s, spec, rng):
    ts = source_times(s)
    frames = decode(s['src'], s['in'], s['out'] - s['in'] + 0.1)
    z = s.get('zoom', 1.0)
    z0, z1 = (z, z) if not isinstance(z, list) else z
    n = len(ts)
    texts = [(dict(l), text_rgba(spec['font'], l['t'], l.get('size', 92))) for l in s.get('text', [])]
    for j, t in enumerate(ts):
        fr = frames[min(int(round((t - s['in']) * FPS)), len(frames) - 1)]
        age = j / FPS
        zz = z0 + (z1 - z0) * ease(j / max(n - 1, 1)) + s.get('punch', 0) * (1 - ease(age / 0.35))
        amp = s.get('shake', 0) * max(0.0, 1 - age / 0.4)
        dx, dy = (rng.uniform(-amp, amp), rng.uniform(-amp, amp)) if amp > 0 else (0, 0)
        img = crop(fr, s, max(zz, 1.0), dx, dy)
        img = look(img, spec.get('grade', {}), rng)
        if s.get('bw'):
            img = np.repeat(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)[..., None], 3, axis=2)
        img = rgb_split(img, s.get('rgb', 0) * max(0.0, 1 - age / 0.3))
        for it in s.get('impact', []):
            if 0 <= t - it < 0.07:
                g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                g = np.where(g > 110, 0, 255).astype(np.uint8)        # inverted high-contrast impact frame
                img = np.repeat(g[..., None], 3, axis=2)
        fl = s.get('flash')
        if fl and j < 4:
            k = [1.0, 0.75, 0.45, 0.2][j]
            if fl == 'white':
                img = (img * (1 - k) + 255 * k).astype(np.uint8)
            elif fl == 'black':
                img = (img * (1 - k)).astype(np.uint8)
            elif fl == 'invert' and j < 2:
                img = 255 - img
        for l, rgba in texts:
            a0 = l.get('at', 0)
            if a0 <= age < a0 + l.get('dur', 1.5):
                u = (age - a0) / 0.12
                put(img, rgba, l.get('y', 1260), min(u, 1.0), 1.0 + 0.25 * max(0.0, 1 - u))
        yield img
    for _ in range(int(s.get('freeze', 0) * FPS)):
        yield img


def build(spec, out):
    rng = np.random.default_rng(7)
    tmp = tempfile.mkdtemp()
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                            '-pix_fmt', 'yuv420p', f'{tmp}/v.mp4'], stdin=subprocess.PIPE)
    audio = []
    for i, s in enumerate(spec['shots']):
        n = 0
        for img in shot_frames(s, spec, rng):
            enc.stdin.write(np.ascontiguousarray(img).tobytes()); n += 1
        dur = n / FPS
        a = f'{tmp}/a{i}.wav'
        sp = s.get('speed', 1.0)
        if s.get('vol') and not isinstance(sp, list):
            tempo = []
            f = sp
            while f < 0.5:
                tempo.append('atempo=0.5'); f /= 0.5
            tempo.append(f'atempo={f:.4f}')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{s['in']:.3f}", '-t', f"{s['out'] - s['in']:.3f}",
                            '-i', s['src'], '-af', ','.join(tempo) + f",volume={s['vol']},aresample=48000,"
                            f"afade=t=in:d=0.02,apad,afade=t=out:st={max(dur - 0.06, 0):.3f}:d=0.06",
                            '-t', f'{dur:.3f}', '-ac', '2', a], check=True)
        else:
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
                            '-t', f'{dur:.3f}', a], check=True)
        audio.append(a)
    enc.stdin.close(); enc.wait()
    open(f'{tmp}/a.txt', 'w').write(''.join(f"file '{a}'\n" for a in audio))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{tmp}/a.txt', f'{tmp}/a.wav'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{tmp}/v.mp4', '-i', f'{tmp}/a.wav', '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], check=True)
    print(out)


if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2])
