"""Anime / movie motivation edit (CapCut / After Effects look) compiled to plain ffmpeg commands, so the same
edit renders on a machine with only ffmpeg (the owner's laptop, HD sources) and here (360p proxies for QA).
Every path is relative to the channel folder: src/<code>/<id>.mp4, fonts/, work/, shorts/.
Recipe: /mnt/project-files/plans/ragestyles/edit_refs/analysis.md (build on dialogue, drop on a 1-beat grid,
continuous zoom-in per shot, punch + shake + white flash on hits, mono hold and fade at the end).

    python3 animedit_ff.py spec.json            writes jobs/<name>/ (run.sh, run.cmd, graph files) next to the spec
    python3 animedit_ff.py spec.json --run DIR  also runs run.sh inside the channel folder DIR

spec: {"name", "font", "grade": {"warm", "contrast", "sat", "bright", "black", "glow", "sharpen", "grain", "vignette"},
       "shots": [...], "voice": [...], "subs": [...], "fadeout": 0.3}
shot: "src", "in", "out" | "len"                  source seconds; len = output seconds at constant speed
      "speed": 1.0 | [[t, factor], ...]          constant, or a ramp keyed on source time
      "x", "y": 0.5                               crop centre (fraction of the source)
      "zoom": 1.0 | [z0, z1], "ease": "out"|"in"  zoom over the shot; "in" accelerates into the cut
      "ratio": "9:16" | "16:9" | "1:1"            16:9 and 1:1 sit on black inside 9:16
      "punch": 0.0, "shake": 0.0                  zoom kick (+0.10) and px shake at the cut, decaying
      "flash": "white" | "black" | "invert", "smear": px of sideways blur on the first 2 frames
      "impact": [t, ...]                          shot seconds of 2-frame inverted ink frames
      "strobe": [t0, t1]                          bright/dark flicker every 2 frames
      "rgb": 0, "tint": "bw" | "red" | "blue", "freeze": 0.0
voice: {"src", "in", "out", "at", "vol"}          original voice line placed at output second "at"
subs:  {"words": [[word, at], ...], "end", "y", "size", "glow": "#ff2a2a"}   word-by-word line
"""
import json, os, shlex, subprocess, sys
from PIL import ImageFont

W, H, FPS = 1080, 1920, 30
SS = 1.5        # supersample before zoompan so slow zooms do not stair-step
ROOT = os.environ.get('RS_ROOT', '/home/user/rs_work/anime/RS')   # channel folder used to measure text


def pieces_of(s):
    sp = s.get('speed', 1.0)
    if 'len' in s and not isinstance(sp, list):
        s['out'] = s['in'] + s['len'] * sp
    keys = sp if isinstance(sp, list) else [[s['in'], sp]]
    pts = sorted({s['in'], s['out'], *[k for k, _ in keys if s['in'] < k < s['out']]})
    out = []
    for a, b in zip(pts, pts[1:]):
        f = keys[0][1]
        for k, v in keys:
            if a >= k - 1e-9:
                f = v
        out.append((a, b, f))
    return out


def frames_of(s):
    n = int(round(sum((b - a) / f for a, b, f in pieces_of(s)) * FPS))
    return n + int(round(s.get('freeze', 0) * FPS))


def esc_word(t):
    """one word, unquoted: \\\\\\ before each special survives both the filtergraph and the option parser"""
    return ''.join('\\\\\\' + c if c in "\\':,;[]=" else c for c in t.replace('%', ''))


def zexpr(s, dur):
    z = s.get('zoom', 1.0)
    z0, z1 = (z, z) if not isinstance(z, list) else z
    u = f'min(ot/{max(dur, 0.01):.3f},1)'
    e = f'pow({u},2)' if s.get('ease') == 'in' else f'(1-pow(1-{u},3))'
    e = f'{z0}+({z1 - z0:.4f})*{e}'
    if s.get('punch'):
        e += f"+{s['punch']}*pow(max(1-ot/0.2,0),2)"
    return f'max({e},1)'


