# EP08 Conjuring Universe renderer (11/9 KST) = ../ep_backrooms/render_br.py (frame-exact per-section render, voice takes cut into
# pieces around voiceless inserts, per-shot clip audio a=<dB> / lufs=<target>, music ducked under the film lines, SFX bus, quiet Mixkit
# bed) with the ranked-list overlays of ../ep04/render_fk.py:
#   word   cold-open caption, centre (gfx.word_tag look, shrunk to 1760 px or split over two lines)
#   rank   rank card (#N, the entry's demon, the film)            film   film label, top right
#   stats  animated stat card (anim.stat_card, frame sequence)   sub    film-line subtitle, bottom centre (../ep_backrooms/gfx_br.py)
#   png    a ready-made 1920x1080 RGBA overlay (subscribe)
# Tiles: tiles/<key>.png is looked up next to the EDL first (the repo's own graphics), then in <clips>/../tiles (film-frame tiles made on
# the laptop, never committed). Bottom bar only where E['bar'] = {clip: source row} names a clip with a mark at the bottom, and only
# while the shot's zoom still shows it.
# usage: python render_cj.py <edl.json> <clips_dir> <voice_dir> <music.mp3> <out.mp4> [fps]
# env: LEAN=1 deletes shot files once a section is built; ONLY=s05,s09 renders just those sections; REUSE=s00,s03 keeps those sections
#      from the last full render; MUSIC_LUFS (default -39)
import json, os, sys, subprocess, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ep01')); sys.path.insert(0, os.path.join(HERE, '..', 'ep03')); sys.path.insert(0, os.path.join(HERE, '..', 'ep_backrooms'))
from gfx import rank_card, film_label, f as gf, shadow_text, WHITE as GWHITE
import anim
import gfx_br as gx
edl, CLIPS, VOICE, MUSIC, OUT = sys.argv[1:6]
FPS = int(sys.argv[6]) if len(sys.argv) > 6 else 30
EDIR = os.path.dirname(os.path.abspath(edl))
WORK = os.path.join(os.path.dirname(os.path.abspath(OUT)), 'work_' + os.path.splitext(os.path.basename(OUT))[0])
os.makedirs(WORK, exist_ok=True)
ONLY = set(filter(None, os.environ.get('ONLY', '').split(',')))
REUSE = set(filter(None, os.environ.get('REUSE', '').split(',')))
def run(cmd):
    if os.environ.get('DEBUG'): print('RUN', subprocess.list2cmdline(cmd), flush=True)
    subprocess.run(cmd, check=True)
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
def rel(p): return p if os.path.isabs(p) else os.path.join(EDIR, p)
def tile(p):
    for q in (rel(p), os.path.join(CLIPS, '..', 'tiles', os.path.basename(p))):
        if os.path.exists(q): return q
    raise FileNotFoundError(p)
def src(name):
    for ext in ('_hd.mp4', '.mp4', '.webm', '.mkv'):
        p = os.path.join(CLIPS, name + ext)
        if os.path.exists(p): return p
    raise FileNotFoundError(name)
def lufs_span(p, a, d):
    o = subprocess.run(['ffmpeg', '-v', 'info', '-nostats', '-ss', str(a), '-t', str(max(d, 0.5)), '-i', p, '-vn', '-af', 'ebur128', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    v = re.findall(r'I:\s+(-?[\d.]+) LUFS', o)
    return float(v[-1]) if v else -70.0
E = json.load(open(edl))
if E.get('tiers'): anim.set_tiers(E['tiers'])
Z = E.get('zoom', {}); GM = E.get('gamma', {}); BAR = E.get('bar', {})
SPF = 48000 // FPS
_HA = {}
def has_audio(p):
    if p not in _HA:
        _HA[p] = bool(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', p],
                                     capture_output=True, text=True).stdout.strip())
    return _HA[p]
def wav(o, n, a_in=None, db=-99, tempo=1.0):
    ns = n * SPF
    if a_in is None or db <= -90 or not has_audio(a_in[0]):   # silence (also for sources without sound, e.g. the poster wall)
        run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-af', f'atrim=end_sample={ns}', '-c:a', 'pcm_s16le', o])
    else:
        a, tin = a_in; tf = f'atempo={tempo},' if abs(tempo - 1) > 1e-3 else ''
        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(tin), '-i', a, '-vn', '-af', f'aresample=48000,{tf}volume={db:.2f}dB,afade=t=in:d=0.02,apad,atrim=end_sample={ns}',
             '-ac', '2', '-c:a', 'pcm_s16le', o])
