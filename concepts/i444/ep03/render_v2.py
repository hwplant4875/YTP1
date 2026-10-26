# Horror Ranked EP03 v2 renderer: clips + narration + overlays (static PNGs from ep01/gfx.py, animated frame sequences
# from anim.py: stat cards, survival-thermometer beats, the outro board) + SFX + quiet music -> mp4
# usage: python render_v2.py <edl.json> <clips_dir> <voice_dir> <music.mp3> <out.mp4> [fps]
# env: LEAN=1 deletes shot files once a section is built; ONLY=s05,s12 renders just those sections (for QA)
import json, os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ep01')); sys.path.insert(0, HERE)
from gfx import word_tag, rank_card, odds, instruction, center_title, film_label
import anim
edl, CLIPS, VOICE, MUSIC, OUT = sys.argv[1:6]
FPS = int(sys.argv[6]) if len(sys.argv) > 6 else 30
EDIR = os.path.dirname(os.path.abspath(edl))
WORK = os.path.join(os.path.dirname(os.path.abspath(OUT)), 'work_' + os.path.splitext(os.path.basename(OUT))[0])
os.makedirs(WORK, exist_ok=True)
ONLY = set(filter(None, os.environ.get('ONLY', '').split(',')))
def run(cmd): subprocess.run(cmd, check=True)
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
def rel(p): return p if os.path.isabs(p) else os.path.join(EDIR, p)
def src(name):
    for d in (CLIPS, os.path.join(EDIR, 'stillclips')):
        for ext in ('_hd.mp4', '.mp4', '.webm', '.mkv'):
            p = os.path.join(d, name + ext)
            if os.path.exists(p): return p
    raise FileNotFoundError(name)
def rec(r): return {**r, 'tile': rel(r['tile'])}
E = json.load(open(edl)); Z = E.get('zoom', {}); G = E.get('gamma', {}); parts = []; voice_items = []; sfx_items = []; t_global = 0.0
# frame-exact timeline: every section and shot boundary is rounded to whole frames from the absolute voice time,
# video and clip audio are rendered separately (no AAC priming drift), so cuts and overlays stay locked to the narration
SPF = 48000 // FPS
def wav(o, n, a_in=None, db=-99):
    ns = n * SPF
    if a_in is None or db <= -90:
        run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-af', f'atrim=end_sample={ns}', '-c:a', 'pcm_s16le', o])
    else:
        a, tin = a_in
        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(tin), '-i', a, '-vn', '-af', f'aresample=48000,volume={db}dB,apad,atrim=end_sample={ns}',
             '-ac', '2', '-c:a', 'pcm_s16le', o])
def animated(kind, arg, d_ov, L, si, j):
    """render an animated overlay into WORK/anNN_NN/ (cached: skipped when the frames already exist); returns (dir, x, y)"""
    out = os.path.join(WORK, f'an{si:02d}_{j:02d}')
    key = json.dumps([kind, arg], sort_keys=True)
    if os.path.exists(os.path.join(out, 'key.json')) and open(os.path.join(out, 'key.json')).read() == key:
        n, x, y = json.load(open(os.path.join(out, 'xy.json'))); return out, x, y
    for p in (os.listdir(out) if os.path.isdir(out) else []): os.remove(os.path.join(out, p))
    if kind == 'stats':
        a = dict(arg); a['tile_png'] = rel(a['tile_png']); a['dur'] = min(a['dur'], d_ov)
        n, x, y = anim.stat_card(out, **a)
    elif kind == 'tier':
        placed = [rec(r) for r in arg['placed']]
        n, x, y = anim.thermo_beat(out, placed, rec(arg['new']), dur=d_ov)
    elif kind == 'tierfinal':
        n, x, y = anim.thermo_final(out, [rec(r) for r in arg['placed']], d_ov, highlights=[tuple(h) for h in arg.get('highlights', [])],
                                    t_dim=arg.get('t_dim'))
    json.dump([n, x, y], open(os.path.join(out, 'xy.json'), 'w')); open(os.path.join(out, 'key.json'), 'w').write(key)
    return out, x, y
