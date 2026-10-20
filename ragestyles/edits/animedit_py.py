"""Anime / movie motivation edit renderer in Python (numpy + OpenCV + Pillow), same spec as animedit_ff.py.
Why a second renderer: ffmpeg's zoompan snaps the crop to whole pixels and has no radial blur, real multi-radius
glow or per-word glow text. Here every frame is one sub-pixel affine warp from the source (smooth push-ins and
shake with a little rotation), glow is three gaussian radii screened on, transitions get a zoom blur, and the
subtitles are Pillow glyphs with a soft coloured glow that pop in with easing. ffmpeg only decodes, mixes the
voice lines and encodes.

    python animedit_py.py spec.json ROOT [--nvenc]      ROOT = channel folder (src/, fonts/, shorts/)
"""
import json, os, subprocess, sys, tempfile
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from animedit_ff import FPS, H, W, frames_of, pieces_of   # one timing model for both renderers


def probe(src):
    o = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=width,height',
                        '-of', 'csv=p=0', src], capture_output=True, text=True).stdout.strip().split('\n')[0].split(',')
    return int(o[0]), int(o[1])


def decode(src, t0, dur):
    w, h = probe(src)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t0:.3f}', '-t', f'{dur:.3f}', '-i', src,
                          '-vf', f'fps={FPS},format=rgb24', '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def src_times(s):
    out = []
    for a, b, f in pieces_of(s):
        t = a
        while t < b - 1e-6:
            out.append(t); t += f / FPS
    return out


