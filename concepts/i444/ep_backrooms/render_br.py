# Backrooms special renderer (11/7 KST) = ../ep04/render_fk.py (frame-exact per-section render, clip audio rendered apart from
# the picture, SFX bus, quiet Mixkit music) with what this episode needs:
# - a section is a voice take cut into pieces with voiceless inserts between them (EDL 'pieces': [take_from, take_to, at]);
#   its length is EDL 'len' (take + inserts + pad)
# - per-shot clip audio: opts a=<dB> (fixed gain) or lufs=<target> (measured and levelled, used for the film lines);
#   insert shots (opts ins=1) always play at 1.0x; a slowed shot is silent unless it carries a or lufs
# - music ducking windows (EDL 'duck': [from, to, dB]) under the film lines and the near-silence, with 0.25 s ramps
# - overlays from gfx_br.py: cap, corner, drop (animated), choice, place, sub, date, final, png
# - no bottom bar by default (E['bar'] = {clip: y} only where a clip carries a mark at the bottom)
# usage: python render_br.py <edl.json> <clips_dir> <voice_dir> <music.mp3> <out.mp4> [fps]
# env: LEAN=1 deletes shot files once a section is built; ONLY=s05,s09 renders just those sections; REUSE=s00,s03 keeps those
#      sections from the last full render; MUSIC_LUFS (default -39)
import json, os, sys, subprocess, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
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
Z = E.get('zoom', {}); GM = E.get('gamma', {}); BAR = E.get('bar', {})
SPF = 48000 // FPS
def wav(o, n, a_in=None, db=-99, tempo=1.0):
    ns = n * SPF
    if a_in is None or db <= -90:
        run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-af', f'atrim=end_sample={ns}', '-c:a', 'pcm_s16le', o])
    else:
        a, tin = a_in; tf = f'atempo={tempo},' if abs(tempo - 1) > 1e-3 else ''
        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(tin), '-i', a, '-vn', '-af', f'aresample=48000,{tf}volume={db:.2f}dB,afade=t=in:d=0.02,apad,atrim=end_sample={ns}',
             '-ac', '2', '-c:a', 'pcm_s16le', o])
def overlay_png(kind, arg, path):
    if kind == 'cap': gx.cap(arg, path)
    elif kind == 'corner': gx.corner(arg['p'], path)
    elif kind == 'choice': gx.choice(arg, path)
    elif kind == 'place': gx.place(arg, path)
    elif kind == 'sub': gx.sub(arg, path)
    elif kind == 'date': gx.date(arg, path)
    elif kind == 'final': gx.final(path)
    elif kind == 'png': return rel(arg)
    else: raise ValueError(kind)
    return path
FADE = {'cap': (0, 0), 'corner': (0, 0), 'choice': (0.1, 0), 'place': (0.2, 0.3), 'sub': (0.08, 0.08), 'date': (0.1, 0.15), 'final': (0.12, 0),
        'png': (0.15, 0.15)}
def drop_frames(arg, d_ov, si, j):
    out = os.path.join(WORK, f'drop{si:02d}_{j:02d}'); key = json.dumps([arg, round(d_ov, 3), FPS])
    kp = os.path.join(out, 'key.json')
    if os.path.exists(kp) and open(kp).read() == key: return out
    os.makedirs(out, exist_ok=True)
    for p in os.listdir(out): os.remove(os.path.join(out, p))
    gx.drop(out, arg['p'], d_ov, FPS, arg.get('hold', 1.0)); open(kp, 'w').write(key)
    return out
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
            if name in BAR: vf += f",drawbox=x=0:y={BAR[name]}:w=iw:h=ih:color=black:t=fill"
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
        # ---- overlays, in EDL order (later ones on top) ----
        ins = ['-i', raw]; chain = '[0:v]'; fc = []; n = 1
        for j, (kind, arg, a, b) in enumerate(S.get('overlays', [])):
            b = min(b, L)
            if b <= a: continue
            if kind == 'drop':
                d = drop_frames(arg, b - a, si, j)
                ins += ['-framerate', str(FPS), '-i', os.path.join(d, '%04d.png')]
                fc.append(f"[{n}:v]format=rgba,setpts=PTS-STARTPTS+{a}/TB[o{n}]")
                fc.append(f"{chain}[o{n}]overlay=0:0:eof_action=repeat:enable='between(t,{a},{b})'[c{n}]"); chain = f'[c{n}]'; n += 1
                continue
            png = overlay_png(kind, arg, os.path.join(WORK, f'ov{si:02d}_{j:02d}.png'))
            fi, fo = FADE.get(kind, (0.12, 0.12))
            if kind == 'corner' and isinstance(arg, dict) and arg.get('fin'): fi = arg['fin']
            ins += ['-loop', '1', '-framerate', str(FPS), '-t', f'{L + 1:.3f}', '-i', png]
            fd = (f",fade=t=in:st={a}:d={fi}:alpha=1" if fi else '') + (f",fade=t=out:st={max(a, b - fo)}:d={fo}:alpha=1" if fo else '')
            fc.append(f"[{n}:v]format=rgba{fd}[o{n}]")
            fc.append(f"{chain}[o{n}]overlay=0:0:enable='between(t,{a},{b})'[c{n}]"); chain = f'[c{n}]'; n += 1
        run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', (';'.join(fc) + ';' if fc else '') + f"{chain}null[v]", '-map', '[v]',
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
# SFX bus: every cue at its absolute time, mixed once, well under the voice
sfxa = os.path.join(WORK, 'sfx.wav')
if sfx_items:
    ins = []; fc = []
    for k, (w, t, g) in enumerate(sfx_items):
        ins += ['-i', w]; ms = int(round(t * 1000)); fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume={g}dB,adelay={ms}|{ms}[s{k}]")
    fc.append(''.join(f'[s{k}]' for k in range(len(sfx_items))) + f"amix=inputs={len(sfx_items)}:normalize=0,apad,atrim=0:{t_global}[sx]")
    run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '[sx]', '-c:a', 'pcm_s16le', sfxa])
else:
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', str(t_global), '-c:a', 'pcm_s16le', sfxa])
# music: levelled to -39 LUFS, gentle high shelf, ducked under the film lines (-10 dB) and the near-silence (-26 dB), faded out at the end
def duck_expr(ws, r=0.25):
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
     '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '384k', '-aac_tns', '0', '-t', str(t_global), OUT])
print('done', OUT, round(t_global, 2))