audios = []
for si, S in enumerate(E['sections']):
    vp = os.path.join(VOICE, S['voice'] + '.mp3'); vd = dur(vp); L = vd + S.get('pad', 0.5)
    F0 = round(t_global * FPS); NF = round((t_global + L) * FPS) - F0
    if ONLY and S['voice'] not in ONLY:
        t_global += L; continue
    shots = S['shots']; segs = []; asegs = []
    for k, (t, name, tin, *sp) in enumerate(shots):
        sp = sp[0] if sp else 1.0  # optional speed (<1 = slow motion)
        f0 = round(t * FPS); f1 = round(shots[k + 1][0] * FPS) if k + 1 < len(shots) else NF; n = f1 - f0
        if n <= 0: continue
        o = os.path.join(WORK, f's{si:02d}_{k:02d}.mp4'); ao = os.path.join(WORK, f's{si:02d}_{k:02d}.wav')
        vf = (f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
              f"zoompan=z='{Z.get(name,1.04)}+0.03*on/({max(1,n)})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps={FPS},"
              f"eq=contrast=1.05:saturation=0.92:gamma={G.get(name,1.12)},vignette=PI/5,setsar=1")
        if sp != 1.0: vf = f"setpts=PTS/{sp},fps={FPS}," + vf
        if name == 'BLACK':
            run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=c=black:s=1920x1080:r={FPS}', '-frames:v', str(n), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-video_track_timescale', '15360', o])
            wav(ao, n)
        else:
            run(['ffmpeg', '-v', 'error', '-y', '-ss', str(tin), '-i', src(name), '-an', '-vf', vf, '-frames:v', str(n),
                 '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-video_track_timescale', '15360', o])
            wav(ao, n, (src(name), tin), S.get('clip_audio_db', -99))
        segs.append(o); asegs.append(ao)
    lst = os.path.join(WORK, f'sec{si:02d}.txt'); open(lst, 'w').write(''.join(f"file '{p}'\n" for p in segs))
    raw = os.path.join(WORK, f'sec{si:02d}_raw.mp4'); run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', raw])
    alst = os.path.join(WORK, f'sec{si:02d}_a.txt'); open(alst, 'w').write(''.join(f"file '{p}'\n" for p in asegs))
    sa = os.path.join(WORK, f'sec{si:02d}.wav'); run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', alst, '-c', 'copy', sa]); audios.append(sa)
    # overlays, in EDL order (later ones on top)
    ins = ['-i', raw]; chain = '[0:v]'; fc = []; n = 1
    for j, ov in enumerate(S.get('overlays', [])):
        kind, arg, a, b = ov; b = min(b, L)
        if b <= a: continue
        if kind in ('stats', 'tier', 'tierfinal'):
            d, x, y = animated(kind, arg, b - a, L, si, j)
            ins += ['-framerate', str(FPS), '-i', os.path.join(d, '%04d.png')]
            fc.append(f"[{n}:v]format=rgba,setpts=PTS-STARTPTS+{a}/TB[o{n}]")
            fc.append(f"{chain}[o{n}]overlay={x}:{y}:eof_action=repeat:enable='between(t,{a},{b})'[c{n}]"); chain = f'[c{n}]'; n += 1
            continue
        png = os.path.join(WORK, f'ov{si:02d}_{j:02d}.png')
        if kind == 'word': word_tag(arg, png)
        elif kind == 'rank': rank_card(*arg, png)
        elif kind == 'odds': odds(arg if isinstance(arg, (int, float)) else 0, png) if arg != '??' else center_title(['SURVIVAL RATE', '!??%'], png, 130)
        elif kind == 'instr': instruction(arg, png)
        elif kind == 'title': center_title(arg, png)
        elif kind == 'film': film_label(arg, png)
        ins += ['-loop', '1', '-framerate', str(FPS), '-t', str(L + 1), '-i', png]
        fd = '' if kind in ('word', 'film', 'title') else f",fade=t=in:st={a}:d=0.12:alpha=1,fade=t=out:st={max(a, b-0.12)}:d=0.12:alpha=1"
        fc.append(f"[{n}:v]format=rgba{fd}[o{n}]")
        fc.append(f"{chain}[o{n}]overlay=0:0:enable='between(t,{a},{b})'[c{n}]"); chain = f'[c{n}]'; n += 1
    sec = os.path.join(WORK, f'sec{si:02d}.mp4')
    run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', (';'.join(fc) + ';' if fc else '') + f"{chain}null[v]", '-map', '[v]', '-frames:v', str(NF), '-r', str(FPS),
         '-video_track_timescale', '15360', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', sec])
    t0 = 0.0 if ONLY else F0 / FPS
    if ONLY: t0 = sum(dur(p) for p in parts)
    parts.append(sec); voice_items.append((vp, t0))
    for t, w, g in S.get('sfx', []):
        if t < L: sfx_items.append((rel(w), t0 + t, g))
    t_global += L
    print('section', S['voice'], 'ok', flush=True)
    if os.environ.get('LEAN') == '1':  # free disk: drop shot files once the section is built
        for p in segs + asegs + [raw]: os.remove(p)