def fit_word(word, out):
    """EP04 cold-open caption: centre, f(170), stroke 5, shrunk to fit 1760 px, or two lines when it still would not fit"""
    from PIL import Image
    im = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); w = word.upper(); sz = 170
    while gf(sz).getlength(w) > 1760 and sz > 120: sz -= 5
    if gf(sz).getlength(w) <= 1760: shadow_text(im, (960, 540), w, gf(sz), GWHITE, stroke=5)
    else:
        ws = w.split(); k = min(range(1, len(ws)), key=lambda i: abs(len(' '.join(ws[:i])) - len(' '.join(ws[i:]))))
        shadow_text(im, (960, 455), ' '.join(ws[:k]), gf(170), GWHITE, stroke=5); shadow_text(im, (960, 635), ' '.join(ws[k:]), gf(170), GWHITE, stroke=5)
    im.save(out)
def overlay_png(kind, arg, path):
    if kind == 'word': fit_word(arg, path)
    elif kind == 'rank': rank_card(*arg, path)
    elif kind == 'film': film_label(arg, path)
    elif kind == 'sub': gx.sub(arg, path)
    elif kind == 'png': return rel(arg)
    else: raise ValueError(kind)
    return path
FADE = {'word': (0, 0), 'film': (0, 0), 'sub': (0.08, 0.08), 'rank': (0.12, 0.12), 'png': (0.15, 0.15)}
def stat_frames(arg, d_ov, si, j):
    """the animated stat card as a PNG sequence in WORK/anNN_NN (cached by its arguments); returns (dir, x, y)"""
    out = os.path.join(WORK, f'an{si:02d}_{j:02d}'); key = json.dumps([arg, round(d_ov, 3), E.get('tiers'), FPS], sort_keys=True)
    kp = os.path.join(out, 'key.json')
    if os.path.exists(kp) and open(kp).read() == key:
        n, x, y = json.load(open(os.path.join(out, 'xy.json'))); return out, x, y
    os.makedirs(out, exist_ok=True)
    for p in os.listdir(out): os.remove(os.path.join(out, p))
    a = dict(arg); a['tile_png'] = tile(a['tile_png']); a['dur'] = min(a['dur'], d_ov)
    n, x, y = anim.stat_card(out, fps=FPS, **a)
    json.dump([n, x, y], open(os.path.join(out, 'xy.json'), 'w')); open(kp, 'w').write(key)
    return out, x, y
def vfade(S, L):
    v = S.get('vfade', {}); o = ''
    if v.get('in'): o += f"fade=t=in:st=0:d={v['in']},"
    if v.get('out'): o += f"fade=t=out:st={L - v['out']:.3f}:d={v['out']},"
    return o
