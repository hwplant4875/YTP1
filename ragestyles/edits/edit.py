"""Pure "edit" builder: cuts real footage into a 9:16 canvas with a 3:4 (or 4:3) picture window,
title above, short captions below, original audio crossfaded between cuts. No narration.
usage: python3 edit.py spec.json out.mp4 [--preview]

spec.json:
{ "src": {"name": "path.mp4", ...},            # sources
  "srcCrop": {"name": "w:h:x:y"},              # optional per-source crop (e.g. remove pillarbox)
  "title": ["LINE 1", "LINE 2"],               # top bar (line 2 in accent colour)
  "window": {"y": 300, "h": 1440},             # 3:4 window position on the 1080x1920 canvas
  "shots": [ {"src": "name", "in": 12.0, "out": 17.5,
              "fit": "fill" | "wide",          # fill = crop to 3:4 window; wide = full frame (4:3) over blurred fill
              "cx": [0.5, 0.55], "zoom": 1.0,  # fill: horizontal centre (start, end) as fraction of source width
              "tr": "fade", "td": 0.25,        # transition INTO the next shot
              "cap": "TEXT", "capIn": 0.4, "capOut": null,
              "speed": 1.0, "png": [{"file": "x.png", "in": 2, "out": 4.5}] } ] }
"""
import json, subprocess, sys, os

W, H = 1080, 1920
FONT = '/home/user/rs_work/fonts/YOUTUBESANSBLACK.OTF'
ACC = '0xFFD400'


def esc(s):
    return s.replace('\\', '\\\\').replace(':', '\\:').replace("'", "’").replace('%', '\\%')


def shot_filter(spec, s, d, wy, wh):
    sp = s.get('speed', 1.0)
    pre = f"[0:v]setpts=(PTS-STARTPTS)/{sp},fps=30"
    sc = spec.get('srcCrop', {}).get(s['src'])
    if sc:
        pre += f",crop={sc}"
    sf = spec.get('srcFilter', {}).get(s['src'])  # raw filters, e.g. pillarbox crop + delogo + denoise
    if sf:
        pre += f",{sf}"
    fc = []
    if s.get('fit', 'fill') == 'fill':
        z = s.get('zoom', 1.0)
        cx = s.get('cx', .5)
        cx0, cx1 = cx if isinstance(cx, list) else (cx, cx)
        cy = s.get('cy', 0.5)
        # crop a window-aspect region of height ih/z, panning cx0 -> cx1
        x = f"max(0,min(iw-ow,iw*({cx0}+({cx1}-{cx0})*t/{d:.3f})-ow/2))"
        y = f"max(0,min(ih-oh,ih*{cy}-oh/2))"
        fc.append(f"{pre},crop='ih/{z}*{W}/{wh}':'ih/{z}':'{x}':'{y}',scale={W}:{wh}:flags=lanczos,unsharp=5:5:0.6,"
                  f"setsar=1,format=yuv420p[v]")
    else:  # wide: full frame scaled to window width, over a blurred fill of the window
        fc.append(f"{pre},split[sa][sb]")
        fc.append(f"[sa]scale=-2:{wh},crop={W}:{wh},boxblur=30:2,eq=brightness=-0.32:saturation=0.7[bg]")
        wz = s.get('zoom', 1.0)  # >1 trims the sides of a wide frame to make the subject bigger
        fc.append(f"[sb]scale={round(W * wz / 2) * 2}:-2:flags=lanczos,crop={W}:ih,unsharp=5:5:0.6[fg]")
        fc.append(f"[bg][fg]overlay=0:(H-h)/2,setsar=1,format=yuv420p[v]")
    last = 'v'
    for k, p in enumerate(s.get('png', [])):
        fd = p.get('fade', .25)
        fc.append(f"[{k + 1}:v]format=rgba,fade=t=in:st={p['in']}:d={fd}:alpha=1,fade=t=out:st={p['out'] - fd:.3f}:d={fd}:alpha=1[p{k}]")
        fc.append(f"[{last}][p{k}]overlay=0:-{wy}:shortest=1[o{k}]")  # pngs are full-canvas
        last = f'o{k}'
    tempo = f"atempo={sp}" if sp >= .5 else f"atempo=0.5,atempo={sp / .5}"
    fc.append(f"[0:a]asetpts=PTS-STARTPTS,{tempo},aformat=sample_rates=48000:channel_layouts=stereo[a]")
    return fc, last


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-3000:])


