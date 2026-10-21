"""Full-frame 9:16 shorts editor (reference style: footage fills the screen, short title on top,
one-to-three-word pop captions, flash + hit on impacts, slow-motion replays).

    python3 ff.py spec.json out.mp4 [--preview]

spec:
  "title": [[["THE MOUNTAIN ", "#fff"], ["vs 511 KG", "#ffd400"]], ...]   lines shown the whole video (optional)
  "segs":  [{"src", "in", "out", "speed" (1 = normal, 0.4 = slow-mo), "zoom": [cx, cy, z0, z1] (centre as
            fraction of the source frame, zoom from z0 to z1 over the segment), "audio": gain dB or null to mute,
            "tag": "REPLAY" (small corner tag), "grade": true}]
  "caps":  [{"t": [[text, color], ...], "in", "out", "y" (default 1180), "size" (default 92)}]   output seconds
  "hits":  [t, ...]   output seconds: white flash + sub hit
  "endfade": seconds of fade at the end (audio only, video stays)
  "list":  {"x", "y", "gap", "size", "items": [{"n": "5.", "label": "HOOPER", "at": t}]}  classic ranked list on the left;
           numbers always shown, label appears at "at" and stays yellow while it is the latest one
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
TFONT = '/mnt/project-files/fonts/TikTokSans-Black.ttf'
CFONT = '/mnt/project-files/fonts/YouTubeSans-Black.otf'
HIT = '/mnt/project-files/sfx/user/sub_hit_warm.wav'


def run(cmd):
    subprocess.run(cmd, check=True)


def probe(src):
    o = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                        '-of', 'csv=p=0', '--', src], capture_output=True, text=True).stdout.strip().split(',')
    return int(o[0]), int(o[1])


def seg_video(s, out, preview):
    sw, sh = probe(s['src'])
    sp = s.get('speed', 1.0)
    dur = (s['out'] - s['in']) / sp
    cx, cy, z0, z1 = s.get('zoom', [0.5, 0.5, 1.0, 1.0])
    # base crop: largest 9:16 window of the source, then zoom in by z (animated, eased)
    bw, bh = (sw, sw * 16 / 9) if sw * 16 / 9 <= sh else (sh * 9 / 16, sh)
    e = f"(1-cos(PI*min(t/{dur:.3f},1)))/2"
    z = f"({z0}+({z1}-{z0})*{e})"
    cw, ch = f"({bw:.1f}/{z})", f"({bh:.1f}/{z})"
    x = f"max(0,min({sw}-{cw},{cx}*{sw}-{cw}/2))"
    y = f"max(0,min({sh}-{ch},{cy}*{sh}-{ch}/2))"
    if s.get('fit') == 'blur':  # landscape source: sharp band in the middle, blurred copy fills the frame
        pre = f"crop={s['pre']}," if s.get('pre') else ''
        fh = s.get('bandH', 1080)
        vf = [f"setpts=(PTS-STARTPTS)/{sp}", f"fps={FPS}", f"{pre}split[a][b]",
              f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,eq=brightness=-0.12[bg]",
              f"[b]scale={W}:{fh}:force_original_aspect_ratio=increase,crop={W}:{fh}[fg]",
              f"[bg][fg]overlay=0:{s.get('bandY', '(H-h)/2')}", "setsar=1"]
    else:
        vf = [f"setpts=(PTS-STARTPTS)/{sp}", f"fps={FPS}",
              f"crop=w='{cw}':h='{ch}':x='{x}':y='{y}':exact=1",
              f"scale={W}:{H}:flags=lanczos", "setsar=1"]
    if s.get('grade', True):
        vf.append("unsharp=5:5:0.6,eq=contrast=1.07:saturation=1.12:gamma=1.02")
    if sp < 1:  # smoother slow-mo
        vf.insert(1, f"minterpolate=fps={FPS}:mi_mode=blend")
    vf.append('format=yuv420p')
    ag = s.get('audio', 0)
    if ag is None:
        a_in = ['-f', 'lavfi', '-t', f'{dur:.3f}', '-i', 'anullsrc=r=48000:cl=stereo']
        amap = ['-map', '1:a']
        af = []
    else:
        a_in, amap = [], ['-map', '0:a']
        at = []
        r = sp
        while r < 0.5:
            at.append('atempo=0.5'); r /= 0.5
        if r != 1: at.append(f'atempo={r}')
        af = ['-af', ','.join(['aresample=48000'] + at + [f'volume={ag}dB', 'afade=in:d=0.05',
                                                           f'afade=out:st={max(0, dur - 0.12):.3f}:d=0.12'])]
    run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(s['in']), '-t', f"{s['out'] - s['in']:.3f}", '-i', s['src'],
         *a_in, '-filter_complex' if s.get('fit') == 'blur' else '-vf', ','.join(vf).replace(',[a]', ';[a]').replace(',[b]', ';[b]').replace(',[bg][fg]', ';[bg][fg]'), *af, *(['-map', '0:v'] if s.get('fit') != 'blur' else []), *amap, '-t', f'{dur:.3f}',
         '-c:v', 'libx264', '-preset', 'veryfast' if preview else 'medium', '-crf', '16',
         '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', out])
    return dur


def text_layer(d, parts, font, y, sw=10):
    wsum = sum(d.textlength(t, font=font) for t, _ in parts)
    x = (W - wsum) / 2
    for t, col in parts:
        d.text((x, y), t, font=font, fill=col, stroke_width=sw, stroke_fill='black', anchor='ls')
        x += d.textlength(t, font=font)


def build(spec, out, preview=False):
    work = os.path.splitext(out)[0] + '_work'
    os.makedirs(work, exist_ok=True)
    parts, t0, tags = [], 0.0, []
    for i, s in enumerate(spec['segs']):
        p = f'{work}/s{i}.mp4'
        d = seg_video(s, p, preview)
        if s.get('tag'):
            tags.append((t0, t0 + d, s['tag']))
        parts.append(p); t0 += d
    total = t0
    open(f'{work}/l.txt', 'w').write(''.join(f"file '{os.path.abspath(p)}'\n" for p in parts))
    base = f'{work}/base.mp4'
    run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{work}/l.txt', '-c', 'copy', base])

    hits = spec.get('hits', [])
    tfont = ImageFont.truetype(TFONT, spec.get('titleSize', 74))
    fonts = {}
    title_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(title_img)
    if spec.get('title'):  # soft dark band so the title reads on any footage
        for yy in range(0, 520, 4):
            td.rectangle((0, yy, W, yy + 4), fill=(0, 0, 0, int(165 * max(0.0, 1 - yy / 520) ** 1.4)))
    y = spec.get('titleY', 290)
    for line in spec.get('title', []):
        text_layer(td, line, tfont, y, 9)
        y += int(spec.get('titleSize', 74) * 1.12)

    n = int(round(total * FPS))
    fade = spec.get('endfade', 0.6)
    enc = subprocess.Popen(
        ['ffmpeg', '-loglevel', 'error', '-y', '-i', base,
         '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
         *sum([['-i', HIT] for _ in hits], []),
         '-filter_complex',
         '[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v];' +
         ''.join(f'[{k + 2}:a]adelay={int(t * 1000)}|{int(t * 1000)},volume=-6dB[h{k}];' for k, t in enumerate(hits)) +
         '[0:a]' + ''.join(f'[h{k}]' for k in range(len(hits))) +
         f'amix=inputs={len(hits) + 1}:normalize=0:duration=first,afade=out:st={total - fade:.3f}:d={fade}[a]',
         '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'veryfast' if preview else 'slow', '-crf', '17',
         '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for fi in range(n):
        t = fi / FPS
        img = title_img.copy()
        d = ImageDraw.Draw(img)
        for c in spec.get('caps', []):
            if c['in'] <= t < c['out']:
                size = c.get('size', 92)
                k = min(1, (t - c['in']) / 0.12)  # pop: 115% -> 100%
                base_f = fonts.setdefault(size, ImageFont.truetype(CFONT, size))
                wid = sum(d.textlength(tx, font=base_f) for tx, _ in c['t'])
                size_fit = int(size * min(1, 820 / wid))  # keep clear of the right-side buttons
                fs = int(size_fit * (1.15 - 0.15 * k))
                key = fs
                if key not in fonts:
                    fonts[key] = ImageFont.truetype(CFONT, fs)
                text_layer(d, [(tx, col) for tx, col in c['t']], fonts[key], c.get('y', 1180), max(6, fs // 9))
        L = spec.get('list')
        if L:
            lf = fonts.setdefault(('list', L.get('size', 52)), ImageFont.truetype(CFONT, L.get('size', 52)))
            shown = [it for it in L['items'] if it['at'] <= t]
            cur = max(shown, key=lambda it: it['at']) if shown else None
            for k, it in enumerate(L['items']):
                yy = L.get('y', 640) + k * L.get('gap', 96)
                d.text((L.get('x', 40), yy), it['n'], font=lf, fill='white', stroke_width=6, stroke_fill='black', anchor='ls')
                if it in shown:
                    nx = L.get('x', 40) + d.textlength(it['n'] + ' ', font=lf)
                    d.text((nx, yy), it['label'], font=lf, fill='#ffd400' if it is cur else 'white',
                           stroke_width=6, stroke_fill='black', anchor='ls')
        for a, b, tag in tags:
            if a <= t < b:
                f = fonts.setdefault('tag', ImageFont.truetype(TFONT, 44))
                tw = d.textlength(tag, font=f)
                d.rounded_rectangle((60, 520, 60 + tw + 44, 590), 14, fill=(230, 30, 30, 235))
                d.text((82, 572), tag, font=f, fill='white', anchor='ls')
        for h in hits:
            if h <= t < h + 0.1:
                a = int(220 * (1 - (t - h) / 0.1))
                d.rectangle((0, 0, W, H), fill=(255, 255, 255, a))
        enc.stdin.write(img.tobytes())
    enc.stdin.close(); enc.wait()
    if enc.returncode:
        sys.exit('encode failed')
    print(f'{out}  {total:.2f}s')


if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2], '--preview' in sys.argv)