parts, audios, voice_items, sfx_items, ducks = [], [], [], [], []
t_global = 0.0
for si, S in enumerate(E['sections']):
    v = S['voice']; vp = os.path.join(VOICE, v + '.mp3'); L = S['len']
    F0 = round(t_global * FPS); NF = round((t_global + L) * FPS) - F0
    if ONLY and v not in ONLY:
        t_global += L; continue
    t0 = sum(dur(p) for p in parts) if ONLY else F0 / FPS
    _sec, _sa, _sv = (os.path.join(WORK, f'sec{si:02d}{x}') for x in ('.mp4', '.wav', '_voice.wav'))
    reuse = v in REUSE and not ONLY and all(os.path.exists(p) for p in (_sec, _sa, _sv))
    if not reuse:
        # ---- picture + clip audio, shot by shot ----
        shots = S['shots']; segs = []; asegs = []
        for k, (t, name, tin, sp, *rest) in enumerate(shots):
            op = rest[0] if rest else {}
            f0 = round(t * FPS); f1 = round(shots[k + 1][0] * FPS) if k + 1 < len(shots) else NF; n = f1 - f0
            if n <= 0: continue
            if op.get('ins'): sp = 1.0
            o = os.path.join(WORK, f's{si:02d}_{k:02d}.mp4'); ao = os.path.join(WORK, f's{si:02d}_{k:02d}.wav')
            if name == 'BLACK':
                run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=c=black:s=1920x1080:r={FPS}', '-frames:v', str(n), '-c:v', 'libx264',
                     '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-video_track_timescale', '15360', o])
                wav(ao, n); segs.append(o); asegs.append(ao); continue
            vf = (f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080," + ("hflip," if op.get('flip') else '') +
                  f"zoompan=z='{op.get('z', Z.get(name, 1.04))}+0.03*on/({max(1, n)})':x='max(0,min(iw-iw/zoom,iw/2-(iw/zoom/2)+{op.get('dx', 0)}))':"
                  f"y='max(0,min(ih-ih/zoom,ih/2-(ih/zoom/2)+{op.get('dy', 0)}))':d=1:s=1920x1080:fps={FPS},"
                  f"eq=contrast=1.04:saturation=0.95:gamma={op.get('g', GM.get(name, 1.06))},vignette=PI/5,setsar=1")
            vf = (f"setpts=PTS/{sp}," if sp != 1.0 else '') + f"fps={FPS}," + vf
            if name in BAR:   # BAR = the source row where the mark starts: drawn only while this shot's framing still shows it
                z0 = float(op.get('z', Z.get(name, 1.04))); hh = 1080 / z0
                y0 = min(max(0.0, 540 - hh / 2 + float(op.get('dy', 0))), 1080 - hh); yb = int((BAR[name] - y0) * z0)
                if yb < 1080: vf += f",drawbox=x=0:y={max(0, yb)}:w=iw:h=ih:color=black:t=fill"
            vf += f",setpts=N/({FPS}*TB)"
            run(['ffmpeg', '-v', 'error', '-y', '-ss', str(tin), '-i', src(name), '-an', '-vf', vf, '-frames:v', str(n),
                 '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-video_track_timescale', '15360', o])
            if 'lufs' in op:
                g = max(-30, min(30, op['lufs'] - lufs_span(src(name), tin, n / FPS * sp)))
                wav(ao, n, (src(name), tin), g, tempo=sp)
            elif 'a' in op: wav(ao, n, (src(name), tin), op['a'], tempo=sp)
            elif sp != 1.0: wav(ao, n)
            else: wav(ao, n, (src(name), tin), S.get('clip_audio_db', -99))
            segs.append(o); asegs.append(ao)
        lst = os.path.join(WORK, f'sec{si:02d}.txt'); open(lst, 'w').write(''.join(f"file '{p}'\n" for p in segs))
        raw = os.path.join(WORK, f'sec{si:02d}_raw.mp4'); run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', raw])
        alst = os.path.join(WORK, f'sec{si:02d}_a.txt'); open(alst, 'w').write(''.join(f"file '{p}'\n" for p in asegs))
        run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', alst, '-c', 'copy', _sa])
        # ---- overlays, in EDL order (later ones on top); the concatenated frames are renumbered first (Backrooms v3, 1:11 flicker) ----
        ins = ['-i', raw]; chain = '[b0]'; fc = [f"[0:v]setpts=N/({FPS}*TB)[b0]"]; n = 1
        for j, (kind, arg, a, b) in enumerate(S.get('overlays', [])):
            b = min(b, L)
            if b <= a: continue
            if kind == 'stats':
                d, x, y = stat_frames(arg, b - a, si, j)
                ins += ['-framerate', str(FPS), '-i', os.path.join(d, '%04d.png')]
                fc.append(f"[{n}:v]format=rgba,setpts=PTS-STARTPTS+{a}/TB[o{n}]")
                fc.append(f"{chain}[o{n}]overlay={x}:{y}:eof_action=repeat:enable='between(t,{a},{b})'[c{n}]"); chain = f'[c{n}]'; n += 1
                continue
            png = overlay_png(kind, arg, os.path.join(WORK, f'ov{si:02d}_{j:02d}.png'))
            fi, fo = FADE.get(kind, (0.12, 0.12))
            ins += ['-loop', '1', '-framerate', str(FPS), '-t', f'{L + 1:.3f}', '-i', png]
            fd = (f",fade=t=in:st={a}:d={fi}:alpha=1" if fi else '') + (f",fade=t=out:st={max(a, b - fo)}:d={fo}:alpha=1" if fo else '')
            fc.append(f"[{n}:v]format=rgba{fd}[o{n}]")
            fc.append(f"{chain}[o{n}]overlay=0:0:enable='between(t,{a},{b})'[c{n}]"); chain = f'[c{n}]'; n += 1
        run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc) + f";{chain}{vfade(S, NF / FPS)}null[v]", '-map', '[v]',
             '-frames:v', str(NF), '-r', str(FPS), '-video_track_timescale', '15360', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
             '-pix_fmt', 'yuv420p', _sec])
        # ---- the section's voice: the take's pieces at their places, a short fade at every cut, the take's own end faded ----
        vin, vfc = [], []
        for k, (a, b, at) in enumerate(S['pieces']):
            vin += ['-i', vp]; ms = int(round(at * 1000)); last = abs(b - S['take']) < 0.02
            fo = f"afade=t=out:st={max(0, b - a - 0.16):.3f}:d=0.1" if last else f"afade=t=out:st={max(0, b - a - 0.03):.3f}:d=0.03"
            vfc.append(f"[{k}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.015,{fo},adelay={ms}|{ms}[p{k}]")
        np_ = len(S['pieces'])
        vfc.append(''.join(f'[p{k}]' for k in range(np_)) + f"amix=inputs={np_}:normalize=0,apad,atrim=end_sample={NF * SPF}[vo]")
        run(['ffmpeg', '-v', 'error', '-y', *vin, '-filter_complex', ';'.join(vfc), '-map', '[vo]', '-c:a', 'pcm_s16le', _sv])
        if os.environ.get('LEAN') == '1':
            for p in segs + asegs + [raw]: os.remove(p)
        print('section', v, 'ok', flush=True)
    else:
        print('section', v, 'reused', flush=True)
    parts.append(_sec); audios.append(_sa); voice_items.append((_sv, t0))
    for t, w, g in S.get('sfx', []):
        if t < L: sfx_items.append((rel(w), t0 + t, g))
    for a, b, db in S.get('duck', []): ducks.append((t0 + a, t0 + b, db))
    t_global += L
