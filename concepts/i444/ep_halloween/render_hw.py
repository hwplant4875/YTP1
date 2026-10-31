# Horror Ranked Halloween special renderer = ../ep03/render_v2.py with a per-clip logo bar height (EDL 'bar'), no mosaic.
# EP03 v2 renderer: clips + narration + overlays (static PNGs from ep01/gfx.py, animated frame sequences
# from anim.py: stat cards, tier-board (or survival-thermometer) beats, the outro board) + SFX + quiet music -> mp4
# usage: python render_v2.py <edl.json> <clips_dir> <voice_dir> <music.mp3> <out.mp4> [fps]
# env: LEAN=1 deletes shot files once a section is built; ONLY=s05,s12 renders just those sections (for QA)
import json, os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ep01')); sys.path.insert(0, os.path.join(HERE, '..', 'ep03'))
from gfx import word_tag, rank_card, odds, instruction, center_title, film_label
import anim
edl, CLIPS, VOICE, MUSIC, OUT = sys.argv[1:6]
FPS = int(sys.argv[6]) if len(sys.argv) > 6 else 30
EDIR = os.path.dirname(os.path.abspath(edl))
WORK = os.path.join(os.path.dirname(os.path.abspath(OUT)), 'work_' + os.path.splitext(os.path.basename(OUT))[0])
os.makedirs(WORK, exist_ok=True)
ONLY = set(filter(None, os.environ.get('ONLY', '').split(',')))
def run(cmd): subprocess.run(cmd, check=True)
# spoiler mosaic for the cold open: killers' unmasked faces, keyed by (clip, in-point); boxes are 1920x1080 output pixels
# (x, y, w, h, from_t) and cover the face's whole path through the shot (hand-placed from frames, checked at full rate)
MOSAIC = {('s7_10_sidney_kills', 139.92): [(1050, 150, 480, 480, 0)], ('s5_10_daughter', 103.75): [(1020, 85, 720, 875, 0)],
          ('s5_09_fighting', 144.78): [(570, 85, 750, 605, 0)], ('s6_family', 172.95): [(690, 85, 660, 845, 0.38)],
          ('s1_10_surprise', 60): [(0, 85, 1470, 890, 0)], ('s3_11_family', 65.3): [(570, 85, 780, 665, 0)],
          ('s5_09_fighting', 51): [(240, 85, 1530, 845, 0)], ('s2_10_blame', 9.0): [(90, 85, 900, 890, 0)],
          ('s7_09_anna_camp', 100): [(420, 90, 840, 680, 0)]}
BLOCK = 54  # mosaic cell size in output pixels (~8-10 cells across a face)
def mosaic(vf, boxes):
    for k, (x, y, w, h, t0) in enumerate(boxes):
        vf += (f",split[mA{k}][mB{k}];[mB{k}]crop={w}:{h}:{x}:{y},scale={max(1, w // BLOCK)}:{max(1, h // BLOCK)}:flags=area,"
               f"scale={w}:{h}:flags=neighbor[mC{k}];[mA{k}][mC{k}]overlay={x}:{y}:enable='gte(t,{t0})'")
    return vf
def fit_word(word, out):
    """gfx.word_tag (centre caption, f(170), stroke 5), shrunk to fit 1760 px, or split over two lines when it still would not fit"""
    from PIL import Image
    from gfx import f, shadow_text, WHITE
    im = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); w = word.upper(); sz = 170
    while f(sz).getlength(w) > 1760 and sz > 120: sz -= 5
    if f(sz).getlength(w) <= 1760: shadow_text(im, (960, 540), w, f(sz), WHITE, stroke=5)
    else:
        ws = w.split(); k = min(range(1, len(ws)), key=lambda i: abs(len(' '.join(ws[:i])) - len(' '.join(ws[i:]))))
        shadow_text(im, (960, 455), ' '.join(ws[:k]), f(170), WHITE, stroke=5); shadow_text(im, (960, 635), ' '.join(ws[k:]), f(170), WHITE, stroke=5)
    im.save(out)
def vfade(S, L):
    """optional dip through black at a section's start/end (EDL 'vfade': {'in': s, 'out': s})"""
    v = S.get('vfade', {}); o = ''
    if v.get('in'): o += f"fade=t=in:st=0:d={v['in']},"
    if v.get('out'): o += f"fade=t=out:st={L - v['out']:.3f}:d={v['out']},"
    return o
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
def rel(p): return p if os.path.isabs(p) else os.path.join(EDIR, p)
def src(name):
    for d in (CLIPS, os.path.join(EDIR, 'stillclips')):
        for ext in ('_hd.mp4', '.mp4', '.webm', '.mkv'):
            p = os.path.join(d, name + ext)
            if os.path.exists(p): return p
    raise FileNotFoundError(name)
