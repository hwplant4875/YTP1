"""Rewind-reaction short: footage plays to the shocking moment (punch zoom), white flash into a
full-screen reaction meme with a short caption and a Vine Boom, white flash back to the footage rewound ~1 s,
and on to the next beat. One clip can carry several beats. Original audio only, no music.

    python3 rewind.py spec.json out.mp4

spec:
  "font": TTF, "boom": sfx path
  "segments": [
    {"type": "clip", "src", "in", "out", "ratio", "crop": [x, y, w, h] (source content box, drops letterbox bars),
     "track": [[t, x, y, zoom], ...], "hits": [{"at": t, "x", "y", "zoom", "dur"}],   times are source times;
     each hit eases from wherever the previous one left the frame
     "circles": [{"from", "to", "track": [[t, x, y], ...], "rx", "ry"}]   red ring on the source (x, y as fractions of the frame, radii of its width),
     "sfx": [{"at", "src", "ss", "vol", "dur", "rate"}],   rate < 1 plays the sound slower and lower
     "speed": [[t, factor], ...]   from source time t on, play at factor (0.5 = slow-mo, 1.6 = fast-forward);
                                   slow parts are motion-interpolated}, audio follows with atempo
     "reverse": factor   play out -> in backwards at this speed (the rewind between a moment and its replay), silent
     "grade": {"b", "c", "s"}   "edit look": brightness offset (0-1), contrast and saturation gains, eased in
    {"type": "meme", "src" (video or still image), "ss", "dur", "hold" (freeze after this many s), "cap",
     "boomVol"}]
  optional: "bgm": {"src", "ss", "vol"} (music bed under the whole short, fades out at the end),
  "memeBg": "blur" | "black", "capSize", "capY" (caption centre; the meme sits just above it), "title": {"text", "y", "size"} (fixed caption on every frame,
  emoji allowed)
"""
import json, os, subprocess, sys, tempfile
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catreact2 import W, H, FPS, compose, interp, sharpen, stream  # noqa: E402

PUNCH = 0.5      # seconds for the zoom-in to settle (ease-out: steep start, flat finish)
FLASH_IN = [0.1, 0.4, 0.7, 1.0]                # last frames before a cut: fade to white (measured on POSTERlSED)
FLASH_OUT = [1.0, 1.0, 0.78, 0.56, 0.36, 0.16]    # first frames after a cut: hold white, fade out
EMOJI = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'


def speed_at(s, t):
    f = 1.0
    for k, v in s.get('speed', []):
        if t >= k - 1e-6:
            f = v
    return f


def src_times(s):
    """source time of every output frame, following the clip's speed map"""
    ts, t = [], s['in']
    while t < s['out'] - 1e-6:
        ts.append(t)
        t += speed_at(s, t) / FPS
    return ts


def frame_count(s):
    if s['type'] == 'clip':
        if s.get('reverse'):
            return max(1, round((s['out'] - s['in']) * FPS / s['reverse']))
        return len(src_times(s)) if s.get('speed') else round((s['out'] - s['in']) * FPS)
    return round(s['dur'] * FPS)


def ease(u):
    """ease-out quart: concave curve, fast at first then flattening out"""
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** 4


def timed_frames(s, n):
    """frames resampled along the speed map; the clip is motion-interpolated to 60 fps first"""
    w, h = map(int, subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries',
                                    'stream=width,height', '-of', 'csv=p=0', s['src']],
                                   capture_output=True, text=True).stdout.split(',')[:2])
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f"{s['in']:.3f}", '-t', f"{s['out'] - s['in'] + 0.2:.3f}",
                          '-i', s['src'], '-vf', 'minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,'
                          'format=rgb24', '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    for t in src_times(s)[:n]:
        u = (t - s['in']) * 60
        i = min(int(u), len(fr) - 1)
        k = u - int(u)
        if k < 0.05 or i + 1 >= len(fr):
            yield t, fr[i]
        else:
            yield t, cv2.addWeighted(fr[i], 1 - k, fr[i + 1], k, 0)