t_global = round((sum(dur(p) for p in parts) if ONLY else t_global) * FPS) / FPS
lst = os.path.join(WORK, 'all.txt'); open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
vid = os.path.join(WORK, 'video.mp4'); run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', vid])
alst = os.path.join(WORK, 'all_a.txt'); open(alst, 'w').write(''.join(f"file '{p}'\n" for p in audios))
clipa = os.path.join(WORK, 'clip_audio.wav'); run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', alst, '-c', 'copy', clipa])
# SFX bus: every cue placed at its absolute time, mixed once, kept well under the voice
sfxa = os.path.join(WORK, 'sfx.wav')
if sfx_items:
    ins = []; fc = []
    for k, (w, t, g) in enumerate(sfx_items):
        ins += ['-i', w]; ms = int(round(t * 1000)); fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume={g}dB,adelay={ms}|{ms}[s{k}]")
    fc.append(''.join(f'[s{k}]' for k in range(len(sfx_items))) + f"amix=inputs={len(sfx_items)}:normalize=0,apad,atrim=0:{t_global}[sx]")
    run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '[sx]', '-c:a', 'pcm_s16le', sfxa])
else:
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', str(t_global), '-c:a', 'pcm_s16le', sfxa])
# audio: clip audio + narration + SFX + quiet music (~-27 LUFS, gentle highshelf cut)
ins = ['-i', vid, '-i', clipa, '-i', sfxa]; fc = []
for k, (vp, t) in enumerate(voice_items):
    ins += ['-i', vp]; fc.append(f"[{k+3}:a]aresample=48000,adelay={int(round(t*1000))}|{int(round(t*1000))}[v{k}]")
m = len(voice_items) + 3; ins += ['-stream_loop', '-1', '-i', MUSIC]
fc.append(f"[{m}:a]aresample=48000,atrim=0:{t_global},loudnorm=I=-27:TP=-3,highshelf=f=3000:g=-4,afade=t=out:st={max(0, t_global-2)}:d=2[mu]")
fc.append(''.join(f'[v{k}]' for k in range(len(voice_items))) + f"amix=inputs={len(voice_items)}:normalize=0,loudnorm=I=-15:TP=-1.5[vo]")
fc.append("[1:a][vo][2:a][mu]amix=inputs=4:normalize=0:duration=first,alimiter=limit=0.95[a]")
run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', str(t_global), OUT])
print('done', OUT, round(t_global, 2))