def build(spec, out, preview=False):
    from concurrent.futures import ThreadPoolExecutor
    win = spec.get('window', {'y': 300, 'h': 1440})
    wy, wh = win['y'], win['h']
    shots, srcs = spec['shots'], spec['src']
    n = len(shots)
    work = out + '.parts'
    os.makedirs(work, exist_ok=True)
    durs = [(s['out'] - s['in']) / s.get('speed', 1.0) for s in shots]
    enc = ['-c:v', 'libx264', '-preset', 'veryfast' if preview else 'medium', '-crf', '20' if preview else '14', '-pix_fmt', 'yuv420p']

    def part(i):
        s, d = shots[i], durs[i]
        fc, last = shot_filter(spec, s, d, wy, wh)
        ins = ['-ss', f"{s['in']:.3f}", '-t', f"{s['out'] - s['in']:.3f}", '-i', srcs[s['src']]]
        for p in s.get('png', []):
            ins += ['-loop', '1', '-framerate', '30', '-t', f'{d:.3f}', '-i', p['file']]
        f = f'{work}/f{i}.txt'
        open(f, 'w').write(';\n'.join(fc))
        run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex_script', f, '-map', f'[{last}]', '-map', '[a]', '-t', f'{d:.3f}']
            + enc + ['-c:a', 'pcm_s16le', f'{work}/s{i}.mov'])

    with ThreadPoolExecutor(4) as ex:
        list(ex.map(part, range(n)))
    fc, ins = [], []
    for i in range(n):
        ins += ['-i', f'{work}/s{i}.mov']
    starts = [0.0]
    vprev, aprev, acc = '0:v', '0:a', durs[0]
    for i in range(1, n):
        td = shots[i - 1].get('td', 0.25)
        tr = shots[i - 1].get('tr', 'fade')
        off = acc - td
        starts.append(off)
        fc.append(f"[{vprev}][{i}:v]xfade=transition={tr}:duration={td}:offset={off:.3f}[vx{i}]")
        fc.append(f"[{aprev}][{i}:a]acrossfade=d={td}:c1=tri:c2=tri[ax{i}]")
        vprev, aprev = f'vx{i}', f'ax{i}'
        acc = off + durs[i]
    total = acc
    dt = []
    t1, t2 = spec['title']
    dt.append(f"drawtext=fontfile={FONT}:text='{esc(t1)}':fontsize={spec.get('titleSize', 92)}:fontcolor=white:x=(w-tw)/2:y={wy - 205}:"
              f"shadowcolor=black@0.6:shadowx=0:shadowy=4")
    dt.append(f"drawtext=fontfile={FONT}:text='{esc(t2)}':fontsize={spec.get('subSize', 50)}:fontcolor={ACC}:x=(w-tw)/2:y={wy - 95}")
    for i, s in enumerate(shots):
        if not s.get('cap'):
            continue
        a = starts[i] + s.get('capIn', 0.3)
        b = starts[i] + s['capOut'] if s.get('capOut') is not None else starts[i] + durs[i] - s.get('td', .25) * .5
        if i == n - 1:
            b = total - .1
        al = f"if(lt(t,{a:.3f}+0.18),(t-{a:.3f})/0.18,if(gt(t,{b:.3f}-0.18),({b:.3f}-t)/0.18,1))"
        dt.append(f"drawtext=fontfile={FONT}:text='{esc(s['cap'])}':fontsize={s.get('capSize', 66)}:fontcolor={s.get('capColor', 'white')}:"
                  f"x=(w-tw)/2:y={wy + wh + 42}:alpha='{al}':enable='between(t,{a:.3f},{b:.3f})'")
    fc.append(f"[{vprev}]pad={W}:{H}:0:{wy}:black," + ','.join(dt) + f",fade=t=out:st={total - .45:.3f}:d=0.45[vout]")
    fc.append(f"[{aprev}]afade=t=out:st={total - .45:.3f}:d=0.45,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
    open(out + '.filter.txt', 'w').write(';\n'.join(fc))
    run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex_script', out + '.filter.txt', '-map', '[vout]', '-map', '[aout]',
         '-t', f"{total:.3f}", '-c:v', 'libx264', '-preset', 'veryfast' if preview else 'slow', '-crf', '22' if preview else '17',
         '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', out])
    json.dump({'starts': starts, 'durs': durs, 'total': total}, open(out + '.timeline.json', 'w'), indent=1)
    print(f'{out}  {total:.2f}s')


if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2], '--preview' in sys.argv)
