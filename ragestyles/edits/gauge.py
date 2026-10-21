"""Full-frame 9:16 "pain meter" ranking short.

Each clip plays full screen; a meter under the title fills at the clip's impact
moment, pins a thumbnail of that fail at its score, and the last clip breaks the
meter. No left-side 1-5 list.

    python3 gauge.py spec.json out.mp4 [--preview]

spec: {"title": [[["Gym fails ranked by ", "#fff"], ["PAIN", "#ff3b3b"]]],
       "clips": [{"src", "in", "out", "hit" (s into the clip), "score" 0-100,
                  "label", "cap" (optional context line), "crop" (optional w:h:x:y)}]}
"""
import json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
FONT = '/mnt/project-files/fonts/TikTokSans-Black.ttf'
CAPFONT = '/mnt/project-files/fonts/YouTubeSans-Black.otf'
HIT = '/mnt/project-files/sfx/user/sub_hit_warm.wav'
BAR = (110, 452, 970, 500)  # meter rectangle, under the title, clear of the right-side buttons
TOP_Y = 236  # title top, below the Dynamic Island


def f(path, size):
    return ImageFont.truetype(path, size)


def stroke_text(d, xy, text, font, fill, sw=8, anchor='la'):
    d.text(xy, text, font=font, fill=fill, stroke_width=sw, stroke_fill='black', anchor=anchor)


def ease_out_back(x):
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def meter_color(p):
    # green -> yellow -> red
    stops = [(0, (60, 220, 90)), (0.5, (255, 214, 0)), (1, (255, 40, 40))]
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if p <= b:
            t = (p - a) / (b - a)
            return tuple(int(ca[i] + (cb[i] - ca[i]) * t) for i in range(3))
    return stops[-1][1]


def run(cmd, **kw):
    print(' '.join(map(str, cmd))[:300], file=sys.stderr)
    subprocess.run(cmd, check=True, **kw)


