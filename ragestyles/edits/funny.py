"""Gym Funny Moments ranking short: full 9:16 (per-clip ratio + blurred fill, crop keyframes for focus and
punch zooms), a left 1-5 list whose labels are tiny reactions with an emoji, typed in at the funny moment.
Slots fill out of order. Original audio only, plus timed SFX. Hard cuts, no slow-mo, no music.

    python3 funny.py spec.json out.mp4

spec:
  "font": TTF, "emoji": NotoColorEmoji.ttf
  "clips": [{"src", "in", "out", "ratio", "track": [[t, x, y, zoom], ...],
             "rank": 4, "label": "Unclipped", "emo": "💀", "labelAt": t,
             "sfx": [{"at": t, "src", "vol"}]}]          times are source times
"""
import json, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catreact2 import W, H, FPS, compose, sharpen, stream  # noqa: E402

TYPE = 0.4   # seconds to type a label


def emoji_img(path, ch, size):
    f = ImageFont.truetype(path, 109)
    im = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), ch, font=f, embedded_color=True, anchor='mm')
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * size / im.height), size), Image.LANCZOS)


def list_rgba(spec, filled, typing):
    """filled: {rank: (label, emo)}; typing: (rank, fraction 0..1) for the label being typed"""
    L = spec.get('list', {})
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(spec['font'], L.get('size', 64))
    cols = L.get('colors', {1: '#ffd400', 2: '#ff3b3b', 3: '#3ba0ff', 4: '#ffffff', 5: '#ffffff'})
    for r in range(1, 6):
        x, y = L.get('x', 40), L.get('y', 520) + (r - 1) * L.get('gap', 104)
        d.text((x, y), f'{r}.', font=f, fill=cols.get(r, '#fff'), stroke_width=7, stroke_fill='black', anchor='ls')
        if r not in filled:
            continue
        label, emo = filled[r]
        frac = typing[1] if typing and typing[0] == r else 1.0
        n = int(round(len(label) * min(frac / 0.85, 1)))
        nx = x + d.textlength(f'{r}. ', font=f)
        d.text((nx, y), label[:n], font=f, fill='white', stroke_width=7, stroke_fill='black', anchor='ls')
        if emo and frac >= 0.9:
            e = emoji_img(spec['emoji'], emo, int(L.get('size', 64) * 0.95))
            im.alpha_composite(e, (int(nx + d.textlength(label + ' ', font=f)), int(y - e.height * 0.92)))
    return np.asarray(im)


def blend(canvas, rgba):
    a = rgba[..., 3:4].astype(np.float32) / 255
    return (canvas * (1 - a) + rgba[..., :3] * a).astype(np.uint8)


def build(spec, out):
    tmp = tempfile.mkdtemp(prefix='funny_')
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                            '-pix_fmt', 'yuv420p', f'{tmp}/v.mp4'], stdin=subprocess.PIPE)
    filled, audio, sfx, t = {}, [], [], 0.0
    cache = {}
    for ci, c in enumerate(spec['clips']):
        n = 0
        for j, fr in enumerate(stream(c['src'], c['in'], c['out'] - c['in'])):
            ts = c['in'] + j / FPS
            canvas = sharpen(compose(fr, c, ts))
            age = ts - c['labelAt']
            cur = dict(filled)
            typing = None
            if age >= 0:
                cur[c['rank']] = (c['label'], c.get('emo', ''))
                if age < TYPE:
                    typing = (c['rank'], age / TYPE)
            key = (tuple(sorted(cur.items())), typing and round(typing[1], 2))
            if key not in cache:
                cache[key] = list_rgba(spec, cur, typing)
            canvas = blend(canvas, cache[key])
            enc.stdin.write(np.ascontiguousarray(canvas).tobytes())
            n += 1
        filled[c['rank']] = (c['label'], c.get('emo', ''))
        for s in c.get('sfx', []):
            sfx.append((s['src'], t + s['at'] - c['in'], s.get('vol', 0.6)))
        has_a = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index',
                                '-of', 'csv=p=0', c['src']], capture_output=True, text=True).stdout.strip()
        a = f'{tmp}/a{ci}.wav'
        dur = n / FPS
        if has_a:
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{c['in']:.3f}", '-t', f'{dur:.3f}', '-i', c['src'], '-af',
                            f"volume={c.get('vol', 1.0)},aresample=48000,afade=t=in:d=0.05,afade=t=out:st={dur - 0.08:.3f}:d=0.08,apad",
                            '-t', f'{dur:.3f}', '-ac', '2', a], check=True)
        else:
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', f'{dur:.3f}', a], check=True)
        audio.append(a)
        t += dur
    enc.stdin.close(); enc.wait()
    total = t
    open(f'{tmp}/a.txt', 'w').write(''.join(f"file '{a}'\n" for a in audio))
    ins, chain, mix = ['-f', 'concat', '-safe', '0', '-i', f'{tmp}/a.txt'], '', ['[0:a]']
    for k, (f, at, vol) in enumerate(sfx):
        ins += ['-i', f]
        chain += f"[{k + 1}:a]volume={vol},adelay={int(at * 1000)}:all=1,aresample=48000[s{k}];"
        mix.append(f'[s{k}]')
    chain += f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0[a]"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', chain, '-map', '[a]', '-t', f'{total:.3f}',
                    f'{tmp}/a.wav'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{tmp}/v.mp4', '-i', f'{tmp}/a.wav', '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out], check=True)
    print(out, round(total, 1))


if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2])
