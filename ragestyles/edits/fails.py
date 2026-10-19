"""9:16 full-frame ranking edit for vertical sources (gym fails): footage covers the whole canvas, title on top,
ranked list on the left, one short caption per shot. Same fixed reveal as rank.py (eased zoom-in with a ~30%
brightness bump that eases back as the zoom lands). Only basic moves: slow-mo ("speed") and an eased push-in ("push").

    python3 fails.py spec.json out.mp4

spec:
  "title": [["RANKING THE", "#fff"], ["WORST GYM FAILS", "#ffd400"]]
  "font", "capFont": TTF paths
  "entries": [{"rank": 5, "name": "SMITH TRAP",
               "shots": [{"src", "in", "out", "cx", "cy", "zoom", "speed", "push", "cap"}]}]
"""
import json, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30


def run(cmd):
    subprocess.run(cmd, check=True)


def shot(s, out, reveal=None):
    sp = s.get('speed', 1.0)
    src_dur = s['out'] - s['in']
    dur = src_dur / sp
    cx, cy, z0 = s.get('cx', 0.5), s.get('cy', 0.5), s.get('zoom', 1.0)
    vf = [f"setpts=PTS/{sp}" if sp != 1 else "null", f"fps={FPS}",
          f"crop='min(iw,ih*{W}/{H})':'min(ih,iw*{H}/{W})'", f"scale={W}:{H}:flags=lanczos"]
    if reveal:
        T, z1, b = reveal['dur'], reveal['zoom'], reveal['bright']
        p = f"min(t/{T},1)"
        z = f"({z0}*(1+({z1}-1)*(1-cos(PI*{p}))/2))"
        bump = f"({b}*sin(PI*{p}))"
        eq = f",eq=eval=frame:brightness='0.35*{bump}':gamma='1+{bump}'"
    elif s.get('push'):
        p = f"min(t/{dur:.3f},1)"
        z = f"({z0}*(1+({s['push']}-1)*(1-cos(PI*{p}))/2))"
        eq = ''
    else:
        z, eq = f"{z0}", ''
    vf += [f"crop=w='iw/{z}':h='ih/{z}':x='(iw-iw/{z})*{cx}':y='(ih-ih/{z})*{cy}':exact=1",
           f"scale={W}:{H}:flags=lanczos" + eq,
           "unsharp=5:5:0.5,eq=contrast=1.05:saturation=1.08:brightness=0.01", "setsar=1", "format=yuv420p"]
    af = [f"atempo={sp}" if sp != 1 else "anull", f"volume={s.get('vol', 1.0)}", "aresample=48000",
          "afade=t=in:d=0.06", f"afade=t=out:st={dur - 0.1:.3f}:d=0.1"]
    run(['ffmpeg', '-v', 'error', '-y', '-ss', str(s['in']), '-t', f'{src_dur:.3f}', '-i', s['src'],
         '-vf', ','.join(vf), '-af', ','.join(af), '-t', f'{dur:.3f}', '-c:v', 'libx264', '-preset', 'medium',
         '-crf', '16', '-c:a', 'aac', '-b:a', '192k', '-ac', '2', out])
    return dur


def text(d, xy, txt, font, fill, anchor, stroke=6):
    d.text(xy, txt, font=font, fill=fill, stroke_width=stroke, stroke_fill='black', anchor=anchor)


def fit(d, txt, path, size, maxw):
    while size > 30 and d.textlength(txt, font=ImageFont.truetype(path, size)) > maxw:
        size -= 2
    return ImageFont.truetype(path, size)


def frame_png(spec, shown, cur, cap, path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    L = spec.get('list', {})
    ts = L.get('titleSize', 80)
    for k, (txt, col) in enumerate(spec['title']):
        text(d, (W / 2, L.get('titleY', 300) + k * int(ts * 1.1)), txt, fit(d, txt, spec['font'], ts, 980), col, 'ms', 7)
    f = ImageFont.truetype(spec['font'], L.get('size', 58))
    for k, r in enumerate(sorted(e['rank'] for e in spec['entries'])):
        x, y = L.get('x', 40), L.get('y', 560) + k * L.get('gap', 88)
        text(d, (x, y), f'{r}.', f, 'white', 'ls')
        if r in shown:
            text(d, (x + d.textlength(f'{r}. ', font=f), y), shown[r], f, '#ffd400' if r == cur else 'white', 'ls')
    if cap:
        text(d, (W / 2, L.get('capY', 1180)), cap, fit(d, cap, spec.get('capFont', spec['font']), L.get('capSize', 66), 960),
             'white', 'ms', 7)
    im.save(path)


def build(spec, out):
    tmp = tempfile.mkdtemp(prefix='fails_')
    rv = spec.get('reveal', {"dur": 1.4, "zoom": 1.22, "bright": 0.3})
    parts, states, t, shown = [], [], 0.0, {}
    for e in spec['entries']:
        shown = dict(shown); shown[e['rank']] = e['name']
        for i, s in enumerate(e['shots']):
            png = f'{tmp}/st{len(states)}.png'
            frame_png(spec, shown, e['rank'], s.get('cap'), png)
            states.append((t, png))
            p = f'{tmp}/p{len(parts):02d}.mp4'
            t += shot(s, p, rv if i == 0 else None)
            parts.append(p)
    total = t
    open(f'{tmp}/l.txt', 'w').write(''.join(f"file '{p}'\n" for p in parts))
    base = f'{tmp}/base.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{tmp}/l.txt', '-c', 'copy', base])
    ins, chain, prev = [], '', '0:v'
    for k, (st, png) in enumerate(states):
        end = states[k + 1][0] if k + 1 < len(states) else total + 1
        ins += ['-i', png]
        n = len(ins) // 2
        chain += f"[{prev}][{n}:v]overlay=0:0:enable='between(t,{st:.3f},{end - 0.001:.3f})'[o{n}];"
        prev = f'o{n}'
    fade = spec.get('endfade', 0.8)
    chain += f"[{prev}]fade=t=out:st={total - fade:.3f}:d={fade},format=yuv420p[v];[0:a]afade=t=out:st={total - fade:.3f}:d={fade}[a]"
    run(['ffmpeg', '-v', 'error', '-y', '-i', base, *ins, '-filter_complex', chain, '-map', '[v]', '-map', '[a]',
         '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out])
    print(out, round(total, 1))


if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2])
