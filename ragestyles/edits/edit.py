"""Pure "edit" builder: cuts real footage onto a 9:16 solid-colour canvas. The picture sits in a window
(default 1:1), a title PNG (text + emoji, see title_png.py) sits above it, optional short captions below.
Original audio is crossfaded between cuts; no narration.
usage: python3 edit.py spec.json out.mp4 [--preview]

spec.json:
{ "src": {"name": "path.mp4"},
  "srcFilter": {"name": "crop=...,hqdn3d=..."},   # raw filters applied to that source first
  "bg": "black", "font": "/path/font.ttf",
  "titlePng": "title.png", "titleY": 250,         # title strip position (keep clear of the Dynamic Island)
  "window": {"y": 520, "h": 1080},                # picture window (full width)
  "sfx": {"hit": {"file": "x.wav", "filter": "lowpass=180", "gain": -14}},
  "shots": [ {"src": "name", "in": 12.0, "out": 17.5,
              "fit": "fill" | "wide",             # fill = crop to the window aspect; wide = whole frame, letterboxed on bg
              "cx": [0.5, 0.55], "cy": 0.5, "zoom": 1.0,
              "punch": true,                      # zoom-in + brightness pop over the first 0.5 s (+ "hit" sfx)
              "tr": "fade", "td": 0.25,           # transition INTO the next shot (window only)
              "cap": "TEXT", "capIn": 0.3, "capOut": null, "capColor": "white" } ] }
"""
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor

W, H = 1080, 1920
ACC = '0xFFD400'


def esc(s):
    return s.replace('\\', '\\\\').replace(':', '\\:').replace("'", "’").replace('%', '\\%')


def shot_filter(spec, s, d, wh):
    sp = s.get('speed', 1.0)
    bg = spec.get('bg', 'black')
    pre = f"[0:v]setpts=(PTS-STARTPTS)/{sp},fps=30"
    sf = spec.get('srcFilter', {}).get(s['src'])
    if sf:
        pre += f",{sf}"
    fc = []
    if s.get('fit', 'fill') == 'fill':
        z = s.get('zoom', 1.0)
        cx = s.get('cx', .5)
        cx0, cx1 = cx if isinstance(cx, list) else (cx, cx)
        cy = s.get('cy', 0.5)
        x = f"max(0,min(iw-ow,iw*({cx0}+({cx1}-{cx0})*t/{d:.3f})-ow/2))"
        y = f"max(0,min(ih-oh,ih*{cy}-oh/2))"
        fc.append(f"{pre},crop='min(iw,ih/{z}*{W}/{wh})':'min(ih,ih/{z})':'{x}':'{y}',scale={W}:{wh}:flags=lanczos,unsharp=5:5:0.6,"
                  f"setsar=1,format=yuv420p[v0]")
    else:  # wide: whole frame at window width, letterboxed on the solid background
        wz = s.get('zoom', 1.0)
        fc.append(f"{pre},scale={round(W * wz / 2) * 2}:-2:flags=lanczos,crop={W}:'min(ih,{wh})',unsharp=5:5:0.6,"
                  f"pad={W}:{wh}:0:(oh-ih)/2:{bg},setsar=1,format=yuv420p[v0]")
    if s.get('punch'):
        # zoom in 1.0 -> 1.12 (ease-out) and a brightness pop that settles, over the first 0.5 s
        n = 15
        fc.append(f"[v0]scale={W * 2}:{wh * 2}:flags=lanczos,zoompan=z='if(lt(on,{n}),1+0.12*(1-pow(1-on/{n},3)),1.12)':"
                  f"x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{wh}:fps=30,"
                  f"eq=brightness='0.22*max(0,1-t/0.5)':contrast='1+0.1*max(0,1-t/0.5)':eval=frame,format=yuv420p[v]")
    else:
        fc.append("[v0]null[v]")
    tempo = f"atempo={sp}" if sp >= .5 else f"atempo=0.5,atempo={sp / .5}"
    fc.append(f"[0:a]asetpts=PTS-STARTPTS,{tempo},aformat=sample_rates=48000:channel_layouts=stereo[a]")
    return fc


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-3000:])