def shot_cmd(s, spec, i):
    pcs = pieces_of(s)
    n = int(round(sum((b - a) / f for a, b, f in pcs) * FPS))
    dur = n / FPS
    g = []
    if len(pcs) == 1:
        a, b, f = pcs[0]
        g.append(f'[0:v]trim=0:{b - s["in"]:.3f},setpts=(PTS-STARTPTS)/{f},fps={FPS}[sp]')
    else:
        g.append(f'[0:v]split={len(pcs)}' + ''.join(f'[r{k}]' for k in range(len(pcs))))
        for k, (a, b, f) in enumerate(pcs):
            g.append(f'[r{k}]trim={a - s["in"]:.3f}:{b - s["in"]:.3f},setpts=(PTS-STARTPTS)/{f}[q{k}]')
        g.append(''.join(f'[q{k}]' for k in range(len(pcs))) + f'concat=n={len(pcs)}:v=1:a=0,fps={FPS}[sp]')
    cx, cy = s.get('x', 0.5), s.get('y', 0.5)
    amp = s.get('shake', 0) * SS
    shx = f"+{amp}*max(1-ot/0.3,0)*sin(ot*97)" if amp else ''
    shy = f"+{amp}*max(1-ot/0.3,0)*cos(ot*71)" if amp else ''
    ratio = s.get('ratio', '9:16')
    if ratio == '9:16':
        ar = '9/16'
        zs, post = f'{W}x{H}', ''
    else:
        ar = '16/9' if ratio == '16:9' else '1'
        bh = int(W / eval(ar)) // 2 * 2
        zs, post = f'{W}x{bh}', f',pad={W}:{H}:0:(oh-ih)/2:black'
    sw, sh = (W, H) if ratio == '9:16' else (W, int(W / eval(ar)) // 2 * 2)
    pre = (f"crop='trunc(min(iw,ih*{ar})/2)*2':'trunc(min(ih,iw/({ar}))/2)*2':"
           f"'max(min({cx}*iw-ow/2,iw-ow),0)':'max(min({cy}*ih-oh/2,ih-oh),0)',"
           f'scale={int(sw * SS)}:{int(sh * SS)}:flags=lanczos,setsar=1')
    g.append(f"[sp]{pre},zoompan=z='{zexpr(s, dur)}':x='max(min((iw-iw/zoom)/2{shx},iw-iw/zoom),0)':"
             f"y='max(min((ih-ih/zoom)/2{shy},ih-ih/zoom),0)':d=1:s={zs}:fps={FPS}{post},setpts=PTS-STARTPTS,format=gbrp[z]")
    gr = spec.get('grade', {})
    fx = []
    if gr.get('warm'):
        w = gr['warm']
        fx.append(f'colorbalance=rm={w}:bm={-w}:rh={w / 2}:bh={-w / 2}')
    fx.append(f"eq=contrast={gr.get('contrast', 1.15)}:saturation={gr.get('sat', 1.25)}:brightness={gr.get('bright', 0)}")
    if gr.get('black'):
        b = gr['black'] / 255
        fx.append(f'colorlevels=rimin={b:.3f}:gimin={b:.3f}:bimin={b:.3f}')
    tint = s.get('tint')
    if tint == 'bw':
        fx.append('hue=s=0')
    elif tint == 'red':
        fx.append('colorchannelmixer=.5:.6:.2:0:.12:.2:.05:0:.1:.15:.05:0')
    elif tint == 'blue':
        fx.append('colorchannelmixer=.08:.15:.05:0:.2:.35:.1:0:.45:.6:.3:0')
    g.append('[z]' + ','.join(fx) + '[c]')
    last = 'c'
    if gr.get('glow'):
        k = gr['glow'] * 2.2
        lut = f"'max(val-165,0)*{k:.2f}'"
        g.append(f'[c]split[c0][c1];[c1]scale={W // 6}:{H // 6},lutrgb=r={lut}:g={lut}:b={lut},gblur=sigma=5,'
                 f'scale={W}:{H}[gl];[c0][gl]blend=all_mode=screen[gw]')
        last = 'gw'
    post = []
    if gr.get('sharpen'):
        post.append(f"unsharp=5:5:{gr['sharpen']}")
    if gr.get('vignette'):
        post.append(f"vignette=angle={gr['vignette']}")
    if s.get('smear'):
        post.append(f"avgblur=sizeX={int(s['smear'])}:sizeY=1:enable='lt(t,0.067)'")
    if s.get('rgb'):
        p = int(s['rgb'])
        post.append(f"rgbashift=rh={p}:bh={-p}:enable='lt(t,0.1)'")
        post.append(f"rgbashift=rh={p // 2}:bh={-(p // 2)}:enable='between(t,0.1,0.2)'")
    for it in s.get('impact', []):
        en = f"enable='between(t,{it:.3f},{it + 0.066:.3f})'"
        post.append(f"colorchannelmixer=.3:.59:.11:0:.3:.59:.11:0:.3:.59:.11:0:{en}")
        post.append(f"lutrgb=r='if(gt(val,110),0,255)':g='if(gt(val,110),0,255)':b='if(gt(val,110),0,255)':{en}")
    if s.get('strobe'):
        a, b = s['strobe']
        post.append(f"eq=brightness=0.45:enable='between(t,{a},{b})*lt(mod(n,4),2)'")
        post.append(f"eq=brightness=-0.5:enable='between(t,{a},{b})*gte(mod(n,4),2)'")
    fl = s.get('flash')
    if fl in ('white', 'black'):
        post.append(f'fade=t=in:st=0:d=0.1:color={fl}')
    elif fl == 'invert':
        post.append("negate=enable='lt(t,0.067)'")
    if gr.get('grain'):
        post.append(f"noise=alls={int(gr['grain'] * 255)}:allf=t")
    if s.get('freeze'):
        post.append(f"tpad=stop_mode=clone:stop_duration={s['freeze']}")
    post.append('format=yuv420p')
    g.append(f'[{last}]' + ','.join(post) + '[v]')
    out = f"work/{spec['name']}_{i:02d}.mp4"
    args = ['ffmpeg', '-v', 'error', '-y', '-ss', f"{s['in']:.3f}", '-t', f"{s['out'] - s['in'] + 0.2:.3f}", '-i', s['src'],
            '-filter_complex', ';'.join(g), '-map', '[v]', '-an', '-frames:v', str(frames_of(s)), '-r', str(FPS),
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-pix_fmt', 'yuv420p', out]
    return args, out


def sub_filters(spec):
    """glow layer filters and crisp text filters for the word-by-word subtitles (global output time)"""
    font = ImageFont.truetype(os.path.join(ROOT, spec['font']), 10)
    glow, crisp = [], []
    for l in spec.get('subs', []):
        size = l.get('size', 84)
        words = [w for w, _ in l['words']]
        f = font.font_variant(size=size)
        while f.getlength(' '.join(words)) + size * 0.3 > W - 120:          # keep the line inside the frame
            size -= 2
            f = font.font_variant(size=size)
        full = ' '.join(words)
        x0 = (W - f.getlength(full)) / 2
        y = l.get('y', 1000)
        end = l['end']
        for k, (w, at) in enumerate(l['words']):
            x = x0 + f.getlength(' '.join(words[:k]) + (' ' if k else ''))
            pop = f'max(0,1-(t-{at})/0.1)'
            base = (f"fontfile={spec['font']}:expansion=none:text={esc_word(w)}:fontsize={size}:"
                    f"x={x:.0f}:y='{y:.0f}-ascent/2-{pop}*12':enable='between(t,{at},{end})'")
            gc = l.get('glow', '#ff2a2a').replace('#', '0x')
            glow.append(f"drawtext={base}:fontcolor={gc}:borderw={size // 6}:bordercolor={gc}:alpha='min(1,(t-{at})/0.1)'")
            crisp.append(f"drawtext={base}:fontcolor=white:borderw={max(3, size // 18)}:bordercolor=black:"
                         f"alpha='min(1,(t-{at})/0.1)'")
    return glow, crisp


def final_cmd(spec, outs, total):
    args = ['ffmpeg', '-v', 'error', '-y']
    for o in outs:
        args += ['-i', o]
    voices = spec.get('voice', [])
    for v in voices:
        args += ['-ss', f"{v['in']:.3f}", '-t', f"{v['out'] - v['in']:.3f}", '-i', v['src']]
    nv = len(outs)
    g = [''.join(f'[{k}:v]' for k in range(nv)) + f'concat=n={nv}:v=1:a=0[cat]']
    glow, crisp = sub_filters(spec)
    last = 'cat'
    if glow:
        g.append(f'color=c=black@0:s={W}x{H}:r={FPS}:d={total:.3f},format=rgba,' + ','.join(glow) +
                 ',gblur=sigma=10[gl0]')
        g.append('[cat][gl0]overlay=0:0:format=auto,' + ','.join(crisp) + '[tx]')
        last = 'tx'
    fo = spec.get('fadeout', 0.3)
    g.append(f'[{last}]fade=t=out:st={total - fo:.3f}:d={fo},format=yuv420p[v]')
    if voices:
        for j, v in enumerate(voices):
            d = int(v['at'] * 1000)
            g.append(f"[{nv + j}:a]asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
                     f"volume={v.get('vol', 1.0)},afade=t=in:d=0.03,afade=t=out:st={v['out'] - v['in'] - 0.08:.3f}:d=0.08,"
                     f"adelay={d}|{d}[va{j}]")
        g.append(''.join(f'[va{j}]' for j in range(len(voices))) +
                 f'amix=inputs={len(voices)}:normalize=0:duration=longest,apad,atrim=0:{total:.3f}[a]')
    else:
        args += ['-f', 'lavfi', '-t', f'{total:.3f}', '-i', 'anullsrc=r=48000:cl=stereo']
        g.append(f'[{nv}:a]anull[a]')
    args += ['-filter_complex', ';'.join(g), '-map', '[v]', '-map', '[a]', '-t', f'{total:.3f}', '-r', str(FPS),
             '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
             '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', f"shorts/{spec['name']}.mp4"]
    return args


def compile_spec(spec):
    cmds, outs, t, starts = [], [], 0, []
    spec['shots'][0].pop('flash', None)     # frame 0 is the IG/TikTok cover: always the full picture
    for i, s in enumerate(spec['shots']):
        a, o = shot_cmd(s, spec, i)
        cmds.append(a); outs.append(o); starts.append(t)
        t += frames_of(s) / FPS
    cmds.append(final_cmd(spec, outs, t))
    return cmds, starts, t


def cmd_quote(a):
    if a and not any(c in a for c in ' ;,[]=\'():&|<>^#@'):
        return a
    return '"' + a + '"'


def write(spec, jobs):
    """jobs/<name>/ gets run.sh, run.cmd and one filtergraph file per command (cmd.exe caps a line at 8191 chars);
    copy that folder to <channel>/jobs/<name>/ and run it from <channel>"""
    cmds, starts, total = compile_spec(spec)
    d = os.path.join(jobs, spec['name'])
    os.makedirs(d, exist_ok=True)
    sh, bat = ['set -e', 'mkdir -p work shorts'], ['@echo off', 'if not exist work mkdir work', 'if not exist shorts mkdir shorts']
    for k, c in enumerate(cmds):
        j = c.index('-filter_complex')
        gname = f'g{k:02d}.txt'
        open(os.path.join(d, gname), 'w', newline='\n').write(c[j + 1])
        rel = f"jobs/{spec['name']}/{gname}"
        sh.append(' '.join(shlex.quote(a) for a in c[:j] + ['-filter_complex_script', rel] + c[j + 2:]))
        bat.append(' '.join(cmd_quote(a) for a in c[:j] + ['-/filter_complex', rel] + c[j + 2:]) + ' || exit /b 1')
    open(os.path.join(d, 'run.sh'), 'w').write('\n'.join(sh) + '\n')
    open(os.path.join(d, 'run.cmd'), 'w', newline='').write('\r\n'.join(bat) + '\r\n')
    return os.path.join(d, 'run.sh'), starts, total


if __name__ == '__main__':
    spec = json.load(open(sys.argv[1]))
    jobs = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), 'jobs')
    sh, starts, total = write(spec, jobs)
    print(sh, f'total {total:.2f}s')
    print(' '.join(f'{i}:{t:.2f}' for i, t in enumerate(starts)))
    if '--run' in sys.argv:
        subprocess.run(['bash', sh], cwd=sys.argv[sys.argv.index('--run') + 1], check=True)