def rec(r): return {**r, 'tile': rel(r['tile'])}
E = json.load(open(edl)); BOARD = E.get('beat_style') == 'board'
if E.get('tiers'): anim.set_tiers(E['tiers'])
Z = E.get('zoom', {}); G = E.get('gamma', {}); parts = []; voice_items = []; sfx_items = []; t_global = 0.0
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
    key = json.dumps([kind, arg, E.get('tiers'), E.get('beat_style')], sort_keys=True)
    if os.path.exists(os.path.join(out, 'key.json')) and open(os.path.join(out, 'key.json')).read() == key:
        n, x, y = json.load(open(os.path.join(out, 'xy.json'))); return out, x, y
    for p in (os.listdir(out) if os.path.isdir(out) else []): os.remove(os.path.join(out, p))
    if kind == 'stats':
        a = dict(arg); a['tile_png'] = rel(a['tile_png']); a['dur'] = min(a['dur'], d_ov)
        n, x, y = anim.stat_card(out, **a)
    elif kind == 'tier':
        placed = [rec(r) for r in arg['placed']]
        if BOARD: n, x, y = anim.board_beat(out, placed, rec(arg['new']), dur=d_ov, t_hit=arg.get('t_hit', 0.5),
                                            pool=[rec(r) for r in arg.get('pool', [])] or None)
        else: n, x, y = anim.thermo_beat(out, placed, rec(arg['new']), dur=d_ov)
    elif kind == 'tierfinal':
        n, x, y = (anim.board_final if BOARD else anim.thermo_final)(out, [rec(r) for r in arg['placed']], d_ov, highlights=[tuple(h) for h in arg.get('highlights', [])],
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
        # zoompan (d=1) emits one frame per input frame, so normalise to FPS first or 23.976/60 fps sources play at 1.25x / 0.5x
        vf = (f"setpts=PTS/{sp}," if sp != 1.0 else '') + f"fps={FPS}," + vf
        # owner's request: a solid black bottom bar (reads as letterbox) over the Movieclips/Fandango mark;
        # Scream 7 uploads carry it higher, inside the picture, so their bar is taller
        if 'still' not in name: vf += f",drawbox=x=0:y={E.get('bar', {}).get(name, 980)}:w=iw:h=ih:color=black:t=fill"
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
        if kind == 'word': fit_word(arg, png)
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
    run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', (';'.join(fc) + ';' if fc else '') + f"{chain}{vfade(S, NF / FPS)}null[v]", '-map', '[v]', '-frames:v', str(NF), '-r', str(FPS),
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
# voice: 100 ms fade ending 60 ms before each section's end (silence after) (owner 10/31: s08's take ended on the clipped start of a next syllable)
# audio: clip audio + narration + SFX + quiet music (~-27 LUFS, gentle highshelf cut)
ins = ['-i', vid, '-i', clipa, '-i', sfxa]; fc = []
for k, (vp, t) in enumerate(voice_items):
    ins += ['-i', vp]; fc.append(f"[{k+3}:a]aresample=48000,afade=t=out:st={max(0, dur(vp) - 0.16):.3f}:d=0.1,adelay={int(round(t*1000))}|{int(round(t*1000))}[v{k}]")
m = len(voice_items) + 3; ins += ['-stream_loop', '-1', '-i', MUSIC]
# MUSIC_LEVELLED=1: the bed is already levelled per cue (e.g. a quieter final cue), so skip loudnorm, which would even it out
mnorm = '' if os.environ.get('MUSIC_LEVELLED') == '1' else 'loudnorm=I=-39:TP=-3,'  # Horror Ranked default: music at -39 LUFS (EP03 v11), well under the voice
fc.append(f"[{m}:a]aresample=48000,atrim=0:{t_global},{mnorm}highshelf=f=3000:g=-4,afade=t=out:st={max(0, t_global-2)}:d=2[mu]")
fc.append(''.join(f'[v{k}]' for k in range(len(voice_items))) + f"amix=inputs={len(voice_items)}:normalize=0,loudnorm=I=-15:TP=-1.5[vo]")
fc.append("[1:a][vo][2:a][mu]amix=inputs=4:normalize=0:duration=first,alimiter=limit=0.95[a]")
run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', str(t_global), OUT])
print('done', OUT, round(t_global, 2))
