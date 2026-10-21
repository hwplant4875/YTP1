"""9:16 shorts ranking edit: 1:1 footage square on a black 9:16 canvas, ranked list on the left, fixed name reveal
(eased zoom-in with a ~30% brightness bump that eases back to normal as the zoom lands).

    python3 rank.py spec.json out.mp4

spec:
  "title": [["MOST WORLD'S STRONGEST", "#fff"], ["MAN TITLES", "#ffd400"]]   lines above the footage (optional)
  "font":  path to the TTF used for title and list
  "athletes": [{"rank": 5, "name": "MAGNUSSON",
                "shots": [{"src", "in", "out", "cx"}]}]   first shot carries the reveal
  "reveal": {"dur": 1.4, "zoom": 1.22, "bright": 0.3}
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

S, FPS = 1080, 30
W, H, TOP = 1080, 1920, 420   # square footage sits at y TOP..TOP+S


def run(cmd):
    subprocess.run(cmd, check=True)


def shot(s, out, reveal=None):
    dur = s['out'] - s['in']
    cx, cy = s.get('cx', 0.5), s.get('cy', 0.5)
    vf = [f"fps={FPS}"]
    if reveal:
        T, z1, b = reveal['dur'], reveal['zoom'], reveal['bright']
        p = f"min(t/{T},1)"
        z = f"(1+({z1}-1)*(1-cos(PI*{p}))/2)"           # ease in-out, then hold
        bump = f"({b}*sin(PI*{p}))"                      # up and back to 0 exactly when the zoom lands
        vf += [f"crop=w='ih/{z}':h='ih/{z}':x='(iw-ih/{z})*{cx}':y='(ih-ih/{z})*{cy}':exact=1",
               f"scale={S}:{S}:flags=lanczos",
               f"eq=eval=frame:brightness='0.35*{bump}':gamma='1+{bump}'"]
    else:
        vf += [f"crop=ih:ih:(iw-ih)*{cx}:0", f"scale={S}:{S}:flags=lanczos"]
    vf += ["unsharp=5:5:0.6,eq=contrast=1.05:saturation=1.08:brightness=0.01", f"pad={W}:{H}:0:{TOP}:black", "setsar=1", "format=yuv420p"]
    af = f"aresample=48000,afade=t=in:d=0.06,afade=t=out:st={dur - 0.1:.3f}:d=0.1"
    run(['ffmpeg', '-v', 'error', '-y', '-ss', str(s['in']), '-t', f'{dur:.3f}', '-i', s['src'],
         '-vf', ','.join(vf), '-af', af, '-c:v', 'libx264', '-preset', 'medium', '-crf', '16',
         '-c:a', 'aac', '-b:a', '192k', '-ac', '2', out])
    return dur


def list_png(spec, shown, cur, path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    L = spec.get('list', {})
    f = ImageFont.truetype(spec['font'], L.get('size', 56))
    if spec.get('title'):
        ts = L.get('titleSize', 84)
        tf = ImageFont.truetype(spec['font'], ts)
        lines = spec['title'][::-1]
        for k, (txt, col) in enumerate(lines):  # bottom line sits just above the footage
            d.text((W / 2, TOP - 40 - k * int(ts * 1.1)), txt, font=tf, fill=col, stroke_width=6, stroke_fill='black', anchor='ms')
    ranks = sorted((a['rank'] for a in spec['athletes']))
    for k, r in enumerate(ranks):
        y = TOP + L.get('y', 120) + k * L.get('gap', 86)
        x = L.get('x', 36)
        d.text((x, y), f'{r}.', font=f, fill='white', stroke_width=5, stroke_fill='black', anchor='ls')
        if r in shown:
            nx = x + d.textlength(f'{r}. ', font=f)
            d.text((nx, y), shown[r], font=f, fill='#ffd400' if r == cur else 'white',
                   stroke_width=5, stroke_fill='black', anchor='ls')
    im.save(path)


def build(spec, out):
    tmp = tempfile.mkdtemp(prefix='rank_')
    rv = spec.get('reveal', {"dur": 1.4, "zoom": 1.22, "bright": 0.3})
    parts, states, t, shown = [], [], 0.0, {}
    list_png(spec, {}, None, f'{tmp}/st0.png'); states.append((0.0, f'{tmp}/st0.png'))
    for a in spec['athletes']:
        shown = dict(shown); shown[a['rank']] = a['name']
        png = f'{tmp}/st{len(states)}.png'
        list_png(spec, shown, a['rank'], png)
        states.append((t, png))
        for i, s in enumerate(a['shots']):
            p = f'{tmp}/p{len(parts):02d}.mp4'
            t += shot(s, p, rv if i == 0 else None)
            parts.append(p)
    total = t
    open(f'{tmp}/l.txt', 'w').write(''.join(f"file '{p}'\n" for p in parts))
    base = f'{tmp}/base.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{tmp}/l.txt', '-c', 'copy', base])
    # the list state changes exactly when each athlete's first shot starts
    ins, chain, prev = [], '', '0:v'
    for k, (st, png) in enumerate(states):
        end = states[k + 1][0] if k + 1 < len(states) else total + 1
        if end <= st:
            continue
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