def plain_frames(s, n):
    last = None
    frames = stream(s['src'], s['in'], s['out'] - s['in'] + 0.2)
    for j in range(n):
        fr = next(frames, None)
        fr = last if fr is None else fr
        last = fr
        yield s['in'] + j / FPS, fr


def reverse_frames(s, n):
    frames = list(stream(s['src'], s['in'], s['out'] - s['in'] + 0.05))
    for j in range(n):
        t = s['out'] - j * s['reverse'] / FPS
        yield t, frames[min(max(int(round((t - s['in']) * FPS)), 0), len(frames) - 1)]


def grade(fr, g, k):
    """slight brightness / contrast / saturation lift, k = 0..1 blend"""
    if k <= 0:
        return fr
    f = fr.astype(np.float32)
    f = (f - 128) * (1 + (g.get('c', 1.0) - 1) * k) + 128 + 255 * g.get('b', 0.0) * k
    grey = f.mean(axis=2, keepdims=True)
    f = grey + (f - grey) * (1 + (g.get('s', 1.0) - 1) * k)
    return np.clip(f, 0, 255).astype(np.uint8)


def clip_frames(s, n):
    x0, y0, cw, ch = s.get('crop', [0, 0, 0, 0])
    gen = reverse_frames if s.get('reverse') else timed_frames if s.get('speed') else plain_frames
    for j, (t, fr) in enumerate(gen(s, n)):
        if cw:
            fr = fr[y0:y0 + ch, x0:x0 + cw]
        x, y, z = interp(s.get('track', [[0, 0.5, 0.5, 1.0]]), t)
        bz = z
        for h in sorted(s.get('hits', []), key=lambda h: h['at']):
            if h['at'] > t:
                break
            e = ease((t - h['at']) / h.get('dur', PUNCH))
            x, y = x + (h.get('x', x) - x) * e, y + (h.get('y', y) - y) * e
            z += (bz * h.get('zoom', 1.3) - z) * e
        for c in s.get('circles', []):
            if c['from'] <= t <= c['to']:
                fr = ring(fr, c, t)
        if s.get('grade'):
            fr = grade(fr, s['grade'], ease(j / (0.3 * FPS)))
        yield sharpen(compose(fr, {'ratio': s.get('ratio', '9:16'), 'track': [[0, x, y, z]], 'lift': 0}, t))


def ring(fr, c, t):
    """hand-drawn style red ellipse that pops in slightly oversized and settles"""
    fr = fr.copy()
    sh, sw = fr.shape[:2]
    cx, cy, _ = interp([k + [1.0] for k in c['track']], t)
    pop = 1 + 0.35 * (1 - ease((t - c['from']) / 0.15))
    rx, ry = c['rx'] * sw * pop, c.get('ry', c['rx']) * sw * pop
    th = max(3, int(sw * 0.009))
    cv2.ellipse(fr, (int(cx * sw), int(cy * sh)), (int(rx), int(ry)), -8, 0, 360, (0, 0, 0), th + 4, cv2.LINE_AA)
    cv2.ellipse(fr, (int(cx * sw), int(cy * sh)), (int(rx), int(ry)), -8, 0, 360, (235, 20, 20), th, cv2.LINE_AA)
    return fr


def is_emoji(ch):
    return ord(ch) >= 0x2190 and not ('\u3000' <= ch <= '\uffef')


