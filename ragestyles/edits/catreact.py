"""Cat-reaction fail short: 1:1 footage on top, a thick white line, a cat meme below that watches ("hmm") and
switches to a shocked cat on the fail. On the fail: slow-mo replay + quick score rows. No other text.
Next clip slides in with a whoosh.

    python3 catreact.py spec.json out.mp4

spec:
  "font": TTF, "pop": sfx, "whoosh": sfx
  "clips": [{"src", "in", "hit", "out", "cx", "cy",
             "replay": {"in", "out", "speed"},
             "watch": {"src", "cy"}, "shock": {"src", "cy"},
             "score": [["IMPACT", 8], ["FUNNY", 9]]}]   total row is added
"""
import json, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
SQ, LINE = 1080, 14              # footage square, white divider
MY, MH = SQ + LINE, H - SQ - LINE  # meme area
SLIDE = 7                         # frames for the slide-in


def frames(src, vf, w, h, ss=None, t=None):
    cmd = ['ffmpeg', '-v', 'error']
    if ss is not None:
        cmd += ['-ss', f'{ss:.3f}']
    if t is not None:
        cmd += ['-t', f'{t:.3f}']
    cmd += ['-i', src, '-vf', vf + f',fps={FPS},format=rgb24', '-f', 'rawvideo', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def square(c, ss, t, speed=1.0):
    pts = f"setpts=PTS/{speed}," if speed != 1 else ''
    vf = (f"{pts}crop='min(iw,ih)':'min(iw,ih)':'(iw-min(iw,ih))*{c.get('cx', 0.5)}':'(ih-min(iw,ih))*{c.get('cy', 0.5)}',"
          f"scale={SQ}:{SQ}:flags=lanczos,unsharp=5:5:0.5,eq=contrast=1.04:saturation=1.06")
    return frames(c['src'], vf, SQ, SQ, ss, t)


def meme(m):
    vf = (f"scale={W}:{MH}:force_original_aspect_ratio=increase:flags=lanczos,"
          f"crop={W}:{MH}:(iw-{W})/2:(ih-{MH})*{m.get('cy', 0.3)},unsharp=5:5:0.4")
    return frames(m['src'], vf, W, MH, m.get('ss'))


def score_layer(font_path, rows, shown, pop):
    """rows up to `shown` drawn; the newest one scaled by `pop` (>=1)."""
    im = Image.new('RGBA', (SQ, SQ), (0, 0, 0, 0))
    for k, (label, val) in enumerate(rows[:shown]):
        total = k == len(rows) - 1
        size = 120 if total else 96
        s = pop if k == shown - 1 else 1.0
        f = ImageFont.truetype(font_path, int(size * s))
        y = 720 + k * 118 + (14 if total else 0)
        d = ImageDraw.Draw(im)
        d.text((60, y), label, font=f, fill='white', stroke_width=8, stroke_fill='black', anchor='ls')
        x = 60 + d.textlength(label + ' ', font=f)
        d.text((x, y), str(val), font=f, fill='#ffd400', stroke_width=8, stroke_fill='black', anchor='ls')
    return im


def build(spec, out):
    tmp = tempfile.mkdtemp(prefix='cat_')
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                            '-pix_fmt', 'yuv420p', f'{tmp}/v.mp4'], stdin=subprocess.PIPE)
    audio, sfx, t, prev_sq = [], [], 0.0, None
    for ci, c in enumerate(spec['clips']):
        live = square(c, c['in'], c['out'] - c['in'])
        r = c['replay']
        slow = square(c, r['in'], r['out'] - r['in'], r['speed'])
        watch, shock = meme(c['watch']), meme(c['shock'])
        hit = round((c['hit'] - c['in']) * FPS)
        rows = [[a, b] for a, b in c['score']] + [['TOTAL', sum(b for _, b in c['score'])]]
        pop_at = [len(live) + 4 + k * 8 for k in range(len(rows))]
        seq = list(live) + list(slow)
        if ci:
            sfx.append((spec['whoosh'], t, 0.5))
        for k in pop_at:
            sfx.append((spec['pop'], t + k / FPS, 0.7))
        mi = 0
        for i, fr in enumerate(seq):
            canvas = np.zeros((H, W, 3), np.uint8)
            sq = fr
            if prev_sq is not None and i < SLIDE - 1:      # next clip pushes the last one out to the left
                off = int(SQ * (1 - (1 - (i + 1) / SLIDE) ** 3))
                sq = np.concatenate([prev_sq[:, off:], fr[:, :off]], axis=1)
            canvas[:SQ] = sq
            if i >= pop_at[0] - 4:
                shown = sum(1 for k in pop_at if i >= k)
                if shown:
                    age = i - pop_at[shown - 1]
                    pop = 1 + 0.35 * max(0, 1 - age / 4)
                    layer = score_layer(spec['font'], rows, shown, pop)
                    base = Image.fromarray(canvas[:SQ])
                    base.paste(layer, (0, 0), layer)
                    canvas[:SQ] = np.asarray(base)
            canvas[SQ:SQ + LINE] = 255
            m = watch[i % len(watch)] if i < hit else shock[min(i - hit, len(shock) - 1) if c['shock'].get('hold') else (i - hit) % len(shock)]
            canvas[MY:] = m
            enc.stdin.write(canvas.tobytes())
        prev_sq = seq[-1]
        # audio: live part, then slowed replay part
        has_a = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index',
                                '-of', 'csv=p=0', c['src']], capture_output=True, text=True).stdout.strip()
        for k, (ss, dur, sp) in enumerate([(c['in'], c['out'] - c['in'], 1.0), (r['in'], r['out'] - r['in'], r['speed'])]):
            a = f'{tmp}/a{ci}_{k}.wav'
            n = len(live) if k == 0 else len(slow)
            if has_a:
                tempo = ','.join(['atempo=0.5'] * (sp < 0.5) + [f'atempo={sp / (0.5 if sp < 0.5 else 1):.4f}']) if sp != 1 else 'anull'
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{ss:.3f}', '-t', f'{dur:.3f}', '-i', c['src'], '-af',
                                f'{tempo},volume={0.55 if k else 1.0},aresample=48000,apad', '-t', f'{n / FPS:.3f}', '-ac', '2', a], check=True)
            else:
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
                                '-t', f'{n / FPS:.3f}', a], check=True)
            audio.append(a)
        t += len(seq) / FPS
    enc.stdin.close(); enc.wait()
    total = t
    open(f'{tmp}/a.txt', 'w').write(''.join(f"file '{a}'\n" for a in audio))
    ins = ['-f', 'concat', '-safe', '0', '-i', f'{tmp}/a.txt']
    chain, mix = '', ['[0:a]']
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