t_global = round((sum(dur(p) for p in parts) if ONLY else t_global) * FPS) / FPS
lst = os.path.join(WORK, 'all.txt'); open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
vid = os.path.join(WORK, 'video.mp4'); run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', vid])
alst = os.path.join(WORK, 'all_a.txt'); open(alst, 'w').write(''.join(f"file '{p}'\n" for p in audios))
clipa = os.path.join(WORK, 'clip_audio.wav'); run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', alst, '-c', 'copy', clipa])
vlst = os.path.join(WORK, 'all_v.txt'); open(vlst, 'w').write(''.join(f"file '{p}'\n" for p, _ in voice_items))
voicea = os.path.join(WORK, 'voice.wav'); run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', vlst, '-c', 'copy', voicea])
sfxa = os.path.join(WORK, 'sfx.wav')   # SFX bus: every cue at its absolute time, mixed once, well under the voice
if sfx_items:
    ins = []; fc = []
    for k, (w, t, g) in enumerate(sfx_items):
        ins += ['-i', w]; ms = int(round(t * 1000)); fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume={g}dB,adelay={ms}|{ms}[s{k}]")
    fc.append(''.join(f'[s{k}]' for k in range(len(sfx_items))) + f"amix=inputs={len(sfx_items)}:normalize=0,apad,atrim=0:{t_global}[sx]")
    run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '[sx]', '-c:a', 'pcm_s16le', sfxa])
else:
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', str(t_global), '-c:a', 'pcm_s16le', sfxa])
def duck_expr(ws, r=0.25):   # music ducked under each film line with 0.25 s ramps
    fs = []
    for a, b, db in ws:
        g = 10 ** (db / 20)
        fs.append(f"(1-{1 - g:.4f}*clip(min((t-{a - r:.3f})/{r},({b + r:.3f}-t)/{r}),0,1))")
    return '*'.join(fs) or '1'
mnorm = f"loudnorm=I={os.environ.get('MUSIC_LUFS', '-39')}:TP=-3,"
duck = f"volume='{duck_expr(ducks)}':eval=frame," if ducks else ''
fc = [f"[3:a]aresample=48000,atrim=0:{t_global},{mnorm}highshelf=f=3000:g=-4,{duck}afade=t=out:st={max(0, t_global - 3)}:d=3[mu]",
      "[1:a]loudnorm=I=-14.6:TP=-1.5[vo]",
      "[2:a][vo][4:a][mu]amix=inputs=4:normalize=0:duration=first,alimiter=limit=0.84:level=0[a]"]
run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', voicea, '-i', clipa, '-stream_loop', '-1', '-i', MUSIC, '-i', sfxa, '-filter_complex', ';'.join(fc),
     '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '384k', '-aac_tns', '0', '-aac_pns', '0', '-t', str(t_global), OUT])
print('done', OUT, round(t_global, 2))