def caption_rgba(font, text, y, size=96):
    """white text with black stroke, centred at y; emoji drawn from Noto Color Emoji"""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    runs = []
    for ch in text:
        e = is_emoji(ch) or ch in '\ufe0f\u200d'
        if runs and runs[-1][0] == e:
            runs[-1][1] += ch
        else:
            runs.append([e, ch])
    while True:
        f = ImageFont.truetype(font, size)
        widths = [len([c for c in r if c not in '\ufe0f\u200d']) * size * 1.1 if e else d.textlength(r, font=f)
                  for e, r in runs]
        if sum(widths) <= 960 or size <= 36:
            break
        size -= 4
    stroke = max(4, size // 12)
    x = (W - sum(widths)) / 2
    ef = ImageFont.truetype(EMOJI, 109)
    for (e, r), w in zip(runs, widths):
        if not e:
            d.text((x, y), r, font=f, fill='white', stroke_width=stroke, stroke_fill='black', anchor='lm')
        else:
            for c in [c for c in r if c not in '\ufe0f\u200d']:
                g = Image.new('RGBA', (136, 128), (0, 0, 0, 0))
                ImageDraw.Draw(g).text((0, 0), c, font=ef, embedded_color=True)
                g = g.crop(g.getbbox() or (0, 0, 1, 1)).resize((int(size * 1.0), int(size * 1.0)), Image.LANCZOS)
                im.alpha_composite(g, (int(x + size * 0.05), int(y - size / 2)))
                x += size * 1.1
            continue
        x += w
    return np.asarray(im)


def over(img, rgba):
    a = rgba[..., 3:4].astype(np.float32) / 255
    return (img * (1 - a) + rgba[..., :3] * a).astype(np.uint8)


def meme_frames(spec, s, n):
    if s['src'].lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        im = Image.open(s['src']).convert('RGB')
        mh = int(round(im.height * W / im.width / 2)) * 2
        fr = np.asarray(im.resize((W, mh), Image.LANCZOS))[None]
    else:
        fr, mh = video_meme(s, n)
    if s.get('hold'):
        fr = fr[:max(1, int(s['hold'] * FPS))]           # freeze before the meme's own cut or zoom
    top = max(0, 860 - mh // 2)
    cap = None
    cs = spec.get('capSize', 96)
    if spec.get('capY') and s.get('cap'):
        room = int(spec['capY'] - cs * 0.8) - 260          # meme sits between the title and the centred caption
        if mh > room / 0.8:                                # tall meme: full size, caption laid over its centre
            top = max(0, 960 - mh // 2)
        elif mh > room:                                    # slightly too tall: shrink it a little, black sides
            mw = int(W * room / mh) // 2 * 2
            fr = np.stack([np.pad(cv2.resize(f, (mw, room), interpolation=cv2.INTER_AREA),
                                  ((0, 0), ((W - mw) // 2, W - mw - (W - mw) // 2), (0, 0))) for f in fr])
            mh = room
        if mh <= room:
            top = int(spec['capY'] - cs * 0.8 - mh)
    elif spec.get('capY'):
        top = max(0, 960 - mh // 2)
    if s.get('cap'):
        cap = caption_rgba(spec['font'], s['cap'], spec.get('capY') or min(top + mh + cs * 0.8, 1480), cs)
    for j in range(n):
        m = fr[min(j, len(fr) - 1)]
        if spec.get('memeBg') == 'black':
            bg = np.zeros((H, W, 3), np.uint8)
        else:
            bg = cv2.resize(m, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
            bg = cv2.GaussianBlur(bg, (0, 0), 6)
            bg = (cv2.resize(bg, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) * 0.6).astype(np.uint8)
        bg[top:top + min(mh, H - top)] = m[:H - top]
        if cap is not None:
            bg = over(bg, cap)
        yield sharpen(bg)


def video_meme(s, n):
    w, h = map(int, subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries',
                                    'stream=width,height', '-of', 'csv=p=0', s['src']],
                                   capture_output=True, text=True).stdout.split(',')[:2])
    mh = int(round(h * W / w / 2)) * 2
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-stream_loop', '-1', '-ss', f"{s.get('ss', 0):.3f}", '-i', s['src'],
                          '-t', f'{n / FPS + 0.1:.3f}', '-vf', f'scale={W}:{mh}:flags=lanczos,fps={FPS},format=rgb24',
                          '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, mh, W, 3), mh


def build(spec, out):
    tmp = tempfile.mkdtemp(prefix='rewind_')
    segs = spec['segments']
    counts = [frame_count(s) for s in segs]
    title = None
    if spec.get('title'):
        tt = spec['title']
        title = caption_rgba(spec['font'], tt['text'], tt.get('y', 250), tt.get('size', 64))
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
            if title is not None:
                img = over(img, title)
            enc.stdin.write(np.ascontiguousarray(img).tobytes())
        dur = n / FPS
        a = f'{tmp}/a{i}.wav'
        has_a = s['type'] == 'clip' and not s.get('reverse') and subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', s['src']],
            capture_output=True, text=True).stdout.strip()
        if has_a and s.get('speed'):
            # constant-speed pieces, each time-stretched with atempo (pitch kept), then joined
            cuts = sorted({s['in'], s['out']} | {k for k, _ in s['speed'] if s['in'] < k < s['out']})
            parts = []
            for q, (p0, p1) in enumerate(zip(cuts, cuts[1:])):
                f, pa = speed_at(s, p0), f'{tmp}/a{i}_{q}.wav'
                tempo = []
                while f < 0.5:
                    tempo.append('atempo=0.5'); f /= 0.5
                tempo.append(f'atempo={f:.4f}')
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{p0:.3f}', '-t', f'{p1 - p0:.3f}', '-i', s['src'],
                                '-af', ','.join(tempo) + ',aresample=48000', '-ac', '2', pa], check=True)
                parts.append(pa)
            open(f'{tmp}/p{i}.txt', 'w').write(''.join(f"file '{x}'\n" for x in parts))
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{tmp}/p{i}.txt',
                            '-af', f"volume={s.get('vol', 1.0)},afade=t=in:d=0.04,afade=t=out:st={dur - 0.1:.3f}:d=0.1,"
                                   "apad", '-t', f'{dur:.3f}', a], check=True)
        elif has_a:
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{s['in']:.3f}", '-t', f'{dur:.3f}', '-i', s['src'],
                            '-af', f"volume={s.get('vol', 1.0)},aresample=48000,afade=t=in:d=0.04,"
                                   f"afade=t=out:st={dur - 0.1:.3f}:d=0.1,apad", '-t', f'{dur:.3f}', '-ac', '2', a], check=True)
        else:
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
                            '-t', f'{dur:.3f}', a], check=True)
            if s['type'] == 'meme':
                sfx.append((spec['boom'], 0, starts[i] / FPS - 0.05, s.get('boomVol', 0.6), None, None))
        for e in s.get('sfx', []):
            if s['type'] == 'clip' and s.get('speed'):
                off = sum(1 for x in src_times(s) if x < e['at']) / FPS
            else:
                off = e['at'] - s.get('in', 0)
            sfx.append((e['src'], e.get('ss', 0), starts[i] / FPS + off, e.get('vol', 0.8), e.get('dur'), e.get('rate')))
        audio.append(a)
    enc.stdin.close(); enc.wait()
    total = starts[-1] / FPS
    open(f'{tmp}/a.txt', 'w').write(''.join(f"file '{a}'\n" for a in audio))
    ins, chain, mix = ['-f', 'concat', '-safe', '0', '-i', f'{tmp}/a.txt'], '', ['[0:a]']
    for k, (f, ss, at, vol, d, rate) in enumerate(sfx):
        ins += ['-ss', f'{ss:.3f}'] + (['-t', f'{d:.3f}'] if d else []) + ['-i', f]
        fade = f"afade=t=out:st={d - 0.12:.3f}:d=0.12," if d else ''
        slow = f"aresample=48000,asetrate={48000 * rate:.0f}," if rate else ''
        chain += f"[{k + 1}:a]{fade}{slow}volume={vol},adelay={int(max(at, 0) * 1000)}:all=1,aresample=48000[s{k}];"
        mix.append(f'[s{k}]')
    if spec.get('bgm'):
        b = spec['bgm']
        k = len(sfx) + 1
        ins += ['-ss', f"{b.get('ss', 0):.3f}", '-i', b['src']]
        chain += (f"[{k}:a]volume={b.get('vol', 0.4)},aresample=48000,afade=t=in:d=0.05,"
                  f"afade=t=out:st={max(total - 0.8, 0):.3f}:d=0.8[bg];")
        mix.append('[bg]')
    chain += f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0[a]"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', chain, '-map', '[a]', '-t', f'{total:.3f}',
                    f'{tmp}/a.wav'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{tmp}/v.mp4', '-i', f'{tmp}/a.wav', '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out], check=True)
    print(out, round(total, 1))


if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2])
