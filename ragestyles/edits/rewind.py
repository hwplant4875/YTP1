"""Rewind-reaction short: footage plays to the shocking moment (punch zoom), white flash into a
full-screen reaction meme with a short caption and a Vine Boom, white flash back to the footage rewound ~1 s,
and on to the next beat. One clip can carry several beats. Original audio only, no music.

    python3 rewind.py spec.json out.mp4

spec:
  "font": TTF, "boom": sfx path
  "segments": [
    {"type": "clip", "src", "in", "out", "ratio", "crop": [x, y, w, h] (source content box, drops letterbox bars),
     "track": [[t, x, y, zoom], ...], "hits": [{"at": t, "x", "y", "zoom"}]},      times are source times
    {"type": "meme", "src", "ss", "dur", "cap", "boomVol"}]
"""
import json, os, subprocess, sys, tempfile
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catreact2 import W, H, FPS, compose, interp, sharpen, stream  # noqa: E402

PUNCH = 0.5      # seconds for the zoom-in to settle (ease-out: steep start, flat finish)
FLASH_IN = [0.2, 0.5, 0.8, 1.0]                # last frames before a cut: fade to white (matches the reference)
FLASH_OUT = [1.0, 1.0, 0.8, 0.58, 0.37, 0.15]     # first frames after a cut: hold white, fade out


def ease(u):
    """ease-out quart: concave curve, fast at first then flattening out"""
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** 4


def clip_frames(s, n):
    x0, y0, cw, ch = s.get('crop', [0, 0, 0, 0])
    last = None
    frames = stream(s['src'], s['in'], s['out'] - s['in'] + 0.2)
    for j in range(n):
        fr = next(frames, None)
        fr = last if fr is None else fr
        last = fr
        if cw:
            fr = fr[y0:y0 + ch, x0:x0 + cw]
        t = s['in'] + j / FPS
        x, y, z = interp(s.get('track', [[0, 0.5, 0.5, 1.0]]), t)
        hits = [h for h in s.get('hits', []) if h['at'] <= t]
        if hits:
            h = hits[-1]
            e = ease((t - h['at']) / h.get('dur', PUNCH))
            x, y = x + (h.get('x', x) - x) * e, y + (h.get('y', y) - y) * e
            z *= 1 + (h.get('zoom', 1.3) - 1) * e
        yield sharpen(compose(fr, {'ratio': s.get('ratio', '9:16'), 'track': [[0, x, y, z]], 'lift': 0}, t))


def caption_rgba(font, text, y):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    size = 96
    f = ImageFont.truetype(font, size)
    while d.textlength(text, font=f) > 960 and size > 40:
        size -= 4
        f = ImageFont.truetype(font, size)
    d.text((W / 2, y), text, font=f, fill='white', stroke_width=8, stroke_fill='black', anchor='mm')
    return np.asarray(im)


def meme_frames(spec, s, n):
    w, h = map(int, subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries',
                                    'stream=width,height', '-of', 'csv=p=0', s['src']],
                                   capture_output=True, text=True).stdout.split(',')[:2])
    mh = int(round(h * W / w / 2)) * 2
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-stream_loop', '-1', '-ss', f"{s.get('ss', 0):.3f}", '-i', s['src'],
                          '-t', f'{n / FPS + 0.1:.3f}', '-vf', f'scale={W}:{mh}:flags=lanczos,fps={FPS},format=rgb24',
                          '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, mh, W, 3)
    top = max(0, 860 - mh // 2)
    cap = caption_rgba(spec['font'], s['cap'], min(top + mh + 70, 1480)) if s.get('cap') else None
    for j in range(n):
        m = fr[min(j, len(fr) - 1)]
        bg = cv2.resize(m, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
        bg = cv2.GaussianBlur(bg, (0, 0), 6)
        bg = (cv2.resize(bg, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) * 0.6).astype(np.uint8)
        bg[top:top + min(mh, H - top)] = m[:H - top]
        if cap is not None:
            a = cap[..., 3:4].astype(np.float32) / 255
            bg = (bg * (1 - a) + cap[..., :3] * a).astype(np.uint8)
        yield sharpen(bg)


def build(spec, out):
    tmp = tempfile.mkdtemp(prefix='rewind_')
    segs = spec['segments']
    counts = [round(((s['out'] - s['in']) if s['type'] == 'clip' else s['dur']) * FPS) for s in segs]
    starts = np.cumsum([0] + counts)
    white = np.zeros(int(starts[-1]), np.float32)
    for i, b in enumerate(starts[1:-1]):
        if 'meme' not in (segs[i]['type'], segs[i + 1]['type']):
            continue                       # clip to clip: hard cut
        for k, a in enumerate(FLASH_IN):
            white[b - len(FLASH_IN) + k] = max(white[b - len(FLASH_IN) + k], a)
        for k, a in enumerate(FLASH_OUT):
            white[b + k] = max(white[b + k], a)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                            '-pix_fmt', 'yuv420p', f'{tmp}/v.mp4'], stdin=subprocess.PIPE)
    audio, sfx = [], []
    for i, (s, n) in enumerate(zip(segs, counts)):
        gen = clip_frames(s, n) if s['type'] == 'clip' else meme_frames(spec, s, n)
        for j, img in enumerate(gen):
            a = white[starts[i] + j]
            if a:
                img = (img.astype(np.float32) * (1 - a) + 255 * a).astype(np.uint8)
            enc.stdin.write(np.ascontiguousarray(img).tobytes())
        dur = n / FPS
        a = f'{tmp}/a{i}.wav'
        has_a = s['type'] == 'clip' and subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', s['src']],
            capture_output=True, text=True).stdout.strip()
        if has_a:
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{s['in']:.3f}", '-t', f'{dur:.3f}', '-i', s['src'],
                            '-af', f"volume={s.get('vol', 1.0)},aresample=48000,afade=t=in:d=0.04,"
                                   f"afade=t=out:st={dur - 0.1:.3f}:d=0.1,apad", '-t', f'{dur:.3f}', '-ac', '2', a], check=True)
        else:
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
                            '-t', f'{dur:.3f}', a], check=True)
            if s['type'] == 'meme':
                sfx.append((spec['boom'], starts[i] / FPS - 0.05, s.get('boomVol', 0.6)))
        audio.append(a)
    enc.stdin.close(); enc.wait()
    total = starts[-1] / FPS
    open(f'{tmp}/a.txt', 'w').write(''.join(f"file '{a}'\n" for a in audio))
    ins, chain, mix = ['-f', 'concat', '-safe', '0', '-i', f'{tmp}/a.txt'], '', ['[0:a]']
    for k, (f, at, vol) in enumerate(sfx):
        ins += ['-i', f]
        chain += f"[{k + 1}:a]volume={vol},adelay={int(max(at, 0) * 1000)}:all=1,aresample=48000[s{k}];"
        mix.append(f'[s{k}]')
    chain += f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0[a]"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', chain, '-map', '[a]', '-t', f'{total:.3f}',
                    f'{tmp}/a.wav'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{tmp}/v.mp4', '-i', f'{tmp}/a.wav', '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out], check=True)
    print(out, round(total, 1))


if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2])
