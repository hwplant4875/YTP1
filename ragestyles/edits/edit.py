"""Pure "edit" builder for RageStyles shorts.
Layout (benchmarked on top-performing story shorts): 9:16 solid canvas, a white title box whose text changes
per story beat, the picture directly under it, nothing else. Original audio crossfaded between cuts.
Camera moves and punch-in hits are rendered per frame in fxcam.py.
usage: python3 edit.py spec.json out.mp4 [--preview]

spec.json:
{ "src": {"name": "path.mp4"},
  "srcFilter": {"name": "crop=..."},                # ffmpeg filters applied to that source first
  "bg": "black", "font": "TikTokSans-Black.ttf",
  "box": {"y": 266, "h": 211, "color": "#ffffff", "text": "#000000", "size": 58},
  "titles": [{"from": 0, "text": "*...* 😳"}, ...],  # box text, switching at the start of shot `from`
  "window": {"y": 477, "h": 974},
  "sfx": {"boom": {"file": "x.wav", "peak": 0.026, "gain": -3, "filter": "..."}, "ding": {...}},
  "shots": [ {"src": "name", "in": 12.0, "out": 17.5, "fit": "fill" | "wide",
              "cx": 0.5 | [a, b], "cy": 0.5, "zoom": 1.0, "kb": 0.06,
              "hits": [{"t": 1.2, "zoom": 1.08, "amount": 0.5, "strong": false, "boom": -3}],
              "overlays": [{"png": "arrow.png", "in": 2.6, "out": 4.6, "sfx": "ding"}],
              "tr": "fade", "td": 0.2,
              "cap": "TEXT" } ] }
"""
import json, subprocess, sys, os, hashlib
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fxcam, title_png

W, H = 1080, 1920


def esc(s):
    return s.replace('\\', '\\\\').replace(':', '\\:').replace("'", "’").replace('%', '\\%')


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-3000:])