class Look:
    def __init__(self, g):
        self.g = g
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
        v = g.get('vig', 0.45 if g.get('vignette') else 0.0)
        self.vig = (1 - v * np.clip(r - 0.25, 0, 1) ** 1.6 / 0.75 ** 1.6)[..., None]
        rng = np.random.default_rng(3)
        self.grain = [rng.normal(0, 255 * g.get('grain', 0), (H // 2, W // 2, 1)).astype(np.float32) for _ in range(6)]

    def __call__(self, img, j):
        g = self.g
        f = img.astype(np.float32)
        if g.get('warm'):
            f[..., 0] *= 1 + g['warm']; f[..., 2] *= 1 - g['warm']
        f = (f - 128) * g.get('contrast', 1.15) + 128 + 255 * g.get('bright', 0)
        grey = f @ np.array([0.299, 0.587, 0.114], np.float32)
        f = grey[..., None] + (f - grey[..., None]) * g.get('sat', 1.25)
        b = g.get('black', 10)
        f = np.clip((f - b) * (255 / (255 - b)), 0, 255)
        if g.get('glow'):
            hi = cv2.resize(np.clip(f - 165, 0, None), (W // 4, H // 4), interpolation=cv2.INTER_AREA)
            gl = sum(cv2.GaussianBlur(hi, (0, 0), s) * k for s, k in ((2, .5), (7, .35), (18, .3)))
            gl = cv2.resize(gl, (W, H), interpolation=cv2.INTER_LINEAR) * (g['glow'] * 2.6 / 255)
            f = 255 - (255 - f) * np.clip(1 - gl, 0, 1)                                  # screen
        if g.get('sharpen'):
            f += (f - cv2.GaussianBlur(f, (0, 0), 1.4)) * g['sharpen']
        f *= self.vig
        if g.get('grain'):
            f += cv2.resize(self.grain[j % 6], (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
        return np.clip(f, 0, 255).astype(np.uint8)


def warp(fr, s, z, dx, dy, rot):
    """one sub-pixel affine from the source frame to the 9:16 canvas (or a letterbox band)"""
    sh, sw = fr.shape[:2]
    ratio = s.get('ratio', '9:16')
    ar = {'9:16': 9 / 16, '16:9': 16 / 9, '1:1': 1.0}[ratio]
    ow, oh = (W, H) if ratio == '9:16' else (W, int(W / ar) // 2 * 2)
    cw = min(sw, sh * ar); ch = cw / ar
    cx = min(max(s.get('x', 0.5) * sw, cw / 2), sw - cw / 2)
    cy = min(max(s.get('y', 0.5) * sh, ch / 2), sh - ch / 2)
    k = ow / cw * z
    vw, vh = ow / k, oh / k                                    # visible source window after zoom
    cx = min(max(cx, vw / 2), sw - vw / 2) + dx / k
    cy = min(max(cy, vh / 2), sh - vh / 2) + dy / k
    M = cv2.getRotationMatrix2D((cx, cy), rot, k)
    M[0, 2] += ow / 2 - cx; M[1, 2] += oh / 2 - cy
    band = cv2.warpAffine(fr, M, (ow, oh), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    if ratio == '9:16':
        return band
    img = np.zeros((H, W, 3), np.uint8)
    img[(H - oh) // 2:(H - oh) // 2 + oh] = band
    return img


def zoom_at(s, u, age):
    z = s.get('zoom', 1.0)
    z0, z1 = (z, z) if not isinstance(z, list) else z
    e = u * u if s.get('ease') == 'in' else 1 - (1 - u) ** 3
    return max(1.0, z0 + (z1 - z0) * e + s.get('punch', 0) * max(0.0, 1 - age / 0.2) ** 2)


def radial_blur(img, amt):
    acc = img.astype(np.float32)
    for i in range(1, 6):
        z = 1 + amt * i / 5
        M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
        acc += cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return (acc / 6).astype(np.uint8)


def shot_frames(s, look, rng):
    ts = src_times(s)
    frames = decode(s['src'], s['in'], s['out'] - s['in'] + 0.15)
    n = len(ts)
    img = None
    for j, t in enumerate(ts):
        fr = frames[min(int(round((t - s['in']) * FPS)), len(frames) - 1)]
        age = j / FPS
        amp = s.get('shake', 0) * max(0.0, 1 - age / 0.3)
        dx, dy = (amp * np.sin(age * 97), amp * np.cos(age * 71)) if amp else (0, 0)
        rot = amp * 0.06 * np.sin(age * 53) if amp else 0
        img = warp(fr, s, zoom_at(s, j / max(n - 1, 1), age), dx, dy, rot)
        img = look(img, j)
        tint = s.get('tint')
        if tint:
            gr = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)[..., None]
            col = {'bw': (1, 1, 1), 'red': (1.15, .28, .22), 'blue': (.3, .55, 1.1)}[tint]
            img = np.clip(gr * np.array(col, np.float32), 0, 255).astype(np.uint8)
        if s.get('smear') and j < 2:
            img = radial_blur(img, s['smear'] / 600 * (1 - j / 2))
        if s.get('rgb') and age < 0.2:
            p = s['rgb'] * (1 - age / 0.2)
            o = img.copy()
            o[..., 0] = cv2.warpAffine(img[..., 0], np.float32([[1, 0, p], [0, 1, 0]]), (W, H), borderMode=cv2.BORDER_REFLECT)
            o[..., 2] = cv2.warpAffine(img[..., 2], np.float32([[1, 0, -p], [0, 1, 0]]), (W, H), borderMode=cv2.BORDER_REFLECT)
            img = o
        for it in s.get('impact', []):
            if 0 <= age - it < 0.067:
                g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                img = np.repeat(np.where(g > 110, 0, 255).astype(np.uint8)[..., None], 3, axis=2)
        if s.get('strobe') and s['strobe'][0] <= age <= s['strobe'][1]:
            img = np.clip(img.astype(np.int16) + (115 if j % 4 < 2 else -128), 0, 255).astype(np.uint8)
        fl = s.get('flash')
        if fl and j < 3:
            k = [1.0, 0.55, 0.2][j]
            if fl == 'white':
                img = (img * (1 - k) + 255 * k).astype(np.uint8)
            elif fl == 'black':
                img = (img * (1 - k)).astype(np.uint8)
            elif fl == 'invert' and j < 2:
                img = 255 - img
        yield img
    for _ in range(int(round(s.get('freeze', 0) * FPS))):
        yield img


class Subs:
    """word glyphs (white, black stroke) over a soft coloured glow, placed exactly as the line will read"""
    def __init__(self, spec, root):
        self.items = []
        fpath = os.path.join(root, spec['font'])
        for l in spec.get('subs', []):
            size = l.get('size', 100)
            words = [w[0] for w in l['words']]
            f = ImageFont.truetype(fpath, size)
            while f.getlength(' '.join(words)) + size * 0.3 > W - 120:      # keep the line inside the frame
                size -= 2
                f = ImageFont.truetype(fpath, size)
            x0 = (W - f.getlength(' '.join(words))) / 2
            col = l.get('glow', '#ff2a2a')
            for k, (w, at, *fill) in enumerate(l['words']):
                x = x0 + f.getlength(' '.join(words[:k]) + (' ' if k else ''))
                pad = size // 2
                tw = int(f.getlength(w)) + 2 * pad
                th = int(size * 1.35) + 2 * pad
                glow = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
                ImageDraw.Draw(glow).text((pad, pad), w, font=f, fill=col, stroke_width=size // 9, stroke_fill=col)
                glow = glow.filter(ImageFilter.GaussianBlur(size / 6))
                crisp = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
                ImageDraw.Draw(crisp).text((pad, pad), w, font=f, fill=(fill or [l.get('fill', 'white')])[0], stroke_width=max(3, size // 16),
                                           stroke_fill='black')
                im = Image.alpha_composite(glow, glow)
                im = Image.alpha_composite(im, crisp)
                asc = f.getmetrics()[0]
                self.items.append((at, l['end'], np.asarray(im), x - pad, l.get('y', 1000) - asc / 2 - pad))

    def draw(self, img, t):
        for at, end, rgba, x, y in self.items:
            if not at <= t <= end:
                continue
            u = min(1.0, (t - at) / 0.1)
            sc = 1 + 0.22 * (1 - u) ** 2
            g = rgba if sc == 1 else cv2.resize(rgba, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR)
            h, w = g.shape[:2]
            cx, cy = x + rgba.shape[1] / 2, y + rgba.shape[0] / 2 - 12 * (1 - u)
            x0, y0 = int(cx - w / 2), int(cy - h / 2)
            xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
            if xa >= xb or ya >= yb:
                continue
            src = g[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32)
            a = src[..., 3:4] / 255 * u
            img[ya:yb, xa:xb] = (img[ya:yb, xa:xb] * (1 - a) + src[..., :3] * a).astype(np.uint8)


def build(spec, root, nvenc=False):
    os.chdir(root)
    spec['shots'][0].pop('flash', None)
    look, subs, rng = Look(spec.get('grade', {})), Subs(spec, root), np.random.default_rng(7)
    total = sum(frames_of(s) for s in spec['shots'])
    fo = int(round(spec.get('fadeout', 0.3) * FPS))
    tmp = tempfile.mkdtemp()
    venc = ['-c:v', 'libx264', '-preset', 'slow', '-crf', '17']
    if nvenc and subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=s=256x256:d=0.1', '-c:v', 'h264_nvenc',
                                 '-f', 'null', '-'], capture_output=True).returncode == 0:
        venc = ['-c:v', 'h264_nvenc', '-preset', 'p7', '-rc', 'vbr', '-cq', '17', '-b:v', '0']
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', *venc, '-pix_fmt', 'yuv420p', f'{tmp}/v.mp4'], stdin=subprocess.PIPE)
    n = 0
    for s in spec['shots']:
        want = frames_of(s)
        k = 0
        for img in shot_frames(s, look, rng):
            if k >= want:
                break
            img = np.ascontiguousarray(img)
            subs.draw(img, n / FPS)
            if n >= total - fo:
                img = (img * max(0.0, (total - n) / fo)).astype(np.uint8)
            enc.stdin.write(img.tobytes()); n += 1; k += 1
        while k < want:                                   # keep the timeline exact
            enc.stdin.write(img.tobytes()); n += 1; k += 1
    enc.stdin.close(); enc.wait()
    dur = n / FPS
    args = ['ffmpeg', '-v', 'error', '-y', '-i', f'{tmp}/v.mp4']
    voices = spec.get('voice', [])
    for v in voices:
        args += ['-ss', f"{v['in']:.3f}", '-t', f"{v['out'] - v['in']:.3f}", '-i', v['src']]
    if voices:
        g = []
        for j, v in enumerate(voices):
            d = int(v['at'] * 1000)
            g.append(f"[{j + 1}:a]asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
                     f"volume={v.get('vol', 1.0)},afade=t=in:d=0.03,afade=t=out:st={v['out'] - v['in'] - 0.08:.3f}:d=0.08,"
                     f"adelay={d}|{d}[va{j}]")
        g.append(''.join(f'[va{j}]' for j in range(len(voices))) +
                 f'amix=inputs={len(voices)}:normalize=0:duration=longest,apad,atrim=0:{dur:.3f}[a]')
        args += ['-filter_complex', ';'.join(g), '-map', '0:v', '-map', '[a]']
    else:
        args += ['-f', 'lavfi', '-t', f'{dur:.3f}', '-i', 'anullsrc=r=48000:cl=stereo', '-map', '0:v', '-map', '1:a']
    os.makedirs('shorts', exist_ok=True)
    out = f"shorts/{spec['name']}.mp4"
    subprocess.run(args + ['-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', f'{dur:.3f}', '-movflags', '+faststart',
                           out], check=True)
    print(out, f'{dur:.2f}s')


if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), os.path.abspath(sys.argv[2]), '--nvenc' in sys.argv)