def build(spec, out, preview=False):
    work = os.path.splitext(out)[0] + '_work'
    os.makedirs(work, exist_ok=True)
    clips = spec['clips']
    # 1) base video: each clip filled to 9:16, punch-in zoom + white flash at impact, own audio kept
    parts, t0, timeline = [], 0.0, []
    for i, c in enumerate(clips):
        dur = c['out'] - c['in']
        h = c['hit']
        crop = f"crop={c['crop']}," if c.get('crop') else ''
        z = f"if(between(t,{h},{h + 0.5}),1+0.14*sin(PI*(t-{h})/0.5),1)"
        vf = (f"{crop}scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},"
              f"scale=w='trunc({W}*({z})/2)*2':h='trunc({H}*({z})/2)*2':eval=frame:flags=bicubic,crop={W}:{H},"
              f"unsharp=5:5:0.8,eq=contrast=1.06:saturation=1.12,"
              f"drawbox=0:0:{W}:{H}:white@0.85:t=fill:enable='between(t,{h},{h + 0.07})',"
              f"fps={FPS},format=yuv420p")
        af = f"aresample=48000,afade=in:d=0.08,afade=out:st={dur - 0.15:.3f}:d=0.15"
        p = f"{work}/p{i}.mp4"
        run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(c['in']), '-t', f'{dur:.3f}', '-i', c['src'],
             '-vf', vf, '-af', af, '-c:v', 'libx264', '-preset', 'veryfast' if preview else 'medium', '-crf', '17',
             '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', p])
        parts.append(p)
        timeline.append((t0, t0 + dur, t0 + h, c))
        t0 += dur
    total = t0
    lst = f'{work}/list.txt'
    open(lst, 'w').write(''.join(f"file '{os.path.abspath(p)}'\n" for p in parts))
    base = f'{work}/base.mp4'
    run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', base])

    # thumbnails of each impact frame (for the pins on the meter)
    thumbs = []
    for i, (a, b, hit, c) in enumerate(timeline):
        tp = f'{work}/t{i}.png'
        run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', f'{hit + 0.05:.3f}', '-i', base, '-frames:v', '1', tp])
        im = Image.open(tp).convert('RGB')
        s = min(im.size)
        im = im.crop(((im.width - s) // 2, int(im.height * 0.3), (im.width + s) // 2, int(im.height * 0.3) + s)).resize((104, 104))
        m = Image.new('L', (104, 104), 0); ImageDraw.Draw(m).ellipse((0, 0, 103, 103), fill=255)
        disc = Image.new('RGBA', (116, 116), (0, 0, 0, 0))
        dd = ImageDraw.Draw(disc); dd.ellipse((0, 0, 115, 115), fill=meter_color(c['score'] / 100) + (255,))
        disc.paste(im, (6, 6), m)
        thumbs.append(disc)

    # 2) overlay frames (RGBA) piped into ffmpeg
    tfont = f(FONT, 66); small = f(FONT, 30); big = f(FONT, 120); lab = f(FONT, 104); cap = f(CAPFONT, 58)
    random.seed(7)
    shards = [(random.uniform(-1, 1), random.uniform(-1.4, 0.2), random.uniform(12, 34), random.uniform(0, 6.28)) for _ in range(46)]
    n = int(round(total * FPS))
    x0, y0, x1, y1 = BAR
    best = 0
    sfx_times = []
    for i, (a, b, hit, c) in enumerate(timeline):
        sfx_times.append(hit)

    def score_at(t):
        """current meter value and index of the clip being shown"""
        for i, (a, b, hit, c) in enumerate(timeline):
            if a <= t < b or i == len(timeline) - 1:
                if t < hit:
                    # tension: meter creeps up a little before the impact
                    return i, min(c['score'], 4 + 10 * max(0, (t - a) / max(0.01, hit - a))), 0
                k = min(1, (t - hit) / 0.45)
                return i, c['score'] * ease_out_back(k), t - hit
        return len(timeline) - 1, 0, 0

    enc = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-i', base,
                            '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            *sum([['-i', HIT] for _ in sfx_times], []),
                            '-filter_complex',
                            '[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v];' +
                            ''.join(f'[{k + 2}:a]adelay={int(t * 1000)}|{int(t * 1000)},volume=-4dB[s{k}];' for k, t in enumerate(sfx_times)) +
                            '[0:a]' + ''.join(f'[s{k}]' for k in range(len(sfx_times))) +
                            f'amix=inputs={len(sfx_times) + 1}:normalize=0:duration=first[a]',
                            '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'veryfast' if preview else 'slow',
                            '-crf', '18', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out],
                           stdin=subprocess.PIPE)
    last = len(timeline) - 1
    for fi in range(n):
        t = fi / FPS
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        i, val, since = score_at(t)
        a, b, hit, c = timeline[i]
        broke = i == last and since > 0.35
        shake = 0
        if 0 < since < 0.35:
            shake = int(14 * (1 - since / 0.35) * math.sin(since * 90))
        # dark gradient behind the title + meter so they read on any footage
        for yy in range(0, 560, 8):
            d.rectangle((0, yy, W, yy + 8), fill=(0, 0, 0, int(150 * max(0, 1 - yy / 560))))
        # title
        y = TOP_Y
        for line in spec['title']:
            wsum = sum(d.textlength(s, font=tfont) for s, _ in line)
            x = (W - wsum) / 2
            for s, col in line:
                stroke_text(d, (x + shake, y), s, tfont, col, 7)
                x += d.textlength(s, font=tfont)
            y += 82
        # meter
        bx = shake
        if not broke:
            d.rounded_rectangle((x0 + bx - 6, y0 - 6, x1 + bx + 6, y1 + 6), 30, fill=(0, 0, 0, 200))
            d.rounded_rectangle((x0 + bx, y0, x1 + bx, y1), 24, fill=(40, 40, 40, 230))
            v = max(0, min(val, 100))
            fx = x0 + (x1 - x0) * v / 100
            if fx > x0 + 10:
                # gradient fill up to the current value
                for xx in range(int(x0), int(fx), 4):
                    col = meter_color((xx - x0) / (x1 - x0))
                    d.rectangle((xx + bx, y0 + 4, xx + 4 + bx, y1 - 4), fill=col + (255,))
                d.rounded_rectangle((x0 + bx, y0, fx + bx, y1), 24, outline=(255, 255, 255, 230), width=4)
            # "PAIN" tag left of the number
            stroke_text(d, (x0 + bx, y1 + 16), 'PAIN METER', small, (255, 255, 255, 235), 5)
            # pins of earlier fails sit on the meter at their score
            for j in range(i):
                sj = timeline[j][3]['score']
                px = x0 + (x1 - x0) * sj / 100
                img.alpha_composite(thumbs[j], (int(px - 58 + bx), y1 + 10))
            if t >= hit:
                pop = min(1, (t - hit) / 0.18)
                num = f"{int(round(max(0, min(val, 100))))}"
                fs = int(150 * (1.4 - 0.4 * pop))
                stroke_text(d, (W / 2 + bx, 760), num, f(FONT, fs), meter_color(min(1, val / 100)) + (255,), 10, 'mm')
        else:
            # the meter shatters: shards fly out from where it was, then a red "METER BROKEN" stamp
            k = since - 0.35
            for (vx, vy, sz, rot) in shards:
                cx = (x0 + x1) / 2 + vx * (x1 - x0) / 2 + vx * 900 * k
                cy = (y0 + y1) / 2 + vy * 600 * k + 1400 * k * k
                if cy > H + 50:
                    continue
                pts = [(cx + sz * math.cos(rot + q * 2.1 + k * 6), cy + sz * math.sin(rot + q * 2.1 + k * 6)) for q in range(3)]
                d.polygon(pts, fill=meter_color(abs(vx)) + (255,), outline=(255, 255, 255, 255))
            pop = min(1, k / 0.2)
            fs = int(132 * (1.6 - 0.6 * pop))
            stroke_text(d, (W / 2, 700), 'METER', f(FONT, fs), (255, 255, 255, 255), 11, 'mm')
            stroke_text(d, (W / 2, 700 + fs), 'BROKEN', f(FONT, fs), (255, 40, 40, 255), 11, 'mm')
        # new record stamp when this fail beats every earlier one
        if t >= hit + 0.45 and not broke and c['score'] > max([0] + [tt[3]['score'] for tt in timeline[:i]]) and i > 0:
            k = min(1, (t - hit - 0.45) / 0.15)
            stamp = Image.new('RGBA', (560, 120), (0, 0, 0, 0))
            sd = ImageDraw.Draw(stamp)
            sd.rounded_rectangle((4, 4, 556, 116), 18, fill=(255, 214, 0, 255), outline=(0, 0, 0, 255), width=6)
            sd.text((280, 62), 'NEW HIGH SCORE', font=f(FONT, 56), fill='black', anchor='mm')
            stamp = stamp.rotate(-6, expand=True, resample=Image.BICUBIC)
            sc = 1.5 - 0.5 * k
            stamp = stamp.resize((int(stamp.width * sc), int(stamp.height * sc)))
            img.alpha_composite(stamp, (int(W / 2 - stamp.width / 2), int(900 - stamp.height / 2)))
        # label word for this fail, after impact, lower centre
        if t >= hit + 0.25 and c.get('label'):
            k = min(1, (t - hit - 0.25) / 0.15)
            fs = int(104 * (1.3 - 0.3 * k))
            stroke_text(d, (W / 2, 1330), c['label'], f(FONT, fs), (255, 255, 255, 255), 10, 'mm')
        # context caption before impact
        if t < hit and c.get('cap'):
            words = c['cap']
            stroke_text(d, (W / 2, 1330), words, cap, (255, 230, 0, 255), 9, 'mm')
        enc.stdin.write(img.tobytes())
    enc.stdin.close()
    enc.wait()
    if enc.returncode:
        sys.exit('encode failed')


if __name__ == '__main__':
    sp = json.load(open(sys.argv[1]))
    build(sp, sys.argv[2], '--preview' in sys.argv)