def build(spec, out, preview=False):
    win = spec.get('window', {'y': 477, 'h': 974})
    wy, wh = win['y'], win['h']
    bg = spec.get('bg', 'black')
    font = spec.get('font', '/home/user/rs_work/fonts/TikTokSans-Black.ttf')
    shots, srcs = spec['shots'], spec['src']
    n = len(shots)
    work = out + '.parts'
    os.makedirs(work, exist_ok=True)
    durs = [s['out'] - s['in'] for s in shots]

    def part(i):
        s, d = shots[i], durs[i]
        sf = spec.get('srcFilter', {}).get(s['src'], '')
        fxcam.render_shot(srcs[s['src']], s['in'], d, sf, s, W, wh, f'{work}/v{i}.mp4',
                          crf=20 if preview else 14, preset='veryfast' if preview else 'medium')
        if spec.get('mute'):  # the user lays music over it; source audio (voices, arena music) is dropped
            run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', f'{d:.3f}',
                 '-c:a', 'pcm_s16le', f'{work}/a{i}.wav'])
        else:
            run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{s['in']:.3f}", '-t', f'{d:.3f}', '-i', srcs[s['src']], '-vn',
                 '-af', 'aresample=48000,aformat=channel_layouts=stereo,apad', '-t', f'{d:.3f}', '-c:a', 'pcm_s16le', f'{work}/a{i}.wav'])

    with ThreadPoolExecutor(4) as ex:
        list(ex.map(part, range(n)))

    fc, ins = [], []
    for i in range(n):
        ins += ['-i', f'{work}/v{i}.mp4', '-i', f'{work}/a{i}.wav']
    starts = [0.0]
    vprev, aprev, acc = '0:v', '1:a', durs[0]
    for i in range(1, n):
        td = shots[i - 1].get('td', 0.2)
        tr = shots[i - 1].get('tr', 'fade')
        off = acc - td
        starts.append(off)
        if tr == 'cut':  # hard cut (the zoom-through move is rendered into the shots)
            td, off = 0, acc
            starts[-1] = off
            fc.append(f"[{vprev}][{2 * i}:v]concat=n=2:v=1:a=0[vx{i}]")
            fc.append(f"[{aprev}][{2 * i + 1}:a]concat=n=2:v=0:a=1[ax{i}]")
        else:
            fc.append(f"[{vprev}][{2 * i}:v]xfade=transition={tr}:duration={td}:offset={off:.3f}[vx{i}]")
            fc.append(f"[{aprev}][{2 * i + 1}:a]acrossfade=d={td}:c1=tri:c2=tri[ax{i}]")
        vprev, aprev = f'vx{i}', f'ax{i}'
        acc = off + durs[i]
    total = acc
    k = 2 * n
    fc.append(f"[{vprev}]pad={W}:{H}:0:{wy}:{bg}[c0]")
    cur = 'c0'
    # title box per story beat
    box = spec.get('box', {})
    titles = spec.get('titles', [])
    for j, ti in enumerate(titles):
        a = starts[ti['from']]
        b = starts[titles[j + 1]['from']] if j + 1 < len(titles) else total + 1
        png = f"{work}/title{j}.png"
        title_png.main(png, ti['text'], font, box.get('size', 58), box.get('text', '#000000'),
                       f"{box.get('color', '#ffffff')}:{box.get('h', 211)}")
        ins += ['-loop', '1', '-framerate', '30', '-t', f'{total:.3f}', '-i', png]
        fc.append(f"[{cur}][{k}:v]overlay=0:{box.get('y', 266)}:enable='between(t,{a:.3f},{b - 0.001:.3f})'[c{k}]")
        cur, k = f'c{k}', k + 1
    # overlays (arrows / circles) in canvas coordinates, popping in with a quick scale-free fade
    sfx_events = []
    for i, s in enumerate(shots):
        for o in s.get('overlays', []):
            a, b = starts[i] + o['in'], starts[i] + o['out']
            ins += ['-loop', '1', '-framerate', '30', '-t', f'{total:.3f}', '-i', o['png']]
            fc.append(f"[{k}:v]format=rgba,fade=t=in:st={a:.3f}:d=0.08:alpha=1,fade=t=out:st={b - 0.15:.3f}:d=0.15:alpha=1[o{k}]")
            fc.append(f"[{cur}][o{k}]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[c{k}]")
            cur, k = f'c{k}', k + 1
            if o.get('sfx'):
                sfx_events.append((o['sfx'], a, o.get('gain')))
        for h in s.get('hits', []):
            if h.get('boom', 0) is not None and not (spec.get('mute') and 'boom' not in h):
                sfx_events.append(('boom', starts[i] + h['t'], h.get('boom')))
    for i, s in enumerate(shots):
        caps = s.get('caps', [])  # [{"parts": [[text, colour], ...], "in": s, "out": s}] relative to shot start
        if s.get('capParts'):
            caps = [{'parts': s['capParts'], 'in': s.get('capIn', 0), 'out': s.get('capOut', durs[i])}] + caps
        for j, cp in enumerate(caps):
            a = starts[i] + cp.get('in', 0)
            b = min(starts[i] + cp.get('out', durs[i]), total - .1)
            png = f"{work}/cap{i}_{j}.png"
            title_png.caption(png, cp['parts'], spec.get('capFont', font), s.get('capSize', 100))
            ins += ['-loop', '1', '-framerate', '30', '-t', f'{total:.3f}', '-i', png]
            fc.append(f"[{cur}][{k}:v]overlay=0:{wy + wh + s.get('capGap', 30)}:enable='between(t,{a:.3f},{b - 0.001:.3f})'[c{k}]")
            cur, k = f'c{k}', k + 1
    dt = []
    for i, s in enumerate(shots):
        if s.get('cap'):
            a = starts[i] + s.get('capIn', 0.3)
            b = min(starts[i] + s.get('capOut', durs[i]), total - .1)
            dt.append(f"drawtext=fontfile={font}:text='{esc(s['cap'])}':fontsize={s.get('capSize', 64)}:fontcolor=white:x=(w-tw)/2:y={wy + wh + 44}:"
                      f"enable='between(t,{a:.3f},{b:.3f})'")
    chain = (','.join(dt) + ',') if dt else ''
    fc.append(f"[{cur}]{chain}fade=t=out:st={total - .4:.3f}:d=0.4,format=yuv420p[vout]")
    # sfx mix: align each sound's transient (peak) to its event time
    amix = [f'[{aprev}]']
    for name, t, gain in sfx_events:
        sx = spec['sfx'][name]
        ins += ['-i', sx['file']]
        ms = max(0, int((t - sx.get('peak', 0)) * 1000))
        g = sx.get('gain', -6) if gain is None else gain
        fc.append(f"[{k}:a]{sx.get('filter', 'anull')},volume={g}dB,aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[s{k}]")
        amix.append(f'[s{k}]')
        k += 1
    mixed = f"{''.join(amix)}amix=inputs={len(amix)}:normalize=0:duration=first," if len(amix) > 1 else amix[0]
    norm = 'anull' if spec.get('mute') else 'loudnorm=I=-14:TP=-1.5:LRA=11'
    fc.append(f"{mixed}afade=t=out:st={total - .4:.3f}:d=0.4,{norm},aresample=48000[aout]")
    open(out + '.filter.txt', 'w').write(';\n'.join(fc))
    run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex_script', out + '.filter.txt', '-map', '[vout]', '-map', '[aout]',
         '-t', f"{total:.3f}", '-c:v', 'libx264', '-preset', 'veryfast' if preview else 'slow', '-crf', '22' if preview else '17',
         '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', out])
    json.dump({'starts': starts, 'durs': durs, 'total': total}, open(out + '.timeline.json', 'w'), indent=1)
    print(f'{out}  {total:.2f}s')


if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2], '--preview' in sys.argv)