def build(spec, out, preview=False):
    win = spec.get('window', {'y': 520, 'h': 1080})
    wy, wh = win['y'], win['h']
    bg = spec.get('bg', 'black')
    font = spec.get('font', '/home/user/rs_work/fonts/TikTokSans-Black.ttf')
    shots, srcs = spec['shots'], spec['src']
    n = len(shots)
    work = out + '.parts'
    os.makedirs(work, exist_ok=True)
    durs = [(s['out'] - s['in']) / s.get('speed', 1.0) for s in shots]
    enc = ['-c:v', 'libx264', '-preset', 'veryfast' if preview else 'medium', '-crf', '20' if preview else '14', '-pix_fmt', 'yuv420p']

    def part(i):
        s, d = shots[i], durs[i]
        f = f'{work}/f{i}.txt'
        open(f, 'w').write(';\n'.join(shot_filter(spec, s, d, wh)))
        run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{s['in']:.3f}", '-t', f"{s['out'] - s['in']:.3f}", '-i', srcs[s['src']],
             '-filter_complex_script', f, '-map', '[v]', '-map', '[a]', '-t', f'{d:.3f}'] + enc + ['-c:a', 'pcm_s16le', f'{work}/s{i}.mov'])

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
    k = n
    vlast = 'cv'
    fc.append(f"[{vprev}]pad={W}:{H}:0:{wy}:{bg}[cv]")
    if spec.get('titlePng'):
        ins += ['-loop', '1', '-framerate', '30', '-t', f'{total:.3f}', '-i', spec['titlePng']]
        fc.append(f"[cv][{k}:v]overlay=0:{spec.get('titleY', 250)}:shortest=1[ct]")
        vlast = 'ct'
        k += 1
    dt = []
    for i, s in enumerate(shots):
        if not s.get('cap'):
            continue
        a = starts[i] + s.get('capIn', 0.3)
        b = starts[i] + s['capOut'] if s.get('capOut') is not None else starts[i] + durs[i] - s.get('td', .25) * .5
        b = min(b, total - .1)
        al = f"if(lt(t,{a:.3f}+0.15),(t-{a:.3f})/0.15,if(gt(t,{b:.3f}-0.15),({b:.3f}-t)/0.15,1))"
        dt.append(f"drawtext=fontfile={font}:text='{esc(s['cap'])}':fontsize={s.get('capSize', 64)}:fontcolor={s.get('capColor', 'white')}:"
                  f"x=(w-tw)/2:y={wy + wh + 40}:alpha='{al}':enable='between(t,{a:.3f},{b:.3f})'")
    chain = (','.join(dt) + ',') if dt else ''
    fc.append(f"[{vlast}]{chain}fade=t=out:st={total - .45:.3f}:d=0.45,format=yuv420p[vout]")
    # sfx: a hit under every punch-in shot
    amix = [f'[{aprev}]']
    hit = spec.get('sfx', {}).get('hit')
    if hit:
        for i, s in enumerate(shots):
            if s.get('punch'):
                ins += ['-i', hit['file']]
                ms = int(starts[i] * 1000)
                fc.append(f"[{k}:a]{hit.get('filter', 'anull')},volume={hit.get('gain', -14)}dB,aresample=48000,"
                          f"aformat=channel_layouts=stereo,adelay={ms}|{ms}[h{k}]")
                amix.append(f'[h{k}]')
                k += 1
    mixed = f"{''.join(amix)}amix=inputs={len(amix)}:normalize=0:duration=first," if len(amix) > 1 else amix[0]
    fc.append(f"{mixed}afade=t=out:st={total - .45:.3f}:d=0.45,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
    open(out + '.filter.txt', 'w').write(';\n'.join(fc))
    run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex_script', out + '.filter.txt', '-map', '[vout]', '-map', '[aout]',
         '-t', f"{total:.3f}", '-c:v', 'libx264', '-preset', 'veryfast' if preview else 'slow', '-crf', '22' if preview else '17',
         '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', out])
    json.dump({'starts': starts, 'durs': durs, 'total': total}, open(out + '.timeline.json', 'w'), indent=1)
    print(f'{out}  {total:.2f}s')


if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2], '--preview' in sys.argv)
